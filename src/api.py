from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.agent_service import answer_to_dict, get_agent_service, get_service_health
from src.logging_config import configure_logging

app = FastAPI(
    title="Bedrock Agent RAG Demo API",
    version="0.1.0",
    description="FastAPI backend for a Bedrock Agent and Knowledge Base demo.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question to send to Bedrock Agent.")
    session_id: str | None = Field(default=None, description="Optional session ID for multi-turn continuity.")
    enable_trace: bool = Field(default=False, description="Whether to request Bedrock trace events.")


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    trace_count: int
    traces: list[dict]


@app.on_event("startup")
def startup_event() -> None:
    health = get_service_health()
    if health.config:
        configure_logging(health.config.log_level)


@app.get("/health")
def health_check() -> dict:
    health = get_service_health()
    return {
        "ok": health.ok,
        "configured": health.configured,
        "message": health.message,
        "aws_region": health.config.aws_region if health.config else None,
        "agent_id": health.config.agent_id if health.config else None,
        "agent_alias_id": health.config.agent_alias_id if health.config else None,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    health = get_service_health()
    if not health.configured:
        raise HTTPException(status_code=500, detail=health.message)

    try:
        result = get_agent_service().ask(
            question=request.question,
            session_id=request.session_id,
            enable_trace=request.enable_trace,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Bedrock Agent request failed: {exc}") from exc

    return ChatResponse(**answer_to_dict(result))
