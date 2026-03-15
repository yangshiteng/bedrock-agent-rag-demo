from __future__ import annotations

from src.agent_service import answer_to_dict, get_service_health
from src.invoke_agent import AgentAnswer


def test_answer_to_dict_includes_trace_count() -> None:
    payload = answer_to_dict(
        AgentAnswer(
            session_id="demo-session",
            answer="This is an answer.",
            traces=[{"step": "retrieval"}, {"step": "response"}],
        )
    )

    assert payload["session_id"] == "demo-session"
    assert payload["answer"] == "This is an answer."
    assert payload["trace_count"] == 2


def test_get_service_health_reports_missing_configuration(monkeypatch) -> None:
    monkeypatch.setenv("BEDROCK_AGENT_ID", "")
    monkeypatch.setenv("BEDROCK_AGENT_ALIAS_ID", "")

    health = get_service_health()

    assert health.ok is False
    assert health.configured is False
    assert "BEDROCK_AGENT_ID" in health.message
