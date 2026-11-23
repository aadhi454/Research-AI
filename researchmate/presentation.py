"""Paper-to-PowerPoint generator module for ResearchMate AI.

This module:
1. Synthesizes a paper-grounded slide outline using Gemini Interactions API / LCEL.
2. Validates the generated outline structure, citations, and metadata.
3. Formats Markdown markers natively into bold runs and plain text to prevent raw symbols.
4. Renders a styled, widescreen (16:9) .pptx presentation using python-pptx with
   cinematic academic typography, varied slide layouts, editable charts, citations,
   and presenter speaker notes.
"""

import html
import io
import json
import re
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from researchmate.analysis import format_paper_pages_for_analysis
from researchmate.config import settings
from researchmate.pdf import ExtractedPage
from researchmate.prompts import build_paper_presentation_chain
from researchmate.rag import (
    GenerationError,
    RAGError,
    format_actionable_error,
)


class PresentationError(RAGError):
    """Raised when presentation outline generation or PPTX building fails."""
    pass


THEMES: Dict[str, Dict[str, Any]] = {
    "Cinematic Teal (ResearchMate Dark)": {
        "bg_color": (11, 21, 40),        # #0b1528
        "card_color": (17, 34, 58),      # #11223a
        "card_border": (30, 58, 95),     # #1e3a5f
        "title_color": (56, 217, 212),   # #38d9d4
        "tag_color": (251, 191, 36),     # #fbbf24
        "body_color": (241, 245, 249),   # #f1f5f9
        "muted_color": (148, 163, 184),  # #94a3b8
    },
    "Academic Classic (Clean Light)": {
        "bg_color": (248, 250, 252),     # #f8fafc
        "card_color": (255, 255, 255),   # #ffffff
        "card_border": (226, 232, 240),  # #e2e8f0
        "title_color": (15, 23, 42),      # #0f172a
        "tag_color": (2, 132, 199),      # #0284c7
        "body_color": (51, 65, 85),      # #334155
        "muted_color": (100, 116, 139),  # #64748b
    },
    "Midnight Slate (Modern Contrast)": {
        "bg_color": (15, 23, 42),        # #0f172a
        "card_color": (30, 41, 59),      # #1e293b
        "card_border": (51, 65, 85),     # #334155
        "title_color": (34, 211, 238),   # #22d3ee
        "tag_color": (168, 85, 247),     # #a855f7
        "body_color": (226, 232, 240),   # #e2e8f0
        "muted_color": (148, 163, 184),  # #94a3b8
    },
}


def clean_plain_text(text: str) -> str:
    """Strip all markdown formatting, bullets, backticks, asterisks, and heading symbols."""
    if not text:
        return ""
    t = text.strip()
    # Strip leading bullet/numbered list marker or heading hashes
    t = re.sub(r"^([•\-\*]\s+|\d+[\.\)]\s+|#+\s+)", "", t)
    # Strip markdown bold/italic asterisks and backticks
    t = re.sub(r"\*\*([^*]+)\*\*", r"\1", t)
    t = re.sub(r"\*([^*]+)\*", r"\1", t)
    t = re.sub(r"`([^`]+)`", r"\1", t)
    return t.replace("**", "").replace("*", "").replace("`", "").strip()


def parse_markdown_spans(text: str) -> List[Tuple[str, bool]]:
    """Parse a bullet point line into styled text spans: list of (text_span, is_bold).

    Strips leading bullets and markdown symbols, separating bold labels from body text.
    Handles both '**Label:** Body' and standard 'Label: Body' patterns so no raw markdown
    markers appear in the PowerPoint presentation.
    """
    if not text:
        return []
    t = text.strip()
    # Strip leading bullet or number marker
    t = re.sub(r"^([•\-\*]\s+|\d+[\.\)]\s+|#+\s+)", "", t)
    t = t.replace("`", "")

    spans: List[Tuple[str, bool]] = []

    # Case 1: **Bold label:** Rest pattern
    bold_prefix_match = re.match(r"^\*\*([^*]+)\*\*[:\s]*(.*)$", t)
    if bold_prefix_match:
        label = bold_prefix_match.group(1).strip().rstrip(":")
        rest = bold_prefix_match.group(2).strip()
        rest_cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", rest).replace("*", "")
        spans.append((f"{label}: ", True))
        if rest_cleaned:
            spans.append((rest_cleaned, False))
        return spans

    # Case 2: Inline **bold** segments anywhere in line
    if "**" in t:
        parts = re.split(r"(\*\*[^*]+\*\*)", t)
        for part in parts:
            if not part:
                continue
            if part.startswith("**") and part.endswith("**") and len(part) >= 4:
                inner = part[2:-2].strip()
                if inner:
                    spans.append((inner, True))
            else:
                cleaned_part = part.replace("*", "")
                if cleaned_part:
                    spans.append((cleaned_part, False))
        return spans

    # Case 3: "Label: Rest" pattern without markdown asterisks (e.g. "Primary Goal: Evaluate...")
    label_match = re.match(r"^([A-Za-z0-9\s\-/]{2,30}):\s+(.*)$", t)
    if label_match and len(label_match.group(1).split()) <= 4:
        label = label_match.group(1).strip()
        rest = label_match.group(2).strip()
        spans.append((f"{label}: ", True))
        if rest:
            spans.append((rest.replace("*", ""), False))
        return spans

    # Case 4: Plain text span without formatting
    spans.append((t.replace("*", ""), False))
    return spans


