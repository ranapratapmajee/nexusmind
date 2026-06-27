# path: app/api/routes.py

import os
import re
import shutil
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from app.settings import settings
from app.core_graph import get_master_graph
from app.state_models import GlobalState
from app.api.schemas import ChatOptionsResponse, ChatRequest, ChatResponse
from app.rag_storage import run_ingest  # 🟢 Import the unified ingest workflow tool

router = APIRouter(prefix="/api", tags=["chat"])
master_graph = get_master_graph()

@router.get("/chat/options", response_model=ChatOptionsResponse)
async def get_chat_options() -> ChatOptionsResponse:
    return ChatOptionsResponse(
        default_model_id=settings.OLLAMA_MODEL,
        default_mode="chat",
        available_modes=["chat", "deep_research"],
        available_models=[settings.OLLAMA_MODEL, settings.GEMINI_MODEL]
    )

@router.post("/chat", response_model=ChatResponse)
async def handle_chat_message(req: ChatRequest) -> ChatResponse:
    initial_state = GlobalState(
        session_id=req.session_id,
        raw_user_query=req.message,
        ui_requested_mode=req.mode,
        allocated_model_id=req.model_id if req.model_id != "auto" else settings.OLLAMA_MODEL
    )
    try:
        output_dict = await master_graph.ainvoke(initial_state)
        return ChatResponse(
            reply=output_dict.get("final_assistant_reply", ""),
            trace_logs=output_dict.get("chronological_trace_logs", []),
            metrics=output_dict.get("performance_metrics_ms", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph Processing Fault: {str(e)}")


@router.post("/rag/upload", tags=["rag"])
async def stream_rag_upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Receives engineering source documents, flushes them to disk registers inside 
    the configured file folder space, and boots the async vector processing pipelines.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Transmission rejected: Missing proper filename metadata payload.")

    # 1. Resolve targeting folder layout parameters (Resolves to your configuration path e.g., './data')
    target_dir = os.path.abspath(settings.OFFLINE_PDF_DIR)
    os.makedirs(target_dir, exist_ok=True)

    # Sanitize inputs to guarantee zero path traversal vulnerabilities
    safe_filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", file.filename)
    file_path = os.path.join(target_dir, safe_filename)

    # 2. Write incoming streaming chunks from memory directly onto target disk space
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware file writing fault execution error: {str(e)}")

    # 3. 🟢 LINK TO INGEST PIPELINE: Hand the file path straight down to the background process
    # The server responds instantly to the Streamlit sidebar, keeping the UI snappy
    background_tasks.add_task(run_ingest, file_path)

    return {
        "status": "queued",
        "file_name": safe_filename,
        "message": f"Document saved cleanly to '{target_dir}'. Background generation processing pipeline spawned."
    }