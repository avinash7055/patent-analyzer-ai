<p align="center">
  <h1 align="center">⚙️ Patent Analyzer AI</h1>
  <p align="center">
    <strong>AI-Powered IDF vs PR — Key Features Correlation Analysis</strong>
  </p>
  <p align="center">
    <a href="#features">Features</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#tech-stack">Tech Stack</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#api-reference">API Reference</a> •
    <a href="#project-structure">Project Structure</a>
  </p>
</p>

---

## 📋 Overview

**Patent Analyzer AI** is a full-stack application that automates the comparison and correlation analysis between an **Invention Disclosure Form (IDF)** and a **Patentability Report (PR)**. It extracts key technical features from the IDF, validates their presence in the PR, maps them against prior art references, and generates a professional PDF report — all powered by AI.

Upload your `.docx` documents, click **Analyze**, and let the AI pipeline do the rest.

> **Note:** The interactive RAG-based AI Chat feature is currently under development and temporarily disabled.

---

## ✨ Features

| Category | Capabilities |
|---|---|
| **Document Processing** | Upload & parse `.docx` IDF and PR documents (via `python-docx` with XML fallback) |
| **Feature Extraction** | AI-powered extraction of all key technical features from the IDF |
| **PR Validation** | Automated verification that each IDF feature is correctly captured in the PR |
| **Prior Art Mapping** | Feature-by-feature mapping against every prior art reference in the PR |
| **PDF Report** | Professional landscape-format PDF report with tables, color coding, and gap analysis |
| **Image Extraction** | Automatic extraction & AI vision-based description of embedded images from both documents |
| **Smart Caching** | SHA-256 file hashing to detect duplicate uploads and return cached results instantly |
| **Model Preloading** | Embedding model is downloaded once and cached locally for fast offline startup |
| **AI Chat** *(Coming Soon)* | Context-aware RAG Q&A chatbot over analyzed documents with conversation history |

---

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────────────┐
│                   React Frontend (Vite)                    │
│  ┌──────────┬──────────┬──────────┬────────────────────┐  │
│  │ Features │Validation│  Matrix  │   PDF Report       │  │
│  │   Tab    │   Tab    │   Tab    │     Tab            │  │
│  └──────────┴──────────┴──────────┴────────────────────┘  │
└──────────────────────┬────────────────────────────────────┘
                       │ REST API (JSON)
┌──────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend                          │
│  ┌────────────────────────────────────────────────────┐   │
│  │               LangGraph Pipeline                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │   │
│  │  │ Feature  │──│   PR     │──│   Prior Art      │ │   │
│  │  │Extractor │  │Validator │  │   Mapper         │ │   │
│  │  └──────────┘  └──────────┘  └──────────────────┘ │   │
│  └────────────────────────────────────────────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Document    │  │ Vector Store │  │ Chat Engine  │    │
│  │  Processor   │  │ (ChromaDB)   │  │ (RAG + LLM)  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Image      │  │   Report     │  │   Model      │    │
│  │  Extractor   │  │  Generator   │  │   Loader     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└───────────────────────────────────────────────────────────┘
```

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite 7, Vanilla CSS, Lucide React Icons |
| **Backend** | FastAPI, Uvicorn, Python 3.11+ |
| **LLM** | Groq Cloud (Llama 3.3-70B for analysis, Llama 3.1-8B for intent routing) |
| **Vision LLM** | Groq Cloud (Llama 4 Scout 17B for image description) |
| **Agent Framework** | LangGraph (StateGraph with sequential pipeline) |
| **Embeddings** | BAAI/bge-small-en-v1.5 (local, via Sentence Transformers) |
| **Vector Store** | ChromaDB (persistent, cosine similarity) |
| **Document Parsing** | python-docx, lxml, zipfile (XML fallback) |
| **PDF Generation** | fpdf2 (landscape A4 with color-coded tables) |
| **Image Processing** | Pillow (EMF/WMF → PNG conversion) |
| **Typography** | Outfit (sans-serif), JetBrains Mono (monospace) via Google Fonts |

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.11+
- **Node.js** 18+
- **Groq API Key** — obtain free from [console.groq.com](https://console.groq.com)

### 1. Clone the Repository

```bash
git clone https://github.com/avinash7055/patent-analyzer-ai.git
cd patent-analyzer-ai
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

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

#### (Optional) Pre-download Embedding Model

The embedding model is automatically downloaded on first server start, but you can pre-download it:

```bash
python download_model.py
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

| Service | URL |
|---|---|
| Frontend | `http://localhost:5173` |
| Backend API | `http://localhost:8000` |
| API Docs (Swagger) | `http://localhost:8000/docs` |

