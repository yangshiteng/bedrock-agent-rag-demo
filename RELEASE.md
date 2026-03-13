# Release Notes

## v0.1.0

Initial public portfolio release of `bedrock-agent-business-assistant`.

Highlights:

- Python application for invoking an existing AWS Bedrock Agent with `boto3`
- Clear separation of runtime client, configuration, logging, and invocation logic
- Business knowledge assistant scenario covering agent orchestration, retrieval, and tool use
- Lightweight RAG evaluation workflow with sample dataset and unit tests
- Documentation for manual AWS setup when agent resources are configured outside the repository

## Suggested Next Release

- Add trace-aware evaluation using Bedrock citations or trace metadata
- Add mocked integration tests for agent runtime responses
- Add CI checks for tests and style validation
