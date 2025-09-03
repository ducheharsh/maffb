from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import re
from datetime import datetime
import os

class MarkdownFormatterInput(BaseModel):
    content: str = Field(..., description="The content to format as markdown")
    format_type: str = Field(default="summary", description="Type of formatting: 'summary', 'readme', or 'general'")
    title: str = Field(default="", description="Title for the formatted content")
    date: str = Field(default="", description="Date for the content (optional)")

class MarkdownFormatterTool(BaseTool):
    name: str = "Markdown Formatter Tool"
    description: str = "Formats content into beautiful, well-structured markdown with proper headings, lists, and formatting"
    args_schema: Type[BaseModel] = MarkdownFormatterInput

    def _run(self, content: str, format_type: str = "summary", title: str = "", date: str = "") -> str:
        """
        Format content into beautiful markdown based on the specified type.
        
        Args:
            content: The raw content to format
            format_type: Type of formatting ('summary', 'readme', or 'general')
            title: Optional title for the content
            date: Optional date for the content
            
        Returns:
            Formatted markdown content
        """
        if format_type == "summary":
            return self._format_summary(content, title, date)
        elif format_type == "readme":
            return self._format_readme_update(content, title, date)
        else:
            return self._format_general(content, title, date)

    def _format_summary(self, content: str, title: str, date: str) -> str:
        """Format content as a blog summary with proper structure."""
        formatted = ""
        
        if title:
            formatted += f"# {title}\n\n"
        
        if date:
            formatted += f"**Date:** {date}\n\n"
        
        # Split content into sections and format
        sections = content.split('\n\n')
        for section in sections:
            if section.strip():
                # Check if it's a heading
                if section.strip().startswith(('##', '###', '####')):
                    formatted += f"{section.strip()}\n\n"
                # Check if it's a list item
                elif section.strip().startswith(('- ', '* ', '1. ')):
                    formatted += f"{section.strip()}\n"
                # Check if it's a URL
                elif 'http' in section and any(word in section.lower() for word in ['blog', 'post', 'article']):
                    formatted += f"🔗 **Source:** {section.strip()}\n\n"
                # Regular paragraph
                else:
                    formatted += f"{section.strip()}\n\n"
        
        return formatted.strip()

    def _format_readme_update(self, content: str, title: str, date: str) -> str:
        """Format content for README updates with daily summaries."""
        today = date if date else datetime.now().strftime("%Y-%m-%d")
        
        formatted = f"## 📅 Daily Blog Summary - {today}\n\n"
        
        if title:
            formatted += f"### {title}\n\n"
        
        # Format the content with proper markdown
        lines = content.split('\n')
        for line in lines:
            if line.strip():
                # Format headings
                if line.strip().startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    if level == 1:
                        formatted += f"### {line.strip('#').strip()}\n\n"
                    elif level == 2:
                        formatted += f"#### {line.strip('#').strip()}\n\n"
                    else:
                        formatted += f"##### {line.strip('#').strip()}\n\n"
                # Format lists
                elif line.strip().startswith(('- ', '* ', '1. ')):
                    formatted += f"{line.strip()}\n"
                # Format URLs
                elif 'http' in line:
                    formatted += f"🔗 **Source:** {line.strip()}\n\n"
                # Format emphasis
                elif '**' in line or '__' in line:
                    formatted += f"{line.strip()}\n\n"
                # Regular text
                else:
                    formatted += f"{line.strip()}\n\n"
        
        return formatted.strip()

    def _format_general(self, content: str, title: str, date: str) -> str:
        """General markdown formatting for any content."""
        formatted = ""
        
        if title:
            formatted += f"# {title}\n\n"
        
        if date:
            formatted += f"**Date:** {date}\n\n"
        
        # Basic formatting
        lines = content.split('\n')
        for line in lines:
            if line.strip():
                # Auto-detect and format headings
                if line.strip().isupper() and len(line.strip()) < 100:
                    formatted += f"## {line.strip()}\n\n"
                # Format lists
                elif line.strip().startswith(('- ', '* ', '1. ')):
                    formatted += f"{line.strip()}\n"
                # Format URLs
                elif 'http' in line:
                    formatted += f"🔗 {line.strip()}\n\n"
                # Regular text
                else:
                    formatted += f"{line.strip()}\n\n"
        
        return formatted.strip()

    def update_readme_with_summary(self, summary_content: str, date: str = None) -> str:
        """
        Update the README with a new daily summary section.
        
        Args:
            summary_content: The formatted summary content
            date: Optional date for the summary
            
        Returns:
            Updated README content
        """
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Read current README
        readme_path = "README.md"
        if os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as f:
                current_readme = f.read()
        else:
            current_readme = "# Maffb - Multi-Agent Fleet for Blogs\n\n"
        
        # Find the right place to insert the summary (after the main description)
        if "## 📅 Daily Blog Summary" in current_readme:
            # Update existing summary section
            pattern = r"(## 📅 Daily Blog Summary.*?)(?=\n## |\n### |$)"
            replacement = f"## 📅 Daily Blog Summary\n\n{summary_content}\n\n"
            updated_readme = re.sub(pattern, replacement, current_readme, flags=re.DOTALL)
        else:
            # Insert new summary section after the main description
            insert_point = current_readme.find("## Features")
            if insert_point != -1:
                before = current_readme[:insert_point]
                after = current_readme[insert_point:]
                updated_readme = f"{before}\n## 📅 Daily Blog Summary\n\n{summary_content}\n\n{after}"
            else:
                # Fallback: add at the end
                updated_readme = f"{current_readme}\n\n## 📅 Daily Blog Summary\n\n{summary_content}\n\n"
        
        return updated_readme
