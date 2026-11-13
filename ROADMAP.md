# ResearchMate AI — Development Roadmap

## Product goal

Build a professional but explainable college project for **Assignment 5: Paper-to-Presentation & Viva Agent**. A student uploads one research paper and can understand it, ask grounded questions, prepare a presentation, and practice a viva. The application must make the seven mandatory course criteria visible in both the design and the demonstration.

## Delivery phases

### 0. Project foundation — started

- Create a modular Python / Streamlit project.
- Keep secrets in local environment configuration.
- Provide an LCEL prompt → Gemini → output-parser scaffold.
- Establish navigation for the required user workflows.

**Done when:** the app launches locally, configuration has no committed secrets, and the project structure is understandable to a beginner.

### 1. PDF intake and page-aware extraction

- Accept PDF upload and validate size/type; handle empty, encrypted, and scanned PDFs gracefully.
- Extract text per page with PyMuPDF and preserve 1-based page labels.
- Create stable document IDs and chunk text with overlap; attach document name, page, and chunk metadata.
- Show a document preview and useful processing errors.

**Done when:** a sample paper can be uploaded and extracted text can be traced back to its original page.

### 2. Embeddings, ChromaDB, and Agentic RAG

- Use Gemini embedding integration with distinct document/query retrieval task settings where supported.
- Persist vectors in a local ChromaDB collection; scope retrieval to the current document.
- Retrieve relevant chunks for each query, pass only those excerpts to the answer prompt, and include page citations.
- Add a clear “not found in this paper” response when retrieved context is insufficient.

**Done when:** a question about the paper returns a grounded answer and supporting page references, while an unrelated question is not presented as paper fact.

### 3. Prompt engineering and specialized workflows

- Create versioned prompt templates for paper summary, concept/method/result extraction, slide outline, viva question, and answer evaluation.
- Use structured output schemas for machine-consumed results; validate output and recover from malformed responses.
- Keep the prompts explicit about evidence, uncertainty, audience, and citation format.

**Done when:** generated outputs are consistent, relevant to supplied evidence, and render safely in the UI.

### 4. Intent detection and routing₹

- Classify a request into paper chat, summary, concept extraction, slide creation, viva, or flashcards.
- Route each intent to a dedicated chain/tool and return a user-friendly fallback for ambiguous requests.
- Log the selected route and response metadata for explainability.

**Done when:** the same chat entry point reliably routes representative requests to the expected workflow, and the chosen route is inspectable.

### 5. Paper chat experience

- Add conversational follow-up questions with document-aware history.
- Use retrieval on every answer rather than trusting conversation history alone.
- Render citations as page chips/expanders linked to extracted source passages.
- Allow clearing the active conversation and switching papers without mixing their data.

**Done when:** users can ask follow-ups and inspect the retrieved evidence behind each answer.

### 6. Presentation generation and themes

- Let the student choose slide count, talk duration, audience/technical level, and a visual theme.
- Generate and validate a slide outline before rendering a PPTX with python-pptx.
- Add source notes/page citations to relevant slides; provide a download and a slide preview.
- Offer a small curated set of themes plus editable accent/background colors.

**Done when:** each exported deck opens successfully, follows requested settings, and traces factual slides to the paper.

### 7. Viva simulator and flashcards

- Run an interactive examiner session: one question at a time, student answer, rubric-based feedback, and optional follow-up.
- Cover paper-specific understanding (problem, method, results, limitations, contribution) with evidence-aware questions.
- Generate editable flashcards and provide reveal/next/shuffle controls.
- Save session/card state per paper without storing unnecessary personal information.

**Done when:** a student completes a session, sees clear actionable feedback, and can revise from paper-grounded cards.

### 8. Performance dashboard

**Current implementation:** Completed viva sessions save score summaries and topic averages locally in SQLite; the dashboard shows session averages, best score, topic performance, strengths, revision areas, and recent sessions. Individual answers are not stored.

- Track scores by rubric dimension and topic, session history, and suggested revision areas.
- Display progress with simple, accessible Plotly charts and clear empty states.
- Explain how scores are computed and allow clearing local history.

**Done when:** dashboard values match recorded sessions and can be understood without interpreting raw data.

### 9. Assignment demonstration and delivery

- Walk through one paper from upload to cited chat, slide export, viva practice, flashcards, and dashboard.
- Validate the seven mandatory criteria with a traceability table below.
- Add screenshots/demo script, limitations, setup instructions, and troubleshooting.
- Check failure states, secret handling, and output quality before presenting.

## Mandatory acceptance criteria traceability

| Course criterion | Planned implementation | Demonstration evidence |
|---|---|---|
| LLM integration | Gemini chat model via LangChain integration | Successful grounded response using local key |
| Interactive GUI | Streamlit multi-workflow interface | Upload, chat, settings, session controls, downloads |
| Prompt engineering | Task-specific templates with evidence and uncertainty rules | Inspectable templates and consistent outputs |
| LangChain prompt templates + LCEL | `ChatPromptTemplate` composed with model and parser using `|` | Show chain construction and invoke flow |
| Agentic RAG | Retrieve paper chunks, then route context to a task chain | Query-specific evidence and page citation |
| Intent detection/routing | Intent classifier directs user tasks to specialized flows | Show sample intents and selected destinations |
| ChromaDB vector database | Persistent local vector collection with document/page metadata | Search a paper and inspect retrieved chunks |

## Additional chosen features

- **Chat with PDF:** page-aware conversational retrieval.
- **Interactive viva:** one-at-a-time examiner simulation, feedback, follow-ups.
- **Page-wise sources:** citations and source passages tied to original PDF pages.
- **Performance dashboard:** scores, topic strengths, gaps, and progress.
- **Custom PowerPoint:** slide count, duration, language level, and theme options.
- **Flashcards:** paper-derived question/answer revision cards.

## Beginner-friendly build order

Each milestone should be added in a small, explainable increment: first make PDF page extraction visible, then index it, then retrieve, then call Gemini, then add each workflow. This makes the assignment easy to demonstrate and helps identify whether a problem comes from the PDF, retrieval, prompt, model, or interface.