def add_formatted_bullet_runs(
    paragraph: Any,
    bullet_text: str,
    c_body: RGBColor,
    c_title: RGBColor,
    font_size: Pt = Pt(15),
    space_after: Pt = Pt(12),
) -> None:
    """Add a bullet point to a paragraph using native PowerPoint runs for bold labels and body."""
    paragraph.space_after = space_after
    paragraph.line_spacing = 1.25

    # Native bullet symbol run
    r_sym = paragraph.add_run()
    r_sym.text = "•  "
    r_sym.font.bold = True
    r_sym.font.color.rgb = c_title
    r_sym.font.size = font_size

    spans = parse_markdown_spans(bullet_text)
    for span_text, is_bold in spans:
        if not span_text:
            continue
        run = paragraph.add_run()
        run.text = span_text
        run.font.bold = is_bold
        run.font.color.rgb = c_body
        run.font.size = font_size


def rgb_to_hex(rgb_tuple: Tuple[int, int, int]) -> str:
    """Convert an RGB tuple (r, g, b) into a hex color string."""
    return "#%02x%02x%02x" % rgb_tuple


def render_bullet_spans_html(
    bullet_text: str,
    body_hex: str,
    title_hex: str,
    is_presentation_mode: bool = False,
) -> str:
    """Render bullet spans into clean HTML with native bold label runs and theme bullet."""
    spans = parse_markdown_spans(bullet_text)
    inner_parts: List[str] = []
    for text_content, is_bold in spans:
        escaped = html.escape(text_content)
        if is_bold:
            inner_parts.append(
                f'<strong style="color:{body_hex}; font-weight:700;">{escaped}</strong>'
            )
        else:
            inner_parts.append(
                f'<span style="color:{body_hex}; opacity:0.92;">{escaped}</span>'
            )

    font_size = "1.08rem" if is_presentation_mode else "0.95rem"
    margin_bottom = "1rem" if is_presentation_mode else "0.75rem"
    joined = "".join(inner_parts)
    return (
        f'<li style="margin-bottom:{margin_bottom}; line-height:1.45; font-size:{font_size}; '
        f'list-style:none; display:flex; align-items:baseline;">'
        f'<span style="color:{title_hex}; font-weight:900; margin-right:0.6rem; font-size:1.15em;">•</span>'
        f'<div>{joined}</div>'
        f'</li>'
    )


def render_chart_html(
    chart_data: Dict[str, Any],
    title_hex: str,
    muted_hex: str,
    border_hex: str,
) -> str:
    """Render an inline responsive chart matching theme colors and quantitative data."""
    title = html.escape(str(chart_data.get("title", "Empirical Findings Comparison")))
    categories = [html.escape(str(c)) for c in chart_data.get("categories", [])]
    values = chart_data.get("values", [])
    if not categories or not values or len(categories) != len(values):
        return ""

    max_val = max(values) if values else 1.0
    if max_val <= 0:
        max_val = 1.0

    bars_html: List[str] = []
    for cat, val in zip(categories, values):
        height_pct = max(10, min(100, int((val / max_val) * 100)))
        val_str = (
            f"{val:.1f}"
            if isinstance(val, float) and not val.is_integer()
            else f"{int(val)}"
        )
        bars_html.append(
            f"""
        <div style="flex:1; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; height:100%; min-width:48px;">
          <div style="font-size:0.8rem; font-weight:700; color:{title_hex}; margin-bottom:0.25rem;">{val_str}</div>
          <div style="width:68%; height:{height_pct}%; background:{title_hex}; border-radius:4px 4px 0 0; opacity:0.92;"></div>
          <div style="border-top:1px solid {border_hex}; width:100%; margin-top:0.25rem; padding-top:0.35rem; font-size:0.75rem; color:{muted_hex}; text-align:center; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{cat}</div>
        </div>
        """
        )

    all_bars = "".join(bars_html)
    return f"""
    <div style="background:rgba(255,255,255,0.02); border:1px solid {border_hex}; border-radius:8px; padding:1.25rem 1rem 0.75rem 1rem; width:100%; height:100%; display:flex; flex-direction:column; justify-content:space-between; box-sizing:border-box;">
      <div style="font-size:0.85rem; font-weight:700; color:{title_hex}; text-align:center; margin-bottom:1rem; letter-spacing:0.04em; text-transform:uppercase;">
        📊 {title}
      </div>
      <div style="flex:1; display:flex; align-items:flex-end; justify-content:space-around; gap:0.5rem; height:180px; min-height:160px; box-sizing:border-box; padding-bottom:0.25rem;">
        {all_bars}
      </div>
    </div>
    """


