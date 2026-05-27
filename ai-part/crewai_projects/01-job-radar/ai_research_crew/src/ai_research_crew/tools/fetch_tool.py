"""
fetch_tool.py — WebFetchTool
Fetches and cleans the text content of any URL.

Teaching note: This is a custom CrewAI BaseTool.
  - BaseTool requires a `name`, `description`, `args_schema`, and `_run()` method.
  - The agent calls this tool by providing a `url` argument.
  - The tool returns plain text (HTML stripped) up to 4 000 characters.
"""
import re
import httpx
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class FetchInput(BaseModel):
    url: str = Field(description="The full URL of the webpage to fetch and extract text from")


class WebFetchTool(BaseTool):
    """
    Fetches plain-text content from a given URL.

    Use when you have a direct URL to:
    - A job posting page
    - A company careers page
    - A salary survey or market report
    Returns up to 4 000 characters of clean text.
    """

    name: str = "Fetch Web Page"
    description: str = (
        "Fetches the text content of a given URL and returns up to 4 000 characters. "
        "Use when you have a specific URL to a job posting, careers page, or resource."
    )
    args_schema: type[BaseModel] = FetchInput

    def _run(self, url: str) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
        }
        try:
            with httpx.Client(timeout=12, follow_redirects=True) as client:
                resp = client.get(url, headers=headers)
                resp.raise_for_status()

            # Strip scripts, styles, and HTML tags — leave plain text
            text = re.sub(r"<script[^>]*>.*?</script>", " ", resp.text, flags=re.DOTALL)
            text = re.sub(r"<style[^>]*>.*?</style>",  " ", text,      flags=re.DOTALL)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\s+",     " ", text).strip()

            return text[:4000] if len(text) > 4000 else text

        except httpx.HTTPStatusError as e:
            return f"HTTP error fetching {url}: {e.response.status_code}"
        except httpx.TimeoutException:
            return f"Timeout fetching {url} — the site may be slow or blocking requests."
        except Exception as e:
            return f"Error fetching {url}: {type(e).__name__}: {e}"
