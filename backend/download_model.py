"""
download_model.py
─────────────────
Run this ONCE to download the embedding model from HuggingFace
and save it locally so the server never needs to fetch it again.

Usage (from the backend/ folder, with venv active):
    python download_model.py
"""

import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Ensure backend/ is in path so config can be found
sys.path.insert(0, str(Path(__file__).parent))

from config import EMBEDDING_MODEL, EMBEDDING_MODEL_LOCAL_NAME, MODEL_CACHE_DIR
from sentence_transformers import SentenceTransformer

local_path = MODEL_CACHE_DIR / EMBEDDING_MODEL_LOCAL_NAME

if local_path.exists() and any(local_path.iterdir()):
    logger.info(f"Model already cached at: {local_path}")
    logger.info("Nothing to do. Server will load from local cache.")
else:
    logger.info(f"Downloading '{EMBEDDING_MODEL}' from HuggingFace...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    local_path.mkdir(parents=True, exist_ok=True)
    model.save(str(local_path))
    logger.info(f"✓ Model saved to: {local_path}")
    logger.info("Next server startup will load from disk — fast & offline!")
