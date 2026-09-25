"""Regression checks for authoritative upstream usage parsing."""

import gc
import http.client
import json
import sqlite3
import sys
import tempfile
import time
import unittest
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server  # noqa: E402


class UsageParsingTests(unittest.TestCase):
    def test_channel_cooldown_keeps_one_matching_probe_route(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "channels.sqlite3"
            db = sqlite3.connect(db_path)
            try:
                db.execute(
                    """CREATE TABLE channels (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        upstream_base_url TEXT,
                        upstream_api_key TEXT,
                        active INTEGER,
                        priority INTEGER,
                        allowed_models TEXT,
                        consecutive_failures INTEGER,
                        last_failure_at INTEGER
                    )"""
                )
                db.execute("CREATE TABLE models (name TEXT PRIMARY KEY, routing_mode TEXT NOT NULL DEFAULT 'legacy')")
                db.execute("CREATE TABLE model_channels (model_name TEXT, channel_id INTEGER)")
                db.execute("INSERT INTO models(name, routing_mode) VALUES ('gpt-5.5', 'legacy')")
                db.executemany(
                    "INSERT INTO channels VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        (1, "cooling", "https://cooling.example", "key-1", 1, 100, "gpt-5.5", 3, server.now()),
                        (2, "other-model", "https://other.example", "key-2", 1, 200, "gemini-3.1-pro-preview", 3, server.now()),
                    ],
                )
                routes = server.get_upstream_routes(db, "gpt-5.5")
            finally:
                db.close()
            self.assertEqual([route["channel_id"] for route in routes], [1])

    def test_large_json_upload_is_not_compressed(self):
        body = json.dumps({"model": "test", "input": "long context " * 30000}).encode()
        received = []

        class Upstream(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                data = self.rfile.read(int(self.headers["Content-Length"]))
                received.append((data, self.headers.get("Content-Encoding")))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'{}')

        with HTTPServer(("127.0.0.1", 0), Upstream) as upstream:
            thread = threading.Thread(target=upstream.handle_request)
            thread.start()
            try:
                request = server.Request(f"http://127.0.0.1:{upstream.server_port}/", data=body,
                                         headers={"Content-Type": "application/json"})
                with server.open_timed_upstream(request, time.perf_counter(), {}) as response:
                    self.assertEqual(response.read(), b'{}')
                self.assertEqual(received, [(body, None)])
            finally:
                thread.join(timeout=5)

    def test_real_http_stream_records_delta_before_end(self):
        token_seen = threading.Event()
        forwarded = threading.Event()
        acknowledged = []
        payload = (
            b'data: {"type":"response.created","response":{}}\n\n',
            b'data: {"type":"response.output_text.delta","delta":"hello"}\n\n',
            b'data: {"type":"response.completed","response":{"output":[]}}\n\n',
        )

        class Upstream(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                self.wfile.write(payload[0] + payload[1])
                self.wfile.flush()
                acknowledged.append(token_seen.wait(2) and forwarded.wait(2))
                time.sleep(0.15)
                self.wfile.write(payload[2])

        original = server.is_first_token_event

        def detect(event):
            result = original(event)
            if result:
                token_seen.set()
            return result

        with HTTPServer(("127.0.0.1", 0), Upstream) as upstream:
            thread = threading.Thread(target=upstream.handle_request)
            thread.start()
            try:
                started = time.perf_counter()
                with patch.object(server, "is_first_token_event", side_effect=detect):
                    transport = {}
                    with server.open_timed_upstream(server.Request(f"http://127.0.0.1:{upstream.server_port}/"), started, transport) as response:
                        timing = {}
                        body, first_ms = server.read_upstream_response(
                            response,
                            started,
                            timing,
                            lambda chunk: forwarded.set() if b"output_text.delta" in chunk else None,
                        )
                self.assertEqual(acknowledged, [True])
                self.assertEqual(body, b"".join(payload))
                self.assertGreaterEqual(timing["endMs"] - first_ms, 100)
                self.assertEqual(timing["firstTokenMs"], first_ms)
                self.assertNotIn("hello", json.dumps(timing))
                self.assertGreaterEqual(transport["connectionMs"], 0)
                self.assertLessEqual(transport["requestSentMs"], timing["headersMs"])
            finally:
                thread.join(timeout=5)

    def test_interrupted_stream_keeps_received_events_for_refund_decision(self):
        first = b'data: {"type":"response.output_text.delta","delta":"partial"}\n\n'

        class InterruptedResponse:
            headers = {"Content-Type": "text/event-stream"}

            def __init__(self):
                self.calls = 0

            def readline(self):
                self.calls += 1
                if self.calls == 1:
                    return first
                raise ConnectionResetError("upstream disconnected")

        forwarded = []
        timing = {}
        body, first_ms = server.read_upstream_response(
            InterruptedResponse(),
            time.perf_counter() - 0.01,
            timing,
            forwarded.append,
        )
        self.assertEqual(body, first)
        self.assertEqual(forwarded, [first])
        self.assertGreater(first_ms, 0)
        self.assertIn("ConnectionResetError", timing["streamError"])

    def test_responses_first_token_precedes_completion(self):
        class Response(BytesIO):
            headers = {"content-type": "text/event-stream"}
        body = (
            b'data: {"type":"response.created","response":{}}\n\n'
            b'data: {"type":"response.output_text.delta","delta":"hello"}\n\n'
            b'data: {"type":"response.completed","response":{"output":[{"text":"hello"}]}}\n\n'
        )
        with patch.object(server.time, "perf_counter", return_value=12.5):
            received, first_ms = server.read_upstream_response(Response(body), 10)
        self.assertEqual(received, body)
        self.assertEqual(first_ms, 2500)

    def test_final_only_stream_still_counts_as_first_data_like_new_api(self):
        class Response(BytesIO):
            headers = {"Content-Type": "text/event-stream"}
        body = b'data: {"type":"response.completed","response":{"output":[{"text":"hello"}]}}\n\n'
        with patch.object(server.time, "perf_counter", return_value=12.5):
            self.assertEqual(server.read_upstream_response(Response(body), 10), (body, 2500))

    def test_new_api_frt_counts_created_event_before_content(self):
        class Response(BytesIO):
            headers = {"Content-Type": "text/event-stream"}
        body = (
            b': ping\n'
            b'data: \n'
            b'data: {"type":"response.created"}\n'
            b'data: {"type":"response.output_text.delta","delta":"hello"}\n'
        )
        timing = {}
        with patch.object(server.time, "perf_counter", side_effect=[10, 11, 12, 13, 15, 16]):
            received, first_ms = server.read_upstream_response(Response(body), 10, timing)
        self.assertEqual(received, body)
        self.assertEqual(first_ms, 3000)
        self.assertEqual(timing["firstContentMs"], 5000)
        self.assertEqual(timing["endMs"], 6000)

    def test_first_token_protocol_events(self):
        for event in (
            {"type": "response.function_call_arguments.delta", "delta": "{"},
            {"type": "response.reasoning_summary_text.delta", "delta": "thinking"},
            {"choices": [{"delta": {"content": "hello"}}]},
            {"candidates": [{"content": {"parts": [{"text": "hello"}]}}]},
        ):
            self.assertTrue(server.is_first_token_event(event), event)
        for event in (
            {"choices": [{"delta": {"role": "assistant"}}]},
            {"type": "response.output_text.done", "text": "hello"},
            {"type": "response.output_text.delta", "delta": ""},
            {"type": "message_start", "message": {"content": []}},
        ):
            self.assertFalse(server.is_first_token_event(event), event)

    def test_stream_first_token_time_uses_first_generated_sse_event(self):
        class Response(BytesIO):
            headers = {"Content-Type": "text/event-stream"}

        response = Response(
            b"data: {\"type\":\"message_start\",\"message\":{\"content\":[]}}\n\n"
            b"data: {\"type\":\"content_block_delta\",\"delta\":{\"type\":\"text_delta\",\"text\":\"hello\"}}\n\n"
            b"data: [DONE]\n\n"
        )
        body, first_token_ms = server.read_upstream_response(response, time.perf_counter() - 0.01)
        self.assertIn(b"text_delta", body)
        self.assertGreater(first_token_ms, 0)

    def test_announcement_validation_keeps_only_supported_fields(self):
        items = server.normalize_announcements([{"title": "维护通知", "detail": "今晚维护", "badge": "提醒", "tone": "orange", "active": True}])
        self.assertEqual(items[0]["title"], "维护通知")
        self.assertEqual(items[0]["tone"], "orange")
        with self.assertRaises(ValueError):
            server.normalize_announcements([{"title": "", "detail": "", "badge": "", "tone": "red"}])

    def test_token_reservation_is_capped_at_three_account_units(self):
        self.assertEqual(server.cap_token_reservation(850_000), 850_000)
        self.assertEqual(server.cap_token_reservation(3_000_000), 3_000_000)
        self.assertEqual(server.cap_token_reservation(14_594_033), 3_000_000)
        self.assertEqual(server.cap_token_reservation(-1), 0)

    def test_claude_headers_use_provider_key_and_hide_downstream_key(self):
        headers = server.build_upstream_headers(
            {
                "Authorization": "Bearer nb_sk_customer",
                "X-NBAPI-Key": "nb_sk_customer",
                "Idempotency-Key": "request-1",
                "anthropic-beta": "prompt-caching-2024-07-31",
            },
            {"api_key": "sk_provider"},
            "/v1/messages",
        )
        self.assertEqual(headers["Authorization"], "Bearer sk_provider")
        self.assertEqual(headers["x-api-key"], "sk_provider")
        self.assertEqual(headers["anthropic-version"], "2023-06-01")
        self.assertEqual(headers["anthropic-beta"], "prompt-caching-2024-07-31")
        self.assertNotIn("X-NBAPI-Key", headers)
        self.assertNotIn("Idempotency-Key", headers)

    def test_openai_chat_payload_converts_to_gemini_native(self):
        payload = {
            "model": "gemini-3.1-pro-preview",
            "messages": [
                {"role": "system", "content": "You are concise."},
                {"role": "user", "content": "天气怎么样？"},
            ],
            "temperature": 0.2,
            "top_p": 0.9,
            "max_tokens": 128,
            "tools": [{
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather",
                    "parameters": {"type": "object", "properties": {"city": {"type": "string"}}},
                },
            }],
            "tool_choice": {"type": "function", "function": {"name": "get_weather"}},
        }
        converted = server.openai_chat_to_gemini_generate_content(payload)
        self.assertEqual(converted["systemInstruction"]["parts"], [{"text": "You are concise."}])
        self.assertEqual(converted["contents"], [{"role": "user", "parts": [{"text": "天气怎么样？"}]}])
        self.assertEqual(converted["generationConfig"]["maxOutputTokens"], 128)
        self.assertEqual(converted["tools"][0]["functionDeclarations"][0]["name"], "get_weather")
        self.assertEqual(converted["toolConfig"]["functionCallingConfig"]["allowedFunctionNames"], ["get_weather"])

    def test_gemini_function_call_converts_to_openai_tool_call(self):
        payload = {
            "candidates": [{
                "content": {"parts": [{"functionCall": {"name": "get_weather", "args": {"city": "北京"}}}]},
                "finishReason": "STOP",
            }],
            "usageMetadata": {"promptTokenCount": 5, "candidatesTokenCount": 1},
        }
        converted = server.gemini_response_to_openai_chat(payload, "gemini-3.1-pro-preview")
        message = converted["choices"][0]["message"]
        self.assertEqual(converted["choices"][0]["finish_reason"], "tool_calls")
        self.assertEqual(message["tool_calls"][0]["function"]["name"], "get_weather")
        self.assertEqual(json.loads(message["tool_calls"][0]["function"]["arguments"]), {"city": "北京"})
        self.assertEqual(converted["usage"]["prompt_tokens"], 5)

    def test_bridged_openai_chat_response_can_be_wrapped_as_sse(self):
        payload = {
            "id": "chatcmpl_test",
            "object": "chat.completion",
            "created": 1,
            "model": "gemini-3.1-pro-preview",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "你好"}, "finish_reason": "stop"}],
        }
        body = server.openai_chat_to_sse_bytes(payload).decode("utf-8")
        self.assertIn('"object":"chat.completion.chunk"', body)
        self.assertIn('"content":"你好"', body)
        self.assertTrue(body.endswith("data: [DONE]\n\n"))

    def assert_usage(self, body, expected_counts, expected_billable):
        payload = server.extract_response_payload(body.encode("utf-8"))
        self.assertEqual(server.extract_usage_counts(payload), expected_counts)
        self.assertEqual(server.has_separate_usage_counts(payload), expected_billable)

    def test_claude_sse_merges_start_input_and_terminal_output(self):
        self.assert_usage(
            """data: {\"type\":\"message_start\",\"message\":{\"content\":[],\"usage\":{\"input_tokens\":6,\"output_tokens\":0}}}

data: {\"type\":\"content_block_delta\",\"delta\":{\"type\":\"text_delta\",\"text\":\"hello\"}}

data: {\"type\":\"message_delta\",\"delta\":{\"stop_reason\":\"end_turn\"},\"usage\":{\"output_tokens\":626}}

data: [DONE]
""",
            (6, 626),
            True,
        )

    def test_response_with_content_and_zero_output_is_not_billable(self):
        self.assert_usage(
            json.dumps({"content": [{"type": "text", "text": "hello"}], "usage": {"input_tokens": 6, "output_tokens": 0}}),
            (6, 0),
            False,
        )

    def test_empty_claude_response_with_zero_output_remains_valid(self):
        self.assert_usage(
            json.dumps({"content": [], "usage": {"input_tokens": 6, "output_tokens": 0}}),
            (6, 0),
            True,
        )

    def test_openai_responses_nested_usage_is_supported(self):
        self.assert_usage(
            json.dumps({"type": "response.completed", "response": {"output": [{"type": "message", "content": [{"type": "output_text", "text": "hello"}]}], "usage": {"input_tokens": 4, "output_tokens": 2}}}),
            (4, 2),
            True,
        )

    def test_gemini_usage_includes_reasoning_tokens(self):
        self.assert_usage(
            json.dumps({"candidates": [{"content": {"parts": [{"text": "hello"}]}}], "usageMetadata": {"promptTokenCount": 4, "candidatesTokenCount": 2, "thoughtsTokenCount": 3}}),
            (4, 5),
            True,
        )

    def test_claude_cache_read_is_not_subtracted_from_input_twice(self):
        payload = {
            "content": [{"type": "text", "text": "hello"}],
            "usage": {
                "input_tokens": 10,
                "output_tokens": 5,
                "cache_read_input_tokens": 3,
                "cache_creation_input_tokens": 2,
            },
        }
        # Model rows store a per-1M-token price in micro-dollars. A price of
        # 1,000,000 therefore represents one micro-dollar for each token.
        model = ("claude-test", "Claude", "Anthropic", "chat", "per_token", 1_000_000, 1, 1_000_000, 1_000_000, 1_000_000, 1_000_000)
        amount, input_tokens, output_tokens, cache_read, cache_write = server.calculate_token_charge_micros(model, payload)
        self.assertEqual((input_tokens, output_tokens, cache_read, cache_write), (10, 5, 3, 2))
        self.assertEqual(amount, 20)

    def test_openai_cache_read_is_removed_from_normal_input_price(self):
        payload = {
            "choices": [{"message": {"content": "hello"}}],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "prompt_tokens_details": {"cached_tokens": 3},
            },
        }
        model = ("gpt-test", "GPT", "OpenAI", "chat", "per_token", 1_000_000, 1, 1_000_000, 1_000_000, 1_000_000, 1_000_000)
        amount, input_tokens, output_tokens, cache_read, cache_write = server.calculate_token_charge_micros(model, payload)
        self.assertEqual((input_tokens, output_tokens, cache_read, cache_write), (10, 5, 3, 0))
        self.assertEqual(amount, 15)

    def test_dynamic_pricing_uses_first_tier_below_threshold(self):
        payload = {
            "usage": {
                "prompt_tokens": 99,
                "completion_tokens": 5,
                "prompt_tokens_details": {"cached_tokens": 10},
                "cache_creation_input_tokens": 3,
            },
        }
        model = (
            "dynamic-test", "GPT", "OpenAI", "chat", "per_token", 1_000_000, 1,
            1_000_000, 1_000_000, 1_000_000, 1_000_000,
            "dynamic", 100, 2_000_000, 3_000_000, 4_000_000, 5_000_000,
        )
        amount, input_tokens, output_tokens, cache_read, cache_write = server.calculate_token_charge_micros(model, payload)
        self.assertEqual((input_tokens, output_tokens, cache_read, cache_write), (99, 5, 10, 3))
        self.assertEqual(amount, 107)
        self.assertEqual(server.model_pricing_tier(model, 99), 1)
        self.assertEqual(server.calculate_token_estimate_micros(model, 99, 5), 104)

    def test_dynamic_pricing_uses_second_tier_at_threshold_and_prices_cache(self):
        payload = {
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 5,
                "prompt_tokens_details": {"cached_tokens": 10},
                "cache_creation_input_tokens": 3,
            },
        }
        model = (
            "dynamic-test", "GPT", "OpenAI", "chat", "per_token", 1_000_000, 1,
            1_000_000, 1_000_000, 1_000_000, 1_000_000,
            "dynamic", 100, 2_000_000, 3_000_000, 4_000_000, 5_000_000,
        )
        amount, input_tokens, output_tokens, cache_read, cache_write = server.calculate_token_charge_micros(model, payload)
        self.assertEqual((input_tokens, output_tokens, cache_read, cache_write), (100, 5, 10, 3))
        self.assertEqual(amount, 250)
        self.assertEqual(server.model_pricing_tier(model, 100), 2)
        self.assertEqual(server.calculate_token_estimate_micros(model, 100, 5), 215)

    def test_approved_dynamic_customer_rates_match_pricing_plan(self):
        self.assertEqual(server.DYNAMIC_PRICING_CORRECTIONS, {
            "gpt-5.6-sol": (1_700_000, 1_700_000, 14_500_000, 117_000, 1_462_500, 272_000, 3_400_000, 21_750_000, 234_000, 2_925_000),
            "gpt-5.6-terra": (702_000, 702_000, 6_012_000, 70_200, 877_500, 200_000, 1_404_000, 9_018_000, 140_400, 1_755_000),
            "gpt-6-astra": (3_510_000, 3_510_000, 17_550_000, 351_000, 4_387_500, 272_000, 7_020_000, 26_325_000, 702_000, 8_775_000),
        })


