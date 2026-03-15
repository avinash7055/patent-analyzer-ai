import logging

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
from config import GROQ_API_KEY, ANALYSIS_MODEL, TEMPERATURE, MAX_TOKENS, RAG_CHAT_PROMPT
from src.agents import classify_intent
from src.vector_store import VectorStore

logger = logging.getLogger(__name__)


class ChatEngine:

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model_name=ANALYSIS_MODEL,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        self.history: list[dict] = []

    def chat(self, message: str) -> dict:
        intent_result = classify_intent(message)
        intent = intent_result.get("intent", "patent_question")

        if intent == "greeting":
            response_text = intent_result.get(
                "friendly_response",
                "Hello! I am your patent analysis assistant. Ask me anything about the IDF, PR, key features, or prior art mapping."
            )
            self._add_to_history(message, response_text)
            return {
                "intent": intent,
                "answer": response_text,
                "sources": [],
                "images": [],
            }

        if intent == "irrelevant":
            response_text = intent_result.get(
                "friendly_response",
                "I specialize in patent analysis. Try asking about key features, prior art mapping, or the patentability report."
            )
            self._add_to_history(message, response_text)
            return {
                "intent": intent,
                "answer": response_text,
                "sources": [],
                "images": [],
            }

        if intent == "export_request":
            self._add_to_history(message, "Use the Report tab to download the PDF report or export the mapping table as CSV.")
            return {
                "intent": intent,
                "answer": "You can download the PDF report from the Report tab, or export the prior art mapping table as CSV from the Matrix tab.",
                "sources": [],
                "images": [],
            }

        return self._rag_answer(message)

    # Keywords that indicate the user wants to see images/figures
    _IMAGE_KEYWORDS = {
        "image", "images", "figure", "figures", "diagram", "diagrams",
        "picture", "pictures", "photo", "drawing", "drawings",
        "illustration", "chart", "graph", "show me", "visual",
    }

    def _wants_images(self, question: str) -> bool:
        q_lower = question.lower()
        return any(kw in q_lower for kw in self._IMAGE_KEYWORDS)

    def _rag_answer(self, question: str) -> dict:
        try:
            retrieved = self.vector_store.query(question)

            context_parts = []
            sources = []
            images = []
            seen_sources = set()

            wants_images = self._wants_images(question)

            for chunk in retrieved:
                context_parts.append(chunk["text"])

                # Deduplicate sources
                src_key = (
                    chunk["metadata"].get("doc_type", ""),
                    chunk["metadata"].get("section", ""),
                )
                if src_key not in seen_sources:
                    seen_sources.add(src_key)
                    sources.append({
                        "section": src_key[1],
                        "doc_type": src_key[0],
                    })

                # Only include images if the user specifically asks
                if wants_images and chunk["metadata"].get("has_image") == "true":
                    img_path = chunk["metadata"].get("image_path", "")
                    if img_path and img_path not in images:
                        images.append(img_path)

            context = "\n\n---\n\n".join(context_parts)
            chat_history = self._format_history()

            prompt = RAG_CHAT_PROMPT.format(
                context=context,
                chat_history=chat_history,
                question=question,
            )

            response = self.llm.invoke([HumanMessage(content=prompt)])
            answer = response.content

            self._add_to_history(question, answer)

            return {
                "intent": "patent_question",
                "answer": answer,
                "sources": sources,
                "images": images,
            }

        except Exception as e:
            logger.error(f"RAG answer failed: {e}")
            return {
                "intent": "error",
                "answer": f"An error occurred while processing your question. Please try again.",
                "sources": [],
                "images": [],
            }

    def _add_to_history(self, user_msg: str, assistant_msg: str):
        self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": assistant_msg})
        if len(self.history) > 20:
            self.history = self.history[-20:]

    def _format_history(self) -> str:
        if not self.history:
            return "No previous conversation."
        lines = []
        for msg in self.history[-10:]:
            role = msg["role"].capitalize()
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    def clear_history(self):
        self.history = []