### 5. Usage

1. **Upload Documents** — Drop your IDF (`.docx`) and PR (`.docx`) files into the upload zones on the home page.
2. **Run Analysis** — Click the **"Analyze Documents"** button. The AI pipeline will:
   - Extract key features from the IDF
   - Validate features against the PR
   - Map features to prior art references
   - Extract & describe images using Vision LLM
   - Generate a professional PDF report
   - Build a vector store for future chat
3. **Explore Results** — Navigate between tabs:
   - **Key Features** — View all extracted features with IDs, names, descriptions, and section references
   - **PR Validation** — See which features are correctly captured in the PR with pass/fail status
   - **Prior Art Matrix** — Interactive feature-to-prior-art mapping table with color-coded cells
   - **PDF Report** — Download the generated landscape analysis report

---

## 📡 API Reference

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload IDF and PR documents (multipart form) |
| `POST` | `/api/analyze` | Run the full analysis pipeline |
| `GET` | `/api/results` | Retrieve the latest analysis results |
| `GET` | `/api/report/pdf` | Download the generated PDF report |
| `POST` | `/api/chat` | Send a chat message *(temporarily disabled on frontend)* |
| `GET` | `/api/images/{doc_type}/{filename}` | Retrieve an extracted image |
| `GET` | `/api/health` | Health check endpoint |

### Upload Response

```json
{
  "status": "uploaded",
  "cached": false,
  "idf_filename": "my_idf.docx",
  "pr_filename": "my_pr.docx"
}
```

> When `cached` is `true`, the same files were previously analyzed — the next `/api/analyze` call returns results instantly.

### Analysis Response

```json
{
  "features": [
    {
      "id": "KF1",
      "name": "Feature name",
      "description": "Detailed description",
      "idf_section": "Section reference"
    }
  ],
  "validation": [
    {
      "feature_id": "KF1",
      "feature_name": "Feature name",
      "pr_element": "A1a",
      "captured": true,
      "details": "Explanation"
    }
  ],
  "mapping": {
    "KF1": {
      "D1": "NO",
      "D2": "Yes, Partially - explanation..."
    }
  },
  "prior_art_labels": {
    "D1": "Patent Number - Short Title"
  },
  "status": "complete"
}
```

### Health Check

```json
{
  "status": "ok",
  "has_analysis": true
}
```

---

## 🤖 AI Pipeline (LangGraph)

The analysis runs as a **LangGraph StateGraph** with three sequential nodes:

```
┌────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Extract      │────▶│   Validate   │────▶│   Map Prior     │────▶ END
│   Features     │     │   PR         │     │   Art           │
└────────────────┘     └──────────────┘     └─────────────────┘
```

1. **Extract Features** — Sends the IDF text to **Llama 3.3-70B** with a structured prompt to extract all key technical features (KF1, KF2, …) with descriptions and section references.

2. **Validate PR** — Compares extracted features against the PR's technical elements to verify each feature is correctly captured, returning per-feature pass/fail status.

3. **Map Prior Art** — Maps each feature against every prior art reference (D1, D2, …) found in the PR, classifying each as `"NO"`, `"Yes, Partially"`, or providing exact quoted text.

### Image Processing

Images embedded in both IDF and PR documents are:
1. **Extracted** from the `.docx` ZIP archive
2. **Converted** to PNG when necessary (EMF/WMF formats)
3. **Described** by **Llama 4 Scout 17B** Vision LLM with parallel processing (up to 5 concurrent calls)
4. **Indexed** into the vector store with combined context (surrounding text + vision description)

### Caching System

The application implements a **two-tier caching** strategy:

- **In-memory cache** — SHA-256 hashes of uploaded files are compared to skip re-analysis
- **Disk cache** — Analysis results are persisted to `data/analysis_cache.json` to survive server restarts
- **Vector store persistence** — ChromaDB collection is automatically reconnected on startup

---

## 📁 Project Structure

