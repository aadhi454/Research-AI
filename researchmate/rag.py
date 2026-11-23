"""Grounded Retrieval-Augmented Generation (RAG) module for ResearchMate AI.

This module handles:
1. Splitting extracted PDF text into overlapping chunks with 1-based page metadata.
2. Embedding document chunks with Gemini RETRIEVAL_DOCUMENT embeddings.
3. Storing and querying vector representations in a persistent local ChromaDB collection.
4. Embedding user questions with Gemini RETRIEVAL_QUERY embeddings for vector compatibility.
5. Strict document isolation so retrieval is scoped only to the active uploaded paper.
6. Transparent multi-stage progress tracking with chunk counts and elapsed timing.
7. Verification that partially indexed papers are cleaned up and never treated as complete.
8. Generating answers grounded strictly in retrieved excerpts via LangChain LCEL chain.
"""

import os
import time
from typing import Any, Callable, Dict, List, Optional, Set
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from researchmate.config import settings
from researchmate.pdf import ExtractedPage
from researchmate.prompts import build_paper_qa_chain


class RAGError(Exception):
    """Base exception for RAG pipeline errors."""
    pass


class MissingAPIKeyError(RAGError):
    """Raised when the Gemini API key is missing."""
    pass


class EmbeddingError(RAGError):
    """Raised when embedding generation fails or times out."""
    pass


class RetrievalError(RAGError):
    """Raised when vector search fails."""
    pass


class GenerationError(RAGError):
    """Raised when answer synthesis fails or times out."""
    pass


def format_actionable_error(exc: Exception, api_key: Optional[str] = None) -> str:
    """Format exceptions into beginner-friendly, actionable diagnostic messages.

    Ensures the raw API key is never printed or displayed in UI or logs.
    """
    msg = str(exc)
    # Mask API key if it appears anywhere in exception details
    key_to_mask = api_key or settings.gemini_api_key
    if key_to_mask and len(key_to_mask) > 4 and key_to_mask in msg:
        msg = msg.replace(key_to_mask, "[REDACTED_API_KEY]")

    msg_lower = msg.lower()

    if "api key is not configured" in msg_lower or "missingapikey" in msg_lower:
        return (
            "Gemini API key is required. Please enter your API key in the sidebar under 'AI Configuration', "
            "or set GEMINI_API_KEY in your Streamlit Cloud Secrets / .env file."
        )
    if "api_key_invalid" in msg_lower or "api key not valid" in msg_lower or ("invalid_argument" in msg_lower and "key" in msg_lower):
        return (
            "Invalid Gemini API key. Please check your GEMINI_API_KEY and verify that it is active in Google AI Studio (https://aistudio.google.com/)."
        )
    if "permission_denied" in msg_lower:
        return (
            "Permission denied by Google AI Studio. Please verify that your API key has access to Gemini models and has billing or quota configured."
        )
    if "deadline" in msg_lower or "timed out" in msg_lower or "timeout" in msg_lower or "504" in msg_lower:
        return (
            "Gemini request timed out (504 Deadline Exceeded). "
            "The model took too long to generate a response. Please try submitting again."
        )
    if "resource_exhausted" in msg_lower or "429" in msg_lower or "quota" in msg_lower:
        return (
            "Gemini API rate limit or quota exceeded. Please wait a moment before trying again, or check your quota in Google AI Studio."
        )
    if "not found" in msg_lower or "404" in msg_lower:
        return (
            "The requested AI model was not found or is unsupported for this API version. Research AI automatically switches to gemini-2.0-flash."
        )
    if "dns" in msg_lower or "nodename" in msg_lower or "503" in msg_lower or "connecterror" in msg_lower or "connectionerror" in msg_lower:
        return (
            "Unable to connect to Google Gemini services. Please verify your internet connection, proxy, or firewall settings."
        )

    return f"Service error: {msg}"


