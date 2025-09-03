import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
from python_http_client.exceptions import HTTPError
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
    eu_residency: bool = Field(default=False)
    
    def __init__(self, **data):
        super().__init__(**data)
        # Initialize SendGrid client if API key is available
        api_key = os.getenv("SENDGRID_API_KEY")

        # EU data residency toggle via env (SENDGRID_EU_RESIDENCY=true)
        self.eu_residency = os.getenv("SENDGRID_EU_RESIDENCY", "false").lower() in ("1", "true", "yes")

        # If EU residency is enabled, direct the client to EU API base before instantiation
        if self.eu_residency:
            os.environ["SENDGRID_API_BASE_URL"] = "https://api.eu.sendgrid.com"

        if api_key:
            self.sg = sendgrid.SendGridAPIClient(api_key=api_key)
            # Also set residency on the client if supported
            if self.eu_residency and hasattr(self.sg, "set_sendgrid_data_residency"):
                try:
                    self.sg.set_sendgrid_data_residency("eu")
                except Exception:
                    pass
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
        else:
            # Encourage explicit, verified sender configuration
            if self.from_email == "blogs@harshduche.com":
                print(
                    "Warning: FROM_EMAIL not set. Set a verified sender via FROM_EMAIL env var to avoid 401 errors."
                )

        # Warn if API key looks suspiciously short
        if api_key and len(api_key) < 60:
            print("Warning: SENDGRID_API_KEY length looks short; ensure the full key was copied.")

    def _switch_region_and_reinit(self) -> None:
        """
        Toggle between US and EU API base URL and re-initialize the SendGrid client.
        """
        api_key = os.getenv("SENDGRID_API_KEY")
        self.eu_residency = not self.eu_residency
        if self.eu_residency:
            os.environ["SENDGRID_API_BASE_URL"] = "https://api.eu.sendgrid.com"
        else:
            # Clear to default US API base
            os.environ.pop("SENDGRID_API_BASE_URL", None)
        self.sg = sendgrid.SendGridAPIClient(api_key=api_key)
        if self.eu_residency and hasattr(self.sg, "set_sendgrid_data_residency"):
            try:
                self.sg.set_sendgrid_data_residency("eu")
            except Exception:
                pass

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
            
            # Load emailer list (project_root/knowledge/emailer_list.json)
            emailer_list_path = Path(__file__).parent.parent.parent.parent / "knowledge" / "emailer_list.json"
            
            if not emailer_list_path.exists():
                return "Error: emailer_list.json file not found"
                
            with open(emailer_list_path, 'r') as f:
                emailer_list = json.load(f)

            # Validate recipient list
            if not isinstance(emailer_list, list) or len(emailer_list) == 0:
                return "Email delivery failed. A recipient email list is required to complete this task."
            
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
                    
                    # Send message
                    response = self.sg.send(message)
                    
                    if response.status_code in [200, 201, 202]:
                        success_count += 1
                        print(f"✅ Email sent successfully to {recipient_email} ({recipient_name})")
                    else:
                        try:
                            response_body = response.body.decode("utf-8") if hasattr(response.body, "decode") else str(response.body)
                        except Exception:
                            response_body = "<unreadable body>"
                        error_prefix = ""
                        if response.status_code == 401:
                            error_prefix = (
                                "Hint: 401 Unauthorized often means an invalid API key or unverified FROM_EMAIL. "
                                "Ensure SENDGRID_API_KEY has Mail Send permission and FROM_EMAIL is a verified sender/domain. "
                            )
                        print(
                            f"❌ Failed to send email to {recipient_email} ({recipient_name}): "
                            f"{response.status_code} - {error_prefix}{response_body}"
                        )
                        
                except HTTPError as e:
                    # Try to surface detailed SendGrid error body
                    try:
                        body = e.body.decode("utf-8") if hasattr(e.body, "decode") else str(e.body)
                    except Exception:
                        body = str(e)
                    # Auto-retry with alternate region for regional attribute errors
                    if "regional attribute" in body.lower() and getattr(e, 'status_code', 0) == 401:
                        print("ℹ️ Detected regional mismatch. Switching API region and retrying once...")
                        self._switch_region_and_reinit()
                        try:
                            message = Mail(
                                from_email=self.from_email,
                                to_emails=recipient_email,
                                subject=custom_subject or self.subject,
                                html_content=html_content
                            )
                            retry_response = self.sg.send(message)
                            if retry_response.status_code in [200, 201, 202]:
                                success_count += 1
                                print(
                                    f"✅ Email sent successfully to {recipient_email} ({recipient_name}) after switching region"
                                )
                                continue
                            else:
                                try:
                                    retry_body = (
                                        retry_response.body.decode("utf-8")
                                        if hasattr(retry_response.body, "decode")
                                        else str(retry_response.body)
                                    )
                                except Exception:
                                    retry_body = "<unreadable body>"
                                print(
                                    f"❌ Failed to send email to {recipient_email} ({recipient_name}) after region switch: "
                                    f"{retry_response.status_code} - {retry_body}"
                                )
                                continue
                        except Exception as re:
                            print(
                                f"❌ Error after region switch for {recipient_email} ({recipient_name}): {str(re)}"
                            )
                            continue
                    else:
                        print(
                            f"❌ Error sending email to {recipient_email} ({recipient_name}): {getattr(e, 'status_code', 'HTTPError')} - {body}"
                        )
                        continue
                except Exception as e:
                    print(
                        f"❌ Error sending email to {recipient_email} ({recipient_name}): {str(e)}"
                    )
                    continue
            
            if success_count > 0:
                return f"Successfully sent emails to {success_count} recipients from emailer_list.json"
            else:
                return "Failed to send emails to any recipients"
                
        except Exception as e:
            return f"Error in emailer tool: {str(e)}"


if __name__ == "__main__":
    # Simple CLI smoke test to validate SendGrid setup
    # Usage: python -m src.maffb.tools.emailer_tool
    tool = EmailerTool()
    test_summary = [{
        "title": "Maffb SendGrid Smoke Test",
        "url": "https://example.com",
        "summary": "This is a test message to verify SendGrid configuration.",
        "source": "system"
    }]
    print(tool._run(blog_summaries=test_summary, custom_subject=os.getenv("SUBJECT", "Maffb SendGrid Smoke Test")))
 