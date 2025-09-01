# extractor.py
from pathlib import Path
from typing import Union
import fitz  # PyMuPDF
from docx import Document


def extract_text_from_pdf(path: Union[str, Path]) -> str:
    """Extracts clean text from a PDF using PyMuPDF (fitz)."""
    doc = fitz.open(str(path))
    texts = []
    for page in doc:
        text = page.get_text().strip()
        if text:
            texts.append(text)
    return "\n\n".join(texts)


def extract_text_from_docx(path: Union[str, Path]) -> str:
    """Extracts clean text from a DOCX file using python-docx."""
    doc = Document(path)
    return "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())


def extract_text(path: Union[str, Path]) -> str:
    """Detects file type and extracts clean text accordingly."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if path.suffix.lower() == ".pdf":
        return extract_text_from_pdf(path)
    
    elif path.suffix.lower() == ".docx":
        return extract_text_from_docx(path)

    else:
        raise ValueError(f"Unsupported file type: {path.suffix} (only .pdf / .docx)")
