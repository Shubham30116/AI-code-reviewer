import streamlit as st
import json
from reviewer import review_code, chat_about_code
from utils import detect_language, read_uploaded_file, add_line_numbers, score_color, score_label, severity_color, severity_bg, count_issues
from history import save_review, load_history, load_review_by_id, delete_review

st.set_page_config(page_title="AI Code Reviewer", page_icon="🔍", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

.hero { padding: 2rem 0 1rem; border-bottom: 0.5px solid #e5e5e5; margin-bottom: 1.5rem; }
.hero h1 { font-size: 26px; font-weight: 600; margin: 0 0 4px; letter-spacing: -0.5px; }
.hero p { font-size: 14px; color: #888; margin: 0; }

.score-ring { text-align: center; padding: 1.5rem 0; }
.score-num { font-size: 52px; font-weight: 700; line-height: 1; }
.score-sub { font-size: 13px; color: #888; margin-top: 6px; }

.cat-card { background: #fff; border: 0.5px solid #e8e8e5; border-radius: 12px; padding: 14px 16px; margin-bottom: 10px; }
.cat-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.cat-name { font-size: 14px; font-weight: 500; }
.cat-score { font-size: 13px; font-weight: 600; }
.progress-bar { height: 4px; border-radius: 2px; background: #f0f0ee; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 2px; }

.issue-card { border-left: 3px solid; border-radius: 0 8px 8px 0; padding: 10px 14px; margin: 8px 0; }
.issue-title { font-size: 13px; font-weight: 500; margin-bottom: 3px; }
.issue-desc { font-size: 12px; color: #666; margin-bottom: 6px; line-height: 1.5; }
.issue-fix { font-size: 12px; background: #f8f8f6; border-radius: 6px; padding: 6px 10px; line-height: 1.5; }
.line-badge { font-size: 11px; font-family: 'JetBrains Mono', monospace; background: #f1efe8; color: #5f5e5a; border-radius: 4px; padding: 1px 6px; margin-left: 6px; }

.strength-item { display: flex; align-items: flex-start; gap: 8px; padding: 6px 0; font-size: 13px; color: #444; border-bottom: 0.5px solid #f0f0ee; }
.priority-item { display: flex; align-items: flex-start; gap: 8px; padding: 6px 0; font-size: 13px; color: #444; border-bottom: 0.5px solid #f0f0ee; }

.metric-box { background: #f8f8f6; border-radius: 10px; padding: 14px; text-align: center; }
.metric-num { font-size: 24px; font-weight: 600; }
.metric-label { font-size: 12px; color: #888; margin-top: 2px; }

.history-row { display: flex; align-items: center; gap: 10px; padding: 10px 14px; border: 0.5px solid #e8e8e5; border-radius: 10px; margin-bottom: 8px; cursor: pointer; transition: background 0.1s; }
.history-row:hover { background: #fafaf8; }

.code-block { font-family: 'JetBrains Mono', monospace; font-size: 12px; background: #1e1e2e; color: #cdd6f4; border-radius: 10px; padding: 16px; overflow-x: auto; white-space: pre; line-height: 1.6; }

.chat-msg-user { background: #534AB7; color: #fff; border-radius: 12px 12px 2px 12px; padding: 10px 14px; font-size: 13px; margin: 6px 0 6px auto; max-width: 80%; }
.chat-msg-ai { background: #f1efe8; color: #2c2c2a; border-radius: 12px 12px 12px 2px; padding: 10px 14px; font-size: 13px; margin: 6px auto 6px 0; max-width: 90%; line-height: 1.6; }

.tag-lang { font-size: 11px; font-weight: 500; background: #EEEDFE; color: #3C3489; border-radius: 20px; padding: 2px 10px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key = st.text_input("Gemini API Key", type="password", placeholder="AIzaSy...")
    st.caption("Get your key at [aistudio.google.com](https://console.anthropic.com)")
    st.divider()
    page = st.radio("Navigate", ["🔍 Review Code", "💬 Chat with Code", "🕓 History"], label_visibility="collapsed")
    st.divider()
    st.markdown("**Sample code to try**")
    if st.button("Load Python sample"):
        st.session_state["sample_code"] = '''import sqlite3

def get_user(username, password):
    conn = sqlite3.connect("users.db")
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
    result = conn.execute(query).fetchone()
    conn.close()
    return result

def calculate_total(items):
    total = 0
    for i in range(len(items)):
        total = total + items[i]["price"] * items[i]["qty"]
    return total

def load_data(filename):
    f = open(filename)
    data = f.read()
    return data

API_KEY = "sk-abc123supersecret"
DEBUG = True
'''

# ── Session state ─────────────────────────────────────────────────────────────
if "review_result" not in st.session_state:
    st.session_state["review_result"] = None
if "review_code_text" not in st.session_state:
    st.session_state["review_code_text"] = ""
if "review_language" not in st.session_state:
    st.session_state["review_language"] = ""
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "sample_code" not in st.session_state:
    st.session_state["sample_code"] = ""

# ════════════════════════════════════════════════════════════════════════════
# PAGE: REVIEW CODE
# ════════════════════════════════════════════════════════════════════════════
if "Review" in page:
    st.markdown("""
    <div class="hero">
      <h1>AI Code Reviewer</h1>
      <p>Paste your code and get instant feedback on bugs, quality, security, and performance.</p>
    </div>
    """, unsafe_allow_html=True)

    col_in, col_out = st.columns([1, 1], gap="large")

    with col_in:
        st.markdown("#### Your code")
        uploaded = st.file_uploader("Upload a file", type=["py","js","ts","java","cpp","c","cs","go","rb","php","sql","sh"], label_visibility="collapsed")

        default_code = st.session_state.get("sample_code", "")
        if uploaded:
            default_code, detected_lang = read_uploaded_file(uploaded)

        code_input = st.text_area("Paste code here", value=default_code, height=340,
                                   placeholder="# Paste your code here...", label_visibility="collapsed")

        lang_options = ["Auto-detect", "Python", "JavaScript", "TypeScript", "Java", "C++", "C", "C#", "Go", "Rust", "Ruby", "PHP", "SQL", "Bash"]
        lang_choice = st.selectbox("Language", lang_options)
        language = detect_language(code_input) if lang_choice == "Auto-detect" else lang_choice

        st.markdown(f"Detected: <span class='tag-lang'>{language}</span>", unsafe_allow_html=True)

        run_btn = st.button("🔍 Review Code", type="primary", use_container_width=True, disabled=not api_key)
        if not api_key:
            st.caption("⬅️ Enter your API key in the sidebar to get started.")

    with col_out:
        if run_btn and code_input.strip():
            with st.spinner("Reviewing your code..."):
                try:
                    result = review_code(code_input.strip(), language, api_key)
                    st.session_state["review_result"] = result
                    st.session_state["review_code_text"] = code_input.strip()
                    st.session_state["review_language"] = language
                    st.session_state["chat_history"] = []
                    save_review(language, code_input.strip(), result)
                except Exception as e:
                    st.error(f"Error: {e}")

        result = st.session_state.get("review_result")
        if result:
            score = result.get("overall_score", 0)
            color = score_color(score)
            label = score_label(score)
            counts = count_issues(result)

            st.markdown(f"""
            <div class="score-ring">
              <div class="score-num" style="color:{color}">{score}</div>
              <div class="score-sub">{label} · overall score out of 100</div>
            </div>
            """, unsafe_allow_html=True)

            # Metrics row
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f'<div class="metric-box"><div class="metric-num" style="color:#E24B4A">{counts["high"]}</div><div class="metric-label">Critical</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-box"><div class="metric-num" style="color:#EF9F27">{counts["medium"]}</div><div class="metric-label">Warnings</div></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="metric-box"><div class="metric-num" style="color:#378ADD">{counts["low"]}</div><div class="metric-label">Suggestions</div></div>', unsafe_allow_html=True)
            with m4:
                total = sum(counts.values())
                st.markdown(f'<div class="metric-box"><div class="metric-num">{total}</div><div class="metric-label">Total issues</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Summary
            st.info(result.get("summary", ""))

            # Tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📋 Issues", "✅ Strengths", "🔧 Improved code", "📊 Scores"])

            with tab1:
                cat_labels = {
                    "bugs": "🐛 Bugs",
                    "code_quality": "📐 Code quality",
                    "security": "🔒 Security",
                    "performance": "⚡ Performance",
                    "best_practices": "📚 Best practices"
                }
                categories = result.get("categories", {})
                any_issues = False
                for cat_key, cat_label in cat_labels.items():
                    cat = categories.get(cat_key, {})
                    issues = cat.get("issues", [])
                    if issues:
                        any_issues = True
                        with st.expander(f"{cat_label} — {len(issues)} issue(s)", expanded=cat_key == "bugs"):
                            for issue in issues:
                                sev = issue.get("severity", "low")
                                line = issue.get("line")
                                line_badge = f"<span class='line-badge'>line {line}</span>" if line else ""
                                st.markdown(f"""
                                <div class="issue-card" style="border-left-color:{severity_color(sev)}; background:{severity_bg(sev)}">
                                  <div class="issue-title">{issue.get('title','')}{line_badge}</div>
                                  <div class="issue-desc">{issue.get('description','')}</div>
                                  <div class="issue-fix">💡 {issue.get('fix','')}</div>
                                </div>
                                """, unsafe_allow_html=True)
                if not any_issues:
                    st.success("No issues found — great code!")

            with tab2:
                strengths = result.get("key_strengths", [])
                priorities = result.get("top_priorities", [])
                if strengths:
                    st.markdown("**What's working well**")
                    for s in strengths:
                        st.markdown(f'<div class="strength-item">✅ {s}</div>', unsafe_allow_html=True)
                if priorities:
                    st.markdown("<br>**Top priorities to fix**", unsafe_allow_html=True)
                    for i, p in enumerate(priorities, 1):
                        st.markdown(f'<div class="priority-item">🔴 {p}</div>', unsafe_allow_html=True)

            with tab3:
                improved = result.get("improved_code", "")
                if improved:
                    st.markdown(f'<div class="code-block">{improved}</div>', unsafe_allow_html=True)
                    st.download_button("⬇️ Download improved code",
                                       data=improved,
                                       file_name=f"improved_code.{st.session_state['review_language'].lower()[:2]}",
                                       mime="text/plain")
                else:
                    st.info("No improved version generated.")

            with tab4:
                categories = result.get("categories", {})
                cat_names = {
                    "bugs": "Bugs", "code_quality": "Code quality",
                    "security": "Security", "performance": "Performance",
                    "best_practices": "Best practices"
                }
                for cat_key, cat_name in cat_names.items():
                    cat = categories.get(cat_key, {})
                    s = cat.get("score", 100)
                    c = score_color(s)
                    st.markdown(f"""
                    <div class="cat-card">
                      <div class="cat-header">
                        <span class="cat-name">{cat_name}</span>
                        <span class="cat-score" style="color:{c}">{s}/100</span>
                      </div>
                      <div class="progress-bar">
                        <div class="progress-fill" style="width:{s}%; background:{c};"></div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center; padding: 4rem 2rem; color: #aaa;">
              <div style="font-size:40px; margin-bottom:12px;">🔍</div>
              <div style="font-size:15px;">Your review will appear here</div>
              <div style="font-size:13px; margin-top:6px;">Paste code on the left and click Review</div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE: CHAT WITH CODE
# ════════════════════════════════════════════════════════════════════════════
elif "Chat" in page:
    st.markdown("""
    <div class="hero">
      <h1>Chat with your code</h1>
      <p>Ask follow-up questions about the review — like having a senior dev on call.</p>
    </div>
    """, unsafe_allow_html=True)

    result = st.session_state.get("review_result")
    if not result:
        st.info("Run a code review first, then come back here to chat about it.")
    else:
        lang = st.session_state.get("review_language", "")
        code = st.session_state.get("review_code_text", "")
        st.markdown(f"Reviewing: <span class='tag-lang'>{lang}</span> · score {result.get('overall_score')}/100", unsafe_allow_html=True)
        st.markdown(f"_{result.get('summary', '')}_")
        st.divider()

        # Suggestions
        suggestions = [
            "How do I fix the SQL injection vulnerability?",
            "Rewrite the worst function with best practices",
            "What's the biggest security risk in this code?",
            "Explain the performance issue in simple terms",
        ]
        st.markdown("**Quick questions:**")
        cols = st.columns(2)
        for i, s in enumerate(suggestions):
            if cols[i % 2].button(s, key=f"sug_{i}"):
                st.session_state["chat_prefill"] = s

        st.divider()

        # Chat history
        for msg in st.session_state["chat_history"]:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-msg-ai">{msg["content"]}</div>', unsafe_allow_html=True)

        prefill = st.session_state.pop("chat_prefill", "")
        question = st.text_input("Ask anything about your code...", value=prefill, key="chat_input")
        if st.button("Send", type="primary") and question.strip() and api_key:
            st.session_state["chat_history"].append({"role": "user", "content": question})
            with st.spinner("Thinking..."):
                try:
                    answer = chat_about_code(code, lang, result, question, api_key)
                    st.session_state["chat_history"].append({"role": "assistant", "content": answer})
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

# ════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ════════════════════════════════════════════════════════════════════════════
elif "History" in page:
    st.markdown("""
    <div class="hero">
      <h1>Review history</h1>
      <p>All your past code reviews, saved locally.</p>
    </div>
    """, unsafe_allow_html=True)

    rows = load_history()
    if not rows:
        st.info("No reviews yet. Run your first review to see it here.")
    else:
        for row in rows:
            c1, c2 = st.columns([5, 1])
            with c1:
                score = row["overall_score"]
                color = score_color(score)
                st.markdown(f"""
                <div class="history-row">
                  <span class="tag-lang">{row['language']}</span>
                  <span style="font-size:13px;font-weight:500;flex:1">{row['code_snippet'][:60]}...</span>
                  <span style="font-size:13px;color:{color};font-weight:600">{score}/100</span>
                  <span style="font-size:12px;color:#aaa">{row['created_at']}</span>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                if st.button("Load", key=f"load_{row['id']}"):
                    full = load_review_by_id(row["id"])
                    st.session_state["review_result"] = full
                    st.session_state["review_language"] = row["language"]
                    st.session_state["review_code_text"] = row["code_snippet"]
                    st.success("Loaded! Go to Review Code tab.")
                if st.button("🗑", key=f"del_{row['id']}"):
                    delete_review(row["id"])
                    st.rerun()
