#!/bin/bash

# path: run_nexusmind.sh
set -euo pipefail

# 1. Paths & Configurations
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$PROJECT_DIR/app/config/config.yaml"
ENV_FILE="$PROJECT_DIR/.env"

clear
echo "NexusMind Boot Sequence Initialized (Colima Mode)..."
echo "----------------------------------------------------"

# 2. LOAD ENVIRONMENT VARIABLES FIRST
if [ -f "$ENV_FILE" ]; then
    echo "• Loading environment variables (.env)..."
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# macOS AI Safety Overrides
export TOKENIZERS_PARALLELISM=false
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Cannot locate config.yaml at $CONFIG_FILE"
    exit 1
fi

# 3. COLIMA ENVIRONMENT ROUTING SETUP
# Forces the local docker context client to look at Colima's user space socket
export DOCKER_HOST="unix://$HOME/.colima/default/docker.sock"

# 4. Extract Ports
CHROMA_PORT=${CHROMA_PORT:-8000}
API_PORT=${API_PORT:-8001}
OLLAMA_PORT="11434"
UI_PORT="8501"

cd "$PROJECT_DIR"
is_port_in_use() { lsof -ti :"$1" >/dev/null 2>&1; }

# 5. Shutdown Dangling Instances
echo "• Cleaning up stale application ports..."
pkill -f "uvicorn app.main:app" || true
pkill -f "streamlit run frontend/streamlit_app.py" || true

# 6. Sync Workspace Dependencies
echo "• Verifying project environment package structures (uv sync)..."
uv sync --quiet

# 7. Infrastructure Validation
# ChromaDB Layer (Colima Managed Engine)
if is_port_in_use "$CHROMA_PORT"; then
    echo "• Connection verified: Vector Database active on port $CHROMA_PORT."
else
    if ! colima status >/dev/null 2>&1; then
        echo "• Colima engine down. Spawning lightweight macOS virtual machine..."
        colima start --cpu 2 --memory 4 --vm-type vz --mount-type virtiofs >/dev/null 2>&1
        docker context use colima >/dev/null 2>&1
    fi
    echo "• Booting containerized ChromaDB cluster..."
    docker compose up -d >/dev/null 2>&1
fi

# Ollama Layer
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

# Print Dashboard BEFORE starting the noisy services
echo ""
echo "--------------------------------------"
echo "NexusMind Platform Online (Colima Engine)"
echo "UI Dashboard : http://localhost:$UI_PORT"
echo "Backend API  : http://localhost:$API_PORT"
echo "Press [CTRL+C] to exit and stop completely."
echo "--------------------------------------"
echo "Streaming Live Logs..."
echo ""

# 8. Launch Services
ENV_FLAG=""
if [ -f "$ENV_FILE" ]; then ENV_FLAG="--env-file $ENV_FILE"; fi

# Start Backend API IN THE BACKGROUND
echo "• Mounting FastAPI application gateway..."
export PYTHONPATH="$PROJECT_DIR"
uv run $ENV_FLAG uvicorn app.main:app --host 0.0.0.0 --port "$API_PORT" &
API_PID=$!

# Wait for API to be fully online before booting Streamlit
for i in {1..10}; do if is_port_in_use "$API_PORT"; then break; fi; sleep 1; done

# Start Frontend UI IN THE BACKGROUND
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

# 9. Graceful Teardown
cleanup() {
    echo -e "\n\n🛑 Stopping NexusMind Application services..."
    kill "$API_PID" 2>/dev/null || true
    kill "$UI_PID" 2>/dev/null || true
    pkill -f "uvicorn app.main:app" || true
    pkill -f "streamlit run frontend/streamlit_app.py" || true

    echo "🐳 Stopping and removing ChromaDB database containers..."
    docker compose down >/dev/null 2>&1 || true

    echo "🔌 Powering down Colima Virtual Machine environment..."
    colima stop >/dev/null 2>&1 || true

    echo "✅ Clean teardown finalized. All hardware resources released."
    exit 0
}

# Bind the cleanup function to CTRL+C
trap cleanup SIGINT SIGTERM

# Hold the script open to stream logs and wait for termination signals
wait