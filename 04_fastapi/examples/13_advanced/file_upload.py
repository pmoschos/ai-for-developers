"""
13 — Advanced: File Uploads

Run:  uvicorn examples.13_advanced.file_upload:app --reload

Try in /docs:
  POST /upload → upload a single file
  POST /upload-many → upload multiple files
"""

from fastapi import FastAPI, UploadFile

app = FastAPI(title="File Uploads")


@app.post("/upload")
async def upload(file: UploadFile):
    """
    UploadFile streams the body — ideal for large files.
    Access file.filename, file.content_type, and file.read().
    """
    contents = await file.read()
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
    }


@app.post("/upload-many")
async def upload_many(files: list[UploadFile]):
    """Upload multiple files at once."""
    results = []
    for f in files:
        data = await f.read()
        results.append({"name": f.filename, "size": len(data)})
    return results
