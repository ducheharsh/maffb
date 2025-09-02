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

- **Sender Email:** `ducheharsh@gmail.com` (fixed)
- **Recipients:** All emails in `emailer_list.json`
- **Template:** `src/maffb/templates/email_template.html`

## How It Works

1. **Blogs Collector** gathers RSS content
2. **Blogs Analyst** analyzes content  
3. **Blogs Summarizer** creates summaries
4. **Blogs Summary Emailer** sends emails to all recipients

## SendGrid Setup

1. Create a SendGrid account
2. Get your API key
3. Verify your sender domain (ducheharsh@gmail.com)
4. Set the API key as environment variable

## Test the System

Run the crew to test email functionality:
```bash
python -m src.maffb.main
```
