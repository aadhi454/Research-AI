"""Modern, professional SaaS UI/UX styling for Research AI — Agentic AI.

Inspired by Perplexity AI, Linear, Notion, and modern AI development platforms.
Features:
- Clean obsidian & slate dark theme with subtle border hierarchy.
- Refined typography and consistent spacing.
- Agent workflow status badges with live indicators.
- Perplexity-style citation pills, interactive chips, and polished cards.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ====================================================================
   GLOBAL MODERN SAAS THEME (Perplexity / Linear / Notion inspired)
   ==================================================================== */

:root {
    --bg-main: #090d16;
    --bg-surface: #111827;
    --bg-card: rgba(17, 24, 39, 0.75);
    --bg-glass: rgba(15, 23, 42, 0.65);
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-highlight: rgba(59, 130, 246, 0.3);
    --primary: #3b82f6;
    --primary-glow: rgba(59, 130, 246, 0.15);
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --accent-emerald: #10b981;
    --accent-indigo: #6366f1;
    --accent-amber: #f59e0b;
}

html, body, [class*="st-"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

code, pre, .stCodeBlock {
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, monospace !important;
}

.stApp {
    background-color: var(--bg-main) !important;
    background-image: 
        radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.08) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(99, 102, 241, 0.06) 0px, transparent 50%),
        radial-gradient(at 50% 100%, rgba(16, 185, 129, 0.04) 0px, transparent 50%) !important;
    background-attachment: fixed !important;
    color: var(--text-primary) !important;
}

/* App block container */
.block-container {
    max-width: 1200px !important;
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
}

/* Header & Typography */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

p, span, label {
    color: var(--text-secondary);
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #0b101b !important;
    border-right: 1px solid var(--border-subtle) !important;
}

section[data-testid="stSidebar"] div.block-container {
    padding-top: 1.5rem !important;
}

/* Modern Card containers */
div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"][border="true"],
.stCard {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"][border="true"]:hover {
    border-color: var(--border-highlight) !important;
}

/* Tabs styling */
div[data-testid="stTabs"] {
    border-top: 1px solid var(--border-subtle) !important;
    padding-top: 0.5rem !important;
}

button[data-testid="stTab"] {
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.15s ease-in-out !important;
}

button[data-testid="stTab"]:hover {
    color: var(--text-primary) !important;
    background: rgba(255, 255, 255, 0.04) !important;
}

button[data-testid="stTab"][aria-selected="true"] {
    color: var(--primary) !important;
    font-weight: 600 !important;
    border-bottom: 2px solid var(--primary) !important;
}

/* Buttons */
button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #3b82f6) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.35) !important;
    transition: all 0.18s ease-in-out !important;
}

button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1d4ed8, #2563eb) !important;
    box-shadow: 0 6px 20px 0 rgba(37, 99, 235, 0.45) !important;
    transform: translateY(-1px) !important;
}

button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}

button[kind="secondary"]:hover {
    background: rgba(255, 255, 255, 0.09) !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
}

/* Inputs & Textareas */
input, textarea, .stSelectbox > div > div {
    background-color: #0d1322 !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
}

input:focus, textarea:focus, .stSelectbox > div > div:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 2px var(--primary-glow) !important;
}

/* Metrics */
div[data-testid="stMetric"] {
    background: rgba(17, 24, 39, 0.6) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    padding: 0.85rem 1.1rem !important;
    backdrop-filter: blur(8px) !important;
}

div[data-testid="stMetricLabel"] {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
}

div[data-testid="stMetricValue"] {
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
}

/* Status box & expanders */
div[data-testid="stStatusWidget"] {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
}

div[data-testid="stExpander"] {
    background: rgba(17, 24, 39, 0.5) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
}

/* Perplexity-style badge pills */
.rp-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.25rem 0.65rem;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.03em;
    background: rgba(59, 130, 246, 0.12);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.24);
}

.rp-badge-green {
    background: rgba(16, 185, 129, 0.12);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.24);
}

.rp-badge-amber {
    background: rgba(245, 158, 11, 0.12);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.24);
}

/* Live Agent Pulse Dot */
.rp-pulse-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #10b981;
    display: inline-block;
    box-shadow: 0 0 8px #10b981;
    animation: rp-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes rp-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.45; transform: scale(0.9); }
}

/* Citations Pill */
.rp-citation-pill {
    display: inline-flex;
    align-items: center;
    background: rgba(59, 130, 246, 0.14);
    color: #93c5fd;
    border: 1px solid rgba(59, 130, 246, 0.3);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.15rem 0.5rem;
    border-radius: 6px;
    margin-right: 0.35rem;
}
</style>
"""


def get_header_html() -> str:
    """Generate modern, minimal SaaS top navigation header."""
    return """
    <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:1rem;
    margin: 0.2rem 0 1.2rem; padding: 0.75rem 1.25rem; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(12px);">
      <div style="display:flex; align-items:center; gap:0.75rem;">
        <div style="width:34px; height:34px; border-radius:8px; background:linear-gradient(135deg, #2563eb, #6366f1);
        display:flex; align-items:center; justify-content:center; font-size:1.1rem; box-shadow:0 2px 10px rgba(37,99,235,0.3);">
          🔬
        </div>
        <div>
          <div style="font-size:1.05rem; font-weight:750; color:#f8fafc; letter-spacing:-0.01em;">
            Research AI
          </div>
          <div style="font-size:0.72rem; color:#94a3b8; font-weight:500;">
            Agentic Academic Intelligence & Research Platform
          </div>
        </div>
      </div>
      <div style="display:flex; align-items:center; gap:0.6rem; flex-wrap:wrap;">
        <span class="rp-badge rp-badge-green">
          <span class="rp-pulse-dot"></span> Multi-Agent Network Active
        </span>
        <span class="rp-badge">
          Gemini 2.0 Flash · ChromaDB RAG
        </span>
      </div>
    </div>
    """


