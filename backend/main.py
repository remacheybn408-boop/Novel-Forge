"""v0.6.0 WebUI Backend — FastAPI server for local filesystem operations."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import fs, chapters, review

app = FastAPI(title="Novel Pipeline Backend", version="0.6.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(fs.router)
app.include_router(chapters.router)
app.include_router(review.router)

@app.get("/api/status")
def api_status():
    return {"ok": True, "version": "v0.6.0-webui-preview", "engine_version": "v0.5.5", "mode": "local"}
