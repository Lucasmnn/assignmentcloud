import streamlit as st

def inject_css() -> None:
    """Inject all custom CSS into the Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #e0e0e0;
}

footer {visibility: hidden;}
header {visibility: hidden;}

/* Hide the sidebar collapse/close button */
button[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
button[kind="headerNoPadding"],
.st-emotion-cache-1vt4y6f,
[data-testid="stSidebar"] button[title="Collapse sidebar"] {
    display: none !important;
    visibility: hidden !important;
}

/* ── Landing Page ── */
.landing-container {
    height: 100vh;
    width: 100vw;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: radial-gradient(circle at center, #1a1c2c 0%, #0d0e17 100%);
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: 9999;
    overflow: hidden;
}

.landing-content {
    text-align: center;
    max-width: 550px;
    padding: 40px;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(25px);
    border-radius: 30px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 40px 100px rgba(0,0,0,0.5);
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.landing-logo {
    font-family: 'Outfit', sans-serif;
    font-size: 80px;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1;
}

.landing-description {
    font-size: 15px;
    color: #6b6b8a;
    line-height: 1.5;
    margin-bottom: 5px;
}

/* Button Box Below the Card */
.landing-btn-box {
    margin-top: 30px;
    z-index: 10001;
}

div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    padding: 15px 45px !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    border-radius: 50px !important;
    border: none !important;
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4) !important;
    display: block !important;
    margin: 0 auto !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stButton"] button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.6) !important;
}

/* ── Metrics ── */
div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    padding: 15px 20px !important;
    border-radius: 16px !important;
}

/* ── Movie Card ── */
.movie-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    position: relative;
    cursor: pointer;
    min-height: 180px;
}

.movie-title {
    font-size: 1.15em;
    font-weight: 700;
    color: white;
    margin-bottom: 10px;
}

.movie-year { font-size: 0.85em; color: #8b8ba7; margin-bottom: 12px; }

.movie-meta { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }

.movie-rating {
    background: rgba(255, 193, 7, 0.1);
    color: #ffc107;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.88em;
    font-weight: 600;
}

.movie-lang {
    background: rgba(102, 126, 234, 0.1);
    color: #a5b4fc;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.82em;
    font-weight: 500;
}

.genre-badge {
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75em;
    font-weight: 600;
    background: rgba(255, 255, 255, 0.05);
    color: #8b8ba7;
    margin-right: 5px;
    margin-top: 5px;
}

/* Full coverage button for cards */
[data-testid="stColumn"]:has(.movie-card) .stButton {
    position: absolute !important;
    top: 0 !important; left: 0 !important;
    width: 100% !important; height: 100% !important;
    z-index: 10 !important;
}

[data-testid="stColumn"]:has(.movie-card) button {
    opacity: 0 !important;
    width: 100% !important; height: 100% !important;
    border: none !important;
    background: transparent !important;
}

/* ── UI Components ── */
.main-search-container {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 24px;
}

.search-title {
    font-family: 'Outfit', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: white;
}

.filter-pill {
    background: rgba(102, 126, 234, 0.12);
    color: #a5b4fc;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.82em;
    font-weight: 600;
}
</style>
"""