def get_hero_html() -> str:
    """Generate Perplexity-style modern hero landing banner."""
    return """
    <div style="margin: 0.5rem 0 1.5rem; padding: 2rem 1.8rem; border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; background: linear-gradient(180deg, rgba(17, 24, 39, 0.8) 0%, rgba(13, 19, 32, 0.95) 100%);
    backdrop-filter: blur(16px); position:relative; overflow:hidden;">
      <div style="max-width: 740px;">
        <div style="display:inline-flex; align-items:center; gap:0.5rem; padding:0.25rem 0.75rem;
        background:rgba(59,130,246,0.12); border:1px solid rgba(59,130,246,0.25); border-radius:9999px;
        font-size:0.76rem; font-weight:600; color:#60a5fa; margin-bottom:0.9rem;">
          ⚡ Agentic AI Architecture for Research Discovery
        </div>
        <h1 style="font-size: 2.1rem; font-weight: 800; line-height: 1.2; color: #f8fafc; margin-bottom: 0.7rem; letter-spacing:-0.03em;">
          Deep paper synthesis, grounded vector chat & presentation intelligence
        </h1>
        <p style="font-size: 0.95rem; color: #94a3b8; line-height: 1.6; margin-bottom: 1.2rem;">
          Upload any academic paper to activate an autonomous team of specialized AI agents.
          Extract verifiable evidence, synthesize 6-section academic summaries, generate 16:9 PowerPoint decks,
          and conduct interactive oral viva defenses with page-level citations.
        </p>
      </div>
    </div>
    """


def get_workflow_cards_html() -> str:
    """Generate 5 modern, clean agent role cards for the Overview tab."""
    return """
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap:1rem; margin:1rem 0 1.5rem;">
      <div style="padding:1.1rem 1.1rem; border-radius:12px; background:rgba(17,24,39,0.7); border:1px solid rgba(255,255,255,0.08);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
          <span style="font-size:1.2rem;">📄</span>
          <span class="rp-badge">01 · INGESTION</span>
        </div>
        <div style="font-weight:700; color:#f8fafc; font-size:0.92rem; margin-bottom:0.35rem;">Ingestion Agent</div>
        <div style="font-size:0.8rem; color:#94a3b8; line-height:1.45;">
          Performs page-aware extraction using PyMuPDF, preserving 1-based coordinates and coordinate metadata.
        </div>
      </div>

      <div style="padding:1.1rem 1.1rem; border-radius:12px; background:rgba(17,24,39,0.7); border:1px solid rgba(255,255,255,0.08);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
          <span style="font-size:1.2rem;">🔍</span>
          <span class="rp-badge">02 · RETRIEVAL</span>
        </div>
        <div style="font-weight:700; color:#f8fafc; font-size:0.92rem; margin-bottom:0.35rem;">Vector RAG Agent</div>
        <div style="font-size:0.8rem; color:#94a3b8; line-height:1.45;">
          Indexes passages with Google text-embedding-004 in ChromaDB. Retrieves exact excerpts scoped strictly to active paper.
        </div>
      </div>

      <div style="padding:1.1rem 1.1rem; border-radius:12px; background:rgba(17,24,39,0.7); border:1px solid rgba(255,255,255,0.08);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
          <span style="font-size:1.2rem;">🧠</span>
          <span class="rp-badge">03 · ROUTER</span>
        </div>
        <div style="font-weight:700; color:#f8fafc; font-size:0.92rem; margin-bottom:0.35rem;">Intent Router</div>
        <div style="font-size:0.8rem; color:#94a3b8; line-height:1.45;">
          Classifies queries into QA, summaries, concepts, slides, or viva defense with deterministic fallback.
        </div>
      </div>

      <div style="padding:1.1rem 1.1rem; border-radius:12px; background:rgba(17,24,39,0.7); border:1px solid rgba(255,255,255,0.08);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
          <span style="font-size:1.2rem;">📊</span>
          <span class="rp-badge">04 · DESIGN</span>
        </div>
        <div style="font-weight:700; color:#f8fafc; font-size:0.92rem; margin-bottom:0.35rem;">Slide Architect</div>
        <div style="font-size:0.8rem; color:#94a3b8; line-height:1.45;">
          Generates structured academic 16:9 PowerPoint decks with verified page citations and speaker talking notes.
        </div>
      </div>

      <div style="padding:1.1rem 1.1rem; border-radius:12px; background:rgba(17,24,39,0.7); border:1px solid rgba(255,255,255,0.08);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
          <span style="font-size:1.2rem;">🎓</span>
          <span class="rp-badge">05 · EXAMINER</span>
        </div>
        <div style="font-weight:700; color:#f8fafc; font-size:0.92rem; margin-bottom:0.35rem;">Viva Examiner</div>
        <div style="font-size:0.8rem; color:#94a3b8; line-height:1.45;">
          Conducts 6-turn oral examination drills, scoring answer depth and tracking topic mastery over time.
        </div>
      </div>
    </div>
    """
