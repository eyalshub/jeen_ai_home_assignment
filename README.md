# 🧠 Jeen.ai Home Assignment – Semantic Search RAG Simulation

## 🔍 Introduction

As part of the Jeen.ai Home Assignment, I chose to design and implement a **modular, testable, and extensible RAG pipeline** to enable easy future enhancements and experimentation.

### 💡 Key Design Decisions

- 🔧 **Modular Architecture** – Each component (e.g., chunking, embedding, database) is isolated and swappable.
- 🧪 **Full Test Coverage** – Unit tests were written for all core functionalities to ensure correctness and stability.
- 🐳 **Dockerized Environment** – PostgreSQL with `pgvector` runs inside Docker for easy setup and portability across machines.

> 🎯 The goal was to build a clean, maintainable, and production-ready solution — not just a proof-of-concept script.

---

This project implements a minimal **RAG (Retrieval-Augmented Generation)** pipeline using:

- 🧠 **Gemini API** for embedding generation  
- 🗃️ **PostgreSQL + pgvector** for vector storage and semantic search

It consists of two main scripts:

- `index_documents.py` – Extracts text from documents, chunks it, generates embeddings, and stores them in the database.
- `search_documents.py` – Embeds a user query and retrieves the top 5 most semantically similar chunks using cosine similarity.


> 📁 _This project uses CLI only – no UI or graphical components included._

---

## 📦 Features

- ✅ **Embedding generation with Gemini API**  
  Leverages Google's Gemini model to create high-dimensional vector representations of text.

- ✅ **Semantic search with PostgreSQL + pgvector**  
  Uses `pgvector` extension for efficient similarity search via cosine distance.

- ✅ **Flexible chunking strategies**  
  Supports:
  - `fixed` – splits by fixed word count  
  - `sentence` – splits by sentence boundaries  
  - `paragraph` – splits by paragraph markers

- ✅ **Secure configuration**  
  Environment variables (API keys, DB credentials) are stored safely in a `.env` file.

- ✅ **Robust testing**  
  Includes over 10 edge-case unit tests written with `pytest` for confidence in core logic.

- ✅ **Clean, modular codebase**  
  Organized into logical components (`embedder`, `chunker`, `database`, etc.) for easy maintenance and extension.

---
## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your_username/jeen_ai_home_assignment.git
cd jeen_ai_home_assignment

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On Mac/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

```env
# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# PostgreSQL
POSTGRES_DB=jeen_ai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

> ⚠️ **Important:** Make sure `.env` is listed in your `.gitignore`.

---

## 🧪 Run Tests

To run unit tests with verbose output:

```bash
pytest test_search_documents.py -v
```

This will run all 10+ test cases, including:

- Embedding-based similarity sorting  
- Top-K result limiting  
- Filtering by `filename` and `split_strategy`  
- Score range validation  
- Handling of edge cases like blank queries or empty database

---

## 🚀 Run the Pipeline

### 1. Index a document

```bash
python index_documents.py samples/sample.docx fixed
```

- Supported formats: `.docx`, `.pdf`
- Supported chunking strategies:
  - `fixed`
  - `sentence`
  - `paragraph`

### 2. Search documents

Use inside Python:

```python
from search_documents import search_documents

results = search_documents("What is semantic search?")
for r in results:
    print(r["chunk_text"], "→ score:", r["score"])
```

---

## 📁 Project Structure

```
.
├── index_documents.py
├── search_documents.py
├── embedder.py
├── database.py
├── extractor.py
├── chunker.py
├── test_search_documents.py
├── samples/
├── .env             # Not tracked by Git
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🛡️ Security

- ✅ Environment variables are stored in a `.env` file (excluded from Git)
- ✅ API keys and DB credentials are never exposed in code
- ✅ Secure handling of external API calls (Gemini)

---

## 🙌 Credits

Developed by **Eyal Shubeli**  
_As part of the Jeen.ai AI Solutions Engineer Home Assignment – Stage 2._

Includes:

- Chunk-based document indexing  
- Embedding generation using Google Gemini API  
- Cosine similarity search using `pgvector`  
- End-to-end unit testing with `pytest`  

📘 Example Usage
🧾 Step 1: Prepare a sample document

Save your document (e.g., sample.docx) inside the samples/ folder.

samples/
└── sample.docx   # Contains 2–3 paragraphs of educational content


Example contents for sample.docx:

Semantic search is a powerful technique that enables machines to understand the meaning behind words rather than relying solely on keyword matching.
By using embeddings, large language models and vector databases can represent text as high-dimensional vectors.
This approach powers recommendation systems, chatbots, and modern document search engines.

🧠 Step 2: Index the document

Run the following script to chunk the document and save it to the database:

python index_documents.py samples/sample.docx --strategy fixed


✅ Example output:

📄 Reading file: sample.docx
✂️ Splitting text using strategy: fixed
🧠 Generating embeddings for 2 chunks...
💾 Saving 2 chunks to DB...
✅ Done!

🔍 Step 3: Run a semantic search query

You can now search semantically using a Python script or an interactive shell:

from search_documents import search_documents

results = search_documents("What is semantic search?")
for r in results:
    print(r["chunk_text"], round(r["score"], 3))


🧪 Example output:

Semantic search is a powerful technique...                    0.813
...The effectiveness of such systems relies...               0.792
Chunk with sim 0.99                                          -0.002
Chunk with sim 0.95                                          -0.002
Chunk with sim 0.75                                          -0.002

🧼 Resetting the database (optional)

If you want to clean the database between runs (for testing/demo):

from database import get_connection
with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM chunks;")
        conn.commit()

