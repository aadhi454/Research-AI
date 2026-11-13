"""PDF intake and page-aware text extraction for ResearchMate AI.

This module uses PyMuPDF (pymupdf) to read PDF documents page by page,
preserving 1-based page numbers for citation and evidence tracking.
"""

from dataclasses import dataclass
import io
from typing import List, Union
import pymupdf


class PDFProcessingError(Exception):
    """Base exception for all PDF extraction issues."""
    pass


class EmptyPDFError(PDFProcessingError):
    """Raised when the uploaded file is empty (0 bytes) or has 0 pages."""
    pass


class PasswordProtectedPDFError(PDFProcessingError):
    """Raised when the PDF is encrypted and requires a password."""
    pass


class InvalidPDFError(PDFProcessingError):
    """Raised when the file is not a valid PDF or has corrupted data."""
    pass


class ScannedPDFError(PDFProcessingError):
    """Raised when a PDF contains only scanned images or textless pages."""
    pass


@dataclass
class ExtractedPage:
    """Stores text extracted from a single PDF page with 1-based page numbering.

    Attributes:
        page_number: Original 1-based page number (1 for the first page).
        text: Plain text extracted from the page.
    """

    page_number: int
    text: str

    @property
    def word_count(self) -> int:
        """Return the number of words on this page."""
        return len(self.text.split())

    @property
    def char_count(self) -> int:
        """Return the total number of characters on this page."""
        return len(self.text)

    def __getitem__(self, item: str):
        """Allow dict-style access (e.g. page['page_number'] or page['text'])."""
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(f"ExtractedPage has no attribute '{item}'")

    def to_dict(self) -> dict:
        """Convert page details into a standard Python dictionary."""
        return {
            "page_number": self.page_number,
            "text": self.text,
            "word_count": self.word_count,
            "char_count": self.char_count,
        }


def extract_pages_from_pdf(
    pdf_input: Union[bytes, io.BytesIO], filename: str = "document.pdf"
) -> List[ExtractedPage]:
    """Extract text from a PDF file page by page, preserving 1-based page numbers.

    Args:
        pdf_input: The raw bytes or a BytesIO stream of the PDF file.
        filename: Name of the uploaded file for descriptive error messages.

    Returns:
        List of ExtractedPage objects with 1-based page numbers.

    Raises:
        EmptyPDFError: If the file is 0 bytes or has 0 pages.
        InvalidPDFError: If the file is corrupted or not a valid PDF.
        PasswordProtectedPDFError: If the PDF is password-protected/encrypted.
        ScannedPDFError: If no extractable digital text is found in the entire PDF.
    """
    # 1. Resolve raw bytes from input
    if hasattr(pdf_input, "getvalue"):
        pdf_bytes = pdf_input.getvalue()
    elif isinstance(pdf_input, bytes):
        pdf_bytes = pdf_input
    elif hasattr(pdf_input, "read"):
        pdf_bytes = pdf_input.read()
    else:
        raise InvalidPDFError(f"'{filename}' could not be read. Please upload a valid PDF file.")

    # 2. Check for empty file (0 bytes)
    if not pdf_bytes or len(pdf_bytes) == 0:
        raise EmptyPDFError(
            f"The uploaded file '{filename}' is empty (0 bytes). Please upload a valid research paper PDF."
        )

    # 3. Attempt to open document with PyMuPDF
    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    except pymupdf.EmptyFileError as exc:
        raise EmptyPDFError(
            f"The file '{filename}' contains no PDF data. Please upload a valid PDF document."
        ) from exc
    except pymupdf.FileDataError as exc:
        raise InvalidPDFError(
            f"Could not read '{filename}' as a PDF. The file may be corrupted, incomplete, or not a PDF."
        ) from exc
    except Exception as exc:
        raise InvalidPDFError(
            f"Could not open '{filename}': {exc}"
        ) from exc

    # 4. Process document pages safely
    try:
        # Check password protection / encryption
        if doc.is_encrypted or doc.needs_pass:
            raise PasswordProtectedPDFError(
                f"'{filename}' is password-protected or encrypted. "
                "ResearchMate AI cannot read password-protected files. "
                "Please remove the password or export an unencrypted copy and try again."
            )

        # Check total page count
        if doc.page_count == 0 or len(doc) == 0:
            raise EmptyPDFError(
                f"The PDF '{filename}' contains 0 pages. Please upload a document with at least one page."
            )

        extracted_pages: List[ExtractedPage] = []
        total_text_length = 0

        # PyMuPDF pages are 0-indexed, but original document pages are 1-based
        for page_index in range(doc.page_count):
            page = doc[page_index]
            page_number = page_index + 1  # 1-based page number
            page_text = page.get_text() or ""

            extracted_pages.append(
                ExtractedPage(
                    page_number=page_number,
                    text=page_text,
                )
            )
            total_text_length += len(page_text.strip())

        # Check if the PDF has any digital text at all across all pages
        if total_text_length == 0:
            raise ScannedPDFError(
                f"No readable digital text could be extracted from '{filename}'. "
                "It appears to be a scanned document or image-only PDF. "
                "Note: ResearchMate AI extracts digital text and does not support OCR "
                "(Optical Character Recognition) yet. Please upload a PDF with selectable text."
            )

        return extracted_pages

    finally:
        doc.close()

