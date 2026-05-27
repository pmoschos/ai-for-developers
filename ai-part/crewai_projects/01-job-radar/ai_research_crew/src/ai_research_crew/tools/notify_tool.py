"""
notify_tool.py — NotificationTool
Sends the final roadmap report via ntfy.sh (push) and Resend (email).

Teaching note: This tool is called by the last agent (Roadmap Writer) AFTER
  the report is written to disk. It demonstrates:
  1. How to call external REST APIs from a CrewAI tool
  2. Graceful degradation — works fine even if keys are not configured
  3. httpx for async-compatible HTTP calls
"""
import os
import json
import re
import httpx
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class NotifyInput(BaseModel):
    subject: str = Field(description="Subject line for the report delivery")
    body_markdown: str = Field(description="Full Markdown content of the roadmap report")
    alert_message: str = Field(
        description=(
            "Short alert message (max 200 chars). "
            "E.g. 'JobRadar: Python Backend Dev, 62% ready. Top gap: FastAPI. Roadmap ready!'"
        )
    )


class NotificationTool(BaseTool):
    """
    Dispatches the finished roadmap report via two channels:

    1. ntfy.sh  — free, open-source push notifications (no account needed for public topics)
    2. Resend   — modern transactional email API (free tier: 3 000 emails/month)

    Both channels degrade gracefully if env vars are not set.
    Call exactly ONCE, after the roadmap file has been saved.
    """

    name: str = "Dispatch Roadmap Report"
    description: str = (
        "Sends the completed career roadmap report via ntfy.sh push notification "
        "and Resend email. Call exactly once after the report has been saved."
    )
    args_schema: type[BaseModel] = NotifyInput

    # ── ntfy.sh Push ──────────────────────────────────────────────────────────
    def _send_push(self, alert_message: str, subject: str) -> str:
        topic = os.getenv("NTFY_TOPIC")
        if not topic:
            return "[i]  Push skipped — NTFY_TOPIC not set in .env"

        token   = os.getenv("NTFY_TOKEN", "")
        headers = {
            "Title":        subject[:250],
            "Priority":     "high",
            "Tags":         "briefcase,chart_with_upwards_trend",
            "Content-Type": "text/plain",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            resp = httpx.post(
                f"https://ntfy.sh/{topic}",
                content=alert_message[:500].encode("utf-8"),
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 200:
                return f"[OK] Push sent via ntfy.sh (topic: {topic})"
            return f"[!]  ntfy.sh failed — HTTP {resp.status_code}"
        except Exception as e:
            return f"[!]  ntfy.sh error: {e}"

    # ── Resend Email ──────────────────────────────────────────────────────────
    def _send_email(self, subject: str, body_markdown: str) -> str:
        api_key   = os.getenv("RESEND_API_KEY")
        from_addr = os.getenv("REPORT_FROM") or os.getenv("REPORT_FROM_EMAIL")
        to_addr   = os.getenv("REPORT_TO")   or os.getenv("REPORT_TO_EMAIL")

        if not (api_key and from_addr and to_addr):
            return "[!]  Email skipped — RESEND_API_KEY / REPORT_FROM / REPORT_TO not set"

        html_body = self._md_to_html(body_markdown)

        try:
            resp = httpx.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type":  "application/json",
                },
                content=json.dumps({
                    "from":    from_addr,
                    "to":      [to_addr],
                    "subject": subject,
                    "html":    html_body,
                }).encode("utf-8"),
                timeout=15,
            )
            data = resp.json()
            if resp.status_code in (200, 201) and data.get("id"):
                return f"✅ Email sent via Resend to {to_addr}"
            return f"⚠️  Resend failed — HTTP {resp.status_code}: {data}"
        except Exception as e:
            return f"⚠️  Resend error: {e}"

    @staticmethod
    def _md_to_html(md: str) -> str:
        """Minimal Markdown → HTML conversion (no external dependency needed)."""
        html = md
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$",  r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.+)$",   r"<h1>\1</h1>", html, flags=re.MULTILINE)
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*",     r"<em>\1</em>",         html)
        html = re.sub(r"^[-•] (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
        html = re.sub(r"\n\n+", "</p><p>", html)
        return f"<div style='font-family:sans-serif;max-width:760px'><p>{html}</p></div>"

    # Entry point for the tool
    def _run(self, subject: str, body_markdown: str, alert_message: str) -> str:
        push_result  = self._send_push(alert_message, subject)
        email_result = self._send_email(subject, body_markdown)
        return f"{push_result}\n{email_result}"
