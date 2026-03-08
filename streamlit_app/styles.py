import streamlit as st

def inject_css() -> None:
    """Inject all custom CSS into the Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;600;800&display=swap');

/* Force dark theme defaults */
:root {
    --primary-color: #667eea;
    --background-color: #0d0e17;
    --secondary-background-color: #0f111a;
    --text-color: #e0e0e0;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0d0e17 !important;
    font-family: 'Inter', sans-serif;
    color: #e0e0e0;
}

footer {visibility: hidden;}
header {visibility: hidden;}

/* Hide Sidebar Toggle / Collapse Button completely */
button[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
.st-emotion-cache-1vt4y6f, 
button[title="Collapse sidebar"] {
    display: none !important;
}

/* ── Landing Page ── */
.landing-container {
    min-height: 90vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 40px 20px;
    background: radial-gradient(circle at center, #1a1c2c 0%, #0d0e17 100%);
}

.landing-content {
    text-align: center;
    max-width: 750px;
    width: 100%;
    padding: 60px 40px;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(25px);
    border-radius: 35px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: 0 40px 80px -20px rgba(0, 0, 0, 0.7);
}

.landing-logo {
    font-family: 'Outfit', sans-serif;
    font-size: 85px;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
    letter-spacing: -2px;
}

.landing-subtitle {
    font-family: 'Outfit', sans-serif;
    font-size: 26px;
    font-weight: 500;
    color: #8b8ba7;
    margin-bottom: 20px;
}

.landing-description {
    font-size: 17px;
    color: #7171a3;
    margin-bottom: 50px;
    line-height: 1.7;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
}

/* Targeting the Streamlit button widget directly */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    padding: 18px 45px !important;
    font-size: 20px !important;
    font-weight: 700 !important;
    border-radius: 50px !important;
    border: none !important;
    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.35) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

div[data-testid="stButton"] button:hover {
    transform: translateY(-3px) scale(1.03) !important;
    box-shadow: 0 20px 45px rgba(102, 126, 234, 0.5) !important;
}

/* ── Main Catalog UI ── */
[data-testid="stSidebar"] {
    background-color: #0f111a !important;
}

.sidebar-title {
    font-family: 'Outfit', sans-serif;
    font-size: 22px;
    font-weight: 700;
    color: #667eea;
}

.main-search-container {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 28px;
    margin-bottom: 30px;
}

.search-title {
    font-family: 'Outfit', sans-serif;
    font-size: 26px;
    font-weight: 700;
    color: white;
}

/* Metrics */
div[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    padding: 20px !important;
    border-radius: 20px !important;
}

/* Cards */
.movie-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 25px;
    position: relative;
    transition: background 0.3s ease;
}

.movie-card:hover {
    background: rgba(255, 255, 255, 0.04);
}

.movie-title {
    font-family: 'Outfit', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: white;
    margin-bottom: 8px;
}

.movie-year { color: #8b8ba7; font-size: 14px; margin-bottom: 15px; }

.tag {
    font-size: 11px;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 8px;
    text-transform: uppercase;
}

.tag-rating { background: rgba(255, 193, 7, 0.1); color: #ffc107; }
.tag-lang { background: rgba(102, 126, 234, 0.1); color: #a5b4fc; }

.genre-tag {
    font-size: 10px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 6px;
    background: rgba(255,255,255,0.05);
    color: #8b8ba7;
    margin-right: 5px;
}

.filter-pill {
    background: rgba(102, 126, 234, 0.12);
    color: #a5b4fc;
    padding: 6px 14px;
    border-radius: 14px;
    font-size: 13px;
    font-weight: 600;
    margin-right: 8px;
}

/* Card Button Overlay */
[data-testid="stColumn"]:has(.movie-card) .stButton {
    position: absolute !important;
    top: 0 !important; left: 0 !important;
    width: 100% !important; height: 100% !important;
    z-index: 5 !important;
}

[data-testid="stColumn"]:has(.movie-card) button {
    background: transparent !important;
    border: none !important;
    color: transparent !important;
    width: 100% !important;
    height: 100% !important;
}

</style>
"""
