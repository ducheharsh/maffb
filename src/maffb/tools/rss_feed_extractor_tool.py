from crewai.tools import BaseTool
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import requests
import json
from pathlib import Path
import feedparser
from datetime import datetime, timezone


class RssFeedExtractorToolInput(BaseModel):
    """Input schema for RssFeedExtractorTool."""
    topic: str = Field(..., description="The topic to focus on when extracting RSS feeds.")
    max_posts: int = Field(default=10, description="Maximum number of posts to extract per blog.")

class RssFeedExtractorTool(BaseTool):
    name: str = "Rss Feed Extractor Tool"
    description: str = (
        "Extract RSS feeds from engineering blogs and return the latest posts with content."
    )
    args_schema: Type[BaseModel] = RssFeedExtractorToolInput
    
    # Pydantic configuration
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Define session as a proper Pydantic field
    session: requests.Session = Field(default_factory=requests.Session)

    def _run(self, topic: str, max_posts: int = 10) -> str:
        """
        Extract RSS feeds from engineering blogs and return latest posts.
        First tries to find today's posts, then falls back to latest posts if none found.
        
        Args:
            topic: The topic to focus on
            max_posts: Maximum number of posts per blog
            
        Returns:
            JSON string with extracted blog posts
        """
        try:
            # Load blog sources from JSON file
            blog_sources_path = Path(__file__).parent.parent.parent.parent / "knowledge" / "blog_sources.json"
            
            if not blog_sources_path.exists():
                return "Error: blog_sources.json file not found"
                
            with open(blog_sources_path, 'r') as f:
                blog_sources = json.load(f)
            
            extracted_posts = []
            
            for blog in blog_sources:
                blog_name = blog["name"]
                blog_url = blog["url"]
                
                # Try to find RSS feed
                rss_urls = self._find_rss_feed(blog_url)
                
                for rss_url in rss_urls:
                    try:
                        posts = self._extract_posts_from_rss(rss_url, blog_name, blog_url, topic, max_posts)
                        if posts:
                            extracted_posts.extend(posts)
                            break  # Use first working RSS feed
                    except Exception as e:
                        print(f"Error extracting from {rss_url}: {str(e)}")
                        continue
            
            if not extracted_posts:
                return "No posts found from any RSS feeds"
            
            # Sort by date (newest first)
            extracted_posts.sort(key=lambda x: x.get('published', ''), reverse=True)
            
            return json.dumps({
                "topic": topic,
                "total_posts": len(extracted_posts),
                "extraction_date": datetime.now().isoformat(),
                "posts": extracted_posts
            }, indent=2)
            
        except Exception as e:
            return f"Error in RSS feed extraction: {str(e)}"
    
    def _find_rss_feed(self, blog_url: str) -> List[str]:
        """Find potential RSS feed URLs for a blog."""
        # Common RSS feed patterns
        rss_patterns = [
            f"{blog_url}/rss",
            f"{blog_url}/feed",
            f"{blog_url}/rss.xml",
            f"{blog_url}/feed.xml",
            f"{blog_url}/atom.xml",
            f"{blog_url}/rss/",
            f"{blog_url}/feed/",
        ]
        
        # Also try to get RSS feed from HTML page
        try:
            response = self.session.get(blog_url, timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                # Look for RSS feed links in HTML
                if 'rss' in content or 'feed' in content:
                    # Add more specific patterns based on common HTML structures
                    rss_patterns.extend([
                        f"{blog_url}/rss/feed",
                        f"{blog_url}/feed/rss",
                        f"{blog_url}/blog/rss",
                        f"{blog_url}/blog/feed",
                    ])
        except:
            pass
        
        return rss_patterns
    
    def _extract_posts_from_rss(self, rss_url: str, blog_name: str, blog_url: str, topic: str, max_posts: int) -> List[Dict[str, Any]]:
        """Extract posts from a specific RSS feed URL."""
        try:
            response = self.session.get(rss_url, timeout=10)
            if response.status_code != 200:
                return []
            
            # Parse RSS feed
            feed = feedparser.parse(response.content)
            
            posts = []
            post_count = 0
            
            # First pass: try to find today's posts
            today_posts = []
            other_posts = []
            
            for entry in feed.entries:
                # Check if post is relevant to topic (basic keyword matching)
                title = entry.get('title', '').lower()
                summary = entry.get('summary', '').lower()
                content = entry.get('content', [{}])[0].get('value', '').lower() if entry.get('content') else ''
                
                # Simple relevance check
                if any(keyword in title or keyword in summary or keyword in content 
                       for keyword in topic.lower().split()):
                    
                    post = {
                        'title': entry.get('title', 'No Title'),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'summary': entry.get('summary', ''),
                        'blog_name': blog_name,
                        'blog_url': blog_url,
                        'rss_url': rss_url,
                        'extracted_at': datetime.now().isoformat()
                    }
                    
                    # Check if post is from today
                    if self._is_today(post['published']):
                        today_posts.append(post)
                    else:
                        other_posts.append(post)
            
            # Prioritize today's posts, then fall back to latest posts
            if today_posts:
                # Sort today's posts by time (newest first)
                today_posts.sort(key=lambda x: x.get('published', ''), reverse=True)
                posts = today_posts[:max_posts]
            else:
                # Fall back to latest posts regardless of date
                other_posts.sort(key=lambda x: x.get('published', ''), reverse=True)
                posts = other_posts[:max_posts]
            
            return posts
            
        except Exception as e:
            print(f"Error parsing RSS feed {rss_url}: {str(e)}")
            return []
    
    def _is_today(self, date_str: str) -> bool:
        """Check if the given date string represents today."""
        if not date_str:
            return False
        
        try:
            # Parse the date string using feedparser's date parsing
            parsed_date = feedparser._parse_date(date_str)
            if parsed_date:
                # Convert to timezone-aware datetime
                if parsed_date.tzinfo is None:
                    parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                
                # Get today's date in UTC
                today = datetime.now(timezone.utc).date()
                return parsed_date.date() == today
        except:
            pass
        
        return False
