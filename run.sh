#!/bin/bash
# path: run.sh
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$PROJECT_DIR/.env"
cd "$PROJECT_DIR"

clear
echo "NexusMind Boot Sequence Initialized..."
echo "------------------------------------------------------------"

# 1. LOAD ENVIRONMENT VARIABLES VIA BUILTINS
if [ -f "$ENV_FILE" ]; then
    echo "• Loading environment variables (.env)..."
    set -a; source "$ENV_FILE"; set +a
fi

export TOKENIZERS_PARALLELISM=false
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
export PYTHONPATH="$PROJECT_DIR"

CHROMA_PORT=${CHROMA_PORT:-8000}
API_PORT=${API_PORT:-8001}
OLLAMA_PORT="11434"
UI_PORT="8501"

is_port_in_use() { lsof -ti :"$1" >/dev/null 2>&1; }

# 2. CLEAN PREVIOUS RUNS
echo "• Cleaning up stale application ports..."
pkill -f "uvicorn app.main:app" || true
pkill -f "streamlit run frontend/streamlit_app.py" || true

echo "• Verifying environment structures..."
uv sync --quiet

# 3. INFRASTRUCTURE CHECKS (Docker & Ollama)
if ! docker info >/dev/null 2>&1; then
    echo "🚨 Error: Docker Desktop is not running. Please launch it manually."
    exit 1
fi

if is_port_in_use "$CHROMA_PORT"; then
    echo "• Connection verified: ChromaDB active on port $CHROMA_PORT."
else
    echo "• Booting containerized ChromaDB..."
    docker compose up -d >/dev/null 2>&1
fi

if is_port_in_use "$OLLAMA_PORT"; then
    echo "• Connection verified: Ollama active on port $OLLAMA_PORT."
else
    echo "• Initializing local Ollama daemon..."
    nohup ollama serve >/dev/null 2>&1 &
fi

# Wait for infrastructure sockets
for i in {1..10}; do
    if is_port_in_use "$CHROMA_PORT" && is_port_in_use "$OLLAMA_PORT"; then break; fi
    sleep 1
done

# 4. RUN APPLICATIONS IN BACKGROUND
ENV_FLAG=${ENV_FILE:+"--env-file $ENV_FILE"}

echo "• Mounting FastAPI gateway..."
uv run $ENV_FLAG uvicorn app.main:app --host 0.0.0.0 --port "$API_PORT" &
API_PID=$!

for i in {1..10}; do if is_port_in_use "$API_PORT"; then break; fi; sleep 1; done

echo "• Deploying Streamlit dashboard client..."
uv run $ENV_FLAG streamlit run streamlit_app.py \
    --server.port "$UI_PORT" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false &
UI_PID=$!

if [[ "$OSTYPE" == "darwin"* ]]; then
    sleep 1.5
    open "http://localhost:$UI_PORT"
fi

echo "--------------------------------------"
echo "NexusMind Platform Online"
echo "UI Dashboard : http://localhost:$UI_PORT"
echo "Backend API  : http://localhost:$API_PORT"
echo "Press [CTRL+C] to exit and stop completely."
echo "--------------------------------------"

# 5. GRACEFUL TEARDOWN TRAFFIC CONTROL
cleanup() {
    echo -e "\n\n🛑 Stopping NexusMind Application services..."
    kill "$API_PID" "$UI_PID" 2>/dev/null || true
    pkill -f "uvicorn app.main:app" || true
    pkill -f "streamlit run frontend/streamlit_app.py" || true
    
    echo "🐳 Stopping ChromaDB containers (Waiting for complete shutdown)..."
    # Removed redirection to let Docker finish in foreground cleanly
    docker compose down 
    
    echo "✅ Clean teardown finalized. All resources released."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep script alive and responsive to traps cleanly without background forks
while kill -0 "$API_PID" 2>/dev/null || kill -0 "$UI_PID" 2>/dev/null; do
    sleep 1
done