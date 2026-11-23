"""Comprehensive automated test suite for Research AI agents, tools, and workflows."""

import io
import json
import pytest
import pymupdf

from researchmate.config import (
    DEFAULT_GEMINI_MODEL,
    DEFAULT_EMBEDDING_MODEL,
    normalize_model_name,
    normalize_embedding_model_name,
    Settings,
)
from researchmate.pdf import (
    ExtractedPage,
    EmptyPDFError,
    InvalidPDFError,
    extract_pages_from_pdf,
)
from researchmate.rag import (
    split_pages_into_chunks,
    format_actionable_error,
    format_context_for_prompt,
)
from researchmate.router import (
    parse_raw_intent,
    _heuristic_intent,
)
from researchmate.presentation import (
    parse_and_validate_outline,
    clean_plain_text,
    PresentationError,
)
from researchmate.viva import _parse_json
from researchmate.flashcards import _parse_cards


def _create_sample_pdf_bytes(num_pages: int = 3) -> bytes:
    """Generate in-memory PDF with known text on each page for test isolation."""
    doc = pymupdf.open()
    for i in range(1, num_pages + 1):
        page = doc.new_page()
        page.insert_text(
            (50, 72),
            f"Research Paper Heading Page {i}\n"
            f"This is the body content of page {i} describing transformers and attention mechanisms. "
            f"The proposed architecture demonstrates superior empirical performance on benchmark datasets.",
        )
    buf = io.BytesIO()
    doc.save(buf)
    doc.close()
    return buf.getvalue()


class TestModelAndSettingsNormalization:
    def test_model_normalization(self):
        assert normalize_model_name("gemini-2.5-flash") == "gemini-2.0-flash"
        assert normalize_model_name("models/gemini-1.5-flash") == "gemini-1.5-flash"
        assert normalize_model_name(None) == DEFAULT_GEMINI_MODEL
        assert normalize_model_name("") == DEFAULT_GEMINI_MODEL

    def test_embedding_normalization(self):
        assert normalize_embedding_model_name("models/gemini-embedding-001") == "models/text-embedding-004"
        assert normalize_embedding_model_name("gemini-embedding-001") == "models/text-embedding-004"
        assert normalize_embedding_model_name("text-embedding-004") == "models/text-embedding-004"
        assert normalize_embedding_model_name(None) == DEFAULT_EMBEDDING_MODEL


class TestPDFIntake:
    def test_extract_pages_success(self):
        pdf_bytes = _create_sample_pdf_bytes(num_pages=3)
        pages = extract_pages_from_pdf(pdf_bytes, filename="sample.pdf")
        assert len(pages) == 3
        assert pages[0].page_number == 1
        assert pages[1].page_number == 2
        assert pages[2].page_number == 3
        assert "Page 1" in pages[0].text
        assert pages[0].word_count > 0
        assert pages[0].char_count > 0

    def test_empty_pdf_raises_error(self):
        with pytest.raises(EmptyPDFError):
            extract_pages_from_pdf(b"", filename="empty.pdf")

    def test_invalid_pdf_raises_error(self):
        with pytest.raises(InvalidPDFError):
            extract_pages_from_pdf(b"not a valid pdf data", filename="corrupt.pdf")


class TestRAGChunkingAndFormatting:
    def test_split_pages_into_chunks(self):
        pages = [
            ExtractedPage(page_number=1, text="First page content with important findings."),
            ExtractedPage(page_number=2, text="Second page content with methodology and data."),
        ]
        docs = split_pages_into_chunks(pages, filename="test.pdf", chunk_size=50, chunk_overlap=10)
        assert len(docs) >= 2
        for doc in docs:
            assert doc.metadata["filename"] == "test.pdf"
            assert doc.metadata["page"] in (1, 2)
            assert "chunk_index" in doc.metadata

    def test_format_actionable_error_redaction(self):
        secret_key = "AIzaSySecretKey12345"
        err = Exception(f"Failed request with key {secret_key}: 400 Bad Request")
        formatted = format_actionable_error(err, api_key=secret_key)
        assert secret_key not in formatted
        assert "[REDACTED_API_KEY]" in formatted or "Invalid Gemini API key" in formatted

    def test_format_actionable_error_actionable_messages(self):
        assert "timed out" in format_actionable_error(Exception("504 Gateway Timeout")).lower()
        assert "quota" in format_actionable_error(Exception("429 Resource Exhausted")).lower()
        assert "api key is required" in format_actionable_error(Exception("api key is not configured")).lower()


