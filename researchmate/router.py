"""Intent detection and routing module for ResearchMate AI.

This module provides a unified router that:
1. Classifies the student's message into one of 7 distinct intents using Gemini:
   - paper_question: routed to grounded PDF vector retrieval & synthesis
   - summary: routed to 6-point full-paper summary
   - key_concepts: routed to key concepts extraction
   - viva, presentation, flashcards: routed to informative "coming soon" notices
   - unclear: routed to clarification prompt
2. Returns transparent routing metadata, including a user-facing route label and execution metrics.
"""

import time
from typing import Any, Callable, Dict, List, Optional

from researchmate.analysis import (
    extract_paper_concepts,
    generate_paper_summary,
)
from researchmate.config import settings
from researchmate.pdf import ExtractedPage
from researchmate.presentation import generate_presentation
from researchmate.prompts import build_intent_detection_chain
from researchmate.rag import (
    GenerationError,
    MissingAPIKeyError,
    RAGError,
    answer_paper_question,
    format_actionable_error,
)

VALID_INTENTS = {
    "paper_question",
    "summary",
    "key_concepts",
    "viva",
    "presentation",
    "flashcards",
    "unclear",
}

INTENT_LABELS = {
    "paper_question": "Grounded Paper Chat",
    "summary": "Full-Paper Summary",
    "key_concepts": "Key Concepts Extraction",
    "presentation": "Presentation Generator",
    "viva": "Viva Practice",
    "flashcards": "Study Flashcards",
    "unclear": "Clarification Needed",
}

COMING_SOON_MESSAGES = {
    "viva": (
        "🎓 **Viva practice is ready.**\n\n"
        "Open the **Viva practice** tab to start a paper-specific oral defense session with feedback and a score."
    ),
    "flashcards": (
        "🃏 **Paper flashcards are ready.**\n\n"
        "Open the **Flashcards** tab to generate, reveal, navigate, and shuffle page-cited study cards."
    ),
}

UNCLEAR_MESSAGE = (
    "🤔 **I'm not sure what you'd like to do with this paper.**\n\n"
    "Here are some things you can ask me:\n"
    "- **Ask a question**: *'What problem does this paper solve?'* or *'What was the methodology?'*\n"
    "- **Generate a summary**: *'Summarize this paper'* or *'Give me an overview'*\n"
    "- **Extract key concepts**: *'Extract the key concepts'* or *'What are the core terms?'*\n"
    "- **Practice your defense or revise**: Open the Viva practice or Flashcards tab."
)


def parse_raw_intent(raw_text: str) -> str:
    """Normalize and map raw model response to a valid intent label."""
    cleaned = (
        raw_text.strip()
        .lower()
        .replace('"', "")
        .replace("'", "")
        .replace("`", "")
        .replace("\n", " ")
    )

    # Check exact match
    if cleaned in VALID_INTENTS:
        return cleaned

    # Check if a valid intent appears as a standalone token
    for intent in [
        "paper_question",
        "key_concepts",
        "summary",
        "viva",
        "presentation",
        "flashcards",
        "unclear",
    ]:
        if intent in cleaned:
            return intent

    return "unclear"


def detect_intent(
    user_input: str,
    timeout: float = 15.0,
) -> str:
    """Classify user intent using the configured Gemini model with low reasoning effort."""
    text = user_input.strip()
    if not text:
        return "unclear"

    chain = build_intent_detection_chain(timeout=timeout, thinking_level="low")
    raw_response = chain.invoke({"user_input": text})
    return parse_raw_intent(raw_response)


