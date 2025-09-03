from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
from datetime import datetime
import re

class ReadmeUpdaterInput(BaseModel):
    summary_content: str = Field(..., description="The blog summary content to add to the README")
    date: str = Field(default="", description="Date for the summary (defaults to today)")
    title: str = Field(default="Daily Engineering Blog Digest", description="Title for the daily summary")

class ReadmeUpdaterTool(BaseTool):
    name: str = "README Updater Tool"
    description: str = "Updates the README with daily blog summaries, maintaining beautiful markdown formatting and organization"
    args_schema: Type[BaseModel] = ReadmeUpdaterInput

    def _run(self, summary_content: str, date: str = "", title: str = "Daily Engineering Blog Digest") -> str:
        """
        Update the README with a new daily blog summary.
        
        Args:
            summary_content: The blog summary content to add
            date: Optional date for the summary
            title: Title for the daily summary
            
        Returns:
            Confirmation message about the README update
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            # Format the summary content
            formatted_summary = self._format_daily_summary(summary_content, title, date)
            
            # Update the README
            updated_readme = self._update_readme_content(formatted_summary)
            
            # Write the updated README
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(updated_readme)
            
            return f"✅ README successfully updated with daily blog summary for {date}. The summary has been added to the README with beautiful markdown formatting."
            
        except Exception as e:
            return f"❌ Error updating README: {str(e)}"

    def _format_daily_summary(self, content: str, title: str, date: str) -> str:
        """Format the daily summary with beautiful markdown."""
        formatted = f"### 📰 {title} - {date}\n\n"
        
        # Split content into sections and format
        sections = content.split('\n\n')
        for section in sections:
            if section.strip():
                # Format headings
                if section.strip().startswith('#'):
                    level = len(section) - len(section.lstrip('#'))
                    if level == 1:
                        formatted += f"#### {section.strip('#').strip()}\n\n"
                    elif level == 2:
                        formatted += f"##### {section.strip('#').strip()}\n\n"
                    else:
                        formatted += f"###### {section.strip('#').strip()}\n\n"
                # Format lists
                elif section.strip().startswith(('- ', '* ', '1. ')):
                    formatted += f"{section.strip()}\n"
                # Format URLs
                elif 'http' in section and any(word in section.lower() for word in ['blog', 'post', 'article']):
                    formatted += f"🔗 **Source:** {section.strip()}\n\n"
                # Format emphasis
                elif '**' in section or '__' in section:
                    formatted += f"{section.strip()}\n\n"
                # Regular text
                else:
                    formatted += f"{section.strip()}\n\n"
        
        return formatted.strip()

    def _update_readme_content(self, formatted_summary: str) -> str:
        """Update the README content with the new daily summary."""
        readme_path = "README.md"
        
        if not os.path.exists(readme_path):
            # Create a new README if it doesn't exist
            return self._create_new_readme(formatted_summary)
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            current_readme = f.read()
        
        # Check if daily summary section exists
        if "## 📅 Daily Blog Summary" in current_readme:
            # Update existing summary section
            return self._update_existing_summary_section(current_readme, formatted_summary)
        else:
            # Insert new summary section
            return self._insert_new_summary_section(current_readme, formatted_summary)

    def _create_new_readme(self, formatted_summary: str) -> str:
        """Create a new README with the daily summary section."""
        return f"""# Maffb - Multi-Agent Fleet for Blogs

Maffb is an intelligent blog content processing system built with CrewAI that automatically collects, analyzes, and summarizes engineering blog posts from RSS feeds.

## 📅 Daily Blog Summary

{formatted_summary}

## Features

- **Automated RSS Feed Collection**: Monitors multiple engineering blogs for new content
- **AI-Powered Analysis**: Extracts key insights and trends from blog posts
- **Smart Summarization**: Creates concise, informative summaries with source attribution
- **Email Delivery**: Sends daily digests to subscribers
- **Fallback Mechanism**: Always provides content, even when no new posts are available
- **Daily README Updates**: Automatically updates README with latest summaries

## Automated Workflow

### GitHub Actions Cron Job

The system includes an automated GitHub Actions workflow that runs every morning at **8:00 AM IST (2:30 AM UTC)** to:

1. **Collect** latest blog posts from RSS feeds
2. **Analyze** content for key insights and trends
3. **Summarize** posts with proper source attribution
4. **Email** summaries to subscribers
5. **Update** README with daily summaries
6. **Archive** results for 7 days

## Architecture

### Agents

- **Blogs Collector**: Monitors RSS feeds and collects latest posts
- **Blogs Analyst**: Extracts insights and identifies trends
- **Blogs Summarizer**: Creates concise summaries with source attribution
- **Blogs Summary Emailer**: Sends processed content via email
- **README Updater**: Maintains daily summary updates in README

### Tools

- **RSS Feed Extractor**: Intelligent RSS feed discovery and parsing
- **Emailer Tool**: SendGrid integration for email delivery
- **Markdown Formatter**: Beautiful markdown formatting for summaries
- **README Updater**: Automatic README maintenance with daily summaries

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

## License

This project is licensed under the MIT License.
"""

    def _update_existing_summary_section(self, current_readme: str, formatted_summary: str) -> str:
        """Update the existing daily summary section."""
        # Find the daily summary section and replace it
        pattern = r"(## 📅 Daily Blog Summary\n\n)(.*?)(?=\n## |\n### |$)"
        
        # Get today's date for the section header
        today = datetime.now().strftime("%Y-%m-%d")
        new_summary_section = f"## 📅 Daily Blog Summary\n\n{formatted_summary}\n\n"
        
        if re.search(pattern, current_readme, re.DOTALL):
            # Replace existing content
            updated_readme = re.sub(pattern, new_summary_section, current_readme, flags=re.DOTALL)
        else:
            # Fallback: append to the end
            updated_readme = current_readme + f"\n\n{new_summary_section}"
        
        return updated_readme

    def _insert_new_summary_section(self, current_readme: str, formatted_summary: str) -> str:
        """Insert a new daily summary section after the main description."""
        # Find the best insertion point (after the main description, before Features)
        insert_point = current_readme.find("## Features")
        
        if insert_point != -1:
            before = current_readme[:insert_point]
            after = current_readme[insert_point:]
            return f"{before}\n## 📅 Daily Blog Summary\n\n{formatted_summary}\n\n{after}"
        else:
            # Fallback: add at the end
            return f"{current_readme}\n\n## 📅 Daily Blog Summary\n\n{formatted_summary}\n\n"

    def get_readme_stats(self) -> str:
        """Get statistics about the README and daily summaries."""
        try:
            with open("README.md", "r", encoding="utf-8") as f:
                content = f.read()
            
            # Count daily summaries
            summary_count = len(re.findall(r"### 📰 .*? - \d{4}-\d{2}-\d{2}", content))
            
            # Get the latest summary date
            latest_dates = re.findall(r"### 📰 .*? - (\d{4}-\d{2}-\d{2})", content)
            latest_date = max(latest_dates) if latest_dates else "No summaries yet"
            
            return f"📊 README Statistics:\n- Total daily summaries: {summary_count}\n- Latest summary date: {latest_date}\n- README size: {len(content)} characters"
            
        except Exception as e:
            return f"❌ Error reading README stats: {str(e)}"
