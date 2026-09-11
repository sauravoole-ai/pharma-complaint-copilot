from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.ai.llm import LLMAdapter
from app.domain.schemas import (
    ComplaintFields,
    CompletenessResult,
    CopilotMessage,
    DraftAnalysisResult,
    DraftStatus,
    MessageRole,
    RiskSuggestion,
    SourceType,
)
from app.services.validation import validate_and_classify


class AnalysisInputError(ValueError):
    pass


class AnalysisState(TypedDict, total=False):
    source_text: str
    source_type: SourceType
    llm: LLMAdapter
    normalized_text: str
    fields: ComplaintFields
    completeness: CompletenessResult
    status: DraftStatus
    risk: RiskSuggestion
    summary: str
    result: DraftAnalysisResult


def normalize_input(state: AnalysisState) -> AnalysisState:
    normalized = " ".join(state["source_text"].split())
    if not normalized:
        raise AnalysisInputError("Complaint text cannot be blank")
    return {"normalized_text": normalized}


def extract_complaint(state: AnalysisState) -> AnalysisState:
    fields = state["llm"].extract(state["normalized_text"])
    return {"fields": fields}


def validate_extraction(state: AnalysisState) -> AnalysisState:
    return {"fields": ComplaintFields.model_validate(state["fields"])}


def assess_completeness(state: AnalysisState) -> AnalysisState:
    completeness, status = validate_and_classify(state["fields"])
    return {"completeness": completeness, "status": status}


def suggest_risk(state: AnalysisState) -> AnalysisState:
    return {"risk": state["llm"].suggest_risk(state["fields"])}


def summarize_complaint(state: AnalysisState) -> AnalysisState:
    return {"summary": state["llm"].summarize(state["fields"])}


def assemble_draft(state: AnalysisState) -> AnalysisState:
    missing = state["completeness"].missing_fields
    review_note = (
        f"Review required: add {', '.join(missing)}."
        if missing
        else "Extraction complete. Review every field before committing."
    )
    result = DraftAnalysisResult(
        source_type=state["source_type"],
        fields=state["fields"],
        completeness=state["completeness"],
        risk=state["risk"],
        summary=state["summary"],
        status=state["status"],
        messages=[CopilotMessage(role=MessageRole.ASSISTANT, content=review_note)],
    )
    return {"result": result}


builder = StateGraph(AnalysisState)
builder.add_node("normalize_input", normalize_input)
builder.add_node("extract_complaint", extract_complaint)
builder.add_node("validate_extraction", validate_extraction)
builder.add_node("assess_completeness", assess_completeness)
builder.add_node("suggest_risk", suggest_risk)
builder.add_node("summarize_complaint", summarize_complaint)
builder.add_node("assemble_draft", assemble_draft)
builder.add_edge(START, "normalize_input")
builder.add_edge("normalize_input", "extract_complaint")
builder.add_edge("extract_complaint", "validate_extraction")
builder.add_edge("validate_extraction", "assess_completeness")
builder.add_edge("assess_completeness", "suggest_risk")
builder.add_edge("suggest_risk", "summarize_complaint")
builder.add_edge("summarize_complaint", "assemble_draft")
builder.add_edge("assemble_draft", END)
analysis_graph = builder.compile()


def run_analysis(source_text: str, source_type: SourceType, llm: LLMAdapter) -> DraftAnalysisResult:
    final_state = analysis_graph.invoke(
        {"source_text": source_text, "source_type": source_type, "llm": llm}
    )
    return final_state["result"]
