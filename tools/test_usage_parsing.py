"""Regression checks for authoritative upstream usage parsing."""

import json
import sys
import time
import unittest
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import urlopen
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server  # noqa: E402


class UsageParsingTests(unittest.TestCase):
    def test_real_http_stream_records_delta_before_end(self):
        token_seen = threading.Event()
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
                acknowledged.append(token_seen.wait(2))
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
                    with urlopen(f"http://127.0.0.1:{upstream.server_port}/", timeout=5) as response:
                        timing = {}
                        body, first_ms = server.read_upstream_response(response, started, timing)
                self.assertEqual(acknowledged, [True])
                self.assertEqual(body, b"".join(payload))
                self.assertGreaterEqual(timing["endMs"] - first_ms, 100)
                self.assertEqual(timing["firstTokenMs"], first_ms)
                self.assertNotIn("hello", json.dumps(timing))
            finally:
                thread.join(timeout=5)

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

    def test_final_response_is_not_a_first_token(self):
        class Response(BytesIO):
            headers = {"Content-Type": "text/event-stream"}
        body = b'data: {"type":"response.completed","response":{"output":[{"text":"hello"}]}}\n\n'
        self.assertEqual(server.read_upstream_response(Response(body), 0), (body, 0))

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


if __name__ == "__main__":
    unittest.main()
