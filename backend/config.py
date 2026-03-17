import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
UPLOADS_DIR = BASE_DIR / "uploads"
EXTRACTED_DIR = BASE_DIR / "extracted"
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = DATA_DIR / "chromadb"
MODEL_CACHE_DIR = DATA_DIR / "models"

for d in [UPLOADS_DIR, EXTRACTED_DIR, DATA_DIR, CHROMA_DIR, MODEL_CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

ANALYSIS_MODEL = "llama-3.3-70b-versatile"
ROUTER_MODEL = "llama-3.1-8b-instant"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

TEMPERATURE = 0.1
MAX_TOKENS = 8192


FEATURE_EXTRACTOR_PROMPT = """You are a patent analysis expert. Analyze the following Invention Disclosure Form (IDF) document and extract ALL key technical features of the invention.

The IDF may be in any format or template. Read it carefully and identify every important technical aspect.

For each feature, provide:
- A short feature ID (KF1, KF2, etc.)
- A concise feature name
- A detailed description
- The section or part of the document where it appears

Be thorough. Extract features related to:
- Core technical innovations and novel aspects
- Materials and compositions
- Layer structures, constructions, configurations
- Specific property values, measurements, dimensions, ratios
- Performance metrics and characteristics
- Manufacturing processes and methods
- Intended applications and uses
- Any unique arrangements or orientations

IDF DOCUMENT TEXT:
{idf_text}

Respond in JSON format:
{{
  "features": [
    {{
      "id": "KF1",
      "name": "Short feature name",
      "description": "Detailed description of the feature",
      "idf_section": "Section reference or description of where it appears"
    }}
  ]
}}"""

PR_ELEMENTS_EXTRACTOR_PROMPT = """You are a patent analysis expert. Analyze the following Patentability Report (PR) document and extract ALL technical elements that the PR has identified and captured.

The PR may be in any format or template. Read it carefully and identify every technical element, claim element, or feature description that the PR discusses.

PR DOCUMENT TEXT:
{pr_text}

Extract each element with:
- Element ID (as labeled in the document, e.g., A1, A1a, B1, etc. — or assign E1, E2, E3 if no IDs are present)
- Description of what the element covers
- The relevant text/excerpt from the PR

Respond in JSON format:
{{
  "elements": [
    {{
      "id": "A1a",
      "description": "Brief description of what this element covers",
      "text": "The relevant text from the PR document"
    }}
  ]
}}"""

PRIOR_ART_EXTRACTOR_PROMPT = """You are a patent analysis expert. Analyze the following Patentability Report (PR) document and extract ALL prior art references mentioned in it.

The PR may be in any format or template. Look for any referenced patents, publications, or prior art documents.

PR DOCUMENT TEXT:
{pr_text}

For each prior art reference, extract:
- A short reference ID (D1, D2, D3, etc.)
- The patent/publication number (if available)
- A short title or description
- ALL relevant text about this prior art, including what it discloses and how it relates to the invention

Respond in JSON format:
{{
  "prior_art_references": [
    {{
      "id": "D1",
      "patent_number": "US1234567 or N/A if not available",
      "title": "Short descriptive title",
      "text": "Complete summary and relevant details about this prior art reference"
    }}
  ]
}}"""

PR_VALIDATOR_PROMPT = """You are a patent analysis expert. Compare the key features extracted from an IDF against the technical elements captured in a Patentability Report (PR).

For each IDF feature, check if it is correctly captured in the PR's technical elements.

IDF KEY FEATURES:
{features_json}

PR TECHNICAL ELEMENTS:
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
      "pr_element": "Element ID or N/A",
      "captured": true,
      "details": "Brief explanation"
    }}
  ]
}}"""

PRIOR_ART_MAPPER_PROMPT = """You are a patent analysis expert. Map each key feature of an invention against each prior art reference found in the Patentability Report.

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

PDF_TITLE = "Patent Analysis Report"
PDF_SUBTITLE = "IDF vs PR - Key Features Correlation Analysis"
PDF_COLORS = {
    "novel": (16, 185, 129),
    "partial": (245, 158, 11),
    "match": (255, 255, 255),
    "header": (59, 130, 246),
    "bg_dark": (10, 15, 30),
}
