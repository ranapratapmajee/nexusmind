# path: app/api/chat_routes.py
import os
import re
import shutil

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.chat.chat_app import build_chat_options_response, handle_chat_request
from app.config.settings import settings
from app.rag.ingest import ingest_documents
from app.schemas.api_schemas import ChatOptionsResponse, ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chat"])


@router.get("/chat/options", response_model=ChatOptionsResponse)
async def chat_options() -> ChatOptionsResponse:
    return build_chat_options_response()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:

    # Execute the graph
    response = await handle_chat_request(req)
    return response


@router.post("/rag/upload", tags=["rag"])
async def upload_file_stream(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
):
    """Accepts single binary file uploads from the frontend workspace bar."""
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid transmission: Missing target filename format.",
        )

    target_dir = settings.research.offline_pdf_dir_env
    if not os.path.isdir(target_dir):
        target_dir = "./data"
    os.makedirs(target_dir, exist_ok=True)

    # 🧼 SANITIZE FILENAME: Cleans whitespace anomalies to protect file system operations
    safe_filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", file.filename)
    file_path = os.path.join(target_dir, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Kick off processing in a non-blocking background worker thread pool
    background_tasks.add_task(ingest_documents, target_dir)

    return {
        "status": "queued",
        "file_name": safe_filename,
        "message": "File written safely to disk cluster. Vector indexing initialized in background tasks loop.",
    }


@router.post("/rag/trigger-scan", tags=["rag"])
async def trigger_local_scan(background_tasks: BackgroundTasks):
    """Triggers an instantaneous scan over your local storage path variable allocation."""
    target_dir = settings.research.offline_pdf_dir_env
    if not os.path.isdir(target_dir):
        target_dir = "./data"

    background_tasks.add_task(ingest_documents, target_dir)
    return {
        "status": "processing",
        "directory": target_dir,
        "message": "Local collection parsing engine active.",
    }
