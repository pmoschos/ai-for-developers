"""
Streaming Endpoint
==================
Demonstrates streaming responses in FastAPI using Server-Sent Events.
"""

import logging
import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, AsyncGenerator

from app.llm_client import get_llm_client
from openai import OpenAI

logger = logging.getLogger(__name__)
router = APIRouter()


class StreamRequest(BaseModel):
    """Request model for streaming generation"""
    prompt: str = Field(..., min_length=1, description="The prompt to generate from")
    system_prompt: Optional[str] = Field(
        default=None,
        description="Optional system prompt"
    )
    max_tokens: Optional[int] = Field(default=500, ge=1, le=2000)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "prompt": "Explain machine learning in simple terms",
                "system_prompt": "You are a helpful teacher",
                "max_tokens": 300
            }
        }
    }


async def generate_stream(
    prompt: str,
    system_prompt: Optional[str] = None,
    max_tokens: int = 500
) -> AsyncGenerator[str, None]:
    """Generate streaming response using Server-Sent Events format"""
    client = OpenAI()
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=max_tokens,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                # Send as Server-Sent Event
                yield f"data: {json.dumps({'content': content})}\n\n"
        
        # Send completion signal
        yield f"data: {json.dumps({'done': True})}\n\n"
        
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


@router.post("")
async def stream_response(request: StreamRequest):
    """
    Stream a response token-by-token using Server-Sent Events.
    
    The response is sent as a stream of JSON events:
    - `{"content": "token"}` for each token
    - `{"done": true}` when complete
    - `{"error": "message"}` if an error occurs
    
    Example client code:
    ```javascript
    const response = await fetch('/stream', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({prompt: 'Hello'})
    });
    
    const reader = response.body.getReader();
    while (true) {
        const {done, value} = await reader.read();
        if (done) break;
        const text = new TextDecoder().decode(value);
        // Parse SSE data
    }
    ```
    """
    return StreamingResponse(
        generate_stream(
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            max_tokens=request.max_tokens
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# Also add a simple HTML page to test streaming
STREAMING_TEST_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Streaming Test</title>
    <style>
        body { font-family: system-ui; max-width: 800px; margin: 50px auto; padding: 20px; }
        #output { white-space: pre-wrap; background: #f5f5f5; padding: 20px; border-radius: 8px; min-height: 100px; }
        textarea { width: 100%; height: 100px; margin: 10px 0; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <h1>🌊 Streaming Response Test</h1>
    <textarea id="prompt" placeholder="Enter your prompt...">Explain what an API is in simple terms.</textarea>
    <button onclick="streamResponse()">Stream Response</button>
    <h3>Output:</h3>
    <div id="output"></div>
    
    <script>
        async function streamResponse() {
            const prompt = document.getElementById('prompt').value;
            const output = document.getElementById('output');
            output.textContent = '';
            
            const response = await fetch('/stream', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({prompt: prompt})
            });
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            while (true) {
                const {done, value} = await reader.read();
                if (done) break;
                
                const text = decoder.decode(value);
                const lines = text.split('\\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.slice(6));
                        if (data.content) {
                            output.textContent += data.content;
                        }
                    }
                }
            }
        }
    </script>
</body>
</html>
"""


@router.get("/test")
async def streaming_test_page():
    """Serve a test page for streaming"""
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=STREAMING_TEST_HTML)
