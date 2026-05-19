"""
app.py — Kenya MSME Advisor: Chat Interface with Multi-language Support
Run with:  streamlit run src/app.py
"""

import json
import pickle
import re
from pathlib import Path
import streamlit as st
import anthropic
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).parent.parent
DB_DIR   = BASE_DIR / "knowledge_base"

st.set_page_config(page_title="Kenya MSME Advisor", page_icon="🇰🇪", layout="centered")

st.markdown("""
<style>
.header{background:linear-gradient(135deg,#006600 0%,#cc0000 100%);color:white;padding:1.2rem 1.5rem;border-radius:10px;margin-bottom:1rem;}
.source-box{background:#f0f4f0;border-left:4px solid #006600;padding:0.5rem 0.8rem;border-radius:0;font-size:0.8rem;color:#444;margin-top:0.5rem;}
.lang-badge{background:#fff8e1;border:1px solid #f9a825;color:#e65100;padding:0.2rem 0.6rem;border-radius:20px;font-size:0.75rem;margin-top:0.4rem;display:inline-block;}
.disclaimer{font-size:0.75rem;color:#888;text-align:center;margin-top:2rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <h2 style="margin:0">🇰🇪 Kenya MSME Business Advisor</h2>
    <p style="margin:0.3rem 0 0 0;opacity:0.9;font-size:0.9rem">
        AI-powered guidance — English, Kiswahili, Kikuyu, Dholuo, Kalenjin na lugha zingine
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
        st.subheader("⚙️ Setup")
        key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
        if not key:
            st.info("Enter your API key to start chatting.")
            st.markdown("[Get a free API key →](https://console.anthropic.com)")
        return key or None


@st.cache_resource(show_spinner="Loading knowledge base...")
def load_index():
    try:
        with open(DB_DIR / "vectorizer.pkl", "rb") as f: vectorizer = pickle.load(f)
        with open(DB_DIR / "matrix.pkl", "rb") as f:     matrix     = pickle.load(f)
        with open(DB_DIR / "chunks.json") as f:           data       = json.load(f)
        return vectorizer, matrix, data["chunks"], data["metadata"]
    except FileNotFoundError:
        return None, None, [], []


def detect_language(text: str) -> str:
    """Detect the language of the user's input."""
    text_lower = text.lower()
    # Dholuo indicators
    dholuo_words = ['ere','kaka','ango','nyalo','tero','chandruok','osiep',
                    'awuon','bende','mano','adhi','wach','pesa','ohala','ichamo']
    # Kikuyu indicators
    kikuyu_words = ['niwega','niguo','ndungata','ngwataniro','murata','uguo',
                    'niwahota','biashara','thogora','mboroto','gikuyu','ndiaga']
    # Kalenjin indicators
    kalenjin_words = ['amun','mising','nee','tugul','kamusto','ng\'etit',
                      'kabisa','kimwa','chebo','nebo','miosiek']
    # Kamba indicators
    kamba_words = ['nesa','kwata','mwende','mwethya','kikamba','mwatu','nvoo']
    # Kiswahili indicators
    swahili_words = ['biashara','kodi','ushuru','mkopo','akiba','benki','leseni',
                     'usajili','nina','nataka','niambie','jinsi','gani','nini',
                     'ninaweza','kuweza','kupata','pesa','shilingi','malipo']

    dholuo_score  = sum(1 for w in dholuo_words  if w in text_lower)
    kikuyu_score  = sum(1 for w in kikuyu_words  if w in text_lower)
    kalenjin_score= sum(1 for w in kalenjin_words if w in text_lower)
    kamba_score   = sum(1 for w in kamba_words   if w in text_lower)
    swahili_score = sum(1 for w in swahili_words if w in text_lower)

    scores = {
        'dholuo':   dholuo_score,
        'kikuyu':   kikuyu_score,
        'kalenjin': kalenjin_score,
        'kamba':    kamba_score,
        'kiswahili':swahili_score,
    }
    max_lang  = max(scores, key=scores.get)
    max_score = scores[max_lang]
    return max_lang if max_score >= 2 else 'english'


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


def ask_claude(api_key, question, context, history, detected_lang):
    client = anthropic.Anthropic(api_key=api_key)

    # Language-specific response instructions
    lang_instructions = {
        'kiswahili': "Jibu kwa Kiswahili kamili. Tumia maneno rahisi ya Kiswahili.",
        'dholuo':    """The user is writing in Dholuo (Luo language from Nyanza, Kenya).
Respond PRIMARILY in simple Kiswahili (which Luo speakers understand well),
but begin your response with a brief greeting in Dholuo such as 'Amosi!' or 'Misawa!'.
Explain that for detailed business guidance you will use Kiswahili.
At the end, add key terms in Dholuo where helpful.""",
        'kikuyu':    """The user may be writing in Kikuyu (Gikuyu language from Central Kenya).
Respond in simple Kiswahili (which Kikuyu speakers understand very well),
but acknowledge their Kikuyu language with a brief greeting like 'Niwega!'
Provide the full answer in Kiswahili.""",
        'kalenjin':  """The user may be writing in a Kalenjin dialect (Rift Valley, Kenya).
Respond in simple Kiswahili (widely understood by Kalenjin speakers),
acknowledge their language briefly, then provide full guidance in Kiswahili.""",
        'kamba':     """The user may be writing in Kikamba (Eastern Kenya).
Respond in simple Kiswahili (well understood by Kamba speakers),
acknowledge their language briefly, then provide full guidance in Kiswahili.""",
        'english':   "Respond in clear, simple English.",
    }

    lang_note = lang_instructions.get(detected_lang, lang_instructions['english'])

    system = f"""You are a knowledgeable and friendly business advisor specializing in
helping Micro, Small, and Medium Enterprises (MSMEs) in Kenya.

LANGUAGE INSTRUCTION: {lang_note}

You provide practical, accurate guidance on:
- Business registration and licensing (BRS, eCitizen, county permits)
- KRA tax obligations (VAT, income tax, PAYE, Turnover Tax, eTIMS)
- Access to financing (Hustler Fund, YEDF, WEF, SACCOs, banks, chama groups)
- Business compliance and regulatory requirements
- Market access and growth strategies for Kenyan MSMEs
- Cultural business practices (chama, Jua Kali, community networks)

RULES:
1. Base your answers primarily on the CONTEXT documents below.
2. If context does not cover the question, say so and give general guidance.
3. Always be specific to Kenya — mention actual institutions, laws, and processes.
4. Use simple, clear language appropriate for MSME owners.
5. Always recommend consulting a qualified lawyer or accountant for complex decisions.

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


# Language display names
LANG_DISPLAY = {
    'english':   '🇬🇧 English',
    'kiswahili': '🇰🇪 Kiswahili',
    'dholuo':    '🐟 Dholuo (Luo)',
    'kikuyu':    '🏔️ Kikuyu (Gikuyu)',
    'kalenjin':  '🏃 Kalenjin',
    'kamba':     '🎨 Kamba',
}

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
    st.subheader("🌍 Supported Languages")
    st.markdown("""
    - 🇬🇧 **English** — Full support
    - 🇰🇪 **Kiswahili** — Full support
    - 🐟 **Dholuo** — Partial (via Kiswahili)
    - 🏔️ **Kikuyu** — Partial (via Kiswahili)
    - 🏃 **Kalenjin** — Partial (via Kiswahili)
    - 🎨 **Kamba** — Partial (via Kiswahili)
    """)

    st.markdown("---")
    st.subheader("💡 Sample Questions")
    samples = [
        "How do I register a business in Kenya?",
        "What taxes does a small business pay to KRA?",
        "How do I apply for the Hustler Fund?",
        "Ninawezaje kupata mkopo wa biashara?",
        "Kodi ya mauzo ni nini na nani analipa?",
        "Ere kaka anyalo tero chandruok e Hustler Fund?",
        "Niwega — ngwataniro ni giki?",
    ]
    for q in samples:
        if st.button(q, key=q, use_container_width=True):
            st.session_state["prefill"] = q

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
        if turn.get("lang") and turn["lang"] != "english":
            st.markdown(
                f"<div class='lang-badge'>Detected: {LANG_DISPLAY.get(turn['lang'], turn['lang'])}</div>",
                unsafe_allow_html=True
            )
    with st.chat_message("assistant", avatar="🇰🇪"):
        st.write(turn["assistant"])
        if turn.get("sources"):
            st.markdown(
                "<div class='source-box'>📄 Sources: " +
                " | ".join(turn["sources"]) + "</div>",
                unsafe_allow_html=True
            )

prefill  = st.session_state.pop("prefill", "")
question = st.chat_input("Ask in English, Kiswahili, Dholuo, Kikuyu, Kalenjin...")
question = question or prefill

if question:
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
        st.stop()

    # Detect language
    detected_lang = detect_language(question)

    with st.chat_message("user"):
        st.write(question)
        if detected_lang != "english":
            st.markdown(
                f"<div class='lang-badge'>Detected: {LANG_DISPLAY.get(detected_lang, detected_lang)}</div>",
                unsafe_allow_html=True
            )

    with st.chat_message("assistant", avatar="🇰🇪"):
        with st.spinner("Searching knowledge base and thinking..."):
            context, sources = retrieve(question, vectorizer, matrix, chunks, metadata)
            answer = ask_claude(
                api_key, question, context,
                st.session_state["history"], detected_lang
            )
        st.write(answer)
        if sources:
            st.markdown(
                "<div class='source-box'>📄 Sources: " +
                " | ".join(sources) + "</div>",
                unsafe_allow_html=True
            )

    st.session_state["history"].append({
        "user":      question,
        "assistant": answer,
        "sources":   sources,
        "lang":      detected_lang,
    })

st.markdown(
    "<div class='disclaimer'>⚠️ This tool provides general guidance only. "
    "Consult a qualified lawyer or accountant for complex decisions.</div>",
    unsafe_allow_html=True
)
