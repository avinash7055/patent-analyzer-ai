import logging
import shutil
import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from config import UPLOADS_DIR, EXTRACTED_DIR, DATA_DIR
from src.doc_processor import (
    DocumentProcessor,
    extract_prior_art_sections,
    extract_pr_elements_text,
)
from src.image_extractor import ImageExtractor
from src.agents import run_analysis
from src.report_generator import ReportGenerator
from src.vector_store import VectorStore
from src.chat_engine import ChatEngine
from src.model_loader import get_embedding_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

doc_processor = DocumentProcessor()
image_extractor = ImageExtractor()
report_generator = ReportGenerator()
vector_store = VectorStore()
chat_engine: ChatEngine | None = None

analysis_result: dict = {}
uploaded_files: dict = {}

# Disk-based cache to survive server restarts
CACHE_PATH = DATA_DIR / "analysis_cache.json"
_cache = {"idf_hash": None, "pr_hash": None}

def _load_disk_cache():
    global analysis_result, chat_engine, _cache
    if CACHE_PATH.exists():
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            _cache["idf_hash"] = data.get("idf_hash")
            _cache["pr_hash"] = data.get("pr_hash")
            analysis_result = data.get("analysis_result", {})
            if analysis_result and vector_store.collection:
                chat_engine = ChatEngine(vector_store)
                logger.info("Restored analysis result and chat engine from disk cache ✓")
        except Exception as e:
            logger.warning(f"Failed to load disk cache: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-load the embedding model at startup so it's ready for first request."""
    logger.info("=" * 60)
    logger.info("Patent Analyzer AI — Starting up")
    logger.info("Loading embedding model (first run downloads & caches locally)...")
    get_embedding_model()   # ← triggers download+save on first run, disk load after
    _load_disk_cache()      # ← loads previous analysis state from disk
    logger.info("Embedding model ready ✓")
    logger.info("=" * 60)
    yield
    logger.info("Patent Analyzer AI — Shutting down")


app = FastAPI(title="Patent Analysis API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class AnalyzeRequest(BaseModel):
    pass


import hashlib

def _file_hash(path: str) -> str:
    """Compute SHA-256 hash of a file on disk."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def _bytes_hash(data: bytes) -> str:
    """Compute SHA-256 hash of in-memory bytes."""
    return hashlib.sha256(data).hexdigest()

# Mutable cache dict — avoids Python `global` reassignment issues
_cache = {"idf_hash": None, "pr_hash": None}


@app.post("/api/upload")
async def upload_documents(
    idf_file: UploadFile = File(...),
    pr_file: UploadFile = File(...),
):
    global uploaded_files

    # 1. Read file bytes into memory (no disk write yet)
    idf_bytes = await idf_file.read()
    pr_bytes = await pr_file.read()

    # 2. Compute hashes from in-memory bytes
    new_idf_hash = _bytes_hash(idf_bytes)
    new_pr_hash = _bytes_hash(pr_bytes)

    # 3. Check cache BEFORE writing to disk
    cache_hit = (
        analysis_result
        and chat_engine is not None
        and _cache["idf_hash"] is not None
        and new_idf_hash == _cache["idf_hash"]
        and new_pr_hash == _cache["pr_hash"]
    )

    idf_path = UPLOADS_DIR / idf_file.filename
    pr_path = UPLOADS_DIR / pr_file.filename
    uploaded_files = {"idf": str(idf_path), "pr": str(pr_path)}

    if cache_hit:
        # Same files — skip disk write entirely
        logger.info("Same files detected — skipping disk write, cached results available ✓")
        return {
            "status": "uploaded",
            "cached": True,
            "idf_filename": idf_file.filename,
            "pr_filename": pr_file.filename,
        }

    # 4. New files — write to disk
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    with open(idf_path, "wb") as f:
        f.write(idf_bytes)
    with open(pr_path, "wb") as f:
        f.write(pr_bytes)

    # 5. Clean previously extracted data for fresh analysis
    if EXTRACTED_DIR.exists():
        shutil.rmtree(EXTRACTED_DIR)
    EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)

    logger.info(f"New documents uploaded: IDF={idf_file.filename}, PR={pr_file.filename}")

    return {
        "status": "uploaded",
        "cached": False,
        "idf_filename": idf_file.filename,
        "pr_filename": pr_file.filename,
    }


@app.post("/api/analyze")
async def analyze_documents():
    global analysis_result, chat_engine

    if not uploaded_files:
        raise HTTPException(status_code=400, detail="No documents uploaded. Please upload IDF and PR first.")

    # Quick cache check — if same file hashes, return instantly
    current_idf_hash = _file_hash(uploaded_files["idf"])
    current_pr_hash = _file_hash(uploaded_files["pr"])

    if (
        analysis_result
        and chat_engine is not None
        and _cache["idf_hash"] is not None
        and current_idf_hash == _cache["idf_hash"]
        and current_pr_hash == _cache["pr_hash"]
    ):
        logger.info(" Same files — returning cached analysis instantly!")
        return analysis_result

    try:
        logger.info("Processing IDF document...")
        idf_doc = doc_processor.process(uploaded_files["idf"])

        logger.info("Processing PR document...")
        pr_doc = doc_processor.process(uploaded_files["pr"])

        logger.info("Extracting images from IDF...")
        idf_images = image_extractor.extract(uploaded_files["idf"], "IDF")

        logger.info("Extracting images from PR...")
        pr_images = image_extractor.extract(uploaded_files["pr"], "PR")

        pr_elements_text = extract_pr_elements_text(pr_doc)
        prior_art_sections = extract_prior_art_sections(pr_doc)

        logger.info("Running AI analysis pipeline...")
        result = run_analysis(
            idf_text=idf_doc.full_text,
            pr_text=pr_doc.full_text,
            pr_elements_text=pr_elements_text,
            prior_art_sections=prior_art_sections,
        )

        # PDF report generation temporarily disabled
        # logger.info("Generating PDF report...")
        # report_path = EXTRACTED_DIR / "patent_analysis_report.pdf"
        # report_generator.generate(
        #     features=result.get("features", []),
        #     validation=result.get("validation", []),
        #     mapping=result.get("mapping", {}),
        #     prior_art_labels=result.get("prior_art_labels", {}),
        #     output_path=report_path,
        #     title=idf_doc.sections.get("1.3\tDisclosure Title", "Patent Analysis"),
        #     inventors="",
        # )

        logger.info("Building vector store...")
        all_images = [
            {"filename": img.filename, "section": img.section,
             "surrounding_text": img.surrounding_text, "filepath": img.filepath,
             "vision_description": img.vision_description,
             "doc_label": "IDF" if "IDF" in img.image_id else "PR"}
            for img in idf_images + pr_images
        ]
        vector_store.build_index(idf_doc, pr_doc, all_images)

        chat_engine = ChatEngine(vector_store)

        analysis_result = {
            "features": result.get("features", []),
            "validation": result.get("validation", []),
            "mapping": result.get("mapping", {}),
            "prior_art_labels": result.get("prior_art_labels", {}),
            # "report_path": str(report_path),  # PDF report disabled
            "idf_images": [{"id": img.image_id, "filename": img.filename,
                           "path": img.filepath, "section": img.section}
                          for img in idf_images],
            "pr_images": [{"id": img.image_id, "filename": img.filename,
                          "path": img.filepath, "section": img.section}
                         for img in pr_images],
            "status": result.get("status", "complete"),
        }

        # ★ Save hashes into the mutable cache dict
        _cache["idf_hash"] = current_idf_hash
        _cache["pr_hash"] = current_pr_hash
        
        # Save cache to disk for persistence across server restarts
        try:
            with open(CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump({
                    "idf_hash": current_idf_hash,
                    "pr_hash": current_pr_hash,
                    "analysis_result": analysis_result
                }, f)
        except Exception as e:
            logger.warning(f"Failed to write disk cache: {e}")

        logger.info(f"Analysis complete! Hashes cached: IDF={str(current_idf_hash)[:12]}... PR={str(current_pr_hash)[:12]}...")
        return analysis_result

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/results")
async def get_results():
    if not analysis_result:
        raise HTTPException(status_code=404, detail="No analysis results available. Run analysis first.")
    return analysis_result


@app.get("/api/report/pdf")
async def download_report():
    if not analysis_result or "report_path" not in analysis_result:
        raise HTTPException(status_code=404, detail="No report available. Run analysis first.")
    report_path = Path(analysis_result["report_path"])
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found.")
    return FileResponse(
        path=str(report_path),
        filename="patent_analysis_report.pdf",
        media_type="application/pdf",
    )


@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not chat_engine:
        raise HTTPException(status_code=400, detail="Chat not available. Run analysis first to enable chat.")
    result = chat_engine.chat(request.message)
    return result


@app.get("/api/images/{doc_type}/{filename}")
async def get_image(doc_type: str, filename: str):
    image_path = EXTRACTED_DIR / doc_type / filename
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found.")
    return FileResponse(str(image_path))


@app.get("/api/health")
async def health():
    return {"status": "ok", "has_analysis": bool(analysis_result)}
