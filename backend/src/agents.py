import json
import logging
from typing import Any

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
from config import (
    GROQ_API_KEY,
    ANALYSIS_MODEL,
    ROUTER_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
    FEATURE_EXTRACTOR_PROMPT,
    PR_ELEMENTS_EXTRACTOR_PROMPT,
    PRIOR_ART_EXTRACTOR_PROMPT,
    PR_VALIDATOR_PROMPT,
    PRIOR_ART_MAPPER_PROMPT,
    ROUTER_PROMPT,
)

logger = logging.getLogger(__name__)


class AnalysisState(TypedDict, total=False):
    idf_text: str
    pr_text: str
    pr_elements_text: str
    prior_art_text: str
    prior_art_sections: dict[str, str]
    features: list[dict]
    validation: list[dict]
    mapping: dict[str, dict]
    prior_art_labels: dict[str, str]
    error: str
    status: str


def _get_analysis_llm() -> ChatGroq:
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=ANALYSIS_MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        model_kwargs={"response_format": {"type": "json_object"}},
    )


def _get_router_llm() -> ChatGroq:
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=ROUTER_MODEL,
        temperature=0.0,
        max_tokens=1024,
        model_kwargs={"response_format": {"type": "json_object"}},
    )


def _parse_json_response(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        import re
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        raise


def extract_pr_elements_llm(pr_text: str) -> str:
    try:
        llm = _get_analysis_llm()
        prompt = PR_ELEMENTS_EXTRACTOR_PROMPT.format(pr_text=pr_text[:40000])
        response = llm.invoke([HumanMessage(content=prompt)])
        result = _parse_json_response(response.content)

        elements = result.get("elements", [])
        if not elements:
            logger.warning("LLM found no PR elements — falling back to raw PR text")
            return pr_text[:8000]

        lines = []
        for el in elements:
            el_id = el.get("id", "?")
            desc = el.get("description", "")
            text = el.get("text", "")
            lines.append(f"[{el_id}] {desc}: {text}")

        formatted = "\n\n".join(lines)
        logger.info(f"LLM extracted {len(elements)} PR elements")
        return formatted

    except Exception as e:
        logger.error(f"LLM-based PR element extraction failed: {e}")
        return pr_text[:8000]


def extract_prior_art_llm(pr_text: str) -> tuple[dict[str, str], str]:
    try:
        llm = _get_analysis_llm()
        prompt = PRIOR_ART_EXTRACTOR_PROMPT.format(pr_text=pr_text[:40000])
        response = llm.invoke([HumanMessage(content=prompt)])
        result = _parse_json_response(response.content)

        refs = result.get("prior_art_references", [])
        if not refs:
            logger.info("LLM found no prior art references in PR.")
            return {}, ""

        sections = {}
        text_parts = []

        for ref in refs:
            ref_id = ref.get("id", f"D{len(sections)+1}")
            patent_num = ref.get("patent_number", "N/A")
            title = ref.get("title", "")
            text = ref.get("text", "")

            sections[ref_id] = text
            label = f"{patent_num} - {title}" if patent_num != "N/A" else title
            text_parts.append(f"\n--- {ref_id}: {label} ---\n{text}")

        logger.info(f"LLM extracted {len(refs)} prior art references")
        return sections, "\n".join(text_parts)

    except Exception as e:
        logger.error(f"LLM-based prior art extraction failed: {e}")
        return {}, ""


def extract_features_node(state: AnalysisState) -> dict:
    try:
        llm = _get_analysis_llm()
        prompt = FEATURE_EXTRACTOR_PROMPT.format(idf_text=state["idf_text"][:40000])
        response = llm.invoke([HumanMessage(content=prompt)])
        result = _parse_json_response(response.content)
        return {
            "features": result.get("features", []),
            "status": "features_extracted"
        }
    except Exception as e:
        logger.error(f"Feature extraction failed: {e}")
        return {"features": [], "error": str(e), "status": "feature_extraction_failed"}


def validate_pr_node(state: AnalysisState) -> dict:
    try:
        llm = _get_analysis_llm()
        features_json = json.dumps(state["features"], indent=2)
        prompt = PR_VALIDATOR_PROMPT.format(
            features_json=features_json,
            pr_elements_text=state["pr_elements_text"][:40000]
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        result = _parse_json_response(response.content)
        return {
            "validation": result.get("validation", []),
            "status": "pr_validated"
        }
    except Exception as e:
        logger.error(f"PR validation failed: {e}")
        return {"validation": [], "error": str(e), "status": "pr_validation_failed"}


def map_prior_art_node(state: AnalysisState) -> dict:
    try:
        prior_art_text = state.get("prior_art_text", "")
        if not prior_art_text:
            logger.info("No prior art references found — skipping mapping.")
            return {"mapping": {}, "prior_art_labels": {}, "status": "mapping_skipped"}

        llm = _get_analysis_llm()
        features_json = json.dumps(state["features"], indent=2)

        prompt = PRIOR_ART_MAPPER_PROMPT.format(
            features_json=features_json,
            prior_art_text=prior_art_text[:40000]
        )
        response = llm.invoke([HumanMessage(content=prompt)])
        result = _parse_json_response(response.content)
        return {
            "mapping": result.get("mapping", {}),
            "prior_art_labels": result.get("prior_art_labels", {}),
            "status": "mapping_complete"
        }
    except Exception as e:
        logger.error(f"Prior art mapping failed: {e}")
        return {"mapping": {}, "error": str(e), "status": "mapping_failed"}


def build_analysis_graph() -> StateGraph:
    graph = StateGraph(AnalysisState)

    graph.add_node("extract_features", extract_features_node)
    graph.add_node("validate_pr", validate_pr_node)
    graph.add_node("map_prior_art", map_prior_art_node)

    graph.set_entry_point("extract_features")
    graph.add_edge("extract_features", "validate_pr")
    graph.add_edge("validate_pr", "map_prior_art")
    graph.add_edge("map_prior_art", END)

    return graph.compile()


def run_analysis(idf_text: str, pr_text: str) -> AnalysisState:
    logger.info("Extracting PR elements via LLM...")
    pr_elements_text = extract_pr_elements_llm(pr_text)

    logger.info("Extracting prior art references via LLM...")
    prior_art_sections, prior_art_text = extract_prior_art_llm(pr_text)

    graph = build_analysis_graph()
    initial_state: AnalysisState = {
        "idf_text": idf_text,
        "pr_text": pr_text,
        "pr_elements_text": pr_elements_text,
        "prior_art_text": prior_art_text,
        "prior_art_sections": prior_art_sections,
        "features": [],
        "validation": [],
        "mapping": {},
        "prior_art_labels": {},
        "error": "",
        "status": "started",
    }
    result = graph.invoke(initial_state)
    return result


def classify_intent(message: str) -> dict:
    try:
        llm = _get_router_llm()
        prompt = ROUTER_PROMPT.format(message=message)
        response = llm.invoke([HumanMessage(content=prompt)])
        return _parse_json_response(response.content)
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        return {
            "intent": "patent_question",
            "friendly_response": ""
        }