class GeminiRetrievalEmbeddings(Embeddings):
    """Gemini embedding function enforcing appropriate retrieval task types:
    - RETRIEVAL_DOCUMENT when embedding document passages for ChromaDB storage.
    - RETRIEVAL_QUERY when embedding the user query for similarity search.

    Configured with fallback to stable models and clean timeout handling.
    """

    def __init__(self, model: str, google_api_key: str, timeout: float = 60.0):
        # Automatically map non-existent or deprecated embedding models
        if not model or "gemini-embedding" in model or "embedding-001" in model:
            model = "models/text-embedding-004"
        elif not model.startswith("models/"):
            model = f"models/{model}"

        self.model = model
        self.google_api_key = google_api_key
        self.timeout = timeout
        request_opts = {"timeout": timeout}

        # Document embedder with RETRIEVAL_DOCUMENT
        self._doc_embedder = GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=google_api_key,
            task_type="RETRIEVAL_DOCUMENT",
            request_options=request_opts,
        )
        # Query embedder with RETRIEVAL_QUERY
        self._query_embedder = GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=google_api_key,
            task_type="RETRIEVAL_QUERY",
            request_options=request_opts,
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed document chunks using RETRIEVAL_DOCUMENT task type."""
        try:
            return self._doc_embedder.embed_documents(texts)
        except Exception as exc:
            # Fallback 1: without task_type
            try:
                fallback = GoogleGenerativeAIEmbeddings(
                    model=self.model,
                    google_api_key=self.google_api_key,
                    request_options={"timeout": self.timeout},
                )
                return fallback.embed_documents(texts)
            except Exception:
                # Fallback 2: using models/text-embedding-004 directly
                try:
                    fallback_default = GoogleGenerativeAIEmbeddings(
                        model="models/text-embedding-004",
                        google_api_key=self.google_api_key,
                        request_options={"timeout": self.timeout},
                    )
                    return fallback_default.embed_documents(texts)
                except Exception as inner_exc:
                    actionable = format_actionable_error(inner_exc, self.google_api_key)
                    raise EmbeddingError(actionable) from exc

    def embed_query(self, text: str) -> List[float]:
        """Embed user query using RETRIEVAL_QUERY task type."""
        try:
            return self._query_embedder.embed_query(text)
        except Exception as exc:
            # Fallback 1: without task_type
            try:
                fallback = GoogleGenerativeAIEmbeddings(
                    model=self.model,
                    google_api_key=self.google_api_key,
                    request_options={"timeout": self.timeout},
                )
                return fallback.embed_query(text)
            except Exception:
                # Fallback 2: using models/text-embedding-004 directly
                try:
                    fallback_default = GoogleGenerativeAIEmbeddings(
                        model="models/text-embedding-004",
                        google_api_key=self.google_api_key,
                        request_options={"timeout": self.timeout},
                    )
                    return fallback_default.embed_query(text)
                except Exception as inner_exc:
                    actionable = format_actionable_error(inner_exc, self.google_api_key)
                    raise EmbeddingError(actionable) from exc


def split_pages_into_chunks(
    pages: List[ExtractedPage],
    filename: str,
    chunk_size: int = 800,
    chunk_overlap: int = 150,
) -> List[Document]:
    """Split extracted PDF pages into overlapping chunks while preserving metadata.

    Args:
        pages: List of ExtractedPage objects with 1-based page numbers.
        filename: Name of the research paper PDF.
        chunk_size: Target maximum character length per chunk.
        chunk_overlap: Overlapping characters between consecutive chunks.

    Returns:
        List of LangChain Document objects with page, filename, and chunk_index metadata.
    """
    documents: List[Document] = []
    chunk_index = 0

    for page in pages:
        cleaned_text = page.text.strip()
        if not cleaned_text:
            continue

        text_len = len(cleaned_text)
        start = 0

        while start < text_len:
            end = start + chunk_size

            if end >= text_len:
                chunk = cleaned_text[start:].strip()
                if chunk:
                    documents.append(
                        Document(
                            page_content=chunk,
                            metadata={
                                "page": page.page_number,  # 1-based original page number
                                "filename": filename,
                                "chunk_index": chunk_index,
                            },
                        )
                    )
                    chunk_index += 1
                break

            # Find natural breakpoint: paragraph > line break > sentence end > space
            breakpoint = -1
            for sep in ["\n\n", "\n", ". ", " "]:
                pos = cleaned_text.rfind(sep, start + chunk_overlap, end)
                if pos != -1:
                    breakpoint = pos + len(sep)
                    break

            if breakpoint == -1:
                breakpoint = end

            chunk = cleaned_text[start:breakpoint].strip()
            if chunk:
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "page": page.page_number,
                            "filename": filename,
                            "chunk_index": chunk_index,
                        },
                    )
                )
                chunk_index += 1

            start = max(start + 1, breakpoint - chunk_overlap)

    return documents


def get_embedding_function(api_key: Optional[str] = None, timeout: float = 60.0) -> Embeddings:
    """Instantiate the Gemini retrieval embedding function.

    Args:
        api_key: Optional Gemini API key; defaults to settings.gemini_api_key.
        timeout: Request timeout in seconds.

    Returns:
        GeminiRetrievalEmbeddings instance.

    Raises:
        MissingAPIKeyError: If no valid API key is found.
    """
    key = api_key or settings.gemini_api_key
    if not key or key.strip() in ("", "your_gemini_api_key_here"):
        raise MissingAPIKeyError(
            "Gemini API key is not configured. Please add GEMINI_API_KEY to your local .env file."
        )

    return GeminiRetrievalEmbeddings(
        model=settings.gemini_embedding_model,
        google_api_key=key,
        timeout=timeout,
    )


def get_chroma_client() -> chromadb.api.ClientAPI:
    """Create or return a ChromaDB client using CHROMA_DIR with in-memory fallback for cloud environments."""
    persist_dir = settings.chroma_dir or "./chroma_db"
    try:
        os.makedirs(persist_dir, exist_ok=True)
        return chromadb.PersistentClient(
            path=persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    except Exception:
        # Fallback to in-memory EphemeralClient for cloud sandboxes without persistent write permissions
        return chromadb.EphemeralClient(
            settings=ChromaSettings(anonymized_telemetry=False)
        )


def get_vectorstore(
    embedding_function: Optional[Embeddings] = None,
    collection_name: str = "researchmate_papers",
) -> Chroma:
    """Initialize or load the local persistent Chroma vector store."""
    ef = embedding_function or get_embedding_function()
    client = get_chroma_client()
    return Chroma(
        collection_name=collection_name,
        embedding_function=ef,
        client=client,
    )


def is_paper_fully_indexed(
    filename: str,
    pages: Optional[List[ExtractedPage]] = None,
    vectorstore: Optional[Chroma] = None,
) -> bool:
    """Check if the paper is fully and completely indexed in ChromaDB.

    If pages are supplied, computes the exact expected chunk IDs and verifies that
    ALL expected chunks are stored. If an indexing attempt was previously interrupted
    midway, this returns False so partial indexing is never treated as complete.

    Args:
        filename: Name of the paper file.
        pages: Optional list of ExtractedPage objects.
        vectorstore: Optional Chroma vector store instance.

    Returns:
        True if all expected chunks are verified in the vector store; False otherwise.
    """
    try:
        vs = vectorstore or get_vectorstore()
        existing = vs.get(where={"filename": filename})
        existing_ids: Set[str] = set(existing.get("ids", []))

        if not existing_ids:
            return False

        if pages:
            expected_chunks = split_pages_into_chunks(pages, filename)
            expected_ids = {
                f"{doc.metadata['filename']}_p{doc.metadata['page']}_c{doc.metadata['chunk_index']}"
                for doc in expected_chunks
            }
            # Only return True if every expected chunk ID is present
            return existing_ids == expected_ids

        return len(existing_ids) > 0
    except Exception:
        return False


# Backward-compatible alias
is_paper_indexed = is_paper_fully_indexed


def index_paper_chunks(
    pages: List[ExtractedPage],
    filename: str,
    vectorstore: Optional[Chroma] = None,
    force_reindex: bool = False,
    on_progress: Optional[Callable[[str, str, float, Optional[Dict[str, Any]]], None]] = None,
    start_time: Optional[float] = None,
) -> int:
    """Split and embed a research paper into ChromaDB with deduplication and progress updates.

    If the paper is already fully indexed and force_reindex is False, embedding is skipped.
    If partial/incomplete indexing from a previous aborted attempt is detected, the partial
    chunks are purged before clean re-indexing.

    Args:
        pages: List of ExtractedPage objects.
        filename: Name of the uploaded PDF file.
        vectorstore: Optional Chroma vector store instance.
        force_reindex: If True, re-indexes even if already verified.
        on_progress: Optional progress callback (stage, message, elapsed_time, extra_info).
        start_time: Optional reference start timestamp for elapsed time tracking.

    Returns:
        Number of chunks indexed.
    """
    t0 = start_time or time.perf_counter()

    def report(stage: str, msg: str, extra: Optional[Dict[str, Any]] = None):
        if on_progress:
            elapsed = time.perf_counter() - t0
            on_progress(stage, msg, elapsed, extra or {})

    if not pages:
        raise RAGError(f"No pages extracted from '{filename}' to index.")

    vs = vectorstore or get_vectorstore()

    # 1. Check existing index state
    existing = vs.get(where={"filename": filename})
    existing_ids = set(existing.get("ids", []))

    # Compute expected chunks
    report("chunking", f"Stage 2/5 · Splitting {len(pages)} pages into overlapping chunks...")
    documents = split_pages_into_chunks(pages, filename)
    if not documents:
        raise RAGError(f"No readable text content found in '{filename}' to generate chunks.")

    expected_ids = {
        f"{doc.metadata['filename']}_p{doc.metadata['page']}_c{doc.metadata['chunk_index']}"
        for doc in documents
    }
    chunk_count = len(documents)
    report(
        "chunking",
        f"Stage 2/5 · Created {chunk_count} overlapping chunks with 1-based page metadata.",
        {"chunk_count": chunk_count},
    )

    # Check if already fully indexed
    if not force_reindex and existing_ids == expected_ids:
        report(
            "index_check",
            f"Stage 3/5 · Paper is already fully indexed in ChromaDB ({chunk_count} chunks verified). Skipping embedding.",
            {"chunk_count": chunk_count, "skipped_embedding": True},
        )
        return chunk_count

    # If partial chunks exist from a previously interrupted attempt, purge them first
    if existing_ids:
        report(
            "cleanup",
            f"Detected incomplete indexing ({len(existing_ids)}/{chunk_count} chunks). Purging partial index before clean re-embedding...",
            {"partial_count": len(existing_ids)},
        )
        vs.delete(ids=list(existing_ids))

    # 2. Embed and store all chunks
    chunk_ids = [
        f"{doc.metadata['filename']}_p{doc.metadata['page']}_c{doc.metadata['chunk_index']}"
        for doc in documents
    ]

    report(
        "embedding",
        f"Stage 3/5 · Embedding and storing {chunk_count} chunks with Gemini ({settings.gemini_embedding_model})...",
        {"chunk_count": chunk_count},
    )

    t_emb_start = time.perf_counter()
    try:
        vs.add_documents(documents, ids=chunk_ids)
    except Exception as exc:
        actionable = format_actionable_error(exc)
        raise EmbeddingError(f"Embedding failed: {actionable}") from exc

    emb_duration = time.perf_counter() - t_emb_start
    report(
        "embedding",
        f"Stage 3/5 · Successfully embedded and indexed {chunk_count} chunks in ChromaDB ({emb_duration:.1f}s).",
        {"chunk_count": chunk_count, "embedding_duration": emb_duration},
    )

    return chunk_count


def retrieve_relevant_chunks(
    query: str,
    filename: str,
    k: int = 4,
    vectorstore: Optional[Chroma] = None,
) -> List[Document]:
    """Retrieve top-k relevant chunks scoped strictly to the specified paper.

    Args:
        query: The user question.
        filename: The active paper filename to scope retrieval.
        k: Maximum number of relevant chunks to retrieve.
        vectorstore: Optional Chroma instance.

    Returns:
        List of relevant Document objects from the target paper.
    """
    vs = vectorstore or get_vectorstore()

    try:
        results = vs.similarity_search(
            query=query,
            k=k,
            filter={"filename": filename},
        )
        return results
    except Exception as exc:
        actionable = format_actionable_error(exc)
        raise RetrievalError(f"Vector retrieval failed: {actionable}") from exc


def format_context_for_prompt(chunks: List[Document]) -> str:
    """Format retrieved document chunks with clear page labels for LLM context."""
    if not chunks:
        return ""

    formatted_sections = []
    for chunk in chunks:
        page_num = chunk.metadata.get("page", "?")
        passage = f"[Page {page_num}]:\n{chunk.page_content.strip()}"
        formatted_sections.append(passage)

    return "\n\n---\n\n".join(formatted_sections)


def answer_paper_question(
    question: str,
    filename: str,
    pages: Optional[List[ExtractedPage]] = None,
    k: int = 4,
    vectorstore: Optional[Chroma] = None,
    on_progress: Optional[Callable[[str, str, float, Optional[Dict[str, Any]]], None]] = None,
) -> Dict[str, Any]:
    """Execute the full Grounded RAG workflow with granular stage progress tracking:
    1. Check ChromaDB paper index status (Stage 1).
    2. Split pages into overlapping chunks (Stage 2, if unindexed).
    3. Embed and store chunks with Gemini RETRIEVAL_DOCUMENT (Stage 3, if unindexed).
    4. Retrieve relevant excerpts scoped to this paper using RETRIEVAL_QUERY (Stage 4).
    5. Synthesize grounded answer via Gemini LCEL chain with timeout (Stage 5).

    Returns:
        Dictionary containing 'answer', 'sources' (list of Document), and 'context'.
    """
    start_time = time.perf_counter()

    def report(stage: str, msg: str, extra: Optional[Dict[str, Any]] = None):
        if on_progress:
            elapsed = time.perf_counter() - start_time
            on_progress(stage, msg, elapsed, extra or {})

    vs = vectorstore or get_vectorstore()

    # Stage 1: Check paper index
    report("check_index", f"Stage 1/5 · Checking ChromaDB index for '{filename}'...")
    fully_indexed = is_paper_fully_indexed(filename, pages=pages, vectorstore=vs)

    if not fully_indexed:
        if not pages:
            raise RAGError(f"Paper '{filename}' is not indexed and no page data was supplied.")
        # Stages 2 & 3: Chunk and embed
        index_paper_chunks(
            pages=pages,
            filename=filename,
            vectorstore=vs,
            force_reindex=False,
            on_progress=on_progress,
            start_time=start_time,
        )
    else:
        # Retrieve existing count for reporting
        existing = vs.get(where={"filename": filename})
        chunk_count = len(existing.get("ids", []))
        report(
            "check_index",
            f"Stage 1/5 · Paper is already fully indexed in ChromaDB ({chunk_count} chunks verified). Skipping embedding.",
            {"chunk_count": chunk_count, "skipped_embedding": True},
        )

    # Stage 4: Retrieve relevant passages
    report("retrieval", f"Stage 4/5 · Retrieving top {k} relevant passages from '{filename}'...")
    chunks = retrieve_relevant_chunks(query=question, filename=filename, k=k, vectorstore=vs)

    if not chunks:
        report("retrieval", "Stage 4/5 · No matching passages found in the paper.")
        return {
            "answer": "The paper excerpts retrieved do not contain sufficient evidence to answer this question.",
            "sources": [],
            "context": "",
        }

    unique_pages = sorted(list(set(c.metadata.get("page", 1) for c in chunks)))
    pages_str = ", ".join(f"p.{p}" for p in unique_pages)
    report(
        "retrieval",
        f"Stage 4/5 · Retrieved {len(chunks)} relevant excerpts across {pages_str}.",
        {"source_count": len(chunks), "pages": unique_pages},
    )

    # Stage 5: Format context and generate answer
    context = format_context_for_prompt(chunks)
    report("generation", f"Stage 5/5 · Synthesizing grounded answer using Gemini ({settings.gemini_model})...")

    chain = build_paper_qa_chain()
    try:
        answer = chain.invoke({"context": context, "question": question})
    except Exception as exc:
        actionable = format_actionable_error(exc)
        raise GenerationError(actionable) from exc

    total_elapsed = time.perf_counter() - start_time
    report(
        "complete",
        f"Complete · Grounded answer synthesized in {total_elapsed:.1f}s.",
        {"total_elapsed": total_elapsed},
    )

    return {
        "answer": answer,
        "sources": chunks,
        "context": context,
        "total_elapsed": total_elapsed,
    }
