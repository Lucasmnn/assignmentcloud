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

button[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: none !important;
}

/* ── Landing Page ── */
.landing-container {
    min-height: 80vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 60px 20px;
}

.landing-content {
    text-align: center;
    max-width: 700px;
    width: 100%;
    padding: 50px;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    border-radius: 30px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.landing-logo {
    font-family: 'Outfit', sans-serif;
    font-size: 80px;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}

.landing-description {
    font-size: 16px;
    color: #8b8ba7;
    margin-bottom: 40px;
    line-height: 1.6;
}

/* Target the Streamlit button inside landing-btn wrapper */
.landing-btn-wrapper div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    padding: 20px 60px !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    border-radius: 50px !important;
    border: none !important;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4) !important;
    width: auto !important;
    display: block !important;
    margin: 0 auto !important;
    height: auto !important;
    min-height: 60px !important;
}

.landing-btn-wrapper div[data-testid="stButton"] button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 15px 40px rgba(102, 126, 234, 0.5) !important;
    border-color: transparent !important;
}

/* ── Main Catalog ── */
[data-testid="stSidebar"] {
    background-color: #0f111a !important;
}

.sidebar-title {
    font-family: 'Outfit', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: #667eea;
}

.main-search-container {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
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

div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 15px 20px;
    border-radius: 16px;
}

.movie-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 20px;
    position: relative;
}

.movie-title {
    font-family: 'Outfit', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: white;
}

.tag {
    font-size: 11px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
    text-transform: uppercase;
}

.tag-rating { background: rgba(255, 193, 7, 0.1); color: #ffc107; }
.tag-lang { background: rgba(102, 126, 234, 0.1); color: #a5b4fc; }

.genre-tag {
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    background: rgba(255,255,255,0.05);
    color: #b0b0cf;
}

.filter-pill {
    background: rgba(102, 126, 234, 0.15);
    color: #a5b4fc;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: 600;
}

[data-testid="stColumn"]:has(.movie-card) .stButton {
    position: absolute !important;
    top: 0 !important; left: 0 !important;
    width: 100% !important; height: 100% !important;
    z-index: 10 !important;
}

[data-testid="stColumn"]:has(.movie-card) button {
    background: transparent !important;
    border: none !important;
    color: transparent !important;
}

/* Hide Sidebar when on landing page */
body[data-landing="true"] [data-testid="stSidebar"] {
    display: none !important;
}
</style>
"""