class StaticAssetTests(unittest.TestCase):
    def test_frontend_entrypoints_are_served_from_fixed_paths(self):
        app = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        thread = threading.Thread(target=app.serve_forever, daemon=True)
        thread.start()
        connection = http.client.HTTPConnection("127.0.0.1", app.server_port, timeout=3)
        try:
            expected = {
                "/": (200, "text/html", b"assets/nbapi.css"),
                "/assets/nbapi.css": (200, "text/css", b":root"),
                "/assets/nbapi.js": (200, "text/javascript", b"const storageKeys"),
            }
            for path, (status, content_type, marker) in expected.items():
                connection.request("GET", path)
                response = connection.getresponse()
                body = response.read()
                self.assertEqual(response.status, status)
                self.assertIn(content_type, response.getheader("Content-Type"))
                self.assertIn(marker, body)
                if path == "/assets/nbapi.js":
                    etag = response.getheader("ETag")

            connection.request("GET", "/assets/nbapi.js", headers={"If-None-Match": etag})
            response = connection.getresponse()
            self.assertEqual(response.status, 304)
            self.assertEqual(response.read(), b"")

            connection.request("GET", "/assets/not-allowed.txt")
            response = connection.getresponse()
            response.read()
            self.assertEqual(response.status, 404)
        finally:
            connection.close()
            app.shutdown()
            app.server_close()
            thread.join(timeout=3)


class BillingStabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.addCleanup(gc.collect)
        self.db_path_patch = patch.object(server, "DB_PATH", Path(self.temp_dir.name) / "test.sqlite3")
        self.password_patch = patch.object(server, "DEFAULT_SUPER_ADMIN_PASSWORD", "test-password")
        self.db_path_patch.start()
        self.password_patch.start()
        self.addCleanup(self.db_path_patch.stop)
        self.addCleanup(self.password_patch.stop)
        server.init_db()
        with sqlite3.connect(server.DB_PATH) as db:
            cursor = db.execute(
                "INSERT INTO users(username,email,password_hash,role,active,balance_micros,created_at) VALUES ('billing-user','',?,'user',1,10000000,?)",
                (server.hash_password("password"), server.now()),
            )
            self.user_id = cursor.lastrowid
            token = "nb_sk_billing_test"
            self.token = token
            cursor = db.execute(
                "INSERT INTO api_tokens(user_id,name,token_hash,token_secret,token_hint,active,created_at,quota_unlimited,used_micros) VALUES (?,?,?,?,?,1,?,1,0)",
                (self.user_id, "test", server.hashlib.sha256(token.encode()).hexdigest(), token, "test", server.now()),
            )
            self.token_id = cursor.lastrowid

    def admin_api_request(self, method, path, payload=None, token="test-super-session"):
        app = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        thread = threading.Thread(target=app.handle_request)
        thread.start()
        connection = http.client.HTTPConnection("127.0.0.1", app.server_port, timeout=3)
        try:
            body = json.dumps(payload or {}).encode() if payload is not None else None
            connection.request(method, path, body=body, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            })
            response = connection.getresponse()
            data = json.loads(response.read() or b"{}")
            return response.status, data
        finally:
            connection.close()
            app.server_close()
            thread.join(timeout=3)

    def api_token_request(self, method, path, token=None):
        app = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        thread = threading.Thread(target=app.handle_request)
        thread.start()
        connection = http.client.HTTPConnection("127.0.0.1", app.server_port, timeout=3)
        try:
            headers = {"Authorization": f"Bearer {token or self.token}"}
            connection.request(method, path, headers=headers)
            response = connection.getresponse()
            data = json.loads(response.read() or b"{}")
            return response.status, data
        finally:
            connection.close()
            app.server_close()
            thread.join(timeout=3)

    def test_reserve_and_settle_charge_exactly_once(self):
        with sqlite3.connect(server.DB_PATH) as db:
            first = server.reserve_billing(db, self.user_id, self.token_id, "gpt-6-astra", "request-1", 3_000_000)
            duplicate = server.reserve_billing(db, self.user_id, self.token_id, "gpt-6-astra", "request-1", 3_000_000)
            self.assertFalse(first["idempotent"])
            self.assertTrue(duplicate["idempotent"])

            self.assertEqual(db.execute("SELECT balance_micros FROM users WHERE id=?", (self.user_id,)).fetchone()[0], 7_000_000)

            settled = server.settle_billing(
                db, self.user_id, self.token_id, "gpt-6-astra", "request-1",
                129_645, "per_token", 189_426, 2_840, "127.0.0.1",
                136_300, 48_500, "/v1/responses", "request-1", 189_312, 0, "openai_responses",
            )
            repeated = server.settle_billing(
                db, self.user_id, self.token_id, "gpt-6-astra", "request-1",
                129_645, "per_token", 189_426, 2_840, "127.0.0.1",
                136_300, 48_500, "/v1/responses", "request-1", 189_312, 0, "openai_responses",
            )
            self.assertFalse(settled["idempotent"])
            self.assertTrue(repeated["idempotent"])
            self.assertEqual(db.execute("SELECT balance_micros FROM users WHERE id=?", (self.user_id,)).fetchone()[0], 9_870_355)
            self.assertEqual(db.execute("SELECT used_micros FROM api_tokens WHERE id=?", (self.token_id,)).fetchone()[0], 129_645)
            ledger = db.execute("SELECT amount_micros,input_tokens,output_tokens,cache_read_tokens,status FROM ledger WHERE request_id='request-1'").fetchall()
            self.assertEqual(ledger, [(129_645, 189_426, 2_840, 189_312, "charged")])

    def test_gpt_6_sol_seed_is_hidden_explicit_and_idempotent(self):
        with sqlite3.connect(server.DB_PATH) as db:
            before_channels = db.execute("SELECT id, allowed_models FROM channels ORDER BY id").fetchall()
            row = db.execute(
                "SELECT active,routing_mode,api_protocol,endpoint,billing_unit,price_micros,input_price_micros,output_price_micros,cache_read_price_micros,cache_write_price_micros,pricing_mode,tier_threshold_tokens,tier2_input_price_micros,tier2_output_price_micros,tier2_cache_read_price_micros,tier2_cache_write_price_micros FROM models WHERE name='gpt-6-sol'"
            ).fetchone()
            source_prices = db.execute(
                "SELECT billing_unit,price_micros,input_price_micros,output_price_micros,cache_read_price_micros,cache_write_price_micros,pricing_mode,tier_threshold_tokens,tier2_input_price_micros,tier2_output_price_micros,tier2_cache_read_price_micros,tier2_cache_write_price_micros FROM models WHERE name='gpt-5.6-sol'"
            ).fetchone()
            self.assertEqual(row[:4], (0, "explicit", "openai_responses", "/v1/responses"))
            self.assertEqual(row[4:], source_prices)
            self.assertEqual(server.model_supplier_ids(db, "gpt-6-sol"), [])
        server.init_db()
        with sqlite3.connect(server.DB_PATH) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM models WHERE name='gpt-6-sol'").fetchone()[0], 1)
            self.assertEqual(db.execute("SELECT id, allowed_models FROM channels ORDER BY id").fetchall(), before_channels)

    def test_openai_model_list_returns_active_token_allowed_models(self):
        with sqlite3.connect(server.DB_PATH) as db:
            db.execute("UPDATE models SET active=1 WHERE name='gpt-6-sol'")
            db.execute("UPDATE api_tokens SET allowed_models='gpt-6-sol' WHERE id=?", (self.token_id,))
        status, data = self.api_token_request("GET", "/v1/models")
        self.assertEqual(status, 200)
        self.assertEqual(data["object"], "list")
        self.assertEqual([item["id"] for item in data["data"]], ["gpt-6-sol", "gpt-6"])
        self.assertEqual(data["data"][0]["object"], "model")

    def test_gpt_6_alias_routes_bills_and_forwards_as_gpt_6_sol(self):
        received_models = []

        class Upstream(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))) or b"{}")
                received_models.append(payload.get("model"))
                response = json.dumps({
                    "id": "resp-alias", "object": "response", "output": [{"type": "message", "content": [{"type": "output_text", "text": "ok"}]}],
                    "usage": {"input_tokens": 10, "output_tokens": 5},
                }).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

        upstream = HTTPServer(("127.0.0.1", 0), Upstream)
        upstream_thread = threading.Thread(target=upstream.handle_request)
        upstream_thread.start()
        with sqlite3.connect(server.DB_PATH) as db:
            channel_id = db.execute("SELECT id FROM channels ORDER BY id LIMIT 1").fetchone()[0]
            db.execute("UPDATE models SET active=1 WHERE name='gpt-6-sol'")
            db.execute(
                "UPDATE channels SET active=1,upstream_base_url=?,upstream_api_key='provider-key' WHERE id=?",
                (f"http://127.0.0.1:{upstream.server_port}", channel_id),
            )
            db.execute("INSERT INTO model_channels(model_name,channel_id,created_at) VALUES ('gpt-6-sol',?,?)", (channel_id, server.now()))

        proxy = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        proxy_thread = threading.Thread(target=proxy.handle_request)
        proxy_thread.start()
        connection = http.client.HTTPConnection("127.0.0.1", proxy.server_port, timeout=3)
        try:
            connection.request(
                "POST", "/v1/responses",
                body=json.dumps({"model": "gpt-6", "input": "hello"}).encode(),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.token}", "Idempotency-Key": "request-gpt-6-alias"},
            )
            response = connection.getresponse()
            response.read()
            self.assertEqual(response.status, 200)
        finally:
            connection.close()
            proxy.server_close()
            upstream.server_close()
            proxy_thread.join(timeout=3)
            upstream_thread.join(timeout=3)

        self.assertEqual(received_models, ["gpt-6-sol"])
        with sqlite3.connect(server.DB_PATH) as db:
            ledger = db.execute(
                "SELECT model_name,amount_micros,input_tokens,output_tokens,status FROM ledger WHERE request_id='request-gpt-6-alias'"
            ).fetchone()
        self.assertEqual(ledger, ("gpt-6-sol", 90, 10, 5, "charged"))

    def test_openai_model_list_requires_api_token(self):
        status, data = self.api_token_request("GET", "/v1/models", token="invalid")
        self.assertEqual(status, 401)
        self.assertEqual(data["error"], "api_key_required")

    def test_model_alias_and_canonical_id_share_token_permission(self):
        self.assertTrue(server.token_allows_model("gpt-6-sol", "gpt-6"))
        self.assertTrue(server.token_allows_model("gpt-6", "gpt-6-sol"))
        self.assertFalse(server.token_allows_model("gpt-6-astra", "gpt-6"))

    def test_explicit_model_routes_only_to_assigned_suppliers(self):
        with sqlite3.connect(server.DB_PATH) as db:
            channels = db.execute("SELECT id FROM channels ORDER BY id").fetchall()
            first_id, second_id = channels[0][0], channels[1][0]
            db.execute("UPDATE channels SET active=1, upstream_api_key='key', allowed_models='' WHERE id IN (?,?)", (first_id, second_id))
            db.execute("INSERT INTO model_channels(model_name,channel_id,created_at) VALUES ('gpt-6-sol',?,?)", (second_id, server.now()))
            explicit_routes = server.get_upstream_routes(db, "gpt-6-sol")
            legacy_routes = server.get_upstream_routes(db, "gpt-5.5")
        self.assertEqual([route["channel_id"] for route in explicit_routes], [second_id])
        self.assertEqual([route["channel_id"] for route in legacy_routes], [first_id, second_id])

    def test_admin_model_api_requires_supplier_and_hides_after_supplier_delete(self):
        with sqlite3.connect(server.DB_PATH) as db:
            super_id = db.execute("SELECT id FROM users WHERE role='super_admin'").fetchone()[0]
            db.execute("INSERT INTO sessions(token,user_id,expires_at) VALUES ('test-super-session',?,?)", (super_id, server.now() + 3600))
            admin_id = db.execute(
                "INSERT INTO users(username,email,password_hash,role,active,balance_micros,created_at) VALUES ('api-admin','',?,'admin',1,0,?)",
                (server.hash_password("password"), server.now()),
            ).lastrowid
            db.execute("INSERT INTO sessions(token,user_id,expires_at) VALUES ('test-admin-session',?,?)", (admin_id, server.now() + 3600))
            channel_id = db.execute("SELECT id FROM channels ORDER BY id LIMIT 1").fetchone()[0]
        status, data = self.admin_api_request("GET", "/api/admin/models", token="test-admin-session")
        self.assertEqual((status, data["error"]), (403, "super_admin_only"))
        payload = {
            "name": "api-test-model", "providerLabel": "API Test", "provider": "OpenAI", "kind": "对话模型",
            "billingUnit": "per_token", "pricingMode": "static", "apiProtocol": "openai_responses",
            "inputPrice": "1", "outputPrice": "2", "supplierIds": [], "active": True,
        }
        status, data = self.admin_api_request("POST", "/api/admin/models", payload)
        self.assertEqual((status, data["error"]), (400, "active_model_requires_supplier"))
        payload["supplierIds"] = [channel_id]
        status, data = self.admin_api_request("POST", "/api/admin/models", payload)
        self.assertEqual(status, 201)
        self.assertEqual(data["model"]["supplierIds"], [channel_id])
        status, data = self.admin_api_request("DELETE", f"/api/admin/channels/{channel_id}")
        self.assertEqual(status, 200)
        self.assertIn("api-test-model", data["hiddenModels"])
        with sqlite3.connect(server.DB_PATH) as db:
            self.assertEqual(db.execute("SELECT active FROM models WHERE name='api-test-model'").fetchone()[0], 0)

    def test_super_admin_can_create_supplier_with_all_fields(self):
        with sqlite3.connect(server.DB_PATH) as db:
            super_id = db.execute("SELECT id FROM users WHERE role='super_admin'").fetchone()[0]
            db.execute("INSERT INTO sessions(token,user_id,expires_at) VALUES ('test-super-session',?,?)", (super_id, server.now() + 3600))
        payload = {
            "name": "qiaomo",
            "upstreamBaseUrl": "https://qiaomoapi.cn/v1",
            "upstreamApiKey": "provider-secret",
            "priority": "100",
            "note": "格斗",
            "allowedModels": "gpt-6-sol",
            "active": True,
        }
        status, data = self.admin_api_request("POST", "/api/admin/channels", payload)
        self.assertEqual(status, 201)
        self.assertEqual(data["channel"]["name"], "qiaomo")
        self.assertEqual(data["channel"]["allowedModels"], ["gpt-6-sol"])
        self.assertTrue(data["channel"]["upstreamApiKeySet"])
        with sqlite3.connect(server.DB_PATH) as db:
            row = db.execute(
                "SELECT name,upstream_base_url,upstream_api_key,priority,note,allowed_models,active FROM channels WHERE name='qiaomo'"
            ).fetchone()
        self.assertEqual(row, ("qiaomo", "https://qiaomoapi.cn/v1", "provider-secret", 100, "格斗", "gpt-6-sol", 1))


    def test_failed_call_refunds_reservation_exactly_once(self):
        with sqlite3.connect(server.DB_PATH) as db:
            server.reserve_billing(db, self.user_id, self.token_id, "gpt-6-astra", "request-refund", 3_000_000)
            first = server.refund_billing(db, self.user_id, "request-refund", "refund_upstream_failure")
            repeated = server.refund_billing(db, self.user_id, "request-refund", "refund_upstream_failure")
            self.assertTrue(first["refunded"])
            self.assertFalse(repeated["refunded"])
            self.assertEqual(db.execute("SELECT balance_micros FROM users WHERE id=?", (self.user_id,)).fetchone()[0], 10_000_000)
            self.assertEqual(db.execute("SELECT used_micros FROM api_tokens WHERE id=?", (self.token_id,)).fetchone()[0], 0)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM ledger WHERE idempotency_key='request-refund'").fetchone()[0], 1)

    def test_zpay_credit_is_idempotent_and_isolated_from_streaming(self):
        with sqlite3.connect(server.DB_PATH) as db:
            db.execute(
                "INSERT INTO wallet_orders(user_id,amount_micros,status,payment_method,payment_provider,merchant_order_no,created_at,updated_at) VALUES (?,10000000,'pending','alipay','zpay','order-stream-test',?,?)",
                (self.user_id, server.now(), server.now()),
            )
        first = server.credit_zpay_order("order-stream-test", "trade-stream-test", 10_000_000, "127.0.0.1", "test")
        repeated = server.credit_zpay_order("order-stream-test", "trade-stream-test", 10_000_000, "127.0.0.1", "test")
        self.assertFalse(first["idempotent"])
        self.assertTrue(repeated["idempotent"])
        with sqlite3.connect(server.DB_PATH) as db:
            self.assertEqual(db.execute("SELECT balance_micros FROM users WHERE id=?", (self.user_id,)).fetchone()[0], 20_000_000)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM balance_transactions WHERE type='topup_zpay'").fetchone()[0], 1)

    def test_end_to_end_sse_reaches_client_before_completion_and_then_settles(self):
        first_events = (
            b'data: {"type":"response.created","response":{}}\n\n'
            b'data: {"type":"response.output_text.delta","delta":"hello"}\n\n'
        )
        completed = (
            b'data: {"type":"response.completed","response":{"output":[{"type":"message","content":[{"type":"output_text","text":"hello"}]}],"usage":{"input_tokens":272000,"output_tokens":10}}}\n\n'
            b'data: [DONE]\n\n'
        )

        class Upstream(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                self.rfile.read(int(self.headers.get("Content-Length", "0")))
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                self.wfile.write(first_events)
                self.wfile.flush()
                time.sleep(0.5)
                self.wfile.write(completed)
                self.wfile.flush()

        upstream = HTTPServer(("127.0.0.1", 0), Upstream)
        upstream_thread = threading.Thread(target=upstream.handle_request)
        upstream_thread.start()
        with sqlite3.connect(server.DB_PATH) as db:
            db.execute("UPDATE channels SET active=0")
            db.execute(
                "UPDATE channels SET active=1,upstream_base_url=?,upstream_api_key='provider-key',allowed_models='gpt-6-astra' WHERE id=(SELECT MIN(id) FROM channels)",
                (f"http://127.0.0.1:{upstream.server_port}",),
            )

        proxy = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        proxy_thread = threading.Thread(target=proxy.handle_request)
        proxy_thread.start()
        connection = http.client.HTTPConnection("127.0.0.1", proxy.server_port, timeout=3)
        request_body = json.dumps({"model": "gpt-6-astra", "stream": True, "input": "hello"}).encode()
        started = time.perf_counter()
        try:
            connection.request(
                "POST",
                "/v1/responses",
                body=request_body,
                headers={
                    "Content-Type": "application/json",
                    "X-NBAPI-Key": self.token,
                    "Idempotency-Key": "request-stream-e2e",
                },
            )
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            lines = []
            while True:
                line = response.readline()
                lines.append(line)
                if b"output_text.delta" in line:
                    break
            first_chunk_seconds = time.perf_counter() - started
            self.assertLess(first_chunk_seconds, 0.4)
            remainder = response.read()
            total_seconds = time.perf_counter() - started
            self.assertGreaterEqual(total_seconds, 0.45)
            self.assertIn(b"response.completed", remainder)
        finally:
            connection.close()
            proxy.server_close()
            upstream.server_close()
            proxy_thread.join(timeout=3)
            upstream_thread.join(timeout=3)

        with sqlite3.connect(server.DB_PATH) as db:
            ledger = db.execute(
                "SELECT amount_micros,input_tokens,output_tokens,status FROM ledger WHERE request_id='request-stream-e2e'"
            ).fetchall()
            self.assertEqual(ledger, [(1_909_704, 272_000, 10, "charged")])
            self.assertEqual(db.execute("SELECT balance_micros FROM users WHERE id=?", (self.user_id,)).fetchone()[0], 8_090_296)

    def test_client_disconnect_does_not_cancel_final_settlement(self):
        class Upstream(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                self.rfile.read(int(self.headers.get("Content-Length", "0")))
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()
                self.wfile.write(b'data: {"type":"response.output_text.delta","delta":"hello"}\n\n')
                self.wfile.flush()
                time.sleep(0.2)
                self.wfile.write(
                    b'data: {"type":"response.completed","response":{"output":[{"text":"hello"}],"usage":{"input_tokens":20,"output_tokens":5}}}\n\n'
                    b'data: [DONE]\n\n'
                )
                self.wfile.flush()

        upstream = HTTPServer(("127.0.0.1", 0), Upstream)
        upstream_thread = threading.Thread(target=upstream.handle_request)
        upstream_thread.start()
        with sqlite3.connect(server.DB_PATH) as db:
            db.execute("UPDATE channels SET active=0")
            db.execute(
                "UPDATE channels SET active=1,upstream_base_url=?,upstream_api_key='provider-key',allowed_models='gpt-6-astra' WHERE id=(SELECT MIN(id) FROM channels)",
                (f"http://127.0.0.1:{upstream.server_port}",),
            )

        proxy = server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        proxy_thread = threading.Thread(target=proxy.handle_request)
        proxy_thread.start()
        connection = http.client.HTTPConnection("127.0.0.1", proxy.server_port, timeout=3)
        request_body = json.dumps({"model": "gpt-6-astra", "stream": True, "input": "hello"}).encode()
        try:
            connection.request(
                "POST", "/v1/responses", body=request_body,
                headers={"Content-Type": "application/json", "X-NBAPI-Key": self.token, "Idempotency-Key": "request-disconnect"},
            )
            response = connection.getresponse()
            while b"output_text.delta" not in response.readline():
                pass
            connection.close()
            upstream_thread.join(timeout=3)
            deadline = time.time() + 3
            ledger = []
            while time.time() < deadline:
                with sqlite3.connect(server.DB_PATH) as db:
                    ledger = db.execute(
                        "SELECT amount_micros,input_tokens,output_tokens,status FROM ledger WHERE request_id='request-disconnect'"
                    ).fetchall()
                if ledger:
                    break
                time.sleep(0.02)
            self.assertEqual(ledger, [(158, 20, 5, "charged")])
        finally:
            connection.close()
            proxy.server_close()
            upstream.server_close()
            proxy_thread.join(timeout=3)
            upstream_thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
