from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import boto3
from botocore.config import Config as BotoConfig

from src.config import AppConfig


@dataclass
class BedrockAgentRuntimeGateway:
    """Thin gateway around boto3 Bedrock Agent Runtime client."""

    config: AppConfig
    _client: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        retry_config = BotoConfig(
            retries={"max_attempts": 3, "mode": "standard"},
            read_timeout=60,
            connect_timeout=10,
        )
        self._client = boto3.client(
            service_name="bedrock-agent-runtime",
            region_name=self.config.aws_region,
            config=retry_config,
        )

    def invoke(
        self,
        input_text: str,
        session_id: str,
        enable_trace: bool = False,
    ) -> dict[str, Any]:
        return self._client.invoke_agent(
            agentId=self.config.agent_id,
            agentAliasId=self.config.agent_alias_id,
            sessionId=session_id,
            inputText=input_text,
            enableTrace=enable_trace,
        )