def execute_routed_request(
    user_input: str,
    filename: str,
    pages: List[ExtractedPage],
    on_progress: Optional[Callable[[str, str, float, Optional[Dict[str, Any]]], None]] = None,
    existing_summary_data: Optional[Dict[str, Any]] = None,
    existing_concepts_data: Optional[Dict[str, Any]] = None,
    existing_presentation_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Classify user intent and route execution to the appropriate feature.

    Args:
        user_input: The student's prompt or question.
        filename: Name of the uploaded research paper.
        pages: List of extracted ExtractedPage objects.
        on_progress: Optional callback reporting (stage, message, elapsed, extra).
        existing_summary_data: Optional existing summary dict for instant reuse.
        existing_concepts_data: Optional existing concepts dict for instant reuse.
        existing_presentation_data: Optional existing presentation dict for instant reuse.

    Returns:
        Dict containing intent, route_label, answer, sources, cited_pages,
        page_sources, total_elapsed, and optional updated data.
    """
    t0 = time.perf_counter()

    def report(stage: str, msg: str, extra: Optional[Dict[str, Any]] = None):
        if on_progress:
            elapsed = time.perf_counter() - t0
            on_progress(stage, msg, elapsed, extra or {})

    # 1. Intent Detection Stage
    report("intent_detection", "Stage 1/2 · Detecting request intent with Gemini...")
    try:
        intent = detect_intent(user_input)
    except Exception as exc:
        actionable = format_actionable_error(exc)
        raise GenerationError(f"Intent detection failed: {actionable}") from exc

    route_label = INTENT_LABELS.get(intent, "Grounded Paper Chat")
    report(
        "intent_detection",
        f"Stage 1/2 · Detected intent: '{intent}' (Routing to {route_label}).",
        {"intent": intent, "route_label": route_label},
    )

    # 2. Execution Routing Stage
    if intent == "paper_question":
        report("routing", f"Stage 2/2 · Executing Grounded Paper Chat for '{filename}'...")
        qa_result = answer_paper_question(
            question=user_input,
            filename=filename,
            pages=pages,
            on_progress=on_progress,
        )
        total_elapsed = time.perf_counter() - t0
        return {
            "intent": intent,
            "route_label": route_label,
            "answer": qa_result["answer"],
            "sources": qa_result.get("sources", []),
            "cited_pages": [],
            "page_sources": {},
            "total_elapsed": total_elapsed,
        }

    elif intent == "summary":
        report("routing", f"Stage 2/2 · Routing to Full-Paper Summary for '{filename}'...")
        # Reuse existing summary if already generated in session for instantaneous response
        if existing_summary_data and existing_summary_data.get("summary"):
            summary_data = existing_summary_data
            reused = True
            report("routing", "Stage 2/2 · Retrieved existing full-paper summary from active session.")
        else:
            summary_data = generate_paper_summary(
                filename=filename,
                pages=pages,
                on_progress=on_progress,
            )
            reused = False

        total_elapsed = time.perf_counter() - t0
        return {
            "intent": intent,
            "route_label": route_label,
            "answer": summary_data["summary"],
            "sources": [],
            "cited_pages": summary_data.get("cited_pages", []),
            "page_sources": summary_data.get("page_sources", {}),
            "total_elapsed": total_elapsed,
            "updated_summary_data": summary_data if not reused else None,
        }

    elif intent == "key_concepts":
        report("routing", f"Stage 2/2 · Routing to Key Concepts Extraction for '{filename}'...")
        # Reuse existing concepts if already extracted in session for instantaneous response
        if existing_concepts_data and existing_concepts_data.get("concepts"):
            concepts_data = existing_concepts_data
            reused = True
            report("routing", "Stage 2/2 · Retrieved existing key concepts from active session.")
        else:
            concepts_data = extract_paper_concepts(
                filename=filename,
                pages=pages,
                on_progress=on_progress,
            )
            reused = False

        total_elapsed = time.perf_counter() - t0
        return {
            "intent": intent,
            "route_label": route_label,
            "answer": concepts_data["concepts"],
            "sources": [],
            "cited_pages": concepts_data.get("cited_pages", []),
            "page_sources": concepts_data.get("page_sources", {}),
            "total_elapsed": total_elapsed,
            "updated_concepts_data": concepts_data if not reused else None,
        }

    elif intent == "presentation":
        report("routing", f"Stage 2/2 · Routing to Presentation Generator for '{filename}'...")
        if existing_presentation_data and existing_presentation_data.get("slides"):
            pres_data = existing_presentation_data
            reused = True
            report("routing", "Stage 2/2 · Retrieved existing presentation from active session.")
        else:
            pres_data = generate_presentation(
                filename=filename,
                pages=pages,
                slide_count=8,
                duration="10 minutes",
                audience_level="General academic",
                theme_name="Cinematic Teal (ResearchMate Dark)",
                on_progress=on_progress,
            )
            reused = False

        total_elapsed = time.perf_counter() - t0
        slide_summary_bullets = "\n".join(
            f"{s['slide_number']}. **{s['title']}** ({s['category']}) {s.get('citation', '')}"
            for s in pres_data["slides"]
        )
        answer_text = (
            f"📊 **Presentation outline generated ({pres_data['slide_count']} slides)!**\n\n"
            f"{slide_summary_bullets}\n\n"
            f"👉 *Switch to the **Presentation** tab to customize slide count, duration, audience level, "
            f"visual theme, and download your `.pptx` deck!*"
        )
        return {
            "intent": intent,
            "route_label": route_label,
            "answer": answer_text,
            "sources": [],
            "cited_pages": [],
            "page_sources": {},
            "total_elapsed": total_elapsed,
            "updated_presentation_data": pres_data if not reused else None,
        }

    elif intent in COMING_SOON_MESSAGES:
        total_elapsed = time.perf_counter() - t0
        report("complete", f"Complete · {route_label} notice displayed ({total_elapsed:.1f}s).")
        return {
            "intent": intent,
            "route_label": route_label,
            "answer": COMING_SOON_MESSAGES[intent],
            "sources": [],
            "cited_pages": [],
            "page_sources": {},
            "total_elapsed": total_elapsed,
        }

    else:  # unclear
        total_elapsed = time.perf_counter() - t0
        report("complete", f"Complete · Clarification prompt displayed ({total_elapsed:.1f}s).")
        return {
            "intent": "unclear",
            "route_label": route_label,
            "answer": UNCLEAR_MESSAGE,
            "sources": [],
            "cited_pages": [],
            "page_sources": {},
            "total_elapsed": total_elapsed,
        }

