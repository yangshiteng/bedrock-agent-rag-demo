from __future__ import annotations

import os
import uuid
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    aws_region: str
    agent_id: str
    agent_alias_id: str
    aws_profile: str | None = None
    log_level: str = "INFO"


def load_config(dotenv_path: str | None = None) -> AppConfig:
    """Load required Bedrock Agent configuration from environment variables."""
    load_dotenv(dotenv_path=dotenv_path)

    aws_region = os.getenv("AWS_REGION", "us-east-1")
    agent_id = os.getenv("BEDROCK_AGENT_ID", "").strip()
    agent_alias_id = os.getenv("BEDROCK_AGENT_ALIAS_ID", "").strip()
    aws_profile = os.getenv("AWS_PROFILE", "").strip() or None
    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()

    missing = []
    if not agent_id:
        missing.append("BEDROCK_AGENT_ID")
    if not agent_alias_id:
        missing.append("BEDROCK_AGENT_ALIAS_ID")

    if missing:
        raise ValueError(
            "Missing required environment variables: "
            + ", ".join(missing)
            + ". Copy .env.example to .env and set values from your AWS console."
        )

    return AppConfig(
        aws_region=aws_region,
        agent_id=agent_id,
        agent_alias_id=agent_alias_id,
        aws_profile=aws_profile,
        log_level=log_level,
    )


def resolve_session_id(explicit_session_id: str | None = None) -> str:
    """Return session ID from CLI, environment, or generate one for local use."""
    if explicit_session_id:
        return explicit_session_id

    env_session_id = os.getenv("BEDROCK_SESSION_ID", "").strip()
    if env_session_id:
        return env_session_id

    return f"session-{uuid.uuid4()}"
