from __future__ import annotations

import argparse
import json
import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.llm.chatanywhere_client import ChatAnywhereClient


def run_interactive_chat() -> int:
    """Run a simple interactive loop: read terminal input and print model reply."""
    try:
        client = ChatAnywhereClient()
    except ValueError as exc:
        print(f"[配置错误] {exc}")
        return 1

    model = os.getenv("CHATANYWHERE_TEST_MODEL", "gpt-4o-mini")
    print(f"[已连接] model={model}")
    print("输入内容并回车即可请求大模型；输入 exit 或 quit 结束。")

    while True:
        try:
            user_text = input("你> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已退出。")
            return 0

        if not user_text:
            continue
        if user_text.lower() in {"exit", "quit"}:
            print("已退出。")
            return 0

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. "
                    "Reply with a single JSON object with key 'reply'."
                ),
            },
            {"role": "user", "content": user_text},
        ]

        try:
            content = client.generate_json(
                messages=messages,
                model=model,
                temperature=0.2,
                max_tokens=512,
            )
            payload = json.loads(content)
            print(f"模型> {payload.get('reply', content)}")
        except Exception as exc:  # noqa: BLE001
            print(f"[调用失败] {exc}")


class TestChatAnywhereConnectivity(unittest.TestCase):
    """Integration test to verify ChatAnywhere/OpenAI-compatible API connectivity."""

    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.client = ChatAnywhereClient()
        except ValueError as exc:
            raise unittest.SkipTest(str(exc)) from exc

        cls.model = os.getenv("CHATANYWHERE_TEST_MODEL", "gpt-4o-mini")

    def test_generate_json_connectivity(self) -> None:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a strict JSON generator. "
                    "Reply with a single JSON object only. "
                    "The object must contain exactly two keys: status and echo. "
                    "status must be the string ok. "
                    "echo must be the string connectivity_test."
                ),
            },
            {"role": "user", "content": "Return the JSON now."},
        ]

        content = self.client.generate_json(
            messages=messages,
            model=self.model,
            temperature=0,
            max_tokens=128,
        )

        payload = json.loads(content)
        self.assertEqual(payload.get("status"), "ok")
        self.assertEqual(payload.get("echo"), "connectivity_test")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run unittest mode instead of interactive terminal mode.",
    )
    args = parser.parse_args()

    if args.test:
        unittest.main(argv=[sys.argv[0]])
    else:
        raise SystemExit(run_interactive_chat())
