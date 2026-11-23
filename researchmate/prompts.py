"""Prompt templates and LCEL chain construction using Google GenAI SDK Interactions API."""

from typing import Optional
from google import genai
from google.genai import types
from langchain_core.prompt_values import ChatPromptValue
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

from researchmate.config import settings


# 1. Grounded Paper Q&A Prompt
PAPER_QA_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are ResearchMate, an academic paper assistant. "
            "Answer only from the supplied paper excerpts. If the excerpts do not "
            "contain the answer, say so clearly. Cite evidence using the page labels "
            "included in the context.",
        ),
        ("human", "Paper excerpts:\n{context}\n\nQuestion: {question}"),
    ]
)


# 2. Structured Paper Summary Prompt (6 core academic sections)
PAPER_SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are ResearchMate, an expert academic research assistant.\n"
            "Analyze the entire research paper text provided and produce a comprehensive, structured academic summary.\n\n"
            "Your summary MUST cover these 6 sections in order:\n"
            "1. **Research Problem**: What core problem, research gap, or motivating question does the paper address?\n"
            "2. **Objective**: What is the primary aim, proposed thesis, or intended contribution?\n"
            "3. **Methodology & Data / Participants**: How was the study conducted, what algorithms, datasets, sample size, or participants were used?\n"
            "4. **Key Findings**: What are the most significant results, discoveries, benchmarks, or empirical findings?\n"
            "5. **Conclusion**: What are the overarching takeaways and broader academic or practical implications?\n"
            "6. **Limitations**: What constraints, threats to validity, or boundaries are acknowledged by the author (use 'the author' for single-author papers, or 'the authors' for multi-author papers)?\n\n"
            "GROUNDING RULES:\n"
            "- Ground every claim strictly in the supplied text. Never hallucinate or extrapolate missing details.\n"
            "- Use 'the author' when the paper has a single author, or 'the authors' when the paper has multiple authors.\n"
            "- If the paper does not state a detail (such as limitations, participants, or datasets), explicitly write: "
            "'Not explicitly stated in the paper.' Do not guess.\n"
            "- Cite evidence for every section using page labels like [Page X] or [Page X, Page Y].",
        ),
        (
            "human",
            "Research Paper: {filename}\n\n"
            "Full Paper Content by Page:\n{paper_text}\n\n"
            "Please generate the 6-section grounded academic summary with page citations.",
        ),
    ]
)


# 3. Key Concepts Extraction Prompt
PAPER_CONCEPTS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are ResearchMate, an expert academic research assistant.\n"
            "Analyze the entire research paper text provided and extract 5–7 distinct key concepts when the paper supports them "
            "(extract fewer only if the paper is too brief to genuinely support 5 distinct concepts).\n\n"
            "CONCEPT SELECTION CRITERIA:\n"
            "- Include both important theoretical ideas (e.g. underlying theories, foundational principles, conceptual frameworks) "
            "and study-specific concepts (e.g. novel architectures, proposed algorithms, domain-specific metrics, bespoke datasets/techniques).\n"
            "- Ensure every concept is distinct: avoid repeating closely related ideas, listing synonyms, or splitting one overarching concept into multiple entries.\n"
            "- Strictly ground all concepts in the supplied text. Do not invent, extrapolate, or import outside concepts not supported by the paper.\n\n"
            "FORMAT FOR EACH CONCEPT:\n"
            "Present each concept with a clear numbered header (e.g. '### 1. [Concept Name]') and the following structure:\n"
            "- **Concept Name**: The precise academic or technical term used in the paper.\n"
            "- **Plain-Language Explanation**: A clear, beginner-friendly explanation in accessible everyday language.\n"
            "- **Why It Matters to This Paper**: The specific role and importance this concept plays in the author's (or authors') research, methodology, or conclusions.\n"
            "- **Page Evidence**: Citation of the page(s) where this concept is introduced, defined, or discussed in the format [Page X] (e.g. [Page 2] or [Page 3, Page 5]).",
        ),
        (
            "human",
            "Research Paper: {filename}\n\n"
            "Full Paper Content by Page:\n{paper_text}\n\n"
            "Please extract 5–7 distinct key concepts (covering theoretical ideas and study-specific concepts) following the required format with page citations.",
        ),
    ]
)


