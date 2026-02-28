"""PE Tool Suite — Streamlit 앱 (PwC Brand Style)."""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
from datetime import datetime

from packages.agents.orchestrator import run as orchestrator_run
from packages.agents.legal_agent import run as legal_basic_run
from packages.agents.legal_deep_agent import run_deal_killer, run_coc_map, run_indemnity
from packages.agents.accounting_impact_agent import run as accounting_impact_run
from packages.agents.finance_cost_agent import run as finance_cost_run
from packages.report.generator import generate_markdown, generate_html, save_markdown, save_html, save_docx
from packages.report.legal_report import generate_legal_markdown
from packages.rag.chat_engine import answer as rag_answer
from packages.rag.vector_store import initialize_store as init_vector_store

# ─── 페이지 설정 ───
st.set_page_config(
    page_title="PwC PE Tool Suite",
    page_icon="📊",
    layout="wide",
)

# ═══════════════════════════════════════════════════════════════
# PwC Brand CSS — design.txt 기반
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    /* ── PwC Color Variables ── */
    :root {
        --pwc-black: #2D2D2D;
        --pwc-text: #4A4A4A;
        --pwc-yellow: #FFB600;
        --pwc-tangerine: #EB8C00;
        --pwc-orange: #D04A02;
        --pwc-rose: #DB536A;
        --pwc-red: #E0301E;
        --pwc-bg: #F8F9FA;
        --pwc-white: #FFFFFF;
        --pwc-border: #E5E5E5;
        --pwc-gradient: linear-gradient(90deg, #FFB600, #EB8C00, #D04A02, #DB536A, #E0301E);
    }

    /* ── Global Reset ── */
    .stApp {
        font-family: 'Inter', 'Noto Sans KR', -apple-system, sans-serif !important;
        background-color: var(--pwc-bg) !important;
    }
    /* Streamlit 기본 헤더/툴바 숨김 — 상단 잘림 방지 */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    .block-container {
        max-width: 1100px !important;
        padding-top: 2rem !important;
    }

    /* ── Header ── */
    .pwc-header {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 24px 0 16px;
        border-bottom: 3px solid;
        border-image: linear-gradient(90deg, #FFB600, #EB8C00, #D04A02, #DB536A, #E0301E) 1;
        margin-bottom: 24px;
    }
    .pwc-logo {
        width: 56px;
        height: 56px;
        background: var(--pwc-black);
        border-radius: 2px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .pwc-logo-text {
        color: var(--pwc-white);
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .pwc-header-text {
        flex: 1;
    }
    .pwc-header-title {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--pwc-black);
        margin: 0;
        line-height: 1.5;
        padding-top: 4px;
    }
    .pwc-header-subtitle {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        font-size: 0.85rem;
        color: var(--pwc-text);
        margin: 4px 0 0;
    }

    /* ── Step Indicator ── */
    .pwc-step-bar {
        display: flex;
        gap: 0;
        margin-bottom: 28px;
        border-radius: 2px;
        overflow: hidden;
        border: 1px solid var(--pwc-border);
    }
    .pwc-step {
        flex: 1;
        padding: 12px 16px;
        text-align: center;
        font-size: 0.82rem;
        font-weight: 500;
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        transition: all 0.2s ease;
        position: relative;
    }
    .pwc-step-done {
        background: var(--pwc-white);
        color: var(--pwc-text);
        border-right: 1px solid var(--pwc-border);
    }
    .pwc-step-done::before {
        content: "✓ ";
        color: #28A745;
        font-weight: 700;
    }
    .pwc-step-active {
        background: var(--pwc-black);
        color: var(--pwc-white);
        font-weight: 600;
        border-bottom: 3px solid;
        border-image: linear-gradient(90deg, #FFB600, #D04A02, #E0301E) 1;
    }
    .pwc-step-pending {
        background: var(--pwc-bg);
        color: #AAAAAA;
        border-right: 1px solid var(--pwc-border);
    }

    /* ── Card Container ── */
    .pwc-card {
        background: var(--pwc-white);
        border: 1px solid var(--pwc-border);
        border-radius: 2px;
        padding: 32px;
        margin-bottom: 20px;
    }

    /* ── Step Header ── */
    .pwc-section-title {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--pwc-black);
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid var(--pwc-orange);
    }

    /* ── Input Summary (Accordion Header) ── */
    .pwc-summary-header {
        background: var(--pwc-black);
        color: var(--pwc-white);
        padding: 12px 20px;
        border-radius: 2px 2px 0 0;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.3px;
    }

    /* ── Agent Progress ── */
    .pwc-agent-title {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--pwc-orange);
        margin-bottom: 12px;
    }
    .pwc-agent-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 8px 0;
        font-size: 0.9rem;
        color: var(--pwc-text);
        border-bottom: 1px solid #F0F0F0;
    }
    .pwc-agent-done {
        color: #28A745;
        font-weight: 600;
    }
    .pwc-agent-running {
        color: var(--pwc-tangerine);
        font-weight: 600;
    }

    /* ── Progress Bar ── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #FFB600, #EB8C00, #D04A02, #E0301E) !important;
        border-radius: 1px !important;
    }

    /* ── Buttons ── */
    div.stButton > button[kind="primary"],
    div.stButton > button[data-testid="stBaseButton-primary"] {
        background: linear-gradient(90deg, #EB8C00, #D04A02, #E0301E) !important;
        color: white !important;
        border: none !important;
        border-radius: 2px !important;
        font-weight: 600 !important;
        font-family: 'Inter', 'Noto Sans KR', sans-serif !important;
        letter-spacing: 0.3px !important;
        padding: 8px 24px !important;
    }
    div.stButton > button[kind="primary"]:hover,
    div.stButton > button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(90deg, #D04A02, #E0301E, #DB536A) !important;
        box-shadow: 0 2px 8px rgba(208, 74, 2, 0.25) !important;
    }
    div.stButton > button[kind="secondary"],
    div.stButton > button[data-testid="stBaseButton-secondary"] {
        background: var(--pwc-white) !important;
        color: var(--pwc-black) !important;
        border: 1.5px solid var(--pwc-black) !important;
        border-radius: 2px !important;
        font-weight: 500 !important;
        font-family: 'Inter', 'Noto Sans KR', sans-serif !important;
    }
    div.stButton > button[kind="secondary"]:hover,
    div.stButton > button[data-testid="stBaseButton-secondary"]:hover {
        background: var(--pwc-bg) !important;
        border-color: var(--pwc-orange) !important;
        color: var(--pwc-orange) !important;
    }

    /* ── Download Buttons ── */
    div.stDownloadButton > button {
        background: var(--pwc-black) !important;
        color: white !important;
        border: none !important;
        border-radius: 2px !important;
        font-weight: 500 !important;
        font-family: 'Inter', 'Noto Sans KR', sans-serif !important;
    }
    div.stDownloadButton > button:hover {
        background: var(--pwc-orange) !important;
    }

    /* ── Input Fields ── */
    .stSelectbox label, .stTextInput label, .stTextArea label,
    .stRadio label, .stFileUploader label {
        color: var(--pwc-black) !important;
        font-weight: 500 !important;
        font-family: 'Inter', 'Noto Sans KR', sans-serif !important;
        font-size: 0.9rem !important;
    }
    .stTextInput input, .stTextArea textarea {
        border-radius: 2px !important;
        border-color: var(--pwc-border) !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--pwc-orange) !important;
        box-shadow: 0 0 0 1px var(--pwc-orange) !important;
    }
    .stSelectbox > div > div {
        border-radius: 2px !important;
    }

    /* ── Radio as Mini-Cards ── */
    div[data-testid="stRadio"] > div {
        gap: 8px !important;
    }
    div[data-testid="stRadio"] > div > label {
        background: var(--pwc-white) !important;
        border: 1px solid var(--pwc-border) !important;
        border-radius: 2px !important;
        padding: 10px 16px !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="stRadio"] > div > label:hover {
        border-color: var(--pwc-tangerine) !important;
    }
    div[data-testid="stRadio"] > div > label[data-checked="true"],
    div[data-testid="stRadio"] > div > label:has(input:checked) {
        border-color: var(--pwc-orange) !important;
        border-width: 2px !important;
        background: #FFF8F3 !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] button {
        font-family: 'Inter', 'Noto Sans KR', sans-serif !important;
        border-radius: 0 !important;
    }
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: var(--pwc-orange) !important;
        border-bottom: 2px solid var(--pwc-orange) !important;
        font-weight: 600 !important;
    }

    /* ── Alerts ── */
    div[data-testid="stAlert"] {
        border-radius: 2px !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        font-family: 'Inter', 'Noto Sans KR', sans-serif !important;
        font-weight: 600 !important;
        color: var(--pwc-black) !important;
    }

    /* ── Divider ── */
    hr {
        border-color: var(--pwc-border) !important;
    }

    /* ── Landing Page Hero ── */
    .pwc-landing-hero {
        text-align: center;
        padding: 48px 20px 36px;
    }
    .pwc-landing-hero h1 {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--pwc-black);
        margin: 0 0 12px;
    }
    .pwc-landing-hero p {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        font-size: 1.05rem;
        color: var(--pwc-text);
        margin: 0;
        line-height: 1.6;
    }

    /* ── Module Cards ── */
    .pwc-module-card {
        background: var(--pwc-white);
        border: 1px solid var(--pwc-border);
        border-radius: 2px;
        padding: 32px 24px 24px;
        text-align: center;
        transition: all 0.2s ease;
        height: 100%;
    }
    .pwc-module-card:hover {
        border-color: var(--pwc-tangerine);
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }
    .pwc-module-card .card-icon {
        font-size: 2.4rem;
        margin-bottom: 16px;
    }
    .pwc-module-card .card-title {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--pwc-black);
        margin-bottom: 10px;
    }
    .pwc-module-card .card-desc {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        font-size: 0.88rem;
        color: var(--pwc-text);
        line-height: 1.6;
        margin-bottom: 20px;
    }

    /* ── Chatbot Layout (ChatGPT-style) ── */
    .chatbot-container {
        display: flex;
        flex-direction: column;
        height: calc(100vh - 160px);
        max-height: calc(100vh - 160px);
        overflow: hidden;
    }
    .chatbot-header-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid var(--pwc-border);
        margin-bottom: 0;
        flex-shrink: 0;
    }
    .chatbot-header-bar .title {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--pwc-black);
    }
    .chatbot-header-bar .subtitle {
        font-size: 0.8rem;
        color: var(--pwc-text);
        margin-left: 12px;
        font-weight: 400;
    }
    .chatbot-welcome {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 80px 20px 40px;
        text-align: center;
        flex: 1;
    }
    .chatbot-welcome .icon {
        font-size: 3rem;
        margin-bottom: 20px;
    }
    .chatbot-welcome h2 {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--pwc-black);
        margin: 0 0 10px;
    }
    .chatbot-welcome p {
        font-size: 0.9rem;
        color: var(--pwc-text);
        line-height: 1.6;
        margin: 0 0 28px;
        max-width: 480px;
    }
    .chatbot-suggestions {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        justify-content: center;
        max-width: 600px;
    }
    .chatbot-suggestions .chip {
        background: var(--pwc-white);
        border: 1px solid var(--pwc-border);
        border-radius: 20px;
        padding: 8px 18px;
        font-size: 0.82rem;
        color: var(--pwc-text);
        cursor: default;
        transition: all 0.15s ease;
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
    }
    .chatbot-suggestions .chip:hover {
        border-color: var(--pwc-tangerine);
        color: var(--pwc-orange);
    }

    /* ── Sidebar (accounting chatbot only) ── */
    [data-testid="stSidebar"] {
        background: var(--pwc-white) !important;
        border-right: 1px solid var(--pwc-border) !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
        display: none !important;
    }

    /* sidebar buttons — secondary (chat list) */
    [data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
        background: transparent !important;
        color: var(--pwc-text) !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Inter', 'Noto Sans KR', sans-serif !important;
        font-size: 0.84rem !important;
        font-weight: 400 !important;
        padding: 9px 12px !important;
        text-align: left !important;
    }
    [data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
        background: var(--pwc-bg) !important;
    }

    /* sidebar buttons — primary (new chat / active chat) */
    [data-testid="stSidebar"] div.stButton > button[kind="primary"],
    [data-testid="stSidebar"] div.stButton > button[data-testid="stBaseButton-primary"] {
        background: var(--pwc-black) !important;
        color: var(--pwc-white) !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'Inter', 'Noto Sans KR', sans-serif !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        padding: 9px 12px !important;
        text-align: left !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover,
    [data-testid="stSidebar"] div.stButton > button[data-testid="stBaseButton-primary"]:hover {
        background: var(--pwc-orange) !important;
    }

    /* sidebar inputs */
    [data-testid="stSidebar"] .stTextInput label {
        color: var(--pwc-text) !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] .stTextInput input {
        font-size: 0.82rem !important;
        border-radius: 6px !important;
        background: var(--pwc-bg) !important;
        border-color: var(--pwc-border) !important;
    }
    [data-testid="stSidebar"] hr {
        margin: 8px 0 !important;
        border-color: #EBEBEB !important;
    }

    /* LLM connection status */
    .sb-status {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.78rem;
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        padding: 2px 4px;
    }
    .sb-status .dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        flex-shrink: 0;
    }
    .sb-status .dot.on  { background: #28A745; }
    .sb-status .dot.off { background: #E0301E; }

    /* suggestion chip buttons */
    .chatbot-welcome + div [data-testid="stHorizontalBlock"] button {
        background: var(--pwc-white) !important;
        border: 1px solid var(--pwc-border) !important;
        border-radius: 20px !important;
        color: var(--pwc-text) !important;
        font-size: 0.82rem !important;
        font-weight: 400 !important;
        padding: 8px 12px !important;
        font-family: 'Inter', 'Noto Sans KR', sans-serif !important;
    }
    .chatbot-welcome + div [data-testid="stHorizontalBlock"] button:hover {
        border-color: var(--pwc-tangerine) !important;
        color: var(--pwc-orange) !important;
        background: var(--pwc-white) !important;
        box-shadow: none !important;
    }

    /* hide default Streamlit chat avatar for cleaner look */
    [data-testid="stChatMessage"] {
        max-width: 800px;
        margin: 0 auto;
    }

    /* chat input fixed at bottom */
    [data-testid="stChatInput"] {
        max-width: 800px !important;
        margin: 0 auto !important;
    }
    [data-testid="stChatInput"] textarea {
        border-radius: 24px !important;
        padding: 12px 20px !important;
        border-color: var(--pwc-border) !important;
        font-family: 'Inter', 'Noto Sans KR', sans-serif !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: var(--pwc-orange) !important;
        box-shadow: 0 0 0 1px var(--pwc-orange) !important;
    }

    /* back button minimal style for chatbot */
    .chatbot-back-btn {
        position: absolute;
        top: 0;
        left: 0;
    }

    /* ── Coming Soon Badge ── */
    .pwc-coming-soon {
        display: inline-block;
        background: linear-gradient(90deg, #FFB600, #EB8C00);
        color: white;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 14px;
        border-radius: 12px;
        letter-spacing: 0.5px;
        font-family: 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# ─── 사이드바: 회계 모듈에서만 표시 ───
if st.session_state.get("module") != "accounting":
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# ─── 세션 상태 초기화 ───
if "module" not in st.session_state:
    st.session_state.module = None  # None=랜딩, "investment", "legal", "accounting"
if "step" not in st.session_state:
    st.session_state.step = 1
if "report_html" not in st.session_state:
    st.session_state.report_html = None
if "report_generated" not in st.session_state:
    st.session_state.report_generated = False


# ═══════════════════════════════════════════
# 랜딩 페이지 — 모듈 선택
# ═══════════════════════════════════════════
if st.session_state.module is None:
    # 헤더
    st.markdown("""
    <div class="pwc-header">
        <div class="pwc-logo">
            <span class="pwc-logo-text">PwC</span>
        </div>
        <div class="pwc-header-text">
            <div class="pwc-header-title">PE Tool Suite</div>
            <div class="pwc-header-subtitle">Private Equity 투자 프로세스를 위한 통합 도구 모음</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 히어로 섹션
    st.markdown("""
    <div class="pwc-landing-hero">
        <h1>PE 투자 도구 모음</h1>
        <p>투자 검토부터 법무·회계 실사까지, 필요한 모듈을 선택하세요.</p>
    </div>
    """, unsafe_allow_html=True)

    # 3열 카드 그리드
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown("""
        <div class="pwc-module-card">
            <div class="card-icon">📊</div>
            <div class="card-title">투자보고서 자동 생성</div>
            <div class="card-desc">투자위원회 수준의 실사 보고서를<br>AI 에이전트가 자동으로 작성합니다.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("투자보고서 시작 →", use_container_width=True, type="primary", key="btn_investment"):
            st.session_state.module = "investment"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="pwc-module-card">
            <div class="card-icon">⚖️</div>
            <div class="card-title">법무 모듈</div>
            <div class="card-desc">법률 실사 및 계약 검토를 위한<br>자동화 도구입니다.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("법무 모듈 →", use_container_width=True, type="primary", key="btn_legal"):
            st.session_state.module = "legal"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="pwc-module-card">
            <div class="card-icon">📑</div>
            <div class="card-title">회계 및 재무 모듈</div>
            <div class="card-desc">재무제표 분석 및 회계 실사를<br>지원하는 도구입니다.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("회계/재무 모듈 →", use_container_width=True, type="primary", key="btn_accounting"):
            st.session_state.module = "accounting"
            st.rerun()


# ═══════════════════════════════════════════
# 법무 모듈 — Legal Deep Dive
# ═══════════════════════════════════════════
elif st.session_state.module == "legal":
    st.markdown("""
    <div class="pwc-header">
        <div class="pwc-logo"><span class="pwc-logo-text">PwC</span></div>
        <div class="pwc-header-text">
            <div class="pwc-header-title">⚖️ 법무 분석 모듈</div>
            <div class="pwc-header-subtitle">PE 투자 딜 법무 실사 및 회계 연계 분석</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← 홈으로 돌아가기", key="legal_back"):
        st.session_state.module = None
        st.session_state.legal_step = 1
        st.rerun()

    # 세션 초기화
    if "legal_step" not in st.session_state:
        st.session_state.legal_step = 1
    if "legal_results" not in st.session_state:
        st.session_state.legal_results = {}

    # Step Indicator
    legal_steps = ["1. 기본정보 입력", "2. 법무 분석", "3. 회계적 영향"]
    step_html = '<div class="pwc-step-bar">'
    for i, label in enumerate(legal_steps, 1):
        if i < st.session_state.legal_step:
            step_html += f'<div class="pwc-step pwc-step-done">{label}</div>'
        elif i == st.session_state.legal_step:
            step_html += f'<div class="pwc-step pwc-step-active">{label}</div>'
        else:
            step_html += f'<div class="pwc-step pwc-step-pending">{label}</div>'
    step_html += '</div>'
    st.markdown(step_html, unsafe_allow_html=True)

    # ── STEP 1: 기본정보 입력 ──
    if st.session_state.legal_step == 1:
        st.markdown('<div class="pwc-section-title">기본정보 및 문서 입력</div>', unsafe_allow_html=True)

        l_company = st.text_input("회사명 *", placeholder="예: 한국테크 주식회사", key="l_company")
        l_industry = st.text_input("업종 *", placeholder="예: B2B SaaS, 제조, 헬스케어 등", key="l_industry")
        l_purpose = st.selectbox(
            "투자 목적",
            ["성장 (Growth)", "턴어라운드 (Turnaround)", "볼트온 (Bolt-on)"],
            key="l_purpose",
        )

        l_memo = st.text_area(
            "법무 관련 메모",
            placeholder="계약서 핵심 조항, 알려진 법적 이슈, 검토 요청 사항 등을 입력하세요...",
            height=150,
            key="l_memo",
        )

        l_file = st.file_uploader(
            "계약서/법무 문서 업로드 (txt)",
            type=["txt"],
            help="계약서 텍스트 파일을 업로드하면 분석에 활용합니다.",
            key="l_file",
        )
        l_uploaded = ""
        if l_file is not None:
            l_uploaded = l_file.read().decode("utf-8", errors="replace")
            with st.expander("업로드 파일 미리보기"):
                st.text(l_uploaded[:3000])

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        l_deep_dive = st.checkbox(
            "**Legal Deep Dive** 활성화 (Deal Killer / CoC Map / Indemnity 심층 분석)",
            value=True,
            key="l_deep_dive",
        )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col3:
            if st.button("분석 시작 →", use_container_width=True, type="primary", key="legal_start"):
                if not l_company or not l_industry:
                    st.error("회사명과 업종을 모두 입력해주세요.")
                else:
                    st.session_state.legal_context = {
                        "company_name": l_company,
                        "industry": l_industry,
                        "investment_purpose": l_purpose,
                        "memo": l_memo,
                        "uploaded_text": l_uploaded,
                    }
                    st.session_state.legal_deep_dive = l_deep_dive
                    st.session_state.legal_results = {}
                    st.session_state.legal_step = 2
                    st.rerun()

    # ── STEP 2: 법무 분석 실행 & 결과 ──
    elif st.session_state.legal_step == 2:
        st.markdown('<div class="pwc-section-title">법무 분석 결과</div>', unsafe_allow_html=True)
        ctx = st.session_state.legal_context
        deep = st.session_state.legal_deep_dive
        results = st.session_state.legal_results

        # 아직 분석 안 했으면 실행
        if not results.get("_done"):
            progress = st.empty()
            pbar = st.progress(0)

            if deep:
                # Deep Dive: 3개 분석 순차 실행
                progress.markdown("**Deal Killer 분석 중...**")
                pbar.progress(0.1)
                results["deal_killer"] = run_deal_killer(ctx)
                pbar.progress(0.33)

                progress.markdown("**Change of Control Map 분석 중...**")
                results["coc_map"] = run_coc_map(ctx)
                pbar.progress(0.66)

                progress.markdown("**Indemnity Summary 분석 중...**")
                results["indemnity"] = run_indemnity(ctx)
                pbar.progress(1.0)
                results["deep_dive"] = True
            else:
                # 간단 분석
                progress.markdown("**법무 기본 분석 중...**")
                pbar.progress(0.3)
                results["basic"] = legal_basic_run(ctx)
                pbar.progress(1.0)
                results["deep_dive"] = False

            results["_done"] = True
            progress.markdown(
                '<div style="color:#28A745;font-weight:600;">✓ 법무 분석 완료</div>',
                unsafe_allow_html=True,
            )
            st.session_state.legal_results = results

        # 결과 표시
        if results.get("deep_dive"):
            tab1, tab2, tab3 = st.tabs(["Deal Killer", "CoC / Assignment Map", "Indemnity Summary"])
            with tab1:
                st.markdown(results.get("deal_killer", ""))
            with tab2:
                st.markdown(results.get("coc_map", ""))
            with tab3:
                st.markdown(results.get("indemnity", ""))
        else:
            st.markdown(results.get("basic", ""))

        # 하단 버튼
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("← 입력 수정", use_container_width=True, key="legal_back_step1"):
                st.session_state.legal_step = 1
                st.session_state.legal_results = {}
                st.rerun()
        with col2:
            # 마크다운 다운로드
            md = generate_legal_markdown(ctx, results)
            st.download_button(
                "분석 결과 다운로드 (MD)",
                data=md,
                file_name=f"{ctx['company_name']}_법무분석_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col3:
            if st.button("회계적 영향 분석 →", use_container_width=True, type="primary", key="legal_to_impact"):
                st.session_state.legal_step = 3
                st.rerun()

    # ── STEP 3: 회계적 영향 분석 ──
    elif st.session_state.legal_step == 3:
        st.markdown('<div class="pwc-section-title">회계적 영향 분석 (Accounting Impact)</div>', unsafe_allow_html=True)
        ctx = st.session_state.legal_context
        results = st.session_state.legal_results

        if not results.get("accounting_impact"):
            # 법무 결과 합치기
            if results.get("deep_dive"):
                legal_combined = "\n\n".join([
                    results.get("deal_killer", ""),
                    results.get("coc_map", ""),
                    results.get("indemnity", ""),
                ])
            else:
                legal_combined = results.get("basic", "")

            # Finance 분석 (선택적)
            finance_result = ""
            with st.spinner("재무 분석 실행 중..."):
                try:
                    finance_result = finance_cost_run(ctx)
                except Exception:
                    pass

            with st.spinner("회계적 영향 분석 중..."):
                impact = accounting_impact_run(legal_combined, finance_result, ctx)

            results["accounting_impact"] = impact
            results["finance_result"] = finance_result
            st.session_state.legal_results = results

        st.markdown(results["accounting_impact"])

        # 하단 버튼
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("← 법무 분석 결과", use_container_width=True, key="legal_back_step2"):
                st.session_state.legal_step = 2
                st.rerun()
        with col2:
            md = generate_legal_markdown(ctx, results)
            st.download_button(
                "전체 보고서 다운로드 (MD)",
                data=md,
                file_name=f"{ctx['company_name']}_법무_회계분석_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col3:
            if st.button("새 분석 시작", use_container_width=True, key="legal_restart"):
                st.session_state.legal_step = 1
                st.session_state.legal_results = {}
                st.rerun()


# ═══════════════════════════════════════════
# 회계/재무 모듈 — 질의회신 RAG 챗봇 (ChatGPT-style)
# ═══════════════════════════════════════════
elif st.session_state.module == "accounting":
    # ── 멀티 세션 초기화 ──
    if "acc_chats" not in st.session_state:
        # {chat_id: {"title": str, "messages": [], "sources": {}}}
        st.session_state.acc_chats = {}
    if "acc_current_chat" not in st.session_state:
        st.session_state.acc_current_chat = None  # None = 새 대화 (웰컴 화면)

    def _get_current_messages():
        cid = st.session_state.acc_current_chat
        if cid and cid in st.session_state.acc_chats:
            return st.session_state.acc_chats[cid]["messages"]
        return []

    def _get_current_sources():
        cid = st.session_state.acc_current_chat
        if cid and cid in st.session_state.acc_chats:
            return st.session_state.acc_chats[cid]["sources"]
        return {}

    def _create_chat(first_message: str) -> str:
        import time
        chat_id = f"chat_{int(time.time() * 1000)}"
        title = first_message[:30] + ("..." if len(first_message) > 30 else "")
        st.session_state.acc_chats[chat_id] = {
            "title": title,
            "messages": [],
            "sources": {},
        }
        st.session_state.acc_current_chat = chat_id
        return chat_id

    # ── 사이드바 ──
    with st.sidebar:
        # 새 대화 버튼
        if st.button("＋  새 대화", key="new_chat", use_container_width=True, type="primary"):
            st.session_state.acc_current_chat = None
            st.rerun()

        st.markdown("---")

        # 채팅 목록
        chat_ids = list(st.session_state.acc_chats.keys())
        if chat_ids:
            st.caption("대화 목록")
            for cid in reversed(chat_ids):
                chat = st.session_state.acc_chats[cid]
                is_active = (cid == st.session_state.acc_current_chat)
                if st.button(
                    chat['title'],
                    key=f"sel_{cid}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    st.session_state.acc_current_chat = cid
                    st.rerun()

            st.markdown("---")

        # LLM 설정
        st.caption("LLM 설정")

        import os
        default_key = os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", ""))
        default_model = os.getenv("LLM_MODEL", os.getenv("OPENAI_MODEL", "gpt-4"))
        default_base = os.getenv("LLM_BASE_URL", os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1"))

        api_key = st.text_input(
            "API Key",
            value=st.session_state.get("acc_api_key", default_key),
            type="password",
            key="input_api_key",
        )
        api_model = st.text_input(
            "Model",
            value=st.session_state.get("acc_api_model", default_model),
            key="input_api_model",
            help="gpt-4o, gemini-2.0-flash, claude-sonnet-4-20250514, llama3.1:8b 등",
        )
        api_base = st.text_input(
            "Base URL",
            value=st.session_state.get("acc_api_base", default_base),
            key="input_api_base",
        )

        # 세션에 저장 + 환경변수 반영 (llm_client가 즉시 참조)
        st.session_state.acc_api_key = api_key
        st.session_state.acc_api_model = api_model
        st.session_state.acc_api_base = api_base
        os.environ["LLM_API_KEY"] = api_key
        os.environ["LLM_MODEL"] = api_model
        os.environ["LLM_BASE_URL"] = api_base

        # 연결 상태 표시
        is_connected = bool(api_key and len(api_key) > 3)
        dot_cls = "on" if is_connected else "off"
        label = api_model if is_connected else "미연결"
        st.markdown(
            f'<div class="sb-status"><span class="dot {dot_cls}"></span> {label}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # 홈 버튼
        if st.button("← 홈으로 돌아가기", key="acc_back_sidebar", use_container_width=True):
            st.session_state.module = None
            st.rerun()

    # ── 메인 영역: 헤더 ──
    st.markdown("""
    <div class="chatbot-header-bar">
        <div>
            <span class="title">📑 회계 질의회신 챗봇</span>
            <span class="subtitle">K-IFRS 질의회신 기반 회계 자문 AI</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 벡터 스토어 초기화 (최초 1회)
    if "acc_vectorstore_ready" not in st.session_state:
        with st.spinner("질의회신 데이터베이스를 준비하고 있습니다..."):
            count = init_vector_store()
        st.session_state.acc_vectorstore_ready = True

    current_messages = _get_current_messages()
    current_sources = _get_current_sources()

    # ── 대화가 없을 때: 웰컴 + 추천 질문 ──
    if not current_messages and "acc_pending_query" not in st.session_state:
        st.markdown("""
        <div class="chatbot-welcome">
            <div class="icon">📑</div>
            <h2>회계 질의회신 챗봇</h2>
            <p>한국채택국제회계기준(K-IFRS) 관련 질문을 입력하면,<br>
            질의회신 데이터베이스에서 관련 내용을 검색하여 근거 기반 답변을 제공합니다.</p>
        </div>
        """, unsafe_allow_html=True)

        suggestions = [
            "건설계약에서 진행기준 수익인식 방법은?",
            "전환사채 발행 시 전환권 회계처리는?",
            "리스변경이 발생한 경우 회계처리는?",
            "이연법인세 자산의 인식 요건은?",
        ]
        chip_cols = st.columns(len(suggestions))
        for idx, (col, text) in enumerate(zip(chip_cols, suggestions)):
            with col:
                if st.button(text, key=f"chip_{idx}", use_container_width=True):
                    st.session_state.acc_pending_query = text
                    st.rerun()

    # ── 대화 히스토리 표시 ──
    for i, msg in enumerate(current_messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and str(i) in current_sources:
                sources = current_sources[str(i)]
                with st.expander("참고 질의회신", expanded=False):
                    for src in sources:
                        st.markdown(
                            f"**[{src['category']}]** {src['source']} ({src['date']})\n\n"
                            f"> {src['question']}"
                        )

    # ── 사용자 입력 ──
    pending = st.session_state.pop("acc_pending_query", None)
    prompt = pending or st.chat_input("회계 관련 질문을 입력하세요...")
    if prompt:
        # 현재 채팅이 없으면 새로 생성
        if st.session_state.acc_current_chat is None:
            _create_chat(prompt)

        chat_data = st.session_state.acc_chats[st.session_state.acc_current_chat]
        chat_data["messages"].append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("질의회신을 검색하고 답변을 생성하고 있습니다..."):
                result = rag_answer(prompt, chat_data["messages"][:-1])

            st.markdown(result["answer"])

            if result["sources"]:
                with st.expander("참고 질의회신", expanded=False):
                    for src in result["sources"]:
                        st.markdown(
                            f"**[{src['category']}]** {src['source']} ({src['date']})\n\n"
                            f"> {src['question']}"
                        )

        msg_idx = len(chat_data["messages"])
        chat_data["messages"].append({"role": "assistant", "content": result["answer"]})
        chat_data["sources"][str(msg_idx)] = result["sources"]


# ═══════════════════════════════════════════
# 투자보고서 모듈 — 기존 4단계 위저드
# ═══════════════════════════════════════════
elif st.session_state.module == "investment":
    # 헤더
    st.markdown("""
    <div class="pwc-header">
        <div class="pwc-logo"><span class="pwc-logo-text">PwC</span></div>
        <div class="pwc-header-text">
            <div class="pwc-header-title">PE 투자보고서 자동 생성 시스템</div>
            <div class="pwc-header-subtitle">투자위원회 수준의 보고서를 자동으로 생성합니다</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← 홈으로 돌아가기", key="back_home_investment"):
        st.session_state.module = None
        st.session_state.step = 1
        st.session_state.report_generated = False
        st.session_state.report_html = None
        st.rerun()

    # Step Indicator
    steps = ["1. 기업 기본정보", "2. 딜 설정", "3. 추가 입력", "4. 보고서 생성"]
    step_html = '<div class="pwc-step-bar">'
    for i, label in enumerate(steps, 1):
        if i < st.session_state.step:
            step_html += f'<div class="pwc-step pwc-step-done">{label}</div>'
        elif i == st.session_state.step:
            step_html += f'<div class="pwc-step pwc-step-active">{label}</div>'
        else:
            step_html += f'<div class="pwc-step pwc-step-pending">{label}</div>'
    step_html += '</div>'
    st.markdown(step_html, unsafe_allow_html=True)

    # ═══════════════════════════════════════════
    # STEP 1: 기업 기본정보
    # ═══════════════════════════════════════════
    if st.session_state.step == 1:
        st.markdown('<div class="pwc-section-title">기업 기본정보</div>', unsafe_allow_html=True)

        company_name = st.text_input("회사명 *", placeholder="예: 한국테크 주식회사")
        industry = st.text_input("업종 *", placeholder="예: B2B SaaS, 제조, 헬스케어 등")

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("다음 단계 →", use_container_width=True, type="primary"):
                if not company_name or not industry:
                    st.error("회사명과 업종을 모두 입력해주세요.")
                else:
                    st.session_state.company_name = company_name
                    st.session_state.industry = industry
                    st.session_state.step = 2
                    st.rerun()

    # ═══════════════════════════════════════════
    # STEP 2: 딜 설정
    # ═══════════════════════════════════════════
    elif st.session_state.step == 2:
        st.markdown('<div class="pwc-section-title">딜 설정 (Deal Preferences)</div>', unsafe_allow_html=True)

        left, right = st.columns(2, gap="large")

        with left:
            investment_purpose = st.selectbox(
                "투자 목적",
                ["성장 (Growth)", "턴어라운드 (Turnaround)", "볼트온 (Bolt-on)"],
            )
            investment_period = st.selectbox(
                "투자 기간",
                ["3년", "5년", "7년", "10년"],
            )
            exit_preference = st.selectbox(
                "엑싯 선호",
                ["IPO", "전략적 매각 (Strategic Sale)", "재무적 매각 (Secondary Buyout)",
                 "부분 매각 (Partial Exit)", "배당 재캡 (Dividend Recap)"],
            )
            risk_preference = st.selectbox(
                "리스크 선호도",
                ["보수적 (Conservative)", "중립 (Neutral)", "공격적 (Aggressive)"],
            )

        with right:
            st.markdown("**보고서 옵션**")
            report_tone = st.selectbox(
                "보고서 톤",
                ["Conservative", "Neutral", "Aggressive"],
                index=1,
                help="문체와 강조점만 변경됩니다",
            )
            checklist_depth = st.selectbox(
                "체크리스트 깊이",
                ["Lite", "Standard", "Deep"],
                index=1,
            )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← 이전", use_container_width=True):
                st.session_state.step = 1
                st.rerun()
        with col3:
            if st.button("다음 단계 →", use_container_width=True, type="primary"):
                st.session_state.investment_purpose = investment_purpose
                st.session_state.investment_period = investment_period
                st.session_state.exit_preference = exit_preference
                st.session_state.risk_preference = risk_preference
                st.session_state.report_tone = report_tone
                st.session_state.checklist_depth = checklist_depth
                st.session_state.step = 3
                st.rerun()

    # ═══════════════════════════════════════════
    # STEP 3: 추가 입력
    # ═══════════════════════════════════════════
    elif st.session_state.step == 3:
        st.markdown('<div class="pwc-section-title">추가 입력 (메모 & 파일)</div>', unsafe_allow_html=True)

        memo = st.text_area(
            "자유 메모",
            placeholder="투자 대상에 대해 알고 있는 정보, 특이사항, 검토 요청 사항 등을 자유롭게 입력하세요...",
            height=180,
        )

        uploaded_file = st.file_uploader(
            "파일 업로드 (txt 지원)",
            type=["txt"],
            help="텍스트 파일을 업로드하면 보고서 작성에 참고합니다.",
        )

        uploaded_text = ""
        if uploaded_file is not None:
            uploaded_text = uploaded_file.read().decode("utf-8", errors="replace")
            with st.expander("업로드된 파일 미리보기"):
                st.text(uploaded_text[:3000])

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="pwc-section-title">보고서 모드 선택</div>', unsafe_allow_html=True)

        output_mode = st.radio(
            "보고서 모드 선택",
            ["IC Memo", "Full DD Report", "Legal + Finance Appendix"],
            captions=[
                "투자위원회용 1페이지 요약 메모",
                "전체 실사 보고서 (모든 에이전트 동원)",
                "법무/재무 부록만 생성",
            ],
            label_visibility="collapsed",
        )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← 이전", use_container_width=True):
                st.session_state.step = 2
                st.rerun()
        with col3:
            if st.button("보고서 생성 →", use_container_width=True, type="primary"):
                st.session_state.memo = memo
                st.session_state.uploaded_text = uploaded_text
                st.session_state.output_mode = output_mode
                st.session_state.step = 4
                st.session_state.report_generated = False
                st.rerun()

    # ═══════════════════════════════════════════
    # STEP 4: 보고서 생성 & 결과
    # ═══════════════════════════════════════════
    elif st.session_state.step == 4:
        st.markdown('<div class="pwc-section-title">보고서 생성</div>', unsafe_allow_html=True)

        # 입력 요약 — PwC Dark Header Accordion
        with st.expander("입력 요약", expanded=False):
            summary_items = [
                ("회사명", st.session_state.get('company_name', '')),
                ("업종", st.session_state.get('industry', '')),
                ("투자 목적", st.session_state.get('investment_purpose', '')),
                ("투자 기간", st.session_state.get('investment_period', '')),
                ("엑싯 선호", st.session_state.get('exit_preference', '')),
                ("리스크 선호", st.session_state.get('risk_preference', '')),
                ("보고서 톤", st.session_state.get('report_tone', '')),
                ("체크리스트 깊이", st.session_state.get('checklist_depth', '')),
                ("보고서 모드", st.session_state.get('output_mode', '')),
            ]
            for label, value in summary_items:
                st.markdown(
                    f"<div style='display:flex;padding:6px 0;border-bottom:1px solid #F0F0F0;font-size:0.88rem;'>"
                    f"<span style='width:140px;color:#999;font-weight:500;'>{label}</span>"
                    f"<span style='color:#2D2D2D;font-weight:500;'>{value}</span></div>",
                    unsafe_allow_html=True,
                )

        if not st.session_state.report_generated:
            # 보고서 생성 실행
            context = {
                "company_name": st.session_state.get("company_name", ""),
                "industry": st.session_state.get("industry", ""),
                "investment_purpose": st.session_state.get("investment_purpose", ""),
                "investment_period": st.session_state.get("investment_period", ""),
                "exit_preference": st.session_state.get("exit_preference", ""),
                "risk_preference": st.session_state.get("risk_preference", ""),
                "report_tone": st.session_state.get("report_tone", "Neutral"),
                "checklist_depth": st.session_state.get("checklist_depth", "Standard"),
                "memo": st.session_state.get("memo", ""),
                "uploaded_text": st.session_state.get("uploaded_text", ""),
            }
            mode = st.session_state.get("output_mode", "Full DD Report")

            # 진행 상태 표시
            progress_container = st.container()
            status_placeholder = progress_container.empty()
            progress_bar = progress_container.progress(0)

            agent_statuses = {}

            def progress_callback(agent_name, status):
                agent_statuses[agent_name] = status
                lines = []
                for k, v in agent_statuses.items():
                    if v == "완료":
                        icon = '<span style="color:#28A745;font-weight:700;">✓</span>'
                        style = 'color:#28A745;font-weight:600;'
                    else:
                        icon = '<span style="color:#EB8C00;font-weight:700;">◉</span>'
                        style = 'color:#EB8C00;font-weight:600;'
                    lines.append(
                        f'<div class="pwc-agent-item">{icon} '
                        f'<span>{k}</span> '
                        f'<span style="{style};margin-left:auto;">{v}</span></div>'
                    )
                html_block = (
                    f'<div class="pwc-agent-title">에이전트 진행 상황</div>'
                    + "".join(lines)
                )
                status_placeholder.markdown(html_block, unsafe_allow_html=True)
                done = sum(1 for v in agent_statuses.values() if v == "완료")
                total = len(agent_statuses)
                progress_bar.progress(done / max(total, 1))

            try:
                st.markdown(
                    '<div style="font-size:0.9rem;color:#D04A02;font-weight:600;margin-bottom:8px;">'
                    '보고서를 생성하고 있습니다...</div>',
                    unsafe_allow_html=True,
                )

                with st.spinner(""):
                    result = orchestrator_run(context, mode, progress_callback)

                progress_bar.progress(1.0)
                status_placeholder.markdown(
                    '<div class="pwc-agent-title" style="color:#28A745;">모든 에이전트 완료</div>',
                    unsafe_allow_html=True,
                )

                # 마크다운 생성
                md = generate_markdown(context, result, mode)
                html = generate_html(context, result, mode)

                # 파일 저장
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                company = context["company_name"].replace(" ", "_")
                base_name = f"{company}_{mode.replace(' ', '_')}_{timestamp}"

                md_filename = f"{base_name}.md"
                html_filename = f"{base_name}.html"
                docx_filename = f"{base_name}.docx"

                md_path = save_markdown(md, md_filename)
                html_path = save_html(html, html_filename)
                docx_path = save_docx(md, docx_filename)

                st.session_state.report_md = md
                st.session_state.report_html = html
                st.session_state.md_path = md_path
                st.session_state.html_path = html_path
                st.session_state.docx_path = docx_path
                st.session_state.md_filename = md_filename
                st.session_state.html_filename = html_filename
                st.session_state.docx_filename = docx_filename
                st.session_state.report_generated = True

                st.rerun()

            except Exception as e:
                st.error(f"보고서 생성 중 오류가 발생했습니다: {e}")
                st.info("API 키와 환경변수 설정을 확인해주세요. (.env 파일 참고)")

        else:
            # 보고서 결과 표시
            st.markdown(
                '<div style="background:#F0FFF0;border:1px solid #28A745;border-radius:2px;'
                'padding:14px 20px;margin-bottom:20px;font-weight:600;color:#28A745;font-size:0.95rem;">'
                '✓ 보고서가 성공적으로 생성되었습니다</div>',
                unsafe_allow_html=True,
            )

            # 다운로드 버튼
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
            with col1:
                st.download_button(
                    "Markdown 다운로드",
                    data=st.session_state.get("report_md", ""),
                    file_name=st.session_state.get("md_filename", "report.md"),
                    mime="text/markdown",
                    use_container_width=True,
                )
            with col2:
                if st.session_state.get("docx_path"):
                    with open(st.session_state.docx_path, "rb") as f:
                        st.download_button(
                            "Word 다운로드",
                            data=f.read(),
                            file_name=st.session_state.get("docx_filename", "report.docx"),
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                        )
                else:
                    st.caption("Word 생성 불가")
            with col3:
                st.download_button(
                    "HTML 다운로드",
                    data=st.session_state.report_html,
                    file_name=st.session_state.get("html_filename", "report.html"),
                    mime="text/html",
                    use_container_width=True,
                )
            with col4:
                if st.button("새 보고서 작성", use_container_width=True):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()

            # 저장 경로 안내
            st.caption(f"저장 위치: `{st.session_state.get('html_path', '')}`")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            # ── 법무 심층 분석 & 회계적 영향 연계 ──
            st.markdown('<div class="pwc-section-title">법무 · 회계 연계 분석</div>', unsafe_allow_html=True)
            st.markdown(
                '<div style="font-size:0.88rem;color:#666;margin-bottom:12px;">'
                '투자보고서 결과를 기반으로 법무 심층 분석(Deal Killer / CoC Map / Indemnity)과 '
                '회계적 영향 분석을 바로 실행할 수 있습니다.</div>',
                unsafe_allow_html=True,
            )

            inv_ctx = {
                "company_name": st.session_state.get("company_name", ""),
                "industry": st.session_state.get("industry", ""),
                "investment_purpose": st.session_state.get("investment_purpose", ""),
                "risk_preference": st.session_state.get("risk_preference", ""),
                "memo": st.session_state.get("memo", ""),
                "uploaded_text": st.session_state.get("uploaded_text", ""),
            }

            # 세션 초기화
            if "inv_legal_deep" not in st.session_state:
                st.session_state.inv_legal_deep = None
            if "inv_accounting_impact" not in st.session_state:
                st.session_state.inv_accounting_impact = None

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("⚖️ 법무 심층 분석 (Legal Deep Dive)", use_container_width=True, type="primary", key="inv_legal_btn"):
                    with st.spinner("Deal Killer 분석 중..."):
                        dk = run_deal_killer(inv_ctx)
                    with st.spinner("CoC Map 분석 중..."):
                        coc = run_coc_map(inv_ctx)
                    with st.spinner("Indemnity Summary 분석 중..."):
                        ind = run_indemnity(inv_ctx)
                    st.session_state.inv_legal_deep = {
                        "deal_killer": dk, "coc_map": coc, "indemnity": ind,
                    }
                    st.rerun()
            with btn_col2:
                if st.button("📊 회계적 영향 분석 (Accounting Impact)", use_container_width=True, type="primary", key="inv_impact_btn"):
                    # 법무 결과 준비
                    if st.session_state.inv_legal_deep:
                        ld = st.session_state.inv_legal_deep
                        legal_text = "\n\n".join([ld["deal_killer"], ld["coc_map"], ld["indemnity"]])
                    else:
                        # 기본 법무 결과 사용 (orchestrator 결과)
                        legal_text = st.session_state.get("inv_basic_legal", "")
                        if not legal_text:
                            # orchestrator가 생성한 legal agent 결과 가져오기
                            with st.spinner("기본 법무 분석 실행 중..."):
                                legal_text = legal_basic_run(inv_ctx)
                            st.session_state.inv_basic_legal = legal_text
                    # 재무 결과
                    finance_text = st.session_state.get("inv_finance_result", "")
                    if not finance_text:
                        with st.spinner("재무 분석 실행 중..."):
                            try:
                                finance_text = finance_cost_run(inv_ctx)
                                st.session_state.inv_finance_result = finance_text
                            except Exception:
                                finance_text = ""
                    with st.spinner("회계적 영향 분석 중..."):
                        impact = accounting_impact_run(legal_text, finance_text, inv_ctx)
                    st.session_state.inv_accounting_impact = impact
                    st.rerun()

            # 법무 심층 분석 결과 표시
            if st.session_state.inv_legal_deep:
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                ld = st.session_state.inv_legal_deep
                lt1, lt2, lt3 = st.tabs(["Deal Killer", "CoC / Assignment Map", "Indemnity Summary"])
                with lt1:
                    st.markdown(ld["deal_killer"])
                with lt2:
                    st.markdown(ld["coc_map"])
                with lt3:
                    st.markdown(ld["indemnity"])

            # 회계적 영향 분석 결과 표시
            if st.session_state.inv_accounting_impact:
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                st.markdown('<div class="pwc-section-title">회계적 영향 분석 결과</div>', unsafe_allow_html=True)
                st.markdown(st.session_state.inv_accounting_impact)

            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

            # 보고서 미리보기
            st.markdown('<div class="pwc-section-title">보고서 미리보기</div>', unsafe_allow_html=True)
            preview_tab1, preview_tab2 = st.tabs(["Markdown", "HTML"])
            with preview_tab1:
                st.markdown(st.session_state.get("report_md", ""))
            with preview_tab2:
                st.components.v1.html(st.session_state.report_html, height=800, scrolling=True)

        # 이전 단계로
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        col1, _, _ = st.columns([1, 2, 1])
        with col1:
            if st.button("← 입력 수정", use_container_width=True):
                st.session_state.step = 3
                st.session_state.report_generated = False
                st.session_state.report_html = None
                st.rerun()
