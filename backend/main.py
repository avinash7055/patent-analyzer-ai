import logging
import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from config import UPLOADS_DIR, EXTRACTED_DIR
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Patent Analysis API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

doc_processor = DocumentProcessor()
image_extractor = ImageExtractor()
report_generator = ReportGenerator()
vector_store = VectorStore()
chat_engine: ChatEngine | None = None

analysis_result: dict = {}
uploaded_files: dict = {}


class ChatRequest(BaseModel):
    message: str


class AnalyzeRequest(BaseModel):
    pass


@app.post("/api/upload")
async def upload_documents(
    idf_file: UploadFile = File(...),
    pr_file: UploadFile = File(...),
):
    global uploaded_files

    idf_path = UPLOADS_DIR / idf_file.filename
    pr_path = UPLOADS_DIR / pr_file.filename

    with open(idf_path, "wb") as f:
        shutil.copyfileobj(idf_file.file, f)
    with open(pr_path, "wb") as f:
        shutil.copyfileobj(pr_file.file, f)

    uploaded_files = {"idf": str(idf_path), "pr": str(pr_path)}

    return {
        "status": "uploaded",
        "idf_filename": idf_file.filename,
        "pr_filename": pr_file.filename,
    }


@app.post("/api/analyze")
async def analyze_documents():
    global analysis_result, chat_engine

    if not uploaded_files:
        raise HTTPException(status_code=400, detail="No documents uploaded. Please upload IDF and PR first.")

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

        logger.info("Generating PDF report...")
        report_path = EXTRACTED_DIR / "patent_analysis_report.pdf"
        report_generator.generate(
            features=result.get("features", []),
            validation=result.get("validation", []),
            mapping=result.get("mapping", {}),
            prior_art_labels=result.get("prior_art_labels", {}),
            output_path=report_path,
            title=idf_doc.sections.get("1.3\tDisclosure Title", "Patent Analysis"),
            inventors="",
        )

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
            "report_path": str(report_path),
            "idf_images": [{"id": img.image_id, "filename": img.filename,
                           "path": img.filepath, "section": img.section}
                          for img in idf_images],
            "pr_images": [{"id": img.image_id, "filename": img.filename,
                          "path": img.filepath, "section": img.section}
                         for img in pr_images],
            "status": result.get("status", "complete"),
        }

        logger.info("Analysis complete!")
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
