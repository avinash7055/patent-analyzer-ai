<p align="center">
  <h1 align="center">⚙️ Patent Analysis System</h1>
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

The **Patent Analysis System** is a full-stack application that automates the comparison and correlation analysis between an **Invention Disclosure Form (IDF)** and a **Patentability Report (PR)**. It extracts key technical features from the IDF, validates their presence in the PR, maps them against prior art references, and generates a professional PDF report — all powered by AI.

An interactive **RAG-based chat interface** allows users to ask natural-language questions about the analyzed documents.

---

## ✨ Features

| Category | Capabilities |
|---|---|
| **Document Processing** | Upload & parse `.docx` IDF and PR documents (via `python-docx` with XML fallback) |
| **Feature Extraction** | AI-powered extraction of all key technical features from the IDF |
| **PR Validation** | Automated verification that each IDF feature is correctly captured in the PR |
| **Prior Art Mapping** | Feature-by-feature mapping against every prior art reference in the PR |
| **PDF Report** | Professional landscape-format PDF report with tables, color coding, and gap analysis |
| **Image Extraction** | Automatic extraction of embedded images from both IDF and PR documents |
| **RAG Chat** | Context-aware Q&A chatbot over the analyzed documents with conversation history |
| **Intent Classification** | Intelligent routing of chat messages (greetings, patent questions, export requests, irrelevant) |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                │
│  ┌──────────┬──────────┬──────────┬────────┬──────────┐  │
│  │ Features │Validation│  Matrix  │ Report │   Chat   │  │
│  │   Tab    │   Tab    │   Tab    │  Tab   │   Tab    │  │
│  └──────────┴──────────┴──────────┴────────┴──────────┘  │
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
│  │  Doc         │  │ Vector Store │  │ Chat Engine  │   │
│  │  Processor   │  │ (ChromaDB)   │  │ (RAG + LLM)  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │   Image      │  │   Report     │                     │
│  │  Extractor   │  │  Generator   │                     │
│  └──────────────┘  └──────────────┘                     │
└──────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite 7, Vanilla CSS |
| **Backend** | FastAPI, Uvicorn, Python 3.11+ |
| **LLM** | Groq (Llama 3.3-70B for analysis, Llama 3.1-8B for routing) |
| **Agent Framework** | LangGraph (StateGraph with sequential pipeline) |
| **Embeddings** | BAAI/bge-small-en-v1.5 (local, via Sentence Transformers) |
| **Vector Store** | ChromaDB (persistent, cosine similarity) |
| **Document Parsing** | python-docx, lxml, zipfile (XML fallback) |
| **PDF Generation** | fpdf2 |
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

1. **Upload Documents** — Use the sidebar to upload an IDF (`.docx`) and a PR (`.docx`) file.
2. **Run Analysis** — Click the "Analyze" button. The AI pipeline will:
   - Extract key features from the IDF
   - Validate features against the PR
   - Map features to prior art references
   - Generate a PDF report
   - Build a vector store for chat
3. **Explore Results** — Navigate between tabs:
   - **Key Features** — View all extracted features
   - **PR Validation** — See which features are correctly captured in the PR
   - **Prior Art Matrix** — Interactive feature-to-prior-art mapping table
   - **PDF Report** — Download the generated analysis report
   - **Chat** — Ask questions about the documents

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload IDF and PR documents (multipart form) |
| `POST` | `/api/analyze` | Run the full analysis pipeline |
| `GET` | `/api/results` | Retrieve the latest analysis results |
| `GET` | `/api/report/pdf` | Download the generated PDF report |
| `POST` | `/api/chat` | Send a chat message (`{ "message": "..." }`) |
| `GET` | `/api/images/{doc_type}/{filename}` | Retrieve an extracted image |
| `GET` | `/api/health` | Health check endpoint |

### Chat Response Format

```json
{
  "intent": "greeting | patent_question | export_request | irrelevant",
  "answer": "Response text...",
  "sources": [{ "section": "...", "doc_type": "IDF" }],
  "images": ["path/to/image.png"]
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

1. **Extract Features** — Sends the IDF text to Llama 3.3-70B with a structured prompt to extract all key technical features (KF1, KF2, …) with descriptions and section references.

2. **Validate PR** — Compares extracted features against the PR's technical elements to verify each feature is correctly captured.

3. **Map Prior Art** — Maps each feature against every prior art reference (D1, D2, …) found in the PR, classifying each as "NO", "Yes, Partially", or providing exact quoted text.

### RAG Chat

The chat engine uses a **Retrieval-Augmented Generation** approach:

1. User message is classified by intent using Llama 3.1-8B
2. For patent questions, relevant chunks are retrieved from ChromaDB using BGE embeddings
3. Retrieved context + conversation history + question are sent to Llama 3.3-70B
4. The response includes source citations and relevant images

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
│   │   ├── chat_engine.py       # RAG chat engine with conversation history
│   │   ├── doc_processor.py     # DOCX parsing (python-docx + XML fallback)
│   │   ├── image_extractor.py   # Image extraction from DOCX files
│   │   ├── report_generator.py  # PDF report generation (fpdf2)
│   │   └── vector_store.py      # ChromaDB vector store & document chunking
│   ├── uploads/                 # Uploaded document storage
│   ├── extracted/               # Extracted images & generated reports
│   └── data/
│       └── chromadb/            # Persistent vector store
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
│       ├── index.css            # Base CSS
│       └── components/
│           ├── Sidebar.jsx      # Document upload & analysis trigger
│           ├── Sidebar.css
│           ├── FeaturesTab.jsx  # Key features display
│           ├── ValidationTab.jsx # PR validation results
│           ├── MatrixTab.jsx    # Prior art mapping matrix
│           ├── MatrixTab.css
│           ├── ReportTab.jsx    # PDF download interface
│           ├── ChatTab.jsx      # Interactive RAG chat
│           └── ChatTab.css
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