```
patent-analyzer-ai/
├── backend/
│   ├── main.py                  # FastAPI app, routes, upload/analysis/caching logic
│   ├── config.py                # Configuration, LLM prompts, model settings, paths
│   ├── requirements.txt         # Python dependencies
│   ├── download_model.py        # One-time embedding model downloader script
│   ├── .env.example             # Environment variable template
│   ├── src/
│   │   ├── __init__.py
│   │   ├── agents.py            # LangGraph pipeline & intent classification
│   │   ├── chat_engine.py       # RAG chat engine with conversation history
│   │   ├── doc_processor.py     # DOCX parsing (python-docx + XML fallback)
│   │   ├── image_extractor.py   # Image extraction + Vision LLM descriptions
│   │   ├── model_loader.py      # Singleton embedding model loader (download & cache)
│   │   ├── report_generator.py  # PDF report generation (fpdf2, landscape A4)
│   │   └── vector_store.py      # ChromaDB vector store & document chunking
│   ├── uploads/                 # Uploaded document storage (gitignored)
│   ├── extracted/               # Extracted images & generated reports (gitignored)
│   └── data/
│       ├── chromadb/            # Persistent vector store (gitignored)
│       ├── models/              # Cached embedding model (gitignored)
│       └── analysis_cache.json  # Disk-cached analysis results (gitignored)
│
├── frontend/
│   ├── index.html               # Entry HTML with SEO meta tags & Google Fonts
│   ├── package.json             # Node.js dependencies (React 19, Vite 7)
│   ├── vite.config.js           # Vite configuration
│   └── src/
│       ├── App.jsx              # Main application component with tab navigation
│       ├── App.css              # Application styles (cards, tables, animations)
│       ├── api.js               # API client functions (upload, analyze, chat, etc.)
│       ├── main.jsx             # React entry point
│       ├── index.css            # Design system: tokens, typography, animations
│       └── components/
│           ├── FeaturesTab.jsx  # Key features display table
│           ├── ValidationTab.jsx # PR validation results with pass/fail badges
│           ├── MatrixTab.jsx    # Prior art mapping matrix (interactive, color-coded)
│           ├── MatrixTab.css    # Matrix table styles
│           ├── ReportTab.jsx    # PDF download interface
│           ├── ChatTab.jsx      # Interactive RAG chat (temporarily disabled)
│           └── ChatTab.css      # Chat interface styles
│
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

---

## ⚙️ Configuration

All AI and application settings are centralized in [`backend/config.py`](backend/config.py):

| Setting | Default | Description |
|---|---|---|
| `ANALYSIS_MODEL` | `llama-3.3-70b-versatile` | LLM for feature extraction, validation & mapping |
| `ROUTER_MODEL` | `llama-3.1-8b-instant` | LLM for chat intent classification |
| `VISION_MODEL` | `meta-llama/llama-4-scout-17b-16e-instruct` | Vision LLM for image description |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Local embedding model for vector search |
| `TEMPERATURE` | `0.1` | LLM temperature (low for consistency) |
| `MAX_TOKENS` | `8192` | Maximum response tokens |
| `TOP_K_RETRIEVAL` | `5` | Number of chunks retrieved for RAG |

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your free API key from [Groq Console](https://console.groq.com/keys).

---

## 🎨 Frontend Design

The application features a **clean, warm light theme** with:

- **Outfit** font family for a modern, premium feel
- **JetBrains Mono** for code/data elements
- **Warm amber/gold** accent palette with rose/copper secondary tones
- **Glassmorphic** cards with subtle borders and shadows
- **Micro-animations** on hover states, tab transitions, and loading indicators
- **Drag-and-drop** file upload with visual feedback and file validation
- **Responsive tab navigation** that appears after analysis completes

---

## 📦 Key Dependencies

### Backend

| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `langchain-groq` | Groq LLM integration |
| `langgraph` | Agent pipeline orchestration |
| `sentence-transformers` | Local embedding model |
| `chromadb` | Vector database |
| `python-docx` | DOCX document parsing |
| `fpdf2` | PDF report generation |
| `Pillow` | Image processing |
| `python-dotenv` | Environment variable management |

### Frontend

| Package | Purpose |
|---|---|
| `react` 19 | UI library |
| `vite` 7 | Build tool & dev server |
| `lucide-react` | Icon library |
| `react-markdown` | Markdown rendering (for chat) |
| `react-router-dom` | Client-side routing |

---

## 🛣️ Roadmap

- [x] Core analysis pipeline (Feature Extraction → PR Validation → Prior Art Mapping)
- [x] Professional PDF report generation with gap analysis
- [x] Image extraction with Vision LLM descriptions
- [x] Smart file caching with SHA-256 hashing
- [x] Embedding model preloading & local caching
- [x] Disk-persistent analysis cache across server restarts
- [ ] AI Chat interface (RAG-based Q&A over documents)
- [ ] CSV/Excel export for mapping matrix
- [ ] Multi-document batch analysis
- [ ] Dark mode theme toggle

---

## 📄 License

This project is proprietary. All rights reserved.

---

<p align="center">
  Built with ❤️ by <strong>Innovix Labs</strong>
</p>
