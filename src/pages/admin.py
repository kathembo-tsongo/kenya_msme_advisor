"""
Admin page — only for the developer
Access at: http://localhost:8502/admin
"""

import json
import pickle
import hashlib
from pathlib import Path
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from pypdf import PdfReader
from docx import Document

BASE_DIR = Path(__file__).parent.parent.parent
DB_DIR   = BASE_DIR / "knowledge_base"
DOCS_DIR = BASE_DIR / "documents"

st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="centered")

st.markdown("""
<style>
.admin-header {
    background: #1a1a2e;
    color: white;
    padding: 1.2rem 1.5rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="admin-header">
    <h2 style="margin:0">⚙️ Admin Panel</h2>
    <p style="margin:0.3rem 0 0 0; opacity:0.8; font-size:0.9rem">
        Kenya MSME Advisor — Developer Controls
    </p>
</div>
""", unsafe_allow_html=True)

# ── Password protection ────────────────────────────────────────────────────────
if "admin_auth" not in st.session_state:
    st.session_state["admin_auth"] = False

if not st.session_state["admin_auth"]:
    password = st.text_input("🔐 Enter admin password", type="password")
    if st.button("Login", type="primary"):
        if password == "msme2024admin":
            st.session_state["admin_auth"] = True
            st.rerun()
        else:
            st.error("❌ Wrong password.")
    st.stop()

# ── Readers ────────────────────────────────────────────────────────────────────
def read_pdf(path):
    reader = PdfReader(str(path))
    return "\n".join(p.extract_text() or "" for p in reader.pages)

def read_docx(path):
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def read_txt(path):
    return path.read_text(encoding="utf-8", errors="ignore")

def build_index():
    supported = {".pdf": read_pdf, ".docx": read_docx, ".txt": read_txt}
    chunks, metas = [], []
    for file in DOCS_DIR.rglob("*"):
        if file.suffix.lower() not in supported:
            continue
        try:
            content = supported[file.suffix.lower()](file)
            if not content.strip():
                continue
            size, overlap, i, start = 1000, 150, 0, 0
            while start < len(content):
                chunk = content[start:start + size].strip()
                if chunk:
                    chunks.append(chunk)
                    metas.append({"filename": file.name,
                                  "source": str(file.relative_to(BASE_DIR)),
                                  "chunk": i})
                    i += 1
                start += size - overlap
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")

    if not chunks:
        return 0

    DB_DIR.mkdir(parents=True, exist_ok=True)
    vectorizer = TfidfVectorizer(
        max_features=10000, ngram_range=(1, 2), stop_words="english"
    )
    matrix = vectorizer.fit_transform(chunks)

    hasher = hashlib.md5()
    for f in sorted(DOCS_DIR.rglob("*")):
        if f.suffix.lower() in {".pdf", ".docx", ".txt"} and f.is_file():
            hasher.update(str(f.stat().st_mtime).encode())
            hasher.update(f.read_bytes())

    with open(DB_DIR / "vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    with open(DB_DIR / "matrix.pkl", "wb") as f:
        pickle.dump(matrix, f)
    with open(DB_DIR / "chunks.json", "w") as f:
        json.dump({"chunks": chunks, "metadata": metas,
                   "fingerprint": hasher.hexdigest()}, f)
    return len(chunks)

# ── Document status ────────────────────────────────────────────────────────────
st.subheader("📂 Documents")
supported_ext = {".pdf", ".docx", ".txt"}
files = [f for f in DOCS_DIR.rglob("*") if f.suffix.lower() in supported_ext]
if files:
    for f in files:
        size = f.stat().st_size / 1024
        st.write(f"📄 `{f.name}` — {size:.1f} KB")
else:
    st.warning("No documents found in documents/ folder.")

st.markdown("---")

# ── Index status ───────────────────────────────────────────────────────────────
st.subheader("🗄️ Index Status")
try:
    with open(DB_DIR / "chunks.json") as f:
        data = json.load(f)
    st.success(f"✅ {len(data['chunks'])} chunks indexed")
except FileNotFoundError:
    st.error("No index found. Build it below.")

st.markdown("---")

# ── Rebuild button ─────────────────────────────────────────────────────────────
st.subheader("🔄 Rebuild Knowledge Base")
st.caption("Run this every time you add or edit a document.")
if st.button("🔄 Rebuild Now", type="primary", use_container_width=True):
    with st.spinner("Rebuilding index..."):
        n = build_index()
    if n:
        st.success(f"✅ Done! {n} chunks indexed. Users will get updated answers immediately.")
        st.balloons()
    else:
        st.error("No content found to index.")

st.markdown("---")
if st.button("🔓 Logout", use_container_width=True):
    st.session_state["admin_auth"] = False
    st.rerun()
