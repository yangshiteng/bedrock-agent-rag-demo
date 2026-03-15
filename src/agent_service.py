from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from src.bedrock_client import BedrockAgentRuntimeGateway
from src.config import AppConfig, load_config, resolve_session_id
from src.invoke_agent import AgentAnswer, invoke_agent


@dataclass(frozen=True)
class ServiceHealth:
    ok: bool
    configured: bool
    message: str
    config: AppConfig | None = None


class BedrockAgentService:
    """Reusable application service for Bedrock Agent-backed RAG requests."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.gateway = BedrockAgentRuntimeGateway(config)

    def ask(
        self,
        question: str,
        session_id: str | None = None,
        enable_trace: bool = False,
    ) -> AgentAnswer:
        resolved_session_id = resolve_session_id(session_id)
        return invoke_agent(
            question=question,
            session_id=resolved_session_id,
            enable_trace=enable_trace,
            gateway=self.gateway,
        )


@lru_cache(maxsize=1)
def get_agent_service() -> BedrockAgentService:
    return BedrockAgentService(load_config())


def get_service_health() -> ServiceHealth:
    try:
        config = load_config()
    except ValueError as exc:
        return ServiceHealth(
            ok=False,
            configured=False,
            message=str(exc),
        )

    return ServiceHealth(
        ok=True,
        configured=True,
        message="Bedrock Agent RAG service is configured.",
        config=config,
    )


def answer_to_dict(answer: AgentAnswer) -> dict[str, Any]:
    return {
        "session_id": answer.session_id,
        "answer": answer.answer,
        "traces": answer.traces,
        "trace_count": len(answer.traces),
    }
