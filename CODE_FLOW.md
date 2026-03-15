# Patent Analysis System: Code Flow Documentation

This document provides a detailed, step-by-step code-level breakdown of the flow in the **Patent Analysis System**. It traces the lifecycle of a request from user upload, through the FastAPI backend and AI pipelines, to the frontend presentation and RAG chat.

---

## Step 1: User Upload and API Trigger (Frontend UI)
**Relevant File:** `frontend/src/App.jsx`

1. **Upload:** The user drags and drops an IDF (`.docx`) and a PR (`.docx`) file into the `CenterDropZone` components. 
2. **Action Trigger:** The user clicks **"Analyze Documents"**, which fires the `handleAnalyze()` function.
3. **API Calls:** `handleAnalyze()` sequentially calls two API wrappers from `frontend/src/api.js`:
   *   `uploadDocuments(idfFile, prFile)`: Pushes the actual binary `.docx` files to the backend.
   *   `runAnalysis()`: Triggers the heavy AI processing pipeline.

---

## Step 2: Document Ingestion and Caching (FastAPI Backend)
**Relevant File:** `backend/main.py`

1. **`/api/upload` Endpoint:** 
   * Receives the `.docx` files. 
   * It computes a SHA-256 hash of both files using `_file_hash()`. 
   * If the hashes match the previously processed files stored in the cache (`_cache`), it skips disk writing and marks `cached: True`. 
   * Otherwise, it saves the files to the `UPLOADS_DIR` (e.g., `backend/uploads/`).
2. **`/api/analyze` Endpoint Orchestration:** 
   * Validates the cache again to immediately return results if the files haven't changed.
   * If new, it instantiates `DocumentProcessor` (using `python-docx` + XML parsing) to extract raw text and logical sections from the uploaded documents.
   * It uses `ImageExtractor` to pull every embedded `.png`/`.jpeg` out of the docs and saves them to `EXTRACTED_DIR` (`backend/extracted/`).

---

## Step 3: Agentic AI Pipeline (LangGraph)
**Relevant File:** `backend/src/agents.py`

The parsed text is handed over to `run_analysis()`, which compiles and runs a **LangGraph StateGraph**. Data moves securely through the graph inside a typed dictionary called `AnalysisState`.

1. **Node 1: Extract Features (`extract_features_node`)**
   * Initializes a connection to Groq's Large Model (`Llama 3.3-70B`). 
   * Sends the raw IDF text with `FEATURE_EXTRACTOR_PROMPT`. 
   * The LLM returns structured JSON containing purely the technical features `{"features": [...]}`. This is appended to the pipeline `state`.
2. **Node 2: Validate PR (`validate_pr_node`)**
   * Takes the `features` list from Node 1 and the entire PR text. 
   * Asks the LLM to verify if each IDF feature is adequately captured in the PR text using `PR_VALIDATOR_PROMPT`. 
   * Updates the `state` with a detailed `validation` list.
3. **Node 3: Map Prior Art (`map_prior_art_node`)**
   * Takes the features array and chunks of "Prior Art" (D1, D2 citations) extracted from the PR. 
   * The LLM cross-references them to determine if a feature is missing or pre-existing in the cited patents (`PRIOR_ART_MAPPER_PROMPT`). 
   * Updates the `state` with `mapping` and `prior_art_labels`.
   * Execution reaches `END` and the final state is returned back to the main router.

---

## Step 4: Post-Processing & Indexing (FastAPI Backend)
**Relevant File:** `backend/main.py`

Once LangGraph returns the analysis JSON object:

1. **Reporting (`src/report_generator.py`):** The data arrays are fed into `fpdf2` to dynamically create a multi-page, landscape PDF report saving it to `EXTRACTED_DIR/patent_analysis_report.pdf`.
2. **Vectorization (`src/vector_store.py`):** The raw text chunks of the documents AND the metadata referencing the extracted images are converted into dense vector embeddings using local `SentenceTransformers` (`BAAI/bge-small-en-v1.5`). These embeddings are populated into a persistent `ChromaDB` index for future context retrieval.
3. **Cache Storage:** The final `analysis_result` JSON is returned to the frontend. Simultaneously, it writes this state to an in-memory variable AND a disk cache `analysis_cache.json` so results survive server reboots seamlessly.

---

## Step 5: Frontend Rendering
**Relevant File:** `frontend/src/App.jsx`

1. **State Update:** The frontend receives the massive JSON blob from `/api/analyze`.
2. `App.jsx` sets `setAnalysisData(result)`, triggering a React state change.
3. **UI Swap:** The empty drop-zone disappears, and the `topbar-tabs` render across the UI. 
4. **Data Binding:** Depending on the `activeTab`, the application injects the specific array of data into subcomponents like `<FeaturesTab features={...} />` or `<MatrixTab mapping={...} />`, rendering interactive tables and UI cards.

---

## Step 6: RAG Chat Loop
**Relevant Files:** `backend/main.py` & `backend/src/chat_engine.py`

When the user navigates to the **AI Chat Tab** and asks a natural language question:

1. The frontend invokes `POST /api/chat`.
2. **Intent Classification:** `ChatEngine.chat()` calls `classify_intent()` which hits a smaller, faster model (`Llama 3.1-8B`) to classify if the user said a greeting, asked to export a PDF, asked irrelevant info, or asked a genuine "patent_question".
3. **Vector Search (Retrieval):** If classified as a patent question, `VectorStore` chunks the question into vectors, calculates cosine similarity against `ChromaDB`, and pulls the top 5 most relevant document paragraphs.
4. **Answer Generation (Augmented Generation):** It merges the user's question, the prior conversation history (`self.history`), and the retrieved document chunks, passing the unified prompt back to `Llama 3.3-70B` to formulate an accurate answer safely. The response can also include image paths if relevant visual context was retrieved.
5. **Presentation:** The frontend renders the Markdown response in the chat bubble interfaces.
