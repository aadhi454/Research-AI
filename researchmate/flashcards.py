"""Generate and validate paper-grounded study flashcards."""

import json
import re
from typing import Any, Dict, List

from researchmate.pdf import ExtractedPage
from researchmate.prompts import build_paper_flashcards_chain


def _paper_text(pages: List[ExtractedPage]) -> str:
    return "\n\n".join(
        f"[Page {page.page_number}]\n{page.text.strip()}"
        for page in pages
        if page.text.strip()
    )


def _parse_cards(response: str) -> List[Dict[str, str]]:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", response.strip(), flags=re.IGNORECASE)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", cleaned, flags=re.DOTALL)
        if not match:
            raise ValueError("The AI returned an unreadable flashcard set. Please try again.")
        data = json.loads(match.group(0))
    if not isinstance(data, list):
        raise ValueError("The AI returned an unexpected flashcard format. Please try again.")
    cards: List[Dict[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        citation = str(item.get("citation", "")).strip()
        if question and answer:
            cards.append({"question": question, "answer": answer, "citation": citation})
    if len(cards) < 5:
        raise ValueError("The paper did not produce enough usable flashcards. Please try again.")
    return cards[:12]


def generate_flashcards(
    pages: List[ExtractedPage], filename: str, count: int = 10
) -> List[Dict[str, str]]:
    """Generate a varied, page-cited deck using only the active paper."""
    result = build_paper_flashcards_chain().invoke(
        {"filename": filename, "paper_text": _paper_text(pages), "count": count}
    )
    cards = _parse_cards(result)
    valid_pages = {page.page_number for page in pages}
    for card in cards:
        cited = [int(n) for n in re.findall(r"Page\s+(\d+)", card["citation"], flags=re.IGNORECASE)]
        if not cited or not set(cited).issubset(valid_pages):
            card["citation"] = ""
    return cards
