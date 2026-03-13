# bedrock-agent-business-assistant

Portfolio-style Python project showing how an application integrates with an existing AWS Bedrock Agent for business knowledge Q&A, retrieval-augmented generation, and tool-assisted reasoning.

This repository is designed for interview walkthroughs and realistic architecture discussions. It assumes the Bedrock Agent, Knowledge Base, and action groups are already configured in AWS, and focuses on the application layer that invokes and evaluates the agent.

## Why This Project

This project demonstrates:

- Invoking a Bedrock Agent from Python with `boto3`
- Designing an application around agent orchestration rather than direct model prompting
- Explaining how retrieval and action-group tool use work together in a business assistant
- Evaluating RAG-style answers with lightweight, understandable metrics
- Documenting the real-world constraint that some AWS resources are often configured manually

## Architecture

High-level request flow:

`User -> Application -> Bedrock Agent Runtime -> Agent reasoning -> Knowledge Base retrieval -> Action group tools -> Response`

Detailed walkthrough: [`architecture/architecture.md`](architecture/architecture.md)

## Repository Layout

```text
bedrock-agent-business-assistant/
  README.md
  LICENSE
  RELEASE.md
  .env.example
  requirements.txt
  src/
  eval/
  examples/
  architecture/
  docs/
  scripts/
  tests/
```

## AWS Resources Required

You need these existing AWS resources before local execution:

1. Bedrock Agent
2. Agent alias that is deployed and active
3. Bedrock Knowledge Base attached to the agent
4. At least one action group for tool use scenarios
5. IAM permissions to call `bedrock-agent-runtime:InvokeAgent`

## Manual AWS Setup

Full setup guide: [`docs/aws_manual_setup.md`](docs/aws_manual_setup.md)

Summary:

1. Create a Bedrock Agent in the AWS console.
2. Attach a Knowledge Base containing business documents.
3. Create an action group for business tools or API-backed operations.
4. Deploy an agent alias.
5. Copy `BEDROCK_AGENT_ID` and `BEDROCK_AGENT_ALIAS_ID` into `.env`.

## Local Setup

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
copy .env.example .env
```

Set these environment variables in `.env`:

- `AWS_REGION`
- `BEDROCK_AGENT_ID`
- `BEDROCK_AGENT_ALIAS_ID`
- `BEDROCK_SESSION_ID` (optional)

## Run The Demo

Single question:

```bash
python -m src.invoke_agent --question "What policy applies to vendor risk reviews?"
```

Interactive session:

```bash
python -m src.invoke_agent --interactive
```

Multi-question demo script:

```bash
python scripts/run_demo.py
```

## Example Prompts

More prompts: [`examples/sample_questions.md`](examples/sample_questions.md)

- What is the internal definition of quarterly net revenue?
- What policy applies to vendor risk reviews?
- If a department spent $12,000 with a 10% contingency, what is the total?

## Evaluation Approach

The evaluation logic is intentionally simple and easy to explain in interviews:

- `answer length`: checks whether the response is meaningfully populated
- `grounding check`: measures overlap with expected source-related terms
- `keyword coverage`: measures whether important business concepts appear in the answer

Offline evaluation with sample answers:

```bash
python -m eval.eval_runner
```

Live evaluation against your configured Bedrock Agent:

```bash
python -m eval.eval_runner --use-live-agent --session-id portfolio-eval-session
```

Evaluation dataset: [`eval/eval_dataset.json`](eval/eval_dataset.json)

## What Makes This Realistic

- The repository does not pretend all AWS resources are created automatically.
- The code is modular enough for production-style discussion: config, logging, runtime client, invocation flow, tools, and evaluation are separated.
- The demo includes both retrieval-driven questions and tool-friendly calculation questions.

## Limitations

- Evaluation metrics are heuristic and not substitutes for human judgment.
- Grounding is inferred from keyword overlap rather than citation verification.
- Action-group behavior depends on how your Bedrock Agent is configured in AWS.
- This repository does not provision cloud resources with Terraform or CloudFormation.

## Future Improvements

1. Add citation-aware evaluation using Bedrock traces and source metadata.
2. Expand test coverage with mocked `bedrock-agent-runtime` responses.
3. Add CI for tests and linting.
4. Add structured observability for latency and failure analysis.
5. Add guardrail and policy-compliance checks.

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE).
