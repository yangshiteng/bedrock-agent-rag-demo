# AWS Manual Setup

This repository does **not** create AWS resources automatically. Complete these steps manually in the AWS console before running local code.

## Step 1: Create Bedrock Agent

1. Open AWS Console -> Amazon Bedrock -> Agents.
2. Choose **Create agent**.
3. Configure:
   - Agent name (for example `business-knowledge-assistant`)
   - Model (choose a model available in your region)
   - Agent instructions for business-policy Q&A behavior
4. Save and create the agent.

## Step 2: Attach Knowledge Base

1. In the agent configuration, open **Knowledge bases**.
2. Attach an existing Bedrock Knowledge Base, or create a new one.
3. Ensure your business documents are indexed and queryable.
4. Confirm retrieval is enabled for the agent.

## Step 3: Create Action Group

1. Open **Action groups** in the agent configuration.
2. Create an action group for tool use (Lambda/API/function schema).
3. Define operation schema clearly (inputs/outputs).
4. Add at least one tool-oriented operation (for example financial calculator or policy lookup).

## Step 4: Deploy Agent Alias

1. Build/prepare the latest draft agent version.
2. Create or update an alias (for example `prod` or `demo`).
3. Deploy the alias so it can be invoked via runtime API.

## Step 5: Get `AGENT_ID` and `AGENT_ALIAS_ID`

1. Copy the agent ID from the Bedrock Agent details page.
2. Copy the alias ID from the alias details page.
3. Set local environment variables in `.env`:
   - `BEDROCK_AGENT_ID=<agent-id>`
   - `BEDROCK_AGENT_ALIAS_ID=<agent-alias-id>`
   - `AWS_REGION=<your-region>`

## Validation Checklist

- You can see an active agent alias in Bedrock console.
- Knowledge Base is attached and queryable.
- Action group is configured and enabled.
- Your IAM identity can call `bedrock-agent-runtime:InvokeAgent`.
