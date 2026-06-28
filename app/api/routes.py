# filename: app/api/routes.py

import os
import re
import json
import shutil
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse

from app.settings import settings
from app.core_graph import get_master_graph
from app.state_models import GlobalState, ChatPathSelection, ModelTierSelection
from app.api.schemas import ChatRequest
from app.rag_storage import run_ingest

logger = logging.getLogger("nexusmind.routes")
router = APIRouter(prefix="/api", tags=["chat"])
master_graph = get_master_graph()

@router.get("/chat/options")
async def get_chat_options():
    """
    Delivers rich presentation metadata directly to the client interface.
    Keeps the frontend UI completely decoupled from internal configuration names.
    """
    # Map raw Enum values directly to presentation titles
    mode_labels = {
        ChatPathSelection.AUTO.value: "🧠 Auto Orchestrate",
        ChatPathSelection.NEXA_CHAT.value: "✨ Nexa Chat",
        ChatPathSelection.RESEARCH.value: "🔬 Deep Research"
    }
    
    model_labels = {
        ModelTierSelection.AUTO.value: "🤖 Auto Model",
        ModelTierSelection.LOCAL.value: "💻 Local Model",
        ModelTierSelection.CLOUD.value: "☁️ Cloud Model"
    }

    return {
        "default_chat_selection": ChatPathSelection.AUTO.value,
        "default_model_selection": ModelTierSelection.AUTO.value,
        "available_chat_paths": [
            {"id": e.value, "label": mode_labels.get(e.value, e.value)} 
            for e in ChatPathSelection
        ],
        "available_model_tiers": [
            {"id": e.value, "label": model_labels.get(e.value, e.value)} 
            for e in ModelTierSelection
        ]
    }

@router.post("/chat")
async def handle_chat_message_stream(req: ChatRequest):
    """Streams token deltas directly, handling client UI payload translation values cleanly."""
    
    initial_state = GlobalState(
        raw_user_query=req.message,
        pipeline_context={
            "chat_selection": req.chat_selection,
            "model_selection": req.model_selection
        }
    )
    graph_config = {"configurable": {"thread_id": req.session_id}}

    async def event_generator():
        try:
            async for event in master_graph.astream_events(initial_state, graph_config, version="v2"):
                kind = event.get("event")
                metadata = event.get("metadata", {})
                active_node = metadata.get("langgraph_node")
                
                # Case A: Metrics Tracking Profile
                if kind == "on_chain_end" and event.get("name") == "LangGraph":
                    final_output = event["data"].get("output", {})
                    metrics = final_output.get("performance_metrics_ms", {})
                    yield f"data: {json.dumps({'type': 'metrics', 'data': metrics})}\n\n"

                # Case B: Conversational Token Streams Only
                elif kind == "on_chat_model_stream":
                    if active_node in ["fast_conversational", "execute_research_subgraph", "synthesize_research"]:
                        token_chunk = event["data"].get("chunk")
                        if token_chunk and token_chunk.content:
                            yield f"data: {json.dumps({'type': 'token', 'delta': token_chunk.content})}\n\n"

            yield "data: [DONE]\n\n"
            
        except Exception as graph_err:
            logger.error(f"Streaming sequence error: {graph_err}")
            # FIXED: Changed key from 'detail' to 'reply' to match frontend structural expectations
            yield f"data: {json.dumps({'type': 'error', 'reply': f'💥 Processing Pipeline Fault: {str(graph_err)}'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/rag/upload", tags=["rag"])
async def stream_rag_upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Transmission rejected: Missing proper filename metadata payload.")

    target_dir = os.path.abspath(settings.OFFLINE_PDF_DIR)
    os.makedirs(target_dir, exist_ok=True)

    safe_filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", file.filename)
    file_path = os.path.join(target_dir, safe_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hardware file writing fault execution error: {str(e)}")

    background_tasks.add_task(run_ingest, file_path)

    return {
        "status": "queued",
        "file_name": safe_filename,
        "message": f"Document saved cleanly to '{target_dir}'. Background generation processing pipeline spawned."
    }