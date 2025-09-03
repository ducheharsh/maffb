# Maffb - Multi-Agent Fleet for Blogs

Maffb is an intelligent blog content processing system built with CrewAI that automatically collects, analyzes, and summarizes engineering blog posts from RSS feeds.

## Features

- **Automated RSS Feed Collection**: Monitors multiple engineering blogs for new content
- **AI-Powered Analysis**: Extracts key insights and trends from blog posts
- **Smart Summarization**: Creates concise, informative summaries with source attribution
- **Email Delivery**: Sends daily digests to subscribers
- **Fallback Mechanism**: Always provides content, even when no new posts are available

## Automated Workflow

### GitHub Actions Cron Job

The system includes an automated GitHub Actions workflow that runs every morning at **8:00 AM IST (2:30 AM UTC)** to:

1. **Collect** latest blog posts from RSS feeds
2. **Analyze** content for key insights and trends
3. **Summarize** posts with proper source attribution
4. **Email** summaries to subscribers
5. **Archive** results for 7 days

### Setup Instructions

1. **Fork/Clone** this repository to your GitHub account
2. **Add Secrets** in your repository settings:
   - Go to `Settings` → `Secrets and variables` → `Actions`
   - Add `SENDGRID_API_KEY` with your SendGrid API key
3. **Enable Actions** in your repository settings
4. **Customize** the workflow schedule in `.github/workflows/cron_job.yaml` if needed

### Manual Execution

You can also trigger the workflow manually:
- Go to `Actions` tab in your repository
- Select "Maffb Daily Blog Processing"
- Click "Run workflow"

## Architecture

### Agents

- **Blogs Collector**: Monitors RSS feeds and collects latest posts
- **Blogs Analyst**: Extracts insights and identifies trends
- **Blogs Summarizer**: Creates concise summaries with source attribution
- **Blogs Summary Emailer**: Sends processed content via email

### Tools

- **RSS Feed Extractor**: Intelligent RSS feed discovery and parsing
- **Emailer Tool**: SendGrid integration for email delivery

## Configuration

### Blog Sources

Edit `knowledge/blog_sources.json` to add or remove engineering blogs:

```json
[
  {
    "name": "Blog Name",
    "url": "https://blog-url.com"
  }
]
```

### Email Recipients

Edit `knowledge/emailer_list.json` to manage email subscribers:

```json
[
  {
    "name": "Recipient Name",
    "email": "recipient@example.com"
  }
]
```

## Development

### Prerequisites

- Python 3.10+
- uv package manager

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd maffb

# Install dependencies
uv sync

# Run the crew
uv run run_crew
```

### Environment Variables

- `SENDGRID_API_KEY`: Your SendGrid API key for email functionality
- `FROM_EMAIL`: Verified sender email address in SendGrid
- `SUBJECT`: Custom email subject line (optional)

## Output

The system generates:
- **Blog summaries** in markdown format
- **Analysis reports** with key insights
- **Email digests** sent to subscribers
- **Artifacts** stored in GitHub Actions for 7 days

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `uv run run_crew`
5. Submit a pull request

## License

This project is licensed under the MIT License.
