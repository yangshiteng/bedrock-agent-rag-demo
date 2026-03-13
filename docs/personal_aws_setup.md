# Personal AWS Setup

This guide explains how to configure AWS access for personal learning and portfolio use.

Unlike a company environment, you usually do not need SSO, browser-based login, or Duo verification for a personal AWS account. The most common setup is a local AWS CLI profile backed by IAM access keys.

## When You Need This

Use this setup if:

- You created your own AWS account for learning
- You want to run this repository locally against your own Bedrock resources
- You want `boto3` to authenticate using a named local profile such as `personal`

## Recommended Approach

For personal use, the recommended flow is:

1. Create your own AWS account
2. Create an IAM user with programmatic access
3. Attach only the permissions needed for Bedrock usage
4. Configure a named AWS CLI profile
5. Run this project with `AWS_PROFILE=<your-profile>`

## Step 1: Create or Use Your AWS Account

Sign in to your personal AWS account and make sure Bedrock is available in your target region.

Suggested region examples:

- `us-east-1`
- `us-west-2`

## Step 2: Create an IAM User

1. Open AWS Console -> IAM -> Users
2. Create a new user for local development
3. Enable programmatic access if your account flow still presents that option
4. Create access keys for CLI or SDK usage

Store the following values safely:

- `AWS Access Key ID`
- `AWS Secret Access Key`

Do not commit these values into code, `.env`, or Git history.

## Step 3: Grant Permissions

At minimum, your local identity needs permission to invoke the Bedrock Agent runtime.

Typical permissions include access related to:

- `bedrock-agent-runtime:InvokeAgent`
- Bedrock read actions required to inspect resources if you use CLI commands

If your agent depends on additional AWS services, you may need more permissions depending on your setup.

## Step 4: Configure a Named AWS CLI Profile

If AWS CLI is installed locally, run:

```bash
aws configure --profile personal
```

You will be prompted for:

- Access key ID
- Secret access key
- Default region
- Output format

This creates a local named profile such as `personal`.

## Step 5: Use The Profile With This Project

Set the profile in your shell before running the app.

PowerShell:

```powershell
$env:AWS_PROFILE="personal"
python -m src.invoke_agent --question "What policy applies to vendor risk reviews?"
```

Or put it in your local `.env`:

```env
AWS_PROFILE=personal
AWS_REGION=us-east-1
BEDROCK_AGENT_ID=YOUR_AGENT_ID
BEDROCK_AGENT_ALIAS_ID=YOUR_AGENT_ALIAS_ID
```

## Do You Have To Use A Profile?

Strictly speaking, no.

`boto3` can also use:

- the default profile
- environment variables such as `AWS_ACCESS_KEY_ID`
- EC2 or container role credentials

But for personal development, using a named profile is usually the cleanest option because:

- it avoids hardcoding credentials
- it makes account switching easier
- it works well with both AWS CLI and `boto3`

## Personal Account vs Company SSO

Personal account:

- Usually uses IAM access keys
- Often configured with `aws configure --profile personal`
- Does not usually require browser login or Duo

Company account:

- Often uses AWS IAM Identity Center or SSO
- Common flow is `aws sso login --profile company-profile`
- May open a browser and require MFA or Duo approval

## Security Notes

- Never commit `.env` with real secrets
- Prefer least-privilege IAM permissions
- Rotate access keys if they are exposed
- If possible, create a separate IAM user for learning projects rather than using root credentials

## Project-Specific Reminder

This repository still assumes that the Bedrock Agent, alias, Knowledge Base, and action groups are created manually in AWS. This document only covers how your local machine authenticates to AWS when running the code.
