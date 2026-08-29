from __future__ import annotations

import argparse
import os
import sys

from .agent import CobaltAgent
from .config import Settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cobalt CLI - Debian Linux DeepSeek agent")
    parser.add_argument("prompt", nargs="*", help="Prompt or question to send to the assistant")
    parser.add_argument("--api-key", dest="api_key", help="DeepSeek API key; defaults to DEEPSEEK_API_KEY.")
    parser.add_argument("--model", default=None, help="DeepSeek model to use (default: deepseek-chat)")
    parser.add_argument("--base-url", default=None, help="DeepSeek API base URL")
    parser.add_argument("--history-path", default=None, help="Path to the conversation history JSON file")
    parser.add_argument("--shell", default=None, help="Shell executable used for commands")
    parser.add_argument("--temperature", type=float, default=None, help="Sampling temperature for model responses")
    parser.add_argument("--max-tokens", type=int, default=None, help="Maximum number of tokens per response")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    prompt = " ".join(args.prompt)
    if not prompt:
        print("Please provide a prompt.", file=sys.stderr)
        return 2

    settings = Settings(
        api_key=args.api_key or os.getenv("DEEPSEEK_API_KEY"),
        model=args.model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        base_url=args.base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        history_path=args.history_path or os.getenv("COBALT_HISTORY_PATH", "~/.cobalt/history.json"),
        shell=args.shell or os.getenv("SHELL", "/bin/bash"),
        temperature=args.temperature if args.temperature is not None else 0.2,
        max_tokens=args.max_tokens if args.max_tokens is not None else 1024,
    )

    try:
        agent = CobaltAgent(settings=settings)
        response = agent.process(prompt)
        print(response)
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
