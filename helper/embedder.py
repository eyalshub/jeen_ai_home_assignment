# helper/embedder.py

import os
from typing import List
import google.generativeai as genai
from dotenv import load_dotenv



# Load GEMINI_API_KEY from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise EnvironmentError("❌ Missing GEMINI_API_KEY in .env file")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Default model
DEFAULT_MODEL = "models/text-embedding-004"
EMBEDDING_DIM = 768




def get_embedding(text: str, model: str = DEFAULT_MODEL) -> List[float]:
    """
    Generates a text embedding using Google Gemini API.
    Returns a list of floats with length 768 (for model=text-embedding-004).
    Raises:
        ValueError: on empty text or invalid embedding response
        RuntimeError: on API/SDK/network failures
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text is empty – cannot generate embedding.")


    try:
        res = genai.embed_content(
            model=model,
            content=text,
            task_type="retrieval_document"
        )
        embedding = res.get("embedding")
        if not embedding or len(embedding) != EMBEDDING_DIM:
            raise ValueError("Invalid embedding response from Gemini.")
        return embedding

    except Exception as e:
        raise RuntimeError(f"Embedding generation failed: {e}")


def l2_normalize(vec: List[float]) -> List[float]:
    """
    Applies L2 normalization to a vector (unit norm).
    Useful for cosine similarity consistency.
    """
    norm = sum(x * x for x in vec) ** 0.5 or 1.0
    return [x / norm for x in vec]