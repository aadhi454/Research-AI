"""Paper-grounded interactive viva practice helpers."""

import json
import re
from typing import Any, Dict, List

from researchmate.pdf import ExtractedPage
from researchmate.prompts import build_viva_feedback_chain, build_viva_question_chain


def _paper_context(pages: List[ExtractedPage]) -> str:
    """Format extracted pages with page labels so answers can cite evidence."""
    return "\n\n".join(
        f"[Page {page.page_number}]\n{page.text.strip()}"
        for page in pages
        if page.text.strip()
    )


def _parse_json(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise ValueError("The AI returned an unreadable response. Please try again.")
        data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("The AI returned an unexpected response. Please try again.")
    return data


def _verified_citation(value: Any, pages: List[ExtractedPage]) -> str:
    """Keep a model citation only when all cited page numbers exist in the PDF."""
    citation = str(value or "").strip()
    referenced = [int(n) for n in re.findall(r"Page\s+(\d+)", citation, flags=re.IGNORECASE)]
    available = {page.page_number for page in pages}
    return citation if referenced and set(referenced).issubset(available) else ""


def start_viva(pages: List[ExtractedPage], filename: str) -> Dict[str, str]:
    """Generate the first viva question from the uploaded paper."""
    result = build_viva_question_chain().invoke(
        {"filename": filename, "paper_text": _paper_context(pages)}
    )
    data = _parse_json(result)
    question = str(data.get("question", "")).strip()
    if not question:
        raise ValueError("No question was generated. Please start the session again.")
    return {
        "question": question,
        "focus": str(data.get("focus", "Core understanding")),
        "citation": _verified_citation(data.get("citation"), pages),
    }


def evaluate_viva_answer(
    pages: List[ExtractedPage],
    filename: str,
    question: str,
    answer: str,
    previous_turns: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Evaluate one response and generate a follow-up unless this is question six."""
    is_final_question = len(previous_turns) >= 5
    history = "\n".join(
        f"Q: {turn['question']}\nA: {turn['answer']}"
        for turn in previous_turns[-4:]
    ) or "No earlier questions."
    result = build_viva_feedback_chain().invoke(
        {
            "filename": filename,
            "paper_text": _paper_context(pages),
            "history": history,
            "question": question,
            "answer": answer.strip(),
            "final_question_instruction": (
                "This is the final question. Do not create another question; set next_question to an empty string."
                if is_final_question
                else "Ask one concise, paper-grounded follow-up question."
            ),
        }
    )
    data = _parse_json(result)
    raw_score = str(data.get("score", "1"))
    score_match = re.search(r"[1-5]", raw_score)
    score = int(score_match.group(0)) if score_match else 1
    next_question = str(data.get("next_question", "")).strip()
    if not next_question and not is_final_question:
        raise ValueError("The AI did not provide a follow-up question. Please try again.")
    return {
        "score": score,
        "strengths": str(data.get("strengths", "")),
        "improve": str(data.get("improve", "")),
        "feedback": str(data.get("feedback", "")),
        "citation": _verified_citation(data.get("citation"), pages),
        "next_question": next_question,
        "next_focus": str(data.get("next_focus", "Follow-up")),
        "next_citation": _verified_citation(data.get("next_citation"), pages),
    }