# 4. Intent Detection Prompt (Constrained single-token classification)
INTENT_DETECTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are ResearchMate's intent classifier for an academic paper assistant.\n"
            "Your task is to classify the user's message into EXACTLY ONE of the following 7 intent labels:\n\n"
            "- paper_question: The user is asking a factual, technical, or analytical question about the paper's contents, "
            "methodology, findings, data, or arguments (e.g., 'What problem does this solve?', 'What dataset was used?', 'How does section 3 work?').\n"
            "- summary: The user asks for a broad overview, executive summary, or structured summary of the entire paper "
            "(e.g., 'Summarize this paper', 'Give me an overview', 'Executive summary please').\n"
            "- key_concepts: The user asks to extract, list, or explain the core key concepts, terminology, or theoretical frameworks "
            "(e.g., 'Extract key concepts', 'What are the main concepts?', 'List the key terms in this study').\n"
            "- viva: The user asks for viva preparation, oral defense practice, mock examination, or question drills "
            "(e.g., 'Practice viva', 'Ask me defense questions', 'Prepare me for viva').\n"
            "- presentation: The user asks to create presentation slides, PowerPoint, or slide deck outlines "
            "(e.g., 'Create presentation slides', 'Make a PPT for this paper', 'Generate slides').\n"
            "- flashcards: The user asks to create study flashcards, revision cards, or Q&A memory cards "
            "(e.g., 'Generate flashcards', 'Create study cards', 'Make revision flashcards').\n"
            "- unclear: The message is a greeting, conversational chit-chat, ambiguous, or unrelated to the paper "
            "(e.g., 'hello', 'who are you', 'tell me a joke', 'xyz').\n\n"
            "OUTPUT INSTRUCTION:\n"
            "Respond ONLY with the exact label (paper_question, summary, key_concepts, viva, presentation, flashcards, or unclear).\n"
            "Do NOT include punctuation, explanations, quotes, or markdown.",
        ),
        ("human", "User message: {user_input}"),
    ]
)


# 5. Paper-grounded Flashcards
PAPER_FLASHCARDS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are ResearchMate, an academic study-card author. Generate exactly {count} useful flashcards from the supplied research paper only. "
            "Cover a balanced mix of the research problem, objective, participants/data, method, tools or measures, findings, implications, and limitations when the paper supports them. "
            "Do not repeat a fact, invent details, or ask questions that cannot be answered from the paper. "
            "Keep each question specific and each answer concise (1-3 sentences). "
            "Return only a valid JSON array of objects with string keys question, answer, and citation. "
            "Citations must use page labels present in the input, such as [Page 4] or [Page 4, Page 5].",
        ),
        ("human", "Paper: {filename}\n\nPaper text by page:\n{paper_text}\n\nGenerate {count} distinct flashcards."),
    ]
)


# 5. Interactive Viva Prompts
VIVA_QUESTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a fair academic examiner. Create one clear, open-ended viva question grounded only in the supplied paper. "
            "Begin with a core question about the paper's purpose, contribution, or research problem. Do not ask a question whose answer is absent from the paper. "
            "Return only valid JSON with keys: question, focus, citation. The citation must use a supplied page label such as [Page 2].",
        ),
        ("human", "Paper: {filename}\n\nPaper text by page:\n{paper_text}"),
    ]
)

VIVA_FEEDBACK_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a supportive but academically rigorous viva examiner. Evaluate the student's answer against the supplied paper, not outside knowledge. "
            "Credit correct ideas, identify missing or inaccurate points, and never penalize a student for a detail the paper does not contain. "
            "Use a score from 1 (needs substantial work) to 5 (clear, accurate, well-supported). "
            "Cite page labels from the supplied paper for factual feedback. If evidence is insufficient, say so. "
            "Ask one concise follow-up question grounded in a different relevant aspect when possible. "
            "Return only valid JSON with keys: strengths, improve, feedback, score, citation, next_question, next_focus, next_citation. "
            "All values except score must be strings. Do not use markdown fences.",
        ),
        (
            "human",
            "Paper: {filename}\n\nPaper text by page:\n{paper_text}\n\n"
            "Earlier exchange (for progression only):\n{history}\n\n"
            "Current viva question: {question}\nStudent answer: {answer}\n\n"
            "Follow-up instruction: {final_question_instruction}",
        ),
    ]
)


