from io import BytesIO

import pytest
from pypdf import PdfWriter

from app.services.pdf_text import InsufficientPdfTextError, PdfTooLargeError, extract_pdf_text


def blank_pdf() -> bytes:
    output = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(output)
    return output.getvalue()


def test_image_only_pdf_is_rejected():
    with pytest.raises(InsufficientPdfTextError):
        extract_pdf_text(blank_pdf())


def test_oversized_pdf_is_rejected_before_parsing():
    with pytest.raises(PdfTooLargeError):
        extract_pdf_text(b"%PDF" + b"x" * 101, max_upload_bytes=100)
