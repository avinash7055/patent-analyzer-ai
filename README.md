<p align="center">
  <h1 align="center">⚙️ Patent Analyzer AI</h1>
  <p align="center">
    <strong>AI-Powered IDF vs PR — Key Features Correlation Analysis</strong>
  </p>
  <p align="center">
    <a href="#features">Features</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#api-reference">API Reference</a> •
    <a href="#project-structure">Project Structure</a>
  </p>
</p>

---

## 📋 Overview

The **Patent Analyzer AI** is a full-stack application that automates the comparison and correlation analysis between an **Invention Disclosure Form (IDF)** and a **Patentability Report (PR)**. It extracts key technical features from the IDF, validates their presence in the PR, and maps them against prior art references — all powered by AI.

---

## ✨ Features

| Category | Capabilities |
|---|---|
| **Document Processing** | Upload & parse `.docx` IDF and PR documents (via `python-docx` with XML fallback) |
| **Feature Extraction** | AI-powered extraction of all key technical features from the IDF |
| **PR Validation** | Automated verification that each IDF feature is correctly captured in the PR |
| **Prior Art Mapping** | Feature-by-feature mapping against every prior art reference in the PR |
| **Image Extraction** | Automatic extraction of embedded images from both IDF and PR documents |
| **Vision Analysis** | AI-powered image description using Llama 4 Scout vision model |
| **Smart Caching** | File-hash based caching — re-uploading same files returns instant results |
| **RAG Chat** | Context-aware Q&A chatbot over the analyzed documents *(temporarily disabled)* |
| **PDF Report** | Professional landscape-format PDF report with gap analysis *(temporarily disabled)* |

### 🔜 Coming Soon
- **AI Chat** — RAG-based patent Q&A (improved with smart image filtering & concise responses)
- **PDF Report** — Professional report generation with proper title/inventor extraction

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                │
│  ┌──────────┬──────────┬──────────┐                      │
│  │ Features │Validation│  Matrix  │                      │
│  │   Tab    │   Tab    │   Tab    │                      │
│  └──────────┴──────────┴──────────┘                      │
│  ┌──────────────────────────────────┐                    │
│  │    Center Upload UI (Drop Zone) │                    │
│  └──────────────────────────────────┘                    │
└──────────────────────┬───────────────────────────────────┘
                       │ REST API (JSON)
