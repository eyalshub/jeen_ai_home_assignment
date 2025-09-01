# test_extractor.py

from pathlib import Path
from extractor import extract_text


def test_extract_text_from_pdf():
    sample = Path("samples/file-sample_150kB.pdf")
    assert sample.exists(), "Missing test file: sample.pdf"
    text = extract_text(sample)
    assert isinstance(text, str)
    assert len(text.strip()) > 0
    print("\n✅ PDF extraction successful")
    print("\n--- Extracted PDF Text ---\n")
    print(text[:1000])  

def test_extract_text_from_docx():
    sample = Path("samples/file-sample_500kB.docx")
    assert sample.exists(), "Missing test file: sample.docx"
    text = extract_text(sample)
    assert isinstance(text, str)
    assert len(text.strip()) > 0
    print("\n✅ DOCX extraction successful")
    print("\n--- Extracted PDF Text ---\n")
    print(text[:1000])  


if __name__ == "__main__":
    test_extract_text_from_pdf()
    test_extract_text_from_docx()
