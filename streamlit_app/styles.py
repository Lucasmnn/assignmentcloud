import streamlit as st

def inject_css() -> None:
    """Inject all custom CSS into the Streamlit page."""
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """
<style>
/* ── Import Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Hide Streamlit branding & sidebar close button ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Hide the sidebar collapse/close button so it stays permanently open */
button[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
button[kind="headerNoPadding"] {
    display: none !important;
    visibility: hidden !important;
}

/* ── Sidebar styling ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 100%);
}
[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}
[data-testid="stSidebar"] .stMarkdown h2 {
    color: #ffffff !important;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 20px !important;
}

/* Add space between sidebar widgets */
[data-testid="stSidebar"] [data-testid="stElementContainer"] {
    margin-bottom: 12px !important;
}

/* Clear-all filters button */
.clear-filters-btn button {
    background: rgba(239, 83, 80, 0.12) !important;
    color: #ef5350 !important;
    border: 1px solid rgba(239, 83, 80, 0.3) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.clear-filters-btn button:hover {
    background: rgba(239, 83, 80, 0.25) !important;
    border-color: #ef5350 !important;
}

/* ── Metric cards ── */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 18px 22px;
    border-radius: 16px;
    color: white !important;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.35);
}
div[data-testid="stMetric"] label {
    color: rgba(255,255,255,0.85) !important;
    font-weight: 500;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 700;
}

/* ── Movie Card ── */
.movie-card {
    background: linear-gradient(145deg, #1e1e2f, #2a2a40);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    position: relative;
    overflow: hidden;
    min-height: 200px;
    cursor: pointer;
}
.movie-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.movie-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    border-color: rgba(102, 126, 234, 0.3);
}
.movie-card:hover::before {
    opacity: 1;
}

.movie-title {
    font-size: 1.15em;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 10px;
    line-height: 1.3;
    letter-spacing: -0.01em;
}

.movie-year {
    font-size: 0.82em;
    color: #8b8ba7;
    font-weight: 500;
    margin-bottom: 12px;
}

.movie-meta {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 14px;
    flex-wrap: wrap;
}

.movie-rating {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 193, 7, 0.12);
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.88em;
    font-weight: 600;
    color: #ffc107;
}

.movie-lang {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(102, 126, 234, 0.12);
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.82em;
    font-weight: 500;
    color: #667eea;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.genre-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 6px;
}

.genre-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75em;
    font-weight: 600;
    letter-spacing: 0.02em;
}

/* Genre color palette */
.genre-drama { background: rgba(239, 83, 80, 0.15); color: #ef5350; }
.genre-comedy { background: rgba(255, 202, 40, 0.15); color: #ffca28; }
.genre-action { background: rgba(255, 112, 67, 0.15); color: #ff7043; }
.genre-romance { background: rgba(236, 64, 122, 0.15); color: #ec407a; }
.genre-thriller { background: rgba(171, 71, 188, 0.15); color: #ab47bc; }
.genre-horror { background: rgba(183, 28, 28, 0.15); color: #c62828; }
.genre-sci-fi { background: rgba(0, 188, 212, 0.15); color: #00bcd4; }
.genre-adventure { background: rgba(76, 175, 80, 0.15); color: #4caf50; }
.genre-animation { background: rgba(255, 167, 38, 0.15); color: #ffa726; }
.genre-musical { background: rgba(156, 39, 176, 0.15); color: #ce93d8; }
.genre-war { background: rgba(121, 85, 72, 0.15); color: #a1887f; }
.genre-crime { background: rgba(158, 158, 158, 0.15); color: #bdbdbd; }
.genre-mystery { background: rgba(63, 81, 181, 0.15); color: #7986cb; }
.genre-documentary { background: rgba(0, 150, 136, 0.15); color: #4db6ac; }
.genre-western { background: rgba(188, 143, 89, 0.15); color: #bc8f59; }
.genre-fantasy { background: rgba(126, 87, 194, 0.15); color: #7e57c2; }
.genre-children { background: rgba(129, 199, 132, 0.15); color: #81c784; }
.genre-film-noir { background: rgba(96, 96, 96, 0.18); color: #aaaaaa; }
.genre-default { background: rgba(255, 255, 255, 0.08); color: #b0b0b0; }

/* ── Star display ── */
.stars {
    color: #ffc107;
    font-size: 0.95em;
    letter-spacing: 1px;
}

/* ── Section title ── */
.section-title {
    font-size: 2.4em;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 6px;
    letter-spacing: -0.03em;
}

/* ── No results ── */
.no-results {
    text-align: center;
    padding: 60px 20px;
    color: #8b8ba7;
}
.no-results-icon {
    font-size: 4em;
    margin-bottom: 16px;
}
.no-results-text {
    font-size: 1.2em;
    font-weight: 500;
}

/* ── Pagination ── */
.pagination-info {
    text-align: center;
    color: #8b8ba7;
    font-size: 0.9em;
    padding: 10px 0;
    margin-top: 10px;
}

/* ── Divider ── */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(102,126,234,0.3), transparent);
    margin: 24px 0;
    border: none;
}

/* ── Detail view ── */
.detail-header {
    font-size: 2em;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 8px;
    letter-spacing: -0.02em;
}
.detail-tagline {
    font-size: 1.1em;
    color: #8b8ba7;
    font-style: italic;
    margin-bottom: 20px;
}
.detail-overview {
    font-size: 1em;
    color: #c0c0d0;
    line-height: 1.7;
    margin-bottom: 20px;
}
.detail-info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 20px;
}
.detail-info-item {
    background: #1e1e2f;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 14px 18px;
}
.detail-info-label {
    font-size: 0.78em;
    color: #8b8ba7;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
    margin-bottom: 4px;
}
.detail-info-value {
    font-size: 1.05em;
    color: #ffffff !important;
    font-weight: 600;
}

/* ── Clickable Movie Cards Overlay ── */
[data-testid="stColumn"]:has(.movie-card) {
    position: relative !important;
}
[data-testid="stColumn"]:has(.movie-card) [data-testid="stElementContainer"]:has(.stButton),
[data-testid="stColumn"]:has(.movie-card) .stButton {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    z-index: 10 !important;
    margin: 0 !important;
    padding: 0 !important;
}
[data-testid="stColumn"]:has(.movie-card) button {
    height: 100% !important;
    width: 100% !important;
    opacity: 0 !important;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    margin: 0 !important;
    padding: 0 !important;
    cursor: pointer !important;
}
.movie-card {
    position: relative;
    z-index: 1;
    width: 100%;
}

/* ── Active filter pill ── */
.active-filters-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 16px;
}
.filter-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(102, 126, 234, 0.15);
    color: #667eea;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.82em;
    font-weight: 600;
}

/* ── Footer ── */
.app-footer {
    text-align: center;
    color: #6b6b8a;
    font-size: 0.8em;
    padding: 20px 0 10px;
    border-top: 1px solid rgba(255,255,255,0.04);
    margin-top: 40px;
}
</style>
"""
