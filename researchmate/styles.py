"""Futuristic violet-cosmos styling and visual theme for Research AI — AGENTIC-AI.

Designed by vSalagundiadikeshavareddy | 1CR24AD106
Inspired by deep-space aurora gradients, neon violet nebulae, and holographic grid overlays.
"""

import urllib.parse

# 1. Generate a futuristic violet-cosmos SVG background with aurora bands and holographic grid.
_BACKGROUND_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice">
<defs>
  <!-- Deep space background -->
  <radialGradient id="aiSpace" cx="50%" cy="40%" r="80%">
    <stop offset="0%" stop-color="#120826" stop-opacity="1"/>
    <stop offset="40%" stop-color="#0a0418" stop-opacity="1"/>
    <stop offset="100%" stop-color="#030008" stop-opacity="1"/>
  </radialGradient>

  <!-- Aurora violet glow centre -->
  <radialGradient id="aiAurora" cx="50%" cy="35%" r="45%">
    <stop offset="0%" stop-color="#a855f7" stop-opacity="0.32"/>
    <stop offset="30%" stop-color="#7c3aed" stop-opacity="0.18"/>
    <stop offset="65%" stop-color="#4f46e5" stop-opacity="0.08"/>
    <stop offset="100%" stop-color="#030008" stop-opacity="0"/>
  </radialGradient>

  <!-- Left aurora sweep -->
  <linearGradient id="aiLeft" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#6d28d9" stop-opacity="0.45"/>
    <stop offset="50%" stop-color="#4c1d95" stop-opacity="0.25"/>
    <stop offset="100%" stop-color="#030008" stop-opacity="0"/>
  </linearGradient>

  <!-- Right aurora sweep -->
  <linearGradient id="aiRight" x1="100%" y1="0%" x2="0%" y2="100%">
    <stop offset="0%" stop-color="#7c3aed" stop-opacity="0.4"/>
    <stop offset="50%" stop-color="#5b21b6" stop-opacity="0.2"/>
    <stop offset="100%" stop-color="#030008" stop-opacity="0"/>
  </linearGradient>

  <!-- Neon beam vertical -->
  <linearGradient id="aiBeam" x1="50%" y1="0%" x2="50%" y2="100%">
    <stop offset="0%" stop-color="#e879f9" stop-opacity="0.3"/>
    <stop offset="20%" stop-color="#c026d3" stop-opacity="0.18"/>
    <stop offset="55%" stop-color="#7c3aed" stop-opacity="0.08"/>
    <stop offset="100%" stop-color="#030008" stop-opacity="0"/>
  </linearGradient>

  <!-- Nebula mist -->
  <linearGradient id="aiMist" x1="50%" y1="0%" x2="50%" y2="100%">
    <stop offset="0%" stop-color="#2e1065" stop-opacity="0.5"/>
    <stop offset="100%" stop-color="#030008" stop-opacity="0.9"/>
  </linearGradient>
</defs>

<!-- Space base -->
<rect width="1440" height="900" fill="url(#aiSpace)"/>

<!-- Aurora centre glow -->
<ellipse cx="720" cy="310" rx="380" ry="420" fill="url(#aiAurora)"/>

<!-- Neon vertical beam -->
<path d="M 650 900 Q 690 500 705 340 Q 715 200 720 100 Q 725 200 735 340 Q 750 500 790 900 Z" fill="url(#aiBeam)"/>

<!-- Left nebula sweep -->
<path d="M 0 180 Q 300 350 540 310 Q 640 290 660 500 Q 640 700 600 900 L 0 900 Z" fill="url(#aiLeft)"/>

<!-- Right nebula sweep -->
<path d="M 1440 180 Q 1140 350 900 310 Q 800 290 780 500 Q 800 700 840 900 L 1440 900 Z" fill="url(#aiRight)"/>

<!-- Holographic grid overlay (violet) -->
<line x1="0" y1="300" x2="1440" y2="300" stroke="rgba(167, 139, 250, 0.09)" stroke-width="1"/>
<line x1="0" y1="450" x2="1440" y2="450" stroke="rgba(167, 139, 250, 0.07)" stroke-width="1"/>
<line x1="0" y1="600" x2="1440" y2="600" stroke="rgba(167, 139, 250, 0.05)" stroke-width="1"/>
<line x1="360" y1="0" x2="360" y2="900" stroke="rgba(167, 139, 250, 0.07)" stroke-width="1"/>
<line x1="720" y1="0" x2="720" y2="900" stroke="rgba(167, 139, 250, 0.09)" stroke-width="1"/>
<line x1="1080" y1="0" x2="1080" y2="900" stroke="rgba(167, 139, 250, 0.07)" stroke-width="1"/>

