from pathlib import Path
from extractor import extract_text
from chunker import (
    chunk_fixed,
    chunk_by_sentences,
    chunk_by_paragraphs
)
from embedder import get_embedding
from database import insert_chunk
from tqdm import tqdm


# 1. Load and validate file
def load_file(path: Path) -> str:
    print(f"📄 Reading file: {path.name}")
    if not path.exists():
        raise FileNotFoundError(f"❌ File not found: {path}")
    return extract_text(path)


# 2. Choose chunking strategy
def split_text(text: str, strategy: str) -> list[str]:
    print(f"✂️ Splitting text using strategy: {strategy}")
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
    print(f"🧠 Generating embeddings for {len(chunks)} chunks...")
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
    print(f"💾 Saving {len(chunk_data)} chunks to DB...")
    for item in tqdm(chunk_data):
        insert_chunk(
            chunk_text=item["text"],
            embedding=item["embedding"],
            filename=filename,
            strategy=strategy
        )


# 5. Orchestration
def process_file(path: Path, strategy: str = "fixed"):
    try:
        text = load_file(path)
        chunks = split_text(text, strategy)
        embeddings = embed_chunks(chunks)
        save_chunks(embeddings, filename=path.name, strategy=strategy)
        print("✅ Done!")
    except Exception as e:
        print(f"❌ Error: {e}")


# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="Path to .pdf or .docx file")
    parser.add_argument("--strategy", choices=["fixed", "sentence", "paragraph"], default="fixed")
    args = parser.parse_args()

    process_file(Path(args.file), args.strategy)
