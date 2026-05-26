"""
analytics.py — Kenya MSME Advisor: Analytics Dashboard
Access at: http://localhost:8501/analytics
"""

import csv
from pathlib import Path
from collections import Counter
from datetime import datetime
import streamlit as st

BASE_DIR = Path(__file__).parent.parent.parent
LOG_FILE = BASE_DIR / "logs" / "conversations.csv"

st.set_page_config(
    page_title="MSME Advisor — Analytics",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.dash-header{background:linear-gradient(135deg,#006600 0%,#cc0000 100%);
  color:white;padding:1.2rem 1.5rem;border-radius:10px;margin-bottom:1.5rem;}
.find-card{background:#f8f9fa;border-left:4px solid #006600;
  border-radius:0 8px 8px 0;padding:12px 16px;margin-bottom:10px;}
.find-title{font-weight:600;color:#1a1a1a;margin-bottom:4px;font-size:14px;}
.find-body{color:#444;font-size:13px;line-height:1.6;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="dash-header">
    <h2 style="margin:0">📊 Kenya MSME Advisor — Analytics Dashboard</h2>
    <p style="margin:0.3rem 0 0 0;opacity:0.9;font-size:0.9rem">
        Real-time conversation analysis for thesis findings
    </p>
</div>
""", unsafe_allow_html=True)


# ── Load data ──────────────────────────────────────────────────────────────────
def load_data():
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE, encoding="utf-8") as f:
        return list(csv.DictReader(f))


rows = load_data()

if not rows:
    st.warning("No conversations logged yet. Start chatting to generate data!")
    st.stop()

# ── Compute stats ──────────────────────────────────────────────────────────────
total     = len(rows)
sessions  = len(set(r["session_id"] for r in rows))
times     = [float(r["response_time_seconds"]) for r in rows if r["response_time_seconds"]]
avg_time  = sum(times) / len(times) if times else 0
words     = [int(r["answer_length_words"]) for r in rows if r["answer_length_words"]]
avg_words = sum(words) / len(words) if words else 0
topics    = Counter(r["topic_category"] for r in rows)
languages = Counter(r["language_detected"] for r in rows)
dates     = Counter(r["date"] for r in rows)

all_sources = []
for r in rows:
    all_sources.extend(r["sources"].split(" | "))
src_count = Counter(s for s in all_sources if s not in ["none", ""])

lang_labels = {
    "english":   "🇬🇧 English",
    "kiswahili": "🇰🇪 Kiswahili",
    "dholuo":    "🐟 Dholuo",
    "kikuyu":    "🏔️ Kikuyu",
    "kalenjin":  "🏃 Kalenjin",
    "kamba":     "🎨 Kamba",
}

# ── Row 1: Key metrics ─────────────────────────────────────────────────────────
st.subheader("📈 Key Metrics")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total Q&As",   total)
c2.metric("Sessions",     sessions)
c3.metric("Avg Response", f"{avg_time:.1f}s")
c4.metric("Avg Answer",   f"{avg_words:.0f} words")
c5.metric("Fastest",      f"{min(times):.1f}s" if times else "N/A")
c6.metric("Slowest",      f"{max(times):.1f}s" if times else "N/A")

st.markdown("---")

# ── Row 2: Topic + Language ────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🗂️ Questions by Topic")
    total_t = sum(topics.values())
    for topic, count in topics.most_common():
        pct = (count / total_t) * 100
        st.markdown(f"**{topic}** — {count} questions ({pct:.0f}%)")
        st.progress(pct / 100)

with col_right:
    st.subheader("🌍 Language Distribution")
    total_l = sum(languages.values())
    for lang, count in languages.most_common():
        pct   = (count / total_l) * 100
        label = lang_labels.get(lang, lang)
        st.markdown(f"**{label}** — {count} questions ({pct:.0f}%)")
        st.progress(pct / 100)

    st.markdown("---")
    st.subheader("⏱️ Response Time Distribution")
    fast   = sum(1 for t in times if t < 10)
    medium = sum(1 for t in times if 10 <= t < 30)
    slow   = sum(1 for t in times if t >= 30)
    st.markdown(f"**Fast** (under 10s) — {fast} responses")
    st.progress(fast / total if total else 0)
    st.markdown(f"**Medium** (10–30s) — {medium} responses")
    st.progress(medium / total if total else 0)
    st.markdown(f"**Slow** (over 30s) — {slow} responses")
    st.progress(slow / total if total else 0)

st.markdown("---")

# ── Row 3: Top sources ─────────────────────────────────────────────────────────
st.subheader("📚 Most Used Knowledge Sources")
top_sources = src_count.most_common(10)
if top_sources:
    col_s1, col_s2 = st.columns(2)
    mid = len(top_sources) // 2
    with col_s1:
        for src, count in top_sources[:mid + 1]:
            short = src[:45] + "…" if len(src) > 45 else src
            st.markdown(f"**{short}** — {count} uses")
            st.progress(count / top_sources[0][1])
    with col_s2:
        for src, count in top_sources[mid + 1:]:
            short = src[:45] + "…" if len(src) > 45 else src
            st.markdown(f"**{short}** — {count} uses")
            st.progress(count / top_sources[0][1])

st.markdown("---")

# ── Row 4: Daily activity ──────────────────────────────────────────────────────
if len(dates) > 1:
    st.subheader("📅 Daily Activity")
    for date, count in sorted(dates.items()):
        st.markdown(f"**{date}** — {count} questions")
        st.progress(count / max(dates.values()))
    st.markdown("---")

# ── Row 5: Recent conversations ───────────────────────────────────────────────
st.subheader("💬 Recent Conversations")
for r in rows[-10:][::-1]:
    with st.expander(f"🕐 {r['time']} — {r['question'][:60]}..."):
        st.markdown(f"**Topic:** {r['topic_category']}")
        st.markdown(f"**Language:** {lang_labels.get(r['language_detected'], r['language_detected'])}")
        st.markdown(f"**Response time:** {r['response_time_seconds']}s")
        st.markdown(f"**Answer length:** {r['answer_length_words']} words")
        st.markdown(f"**Sources:** {r['sources']}")
        st.markdown("**Answer preview:**")
        st.info(r['answer'][:300] + "...")

st.markdown("---")

# ── Row 6: Download ────────────────────────────────────────────────────────────
st.subheader("📥 Export Data")
col_d1 = st.columns(1)[0]

with col_d1:
    with open(LOG_FILE, "rb") as f:
        st.download_button(
            "📥 Download Full Conversation Log (CSV)",
            data=f,
            file_name="msme_conversations.csv",
            mime="text/csv",
            use_container_width=True,
        )


st.caption("Dashboard auto-refreshes with each new conversation logged.")
