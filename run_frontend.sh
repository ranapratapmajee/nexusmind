#!/bin/bash

# path: run_frontend.sh
set -euo pipefail

# 1. Paths & Configurations
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$PROJECT_DIR/.env"

clear
echo "NexusMind FRONTEND Boot Sequence Initialized..."
echo "----------------------------------------------------"

# 2. Load Environment Variables
if [ -f "$ENV_FILE" ]; then
    echo "• Loading environment variables (.env)..."
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

UI_PORT="8501"
cd "$PROJECT_DIR"

# 3. Clean up stale frontend ports
echo "• Cleaning up stale frontend instances..."
pkill -f "streamlit run frontend/streamlit_app.py" || true

# 4. Sync Workspace Dependencies
uv sync --quiet

# 5. Graceful Teardown Definition
cleanup() {
    echo -e "\n\n🛑 Stopping NexusMind UI..."
    pkill -f "streamlit run frontend/streamlit_app.py" || true
    echo "✅ Frontend teardown finalized."
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "--------------------------------------"
echo "✅ UI Dashboard running on : http://localhost:$UI_PORT"
echo "Press [CTRL+C] to exit UI."
echo "--------------------------------------"

# 6. Launch Browser (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    sleep 1.5
    open "http://localhost:$UI_PORT" &
fi

# 7. Launch Streamlit (Foreground)
ENV_FLAG=""
if [ -f "$ENV_FILE" ]; then ENV_FLAG="--env-file $ENV_FILE"; fi

uv run $ENV_FLAG streamlit run frontend/streamlit_app.py \
    --server.port "$UI_PORT" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false