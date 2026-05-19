"""
app.py — Kenya MSME Advisor: Chat Interface with Summary Cards
Run with:  streamlit run src/app.py
"""

import json
import pickle
import re
from pathlib import Path
import streamlit as st
import anthropic
from sklearn.metrics.pairwise import cosine_similarity
from summary_card import should_show_card, extract_summary, render_summary_card

BASE_DIR = Path(__file__).parent.parent
DB_DIR   = BASE_DIR / "knowledge_base"

st.set_page_config(page_title="Kenya MSME Advisor", page_icon="🇰🇪", layout="centered")

st.markdown("""
<style>
.header{background:linear-gradient(135deg,#006600 0%,#cc0000 100%);color:white;padding:1.2rem 1.5rem;border-radius:10px;margin-bottom:1rem;}
.source-box{background:#f0f4f0;border-left:4px solid #006600;padding:0.5rem 0.8rem;border-radius:4px;font-size:0.8rem;color:#444;margin-top:0.5rem;}
.disclaimer{font-size:0.75rem;color:#888;text-align:center;margin-top:2rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h2 style="margin:0">🇰🇪 Kenya MSME Business Advisor</h2>
    <p style="margin:0.3rem 0 0 0;opacity:0.9;font-size:0.9rem">
        AI-powered guidance on business registration, tax, financing and compliance
    </p>
</div>
""", unsafe_allow_html=True)


def get_api_key():
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                key = line.split("=", 1)[1].strip()
                if key and key != "your_actual_key_here":
                    return key
    with st.sidebar:
        st.subheader("Setup")
        key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
        if not key:
            st.info("Enter your API key to start chatting.")
            st.markdown("[Get a free API key](https://console.anthropic.com)")
        return key or None


@st.cache_resource(show_spinner="Loading knowledge base...")
def load_index():
    try:
        with open(DB_DIR / "vectorizer.pkl", "rb") as f: vectorizer = pickle.load(f)
        with open(DB_DIR / "matrix.pkl", "rb") as f:     matrix     = pickle.load(f)
        with open(DB_DIR / "chunks.json") as f:          data       = json.load(f)
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


def ask_claude(api_key, question, context, history):
    client = anthropic.Anthropic(api_key=api_key)
    system = f"""You are a knowledgeable and friendly business advisor specializing in
helping Micro, Small, and Medium Enterprises (MSMEs) in Kenya.

You provide practical, accurate guidance on:
- Business registration and licensing (BRS, eCitizen, county permits)
- KRA tax obligations (VAT, income tax, PAYE, Turnover Tax, eTIMS)
- Access to financing (Hustler Fund, YEDF, WEF, SACCOs, banks)
- Business compliance and regulatory requirements
- Market access and business growth strategies for Kenyan MSMEs

RULES:
1. Base your answers primarily on the CONTEXT documents below.
2. If context does not cover the question, say so clearly and give general guidance.
3. Always be specific to Kenya — mention actual institutions, laws, and processes.
4. Use simple, clear language that any MSME owner can understand.
5. Where relevant, include numbered steps, costs in KES, and deadlines.
6. If the question is in Swahili, respond fully in Swahili.
7. Always recommend consulting a qualified lawyer or accountant for complex decisions.

CONTEXT FROM KNOWLEDGE BASE:
{context if context else "No specific documents found for this query."}"""

    messages = []
    for turn in history:
        messages += [
            {"role": "user",      "content": turn["user"]},
            {"role": "assistant", "content": turn["assistant"]}
        ]
    messages.append({"role": "user", "content": question})

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        system=system,
        messages=messages,
    )
    return response.content[0].text


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("---")
    st.subheader("📚 Knowledge Base")
    try:
        with open(DB_DIR / "chunks.json") as f:
            n = len(json.load(f)["chunks"])
        st.success(f"✅ {n:,} chunks loaded")
    except FileNotFoundError:
        st.warning("⚠️ No knowledge base.\nRun: python3 src/ingest.py")

    st.markdown("---")
    st.subheader("💡 Sample Questions")
    samples = [
        "How do I register a sole proprietorship in Kenya?",
        "What taxes does a small business pay to KRA?",
        "How do I apply for the Hustler Fund?",
        "What is Turnover Tax (TOT)?",
        "What licenses do I need to open a shop?",
        "How do I set up M-Pesa Paybill for my business?",
        "Ninawezaje kupata mkopo kwa biashara yangu?",
    ]
    for q in samples:
        if st.button(q, key=q, use_container_width=True):
            st.session_state["prefill"] = q

    st.markdown("---")
    st.subheader("⚙️ Display Options")
    show_cards = st.toggle("Show Summary Cards", value=True,
                           help="Show animated summary cards after detailed answers")

    st.markdown("---")
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state["history"] = []
        st.rerun()


# ── Chat ───────────────────────────────────────────────────────────────────────
api_key = get_api_key()
vectorizer, matrix, chunks, metadata = load_index()

if "history" not in st.session_state:
    st.session_state["history"] = []

for turn in st.session_state["history"]:
    with st.chat_message("user"):
        st.write(turn["user"])
    with st.chat_message("assistant", avatar="🇰🇪"):
        st.write(turn["assistant"])
        if turn.get("sources"):
            st.markdown(
                "<div class='source-box'>📄 Sources: " +
                " | ".join(turn["sources"]) + "</div>",
                unsafe_allow_html=True
            )
        if turn.get("card_html"):
            st.markdown(turn["card_html"], unsafe_allow_html=True)

prefill  = st.session_state.pop("prefill", "")
question = st.chat_input("Ask about Kenyan business registration, tax, financing...")
question = question or prefill

if question:
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
        st.stop()

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant", avatar="🇰🇪"):
        with st.spinner("Searching knowledge base and thinking..."):
            context, sources = retrieve(question, vectorizer, matrix, chunks, metadata)
            answer = ask_claude(api_key, question, context, st.session_state["history"])

        st.write(answer)

        if sources:
            st.markdown(
                "<div class='source-box'>📄 Sources: " +
                " | ".join(sources) + "</div>",
                unsafe_allow_html=True
            )

        # Smart summary card — only when content warrants it
        card_html = None
        if show_cards and should_show_card(answer):
            card_data = extract_summary(answer, question)
            card_html = render_summary_card(card_data)
            st.markdown(card_html, unsafe_allow_html=True)

    st.session_state["history"].append({
        "user":      question,
        "assistant": answer,
        "sources":   sources,
        "card_html": card_html,
    })

st.markdown(
    "<div class='disclaimer'>⚠️ This tool provides general guidance only. "
    "Consult a qualified lawyer or accountant for complex decisions.</div>",
    unsafe_allow_html=True
)
