"""
app.py — Kenya MSME Advisor: Operator Interface
The MSME Operator sees ONLY what they need:
  - Ask a question
  - Get an answer in their language
  - See sources cited
  - Sample questions to get started
  - Clear conversation

Run with: streamlit run src/app.py
"""

import json
import pickle
import time
import uuid
from pathlib import Path
import streamlit as st
import anthropic
from sklearn.metrics.pairwise import cosine_similarity
import sys

BASE_DIR = Path(__file__).parent.parent
DB_DIR   = BASE_DIR / "knowledge_base"

sys.path.insert(0, str(Path(__file__).parent))
from logger import log_conversation

st.set_page_config(
    page_title="Kenya MSME Business Advisor",
    page_icon="🇰🇪",
    layout="centered"
)

st.markdown("""
<style>
.header {
    background: linear-gradient(135deg, #006600 0%, #cc0000 100%);
    color: white;
    padding: 1.2rem 1.5rem;
    border-radius: 10px;
    margin-bottom: 1rem;
}
.source-box {
    background: #f0f4f0;
    border-left: 4px solid #006600;
    padding: 0.5rem 0.8rem;
    border-radius: 4px;
    font-size: 0.78rem;
    color: #555;
    margin-top: 0.4rem;
}
.lang-badge {
    background: #fff8e1;
    border: 1px solid #f9a825;
    color: #e65100;
    padding: 0.15rem 0.5rem;
    border-radius: 20px;
    font-size: 0.72rem;
    margin-top: 0.3rem;
    display: inline-block;
}
.disclaimer {
    font-size: 0.75rem;
    color: #888;
    text-align: center;
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #eee;
}
.sample-header {
    font-size: 0.8rem;
    font-weight: 600;
    color: #444;
    margin-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header">
    <h2 style="margin:0">🇰🇪 Kenya MSME Business Advisor</h2>
    <p style="margin:0.3rem 0 0 0;opacity:0.9;font-size:0.9rem">
        AI-powered guidance — English, Kiswahili, Dholuo, Kikuyu, Kalenjin na zaidi
    </p>
</div>
""", unsafe_allow_html=True)


# ── Session ID ─────────────────────────────────────────────────────────────────
if "session_id"     not in st.session_state:
    st.session_state["session_id"]     = str(uuid.uuid4())[:8]
if "history"        not in st.session_state:
    st.session_state["history"]        = []
if "question_count" not in st.session_state:
    st.session_state["question_count"] = 0


# ── API key ────────────────────────────────────────────────────────────────────
def get_api_key():
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                key = line.split("=", 1)[1].strip()
                if key and key != "your_actual_key_here":
                    return key
    return None


# ── Knowledge base ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading knowledge base...")
def load_index():
    try:
        with open(DB_DIR / "vectorizer.pkl", "rb") as f:
            vectorizer = pickle.load(f)
        with open(DB_DIR / "matrix.pkl", "rb") as f:
            matrix = pickle.load(f)
        with open(DB_DIR / "chunks.json") as f:
            data = json.load(f)
        return vectorizer, matrix, data["chunks"], data["metadata"]
    except FileNotFoundError:
        return None, None, [], []


def retrieve(query, vectorizer, matrix, chunks, metadata, k=4):
    if vectorizer is None:
        return "", []
    qvec = vectorizer.transform([query])
    sims = cosine_similarity(qvec, matrix).flatten()
    top  = sims.argsort()[-k:][::-1]
    ctx_parts, sources = [], []
    for i in top:
        if sims[i] > 0.01:
            ctx_parts.append(chunks[i])
            src = metadata[i].get("filename", "Unknown")
            if src not in sources:
                sources.append(src)
    return "\n\n---\n\n".join(ctx_parts), sources


