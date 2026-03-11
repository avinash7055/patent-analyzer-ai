import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "uploads"
EXTRACTED_DIR = BASE_DIR / "extracted"
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = DATA_DIR / "chromadb"

for d in [UPLOADS_DIR, EXTRACTED_DIR, DATA_DIR, CHROMA_DIR]:
    d.mkdir(parents=True, exist_ok=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

ANALYSIS_MODEL = "llama-3.3-70b-versatile"
ROUTER_MODEL = "llama-3.1-8b-instant"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

TEMPERATURE = 0.1
MAX_TOKENS = 8192
TOP_K_RETRIEVAL = 5

FEATURE_EXTRACTOR_PROMPT = """You are a patent analysis expert. Analyze the following Invention Disclosure Form (IDF) and extract ALL key technical features of the invention.

For each feature, provide:
- A short feature ID (KF1, KF2, etc.)
- A concise feature name
- A detailed description
- The IDF section where it appears

Be thorough. Include features related to:
- Materials and compositions (resins, fillers, fibers)
- Layer structure and construction
- Specific property values (Dk, Df, thickness, ratios)
- Performance metrics (reflectivity, transmission)
- Manufacturing processes
- Intended applications/uses
- Orientation/arrangement requirements

IDF TEXT:
{idf_text}

Respond in JSON format:
{{
  "features": [
    {{
      "id": "KF1",
      "name": "Short feature name",
      "description": "Detailed description of the feature",
      "idf_section": "Section reference"
    }}
  ]
}}"""

PR_VALIDATOR_PROMPT = """You are a patent analysis expert. Compare the key features extracted from an IDF against the technical elements captured in a Patentability Report (PR).

For each IDF feature, check if it is correctly captured in the PR's technical elements.

IDF KEY FEATURES:
{features_json}

PR TECHNICAL ELEMENTS TEXT:
{pr_elements_text}

For each feature, determine:
- Which PR element (if any) corresponds to it
- Whether it is captured correctly (true/false)
- Brief explanation

Respond in JSON format:
{{
  "validation": [
    {{
      "feature_id": "KF1",
      "feature_name": "Feature name",
      "pr_element": "A1a or N/A",
      "captured": true,
      "details": "Brief explanation"
    }}
  ]
}}"""

PRIOR_ART_MAPPER_PROMPT = """You are a patent analysis expert. Map each key feature of an invention against each prior art reference found in a Patentability Report.

KEY FEATURES:
{features_json}

PRIOR ART REFERENCES:
{prior_art_text}

For EACH feature and EACH prior art reference, determine the mapping:
- "NO" if the feature is NOT disclosed in this prior art at all
- "Yes, Partially" followed by explanation if the feature is partially or approximately disclosed
- The EXACT quoted text from the prior art if the feature is clearly disclosed

Respond in JSON format:
{{
  "mapping": {{
    "KF1": {{
      "D1": "NO",
      "D2": "Yes, Partially - explanation...",
      "D3": "exact quoted text from prior art..."
    }},
    "KF2": {{
      "D1": "...",
      "D2": "...",
      "D3": "..."
    }}
  }},
  "prior_art_labels": {{
    "D1": "Patent Number - Short Title",
    "D2": "Patent Number - Short Title"
  }}
}}"""

ROUTER_PROMPT = """You are an intent classifier for a patent analysis chatbot. Classify the user's message into one of these categories:

- "greeting" for greetings, hellos, goodbyes, how are you, thanks
- "patent_question" for questions about the IDF, PR, key features, prior art, claims, mapping, or anything related to the patent analysis
- "export_request" for requests to download, export, or save reports, PDFs, CSVs
- "irrelevant" for anything unrelated to patent analysis

User message: {message}

Respond in JSON format:
{{
  "intent": "greeting|patent_question|export_request|irrelevant",
  "friendly_response": "A warm, helpful response appropriate for the intent"
}}"""

RAG_CHAT_PROMPT = """You are a patent analysis assistant. Answer the user's question based ONLY on the provided context from the IDF (Invention Disclosure Form) and PR (Patentability Report).

CONTEXT FROM DOCUMENTS:
{context}

CONVERSATION HISTORY:
{chat_history}

USER QUESTION: {question}

Rules:
1. Answer based on the provided context only
2. If the context contains relevant image references, mention them
3. Cite specific sections, features (KF1, KF2...), or prior art references (D1, D2...)
4. If you are unsure, say so
5. Be concise but thorough

Answer:"""

IMAGE_DESCRIPTION_PROMPT = """Describe this image from a patent document in detail.
Focus on:
- Physical structure, layers, and geometry
- Materials and compositions visible
- Labels, numbered components, and annotations
- Measurements, dimensions, or scale indicators
- Charts/graphs: axes, data trends, and key values
- Any text or captions visible in the image

Surrounding document context: {surrounding_text}

Provide a concise but thorough technical description (2-4 sentences)."""

PDF_TITLE = "Patent Analysis Report"
PDF_SUBTITLE = "IDF vs PR - Key Features Correlation Analysis"
PDF_COLORS = {
    "novel": (16, 185, 129),
    "partial": (245, 158, 11),
    "match": (255, 255, 255),
    "header": (59, 130, 246),
    "bg_dark": (10, 15, 30),
}
