# helper/extractor.py
from pathlib import Path
from typing import Union
import fitz  # PyMuPDF
from docx import Document


def extract_text_from_pdf(path: Union[str, Path]) -> str:
    """Extracts clean text from a PDF using PyMuPDF (fitz)."""
    try:
        doc = fitz.open(str(path))
    except Exception as e:
        raise RuntimeError(f"❌ Failed to open PDF file '{path}': {e}")

    texts = []
    for page_num, page in enumerate(doc, start=1):
        try:
            text = page.get_text().strip()
            if text:
                texts.append(text)
        except Exception as e:
            raise RuntimeError(f"❌ Failed to extract text from page {page_num} in '{path}': {e}")

    return "\n\n".join(texts)


def extract_text_from_docx(path: Union[str, Path]) -> str:
    """Extracts clean text from a DOCX file using python-docx."""
    try:
        doc = Document(path)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to open DOCX file '{path}': {e}")

    try:
        return "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        raise RuntimeError(f"❌ Failed to extract text from DOCX file '{path}': {e}")




def extract_text(path: Union[str, Path]) -> str:
    """Detects file type and extracts clean text accordingly."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"❌ File not found: {path}")

    if path.suffix.lower() == ".pdf":
        return extract_text_from_pdf(path)

    elif path.suffix.lower() == ".docx":
        return extract_text_from_docx(path)

    else:
        raise ValueError(f"❌ Unsupported file type: {path.suffix} (only .pdf / .docx)")