class TestIntentDetectionAndRouting:
    def test_parse_raw_intent(self):
        assert parse_raw_intent("paper_question") == "paper_question"
        assert parse_raw_intent('"summary"') == "summary"
        assert parse_raw_intent("key_concepts\n") == "key_concepts"
        assert parse_raw_intent("presentation") == "presentation"
        assert parse_raw_intent("viva") == "viva"
        assert parse_raw_intent("flashcards") == "flashcards"
        assert parse_raw_intent("unclear") == "unclear"

    def test_heuristic_intent_fallback(self):
        assert _heuristic_intent("Can you summarize this paper for me?") == "summary"
        assert _heuristic_intent("Extract the core key concepts") == "key_concepts"
        assert _heuristic_intent("Create presentation slides") == "presentation"
        assert _heuristic_intent("Practice oral viva defense") == "viva"
        assert _heuristic_intent("Generate revision flashcards") == "flashcards"
        assert _heuristic_intent("What dataset was used in section 4?") == "paper_question"
        assert _heuristic_intent("hi") == "unclear"


class TestPresentationValidation:
    def test_parse_valid_outline(self):
        sample_json = """
        [
            {
                "slide_number": 1,
                "category": "TITLE",
                "title": "Attention Is All You Need",
                "subtitle": "Transformer Architecture",
                "author": "Vaswani et al.",
                "bullet_points": [],
                "citation": "",
                "speaker_notes": "Welcome to our presentation on the Transformer model."
            },
            {
                "slide_number": 2,
                "category": "PROBLEM",
                "title": "Recurrence Bottlenecks",
                "bullet_points": ["Sequential computation: Prevents parallelization", "Long dependencies: Vanishing gradients"],
                "citation": "[Page 2]",
                "speaker_notes": "RNNs suffer from sequential compute constraints."
            }
        ]
        """
        slides = parse_and_validate_outline(sample_json, expected_count=2)
        assert len(slides) == 2
        assert slides[0]["category"] == "TITLE"
        assert slides[0]["title"] == "Attention Is All You Need"
        assert slides[1]["category"] == "PROBLEM"

    def test_parse_outline_with_trailing_comma_and_wrapping(self):
        wrapped_json = """
        ```json
        {
            "slides": [
                {
                    "slide_number": 1,
                    "category": "TITLE",
                    "title": "Deep Learning Survey",
                    "author": "LeCun et al.",
                    "bullet_points": [],
                },
            ]
        }
        ```
        """
        slides = parse_and_validate_outline(wrapped_json, expected_count=1)
        assert len(slides) == 1
        assert slides[0]["title"] == "Deep Learning Survey"


class TestVivaAndFlashcardsParsing:
    def test_viva_json_parsing(self):
        raw = '{"question": "What is the primary contribution?", "focus": "Core thesis", "citation": "[Page 1]",}'
        data = _parse_json(raw)
        assert data["question"] == "What is the primary contribution?"
        assert data["focus"] == "Core thesis"

    def test_flashcards_parsing(self):
        raw = """
        ```json
        [
            {"question": "Q1", "answer": "A1", "citation": "[Page 1]"},
            {"question": "Q2", "answer": "A2", "citation": "[Page 2]"},
            {"question": "Q3", "answer": "A3", "citation": "[Page 3]"},
        ]
        ```
        """
        cards = _parse_cards(raw)
        assert len(cards) == 3
        assert cards[0]["question"] == "Q1"
        assert cards[0]["answer"] == "A1"