# 5. Paper Presentation Outline Prompt (Structured JSON for PowerPoint generation)
PAPER_PRESENTATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are ResearchMate, an expert academic presentation designer.\n"
            "Your task is to generate a comprehensive, highly grounded PowerPoint slide outline from the provided research paper.\n\n"
            "PRESENTATION CONFIGURATION:\n"
            "- Target Slide Count: {slide_count} slides\n"
            "- Presentation Duration: {duration}\n"
            "- Target Audience / Technical Level: {audience_level}\n\n"
            "SLIDE STRUCTURE GUIDELINES (adapt to {slide_count} slides):\n"
            "1. Title Slide (Category: 'TITLE'):\n"
            "   - Use a short presentation headline of 2-7 words, not the full long paper title.\n"
            "   - Put the exact full paper title in the subtitle, followed by a concise one-sentence framing only when space allows.\n"
            "   - Include author(s) name(s). Keep the cover sparse and easy to scan.\n"
            "   - IMPORTANT: The Title Slide MUST NOT contain bullet points ('bullet_points': []).\n"
            "2. Problem Statement (Category: 'PROBLEM'): Core challenge, motivating gap, or research question.\n"
            "3. Research Objective (Category: 'OBJECTIVE'): Primary goal, proposed thesis, or intended contribution.\n"
            "4. Methodology & Data (Category: 'METHODOLOGY'): Algorithms, datasets, sample size, or theoretical framework.\n"
            "5. Key Findings (Category: 'FINDINGS'): Principal empirical results, benchmarks, or discoveries.\n"
            "6. Discussion & Implications (Category: 'DISCUSSION'): Practical significance, academic impact, or comparisons.\n"
            "7. Conclusion & Takeaways (Category: 'CONCLUSION'): Overarching conclusions and summary points.\n"
            "8. Limitations & Boundaries (Category: 'LIMITATIONS'): Constraints acknowledged by the author/authors (or state 'Not explicitly stated in the paper').\n"
            "(If more slides are requested, expand Methodology, Key Findings, or Discussion into dedicated sub-slides).\n\n"
            "TEXT FORMATTING RULES (STRICT):\n"
            "- Do NOT use markdown asterisks (no '**' or '*'), backticks, or '#' heading markers in text strings.\n"
            "- For content slide bullet points, use a clean 'Label: Description' format (e.g. 'Method: Multi-head self-attention with 8 heads'). The slide generator will automatically format the leading label natively as bold text in PowerPoint.\n"
            "- Keep bullet points concise, impactful, and presenter-friendly (avoid dense text walls).\n"
            "- Use exactly 3 concise bullet points on most content slides; split a slide if a claim needs more explanation.\n"
            "- Vary the supported layouts across the deck: use 'single_column' for a focused idea or takeaway and 'two_column' for methods, findings, or comparisons that benefit from grouping. Do not use the same layout on every content slide.\n"
            "- Use 'chart' only when chart_data is explicitly supported by reported quantitative findings.\n\n"
            "GROUNDING RULES:\n"
            "- Every factual claim on content slides MUST include a verifiable page citation in the format [Page X] or [Page X, Page Y].\n"
            "- Strictly ground all content in the supplied paper text. Never invent benchmarks, dataset sizes, or findings.\n"
            "- If a detail (such as limitations or sample size) is not mentioned in the paper, explicitly state: 'Not explicitly stated in the paper.'\n\n"
            "OPTIONAL CHARTS (ONLY FOR EMPIRICAL NUMBERS):\n"
            "- ONLY IF the paper explicitly reports quantitative empirical findings with numbers (e.g. percentages, accuracy, sample sizes, benchmarks), include an optional 'chart_data' object on the FINDINGS slide:\n"
            "  \"chart_data\": {{\n"
            "      \"title\": \"Short Chart Title (e.g. Model Accuracy Comparison)\",\n"
            "      \"categories\": [\"Baseline\", \"Ablation\", \"Proposed\"],\n"
            "      \"series_name\": \"Score (%)\",\n"
            "      \"values\": [74.2, 81.0, 89.5]\n"
            "  }}\n"
            "- If the paper does NOT report explicit quantitative numbers, do NOT include chart_data (omit or set to null). NEVER fabricate numbers.\n\n"
            "OUTPUT FORMAT:\n"
            "Return a valid JSON array of slide objects. Do NOT include markdown code fences (```json ... ```) or any preamble or postamble.\n"
            "Each slide object MUST have these exact fields:\n"
            "- \"slide_number\": integer (1 to {slide_count})\n"
            "- \"category\": uppercase category string (e.g. \"TITLE\", \"PROBLEM\", \"OBJECTIVE\", \"METHODOLOGY\", \"FINDINGS\", \"DISCUSSION\", \"CONCLUSION\", \"LIMITATIONS\")\n"
            "- \"title\": concise slide title string (no markdown)\n"
            "- \"subtitle\": optional subtitle or takeaway line (string, no markdown)\n"
            "- \"author\": string for Slide 1 with paper author(s) name(s) (e.g. \"Ashish Vaswani et al.\")\n"
            "- \"bullet_points\": list of 3-5 concise bullet strings for content slides (empty list [] for Slide 1)\n"
            "- \"citation\": string with page citation (e.g. \"[Page 3, Page 4]\" or \"\" for title/conclusion)\n"
            "- \"layout\": optional layout hint: \"single_column\", \"two_column\", or \"chart\"\n"
            "- \"chart_data\": optional chart data object for findings slides (or null)\n"
            "- \"speaker_notes\": 2-3 sentence presenter talking points matching the presentation duration",
        ),
        (
            "human",
            "Research Paper: {filename}\n\n"
            "Full Paper Content by Page:\n{paper_text}\n\n"
            "Please generate the grounded {slide_count}-slide presentation outline as a JSON array.",
        ),
    ]
)


