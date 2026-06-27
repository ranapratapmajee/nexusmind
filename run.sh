#!/bin/bash
# path: run_nexusmind.sh
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$PROJECT_DIR/.env"

clear
echo "NexusMind Boot Sequence Initialized (Docker Desktop Mode)..."
echo "------------------------------------------------------------"

# =========================================================================
# 2. LOAD ENVIRONMENT VARIABLES FIRST (Safe Multi-Line Evaluation Bounds)
# =========================================================================
if [ -f "$ENV_FILE" ]; then
    echo "• Loading environment variables (.env)..."
    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ "$line" =~ ^#.*$ ]] && continue
        [[ -z "$line" ]] && continue
        export "$line"
    done < "$ENV_FILE"
fi

export TOKENIZERS_PARALLELISM=false
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

CHROMA_PORT=${CHROMA_PORT:-8000}
API_PORT=${API_PORT:-8001}
OLLAMA_PORT="11434"
UI_PORT="8501"

cd "$PROJECT_DIR"
is_port_in_use() { lsof -ti :"$1" >/dev/null 2>&1; }

echo "• Cleaning up stale application ports..."
pkill -f "uvicorn app.main:app" || true
pkill -f "streamlit run frontend/streamlit_app.py" || true

echo "• Verifying project environment package structures (uv sync)..."
uv sync --quiet

# =========================================================================
# 3. INFRASTRUCTURE VALIDATION (Docker Desktop Core Engine)
# =========================================================================

# Check if Docker Desktop daemon is even running first
if ! docker info >/dev/null 2>&1; then
    echo "🚨 Error: Docker Desktop does not appear to be running."
    echo "   Please launch the Docker Desktop application manually and try again."
    exit 1
fi

# ChromaDB Verification Loop
if is_port_in_use "$CHROMA_PORT"; then
    echo "• Connection verified: Vector Database active on port $CHROMA_PORT."
else
    echo "• Booting containerized ChromaDB cluster via Docker Desktop..."
    docker compose up -d >/dev/null 2>&1
fi

# Ollama Verification Loop
if is_port_in_use "$OLLAMA_PORT"; then
    echo "• Connection verified: Ollama Core Daemon active on port $OLLAMA_PORT."
else
    echo "• Initializing local Ollama background server daemon..."
    nohup ollama serve >/dev/null 2>&1 &
fi

echo "• Waiting for database and engine sockets to open..."
for i in {1..10}; do
    if is_port_in_use "$CHROMA_PORT" && is_port_in_use "$OLLAMA_PORT"; then break; fi
    sleep 1
done

echo ""
echo "--------------------------------------"
echo "NexusMind Platform Online (Docker Desktop Engine)"
echo "UI Dashboard : http://localhost:$UI_PORT"
echo "Backend API  : http://localhost:$API_PORT"
echo "Press [CTRL+C] to exit and stop completely."
echo "--------------------------------------"
echo "Streaming Live Logs..."
echo ""

ENV_FLAG=""
if [ -f "$ENV_FILE" ]; then ENV_FLAG="--env-file $ENV_FILE"; fi

echo "• Mounting FastAPI application gateway..."
export PYTHONPATH="$PROJECT_DIR"
uv run $ENV_FLAG uvicorn app.main:app --host 0.0.0.0 --port "$API_PORT" &
API_PID=$!

for i in {1..10}; do if is_port_in_use "$API_PORT"; then break; fi; sleep 1; done

echo "• Deploying Streamlit dashboard client..."
uv run $ENV_FLAG streamlit run frontend/streamlit_app.py \
    --server.port "$UI_PORT" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false &
UI_PID=$!

if [[ "$OSTYPE" == "darwin"* ]]; then
    sleep 1.5
    open "http://localhost:$UI_PORT"
fi

# =========================================================================
# 4. GRACEFUL TEARDOWN MANAGEMENT
# =========================================================================
cleanup() {
    echo -e "\n\n🛑 Stopping NexusMind Application services..."
    kill "$API_PID" 2>/dev/null || true
    kill "$UI_PID" 2>/dev/null || true
    pkill -f "uvicorn app.main:app" || true
    pkill -f "streamlit run frontend/streamlit_app.py" || true
    
    echo "🐳 Stopping ChromaDB containers..."
    docker compose down >/dev/null 2>&1 || true
    
    echo "✅ Clean teardown finalized. Application resources released."
    exit 0
}

trap cleanup SIGINT SIGTERM
wait