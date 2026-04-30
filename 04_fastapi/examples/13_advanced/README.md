# 13 — Advanced Features

Run any example:
```bash
uvicorn examples.13_advanced.file_upload:app --reload
uvicorn examples.13_advanced.static_templates:app --reload
uvicorn examples.13_advanced.websocket_chat:app --reload
```

```bash
# File upload demo
uvicorn file_upload:app --reload

# Static files + Jinja2 templates
# Example: http://127.0.0.1:8000/page/Alice
uvicorn static_templates:app --reload

# WebSocket chat
uvicorn websocket_chat:app --reload
```