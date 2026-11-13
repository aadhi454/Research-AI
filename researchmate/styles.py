"""Cinematic styling and visual theme for ResearchMate AI.

Inspired by atmospheric deep blue and teal aesthetics, misty mountain silhouettes,
a warm golden path glow, thin cyan geometric guidelines, and rounded translucent panels.
"""

import urllib.parse

# 1. Generate lightweight vector background SVG with mountain contours,
#    central golden gateway flare, and thin cyan coordinate guidelines.
_BACKGROUND_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
<defs>
  <!-- Deep atmosphere radial glow -->
  <radialGradient id="rmAtmosphere" cx="50%" cy="20%" r="70%">
    <stop offset="0%" stop-color="#0a1d30" stop-opacity="0.9"/>
    <stop offset="45%" stop-color="#071322" stop-opacity="0.95"/>
    <stop offset="100%" stop-color="#040812" stop-opacity="1"/>
  </radialGradient>

  <!-- Central golden dawn glow -->
  <radialGradient id="rmGoldenSun" cx="50%" cy="30%" r="35%">
    <stop offset="0%" stop-color="#fef08a" stop-opacity="0.38"/>
    <stop offset="25%" stop-color="#f59e0b" stop-opacity="0.22"/>
    <stop offset="60%" stop-color="#0d9488" stop-opacity="0.08"/>
    <stop offset="100%" stop-color="#040812" stop-opacity="0"/>
  </radialGradient>

  <!-- Luminous central vertical path beam -->
  <linearGradient id="rmBeacon" x1="50%" y1="0%" x2="50%" y2="100%">
    <stop offset="0%" stop-color="#fffbeb" stop-opacity="0.25"/>
    <stop offset="25%" stop-color="#fde047" stop-opacity="0.2"/>
    <stop offset="45%" stop-color="#f59e0b" stop-opacity="0.12"/>
    <stop offset="75%" stop-color="#14b8a6" stop-opacity="0.05"/>
    <stop offset="100%" stop-color="#040812" stop-opacity="0"/>
  </linearGradient>

  <!-- Left mountain ridge -->
  <linearGradient id="rmLeftMountain" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#0c2236" stop-opacity="0.92"/>
    <stop offset="40%" stop-color="#081726" stop-opacity="0.95"/>
    <stop offset="100%" stop-color="#040a14" stop-opacity="0.98"/>
  </linearGradient>

  <!-- Right mountain ridge -->
  <linearGradient id="rmRightMountain" x1="100%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#0c2236" stop-opacity="0.92"/>
    <stop offset="40%" stop-color="#081726" stop-opacity="0.95"/>
    <stop offset="100%" stop-color="#040a14" stop-opacity="0.98"/>
  </linearGradient>

  <!-- Distant mist layers -->
  <linearGradient id="rmMist" x1="50%" y1="0%" x2="50%" y2="100%">
    <stop offset="0%" stop-color="#0e334a" stop-opacity="0.4"/>
    <stop offset="100%" stop-color="#05101a" stop-opacity="0.8"/>
  </linearGradient>
</defs>

<!-- Sky base -->
<rect width="1440" height="900" fill="url(#rmAtmosphere)"/>

<!-- Central golden aura & vertical beacon path -->
<ellipse cx="720" cy="280" rx="260" ry="340" fill="url(#rmGoldenSun)"/>
<path d="M 610 900 Q 660 520 680 370 Q 700 240 720 150 Q 740 240 760 370 Q 780 520 830 900 Z" fill="url(#rmBeacon)"/>

<!-- Distant misty peaks -->
<path d="M 0 320 Q 360 380 610 390 L 610 900 L 0 900 Z" fill="url(#rmMist)"/>
<path d="M 1440 320 Q 1080 380 830 390 L 830 900 L 1440 900 Z" fill="url(#rmMist)"/>

<!-- Main mountain silhouettes framing the central golden path -->
<path d="M 0 140 Q 280 310 520 280 Q 640 260 655 450 Q 635 680 590 900 L 0 900 Z" fill="url(#rmLeftMountain)"/>
<path d="M 1440 140 Q 1160 310 920 280 Q 800 260 785 450 Q 805 680 850 900 L 1440 900 Z" fill="url(#rmRightMountain)"/>

