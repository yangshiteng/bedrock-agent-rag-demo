# bedrock-agent-business-assistant

Portfolio-style Python project showing how a production application can integrate with an existing AWS Bedrock Agent for business Q&A, retrieval-augmented generation (RAG), and tool-assisted reasoning.

This repository intentionally assumes the Bedrock Agent resources are created manually in AWS (console or IaC outside this repo). The code focuses on reliable invocation, local developer ergonomics, and measurable RAG evaluation.

## Project Overview

This project demonstrates:

- Invoking an existing Bedrock Agent from Python (`boto3`)
- Business knowledge assistant flows powered by Agent + Knowledge Base retrieval
- Tool use patterns via action groups (example calculator utility included)
- Lightweight evaluation logic for answer quality and grounding

## Architecture

High-level flow:

`User -> Application -> Bedrock Agent Runtime -> Agent reasoning -> Knowledge Base retrieval -> Action group tools -> Response`

Detailed walkthrough: [`architecture/architecture.md`](architecture/architecture.md)

## AWS Resources Required

You need these existing AWS resources before local execution:

1. Bedrock Agent
2. Agent alias (deployed and active)
3. Knowledge Base attached to the agent
4. At least one action group (for tool use demonstration)
5. IAM permissions for the caller identity to invoke `bedrock-agent-runtime:InvokeAgent`

## Manual Setup Instructions

Manual setup is documented in detail in [`docs/aws_manual_setup.md`](docs/aws_manual_setup.md).

Quick summary:

1. Create a Bedrock Agent in AWS console.
2. Attach or create a Knowledge Base and connect it to the agent.
3. Create an action group (Lambda/API-based or function schema-based).
4. Deploy an alias for runtime invocation.
5. Copy `AGENT_ID` and `AGENT_ALIAS_ID` into local `.env`.

## Local Setup

```bash
python -m venv .venv
. .venv/Scripts/activate  # PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.env` from template:

```bash
copy .env.example .env
```

Set required values in `.env`:

- `AWS_REGION`
- `BEDROCK_AGENT_ID`
- `BEDROCK_AGENT_ALIAS_ID`

## Run The Demo Locally

Single question:

```bash
python -m src.invoke_agent --question "What policy applies to vendor risk reviews?"
```

Interactive session (reuses one session ID across turns):

```bash
python -m src.invoke_agent --interactive
```

Portfolio walkthrough script:

```bash
python scripts/run_demo.py
```

## Example Prompts

See [`examples/sample_questions.md`](examples/sample_questions.md).

Starter prompts:

- What is the internal definition of quarterly net revenue?
- What policy applies to vendor risk reviews?
- If a department spent $12,000 with a 10% contingency, what is the total?

## Evaluation Approach

Evaluation is intentionally simple but interview-friendly:

- **Answer length**: word count sanity signal
- **Grounding check**: overlap with expected grounding terms
- **Keyword coverage**: expected business-term recall in answer

Run offline eval using sample answers:

```bash
python -m eval.eval_runner
```

Run live eval against your Bedrock Agent:

```bash
python -m eval.eval_runner --use-live-agent --session-id portfolio-eval-session
```

Dataset lives in [`eval/eval_dataset.json`](eval/eval_dataset.json).

## Limitations

- Metrics are heuristic and not a substitute for human review.
- Grounding check relies on keyword overlap, not citation verification.
- No automatic provisioning of AWS resources in this repository.
- Action-group execution is modeled and documented, but exact behavior depends on your configured agent tools.

## Future Improvements

1. Add citation-aware evaluation using Bedrock traces and source metadata.
2. Expand test coverage with mocked `bedrock-agent-runtime` responses.
3. Add CI pipeline (lint + unit tests + evaluation report artifact).
4. Add structured telemetry (latency, token usage, error rates).
5. Add guardrail validation and policy conformance checks.
