# Architecture

This project demonstrates a production-style invocation path for an existing AWS Bedrock Agent integrated into a Python application.

## End-to-End Flow

`User -> Application -> Bedrock Agent Runtime -> Agent reasoning -> Knowledge Base retrieval -> Action group tools -> Response`

## Component Roles

1. **User**
   Submits a business question from CLI/demo script.

2. **Application (Python + boto3)**
   Loads config, manages session ID, calls `InvokeAgent`, and logs response output.

3. **Bedrock Agent Runtime**
   Receives `agentId`, `agentAliasId`, `sessionId`, and user input.

4. **Agent Reasoning**
   The configured agent orchestration layer plans whether to answer from retrieved context, invoke an action group, or combine both.

5. **Knowledge Base Retrieval**
   Agent retrieves business documents and policy snippets from attached Bedrock Knowledge Base.

6. **Action Group Tools**
   Agent can trigger configured tools (for example calculations or policy workflow lookups) via action groups.

7. **Response**
   Final response stream is returned to the Python app and displayed to the user.

## Sequence Notes

- Session IDs are intentionally reused for multi-turn context continuity.
- Retrieval quality depends on your indexed document quality and chunking strategy.
- Tool quality depends on the action group contract (schema, Lambda/API reliability, and guardrails).