# ── Language detection ─────────────────────────────────────────────────────────
def detect_language(text: str) -> str:
    t = text.lower()
    scores = {
        "dholuo":    sum(1 for w in ["ere","kaka","nyalo","tero","chandruok",
                                      "osiep","awuon","bende","adhi","ohala"]
                         if w in t),
        "kikuyu":    sum(1 for w in ["niwega","niguo","ndungata","ngwataniro",
                                      "murata","niwahota","thogora","mboroto"]
                         if w in t),
        "kalenjin":  sum(1 for w in ["amun","mising","tugul","kamusto","nebo"]
                         if w in t),
        "kamba":     sum(1 for w in ["nesa","kwata","mwende","mwethya","mwatu"]
                         if w in t),
        "kiswahili": sum(1 for w in ["biashara","kodi","ushuru","mkopo","akiba",
                                      "benki","leseni","usajili","nina","nataka",
                                      "niambie","ninaweza","pesa","shilingi",
                                      "malipo","habari","hustler","jinsi"]
                         if w in t),
    }
    best  = max(scores, key=scores.get)
    return best if scores[best] >= 2 else "english"


LANG_DISPLAY = {
    "english":   "🇬🇧 English",
    "kiswahili": "🇰🇪 Kiswahili",
    "dholuo":    "🐟 Dholuo",
    "kikuyu":    "🏔️ Kikuyu",
    "kalenjin":  "🏃 Kalenjin",
    "kamba":     "🎨 Kamba",
}

LANG_INSTRUCTIONS = {
    "kiswahili": "Jibu kwa Kiswahili kamili. Tumia maneno rahisi.",
    "dholuo":    "Greet briefly in Dholuo ('Amosi!') then answer fully in Kiswahili.",
    "kikuyu":    "Greet briefly in Kikuyu ('Niwega!') then answer fully in Kiswahili.",
    "kalenjin":  "Acknowledge briefly then answer fully in Kiswahili.",
    "kamba":     "Acknowledge briefly then answer fully in Kiswahili.",
    "english":   "Respond in clear, simple English.",
}


# ── Claude ─────────────────────────────────────────────────────────────────────
def ask_claude(api_key, question, context, history, lang):
    client  = anthropic.Anthropic(api_key=api_key)
    system  = f"""You are a knowledgeable and friendly business advisor
specialising in helping Micro, Small, and Medium Enterprises (MSMEs) in Kenya.

LANGUAGE: {LANG_INSTRUCTIONS.get(lang, LANG_INSTRUCTIONS['english'])}

You provide practical, accurate guidance on:
- Business registration and licensing (BRS, eCitizen, county permits)
- KRA tax obligations (VAT, income tax, PAYE, Turnover Tax, eTIMS)
- Access to financing (Hustler Fund, YEDF, WEF, SACCOs, banks, chama)
- Social security (NSSF, SHA, NITA)
- Trade and market access (EAC, COMESA, AfCFTA, e-commerce)
- Cultural business practices (chama, Jua Kali, community networks)
- Infrastructure and technology for MSMEs

RULES:
1. Base answers primarily on the CONTEXT documents below.
2. If context does not cover the question, say so and give general guidance.
3. Always be specific to Kenya — mention actual institutions, laws, processes.
4. Use simple, clear language any MSME owner can understand.
5. Always recommend consulting a lawyer or accountant for complex decisions.

CONTEXT FROM KNOWLEDGE BASE:
{context if context else "No specific documents found for this query."}"""

    messages = []
    for turn in history:
        messages += [
            {"role": "user",      "content": turn["user"]},
            {"role": "assistant", "content": turn["assistant"]},
        ]
    messages.append({"role": "user", "content": question})

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        system=system,
        messages=messages,
    )
    return response.content[0].text


