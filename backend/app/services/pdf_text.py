from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class PdfTextError(ValueError):
    code = "invalid_pdf"
    status_code = 422


class PdfTooLargeError(PdfTextError):
    code = "pdf_too_large"
    status_code = 413


class InsufficientPdfTextError(PdfTextError):
    code = "insufficient_pdf_text"


def extract_pdf_text(
    content: bytes,
    *,
    max_upload_bytes: int = 5 * 1024 * 1024,
    max_text_chars: int = 30_000,
    min_text_chars: int = 40,
) -> str:
    if len(content) > max_upload_bytes:
        raise PdfTooLargeError("PDF files must be 5 MiB or smaller")
    try:
        reader = PdfReader(BytesIO(content), strict=False)
        if reader.is_encrypted:
            raise PdfTextError("Encrypted PDFs are not supported")
        parts: list[str] = []
        extracted_chars = 0
        for page in reader.pages:
            text = page.extract_text() or ""
            remaining = max_text_chars - extracted_chars
            if remaining <= 0:
                break
            parts.append(text[:remaining])
            extracted_chars += len(text[:remaining])
    except (PdfReadError, OSError, ValueError) as exc:
        if isinstance(exc, PdfTextError):
            raise
        raise PdfTextError("The uploaded file is not a readable PDF") from exc

    combined = "\n".join(parts).strip()
    if len("".join(combined.split())) < min_text_chars:
        raise InsufficientPdfTextError(
            "The PDF does not contain enough selectable text; scanned PDFs are not supported"
        )
    return combined
