"""
model_loader.py
───────────────
Singleton loader for the SentenceTransformer embedding model.

Strategy:
  1. On first run → download from HuggingFace, save to data/models/<name>/
  2. On every subsequent run → load directly from disk (no internet needed, fast)

Usage:
  from src.model_loader import get_embedding_model
  model = get_embedding_model()
"""

import logging
from pathlib import Path

from sentence_transformers import SentenceTransformer

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import EMBEDDING_MODEL, EMBEDDING_MODEL_LOCAL_NAME, MODEL_CACHE_DIR

logger = logging.getLogger(__name__)

# ── Singleton state ──────────────────────────────────────────────────────────
_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """
    Return the cached SentenceTransformer model.
    Loads from local disk if available, otherwise downloads and saves.
    """
    global _model
    if _model is not None:
        return _model

    local_path = MODEL_CACHE_DIR / EMBEDDING_MODEL_LOCAL_NAME

    if local_path.exists() and any(local_path.iterdir()):
        logger.info(f"Loading embedding model from local cache: {local_path}")
        _model = SentenceTransformer(str(local_path))
    else:
        logger.info(
            f"Local model cache not found at '{local_path}'. "
            f"Downloading '{EMBEDDING_MODEL}' from HuggingFace (one-time only)…"
        )
        _model = SentenceTransformer(EMBEDDING_MODEL)
        local_path.mkdir(parents=True, exist_ok=True)
        _model.save(str(local_path))
        logger.info(f"Model saved to local cache: {local_path}")

    return _model
