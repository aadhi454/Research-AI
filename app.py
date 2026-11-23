"""ResearchMate AI: paper-to-presentation and viva assistant."""

import html
import random
import streamlit as st

from researchmate.analysis import (
    extract_paper_concepts,
    generate_paper_summary,
)
from researchmate.config import settings
from researchmate.pdf import PDFProcessingError, extract_pages_from_pdf
from researchmate.presentation import (
    THEMES,
    PresentationError,
    generate_presentation,
    render_slide_html,
)
from researchmate.rag import (
    EmbeddingError,
    GenerationError,
    MissingAPIKeyError,
    RAGError,
    RetrievalError,
    format_actionable_error,
    is_paper_fully_indexed,
)
from researchmate.router import execute_routed_request
from researchmate.viva import evaluate_viva_answer, start_viva
from researchmate.flashcards import generate_flashcards
from researchmate.progress import load_viva_history, save_completed_viva
from researchmate.styles import (
    CUSTOM_CSS,
    get_header_html,
    get_hero_html,
    get_workflow_cards_html,
)


st.set_page_config(
    page_title="Research AI · AGENTIC-AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject violet-cosmos CSS and SVG atmosphere — AGENTIC-AI edition
st.html(CUSTOM_CSS)

# Initialize session state for extracted pages, paper metadata, grounded chat, and paper analysis
if "extracted_pages" not in st.session_state:
    st.session_state["extracted_pages"] = None
if "paper_pages" not in st.session_state:
    st.session_state["paper_pages"] = None
if "uploaded_paper_name" not in st.session_state:
    st.session_state["uploaded_paper_name"] = None
if "pdf_error" not in st.session_state:
    st.session_state["pdf_error"] = None
if "last_uploaded_file_id" not in st.session_state:
    st.session_state["last_uploaded_file_id"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "paper_summary_data" not in st.session_state:
    st.session_state["paper_summary_data"] = None
if "paper_concepts_data" not in st.session_state:
    st.session_state["paper_concepts_data"] = None
if "presentation_data" not in st.session_state:
    st.session_state["presentation_data"] = None
if "presenter_mode" not in st.session_state:
    st.session_state["presenter_mode"] = False
if "current_slide_idx" not in st.session_state:
    st.session_state["current_slide_idx"] = 0
if "viva_session" not in st.session_state:
    st.session_state["viva_session"] = None
if "flashcard_deck" not in st.session_state:
    st.session_state["flashcard_deck"] = None
if "flashcard_index" not in st.session_state:
    st.session_state["flashcard_index"] = 0
if "flashcard_revealed" not in st.session_state:
    st.session_state["flashcard_revealed"] = False
VIVA_QUESTION_LIMIT = 6

# Compact product header
st.html("""
<div style="display:flex; align-items:center; justify-content:space-between; gap:1rem;
margin:.25rem 0 1rem; padding:.8rem 1rem; border:1px solid rgba(192,132,252,.16);
border-radius:14px; background:rgba(11,4,28,.72); backdrop-filter:blur(14px);">
  <div>
    <div style="font-size:.68rem; letter-spacing:.16em; color:#a78bfa; text-transform:uppercase;">AGENTIC-AI workspace</div>
    <div style="font-size:1.25rem; font-weight:750; color:#f8fafc;">Research AI</div>
  </div>
  <div style="font-size:.75rem; color:#a7a0b8;">PDF analysis · Grounded chat · Viva · Slides</div>
</div>
""")

# Sidebar configuration and status
with st.sidebar:
    st.markdown("### 🔬 Research AI · AGENTIC-AI")
    st.caption("Academic intelligence workspace")
    st.divider()
    st.subheader("Workspace")
    if settings.gemini_api_key and settings.gemini_api_key.strip() not in ("", "your_gemini_api_key_here"):
        st.success("AI services connected", icon=":material/check_circle:")
    else:
        st.info("AI features are ready for deployment secrets.", icon=":material/cloud:")

    if st.session_state.get("uploaded_paper_name") and st.session_state.get("extracted_pages"):
        st.divider()
        st.subheader("Active document")
        st.markdown(f"📄 **{st.session_state['uploaded_paper_name']}**")
        st.caption(f"{len(st.session_state['extracted_pages'])} pages ready in session memory")
        if is_paper_fully_indexed(
            st.session_state["uploaded_paper_name"],
            pages=st.session_state["extracted_pages"],
        ):
            st.caption("⚡ ChromaDB Vector Index: Fully indexed")
        else:
            st.caption("ChromaDB Vector Index: Pending (will index on action)")

        if st.session_state.get("paper_summary_data"):
            st.caption("📑 Summary: Generated")
        if st.session_state.get("paper_concepts_data"):
            st.caption("💡 Key concepts: Extracted")
        if st.session_state.get("presentation_data"):
            st.caption("📊 Presentation: Deck ready")

overview, paper_chat, viva, slides, flashcards, dashboard = st.tabs(
    ["🏠 Overview", "💬 Paper Chat", "🎓 Viva Practice", "📊 Presentation", "🗂️ Flashcards", "📈 Dashboard"]
)

with overview:
    st.subheader("Research workspace")
    metric1, metric2, metric3 = st.columns(3)
    with metric1:
        st.metric(
            "Active paper",
            st.session_state["uploaded_paper_name"] or "Not uploaded",
        )
    with metric2:
        st.metric(
            "Pages ready",
            len(st.session_state["extracted_pages"] or []),
        )
    with metric3:
        completed = sum(
            bool(st.session_state.get(key))
            for key in ("paper_summary_data", "paper_concepts_data", "presentation_data", "flashcard_deck")
        )
        st.metric("Outputs generated", completed)

    st.markdown("#### Agent workflow")
    st.html(get_workflow_cards_html())

with paper_chat:
    st.subheader("📄 Paper Intake & Grounded Chat")
    st.caption("Upload a research paper to extract page-indexed text, analyze full-paper insights, and chat with evidence-grounded AI. · AGENTIC-AI by vSalagundiadikeshavareddy")

    uploaded_file = st.file_uploader(
        "Upload a research paper (PDF)",
        type=["pdf"],
        key="pdf_uploader",
        help="Upload a research paper PDF containing digital selectable text.",
    )

    def reset_paper_features():
        st.session_state["chat_history"] = []
        st.session_state["paper_summary_data"] = None
        st.session_state["paper_concepts_data"] = None
        st.session_state["presentation_data"] = None
        st.session_state["presenter_mode"] = False
        st.session_state["current_slide_idx"] = 0
        st.session_state["viva_session"] = None
        st.session_state["flashcard_deck"] = None
        st.session_state["flashcard_index"] = 0
        st.session_state["flashcard_revealed"] = False

    if uploaded_file is not None:
        file_id = (uploaded_file.name, uploaded_file.size)
        # Re-extract only if a new or different file is uploaded
        if st.session_state["last_uploaded_file_id"] != file_id:
            st.session_state["last_uploaded_file_id"] = file_id
            try:
                pages = extract_pages_from_pdf(
                    uploaded_file.getvalue(), filename=uploaded_file.name
                )
                st.session_state["extracted_pages"] = pages
                st.session_state["paper_pages"] = pages
                st.session_state["uploaded_paper_name"] = uploaded_file.name
                st.session_state["pdf_error"] = None
                reset_paper_features()
            except PDFProcessingError as err:
                st.session_state["extracted_pages"] = None
                st.session_state["paper_pages"] = None
                st.session_state["uploaded_paper_name"] = None
                st.session_state["pdf_error"] = str(err)
                reset_paper_features()
            except Exception as err:
                st.session_state["extracted_pages"] = None
                st.session_state["paper_pages"] = None
                st.session_state["uploaded_paper_name"] = None
                st.session_state["pdf_error"] = (
                    f"An unexpected error occurred while reading '{uploaded_file.name}': {err}"
                )
                reset_paper_features()
    else:
        # Reset state only if the user actively removes an existing uploaded file
        if st.session_state.get("last_uploaded_file_id") is not None:
            st.session_state["extracted_pages"] = None
            st.session_state["paper_pages"] = None
            st.session_state["uploaded_paper_name"] = None
            st.session_state["pdf_error"] = None
            st.session_state["last_uploaded_file_id"] = None
            reset_paper_features()

    if st.session_state["pdf_error"]:
        st.error(st.session_state["pdf_error"], icon=":material/error:")
    elif st.session_state["extracted_pages"]:
        pages = st.session_state["extracted_pages"]
        total_pages = len(pages)
        page_label = "page" if total_pages == 1 else "pages"

        st.success(
            f"Successfully extracted {total_pages} {page_label} from **{st.session_state['uploaded_paper_name']}**.",
            icon=":material/check_circle:",
        )

        st.subheader("Preview extracted text by page")

        if total_pages > 1:
            selected_page_num = st.selectbox(
                "Select page to preview",
                options=list(range(1, total_pages + 1)),
                format_func=lambda p: f"Page {p} of {total_pages}",
                key="preview_page_select",
            )
        else:
            selected_page_num = 1

        current_page = pages[selected_page_num - 1]

        with st.container(border=True, height=420):
            col_hdr_left, col_hdr_right = st.columns([2, 1], vertical_alignment="center")
            with col_hdr_left:
                st.markdown(f"**Page {current_page.page_number} of {total_pages}**")
            with col_hdr_right:
                st.caption(f"{current_page.word_count} words · {current_page.char_count} characters")

            if current_page.text.strip():
                st.text(current_page.text, wrap=True)
            else:
                st.info(
                    "No readable digital text found on this page. It may contain diagrams, charts, or images.",
                    icon=":material/info:",
                )

        # Paper Analysis Area (Available after PDF upload)
        st.divider()
        st.subheader("Paper analysis")
        st.caption("Deep full-paper academic synthesis grounded in original text with page citations.")

        analysis_tab1, analysis_tab2 = st.tabs(["📑 Structured summary", "💡 Key concepts"])

        with analysis_tab1:
            st.markdown("##### Full-paper academic summary")
            st.caption(
                "Synthesizes the complete paper across 6 core sections: Research Problem, Objective, "
                "Methodology & Data, Key Findings, Conclusion, and Limitations."
            )
            col_sum_btn, col_sum_status = st.columns([1, 2], vertical_alignment="center")
            with col_sum_btn:
                btn_summary = st.button(
                    "Generate summary" if not st.session_state.get("paper_summary_data") else "Regenerate summary",
                    key="btn_generate_summary",
                    type="primary",
                    icon=":material/summarize:",
                )
            with col_sum_status:
                if st.session_state.get("paper_summary_data"):
                    sum_time = st.session_state["paper_summary_data"].get("total_elapsed", 0.0)
                    st.caption(f"⚡ Last synthesized in {sum_time:.1f}s")

            if btn_summary:
                if not settings.gemini_api_key or settings.gemini_api_key.strip() in ("", "your_gemini_api_key_here"):
                    st.error(
                        "AI analysis is unavailable until the Gemini service is configured.",
                        icon=":material/key:",
                    )
                else:
                    with st.status("Analyzing full paper & synthesizing summary...", expanded=True) as status_box:
                        def sum_progress_listener(stage: str, msg: str, elapsed: float, extra: dict = None):
                            status_box.write(f"⏱️ **[{elapsed:.1f}s]** {msg}")

                        try:
                            summary_data = generate_paper_summary(
                                filename=st.session_state["uploaded_paper_name"],
                                pages=pages,
                                on_progress=sum_progress_listener,
                            )
                            total_time = summary_data.get("total_elapsed", 0.0)
                            status_box.update(
                                label=f"Summary synthesized in {total_time:.1f}s",
                                state="complete",
                                expanded=False,
                            )
                            st.session_state["paper_summary_data"] = summary_data
                        except (MissingAPIKeyError, EmbeddingError, RetrievalError, GenerationError, RAGError) as exc:
                            status_box.update(label="Summary generation failed", state="error", expanded=True)
                            actionable_msg = format_actionable_error(exc)
                            st.error(actionable_msg, icon=":material/error:")
                        except Exception as exc:
                            status_box.update(label="Unexpected error", state="error", expanded=True)
                            actionable_msg = format_actionable_error(exc)
                            st.error(f"An error occurred: {actionable_msg}", icon=":material/error:")

            if st.session_state.get("paper_summary_data"):
                sum_data = st.session_state["paper_summary_data"]
                with st.container(border=True):
                    st.markdown("#### 📄 Executive academic summary")
                    st.markdown(sum_data["summary"])
                    if sum_data.get("total_elapsed"):
                        st.caption(f"⚡ Synthesized in {sum_data['total_elapsed']:.1f}s")

                    cited_pages = sum_data.get("cited_pages", [])
                    page_sources = sum_data.get("page_sources", {})
                    if cited_pages and page_sources:
                        st.divider()
                        st.caption("🔍 **Cited page evidence & source passages:** (expand to inspect original page text)")
                        for p_num in cited_pages:
                            if p_num in page_sources:
                                page_obj = next((p for p in pages if p.page_number == p_num), None)
                                w_count = page_obj.word_count if page_obj else len(page_sources[p_num].split())
                                with st.expander(f"📄 Citation · Page {p_num} ({w_count} words)", expanded=False):
                                    st.caption(f"Document: {st.session_state['uploaded_paper_name']} · Page {p_num}")
                                    st.text(page_sources[p_num], wrap=True)

        with analysis_tab2:
            st.markdown("##### Key concepts & theoretical frameworks")
            st.caption(
                "Extracts essential academic concepts with plain-language explanations, their specific importance "
                "to this paper, and verifiable page citations."
            )
            col_con_btn, col_con_status = st.columns([1, 2], vertical_alignment="center")
            with col_con_btn:
                btn_concepts = st.button(
                    "Extract key concepts" if not st.session_state.get("paper_concepts_data") else "Re-extract key concepts",
                    key="btn_extract_concepts",
                    type="primary",
                    icon=":material/lightbulb:",
                )
            with col_con_status:
                if st.session_state.get("paper_concepts_data"):
                    con_time = st.session_state["paper_concepts_data"].get("total_elapsed", 0.0)
                    st.caption(f"⚡ Last extracted in {con_time:.1f}s")

            if btn_concepts:
                if not settings.gemini_api_key or settings.gemini_api_key.strip() in ("", "your_gemini_api_key_here"):
                    st.error(
                        "AI analysis is unavailable until the Gemini service is configured.",
                        icon=":material/key:",
                    )
                else:
                    with st.status("Analyzing full paper & extracting key concepts...", expanded=True) as status_box:
                        def con_progress_listener(stage: str, msg: str, elapsed: float, extra: dict = None):
                            status_box.write(f"⏱️ **[{elapsed:.1f}s]** {msg}")

                        try:
                            concepts_data = extract_paper_concepts(
                                filename=st.session_state["uploaded_paper_name"],
                                pages=pages,
                                on_progress=con_progress_listener,
                            )
                            total_time = concepts_data.get("total_elapsed", 0.0)
                            status_box.update(
                                label=f"Key concepts extracted in {total_time:.1f}s",
                                state="complete",
                                expanded=False,
                            )
                            st.session_state["paper_concepts_data"] = concepts_data
                        except (MissingAPIKeyError, EmbeddingError, RetrievalError, GenerationError, RAGError) as exc:
                            status_box.update(label="Concept extraction failed", state="error", expanded=True)
                            actionable_msg = format_actionable_error(exc)
                            st.error(actionable_msg, icon=":material/error:")
                        except Exception as exc:
                            status_box.update(label="Unexpected error", state="error", expanded=True)
                            actionable_msg = format_actionable_error(exc)
                            st.error(f"An error occurred: {actionable_msg}", icon=":material/error:")

            if st.session_state.get("paper_concepts_data"):
                con_data = st.session_state["paper_concepts_data"]
                with st.container(border=True):
                    st.markdown("#### 💡 Extracted key concepts")
                    st.markdown(con_data["concepts"])
                    if con_data.get("total_elapsed"):
                        st.caption(f"⚡ Extracted in {con_data['total_elapsed']:.1f}s")

                    cited_pages = con_data.get("cited_pages", [])
                    page_sources = con_data.get("page_sources", {})
                    if cited_pages and page_sources:
                        st.divider()
                        st.caption("🔍 **Cited page evidence & source passages:** (expand to inspect original page text)")
                        for p_num in cited_pages:
                            if p_num in page_sources:
                                page_obj = next((p for p in pages if p.page_number == p_num), None)
                                w_count = page_obj.word_count if page_obj else len(page_sources[p_num].split())
                                with st.expander(f"📄 Citation · Page {p_num} ({w_count} words)", expanded=False):
                                    st.caption(f"Document: {st.session_state['uploaded_paper_name']} · Page {p_num}")
                                    st.text(page_sources[p_num], wrap=True)

        # Unified "Ask ResearchMate" & Grounded Chat Section
        st.divider()
        st.subheader("🧠 Ask Research AI")
        st.caption(
            "Ask a question about this paper, request a full summary or key concepts, or inquire about viva and presentations. "
            "Research AI automatically detects your intent and routes to the right feature."
        )

        with st.form("paper_qa_form", clear_on_submit=True):
            user_question = st.text_input(
                "Ask a question or request an action",
                placeholder="e.g. 'What dataset was used?', 'Summarize this paper', 'Extract key concepts', 'Can we practice viva?'",
                key="qa_question_input",
            )
            col_submit, col_status = st.columns([1, 3], vertical_alignment="center")
            with col_submit:
                submit_qa = st.form_submit_button("Ask Research AI 🔬", type="primary", icon=":material/send:")
            with col_status:
                if is_paper_fully_indexed(
                    st.session_state["uploaded_paper_name"],
                    pages=st.session_state["extracted_pages"],
                ):
                    st.caption("⚡ ChromaDB Vector Index: Active (fully indexed)")
                else:
                    st.caption("ChromaDB Index: Ready (indexes on demand)")

        if submit_qa:
            if not user_question.strip():
                st.warning("Please type a question or request before submitting.", icon=":material/warning:")
            elif not settings.gemini_api_key or settings.gemini_api_key.strip() in ("", "your_gemini_api_key_here"):
                st.error(
                    "AI chat is unavailable until the Gemini service is configured.",
                    icon=":material/key:",
                )
            else:
                with st.status("Analyzing request & routing...", expanded=True) as status_box:
                    def progress_listener(stage: str, msg: str, elapsed: float, extra: dict = None):
                        status_box.write(f"⏱️ **[{elapsed:.1f}s]** {msg}")

                    try:
                        routed_result = execute_routed_request(
                            user_input=user_question.strip(),
                            filename=st.session_state["uploaded_paper_name"],
                            pages=st.session_state["extracted_pages"],
                            on_progress=progress_listener,
                            existing_summary_data=st.session_state.get("paper_summary_data"),
                            existing_concepts_data=st.session_state.get("paper_concepts_data"),
                            existing_presentation_data=st.session_state.get("presentation_data"),
                        )
                        total_time = routed_result.get("total_elapsed", 0.0)
                        route_label = routed_result.get("route_label", "Grounded Paper Chat")
                        status_box.update(
                            label=f"Routed to {route_label} in {total_time:.1f}s",
                            state="complete",
                            expanded=False,
                        )

                        # Sync fresh summary/concepts/presentation back to session state
                        if routed_result.get("updated_summary_data"):
                            st.session_state["paper_summary_data"] = routed_result["updated_summary_data"]
                        if routed_result.get("updated_concepts_data"):
                            st.session_state["paper_concepts_data"] = routed_result["updated_concepts_data"]
                        if routed_result.get("updated_presentation_data"):
                            st.session_state["presentation_data"] = routed_result["updated_presentation_data"]

                        st.session_state["chat_history"].append(
                            {
                                "question": user_question.strip(),
                                "answer": routed_result["answer"],
                                "intent": routed_result["intent"],
                                "route_label": route_label,
                                "sources": routed_result.get("sources", []),
                                "cited_pages": routed_result.get("cited_pages", []),
                                "page_sources": routed_result.get("page_sources", {}),
                                "elapsed": total_time,
                            }
                        )
                    except (MissingAPIKeyError, EmbeddingError, RetrievalError, GenerationError, RAGError) as exc:
                        status_box.update(label="Request failed", state="error", expanded=True)
                        actionable_msg = format_actionable_error(exc)
                        st.error(actionable_msg, icon=":material/error:")
                    except Exception as exc:
                        status_box.update(label="Unexpected error", state="error", expanded=True)
                        actionable_msg = format_actionable_error(exc)
                        st.error(f"An error occurred: {actionable_msg}", icon=":material/error:")

        # Display Chat History if any
        if st.session_state.get("chat_history"):
            st.markdown("#### Conversation history")
            for idx, item in enumerate(reversed(st.session_state["chat_history"])):
                with st.container(border=True):
                    col_q, col_route = st.columns([3, 1], vertical_alignment="center")
                    with col_q:
                        st.markdown(f"**Request:** {item['question']}")
                    with col_route:
                        route_lbl = item.get("route_label", "Grounded Paper Chat")
                        st.caption(f":material/alt_route: **Routed to:** {route_lbl}")

                    st.markdown(f"**Response:**\n\n{item['answer']}")
                    if item.get("elapsed"):
                        st.caption(f"⚡ Handled in {item['elapsed']:.1f}s · {item.get('route_label', 'Grounded Paper Chat')}")

                    # Chunk sources (for paper_question)
                    sources = item.get("sources", [])
                    if sources:
                        st.caption("🔍 **Retrieved page evidence:** (expand to inspect original passage)")
                        for s_i, src in enumerate(sources, 1):
                            p_num = src.metadata.get("page", "?")
                            c_idx = src.metadata.get("chunk_index", 0)
                            with st.expander(f"📄 Citation {s_i} · Page {p_num} (Chunk #{c_idx})", expanded=False):
                                st.caption(f"Document: {src.metadata.get('filename', 'Paper')} · Page {p_num}")
                                st.text(src.page_content, wrap=True)

                    # Full-paper page citations (for summary and key_concepts)
                    cited_pages = item.get("cited_pages", [])
                    page_sources = item.get("page_sources", {})
                    if cited_pages and page_sources:
                        st.caption("🔍 **Cited page evidence & source passages:** (expand to inspect original page text)")
                        for p_num in cited_pages:
                            if p_num in page_sources:
                                page_obj = next((p for p in pages if p.page_number == p_num), None) if pages else None
                                w_count = page_obj.word_count if page_obj else len(page_sources[p_num].split())
                                with st.expander(f"📄 Citation · Page {p_num} ({w_count} words)", expanded=False):
                                    st.caption(f"Document: {st.session_state.get('uploaded_paper_name', 'Paper')} · Page {p_num}")
                                    st.text(page_sources[p_num], wrap=True)

                    # Quick download button if routed to presentation
                    if item.get("intent") == "presentation" and st.session_state.get("presentation_data"):
                        clean_f = st.session_state.get("uploaded_paper_name", "paper").replace(".pdf", "").replace(" ", "_")
                        st.download_button(
                            label="Download PowerPoint (.pptx)",
                            data=st.session_state["presentation_data"]["pptx_bytes"],
                            file_name=f"{clean_f}_presentation.pptx",
                            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                            type="primary",
                            icon=":material/download:",
                            key=f"dl_pptx_chat_{idx}",
                        )

            if st.button("Clear conversation history", key="clear_chat_history_btn"):
                st.session_state["chat_history"] = []
                st.rerun()

    else:
        st.divider()
        st.subheader("Paper analysis")
        st.info("Upload a research paper PDF above to enable full-paper summary and key concepts extraction.", icon=":material/info:")

        st.divider()
        st.subheader("🧠 Ask Research AI")
        st.text_input(
            "Ask a question or request an action",
            placeholder="e.g. 'What dataset was used?', 'Summarize this paper', 'Extract key concepts'",
            disabled=True,
        )
        st.caption("Upload a research paper above to enable intent-routed assistance.")

with viva:
    st.subheader("🎓 Interactive Viva Simulator")
    st.caption(f"Practice a paper-specific oral defense with up to {VIVA_QUESTION_LIMIT} questions. Get evidence-grounded feedback after each answer. · AGENTIC-AI")

    if not st.session_state.get("extracted_pages"):
        st.info("Upload a research paper in the Paper chat tab to start a viva session.", icon=":material/upload_file:")
    elif not settings.gemini_api_key:
        st.warning("Viva practice is unavailable until the Gemini service is configured.", icon=":material/cloud:")
    else:
        viva_session = st.session_state.get("viva_session")
        start_label = "Start viva practice" if not viva_session else "Start a new session"
        if st.button(start_label, type="primary", icon=":material/play_arrow:", key="btn_start_viva"):
            try:
                with st.spinner("Preparing a question from your paper…"):
                    first_question = start_viva(
                        st.session_state["extracted_pages"],
                        st.session_state["uploaded_paper_name"],
                    )
                st.session_state["viva_session"] = {
                    "turns": [],
                    "current_question": first_question["question"],
                    "current_focus": first_question["focus"],
                    "current_citation": first_question["citation"],
                    "total_score": 0,
                }
                st.rerun()
            except Exception as exc:
                st.error(f"Could not start the viva session: {format_actionable_error(exc)}", icon=":material/error:")

        viva_session = st.session_state.get("viva_session")
        if viva_session:
            turns = viva_session["turns"]
            answered = len(turns)
            average_score = viva_session["total_score"] / answered if answered else 0
            metric1, metric2, metric3 = st.columns(3)
            metric1.metric("Questions answered", f"{answered} / {VIVA_QUESTION_LIMIT}")
            metric2.metric("Average score", f"{average_score:.1f} / 5" if answered else "—")
            metric3.metric("Paper", st.session_state.get("uploaded_paper_name", "Uploaded paper"))
            if answered:
                st.progress(min(1.0, average_score / 5), text="Session performance")

            if answered >= VIVA_QUESTION_LIMIT:
                st.success(f"Viva session complete — you answered all {VIVA_QUESTION_LIMIT} questions.", icon=":material/celebration:")
                st.markdown(f"**Final average score:** {average_score:.1f} / 5")
                if not viva_session.get("history_saved"):
                    try:
                        save_completed_viva(st.session_state.get("uploaded_paper_name", "Research paper"), turns)
                        viva_session["history_saved"] = True
                    except Exception:
                        viva_session["history_saved"] = True
                        viva_session["history_save_failed"] = True
                if viva_session.get("history_save_failed"):
                    st.warning("This session is complete, but its score summary could not be saved to the dashboard.")
                elif viva_session.get("history_saved"):
                    st.caption("Session score and topic results saved to your local dashboard. Your answers are not stored there.")
            else:
                st.markdown(f"#### Question {answered + 1} · {viva_session.get('current_focus', 'Viva question')}")
                st.info(viva_session["current_question"], icon=":material/help:")
                if viva_session.get("current_citation"):
                    st.caption(f"Paper evidence: {viva_session['current_citation']}")

                answer = st.text_area(
                    "Your answer",
                    key=f"viva_answer_{answered}",
                    placeholder="Explain your answer as if you were speaking to your examiner…",
                    height=150,
                )
                if st.button("Submit answer", type="primary", icon=":material/send:", key=f"btn_submit_viva_{answered}", disabled=not answer.strip()):
                    try:
                        with st.spinner("Reviewing your answer against the paper…"):
                            evaluation = evaluate_viva_answer(
                                st.session_state["extracted_pages"],
                                st.session_state["uploaded_paper_name"],
                                viva_session["current_question"],
                                answer,
                                turns,
                            )
                        turns.append({
                            "question": viva_session["current_question"],
                            "focus": viva_session.get("current_focus", "Viva"),
                            "answer": answer.strip(),
                            **evaluation,
                        })
                        viva_session["total_score"] += evaluation["score"]
                        if len(turns) < VIVA_QUESTION_LIMIT:
                            viva_session["current_question"] = evaluation["next_question"]
                            viva_session["current_focus"] = evaluation["next_focus"]
                            viva_session["current_citation"] = evaluation["next_citation"]
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not evaluate the answer: {format_actionable_error(exc)}", icon=":material/error:")

            if turns:
                st.markdown("#### Feedback so far")
                for turn_num, turn in enumerate(turns, start=1):
                    with st.expander(f"Question {turn_num} · Score {turn['score']} / 5", expanded=(turn_num == answered)):
                        st.markdown(f"**Your answer:** {turn['answer']}")
                        st.markdown(f"**What you did well:** {turn['strengths']}")
                        st.markdown(f"**What to strengthen:** {turn['improve']}")
                        st.markdown(f"**Examiner feedback:** {turn['feedback']}")
                        if turn.get("citation"):
                            st.caption(f"Paper evidence: {turn['citation']}")

with slides:
    # 1. PRESENTATION MODE: Focused, large, one-slide-at-a-time view
    if st.session_state.get("presenter_mode") and st.session_state.get("presentation_data"):
        # Immersive presenter view: let the current slide use the full app viewport.
        st.html("""<div id="rm-presenter-mode"></div>
        <style>
        body:has(#rm-presenter-mode) [data-testid="stSidebar"],
        body:has(#rm-presenter-mode) header[data-testid="stHeader"],
        body:has(#rm-presenter-mode) .rm-top-bar,
        body:has(#rm-presenter-mode) .rm-hero,
        body:has(#rm-presenter-mode) [data-testid="stTabsHeader"] { display: none !important; }
        body:has(#rm-presenter-mode) .block-container {
            max-width: none !important; width: 100% !important;
            padding: 0.65rem 1.25rem 0.5rem !important;
        }
        body:has(#rm-presenter-mode) [data-testid="stAppViewContainer"] { overflow: hidden; }
        </style>""")
        pres_data = st.session_state["presentation_data"]
        slides_list = pres_data["slides"]
        total_slides = len(slides_list)
        current_idx = max(
            0, min(st.session_state.get("current_slide_idx", 0), total_slides - 1)
        )
        st.session_state["current_slide_idx"] = current_idx
        current_slide = slides_list[current_idx]
        theme_name = pres_data.get("theme_name", "Cinematic Teal (ResearchMate Dark)")
        duration = pres_data.get("duration", "10 minutes")
        audience_level = pres_data.get("audience_level", "General academic")

        # Top Control Bar in Presentation Mode
        col_exit, col_prev, col_indicator, col_next, col_jump = st.columns(
            [1.4, 0.9, 2.2, 0.9, 2.6], vertical_alignment="center"
        )
        with col_exit:
            if st.button(
                "Exit presentation",
                icon=":material/close:",
                width="stretch",
                key="pres_mode_exit_btn",
            ):
                st.session_state["presenter_mode"] = False
                st.rerun()

        with col_prev:
            if st.button(
                "Previous",
                icon=":material/arrow_back:",
                disabled=(current_idx == 0),
                width="stretch",
                key="pres_mode_prev_btn",
            ):
                st.session_state["current_slide_idx"] = max(0, current_idx - 1)
                st.rerun()

        with col_indicator:
            cat_label = html.escape(str(current_slide.get("category", "")).upper())
            st.markdown(
                f"<div style='text-align:center; font-weight:700; font-size:1.05rem; color:#38d9d4;'>"
                f"Slide {current_idx + 1} of {total_slides} &nbsp;·&nbsp; "
                f"<span style='color:#fbbf24; font-size:0.85rem; letter-spacing:0.04em;'>{cat_label}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

        with col_next:
            if st.button(
                "Next",
                icon=":material/arrow_forward:",
                disabled=(current_idx >= total_slides - 1),
                type="primary",
                width="stretch",
                key="pres_mode_next_btn",
            ):
                st.session_state["current_slide_idx"] = min(total_slides - 1, current_idx + 1)
                st.rerun()

        with col_jump:
            slide_options = [
                f"{s['slide_number']}. [{s['category']}] {s['title'][:22]}..."
                if len(s["title"]) > 22
                else f"{s['slide_number']}. [{s['category']}] {s['title']}"
                for s in slides_list
            ]
            chosen_jump = st.selectbox(
                "Jump to slide",
                options=list(range(total_slides)),
                format_func=lambda i: slide_options[i],
                index=current_idx,
                label_visibility="collapsed",
                key=f"pres_mode_jump_select_{current_idx}",
            )
            if chosen_jump != current_idx:
                st.session_state["current_slide_idx"] = chosen_jump
                st.rerun()

        # Render Large Presentation Slide Canvas
        st.html(
            render_slide_html(
                slide_info=current_slide,
                theme_name=theme_name,
                total_slides=total_slides,
                duration=duration,
                audience_level=audience_level,
                is_presentation_mode=True,
            )
        )

        # Presenter Notes & Talking Points Drawer
        if current_slide.get("speaker_notes") or current_slide.get("citation"):
            with st.expander("🎙️ Presenter notes & talking points", expanded=True):
                if current_slide.get("speaker_notes"):
                    st.write(current_slide["speaker_notes"])
                if current_slide.get("citation"):
                    st.caption(f"📄 Grounded citation: {current_slide['citation']}")

    else:
        # 2. NORMAL VIEW: Slide generator settings and visual slide preview
        st.subheader("Paper-to-PowerPoint generator")
        st.caption(
            "Generate a paper-grounded, widescreen (16:9) slide deck with verifiable page citations on factual slides, "
            "presenter speaker notes, and customizable academic themes."
        )

        if not st.session_state.get("extracted_pages"):
            st.info(
                "Please upload a research paper PDF in the Paper chat tab first to enable presentation generation.",
                icon=":material/upload_file:",
            )
            with st.container(border=True):
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.slider("Number of slides", 5, 15, 8, disabled=True)
                    st.selectbox(
                        "Presentation duration",
                        ["5 minutes", "10 minutes", "15 minutes", "20 minutes"],
                        disabled=True,
                    )
                with col_d2:
                    st.selectbox(
                        "Audience / Technical level",
                        ["General academic", "Specialist / Viva", "Executive"],
                        disabled=True,
                    )
                    st.selectbox("Visual theme", list(THEMES.keys()), disabled=True)
                st.button("Generate PowerPoint", disabled=True, icon=":material/slideshow:")
        else:
            pages = st.session_state["extracted_pages"]
            filename = st.session_state["uploaded_paper_name"]

            with st.container(border=True):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    slide_count = st.slider(
                        "Number of slides",
                        min_value=5,
                        max_value=15,
                        value=8,
                        help="Target slide count for your presentation deck.",
                        key="pres_slide_count",
                    )
                    duration = st.selectbox(
                        "Presentation duration",
                        options=[
                            "5 minutes (Lightning talk)",
                            "10 minutes (Standard conference)",
                            "15 minutes (Deep-dive seminar)",
                            "20 minutes (Thesis / Viva defense)",
                        ],
                        index=1,
                        key="pres_duration",
                    )
                with col_c2:
                    audience_level = st.selectbox(
                        "Audience / Technical level",
                        options=[
                            "General academic (undergrad / interdisciplinary)",
                            "Specialist / Peer review (faculty, examiners, viva)",
                            "Executive / High-level (industry, overview)",
                        ],
                        index=0,
                        key="pres_audience",
                    )
                    theme_name = st.selectbox(
                        "Visual theme",
                        options=list(THEMES.keys()),
                        index=0,
                        key="pres_theme",
                    )

                col_btn, col_status = st.columns([1, 2], vertical_alignment="center")
                with col_btn:
                    btn_gen_presentation = st.button(
                        "Generate PowerPoint"
                        if not st.session_state.get("presentation_data")
                        else "Regenerate PowerPoint",
                        type="primary",
                        icon=":material/slideshow:",
                        key="btn_generate_presentation",
                    )
                with col_status:
                    if st.session_state.get("presentation_data"):
                        pres = st.session_state["presentation_data"]
                        st.caption(
                            f"⚡ Deck ready: {pres['slide_count']} slides generated in {pres['total_elapsed']:.1f}s ({len(pres['pptx_bytes']):,} bytes)"
                        )

            if btn_gen_presentation:
                if not settings.gemini_api_key or settings.gemini_api_key.strip() in (
                    "",
                    "your_gemini_api_key_here",
                ):
                    st.error(
                        "Presentation AI is unavailable until the Gemini service is configured.",
                        icon=":material/key:",
                    )
                else:
                    with st.status(
                        "Generating presentation deck...", expanded=True
                    ) as status_box:

                        def pres_progress_listener(
                            stage: str, msg: str, elapsed: float, extra: dict = None
                        ):
                            status_box.write(f"⏱️ **[{elapsed:.1f}s]** {msg}")

                        try:
                            pres_data = generate_presentation(
                                filename=filename,
                                pages=pages,
                                slide_count=slide_count,
                                duration=duration,
                                audience_level=audience_level,
                                theme_name=theme_name,
                                on_progress=pres_progress_listener,
                            )
                            status_box.update(
                                label=f"Deck generated in {pres_data['total_elapsed']:.1f}s ({pres_data['slide_count']} slides)",
                                state="complete",
                                expanded=False,
                            )
                            st.session_state["presentation_data"] = pres_data
                            st.session_state["current_slide_idx"] = 0
                            st.session_state["presenter_mode"] = False
                            st.rerun()
                        except (
                            MissingAPIKeyError,
                            GenerationError,
                            PresentationError,
                            RAGError,
                        ) as exc:
                            status_box.update(
                                label="Presentation generation failed",
                                state="error",
                                expanded=True,
                            )
                            actionable_msg = format_actionable_error(exc)
                            st.error(actionable_msg, icon=":material/error:")
                        except Exception as exc:
                            status_box.update(
                                label="Unexpected error", state="error", expanded=True
                            )
                            actionable_msg = format_actionable_error(exc)
                            st.error(
                                f"An error occurred: {actionable_msg}",
                                icon=":material/error:",
                            )

            if st.session_state.get("presentation_data"):
                pres_data = st.session_state["presentation_data"]
                clean_filename = filename.replace(".pdf", "").replace(" ", "_")
                slides_list = pres_data["slides"]
                total_slides = len(slides_list)
                current_idx = max(
                    0, min(st.session_state.get("current_slide_idx", 0), total_slides - 1)
                )
                st.session_state["current_slide_idx"] = current_idx
                current_slide = slides_list[current_idx]
                theme_name = pres_data.get("theme_name", "Cinematic Teal (ResearchMate Dark)")
                duration = pres_data.get("duration", "10 minutes")
                audience = pres_data.get("audience_level", "General academic")

                st.divider()

                # Action Bar: Present slides & Download PPTX
                col_present_btn, col_download_btn = st.columns(2, vertical_alignment="center")
                with col_present_btn:
                    if st.button(
                        "Present slides",
                        type="primary",
                        icon=":material/play_circle:",
                        width="stretch",
                        key="btn_start_presentation",
                    ):
                        st.session_state["presenter_mode"] = True
                        st.rerun()

                with col_download_btn:
                    st.download_button(
                        label="Download PowerPoint (.pptx)",
                        data=pres_data["pptx_bytes"],
                        file_name=f"{clean_filename}_presentation.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        icon=":material/download:",
                        width="stretch",
                        key="download_pptx_file_btn",
                    )

                st.caption(
                    f"**Theme:** {theme_name} · **Slides:** {total_slides} · "
                    f"**Format:** Widescreen 16:9 (.pptx) with verified page citations and speaker notes"
                )

                st.divider()

                # 3. Slide Preview: MAIN CONTENT OF PRESENTATION TAB
                st.markdown("#### 🖥️ Slide preview")
                st.caption(
                    "Inspect the generated slides below, or click **Present slides** above for an immersive full-window view:"
                )

                # Slide Navigator Bar
                col_p_prev, col_p_indicator, col_p_next, col_p_jump = st.columns(
                    [1.0, 2.2, 1.0, 2.8], vertical_alignment="center"
                )
                with col_p_prev:
                    if st.button(
                        "Previous slide",
                        icon=":material/arrow_back:",
                        disabled=(current_idx == 0),
                        width="stretch",
                        key="btn_preview_prev",
                    ):
                        st.session_state["current_slide_idx"] = max(0, current_idx - 1)
                        st.rerun()

                with col_p_indicator:
                    cat_label = html.escape(str(current_slide.get("category", "")).upper())
                    st.markdown(
                        f"<div style='text-align:center; font-weight:700; font-size:1rem; color:#38d9d4;'>"
                        f"Slide {current_idx + 1} of {total_slides} &nbsp;·&nbsp; "
                        f"<span style='color:#fbbf24; font-size:0.85rem; letter-spacing:0.04em;'>{cat_label}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                with col_p_next:
                    if st.button(
                        "Next slide",
                        icon=":material/arrow_forward:",
                        disabled=(current_idx >= total_slides - 1),
                        width="stretch",
                        key="btn_preview_next",
                    ):
                        st.session_state["current_slide_idx"] = min(total_slides - 1, current_idx + 1)
                        st.rerun()

                with col_p_jump:
                    slide_options = [
                        f"{s['slide_number']}. [{s['category']}] {s['title'][:22]}..."
                        if len(s["title"]) > 22
                        else f"{s['slide_number']}. [{s['category']}] {s['title']}"
                        for s in slides_list
                    ]
                    chosen_preview_idx = st.selectbox(
                        "Select slide to preview",
                        options=list(range(total_slides)),
                        format_func=lambda i: slide_options[i],
                        index=current_idx,
                        label_visibility="collapsed",
                        key=f"preview_jump_select_{current_idx}",
                    )
                    if chosen_preview_idx != current_idx:
                        st.session_state["current_slide_idx"] = chosen_preview_idx
                        st.rerun()

                # Live Slide Preview Canvas
                preview_html = render_slide_html(
                    slide_info=current_slide,
                    theme_name=theme_name,
                    total_slides=total_slides,
                    duration=duration,
                    audience_level=audience,
                    is_presentation_mode=False,
                )
                st.html(preview_html)

                # Active Slide Notes & Citation Info
                if current_slide.get("speaker_notes") or current_slide.get("citation"):
                    col_n1, col_n2 = st.columns([2, 1])
                    with col_n1:
                        if current_slide.get("speaker_notes"):
                            st.caption(f"🎙️ **Presenter notes:** {current_slide['speaker_notes']}")
                    with col_n2:
                        if current_slide.get("citation"):
                            st.info(
                                f"📄 **Grounded evidence:** {current_slide['citation']}",
                                icon=":material/menu_book:",
                            )

                # Collapsible Full Deck Outline
                with st.expander("📑 View full slide deck text outline", expanded=False):
                    for s in slides_list:
                        s_num = s["slide_number"]
                        s_title = s["title"]
                        s_cat = s["category"]
                        s_cite = s.get("citation", "")
                        cite_badge = f" · {s_cite}" if s_cite else ""
                        st.markdown(f"**Slide {s_num}: [{s_cat}] {s_title}{cite_badge}**")
                        if s.get("author"):
                            st.caption(f"👤 Author(s): {s['author']}")
                        if s.get("subtitle"):
                            st.caption(f"Subtitle: {s['subtitle']}")
                        for b in s.get("bullet_points", []):
                            st.markdown(f"- {b}")
                        if s.get("chart_data"):
                            cd = s["chart_data"]
                            st.caption(
                                f"📊 Chart: {cd.get('title')} ({', '.join(cd.get('categories', []))})"
                            )
                        if s.get("speaker_notes"):
                            st.caption(f"🎙️ Notes: {s['speaker_notes']}")
                        st.divider()

with flashcards:
    st.subheader("Paper flashcards")
    st.caption("Review key ideas with question-and-answer cards grounded in your paper, with page references on the answer side.")

    if not st.session_state.get("extracted_pages"):
        st.info("Upload a research paper in the Paper chat tab to create flashcards.", icon=":material/upload_file:")
    elif not settings.gemini_api_key:
        st.warning("Flashcard AI is unavailable until the Gemini service is configured.", icon=":material/cloud:")
    else:
        deck = st.session_state.get("flashcard_deck")
        if not deck:
            if st.button("Generate 10 flashcards", type="primary", icon=":material/auto_awesome:", key="btn_generate_flashcards"):
                try:
                    with st.spinner("Creating paper-grounded flashcards…"):
                        deck = generate_flashcards(
                            st.session_state["extracted_pages"],
                            st.session_state["uploaded_paper_name"],
                            count=10,
                        )
                    st.session_state["flashcard_deck"] = deck
                    st.session_state["flashcard_index"] = 0
                    st.session_state["flashcard_revealed"] = False
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not generate flashcards: {format_actionable_error(exc)}", icon=":material/error:")
        else:
            total_cards = len(deck)
            index = max(0, min(st.session_state.get("flashcard_index", 0), total_cards - 1))
            st.session_state["flashcard_index"] = index
            card = deck[index]
            st.progress((index + 1) / total_cards, text=f"Card {index + 1} of {total_cards}")

            with st.container(border=True):
                if st.session_state.get("flashcard_revealed"):
                    st.caption("ANSWER")
                    st.markdown(f"### {card['answer']}")
                    if card.get("citation"):
                        st.caption(f"Paper evidence: {card['citation']}")
                else:
                    st.caption("QUESTION")
                    st.markdown(f"### {card['question']}")
                    st.caption("Think of your answer, then reveal the card.")

            prev_col, flip_col, next_col, shuffle_col = st.columns([1, 1.3, 1, 1.2], vertical_alignment="center")
            with prev_col:
                if st.button("Previous", icon=":material/arrow_back:", disabled=(index == 0), width="stretch", key="flashcard_previous"):
                    st.session_state["flashcard_index"] = index - 1
                    st.session_state["flashcard_revealed"] = False
                    st.rerun()
            with flip_col:
                label = "Show question" if st.session_state.get("flashcard_revealed") else "Reveal answer"
                if st.button(label, type="primary", icon=":material/flip:", width="stretch", key="flashcard_flip"):
                    st.session_state["flashcard_revealed"] = not st.session_state.get("flashcard_revealed", False)
                    st.rerun()
            with next_col:
                if st.button("Next", icon=":material/arrow_forward:", disabled=(index >= total_cards - 1), width="stretch", key="flashcard_next"):
                    st.session_state["flashcard_index"] = index + 1
                    st.session_state["flashcard_revealed"] = False
                    st.rerun()
            with shuffle_col:
                if st.button("Shuffle", icon=":material/shuffle:", width="stretch", key="flashcard_shuffle"):
                    random.shuffle(deck)
                    st.session_state["flashcard_index"] = 0
                    st.session_state["flashcard_revealed"] = False
                    st.rerun()

            if st.button("Generate a fresh set", key="btn_regenerate_flashcards"):
                st.session_state["flashcard_deck"] = None
                st.session_state["flashcard_index"] = 0
                st.session_state["flashcard_revealed"] = False
                st.rerun()

with dashboard:
    st.subheader("Learning dashboard")
    st.caption("A private local view of completed viva sessions, overall scores, and topics to review. Individual answers are not stored.")
    try:
        history = load_viva_history()
    except Exception as exc:
        history = []
        st.error(f"Could not load the local score history: {format_actionable_error(exc)}")

    if not history:
        if st.session_state.get("viva_session") and st.session_state["viva_session"].get("turns"):
            st.info("Your current viva is in progress. Complete all six questions to add its score summary here.", icon=":material/insights:")
        else:
            st.info("Complete a six-question viva session to see your score history and topic strengths here.", icon=":material/insights:")
    else:
        total_sessions = len(history)
        overall_average = sum(item["average_score"] for item in history) / total_sessions
        total_answers = sum(item["question_count"] for item in history)
        best_score = max(item["average_score"] for item in history)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Completed sessions", total_sessions)
        m2.metric("Average score", f"{overall_average:.1f} / 5")
        m3.metric("Best session", f"{best_score:.1f} / 5")
        m4.metric("Answers reviewed", total_answers)

        import pandas as pd
        import plotly.express as px
        from collections import defaultdict

        topic_values = defaultdict(list)
        for item in history:
            for topic, score in item["topic_scores"].items():
                topic_values[topic].append(score)
        topic_frame = pd.DataFrame([
            {"Topic": topic, "Average score": sum(scores) / len(scores), "Sessions": len(scores)}
            for topic, scores in topic_values.items()
        ]).sort_values("Average score", ascending=True)

        if not topic_frame.empty:
            st.markdown("#### Topic performance")
            fig = px.bar(
                topic_frame,
                x="Average score",
                y="Topic",
                orientation="h",
                range_x=[0, 5],
                color="Average score",
                color_continuous_scale=[[0, "#f59e0b"], [0.6, "#38d9d6"], [1, "#22c55e"]],
                hover_data={"Sessions": True, "Average score": ":.1f"},
            )
            fig.update_layout(
                template="plotly_dark",
                height=max(300, 48 * len(topic_frame)),
                margin=dict(l=8, r=8, t=12, b=12),
                coloraxis_showscale=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Average viva score (out of 5)",
                yaxis_title="",
            )
            st.plotly_chart(fig, width="stretch")
            strong_topics = topic_frame[topic_frame["Average score"] >= 4.0]["Topic"].tolist()
            review_topics = topic_frame[topic_frame["Average score"] < 3.0]["Topic"].tolist()
            strengths, revision = st.columns(2)
            with strengths:
                st.markdown("**Current strengths**")
                st.write(", ".join(strong_topics) if strong_topics else "Keep practicing to build consistent strengths.")
            with revision:
                st.markdown("**Suggested revision areas**")
                st.write(", ".join(review_topics) if review_topics else "No topic is below 3 / 5 in the saved sessions.")

        st.markdown("#### Recent sessions")
        recent = pd.DataFrame([
            {
                "Paper": item["paper_name"],
                "Completed": item["completed_at"].replace("T", " "),
                "Questions": item["question_count"],
                "Average": f"{item['average_score']:.1f} / 5",
            }
            for item in history[:10]
        ])
        st.dataframe(recent, hide_index=True, width="stretch")

# Bottom academic footer with framing corner stars
st.html(
    """
    <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(56,217,214,0.16); padding-top:1.5rem; margin-top:3rem; font-family:ui-monospace,monospace; font-size:0.75rem; color:#64748b;">
      <span class="rm-corner-star">✦</span>
      <span style="letter-spacing:0.08em;">RESEARCHMATE AI · EMPOWERING RESEARCH DEFENSE</span>
      <span class="rm-corner-star">✦</span>
    </div>
    """
)