def _build_genai_chain(
    prompt: ChatPromptTemplate,
    timeout: Optional[float] = None,
    thinking_level: Optional[str] = None,
):
    """Create an LCEL chain: prompt -> RunnableLambda(Google GenAI SDK generate_content).

    Executes generation with automatic model fallback (gemini-2.0-flash -> gemini-1.5-flash)
    and robust parameter compatibility to prevent HTTP 400 Bad Request errors.
    """

    def _call_genai_generate(prompt_value: ChatPromptValue) -> str:
        api_key = settings.gemini_api_key
        if not api_key or api_key.strip() in ("", "your_gemini_api_key_here", "replace-with-your-gemini-api-key"):
            raise RuntimeError(
                "Gemini API key is not configured. Please enter your API key in the sidebar or set GEMINI_API_KEY."
            )

        http_options = None
        if timeout is not None:
            http_options = types.HttpOptions(timeout=int(timeout * 1000))

        client = genai.Client(
            api_key=api_key.strip(),
            http_options=http_options,
        )

        messages = prompt_value.to_messages()
        system_instruction = None
        user_texts = []

        for msg in messages:
            if msg.type == "system":
                system_instruction = msg.content
            else:
                user_texts.append(msg.content)

        user_content = "\n\n".join(user_texts)

        # Build prioritized list of models to try.
        # gemini-1.5-flash is widest availability on free-tier keys — always try first.
        primary_model = settings.gemini_model
        candidate_models = []
        for m in ["gemini-1.5-flash", primary_model, "gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"]:
            if m and m not in candidate_models:
                candidate_models.append(m)

        last_error = None
        for model_name in candidate_models:
            try:
                # Only include thinking_config for models that explicitly support reasoning
                thinking_config = None
                if thinking_level and "thinking" in model_name.lower():
                    try:
                        thinking_config = types.ThinkingConfig(
                            thinking_level=thinking_level.upper()
                        )
                    except Exception:
                        thinking_config = None

                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    thinking_config=thinking_config,
                )

                response = client.models.generate_content(
                    model=model_name,
                    contents=user_content,
                    config=config,
                )
                if response and response.text:
                    return response.text
                elif response and hasattr(response, "candidates") and response.candidates:
                    first_candidate = response.candidates[0]
                    if hasattr(first_candidate, "content") and first_candidate.content.parts:
                        part_texts = [p.text for p in first_candidate.content.parts if hasattr(p, "text") and p.text]
                        if part_texts:
                            return "".join(part_texts)
            except Exception as exc:
                last_error = exc
                err_str = str(exc).lower()
                # If it's a model availability error, try the next candidate
                if any(kw in err_str for kw in ("not found", "404", "invalid argument", "unsupported", "400", "model", "deprecated")):
                    continue
                # For rate limits or auth errors, re-raise immediately
                raise

        # Final fallback: use langchain-google-genai wrapper which uses a different HTTP client
        # and may succeed where google-genai SDK v3 fails on certain API versions / keys.
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            lc_llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.4,
            )
            lc_messages = prompt_value.to_messages()
            lc_result = lc_llm.invoke(lc_messages)
            if lc_result and lc_result.content:
                return lc_result.content
        except Exception as lc_exc:
            # If langchain fallback also fails, raise original error
            last_error = last_error or lc_exc

        if last_error:
            raise last_error

        return ""

    return prompt | RunnableLambda(_call_genai_generate)