<!-- Thin cyan geometric guidelines & orbital coordinate arcs -->
<circle cx="720" cy="380" r="410" stroke="rgba(56, 217, 214, 0.16)" stroke-width="1.2" fill="none"/>
<circle cx="720" cy="380" r="260" stroke="rgba(56, 217, 214, 0.11)" stroke-dasharray="5 7" stroke-width="1" fill="none"/>
<rect x="250" y="80" width="940" height="740" stroke="rgba(56, 217, 214, 0.12)" stroke-width="1" fill="none"/>
<line x1="250" y1="380" x2="1190" y2="380" stroke="rgba(56, 217, 214, 0.08)" stroke-width="1"/>
<line x1="720" y1="80" x2="720" y2="820" stroke="rgba(56, 217, 214, 0.08)" stroke-width="1"/>
</svg>"""

_ENCODED_SVG = urllib.parse.quote(_BACKGROUND_SVG.replace("\n", " ").strip())

CUSTOM_CSS = f"""
<style>
/* ====================================================================
   RESEARCHMATE AI — CINEMATIC DEEP BLUE & TEAL THEME
   Inspired by misty mountain silhouettes and radiant golden beacon paths
   ==================================================================== */

/* Top level page background */
.stApp {{
    background-color: #050b14 !important;
    background-image: 
        radial-gradient(ellipse 700px 480px at 50% 28%, rgba(251, 191, 36, 0.16) 0%, rgba(245, 158, 11, 0.08) 35%, transparent 75%),
        url("data:image/svg+xml,{_ENCODED_SVG}") !important;
    background-size: cover !important;
    background-position: center top !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
    color: #f1f5f9 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
}}

/* Transparent header */
header[data-testid="stHeader"] {{
    background: transparent !important;
}}

/* Main block container padding */
.block-container {{
    max-width: 1200px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 4rem !important;
}}

/* Corner star accents */
.rm-corner-star {{
    color: #38d9d6;
    font-size: 1.35rem;
    line-height: 1;
    display: inline-block;
    filter: drop-shadow(0 0 8px rgba(56, 217, 214, 0.8)) drop-shadow(0 0 16px rgba(56, 217, 214, 0.4));
    user-select: none;
}}

/* Top metadata navigation bar */
.rm-top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(56, 217, 214, 0.22);
    padding: 0.6rem 0.2rem 1rem 0.2rem;
    margin-bottom: 1.8rem;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 0.78rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}}

.rm-meta-group {{
    display: flex;
    gap: 2rem;
    align-items: center;
    flex-wrap: wrap;
}}

.rm-meta-item {{
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
}}

.rm-meta-label {{
    color: #64748b;
    font-size: 0.68rem;
}}

.rm-meta-val {{
    color: #e2e8f0;
    font-weight: 600;
    letter-spacing: 0.08em;
}}

.rm-meta-val.cyan {{
    color: #38d9d6;
    text-shadow: 0 0 10px rgba(56, 217, 214, 0.35);
}}

/* Central Hero Banner */
.rm-hero {{
    text-align: center;
    padding: 1.8rem 1rem 2.2rem 1rem;
    margin-bottom: 2rem;
    position: relative;
}}

.rm-hero-emblem {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(253, 224, 71, 0.25) 0%, rgba(20, 184, 166, 0.15) 60%, rgba(5, 11, 20, 0.4) 100%);
    border: 1px solid rgba(253, 224, 71, 0.4);
    box-shadow: 0 0 24px rgba(245, 158, 11, 0.35), inset 0 0 12px rgba(253, 224, 71, 0.2);
    margin-bottom: 1rem;
    font-size: 1.8rem;
}}

.rm-hero-title {{
    font-size: 2.5rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin: 0;
    padding: 0;
    background: linear-gradient(180deg, #ffffff 30%, #cffafe 70%, #fde68a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 2px 14px rgba(56, 217, 214, 0.3));
}}

.rm-hero-subtitle {{
    font-size: 1.05rem;
    color: #94a3b8;
    max-width: 680px;
    margin: 0.6rem auto 1.2rem auto;
    line-height: 1.5;
    font-weight: 400;
}}

.rm-hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(12, 30, 48, 0.65);
    border: 1px solid rgba(56, 217, 214, 0.3);
    padding: 0.35rem 0.95rem;
    border-radius: 9999px;
    font-size: 0.76rem;
    color: #38d9d6;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 600;
    backdrop-filter: blur(8px);
    box-shadow: 0 4px 14px rgba(2, 8, 20, 0.4);
}}

.rm-pulse-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #38d9d6;
    box-shadow: 0 0 8px #38d9d6;
}}

/* Translucent Glassmorphism Cards & Panels */
div[data-testid="stContainer"],
div.st-emotion-cache-16txtl3,
div.st-emotion-cache-ocqkz7 {{
    border-radius: 16px !important;
}}