def render_slide_html(
    slide_info: Dict[str, Any],
    theme_name: str,
    total_slides: int,
    duration: str = "10 minutes",
    audience_level: str = "General academic",
    is_presentation_mode: bool = False,
) -> str:
    """Render a slide into a styled, widescreen (16:9) HTML preview consistent with PPTX."""
    theme_def = THEMES.get(theme_name, THEMES["Cinematic Teal (ResearchMate Dark)"])
    bg_hex = rgb_to_hex(theme_def["bg_color"])
    border_hex = rgb_to_hex(theme_def["card_border"])
    title_hex = rgb_to_hex(theme_def["title_color"])
    tag_hex = rgb_to_hex(theme_def["tag_color"])
    body_hex = rgb_to_hex(theme_def["body_color"])
    muted_hex = rgb_to_hex(theme_def["muted_color"])

    min_height = "calc(100vh - 112px)" if is_presentation_mode else "440px"
    padding = "2rem 3.2rem" if is_presentation_mode else "2rem 2.4rem"
    title_font_size = "2.1rem" if is_presentation_mode else "1.75rem"
    content_title_size = "1.65rem" if is_presentation_mode else "1.4rem"

    s_num = slide_info.get("slide_number", 1)
    category = html.escape(str(slide_info.get("category", "KEY TOPIC")).upper())
    title = html.escape(str(slide_info.get("title", "")))
    subtitle = html.escape(str(slide_info.get("subtitle", "")))
    citation = html.escape(str(slide_info.get("citation", "")))
    bullets = slide_info.get("bullet_points", [])
    chart_info = slide_info.get("chart_data")
    layout = slide_info.get("layout", "")

    # Slide 1 (TITLE Slide)
    if s_num == 1 or category == "TITLE":
        author_text = slide_info.get("author") or "Author: Stated in uploaded paper"
        if not author_text.lower().startswith("author"):
            author_text = f"Author: {author_text}"
        author = html.escape(author_text)

        sub_html = (
            f'<div style="font-size:1.15rem; color:{body_hex}; line-height:1.4; opacity:0.9; margin-bottom:1.5rem;">{subtitle}</div>'
            if subtitle
            else ""
        )

        return f"""
        <div style="background:{bg_hex}; border:1px solid {border_hex}; border-radius:{'0' if is_presentation_mode else '12px'}; padding:{padding}; min-height:{min_height}; display:flex; flex-direction:column; justify-content:space-between; box-sizing:border-box; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; box-shadow:0 8px 32px rgba(0,0,0,0.35);">
          <div>
            <div style="font-size:0.85rem; font-weight:800; color:{tag_hex}; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.75rem;">
              ✦ RESEARCHMATE AI · ACADEMIC PRESENTATION
            </div>
            <div style="width:140px; height:3px; background:{title_hex}; border-radius:2px; margin-bottom:1.5rem;"></div>
            <h1 style="font-size:{title_font_size}; font-weight:800; color:{title_hex}; line-height:1.25; margin:0 0 1rem 0;">
              {title}
            </h1>
            {sub_html}
            <div style="font-size:1.1rem; font-weight:700; color:{tag_hex};">
              {author}
            </div>
          </div>
          <div>
            <div style="border-top:1px solid {border_hex}; padding-top:1rem; font-size:0.85rem; color:{muted_hex}; display:flex; justify-content:space-between; align-items:center;">
              <span>Format: {html.escape(duration)} · Audience: {html.escape(audience_level)} · Verified PDF Citations</span>
              <span style="font-weight:600;">Slide 1 of {total_slides}</span>
            </div>
          </div>
        </div>
        """

    # Content Slides (Slides 2 to N)
    sub_html = (
        f'<div style="font-size:0.95rem; color:{muted_hex}; margin-bottom:0.85rem;">{subtitle}</div>'
        if subtitle
        else ""
    )

    # Body Layout Selection
    if chart_info and isinstance(chart_info, dict):
        # Layout C: Empirical Findings with Chart
        bullets_html = "".join(
            [
                render_bullet_spans_html(
                    b, body_hex, title_hex, is_presentation_mode
                )
                for b in bullets[:4]
            ]
        )
        chart_html = render_chart_html(
            chart_data=chart_info,
            title_hex=title_hex,
            muted_hex=muted_hex,
            border_hex=border_hex,
        )
        body_content = f"""
        <div style="display:grid; grid-template-columns: 1.1fr 0.9fr; gap:1.8rem; align-items:center; flex:1;">
          <ul style="margin:0; padding:0;">{bullets_html}</ul>
          <div>{chart_html}</div>
        </div>
        """
    elif len(bullets) >= 4 or layout == "two_column":
        # Layout B: Two-Column Split
        mid = (len(bullets) + 1) // 2
        left_bullets = "".join(
            [
                render_bullet_spans_html(
                    b, body_hex, title_hex, is_presentation_mode
                )
                for b in bullets[:mid]
            ]
        )
        right_bullets = "".join(
            [
                render_bullet_spans_html(
                    b, body_hex, title_hex, is_presentation_mode
                )
                for b in bullets[mid:]
            ]
        )
        body_content = f"""
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:2rem; flex:1;">
          <ul style="margin:0; padding:0;">{left_bullets}</ul>
          <ul style="margin:0; padding:0;">{right_bullets}</ul>
        </div>
        """
    else:
        # Layout A: Single-Column Academic List
        accent_color = tag_hex if category == "LIMITATIONS" else title_hex
        bullets_html = "".join(
            [
                render_bullet_spans_html(
                    b, body_hex, title_hex, is_presentation_mode
                )
                for b in bullets
            ]
        )
        body_content = f"""
        <div style="border-left:3px solid {accent_color}; padding-left:1.5rem; flex:1; display:flex; align-items:center;">
          <ul style="margin:0; padding:0; width:100%;">{bullets_html}</ul>
        </div>
        """

    cite_text = (
        f"📄 Evidence: {citation} · Grounded in uploaded PDF"
        if citation
        else "ResearchMate AI · Grounded Academic Presentation"
    )

    return f"""
    <div style="background:{bg_hex}; border:1px solid {border_hex}; border-radius:{'0' if is_presentation_mode else '12px'}; padding:{padding}; min-height:{min_height}; display:flex; flex-direction:column; justify-content:space-between; box-sizing:border-box; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; box-shadow:0 8px 32px rgba(0,0,0,0.35);">
      <div>
        <div style="font-size:0.8rem; font-weight:800; color:{tag_hex}; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.35rem;">
          {category}
        </div>
        <h2 style="font-size:{content_title_size}; font-weight:700; color:{title_hex}; line-height:1.25; margin:0 0 0.35rem 0;">
          {title}
        </h2>
        {sub_html}
        <div style="width:100%; height:1px; background:{border_hex}; margin-bottom:1.5rem;"></div>
      </div>
      <div style="flex:1; display:flex; align-items:center;">
        {body_content}
      </div>
      <div>
        <div style="border-top:1px solid {border_hex}; padding-top:1rem; font-size:0.85rem; color:{muted_hex}; display:flex; justify-content:space-between; align-items:center;">
          <span>{cite_text}</span>
          <span style="font-weight:600;">Slide {s_num} of {total_slides}</span>
        </div>
      </div>
    </div>
    """