# ── Sidebar — operator focused ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💡 Sample Questions")
    st.caption("Click any question to get started:")

    samples = [
        "How do I register a business in Kenya?",
        "What taxes does a small business pay?",
        "How do I apply for the Hustler Fund?",
        "What licenses do I need to open a shop?",
        "How do I register for NSSF and SHA?",
        "Ninawezaje kupata mkopo wa biashara?",
        "What is eTIMS and does my business need it?",
        "How do I export my products to other countries?",
        "What is a SACCO and how can it help my business?",
        "How do I pay PAYE for my employees?",
    ]
    for q in samples:
        if st.button(q, key=q, use_container_width=True):
            st.session_state["prefill"] = q

    st.markdown("---")
    st.markdown("### 🌍 Languages Supported")
    st.markdown("""
- 🇬🇧 **English** — Full support
- 🇰🇪 **Kiswahili** — Full support
- 🐟 **Dholuo** — Partial
- 🏔️ **Kikuyu** — Partial
- 🏃 **Kalenjin** — Partial
- 🎨 **Kamba** — Partial
""")

    st.markdown("---")
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state["history"]        = []
        st.session_state["question_count"] = 0
        st.rerun()


# ── Load resources ─────────────────────────────────────────────────────────────
api_key                              = get_api_key()
vectorizer, matrix, chunks, metadata = load_index()

# ── Chat history ───────────────────────────────────────────────────────────────
for turn in st.session_state["history"]:
    with st.chat_message("user"):
        st.write(turn["user"])
        if turn.get("lang") and turn["lang"] != "english":
            st.markdown(
                f"<div class='lang-badge'>"
                f"Detected: {LANG_DISPLAY.get(turn['lang'], turn['lang'])}"
                f"</div>",
                unsafe_allow_html=True,
            )
    with st.chat_message("assistant", avatar="🇰🇪"):
        st.write(turn["assistant"])
        if turn.get("sources"):
            st.markdown(
                "<div class='source-box'>📄 Sources: " +
                " | ".join(turn["sources"]) + "</div>",
                unsafe_allow_html=True,
            )

# ── Input ──────────────────────────────────────────────────────────────────────
prefill  = st.session_state.pop("prefill", "")
question = st.chat_input(
    "Ask about business registration, tax, financing..."
)
question = question or prefill

if question:
    if not api_key:
        st.error(
            "⚠️ The advisory service is temporarily unavailable. "
            "Please contact the system administrator."
        )
        st.stop()

    lang = detect_language(question)
    st.session_state["question_count"] += 1

    with st.chat_message("user"):
        st.write(question)
        if lang != "english":
            st.markdown(
                f"<div class='lang-badge'>"
                f"Detected: {LANG_DISPLAY.get(lang, lang)}"
                f"</div>",
                unsafe_allow_html=True,
            )

    with st.chat_message("assistant", avatar="🇰🇪"):
        with st.spinner("Searching knowledge base..."):
            start            = time.time()
            context, sources = retrieve(
                question, vectorizer, matrix, chunks, metadata
            )
            answer           = ask_claude(
                api_key, question, context,
                st.session_state["history"], lang
            )
            elapsed          = time.time() - start

        st.write(answer)
        if sources:
            st.markdown(
                "<div class='source-box'>📄 Sources: " +
                " | ".join(sources) + "</div>",
                unsafe_allow_html=True,
            )

    # Log silently — operator never sees this
    log_conversation(
        session_id      = st.session_state["session_id"],
        question_number = st.session_state["question_count"],
        language        = lang,
        question        = question,
        answer          = answer,
        sources         = sources,
        response_time   = elapsed,
        had_card        = False,
    )

    st.session_state["history"].append({
        "user":      question,
        "assistant": answer,
        "sources":   sources,
        "lang":      lang,
    })

# ── Disclaimer ─────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='disclaimer'>"
    "⚠️ This tool provides general guidance only. "
    "Consult a qualified lawyer or accountant for complex decisions.<br>"
    "Developed by Kathembo Tsongo Dieudonne — Strathmore University, 2026"
    "</div>",
    unsafe_allow_html=True,
)
