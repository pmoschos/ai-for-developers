"""
13 — Advanced: WebSocket Echo / Broadcast

Run:  uvicorn examples.13_advanced.websocket_chat:app --reload

Open http://127.0.0.1:8000/ in multiple browser tabs to chat.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI(title="WebSocket Chat")

# Connected clients
clients: list[WebSocket] = []

# A simple HTML page for testing WebSocket
HTML = """
<!DOCTYPE html>
<html>
<head><title>WebSocket Chat</title></head>
<body>
    <h1>WebSocket Chat</h1>
    <input id="msg" type="text" placeholder="Type a message..." />
    <button onclick="send()">Send</button>
    <ul id="log"></ul>
    <script>
        const ws = new WebSocket("ws://localhost:8000/ws");
        ws.onmessage = (e) => {
            const li = document.createElement("li");
            li.textContent = e.data;
            document.getElementById("log").appendChild(li);
        };
        function send() {
            const input = document.getElementById("msg");
            ws.send(input.value);
            input.value = "";
        }
    </script>
</body>
</html>
"""


@app.get("/")
def home():
    """Serve the chat HTML page."""
    return HTMLResponse(HTML)


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    """
    Bidirectional WebSocket endpoint.
    - Accepts connection
    - Broadcasts every message to all connected clients
    - Removes client on disconnect
    """
    await ws.accept()
    clients.append(ws)
    try:
        while True:
            msg = await ws.receive_text()
            # Broadcast to all connected clients
            for client in clients:
                await client.send_text(f">> {msg}")
    except WebSocketDisconnect:
        clients.remove(ws)