def parse_and_validate_outline(
    raw_response: str,
    expected_count: int = 8,
) -> List[Dict[str, Any]]:
    """Parse and strictly validate JSON slide outline from Gemini response."""
    cleaned = raw_response.strip()

    # Normalize markdown code fences and preamble
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    data = None
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback 1: strip trailing commas which models often produce
        fixed = re.sub(r",\s*([\]\}])", r"\1", cleaned)
        try:
            data = json.loads(fixed)
        except Exception:
            # Fallback 2: locate array brackets [ ... ]
            match = re.search(r"\[\s*\{.*\}\s*\]", cleaned, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                except Exception:
                    pass
            # Fallback 3: locate object brackets { ... }
            if data is None:
                match_obj = re.search(r"\{.*\}", cleaned, re.DOTALL)
                if match_obj:
                    try:
                        data = json.loads(match_obj.group(0))
                    except Exception:
                        pass

    if data is None:
        raise PresentationError(
            "Invalid slide outline format: Failed to parse JSON slide deck from model output."
        )

    # If model wrapped list in a dictionary (e.g. {"slides": [...]})
    if isinstance(data, dict):
        for key in ("slides", "presentation", "deck", "outline", "data"):
            if key in data and isinstance(data[key], list):
                data = data[key]
                break

    if not isinstance(data, list) or len(data) == 0:
        raise PresentationError("Slide outline must be a non-empty list of slide objects.")

    validated: List[Dict[str, Any]] = []
    for idx, item in enumerate(data, 1):
        if not isinstance(item, dict):
            continue

        category = clean_plain_text(str(item.get("category", "KEY TOPIC"))).upper()
        title = clean_plain_text(str(item.get("title", f"Slide {idx}")))
        subtitle = clean_plain_text(str(item.get("subtitle", "")))
        citation = clean_plain_text(str(item.get("citation", "")))
        speaker_notes = clean_plain_text(str(item.get("speaker_notes", "")))
        layout = clean_plain_text(str(item.get("layout", ""))).lower()

        # Handle Slide 1 (TITLE) specifically
        if idx == 1 or category == "TITLE":
            # Extract author from author field or from bullets if model put it there
            author = clean_plain_text(str(item.get("author", "")))
            if not author:
                for b in item.get("bullet_points", []):
                    cb = clean_plain_text(str(b))
                    if cb.lower().startswith("author:") or cb.lower().startswith("authors:"):
                        author = cb.split(":", 1)[1].strip()
                        break
            if not author:
                author = "Author not specified in paper text"

            validated.append(
                {
                    "slide_number": 1,
                    "category": "TITLE",
                    "title": title,
                    "subtitle": subtitle,
                    "author": author,
                    "bullet_points": [],  # Clean title slide has no bullets
                    "citation": "",
                    "layout": "title",
                    "chart_data": None,
                    "speaker_notes": speaker_notes,
                }
            )
            continue

        # Content slides (idx > 1)
        raw_bullets = item.get("bullet_points", [])
        if isinstance(raw_bullets, list):
            bullets = [clean_plain_text(str(b)) for b in raw_bullets if clean_plain_text(str(b))]
        elif isinstance(raw_bullets, str):
            bullets = [
                clean_plain_text(b)
                for b in raw_bullets.split("\n")
                if clean_plain_text(b)
            ]
        else:
            bullets = []

        # Validate optional chart_data (only for quantitative empirical findings)
        chart_data: Optional[Dict[str, Any]] = None
        raw_chart = item.get("chart_data")
        if isinstance(raw_chart, dict):
            c_title = clean_plain_text(str(raw_chart.get("title", "Empirical Findings Comparison")))
            c_series = clean_plain_text(str(raw_chart.get("series_name", "Value")))
            c_cats = [
                clean_plain_text(str(c))
                for c in raw_chart.get("categories", [])
                if clean_plain_text(str(c))
            ]
            c_vals: List[float] = []
            for v in raw_chart.get("values", []):
                try:
                    c_vals.append(float(v))
                except (ValueError, TypeError):
                    continue
            if len(c_cats) >= 2 and len(c_cats) == len(c_vals):
                chart_data = {
                    "title": c_title,
                    "series_name": c_series,
                    "categories": c_cats,
                    "values": c_vals,
                }

        validated.append(
            {
                "slide_number": idx,
                "category": category,
                "title": title,
                "subtitle": subtitle,
                "author": "",
                "bullet_points": bullets,
                "citation": citation,
                "layout": layout,
                "chart_data": chart_data,
                "speaker_notes": speaker_notes,
            }
        )

    min_required = min(3, expected_count)
    if len(validated) < min_required:
        raise PresentationError(
            f"Generated slide outline is too brief ({len(validated)} slides parsed; minimum {min_required} required)."
        )

    return validated


def build_pptx_deck(
    slides_data: List[Dict[str, Any]],
    filename: str,
    theme_name: str = "Cinematic Teal (ResearchMate Dark)",
    duration: str = "10 minutes",
    audience_level: str = "General academic",
) -> bytes:
    """Build a styled, widescreen (16:9) PowerPoint presentation (.pptx) with varied layouts."""
    theme_def = THEMES.get(theme_name, THEMES["Cinematic Teal (ResearchMate Dark)"])

    c_bg = RGBColor(*theme_def["bg_color"])
    c_card_border = RGBColor(*theme_def["card_border"])
    c_title = RGBColor(*theme_def["title_color"])
    c_tag = RGBColor(*theme_def["tag_color"])
    c_body = RGBColor(*theme_def["body_color"])
    c_muted = RGBColor(*theme_def["muted_color"])

    prs = Presentation()
    # Standard 16:9 widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    clean_doc_name = filename.replace(".pdf", "").replace("_", " ").title()
    total_slides = len(slides_data)

    for i, s_info in enumerate(slides_data):
        slide = prs.slides.add_slide(blank_layout)

        # 1. Full slide solid background
        bg = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
        )
        bg.fill.solid()
        bg.fill.fore_color.rgb = c_bg
        bg.line.fill.background()

        # 2. Add Speaker Notes if present
        if s_info.get("speaker_notes"):
            slide.notes_slide.notes_text_frame.text = s_info["speaker_notes"]

        # 3. Slide 1: Simplified Academic Title Slide (No large cards, no bullets)
        if i == 0 or s_info.get("category") == "TITLE":
            # Text box for clean title typography
            tb = slide.shapes.add_textbox(
                Inches(1.2), Inches(1.4), Inches(10.9), Inches(4.8)
            )
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0)
            tf.margin_right = Inches(0)
            tf.margin_top = Inches(0)
            tf.margin_bottom = Inches(0)

            # Category kicker tag
            p_kicker = tf.paragraphs[0]
            p_kicker.text = "✦ RESEARCHMATE AI · ACADEMIC PRESENTATION"
            p_kicker.font.size = Pt(11)
            p_kicker.font.bold = True
            p_kicker.font.color.rgb = c_tag
            p_kicker.space_after = Pt(14)

            # Thin accent rule under kicker
            rule = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(1.85), Inches(2.2), Pt(2)
            )
            rule.fill.solid()
            rule.fill.fore_color.rgb = c_title
            rule.line.fill.background()

            # Paper Title
            p_title = tf.add_paragraph()
            p_title.text = s_info.get("title", clean_doc_name)
            p_title.font.size = Pt(32)
            p_title.font.bold = True
            p_title.font.color.rgb = c_title
            p_title.space_after = Pt(14)

            # Subtitle
            if s_info.get("subtitle"):
                p_sub = tf.add_paragraph()
                p_sub.text = s_info["subtitle"]
                p_sub.font.size = Pt(17)
                p_sub.font.color.rgb = c_body
                p_sub.space_after = Pt(18)

            # Author line
            author_text = s_info.get("author") or "Author: Stated in uploaded paper"
            if not author_text.lower().startswith("author"):
                author_text = f"Author: {author_text}"
            p_auth = tf.add_paragraph()
            p_auth.text = author_text
            p_auth.font.size = Pt(15)
            p_auth.font.bold = True
            p_auth.font.color.rgb = c_tag

            # Bottom Presentation Metadata Row
            p_meta = tf.add_paragraph()
            p_meta.text = (
                f"Format: {duration} · Audience: {audience_level} · Verified PDF Citations"
            )
            p_meta.font.size = Pt(11)
            p_meta.font.color.rgb = c_muted
            p_meta.space_before = Pt(28)

        else:
            # 4. Content Slide Layouts (Varied layouts, no repetitive large rounded cards)
            # Top Header Box
            tb_hdr = slide.shapes.add_textbox(
                Inches(0.9), Inches(0.5), Inches(11.533), Inches(1.3)
            )
            tf_hdr = tb_hdr.text_frame
            tf_hdr.word_wrap = True
            tf_hdr.margin_left = Inches(0)
            tf_hdr.margin_top = Inches(0)

            # Category kicker
            p_cat = tf_hdr.paragraphs[0]
            p_cat.text = s_info.get("category", "KEY TOPIC")
            p_cat.font.size = Pt(10)
            p_cat.font.bold = True
            p_cat.font.color.rgb = c_tag
            p_cat.space_after = Pt(4)

            # Slide Title
            p_htitle = tf_hdr.add_paragraph()
            p_htitle.text = s_info.get("title", "Research Overview")
            p_htitle.font.size = Pt(24)
            p_htitle.font.bold = True
            p_htitle.font.color.rgb = c_title

            # Subtitle (if any)
            if s_info.get("subtitle"):
                p_hsub = tf_hdr.add_paragraph()
                p_hsub.text = s_info["subtitle"]
                p_hsub.font.size = Pt(13)
                p_hsub.font.color.rgb = c_muted

            # Subtle horizontal divider below header
            hdr_line = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(1.95), Inches(11.533), Pt(1)
            )
            hdr_line.fill.solid()
            hdr_line.fill.fore_color.rgb = c_card_border
            hdr_line.line.fill.background()

            bullets = s_info.get("bullet_points", [])
            chart_info = s_info.get("chart_data")
            layout = s_info.get("layout", "")
            category = s_info.get("category", "")

            # Layout Selection:
            # Layout C: Empirical Findings with Native Editable Chart
            if chart_info and isinstance(chart_info, dict):
                # Left Column: Key text findings / bullets
                tb_left = slide.shapes.add_textbox(
                    Inches(0.9), Inches(2.2), Inches(5.0), Inches(4.2)
                )
                tf_left = tb_left.text_frame
                tf_left.word_wrap = True
                tf_left.margin_left = Inches(0)
                tf_left.margin_top = Inches(0)

                for b_idx, b in enumerate(bullets[:4]):
                    p_b = tf_left.paragraphs[0] if b_idx == 0 else tf_left.add_paragraph()
                    add_formatted_bullet_runs(
                        p_b, b, c_body, c_title, font_size=Pt(14), space_after=Pt(12)
                    )

                # Right Column: Native PowerPoint Clustered Column Chart
                try:
                    cd = CategoryChartData()
                    cd.categories = chart_info["categories"]
                    cd.add_series(
                        chart_info.get("series_name", "Metric"),
                        tuple(chart_info["values"]),
                    )
                    chart_shape = slide.shapes.add_chart(
                        XL_CHART_TYPE.COLUMN_CLUSTERED,
                        Inches(6.3),
                        Inches(2.1),
                        Inches(6.1),
                        Inches(4.3),
                        cd,
                    )
                    chart = chart_shape.chart
                    chart.has_legend = False
                    chart.has_title = True
                    chart.chart_title.text_frame.text = chart_info.get(
                        "title", "Empirical Findings Comparison"
                    )
                    chart.chart_title.text_frame.paragraphs[0].font.size = Pt(12)
                    chart.chart_title.text_frame.paragraphs[0].font.bold = True
                    chart.chart_title.text_frame.paragraphs[0].font.color.rgb = c_title

                    # Style series color
                    if len(chart.series) > 0:
                        series = chart.series[0]
                        series.format.fill.solid()
                        series.format.fill.fore_color.rgb = c_title

                    # Style axis labels
                    try:
                        chart.category_axis.tick_labels.font.size = Pt(10)
                        chart.category_axis.tick_labels.font.color.rgb = c_muted
                        chart.value_axis.tick_labels.font.size = Pt(10)
                        chart.value_axis.tick_labels.font.color.rgb = c_muted
                    except Exception:
                        pass
                except Exception:
                    # Fallback to text if chart creation encounters unexpected exception
                    pass

            # Layout B: Two-Column Split Layout (for 4+ bullets or methodology comparisons)
            elif len(bullets) >= 4 or layout == "two_column":
                mid = (len(bullets) + 1) // 2
                left_bullets = bullets[:mid]
                right_bullets = bullets[mid:]

                # Left Column
                tb_c1 = slide.shapes.add_textbox(
                    Inches(0.9), Inches(2.2), Inches(5.5), Inches(4.2)
                )
                tf_c1 = tb_c1.text_frame
                tf_c1.word_wrap = True
                tf_c1.margin_left = Inches(0)
                tf_c1.margin_top = Inches(0)

                for b_idx, b in enumerate(left_bullets):
                    p_b = tf_c1.paragraphs[0] if b_idx == 0 else tf_c1.add_paragraph()
                    add_formatted_bullet_runs(
                        p_b, b, c_body, c_title, font_size=Pt(14), space_after=Pt(14)
                    )

                # Right Column
                tb_c2 = slide.shapes.add_textbox(
                    Inches(6.9), Inches(2.2), Inches(5.5), Inches(4.2)
                )
                tf_c2 = tb_c2.text_frame
                tf_c2.word_wrap = True
                tf_c2.margin_left = Inches(0)
                tf_c2.margin_top = Inches(0)

                for b_idx, b in enumerate(right_bullets):
                    p_b = tf_c2.paragraphs[0] if b_idx == 0 else tf_c2.add_paragraph()
                    add_formatted_bullet_runs(
                        p_b, b, c_body, c_title, font_size=Pt(14), space_after=Pt(14)
                    )

            # Layout A: Single-Column Academic List (Clean Left Accent)
            else:
                # Vertical left accent bar
                accent_color = c_tag if category == "LIMITATIONS" else c_title
                bar = slide.shapes.add_shape(
                    MSO_SHAPE.RECTANGLE,
                    Inches(0.9),
                    Inches(2.3),
                    Pt(3),
                    Inches(3.8),
                )
                bar.fill.solid()
                bar.fill.fore_color.rgb = accent_color
                bar.line.fill.background()

                # Text box for single column
                tb_single = slide.shapes.add_textbox(
                    Inches(1.2), Inches(2.2), Inches(11.2), Inches(4.2)
                )
                tf_single = tb_single.text_frame
                tf_single.word_wrap = True
                tf_single.margin_left = Inches(0)
                tf_single.margin_top = Inches(0)

                for b_idx, b in enumerate(bullets):
                    p_b = tf_single.paragraphs[0] if b_idx == 0 else tf_single.add_paragraph()
                    add_formatted_bullet_runs(
                        p_b, b, c_body, c_title, font_size=Pt(15), space_after=Pt(14)
                    )

            # Bottom Citation & Slide Number Footer Area
            foot_line = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(6.65), Inches(11.533), Pt(1)
            )
            foot_line.fill.solid()
            foot_line.fill.fore_color.rgb = c_card_border
            foot_line.line.fill.background()

            # Left footer: Grounded Evidence Citation
            tb_foot = slide.shapes.add_textbox(
                Inches(0.9), Inches(6.75), Inches(8.5), Inches(0.4)
            )
            tf_foot = tb_foot.text_frame
            tf_foot.margin_left = Inches(0)
            p_foot = tf_foot.paragraphs[0]

            cite_label = s_info.get("citation", "").strip()
            if cite_label:
                p_foot.text = (
                    f"📄 Evidence: {cite_label} · Grounded in uploaded PDF"
                )
            else:
                p_foot.text = "ResearchMate AI · Grounded Academic Presentation"
            p_foot.font.size = Pt(10)
            p_foot.font.color.rgb = c_muted

            # Right footer: Slide number
            tb_num = slide.shapes.add_textbox(
                Inches(9.8), Inches(6.75), Inches(2.6), Inches(0.4)
            )
            tf_num = tb_num.text_frame
            tf_num.margin_right = Inches(0)
            p_num = tf_num.paragraphs[0]
            p_num.alignment = PP_ALIGN.RIGHT
            p_num.text = f"Slide {i+1} of {total_slides}"
            p_num.font.size = Pt(10)
            p_num.font.color.rgb = c_muted

    buf = io.BytesIO()
    prs.save(buf)
    buf.seek(0)
    return buf.getvalue()


