#!/bin/bash

# path: run_backend.sh
set -euo pipefail

# 1. Paths & Configurations
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$PROJECT_DIR/app/config/config.yaml"
ENV_FILE="$PROJECT_DIR/.env"

clear
echo "NexusMind BACKEND Boot Sequence Initialized..."
echo "----------------------------------------------------"

# 2. Load Environment Variables & macOS Patches
if [ -f "$ENV_FILE" ]; then
    echo "• Loading environment variables (.env)..."
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

export TOKENIZERS_PARALLELISM=false
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Cannot locate config.yaml at $CONFIG_FILE"
    exit 1
fi

# 3. Colima Environment Setup
export DOCKER_HOST="unix://$HOME/.colima/default/docker.sock"

# 4. Extract Ports
CHROMA_PORT=${CHROMA_PORT:-8000}
API_PORT=${API_PORT:-8001}
OLLAMA_PORT="11434"

cd "$PROJECT_DIR"
is_port_in_use() { lsof -ti :"$1" >/dev/null 2>&1; }

# 5. Clean up stale backend ports
echo "• Cleaning up stale backend ports..."
pkill -f "uvicorn app.main:app" || true

# 6. Sync Workspace Dependencies
uv sync --quiet

# 7. Infrastructure Validation (ChromaDB & Ollama)
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

if is_port_in_use "$OLLAMA_PORT"; then
    echo "• Connection verified: Ollama active on port $OLLAMA_PORT."
else
    echo "• Initializing local Ollama background server..."
    nohup ollama serve >/dev/null 2>&1 &
fi

echo "• Waiting for databases to spin up..."
for i in {1..10}; do
    if is_port_in_use "$CHROMA_PORT" && is_port_in_use "$OLLAMA_PORT"; then break; fi
    sleep 1
done

# 8. Graceful Teardown Definition
cleanup() {
    echo -e "\n\n🛑 Stopping NexusMind Backend services..."
    pkill -f "uvicorn app.main:app" || true
    echo "🐳 Stopping ChromaDB containers..."
    docker compose down >/dev/null 2>&1 || true
    echo "🔌 Powering down Colima Virtual Machine..."
    colima stop >/dev/null 2>&1 || true
    echo "✅ Backend teardown finalized."
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "--------------------------------------"
echo "✅ Backend API running on : http://localhost:$API_PORT"
echo "Press [CTRL+C] to stop infrastructure."
echo "--------------------------------------"

# 9. Launch FastAPI (Foreground)
ENV_FLAG=""
if [ -f "$ENV_FILE" ]; then ENV_FLAG="--env-file $ENV_FILE"; fi

export PYTHONPATH="$PROJECT_DIR"
uv run $ENV_FLAG uvicorn app.main:app --host 0.0.0.0 --port "$API_PORT"