┌──────────────────────▼───────────────────────────────────┐
│                  FastAPI Backend                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │               LangGraph Pipeline                   │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │  │
│  │  │ Feature  │──│   PR     │──│   Prior Art      │ │  │
│  │  │Extractor │  │Validator │  │   Mapper         │ │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘ │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Doc         │  │ Vector Store │  │   Image      │   │
│  │  Processor   │  │ (ChromaDB)   │  │  Extractor   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite 7, Vanilla CSS |
| **Backend** | FastAPI, Uvicorn, Python 3.11+ |
| **LLM** | Groq (Llama 3.3-70B for analysis, Llama 3.1-8B for routing) |
| **Vision Model** | Llama 4 Scout 17B (for image description) |
| **Agent Framework** | LangGraph (StateGraph with sequential pipeline) |
| **Embeddings** | BAAI/bge-small-en-v1.5 (local, via Sentence Transformers) |
| **Vector Store** | ChromaDB (persistent, cosine similarity) |
| **Document Parsing** | python-docx, lxml, zipfile (XML fallback) |
| **Image Processing** | Pillow |

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- **Groq API Key** — obtain from [console.groq.com](https://console.groq.com)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Innovix_labs
```

### 2. Backend Setup

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your Groq API key:
# GROQ_API_KEY=your_groq_api_key_here
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 4. Run the Application

**Start the backend** (from the `backend/` directory):
```bash
uvicorn main:app --reload --port 8000
```

**Start the frontend** (from the `frontend/` directory):
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` and the backend API at `http://localhost:8000`.

### 5. Usage

1. **Upload Documents** — Drop your IDF (`.docx`) and PR (`.docx`) files into the center upload area.
2. **Run Analysis** — Click the **"Analyze Documents"** button. The AI pipeline will:
   - Extract key features from the IDF
   - Validate features against the PR
   - Map features to prior art references
   - Build a vector store for search
3. **Explore Results** — Navigate between tabs:
   - **Key Features** — View all extracted features with IDF section references
   - **PR Validation** — See which features are correctly captured in the PR with coverage %
   - **Prior Art Matrix** — Color-coded feature-to-prior-art mapping table with CSV export

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload IDF and PR documents (multipart form) |
| `POST` | `/api/analyze` | Run the full analysis pipeline |
| `GET` | `/api/results` | Retrieve the latest analysis results |
| `GET` | `/api/report/pdf` | Download the generated PDF report *(disabled)* |
| `POST` | `/api/chat` | Send a chat message (`{ "message": "..." }`) *(disabled)* |
| `GET` | `/api/images/{doc_type}/{filename}` | Retrieve an extracted image |
| `GET` | `/api/health` | Health check endpoint |

### Upload Response

```json
{
  "status": "uploaded",
  "cached": false,
  "idf_filename": "idf_document.docx",
  "pr_filename": "pr_document.docx"
}
```

> When `cached: true`, the same files were already analyzed — results are returned instantly without re-processing.

---

## 🤖 AI Pipeline (LangGraph)

The analysis runs as a **LangGraph StateGraph** with three sequential nodes:

```
┌────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Extract      │────▶│   Validate   │────▶│   Map Prior     │────▶ END
│   Features     │     │   PR         │     │   Art           │
└────────────────┘     └──────────────┘     └─────────────────┘
```

1. **Extract Features** — Sends the IDF text to Llama 3.3-70B with a structured prompt to extract all key technical features (KF1, KF2, …) with descriptions and section references.

2. **Validate PR** — Compares extracted features against the PR's technical elements to verify each feature is correctly captured.

3. **Map Prior Art** — Maps each feature against every prior art reference (D1, D2, …) found in the PR, classifying each as "NO", "Yes, Partially", or providing exact quoted text.

### Caching System

The application uses **SHA-256 file hashing** to detect duplicate uploads:
- On upload, file hashes are computed in-memory (before writing to disk)
- If hashes match the previous analysis, cached results are returned instantly
- Cache is persisted to disk (`data/analysis_cache.json`) and survives server restarts

---

## 📁 Project Structure

```
Innovix_labs/
├── backend/
│   ├── main.py                  # FastAPI application & route definitions
│   ├── config.py                # Configuration, prompts, and model settings
│   ├── requirements.txt         # Python dependencies
│   ├── .env.example             # Environment variable template
│   ├── src/
│   │   ├── agents.py            # LangGraph pipeline & intent classification
│   │   ├── chat_engine.py       # RAG chat engine with smart image filtering
│   │   ├── doc_processor.py     # DOCX parsing (python-docx + XML fallback)
│   │   ├── image_extractor.py   # Image extraction & vision analysis
│   │   ├── model_loader.py      # Local embedding model loader & caching
│   │   ├── report_generator.py  # PDF report generation (fpdf2)
│   │   └── vector_store.py      # ChromaDB vector store & document chunking
│   ├── uploads/                 # Uploaded document storage
│   ├── extracted/               # Extracted images & generated reports
│   └── data/
│       ├── chromadb/            # Persistent vector store
│       └── models/              # Cached embedding model
│
├── frontend/
│   ├── index.html               # Entry HTML
│   ├── package.json             # Node.js dependencies
│   ├── vite.config.js           # Vite configuration
│   └── src/
│       ├── App.jsx              # Main application component
│       ├── App.css              # Global styles
│       ├── api.js               # API client functions
│       ├── main.jsx             # React entry point
│       ├── index.css            # Design tokens & base styles
│       └── components/
│           ├── FeaturesTab.jsx  # Key features table
│           ├── ValidationTab.jsx # PR validation with coverage bar
│           ├── MatrixTab.jsx    # Prior art mapping matrix
│           ├── MatrixTab.css    # Matrix-specific styles
│           ├── ReportTab.jsx    # PDF download interface (disabled)
│           ├── ChatTab.jsx      # Interactive RAG chat (disabled)
│           └── ChatTab.css      # Chat styles
│
└── README.md
```

---

## ⚙️ Configuration

All AI and application settings are centralized in [`backend/config.py`](backend/config.py):

| Setting | Default | Description |
|---|---|---|
| `ANALYSIS_MODEL` | `llama-3.3-70b-versatile` | LLM for feature extraction, validation & mapping |
| `ROUTER_MODEL` | `llama-3.1-8b-instant` | LLM for chat intent classification |
| `VISION_MODEL` | `meta-llama/llama-4-scout-17b-16e-instruct` | Vision model for image descriptions |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Local embedding model for vector search |
| `TEMPERATURE` | `0.1` | LLM temperature (low for consistency) |
| `MAX_TOKENS` | `8192` | Maximum response tokens |
| `TOP_K_RETRIEVAL` | `5` | Number of chunks retrieved for RAG |

---

## 📄 License

This project is proprietary. All rights reserved.

---

<p align="center">
  Built with ❤️ by <strong>Innovix Labs</strong>
</p>