<!-- Holographic orbital rings -->
<circle cx="720" cy="380" r="380" stroke="rgba(192, 132, 252, 0.13)" stroke-width="1.2" fill="none"/>
<circle cx="720" cy="380" r="240" stroke="rgba(192, 132, 252, 0.09)" stroke-dasharray="6 8" stroke-width="1" fill="none"/>
<circle cx="720" cy="380" r="140" stroke="rgba(232, 121, 249, 0.07)" stroke-dasharray="3 9" stroke-width="1" fill="none"/>

<!-- Mist bands at bottom -->
<path d="M 0 620 Q 360 680 720 660 Q 1080 640 1440 620 L 1440 900 L 0 900 Z" fill="url(#aiMist)"/>
</svg>"""

_ENCODED_SVG = urllib.parse.quote(_BACKGROUND_SVG.replace("\n", " ").strip())

CUSTOM_CSS = f"""
<style>
/* ====================================================================
   RESEARCH AI — AGENTIC-AI · VIOLET COSMOS THEME
   Designed by: vSalagundiadikeshavareddy | 1CR24AD106
   Aurora nebula gradients · Holographic grid · Neon violet accents
   ==================================================================== */

/* Top level page background */
.stApp {{
    background-color: #080012 !important;
    background-image:
        radial-gradient(ellipse 600px 400px at 50% 25%, rgba(168, 85, 247, 0.18) 0%, rgba(124, 58, 237, 0.08) 40%, transparent 75%),
        url("data:image/svg+xml,{_ENCODED_SVG}") !important;
    background-size: cover !important;
    background-position: center top !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
    color: #f1f5f9 !important;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
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

/* Corner star accents - violet */
.rm-corner-star {{
    color: #c084fc;
    font-size: 1.35rem;
    line-height: 1;
    display: inline-block;
    filter: drop-shadow(0 0 8px rgba(192, 132, 252, 0.9)) drop-shadow(0 0 18px rgba(192, 132, 252, 0.5));
    user-select: none;
}}

/* Top metadata navigation bar */
.rm-top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(192, 132, 252, 0.25);
    padding: 0.6rem 0.2rem 1rem 0.2rem;
    margin-bottom: 1.8rem;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 0.78rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    background: rgba(10, 2, 24, 0.5);
    backdrop-filter: blur(12px);
    border-radius: 0 0 12px 12px;
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
    color: #6b7280;
    font-size: 0.68rem;
}}

.rm-meta-val {{
    color: #e2e8f0;
    font-weight: 600;
    letter-spacing: 0.08em;
}}

.rm-meta-val.violet {{
    color: #c084fc;
    text-shadow: 0 0 10px rgba(192, 132, 252, 0.45);
}}

.rm-meta-val.pink {{
    color: #f0abfc;
    text-shadow: 0 0 10px rgba(240, 171, 252, 0.4);
}}

/* Central Hero Banner */
.rm-hero {{
    text-align: center;
    padding: 2rem 1rem 2.4rem 1rem;
    margin-bottom: 2rem;
    position: relative;
}}

.rm-hero-emblem {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 70px;
    height: 70px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(232, 121, 249, 0.28) 0%, rgba(124, 58, 237, 0.18) 55%, rgba(8, 0, 18, 0.5) 100%);
    border: 1.5px solid rgba(232, 121, 249, 0.5);
    box-shadow: 0 0 32px rgba(192, 132, 252, 0.4), inset 0 0 16px rgba(232, 121, 249, 0.2);
    margin-bottom: 1rem;
    font-size: 2rem;
    animation: rm-pulse 3s ease-in-out infinite;
}}

@keyframes rm-pulse {{
    0%, 100% {{ box-shadow: 0 0 32px rgba(192, 132, 252, 0.4), inset 0 0 16px rgba(232, 121, 249, 0.2); }}
    50% {{ box-shadow: 0 0 52px rgba(192, 132, 252, 0.7), inset 0 0 24px rgba(232, 121, 249, 0.35); }}
}}