/* Bordered containers get cinematic translucent styling */
div[data-testid="stContainer"][border="true"],
div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {{
    background: rgba(8, 20, 36, 0.68) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(56, 217, 214, 0.22) !important;
    border-radius: 16px !important;
    box-shadow: 0 16px 36px -10px rgba(1, 8, 20, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}}

div[data-testid="stContainer"][border="true"]:hover {{
    border-color: rgba(56, 217, 214, 0.4) !important;
    box-shadow: 0 18px 40px -8px rgba(1, 8, 20, 0.7), 0 0 20px rgba(56, 217, 214, 0.12) !important;
}}

/* Workflow Step Cards in Overview Tab */
.rm-step-card {{
    background: rgba(9, 23, 40, 0.65);
    border: 1px solid rgba(56, 217, 214, 0.22);
    border-radius: 16px;
    padding: 1.4rem 1.2rem;
    backdrop-filter: blur(14px);
    box-shadow: 0 12px 28px -6px rgba(1, 8, 20, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.06);
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    height: 100%;
}}

.rm-step-card:hover {{
    transform: translateY(-3px);
    border-color: rgba(56, 217, 214, 0.45);
    box-shadow: 0 18px 36px -8px rgba(2, 10, 24, 0.7), 0 0 24px rgba(56, 217, 214, 0.18);
}}

.rm-step-num {{
    font-family: ui-monospace, monospace;
    font-size: 0.8rem;
    color: #fcd34d;
    font-weight: 700;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
    text-shadow: 0 0 8px rgba(251, 191, 36, 0.35);
}}

.rm-step-title {{
    font-size: 1.15rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 0.4rem;
}}

.rm-step-desc {{
    font-size: 0.86rem;
    color: #94a3b8;
    line-height: 1.5;
}}

/* Tabs Styling */
div[data-testid="stTabs"] {{
    margin-top: 0.5rem;
}}

div[data-testid="stTabs"] button[role="tab"] {{
    background: transparent !important;
    color: #94a3b8 !important;
    border-radius: 10px 10px 0 0 !important;
    border: none !important;
    font-size: 0.94rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 1.25rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
}}

div[data-testid="stTabs"] button[role="tab"]:hover {{
    color: #e2e8f0 !important;
    background: rgba(56, 217, 214, 0.06) !important;
}}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
    color: #38d9d6 !important;
    font-weight: 700 !important;
    background: rgba(12, 32, 54, 0.6) !important;
    border-bottom: 2px solid #38d9d6 !important;
    text-shadow: 0 0 12px rgba(56, 217, 214, 0.5) !important;
}}

/* File Uploader styling */
div[data-testid="stFileUploader"] {{
    background: rgba(7, 18, 32, 0.65) !important;
    border: 1px dashed rgba(56, 217, 214, 0.38) !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
    backdrop-filter: blur(12px) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}}

div[data-testid="stFileUploader"]:hover {{
    border-color: #38d9d6 !important;
    box-shadow: 0 0 20px rgba(56, 217, 214, 0.2) !important;
}}

div[data-testid="stFileUploader"] section {{
    background: transparent !important;
    border: none !important;
}}

/* Success & Error Banners */
div[data-testid="stAlert"] {{
    border-radius: 14px !important;
    backdrop-filter: blur(14px) !important;
    padding: 1rem 1.2rem !important;
    font-weight: 500 !important;
}}

div[data-testid="stAlert"] div[role="alert"] {{
    background: transparent !important;
    color: #f8fafc !important;
}}

/* Extracted Text Content Box */
.rm-text-preview-box {{
    background: rgba(4, 10, 18, 0.92) !important;
    border: 1px solid rgba(56, 217, 214, 0.22) !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
    color: #f1f5f9 !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace !important;
    font-size: 0.88rem !important;
    line-height: 1.65 !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
    box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.6) !important;
}}

/* Sidebar styling */
section[data-testid="stSidebar"] {{
    background: #050b14 !important;
    border-right: 1px solid rgba(56, 217, 214, 0.16) !important;
}}

section[data-testid="stSidebar"] div.block-container {{
    padding-top: 2rem !important;
}}

/* Form elements, selects, buttons */
div[data-baseweb="select"] > div {{
    background: rgba(7, 18, 32, 0.85) !important;
    border: 1px solid rgba(56, 217, 214, 0.3) !important;
    border-radius: 10px !important;
    color: #f8fafc !important;
}}

div[data-baseweb="select"] * {{
    color: #f8fafc !important;
}}

