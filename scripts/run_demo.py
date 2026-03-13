from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.bedrock_client import BedrockAgentRuntimeGateway
from src.config import load_config, resolve_session_id
from src.invoke_agent import invoke_agent
from src.logging_config import configure_logging

DEFAULT_QUESTIONS = [
    "What is the internal definition of quarterly net revenue?",
    "What policy applies to vendor risk reviews?",
    "If a department spent $12,000 with a 10% contingency, what is the total?",
]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a short Bedrock Agent portfolio demo.")
    parser.add_argument(
        "--question",
        action="append",
        help="Optional question(s). Repeat --question to supply multiple prompts.",
    )
    parser.add_argument(
        "--session-id",
        type=str,
        default=None,
        help="Session ID to reuse across all demo turns.",
    )
    parser.add_argument("--trace", action="store_true", help="Enable trace capture.")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    config = load_config()
    configure_logging(config.log_level)
    gateway = BedrockAgentRuntimeGateway(config)

    questions = args.question if args.question else DEFAULT_QUESTIONS
    session_id = resolve_session_id(args.session_id)

    print(f"Running demo with session ID: {session_id}")

    for index, question in enumerate(questions, start=1):
        print(f"\n[{index}] Question: {question}")
        result = invoke_agent(
            question=question,
            session_id=session_id,
            enable_trace=args.trace,
            gateway=gateway,
        )
        print("Answer:")
        print(result.answer if result.answer else "[No text response returned by agent]")


if __name__ == "__main__":
    main()
