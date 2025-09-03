# Email Setup for Maffb

## Quick Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set environment variable:**
```bash
export SENDGRID_API_KEY="your_sendgrid_api_key_here"
```

3. **Verify emailer list:**
The system will send emails to all recipients in `knowledge/emailer_list.json`

## Current Configuration

- **Sender Email:** Set via `FROM_EMAIL` env var (must be verified in SendGrid)
- **Recipients:** All emails in `knowledge/emailer_list.json`
- **Template:** `src/maffb/tools/templates/email_template.html`

## How It Works

1. **Blogs Collector** gathers RSS content
2. **Blogs Analyst** analyzes content  
3. **Blogs Summarizer** creates summaries
4. **Blogs Summary Emailer** sends emails to all recipients

## SendGrid Setup

1. Create a SendGrid account
2. Create an API key with Mail Send permissions
3. Verify a sender (Single Sender) or a domain that matches `FROM_EMAIL`
4. Set the API key as environment variable
   - Local: `export SENDGRID_API_KEY="<your_key>"`
   - GitHub Actions: add `SENDGRID_API_KEY` in repo Settings → Secrets and variables → Actions

## Configure sender address

Set the from address (must be verified with SendGrid):

```bash
export FROM_EMAIL="blogs@harshduche.com"  # or your verified sender
```

## Test the System

Run the crew to test email functionality:
```bash
python -m src.maffb.main
```

If you see HTTP 401/403 errors:
- 401 Unauthorized: The API key is missing/invalid. Re-check `SENDGRID_API_KEY` value and scope.
- 403 Forbidden: The `FROM_EMAIL` sender is not verified or lacks permission.

Quick checks:
- `echo ${#SENDGRID_API_KEY}` should be > 0; key typically starts with `SG.`
- Ensure `FROM_EMAIL` matches a verified Single Sender or your verified domain.
- In GitHub Actions, confirm the secret exists and is exported in the workflow.
