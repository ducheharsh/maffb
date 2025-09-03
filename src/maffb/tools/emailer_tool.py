import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
import os
from crewai.tools import BaseTool
from pathlib import Path
import json
from datetime import datetime
from jinja2 import Template
from pydantic import Field
from typing import Optional, List, Dict, Any


class EmailerTool(BaseTool):
    name: str = "Emailer Tool"
    description: str = "Send blog summaries via email using HTML templates to emailer list recipients"
    
    # Define all attributes as Pydantic fields
    sg: Optional[sendgrid.SendGridAPIClient] = Field(default=None)
    from_email: str = Field(default="blogs@harshduche.com")
    subject: str = Field(default="Your Daily Blog Summaries - Maffb")
    
    def __init__(self, **data):
        super().__init__(**data)
        # Initialize SendGrid client if API key is available
        api_key = os.getenv("SENDGRID_API_KEY")
        if api_key:
            self.sg = sendgrid.SendGridAPIClient(api_key=api_key)
        else:
            print("Warning: SENDGRID_API_KEY not found in environment variables")
        
        # Override subject if environment variable is set
        env_subject = os.getenv("SUBJECT")
        if env_subject:
            self.subject = env_subject
        
        # Override from_email if environment variable is set
        env_from_email = os.getenv("FROM_EMAIL")
        if env_from_email:
            self.from_email = env_from_email

    def _run(self, blog_summaries: Optional[List[Dict[str, Any]]] = None, custom_subject: Optional[str] = None) -> str:
        """
        Send blog summaries via email to recipients from emailer_list.json
        
        Args:
            blog_summaries: List of blog summary dictionaries
            custom_subject: Optional custom subject line
        """
        try:
            # Check if SendGrid is initialized
            if not self.sg:
                return "Error: SendGrid not initialized. Please set SENDGRID_API_KEY environment variable."
            
            # Load emailer list
            emailer_list_path = Path(__file__).parent.parent.parent.parent / "knowledge" / "emailer_list.json"
            
            if not emailer_list_path.exists():
                return "Error: emailer_list.json file not found"
                
            with open(emailer_list_path, 'r') as f:
                emailer_list = json.load(f)
            
            # Load HTML template
            html_template_path = Path(__file__).parent / "templates" / "email_template.html"
            
            if not html_template_path.exists():
                return "Error: email_template.html not found"
                
            with open(html_template_path, 'r') as f:
                html_template_content = f.read()
            
            # Prepare template data
            template_data = {
                "generation_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
                "total_blogs": len(blog_summaries) if blog_summaries else 0,
                "blog_summaries": blog_summaries or []
            }
            
            # Render template
            html_template = Template(html_template_content)
            html_content = html_template.render(**template_data)
            
            # Send emails to all recipients in emailer_list.json
            success_count = 0
            for emailer in emailer_list:
                recipient_email = emailer["email"]
                recipient_name = emailer.get("name", "Recipient")
                
                try:
                    # Create email with HTML content
                    message = Mail(
                        from_email=self.from_email,
                        to_emails=recipient_email,
                        subject=custom_subject or self.subject,
                        html_content=html_content
                    )
                    
                    response = self.sg.send(message)
                    
                    if response.status_code in [200, 201, 202]:
                        success_count += 1
                        print(f"✅ Email sent successfully to {recipient_email} ({recipient_name})")
                    else:
                        try:
                            response_body = response.body.decode("utf-8") if hasattr(response.body, "decode") else str(response.body)
                        except Exception:
                            response_body = "<unreadable body>"
                        print(f"❌ Failed to send email to {recipient_email} ({recipient_name}): {response.status_code} - {response_body}")
                        
                except Exception as e:
                    print(f"❌ Error sending email to {recipient_email} ({recipient_name}): {str(e)}")
                    continue
            
            if success_count > 0:
                return f"Successfully sent emails to {success_count} recipients from emailer_list.json"
            else:
                return "Failed to send emails to any recipients"
                
        except Exception as e:
            return f"Error in emailer tool: {str(e)}"
 