.rm-hero-title {{
    font-size: 2.6rem;
    font-weight: 900;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0;
    padding: 0;
    background: linear-gradient(135deg, #f0abfc 0%, #c084fc 35%, #818cf8 65%, #e879f9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 2px 16px rgba(192, 132, 252, 0.4));
}}

.rm-hero-subtitle {{
    font-size: 1.05rem;
    color: #9ca3af;
    max-width: 680px;
    margin: 0.65rem auto 0.6rem auto;
    line-height: 1.55;
    font-weight: 400;
}}

.rm-hero-author {{
    font-size: 0.82rem;
    color: #a78bfa;
    letter-spacing: 0.06em;
    margin: 0.3rem auto 1.1rem auto;
    font-family: ui-monospace, monospace;
    text-shadow: 0 0 10px rgba(167, 139, 250, 0.4);
}}

.rm-hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(18, 8, 38, 0.72);
    border: 1px solid rgba(192, 132, 252, 0.35);
    padding: 0.35rem 1rem;
    border-radius: 9999px;
    font-size: 0.76rem;
    color: #c084fc;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-weight: 600;
    backdrop-filter: blur(8px);
    box-shadow: 0 4px 16px rgba(5, 0, 20, 0.5), 0 0 20px rgba(192, 132, 252, 0.15);
}}

.rm-pulse-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #c084fc;
    box-shadow: 0 0 8px #c084fc, 0 0 16px rgba(192, 132, 252, 0.6);
    animation: rm-blink 1.8s ease-in-out infinite;
}}

@keyframes rm-blink {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.3; }}
}}

/* Translucent Glassmorphism Cards & Panels */
div[data-testid="stContainer"],
div.st-emotion-cache-16txtl3,
div.st-emotion-cache-ocqkz7 {{
    border-radius: 18px !important;
}}

/* Bordered containers get violet-cosmos translucent styling */
div[data-testid="stContainer"][border="true"],
div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {{
    background: rgba(14, 4, 32, 0.72) !important;
    backdrop-filter: blur(18px) !important;
    -webkit-backdrop-filter: blur(18px) !important;
    border: 1px solid rgba(192, 132, 252, 0.22) !important;
    border-radius: 18px !important;
    box-shadow: 0 16px 40px -10px rgba(1, 0, 10, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.07) !important;
    transition: border-color 0.28s ease, box-shadow 0.28s ease !important;
}}

div[data-testid="stContainer"][border="true"]:hover {{
    border-color: rgba(192, 132, 252, 0.45) !important;
    box-shadow: 0 20px 44px -8px rgba(1, 0, 10, 0.75), 0 0 24px rgba(192, 132, 252, 0.15) !important;
}}

/* Workflow Step Cards in Overview Tab */
.rm-step-card {{
    background: rgba(16, 5, 36, 0.7);
    border: 1px solid rgba(192, 132, 252, 0.2);
    border-radius: 18px;
    padding: 1.5rem 1.3rem;
    backdrop-filter: blur(16px);
    box-shadow: 0 12px 30px -6px rgba(1, 0, 10, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    transition: transform 0.22s ease, border-color 0.22s ease, box-shadow 0.22s ease;
    height: 100%;
    position: relative;
    overflow: hidden;
}}

.rm-step-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(192, 132, 252, 0.6), transparent);
    border-radius: 18px 18px 0 0;
}}

.rm-step-card:hover {{
    transform: translateY(-4px);
    border-color: rgba(192, 132, 252, 0.5);
    box-shadow: 0 20px 40px -8px rgba(2, 0, 16, 0.75), 0 0 28px rgba(192, 132, 252, 0.2);
}}

.rm-step-num {{
    font-family: ui-monospace, monospace;
    font-size: 0.8rem;
    color: #e879f9;
    font-weight: 700;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
    text-shadow: 0 0 10px rgba(232, 121, 249, 0.45);
}}

.rm-step-title {{
    font-size: 1.15rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 0.4rem;
}}

.rm-step-desc {{
    font-size: 0.86rem;
    color: #9ca3af;
    line-height: 1.55;
}}

/* Tabs Styling — violet */
div[data-testid="stTabs"] {{
    margin-top: 0.5rem;
}}

div[data-testid="stTabs"] button[role="tab"] {{
    background: transparent !important;
    color: #9ca3af !important;
    border-radius: 10px 10px 0 0 !important;
    border: none !important;
    font-size: 0.94rem !important;
    font-weight: 500 !important;
    padding: 0.65rem 1.3rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.22s ease !important;
}}

div[data-testid="stTabs"] button[role="tab"]:hover {{
    color: #e2e8f0 !important;
    background: rgba(192, 132, 252, 0.07) !important;
}}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
    color: #c084fc !important;
    font-weight: 700 !important;
    background: rgba(20, 6, 46, 0.65) !important;
    border-bottom: 2px solid #c084fc !important;
    text-shadow: 0 0 14px rgba(192, 132, 252, 0.6) !important;
}}