div[data-baseweb="popover"] {{
    background: #071526 !important;
    border: 1px solid rgba(56, 217, 214, 0.3) !important;
    border-radius: 12px !important;
}}

div[data-baseweb="popover"] li {{
    color: #f1f5f9 !important;
}}

div[data-baseweb="popover"] li:hover {{
    background: rgba(56, 217, 214, 0.15) !important;
}}

/* Expandable Citations */
div[data-testid="stExpander"] {{
    background: rgba(6, 17, 30, 0.6) !important;
    border: 1px solid rgba(56, 217, 214, 0.22) !important;
    border-radius: 12px !important;
    margin-top: 0.4rem !important;
    margin-bottom: 0.4rem !important;
}}

div[data-testid="stExpander"]:hover {{
    border-color: rgba(56, 217, 214, 0.42) !important;
}}

div[data-testid="stExpander"] summary {{
    color: #e2e8f0 !important;
    font-size: 0.88rem !important;
}}

/* Custom scrollbars */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: rgba(5, 12, 22, 0.6);
}}

::-webkit-scrollbar-thumb {{
    background: rgba(56, 217, 214, 0.28);
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: rgba(56, 217, 214, 0.5);
}}

/* Responsive adjustments for mobile and small screens */
@media (max-width: 768px) {{
    .rm-top-bar {{
        flex-direction: column;
        align-items: flex-start;
        gap: 0.8rem;
    }}
    .rm-meta-group {{
        gap: 1rem;
    }}
    .rm-hero-title {{
        font-size: 1.8rem;
    }}
    .rm-hero-subtitle {{
        font-size: 0.92rem;
    }}
    .rm-step-card {{
        margin-bottom: 0.8rem;
    }}
}}
</style>
"""


def get_header_html() -> str:
    """Generate the cinematic top metadata bar and corner star accents."""
    return """
    <div class="rm-top-bar">
      <div style="display:flex; align-items:center; gap:0.6rem;">
        <span class="rm-corner-star">✦</span>
        <div class="rm-meta-item">
          <span class="rm-meta-label">PROJECT</span>
          <span class="rm-meta-val cyan">RESEARCHMATE AI</span>
        </div>
      </div>
      <div class="rm-meta-group">
        <div class="rm-meta-item">
          <span class="rm-meta-label">SERVICES</span>
          <span class="rm-meta-val">PAPER-TO-PRESENTATION & VIVA</span>
        </div>
        <div class="rm-meta-item">
          <span class="rm-meta-label">FOCUS</span>
          <span class="rm-meta-val">AGENTIC ACADEMIC RAG</span>
        </div>
      </div>
      <span class="rm-corner-star">✦</span>
    </div>
    """


def get_hero_html() -> str:
    """Generate the central glowing hero banner inspired by the bright-path beacon."""
    return """
    <div class="rm-hero">
      <div class="rm-hero-emblem">✦</div>
      <h1 class="rm-hero-title">RESEARCHMATE AI</h1>
      <p class="rm-hero-subtitle">
        Turn research papers into clear presentations and a confident viva defense.
        Extract grounded evidence, explore concepts, and master your research.
      </p>
      <div class="rm-hero-badge">
        <span class="rm-pulse-dot"></span>
        <span>Milestone 1 Active · Page-Aware PDF Extraction</span>
      </div>
    </div>
    """


def get_workflow_cards_html() -> str:
    """Generate 3 translucent glassmorphic workflow cards for the Overview tab."""
    return """
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:1.2rem; margin:1rem 0 1.5rem 0;">
      <div class="rm-step-card">
        <div class="rm-step-num">01 · INGESTION</div>
        <div class="rm-step-title">Upload & Extract</div>
        <div class="rm-step-desc">
          Upload any digital research PDF. PyMuPDF extracts text page by page, preserving original 1-based page coordinates.
        </div>
      </div>
      <div class="rm-step-card">
        <div class="rm-step-num">02 · EXPLORATION</div>
        <div class="rm-step-title">Agentic RAG</div>
        <div class="rm-step-desc">
          Ask nuanced questions. ChromaDB vector indexing and Gemini retrieve exact passages with page citations.
        </div>
      </div>
      <div class="rm-step-card">
        <div class="rm-step-num">03 · DEFENSE</div>
        <div class="rm-step-title">Slides & Viva</div>
        <div class="rm-step-desc">
          Export academic PowerPoint decks and practice interactive viva examinations with rigorous rubric feedback.
        </div>
      </div>
    </div>
    """

