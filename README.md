<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=7c3aed&height=200&section=header&text=Research%20AI&fontSize=60&fontColor=ffffff&fontAlignY=38&desc=AGENTIC-AI%20%7C%20Academic%20Intelligence%20Platform&descAlignY=58&descColor=c084fc&animation=fadeIn" width="100%"/>

<br/>

[![Python](https://img.shields.io/badge/Python-3.11+-7c3aed?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-c084fc?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google-Gemini_AI-a855f7?style=for-the-badge&logo=google&logoColor=white)](https://deepmind.google/gemini)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-6d28d9?style=for-the-badge&logo=databricks&logoColor=white)](https://trychroma.com)
[![License](https://img.shields.io/badge/License-MIT-e879f9?style=for-the-badge)](LICENSE)

<br/>

> ### 🔬 *Turn research papers into compelling presentations and ace your viva defense.*
> *Powered by Agentic RAG · Gemini · ChromaDB · LangChain*

<br/>

**Developer** &nbsp;·&nbsp; `vSalagundiadikeshavareddy` &nbsp;·&nbsp; Roll No: `1CR24AD106` &nbsp;·&nbsp; Branch: `AGENTIC-AI`

</div>

---

<br/>

## ✨ What is Research AI?

**Research AI (AGENTIC-AI)** is a full-stack AI-powered academic assistant that understands your research papers, generates beautiful presentations, drills you with viva questions, and tracks your learning — all in one sleek interface.

It was built as part of **Assignment 5: Paper-to-Presentation & Viva Agent**, redesigned from the ground up with a **Violet Cosmos** aesthetic — holographic grids, aurora nebula gradients, and neon violet UI.

<br/>

## 🌟 Features

<table>
  <tr>
    <td align="center" width="25%">
      <h3>📄</h3>
      <strong>PDF Extraction</strong><br/>
      <sub>Page-aware text extraction using PyMuPDF with 1-based page coordinates</sub>
    </td>
    <td align="center" width="25%">
      <h3>🧠</h3>
      <strong>Agentic RAG Chat</strong><br/>
      <sub>ChromaDB vector indexing + Gemini retrieval with exact page citations</sub>
    </td>
    <td align="center" width="25%">
      <h3>📊</h3>
      <strong>PowerPoint Generator</strong><br/>
      <sub>Academic slide decks with grounded citations, speaker notes & themes</sub>
    </td>
    <td align="center" width="25%">
      <h3>🎓</h3>
      <strong>Viva Simulator</strong><br/>
      <sub>Interactive oral defense practice with AI rubric-based feedback</sub>
    </td>
  </tr>
  <tr>
    <td align="center" width="25%">
      <h3>🗂️</h3>
      <strong>Flashcards</strong><br/>
      <sub>Paper-grounded flashcards with citations for active recall study</sub>
    </td>
    <td align="center" width="25%">
      <h3>📑</h3>
      <strong>Paper Analysis</strong><br/>
      <sub>6-section academic summary: Problem, Methodology, Findings & more</sub>
    </td>
    <td align="center" width="25%">
      <h3>💡</h3>
      <strong>Key Concepts</strong><br/>
      <sub>Extract theoretical frameworks with plain-language explanations</sub>
    </td>
    <td align="center" width="25%">
      <h3>📈</h3>
      <strong>Dashboard</strong><br/>
      <sub>Local score history, topic performance, and study progress tracking</sub>
    </td>
  </tr>
</table>

<br/>

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Research AI · AGENTIC-AI                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   📄 PDF Upload                                             │
│        └──► PyMuPDF ──► Page-Indexed Text Store            │
│                                                             │
│   🧠 Agentic RAG                                            │
│        └──► Gemini Embeddings ──► ChromaDB ──► Retrieval   │
│                                                             │
│   🤖 Intent Router (LangChain LCEL)                         │
│        ├──► Paper Chat        (grounded Q&A)               │
│        ├──► Paper Summary     (6-section synthesis)        │
│        ├──► Key Concepts      (framework extraction)       │
│        ├──► Presentation      (python-pptx slide deck)     │
│        ├──► Viva Practice     (rubric-based feedback)      │
│        └──► Flashcards        (active recall cards)        │
│                                                             │
│   📊 Dashboard (Pandas + Plotly · local JSON storage)       │
└─────────────────────────────────────────────────────────────┘
```

<br/>

## 🛠️ Tech Stack

| Layer | Technology |
|:------|:-----------|
| **UI Framework** | Streamlit · Custom Violet Cosmos CSS |
| **AI / LLM** | Google Gemini (gemini-2.0-flash) |
| **Embeddings** | Google Gemini Embedding Model |
| **Vector Store** | ChromaDB |
| **Prompt Chains** | LangChain LCEL |
| **PDF Processing** | PyMuPDF (fitz) |
| **Presentations** | python-pptx |
| **Data Viz** | Pandas + Plotly |

<br/>

## ⚡ Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/aadhi454/Research-AI.git
cd Research-AI
git checkout AGENTIC-AI
```

### 2. Create a virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure your API key
```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```
Open `.env` and replace `your_gemini_api_key_here` with your actual Gemini API key.

> 🔒 `.env` is git-ignored. Never commit your API key.

### 5. Launch the app
```bash
streamlit run app.py
```

🌐 Open your browser at `http://localhost:8501`

<br/>

## 🎨 UI Theme — Violet Cosmos

The frontend was completely redesigned with a unique **Violet Cosmos** aesthetic:

- 🌌 **Deep space** dark background (`#080012`)
- 🔮 **Aurora nebula** violet gradients and glow effects
- 🕸️ **Holographic grid** overlay with cosmic lines
- 💜 **Neon violet** (`#c084fc`) primary accent color
- ✨ **Glassmorphism** cards with blur + translucency
- 💫 **Animated** pulsing emblem and blinking status dot
- 📱 **Fully responsive** for all screen sizes

<br/>

## 📁 Project Structure

```
Research-AI/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── .streamlit/
│   └── config.toml             # Violet cosmos Streamlit theme
└── researchmate/
    ├── styles.py               # Custom CSS + HTML components
    ├── config.py               # App configuration & settings
    ├── pdf.py                  # PyMuPDF PDF extraction
    ├── rag.py                  # ChromaDB + Gemini RAG engine
    ├── analysis.py             # Paper summary & concept extraction
    ├── router.py               # Intent detection & routing
    ├── presentation.py         # PowerPoint generation
    ├── viva.py                 # Viva Q&A simulator
    ├── flashcards.py           # Flashcard generation
    ├── progress.py             # Dashboard & score tracking
    └── prompts.py              # LangChain prompt templates
```

<br/>

## 🚀 How to Use

1. **Upload a Paper** — Drag and drop any research PDF into the Paper Chat tab
2. **Explore** — Ask questions, generate summaries, extract key concepts
3. **Present** — Generate a custom-themed PowerPoint slide deck
4. **Practice** — Run a viva session with AI-graded oral exam questions
5. **Study** — Review flashcards and track progress on the Dashboard

<br/>

## 👨‍💻 Developer

<div align="center">

| Field | Details |
|:------|:--------|
| **Name** | vSalagundiadikeshavareddy |
| **Roll No** | 1CR24AD106 |
| **Project** | AGENTIC-AI · Research AI |
| **Assignment** | Paper-to-Presentation & Viva Agent |
| **Branch** | AGENTIC-AI |

</div>

<br/>

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=7c3aed&height=120&section=footer&text=AGENTIC-AI%20%7C%201CR24AD106&fontSize=20&fontColor=c084fc&fontAlignY=65&animation=fadeIn" width="100%"/>

**Research AI · AGENTIC-AI** &nbsp;·&nbsp; Built with 💜 by vSalagundiadikeshavareddy

</div>
