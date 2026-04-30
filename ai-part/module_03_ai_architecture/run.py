"""
Run Script
==========
Easy startup script for the AI API server.
"""

import uvicorn

if __name__ == "__main__":
    print("""
    +--------------------------------------------------------+
    |           AI-Powered API Server                        |
    |                                                        |
    |   Docs: http://localhost:8000/docs                     |
    |   API:  http://localhost:8000                          |
    |                                                        |
    |   Press Ctrl+C to stop                                 |
    +--------------------------------------------------------+
    """)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
