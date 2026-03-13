from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from typing import Any, Iterable

from src.bedrock_client import BedrockAgentRuntimeGateway
from src.config import load_config, resolve_session_id
from src.logging_config import configure_logging

LOGGER = logging.getLogger(__name__)


@dataclass
class AgentAnswer:
    session_id: str
    answer: str
    traces: list[dict[str, Any]]


def _decode_completion_events(events: Iterable[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    text_chunks: list[str] = []
    traces: list[dict[str, Any]] = []

    for event in events:
        chunk = event.get("chunk")
        if chunk and "bytes" in chunk:
            text_chunks.append(chunk["bytes"].decode("utf-8"))

        trace = event.get("trace")
        if trace:
            traces.append(trace)

        return_control = event.get("returnControl")
        if return_control:
            LOGGER.debug("Received returnControl event: %s", return_control)

    return "".join(text_chunks).strip(), traces


def invoke_agent(
    question: str,
    session_id: str,
    enable_trace: bool = False,
    gateway: BedrockAgentRuntimeGateway | None = None,
) -> AgentAnswer:
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if gateway is None:
        gateway = BedrockAgentRuntimeGateway(load_config())

    response = gateway.invoke(
        input_text=question,
        session_id=session_id,
        enable_trace=enable_trace,
    )
    answer, traces = _decode_completion_events(response.get("completion", []))
    return AgentAnswer(session_id=session_id, answer=answer, traces=traces)


def run_single_turn(
    question: str,
    session_id: str,
    enable_trace: bool,
    gateway: BedrockAgentRuntimeGateway,
) -> None:
    result = invoke_agent(
        question=question,
        session_id=session_id,
        enable_trace=enable_trace,
        gateway=gateway,
    )

    print(f"\nSession ID: {result.session_id}")
    print("Agent response:")
    print(result.answer if result.answer else "[No text response returned by agent]")

    if enable_trace:
        print(f"\nTrace events captured: {len(result.traces)}")


def run_interactive_loop(
    session_id: str,
    enable_trace: bool,
    gateway: BedrockAgentRuntimeGateway,
) -> None:
    print(f"Interactive mode started. Session ID: {session_id}")
    print("Type 'exit' to end the conversation.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("Session ended.")
            break
        if not question:
            continue
        run_single_turn(
            question=question,
            session_id=session_id,
            enable_trace=enable_trace,
            gateway=gateway,
        )
        print("")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Invoke an AWS Bedrock Agent from Python.")
    parser.add_argument(
        "--question",
        type=str,
        help="Single question to send to the agent.",
    )
    parser.add_argument(
        "--session-id",
        type=str,
        default=None,
        help="Optional session ID. Defaults to BEDROCK_SESSION_ID or generated UUID.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run an interactive multi-turn chat loop.",
    )
    parser.add_argument(
        "--trace",
        action="store_true",
        help="Enable Bedrock Agent trace capture.",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        app_config = load_config()
    except ValueError as exc:
        parser.error(str(exc))
        return

    configure_logging(app_config.log_level)
    gateway = BedrockAgentRuntimeGateway(app_config)
    session_id = resolve_session_id(args.session_id)

    if args.interactive:
        run_interactive_loop(session_id=session_id, enable_trace=args.trace, gateway=gateway)
        return

    question = args.question or input("Enter your business question: ").strip()
    run_single_turn(
        question=question,
        session_id=session_id,
        enable_trace=args.trace,
        gateway=gateway,
    )


if __name__ == "__main__":
    main()
