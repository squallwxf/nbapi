"""Regression checks for authoritative upstream usage parsing."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server  # noqa: E402


class UsageParsingTests(unittest.TestCase):
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
