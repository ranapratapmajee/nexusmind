# path: ./run_ingest.py

import asyncio
import sys
import os
import logging  # 🟢 Added explicit logging setup

from app.settings import settings
from app.rag_storage import run_ingest

async def main():
    # 🟢 Configure logging format bounds so logger.info() messages print to stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    print("====== Nexa Mind RAG Processing Engine ======")
    target_dir = os.path.abspath(settings.OFFLINE_PDF_DIR)
    print(f"Scanning storage path target: '{target_dir}'...\n")
    
    # Invokes the concurrent ingest pipeline worker
    await run_ingest(target_dir)
    print("\n=============================================")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        settings.OFFLINE_PDF_DIR = sys.argv[1]
        
    asyncio.run(main())