import logging
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
from config import CHROMA_DIR, TOP_K_RETRIEVAL
from src.doc_processor import ProcessedDocument
from src.model_loader import get_embedding_model

logger = logging.getLogger(__name__)


class VectorStore:

    def __init__(self, persist_dir: Path = None):
        self.persist_dir = persist_dir or CHROMA_DIR
        self.embedding_model = get_embedding_model()   # ← singleton, loads once
        self.client = chromadb.PersistentClient(path=str(self.persist_dir))
        
        # Try to load existing collection so it works after restarts
        try:
            self.collection = self.client.get_collection("patent_analysis")
            logger.info("Successfully reconnected to existing 'patent_analysis' vector collection.")
        except Exception:
            self.collection = None

    def build_index(
        self,
        idf_doc: ProcessedDocument,
        pr_doc: ProcessedDocument,
        images: list[dict] = None,
        collection_name: str = "patent_analysis",
    ):
        try:
            self.client.delete_collection(collection_name)
        except Exception:
            pass

        self.collection = self.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        chunks = []
        metadatas = []
        ids = []

        idf_chunks = self._chunk_document(idf_doc, "IDF")
        for i, (text, meta) in enumerate(idf_chunks):
            chunks.append(text)
            metadatas.append(meta)
            ids.append(f"idf_{i}")

        pr_chunks = self._chunk_document(pr_doc, "PR")
        for i, (text, meta) in enumerate(pr_chunks):
            chunks.append(text)
            metadatas.append(meta)
            ids.append(f"pr_{i}")

        if images:
            for i, img in enumerate(images):
                # Build a rich text representation combining all available context
                parts = [f"Image: {img.get('filename', '')}"]
                parts.append(f"Section: {img.get('section', '')}")
                if img.get("surrounding_text"):
                    parts.append(f"Document Context: {img['surrounding_text']}")
                if img.get("vision_description"):
                    parts.append(f"Visual Description: {img['vision_description']}")
                text = ". ".join(parts)
                chunks.append(text)
                metadatas.append({
                    "doc_type": img.get("doc_label", "DOC"),
                    "section": img.get("section", ""),
                    "has_image": "true",
                    "image_path": img.get("filepath", ""),
                })
                ids.append(f"img_{i}")

        if chunks:
            embeddings = self.embedding_model.encode(chunks).tolist()
            self.collection.add(
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids,
            )

        logger.info(f"Indexed {len(chunks)} chunks into collection '{collection_name}'")

    def query(self, question: str, top_k: int = None) -> list[dict]:
        if not self.collection:
            return []

        k = top_k or TOP_K_RETRIEVAL
        query_embedding = self.embedding_model.encode([question]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        output = []
        for i in range(len(results["documents"][0])):
            output.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })
        return output

    def _chunk_document(
        self, doc: ProcessedDocument, doc_type: str
    ) -> list[tuple[str, dict]]:
        chunks = []

        if doc.sections:
            for section_name, section_text in doc.sections.items():
                if len(section_text) > 50:
                    chunks.append((
                        f"[{doc_type}] {section_name}\n{section_text}",
                        {"doc_type": doc_type, "section": section_name, "has_image": "false", "image_path": ""},
                    ))
        else:
            current_chunk = []
            current_len = 0
            for p in doc.paragraphs:
                current_chunk.append(p.text)
                current_len += len(p.text)
                if current_len > 800:
                    chunks.append((
                        f"[{doc_type}]\n" + "\n".join(current_chunk),
                        {"doc_type": doc_type, "section": "General", "has_image": "false", "image_path": ""},
                    ))
                    current_chunk = []
                    current_len = 0
            if current_chunk:
                chunks.append((
                    f"[{doc_type}]\n" + "\n".join(current_chunk),
                    {"doc_type": doc_type, "section": "General", "has_image": "false", "image_path": ""},
                ))

        for table in doc.tables:
            if table.num_rows > 1:
                table_text = "\n".join([" | ".join(row) for row in table.rows])
                chunks.append((
                    f"[{doc_type}] Table\n{table_text}",
                    {"doc_type": doc_type, "section": "Table", "has_image": "false", "image_path": ""},
                ))

        return chunks
