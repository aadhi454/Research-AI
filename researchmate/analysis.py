"""Full-paper analysis module: grounded structured summary and key concepts extraction."""

import re
import time
from typing import Any, Callable, Dict, List, Optional

from researchmate.config import settings
from researchmate.pdf import ExtractedPage
from researchmate.prompts import (
    build_paper_concepts_chain,
    build_paper_summary_chain,
)
from researchmate.rag import (
    GenerationError,
    MissingAPIKeyError,
    RAGError,
    format_actionable_error,
    index_paper_chunks,
    is_paper_fully_indexed,
)


def format_paper_pages_for_analysis(pages: List[ExtractedPage]) -> str:
    """Format full paper text page by page preserving 1-based page numbers."""
    sections = []
    for page in pages:
        clean = page.text.strip()
        if clean:
            sections.append(f"--- [Page {page.page_number}] ---\n{clean}")
    return "\n\n".join(sections)


def extract_cited_pages(text: str, total_pages: int = 1000) -> List[int]:
    """Extract unique 1-based page numbers cited in text brackets or parentheses.

    Matches patterns like [Page 1], (Page 2), [Pages 3-5], [p. 6], [Page 7, Page 8].
    """
    found_pages = set()
    citations = re.findall(
        r"[\[\(](?:Pages?|p\.|pp\.)\s*([^\]\)]+)[\]\)]", text, re.IGNORECASE
    )
    for c in citations:
        # Check for numeric ranges like "3-5" or "3–5"
        ranges = re.findall(r"(\d+)\s*[-–]\s*(\d+)", c)
        for start, end in ranges:
            for p in range(int(start), int(end) + 1):
                if 1 <= p <= total_pages:
                    found_pages.add(p)
        # Check for individual numbers
        nums = re.findall(r"\b\d+\b", c)
        for n in nums:
            p = int(n)
            if 1 <= p <= total_pages:
                found_pages.add(p)

    return sorted(list(found_pages))


def get_page_source_passages(
    pages: List[ExtractedPage], cited_pages: List[int]
) -> Dict[int, str]:
    """Map cited page numbers to their clean source text from the paper."""
    source_map: Dict[int, str] = {}
    page_by_num = {p.page_number: p.text.strip() for p in pages}
    for p_num in cited_pages:
        if p_num in page_by_num and page_by_num[p_num]:
            source_map[p_num] = page_by_num[p_num]
    return source_map


def generate_paper_summary(
    filename: str,
    pages: List[ExtractedPage],
    on_progress: Optional[Callable[[str, str, float, Optional[Dict[str, Any]]], None]] = None,
) -> Dict[str, Any]:
    """Generate a comprehensive 6-point grounded summary across the entire paper.

    Covers:
    1. Research problem
    2. Objective
    3. Methodology & data/participants
    4. Key findings
    5. Conclusion
    6. Limitations

    Reuses ChromaDB vector index if already created, or indexes it so subsequent
    retrievals don't re-embed the paper.
    """
    t0 = time.perf_counter()

    def report(stage: str, msg: str, extra: Optional[Dict[str, Any]] = None):
        if on_progress:
            elapsed = time.perf_counter() - t0
            on_progress(stage, msg, elapsed, extra or {})

    if not pages:
        raise RAGError(f"No pages extracted from '{filename}' to analyze.")

    # 1. ChromaDB index check and reuse
    report("check_index", f"Stage 1/4 · Verifying ChromaDB vector index for '{filename}'...")
    if not is_paper_fully_indexed(filename, pages=pages):
        report("indexing", f"Stage 1/4 · Indexing '{filename}' into ChromaDB for persistent reuse...")
        index_paper_chunks(
            pages=pages, filename=filename, on_progress=on_progress, start_time=t0
        )
    else:
        report(
            "check_index",
            f"Stage 1/4 · ChromaDB index verified for '{filename}'. Reusing existing index.",
            {"skipped_embedding": True},
        )

    # 2. Format full paper content preserving 1-based page numbers
    report("prep", f"Stage 2/4 · Formatting full text across {len(pages)} pages with page boundaries...")
    paper_text = format_paper_pages_for_analysis(pages)
    if not paper_text.strip():
        raise RAGError(f"No readable digital text found in '{filename}' to synthesize a summary.")

    total_words = sum(p.word_count for p in pages)
    total_chars = len(paper_text)
    report(
        "prep",
        f"Stage 2/4 · Formatted {len(pages)} pages ({total_words} words, {total_chars:,} chars) for synthesis.",
        {"total_words": total_words, "total_chars": total_chars},
    )

    # 3. Synthesize 6-point summary via LCEL chain
    report(
        "generation",
        f"Stage 3/4 · Synthesizing grounded 6-section summary using Gemini ({settings.gemini_model})...",
    )
    chain = build_paper_summary_chain()
    try:
        summary = chain.invoke({"filename": filename, "paper_text": paper_text})
    except Exception as exc:
        actionable = format_actionable_error(exc)
        raise GenerationError(actionable) from exc

    # 4. Extract page citations and match with source passages
    report("citations", "Stage 4/4 · Extracting page citations and indexing source passages...")
    cited_pages = extract_cited_pages(summary, total_pages=len(pages))
    # Safeguard: if no bracketed citations were found, provide all pages with text
    if not cited_pages:
        cited_pages = [p.page_number for p in pages if p.text.strip()]

    page_sources = get_page_source_passages(pages, cited_pages)

    total_elapsed = time.perf_counter() - t0
    report(
        "complete",
        f"Complete · Summary synthesized in {total_elapsed:.1f}s citing {len(cited_pages)} pages.",
        {"total_elapsed": total_elapsed, "cited_pages": cited_pages},
    )

    return {
        "summary": summary,
        "cited_pages": cited_pages,
        "page_sources": page_sources,
        "total_elapsed": total_elapsed,
    }