/* File Uploader styling — violet */
div[data-testid="stFileUploader"] {{
    background: rgba(10, 3, 24, 0.68) !important;
    border: 1.5px dashed rgba(192, 132, 252, 0.4) !important;
    border-radius: 18px !important;
    padding: 1.2rem !important;
    backdrop-filter: blur(14px) !important;
    transition: border-color 0.22s ease, box-shadow 0.22s ease !important;
}}

div[data-testid="stFileUploader"]:hover {{
    border-color: #c084fc !important;
    box-shadow: 0 0 24px rgba(192, 132, 252, 0.22) !important;
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
    border-left: 3px solid rgba(192, 132, 252, 0.6) !important;
}}

div[data-testid="stAlert"] div[role="alert"] {{
    background: transparent !important;
    color: #f8fafc !important;
}}

/* Extracted Text Content Box */
.rm-text-preview-box {{
    background: rgba(6, 2, 16, 0.92) !important;
    border: 1px solid rgba(192, 132, 252, 0.22) !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
    color: #f1f5f9 !important;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace !important;
    font-size: 0.88rem !important;
    line-height: 1.65 !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
    box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.7) !important;
}}

/* Sidebar styling — dark violet */
section[data-testid="stSidebar"] {{
    background: #070011 !important;
    border-right: 1px solid rgba(192, 132, 252, 0.18) !important;
}}

section[data-testid="stSidebar"] div.block-container {{
    padding-top: 2rem !important;
}}

/* Form elements, selects */
div[data-baseweb="select"] > div {{
    background: rgba(10, 3, 24, 0.88) !important;
    border: 1px solid rgba(192, 132, 252, 0.3) !important;
    border-radius: 10px !important;
    color: #f8fafc !important;
}}

div[data-baseweb="select"] * {{
    color: #f8fafc !important;
}}

div[data-baseweb="popover"] {{
    background: #0f0526 !important;
    border: 1px solid rgba(192, 132, 252, 0.3) !important;
    border-radius: 12px !important;
}}

div[data-baseweb="popover"] li {{
    color: #f1f5f9 !important;
}}

div[data-baseweb="popover"] li:hover {{
    background: rgba(192, 132, 252, 0.15) !important;
}}

/* Expandable Citations */
div[data-testid="stExpander"] {{
    background: rgba(8, 2, 20, 0.65) !important;
    border: 1px solid rgba(192, 132, 252, 0.2) !important;
    border-radius: 12px !important;
    margin-top: 0.4rem !important;
    margin-bottom: 0.4rem !important;
}}

div[data-testid="stExpander"]:hover {{
    border-color: rgba(192, 132, 252, 0.44) !important;
}}

div[data-testid="stExpander"] summary {{
    color: #e2e8f0 !important;
    font-size: 0.88rem !important;
}}

/* Primary buttons — violet glow */
button[kind="primary"], .stButton > button[data-testid="baseButton-primary"] {{
    background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 50%, #5b21b6 100%) !important;
    border: 1px solid rgba(192, 132, 252, 0.4) !important;
    color: #fff !important;
    box-shadow: 0 4px 16px rgba(109, 40, 217, 0.4) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.22s ease !important;
}}

button[kind="primary"]:hover, .stButton > button[data-testid="baseButton-primary"]:hover {{
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 50%, #6d28d9 100%) !important;
    box-shadow: 0 6px 24px rgba(139, 92, 246, 0.6) !important;
    transform: translateY(-1px) !important;
}}

/* Custom scrollbars — violet */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: rgba(5, 1, 14, 0.7);
}}

::-webkit-scrollbar-thumb {{
    background: rgba(192, 132, 252, 0.3);
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: rgba(192, 132, 252, 0.55);
}}

/* Metric widgets */
div[data-testid="stMetric"] {{
    background: rgba(14, 4, 32, 0.65) !important;
    border: 1px solid rgba(192, 132, 252, 0.18) !important;
    border-radius: 14px !important;
    padding: 1rem !important;
    backdrop-filter: blur(12px) !important;
}}

div[data-testid="stMetricLabel"] {{
    color: #9ca3af !important;
    font-size: 0.82rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}}

div[data-testid="stMetricValue"] {{
    color: #c084fc !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    text-shadow: 0 0 12px rgba(192, 132, 252, 0.4) !important;
}}

/* Responsive adjustments */
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
        font-size: 1.9rem;
    }}
    .rm-hero-subtitle {{
        font-size: 0.92rem;
    }}
    .rm-step-card {{
        margin-bottom: 0.8rem;
    }}
}}

/* Refined application shell: reduce visual noise and improve hierarchy */
.block-container {{
    max-width: 1180px !important;
    padding-top: 0.8rem !important;
}}

