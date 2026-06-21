# path: scripts/run_ingest.py
import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from app.config.settings import settings
from app.rag.ingest import ingest_documents

# Force load the system configurations into the shell profile thread
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


async def main() -> None:
    """Direct terminal execution script to parse local documents."""
    target_dir = settings.research.offline_pdf_dir_env

    if not os.path.isdir(target_dir):
        target_dir = "./data"

    print("🚀 NexusMind Local Data Source Indexer")
    print(f"├── Target Ingestion Directory: {os.path.abspath(target_dir)}")
    print("└── Initializing token vector extraction matrix...")
    print("-" * 80)

    try:
        await ingest_documents(directory=target_dir)
        print("-" * 80)
        print("🎉 Ingestion Pipeline processing loop finalized successfully.")
    except Exception as e:
        print("-" * 80)
        print(f"❌ Critical Exception Fault intercepted during execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