def extract_paper_concepts(
    filename: str,
    pages: List[ExtractedPage],
    on_progress: Optional[Callable[[str, str, float, Optional[Dict[str, Any]]], None]] = None,
) -> Dict[str, Any]:
    """Extract key concepts with plain-language explanations and relevance to the paper.

    Reuses ChromaDB vector index if already created, or indexes it so subsequent
    retrievals don't re-embed the paper.
    """
    t0 = time.perf_counter()

    def report(stage: str, msg: str, extra: Optional[Dict[str, Any]] = None):
        if on_progress:
            elapsed = time.perf_counter() - t0
            on_progress(stage, msg, elapsed, extra or {})

    if not pages:
        raise RAGError(f"No pages extracted from '{filename}' to analyze.")

    # 1. ChromaDB index check and reuse
    report("check_index", f"Stage 1/4 · Verifying ChromaDB vector index for '{filename}'...")
    if not is_paper_fully_indexed(filename, pages=pages):
        report("indexing", f"Stage 1/4 · Indexing '{filename}' into ChromaDB for persistent reuse...")
        index_paper_chunks(
            pages=pages, filename=filename, on_progress=on_progress, start_time=t0
        )
    else:
        report(
            "check_index",
            f"Stage 1/4 · ChromaDB index verified for '{filename}'. Reusing existing index.",
            {"skipped_embedding": True},
        )

    # 2. Format full paper content preserving 1-based page numbers
    report("prep", f"Stage 2/4 · Formatting full text across {len(pages)} pages with page boundaries...")
    paper_text = format_paper_pages_for_analysis(pages)
    if not paper_text.strip():
        raise RAGError(f"No readable digital text found in '{filename}' to extract concepts.")

    total_words = sum(p.word_count for p in pages)
    total_chars = len(paper_text)
    report(
        "prep",
        f"Stage 2/4 · Formatted {len(pages)} pages ({total_words} words, {total_chars:,} chars) for concept analysis.",
        {"total_words": total_words, "total_chars": total_chars},
    )

    # 3. Extract key concepts via LCEL chain
    report(
        "generation",
        f"Stage 3/4 · Extracting key concepts using Gemini ({settings.gemini_model})...",
    )
    chain = build_paper_concepts_chain()
    try:
        concepts = chain.invoke({"filename": filename, "paper_text": paper_text})
    except Exception as exc:
        actionable = format_actionable_error(exc)
        raise GenerationError(actionable) from exc

    # 4. Extract page citations and match with source passages
    report("citations", "Stage 4/4 · Extracting page citations and indexing source passages...")
    cited_pages = extract_cited_pages(concepts, total_pages=len(pages))
    if not cited_pages:
        cited_pages = [p.page_number for p in pages if p.text.strip()]

    page_sources = get_page_source_passages(pages, cited_pages)

    total_elapsed = time.perf_counter() - t0
    report(
        "complete",
        f"Complete · Concepts extracted in {total_elapsed:.1f}s citing {len(cited_pages)} pages.",
        {"total_elapsed": total_elapsed, "cited_pages": cited_pages},
    )

    return {
        "concepts": concepts,
        "cited_pages": cited_pages,
        "page_sources": page_sources,
        "total_elapsed": total_elapsed,
    }

