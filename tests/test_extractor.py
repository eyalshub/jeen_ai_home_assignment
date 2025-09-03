# tests/test_extractor.py

from pathlib import Path
import pytest
from helper.extractor import extract_text

PDF_SAMPLE = Path("samples/file-sample_150kB.pdf")
DOCX_SAMPLE = Path("samples/file-sample_500kB.docx")


@pytest.mark.skipif(not PDF_SAMPLE.exists(), reason="Missing test file: file-sample_150kB.pdf")
def test_extract_text_from_pdf():
    text = extract_text(PDF_SAMPLE)
    assert isinstance(text, str), "❌ PDF output is not a string"
    assert len(text.strip()) > 0, "❌ PDF extraction returned empty text"


@pytest.mark.skipif(not DOCX_SAMPLE.exists(), reason="Missing test file: file-sample_500kB.docx")
def test_extract_text_from_docx():
    text = extract_text(DOCX_SAMPLE)
    assert isinstance(text, str), "❌ DOCX output is not a string"
    assert len(text.strip()) > 0, "❌ DOCX extraction returned empty text"
