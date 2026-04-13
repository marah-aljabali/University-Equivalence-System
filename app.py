import streamlit as st
from enter_data import enter_data
from uploade_best_match import uploade_best_match

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Academic Plan Equivalency Tool",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS (Theme from EduPredict)
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');

/* ── Design tokens ── */
:root {
    --navy:   #0f1f3d;
    --teal:   #0d9488;
    --amber:  #f59e0b;
    --cream:  #f8f7f4;
    --slate:  #64748b;
    --shadow: 0 4px 24px rgba(15,31,61,.10);
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background: var(--cream);
    color: var(--navy);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--navy) !important;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* ── Remove top padding ── */
.block-container { padding-top: 2rem !important; }

/* ── Hero Section ── */
.hero {
    background: linear-gradient(135deg, #0f1f3d 0%, #1a3560 55%, #0f766e 100%);
    border-radius: 20px;
    padding: 52px 48px 44px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: '';
    position: absolute;
    width: 420px; height: 420px;
    background: radial-gradient(circle, rgba(13,148,136,.3) 0%, transparent 70%);
    top: -120px; right: -80px;
    border-radius: 50%;
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    border: 1px solid var(--amber);
    background: rgba(245,158,11,.15);
    color: var(--amber);
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .12em;
    text-transform: uppercase;
    padding: 4px 14px;
    border-radius: 100px;
    margin-bottom: 18px;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 3.4rem;
    color: #fff;
    line-height: 1.12;
    margin: 0 0 14px;
}
.hero-title em { color: #5eead4; font-style: italic; }
.hero-sub {
    font-size: 1.05rem;
    color: #94d5cf;
    font-weight: 300;
    line-height: 1.75;
    max-width: 600px;
}

/* ── Stat bar ── */
.stat-bar {
    display: flex;
    background: var(--navy);
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 32px;
}
.stat-item {
    flex: 1;
    padding: 26px 20px;
    text-align: center;
    border-right: 1px solid rgba(255,255,255,.07);
}
.stat-item:last-child { border-right: none; }
.stat-num {
    font-family: 'DM Serif Display', serif;
    font-size: 2.2rem;
    color: var(--teal);
    line-height: 1;
}
.stat-lbl {
    font-size: .78rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: .08em;
    margin-top: 4px;
}

/* ── Feature cards ── */
.card-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr); /* Changed to 2 for this tool */
    gap: 18px;
    margin-bottom: 32px;
}
.card {
    background: #fff;
    border-radius: 16px;
    padding: 30px;
    box-shadow: var(--shadow);
    border-top: 3px solid transparent;
    transition: transform .2s, box-shadow .2s;
    cursor: pointer;
}
.card:hover { transform: translateY(-4px); box-shadow: 0 14px 36px rgba(15,31,61,.15); }
.card.t { border-top-color: var(--teal); }
.card.a { border-top-color: var(--amber); }
.card-icon { font-size: 2.5rem; margin-bottom: 12px; display: block;}
.card-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.4rem;
    color: var(--navy);
    margin-bottom: 8px;
}
.card-body { font-size: .9rem; color: var(--slate); line-height: 1.65; }

/* ── Buttons ── */
.stButton > button {
    background: var(--teal) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: opacity .2s !important;
}
.stButton > button:hover { opacity: .85 !important; }

/* ── SelectBox Styling ── */
div[data-baseweb="select"] > div {
    background-color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MAIN INTERFACE
# ─────────────────────────────────────────────────────────────────────────────

# If user selects an option from sidebar or hidden selector, we redirect logic
# We use a session state to manage navigation for a cleaner "App" feel
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def nav_to(page):
    st.session_state.page = page
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ROUTING LOGIC
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.page == 'home':
    
    # HERO
    st.markdown("""
    <div class="hero">
      <div class="hero-badge">🎓 AI-Powered Academic Tool</div>
      <div class="hero-title">Plan Equivalency<br><em>Made Simple</em></div>
      <div class="hero-sub">
        Upload your old and new study plans (CSV) to receive a comprehensive,
        AI-driven equivalency report. Automatically matches courses based on
        semantic similarity and enforces credit limits.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # STATS
    st.markdown("""
    <div class="stat-bar">
      <div class="stat-item">
        <div class="stat-num">AI</div>
        <div class="stat-lbl">Semantic Matching</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">30</div>
        <div class="stat-lbl">Max Credit Hours</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">Auto</div>
        <div class="stat-lbl">Column Mapping</div>
      </div>
      <div class="stat-item">
        <div class="stat-num">CSV</div>
        <div class="stat-lbl">Instant Export</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # CARDS (Navigation via Click)
    st.markdown('<div class="card-grid">', unsafe_allow_html=True)
    
    # Card 1
    st.markdown("""
    <div class="card t" onclick="document.querySelector('button[kind=primary]').click()">
        <span class="card-icon">📂</span>
        <div class="card-title">Upload Files</div>
        <div class="card-body">
          Upload your CSV files for the old and new plans. The system will
          automatically map columns and find the best matches.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Upload", key="btn_upload_home", type="primary"):
        nav_to('upload')

    # Card 2
    st.markdown("""
    <div class="card a" onclick="document.querySelector('button[data-testid=baseButton-secondary]').click()">
        <span class="card-icon">✏️</span>
        <div class="card-title">Enter Data Manually</div>
        <div class="card-body">
          Don't have a CSV? Enter course details manually to test the
          AI matching engine instantly.
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Manual Entry", key="btn_enter_home"):
        nav_to('enter')

    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == 'upload':
    # Inject Page Header Style
    st.markdown("""
    <style>
    .page-hdr {
        background: linear-gradient(120deg, #0f1f3d 0%, #1a3560 60%, #0f5f5a 100%);
        border-radius: 16px;
        padding: 34px 40px;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .page-hdr-icon { font-size: 2.6rem; }
    .page-hdr-title {
        font-family: 'DM Serif Display', serif;
        font-size: 2rem;
        color: #fff;
        line-height: 1.2;
        margin: 0;
    }
    </style>
    <div class="page-hdr">
      <div class="page-hdr-icon">📂</div>
      <div>
        <div class="page-hdr-title">Upload Files</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    uploade_best_match()

elif st.session_state.page == 'enter':
    st.markdown("""
    <style>
    .page-hdr {
        background: linear-gradient(120deg, #0f1f3d 0%, #1e3a5f 100%);
        border-radius: 16px;
        padding: 34px 40px;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .page-hdr-icon { font-size: 2.6rem; }
    .page-hdr-title {
        font-family: 'DM Serif Display', serif;
        font-size: 2rem;
        color: #fff;
        line-height: 1.2;
        margin: 0;
    }
    </style>
    <div class="page-hdr">
      <div class="page-hdr-icon">✏️</div>
      <div>
        <div class="page-hdr-title">Manual Data Entry</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    enter_data()