# index_documents.py
from pathlib import Path
from helper.extractor import extract_text
from helper.chunker import (
    chunk_fixed,
    chunk_by_sentences,
    chunk_by_paragraphs
)
from helper.embedder import get_embedding
from helper.database import insert_chunk
from tqdm import tqdm
from logging import basicConfig, getLogger, INFO
import sys


basicConfig(level=INFO)
log = getLogger(__name__)



# 1. Load and validate file
def load_file(path: Path) -> str:
    """
    Load and extract clean text from a supported document.

    Parameters
    ----------
    path : Path
        Path to the .pdf or .docx file.

    Returns
    -------
    str
        Cleaned full text.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    log.info(f"📄 Reading file: {path.name}")
    if not path.exists():
        raise FileNotFoundError(f"❌ File not found: {path}")
    return extract_text(path)


# 2. Choose chunking strategy
def split_text(text: str, strategy: str) -> list[str]:
    """
    Split text using the selected chunking strategy.

    Parameters
    ----------
    text : str
        Full document text.
    strategy : str
        One of {"fixed", "sentence", "paragraph"}.

    Returns
    -------
    list[str]
        List of text chunks.

    Raises
    ------
    ValueError
        If the strategy is unknown.
    """
    log.info(f"✂️ Splitting text using strategy: {strategy}")
    if strategy == "fixed":
        return chunk_fixed(text)
    elif strategy == "sentence":
        return chunk_by_sentences(text)
    elif strategy == "paragraph":
        return chunk_by_paragraphs(text)
    else:
        raise ValueError(f"❌ Unknown strategy: {strategy}")


# 3. Embed each chunk with Gemini
def embed_chunks(chunks: list[str]) -> list[dict]:
    """
    Generate embeddings for each chunk using Gemini API.

    Parameters
    ----------
    chunks : list[str]
        List of text chunks.

    Returns
    -------
    list[dict]
        List of dicts with 'text' and 'embedding'.
    """
    log.info(f"🧠 Generating embeddings for {len(chunks)} chunks...")
    result = []
    for chunk in tqdm(chunks):
        try:
            embedding = get_embedding(chunk)
            result.append({"text": chunk, "embedding": embedding})
        except Exception as e:
            print(f"⚠️ Failed to embed chunk: {e}")
    return result


# 4. Save to PostgreSQL
def save_chunks(chunk_data: list[dict], filename: str, strategy: str):
    """
    Insert chunks and their embeddings into the database.

    Parameters
    ----------
    chunk_data : list[dict]
        List of {"text": ..., "embedding": ...}.
    filename : str
        Original file name.
    strategy : str
        Chunking strategy used.
    """
    log.info(f"💾 Saving {len(chunk_data)} chunks to DB...")
    for item in tqdm(chunk_data):
        insert_chunk(
            chunk_text=item["text"],
            embedding=item["embedding"],
            filename=filename,
            strategy=strategy
        )


# 5. Orchestration
def process_file(path: Path, strategy: str = "fixed"):
    """
    Full pipeline: load file, split, embed, save.

    Parameters
    ----------
    path : Path
        File path to process.
    strategy : str
        Chunking strategy to apply.
    """
    try:
        text = load_file(path)
        chunks = split_text(text, strategy)
        chunks = [c for c in chunks if c.strip()]

        embeddings = embed_chunks(chunks)
        save_chunks(embeddings, filename=path.name, strategy=strategy)
        log.info("✅ Done!")
    except Exception as e:
        log.exception(f"❌ Fatal error during processing: {e}")


# CLI entrypoint
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="Path to .pdf or .docx file")
    parser.add_argument("--strategy", choices=["fixed", "sentence", "paragraph"], default="fixed")
    args = parser.parse_args()

    try:
        process_file(Path(args.file), args.strategy)
    except Exception as e:
        log.error("❌ Failed to complete indexing.")
        sys.exit(1)