.rm-top-bar {{
    margin-bottom: 0.7rem !important;
    padding: 0.45rem 0.2rem 0.65rem 0.2rem !important;
}}

.rm-hero {{
    padding: 1.2rem 1rem 1.3rem 1rem !important;
    margin-bottom: 0.8rem !important;
}}

.rm-hero-emblem {{
    width: 48px !important;
    height: 48px !important;
    font-size: 1.35rem !important;
    margin-bottom: 0.45rem !important;
}}

.rm-hero-title {{
    font-size: 2.15rem !important;
    letter-spacing: 0.055em !important;
}}

.rm-hero-subtitle {{
    max-width: 720px !important;
    margin-top: 0.35rem !important;
}}

.rm-hero-author {{
    margin-bottom: 0.6rem !important;
}}

section[data-testid="stSidebar"] {{
    min-width: 260px !important;
}}

section[data-testid="stSidebar"] div.block-container {{
    padding-top: 1.2rem !important;
}}

div[data-testid="stTabs"] {{
    border-top: 1px solid rgba(192, 132, 252, 0.12);
    padding-top: 0.35rem;
}}

div[data-testid="stMetric"] {{
    min-height: 94px;
}}
</style>
"""


def get_header_html() -> str:
    """Generate the holographic violet metadata bar — AGENTIC-AI edition."""
    return """
    <div class="rm-top-bar">
      <div style="display:flex; align-items:center; gap:0.6rem;">
        <span class="rm-corner-star">◈</span>
        <div class="rm-meta-item">
          <span class="rm-meta-label">PROJECT</span>
          <span class="rm-meta-val violet">RESEARCH AI · AGENTIC-AI</span>
        </div>
      </div>
      <div class="rm-meta-group">
        <div class="rm-meta-item">
          <span class="rm-meta-label">DEVELOPER</span>
          <span class="rm-meta-val pink">vSalagundiadikeshavareddy</span>
        </div>
        <div class="rm-meta-item">
          <span class="rm-meta-label">ROLL NO</span>
          <span class="rm-meta-val">1CR24AD106</span>
        </div>
        <div class="rm-meta-item">
          <span class="rm-meta-label">FOCUS</span>
          <span class="rm-meta-val">AGENTIC ACADEMIC RAG</span>
        </div>
      </div>
      <span class="rm-corner-star">◈</span>
    </div>
    """


def get_hero_html() -> str:
    """Generate the central violet cosmos hero banner — AGENTIC-AI edition."""
    return """
    <div class="rm-hero">
      <div class="rm-hero-emblem">🔬</div>
      <h1 class="rm-hero-title">Research AI</h1>
      <p class="rm-hero-subtitle">
        Transform research papers into compelling presentations and ace your viva defense.
        Powered by Agentic RAG, Gemini, and ChromaDB — built for academic excellence.
      </p>
      <div class="rm-hero-author">
        ◈ &nbsp; vSalagundiadikeshavareddy &nbsp;·&nbsp; 1CR24AD106 &nbsp;·&nbsp; AGENTIC-AI &nbsp; ◈
      </div>
      <div class="rm-hero-badge">
        <span class="rm-pulse-dot"></span>
        <span>AGENTIC-AI Active · Page-Aware PDF Extraction · Gemini RAG</span>
      </div>
    </div>
    """


def get_workflow_cards_html() -> str:
    """Generate 3 holographic violet workflow cards for the Overview tab."""
    return """
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:1.3rem; margin:1rem 0 1.5rem 0;">
      <div class="rm-step-card">
        <div class="rm-step-num">01 · INGESTION</div>
        <div class="rm-step-title">📄 Upload & Extract</div>
        <div class="rm-step-desc">
          Upload any digital research PDF. PyMuPDF extracts text page by page, preserving original 1-based page coordinates with full fidelity.
        </div>
      </div>
      <div class="rm-step-card">
        <div class="rm-step-num">02 · EXPLORATION</div>
        <div class="rm-step-title">🧠 Agentic RAG</div>
        <div class="rm-step-desc">
          Ask nuanced questions. ChromaDB vector indexing and Gemini retrieve exact passages with verifiable page citations from your paper.
        </div>
      </div>
      <div class="rm-step-card">
        <div class="rm-step-num">03 · MASTERY</div>
        <div class="rm-step-title">🎯 Slides & Viva</div>
        <div class="rm-step-desc">
          Export academic PowerPoint decks and practice interactive viva examinations with rigorous AI rubric feedback and flashcards.
        </div>
      </div>
    </div>
    """