def generate_presentation(
    filename: str,
    pages: List[ExtractedPage],
    slide_count: int = 8,
    duration: str = "10 minutes",
    audience_level: str = "General academic",
    theme_name: str = "Cinematic Teal (ResearchMate Dark)",
    on_progress: Optional[Callable[[str, str, float, Optional[Dict[str, Any]]], None]] = None,
) -> Dict[str, Any]:
    """Execute end-to-end presentation generation: outline synthesis -> validation -> PPTX build."""
    t0 = time.perf_counter()

    def report(stage: str, msg: str, extra: Optional[Dict[str, Any]] = None):
        if on_progress:
            elapsed = time.perf_counter() - t0
            on_progress(stage, msg, elapsed, extra or {})

    if not pages:
        raise PresentationError(f"No pages extracted from '{filename}' to generate presentation.")

    # Stage 1: Format paper text with page citations
    report("prep", f"Stage 1/3 · Formatting {len(pages)} pages of '{filename}' for slide synthesis...")
    paper_text = format_paper_pages_for_analysis(pages)
    if not paper_text.strip():
        raise PresentationError(f"No readable digital text found in '{filename}' to create slides.")

    # Stage 2: Generate slide outline using Gemini LCEL chain
    report(
        "outline",
        f"Stage 2/3 · Synthesizing grounded {slide_count}-slide outline with Gemini ({settings.gemini_model})...",
    )
    chain = build_paper_presentation_chain()
    try:
        raw_outline = chain.invoke(
            {
                "filename": filename,
                "paper_text": paper_text,
                "slide_count": slide_count,
                "duration": duration,
                "audience_level": audience_level,
            }
        )
    except Exception as exc:
        actionable = format_actionable_error(exc)
        raise GenerationError(f"Slide outline synthesis failed: {actionable}") from exc

    # Stage 3: Validate outline
    report("validation", "Stage 3/3 · Validating slide structure, citations, and speaker notes...")
    slides_data = parse_and_validate_outline(raw_outline, expected_count=slide_count)

    # Stage 4: Render PowerPoint presentation (.pptx)
    report("pptx", f"Stage 3/3 · Rendering {len(slides_data)} widescreen slides with {theme_name}...")
    pptx_bytes = build_pptx_deck(
        slides_data=slides_data,
        filename=filename,
        theme_name=theme_name,
        duration=duration,
        audience_level=audience_level,
    )

    total_elapsed = time.perf_counter() - t0
    report(
        "complete",
        f"Complete · {len(slides_data)} slides generated in {total_elapsed:.1f}s ({len(pptx_bytes):,} bytes).",
        {"slide_count": len(slides_data), "total_elapsed": total_elapsed},
    )

    return {
        "slides": slides_data,
        "pptx_bytes": pptx_bytes,
        "slide_count": len(slides_data),
        "theme_name": theme_name,
        "duration": duration,
        "audience_level": audience_level,
        "total_elapsed": total_elapsed,
    }