def build_paper_qa_chain(
    timeout: Optional[float] = None,
    thinking_level: Optional[str] = "low",
):
    """Build LCEL chain for Paper Q&A chat."""
    return _build_genai_chain(
        PAPER_QA_PROMPT, timeout=timeout, thinking_level=thinking_level
    )


def build_paper_summary_chain(
    timeout: Optional[float] = 120.0,
    thinking_level: Optional[str] = "low",
):
    """Build LCEL chain for structured 6-section Paper Summary."""
    return _build_genai_chain(
        PAPER_SUMMARY_PROMPT, timeout=timeout, thinking_level=thinking_level
    )


def build_paper_concepts_chain(
    timeout: Optional[float] = 120.0,
    thinking_level: Optional[str] = "low",
):
    """Build LCEL chain for Key Concepts extraction."""
    return _build_genai_chain(
        PAPER_CONCEPTS_PROMPT, timeout=timeout, thinking_level=thinking_level
    )


def build_intent_detection_chain(
    timeout: Optional[float] = 15.0,
    thinking_level: Optional[str] = "low",
):
    """Build LCEL chain for fast intent classification."""
    return _build_genai_chain(
        INTENT_DETECTION_PROMPT, timeout=timeout, thinking_level=thinking_level
    )


def build_paper_flashcards_chain(
    timeout: Optional[float] = 120.0,
    thinking_level: Optional[str] = "low",
):
    """Build LCEL chain for page-cited paper flashcards."""
    return _build_genai_chain(
        PAPER_FLASHCARDS_PROMPT, timeout=timeout, thinking_level=thinking_level
    )


def build_viva_question_chain(
    timeout: Optional[float] = 90.0,
    thinking_level: Optional[str] = "low",
):
    """Build LCEL chain that creates an initial grounded viva question."""
    return _build_genai_chain(
        VIVA_QUESTION_PROMPT, timeout=timeout, thinking_level=thinking_level
    )


def build_viva_feedback_chain(
    timeout: Optional[float] = 120.0,
    thinking_level: Optional[str] = "low",
):
    """Build LCEL chain that assesses an answer and supplies a follow-up."""
    return _build_genai_chain(
        VIVA_FEEDBACK_PROMPT, timeout=timeout, thinking_level=thinking_level
    )


def build_paper_presentation_chain(
    timeout: Optional[float] = 120.0,
    thinking_level: Optional[str] = "low",
):
    """Build LCEL chain for PowerPoint slide outline generation."""
    return _build_genai_chain(
        PAPER_PRESENTATION_PROMPT, timeout=timeout, thinking_level=thinking_level
    )
