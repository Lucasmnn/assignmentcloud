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

/* Hide the sidebar collapse/close button so it stays permanently open */
button[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
button[kind="headerNoPadding"],
.st-emotion-cache-1vt4y6f {
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
    overflow: hidden; /* No scroll on landing */
}

.landing-content {
    text-align: center;
    max-width: 600px;
    padding: 30px;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    border-radius: 25px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.landing-logo {
    font-family: 'Outfit', sans-serif;
    font-size: 80px;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0px;
}

.landing-subtitle {
    font-family: 'Outfit', sans-serif;
    font-size: 24px;
    font-weight: 500;
    color: #8b8ba7;
    margin-bottom: 10px;
}

.landing-description {
    font-size: 15px;
    color: #6b6b8a;
    margin-bottom: 30px;
}

/* ── Sidebar styling ── */
[data-testid="stSidebar"] {
    background: #0f111a !important;
}

.sidebar-title {
    font-family: 'Outfit', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: #667eea;
    margin-bottom: 20px;
}

/* ── Metric cards (Ancien style) ── */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
    padding: 18px 22px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.05);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* ── Movie Card (Ancien style) ── */
.movie-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    transition: transform 0.2s ease;
    cursor: pointer;
    min-height: 180px;
    position: relative;
}

.movie-card:hover {
    transform: translateY(-4px);
    background: rgba(255, 255, 255, 0.04);
}

.movie-title {
    font-size: 1.1em;
    font-weight: 700;
    color: white;
    margin-bottom: 8px;
}

.movie-year {
    font-size: 0.85em;
    color: #8b8ba7;
    margin-bottom: 12px;
}

.movie-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}

.movie-rating {
    background: rgba(255, 193, 7, 0.1);
    color: #ffc107;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 600;
}

.movie-lang {
    background: rgba(102, 126, 234, 0.1);
    color: #a5b4fc;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.8em;
    font-weight: 500;
}

.genre-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.genre-badge {
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75em;
    font-weight: 600;
    background: rgba(255,255,255,0.05);
    color: #8b8ba7;
}

/* ── Clickable Movie Cards Overlay ── */
[data-testid="stColumn"]:has(.movie-card) .stButton {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    z-index: 10 !important;
    margin: 0 !important;
}
[data-testid="stColumn"]:has(.movie-card) button {
    height: 100% !important;
    width: 100% !important;
    opacity: 0 !important;
    background: transparent !important;
    border: none !important;
}

/* ── Main content restructuring ── */
.main-search-container {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 24px;
}

.search-title {
    font-family: 'Outfit', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: white;
}

.active-filters-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 16px;
}

.filter-pill {
    background: rgba(102, 126, 234, 0.1);
    color: #a5b4fc;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8em;
    font-weight: 600;
}

</style>
"""
