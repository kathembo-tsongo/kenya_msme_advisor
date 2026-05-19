"""
ingest.py — Kenya MSME Advisor: Document Ingestion Script
Reads documents from the /documents folder and builds a searchable index.

Run once whenever you add new documents:
    python3 src/ingest.py
"""

import sys
import json
import pickle
from pathlib import Path
from pypdf import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer

BASE_DIR      = Path(__file__).parent.parent
DOCUMENTS_DIR = BASE_DIR / "documents"
DB_DIR        = BASE_DIR / "knowledge_base"


def read_pdf(path):
    reader = PdfReader(str(path))
    return "\n".join(p.extract_text() or "" for p in reader.pages)


def read_docx(path):
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def read_txt(path):
    return path.read_text(encoding="utf-8", errors="ignore")


def load_documents():
    supported = {".pdf": read_pdf, ".docx": read_docx, ".txt": read_txt}
    docs = []

    if not DOCUMENTS_DIR.exists():
        print(f"[ERROR] Documents folder not found: {DOCUMENTS_DIR}")
        sys.exit(1)

    files = list(DOCUMENTS_DIR.rglob("*"))
    if not any(f.suffix.lower() in supported for f in files):
        print("  No supported files found (PDF, DOCX, TXT).")
        return docs

    for file in files:
        if file.suffix.lower() not in supported:
            continue
        print(f"  Loading: {file.name} ...", end=" ", flush=True)
        try:
            content = supported[file.suffix.lower()](file)
            if content.strip():
                docs.append({
                    "content":  content,
                    "filename": file.name,
                    "source":   str(file.relative_to(BASE_DIR))
                })
                print(f"✓  ({len(content):,} chars)")
            else:
                print("⚠  empty, skipped")
        except Exception as e:
            print(f"✗  {e}")
    return docs


def split_chunks(docs, size=1000, overlap=150):
    chunks, metas = [], []
    for doc in docs:
        text, i, start = doc["content"], 0, 0
        while start < len(text):
            chunk = text[start:start + size].strip()
            if chunk:
                chunks.append(chunk)
                metas.append({
                    "filename": doc["filename"],
                    "source":   doc["source"],
                    "chunk":    i
                })
                i += 1
            start += size - overlap
    return chunks, metas


def build_index(chunks, metas):
    DB_DIR.mkdir(parents=True, exist_ok=True)
    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        stop_words="english"
    )
    matrix = vectorizer.fit_transform(chunks)

    with open(DB_DIR / "vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open(DB_DIR / "matrix.pkl", "wb") as f:
        pickle.dump(matrix, f)
    with open(DB_DIR / "chunks.json", "w") as f:
        json.dump({"chunks": chunks, "metadata": metas}, f, indent=2)

    print(f"  ✓ Index saved — {len(chunks)} chunks → {DB_DIR}")


def main():
    print("=" * 60)
    print("  Kenya MSME Advisor — Document Ingestion")
    print("=" * 60)

    print(f"\n[1/3] Loading documents from: {DOCUMENTS_DIR}")
    docs = load_documents()
    if not docs:
        print("\n  Add PDF, DOCX, or TXT files to documents/ and re-run.")
        return

    print(f"\n[2/3] Splitting {len(docs)} document(s) into chunks...")
    chunks, metas = split_chunks(docs)
    print(f"  → {len(chunks)} chunks created")

    print("\n[3/3] Building offline TF-IDF search index...")
    build_index(chunks, metas)

    print("\n✅ Knowledge base is ready!")
    print("   Launch the app with:  streamlit run src/app.py")


if __name__ == "__main__":
    main()
