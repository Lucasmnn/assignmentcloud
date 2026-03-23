import streamlit as st


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


_CSS = """
<style>
/* ══════════════════════════════════════════════════════════════════
   NETFLIX-STYLE GLOBAL RESET
   ══════════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Netflix+Sans:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --nf-red:       #E50914;
    --nf-red-dark:  #B20710;
    --nf-black:     #000000;
    --nf-dark:      #141414;
    --nf-dark2:     #181818;
    --nf-dark3:     #232323;
    --nf-gray:      #808080;
    --nf-light:     #e5e5e5;
    --nf-white:     #ffffff;
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    background-color: var(--nf-dark) !important;
    color: var(--nf-white) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header,
button[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
.stDeployButton { display: none !important; }

/* ── Remove default Streamlit padding ── */
.block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
}
section[data-testid="stSidebar"] { display: none !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--nf-dark2); }
::-webkit-scrollbar-thumb { background: var(--nf-red); border-radius: 3px; }
* { scrollbar-width: thin; scrollbar-color: var(--nf-red) var(--nf-dark2); }


/* ══════════════════════════════════════════════════════════════════
   NAVBAR
   ══════════════════════════════════════════════════════════════════ */
.nf-navbar {
    position: sticky;
    top: 0;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 48px;
    background: linear-gradient(180deg, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.8) 70%, transparent 100%);
    backdrop-filter: blur(4px);
}
.nf-logo {
    font-size: 2rem;
    font-weight: 900;
    color: var(--nf-red) !important;
    letter-spacing: -0.04em;
    text-transform: uppercase;
    text-shadow: 0 2px 8px rgba(229,9,20,0.4);
}
.nf-nav-tagline {
    font-size: 0.82rem;
    color: var(--nf-gray);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}


/* ══════════════════════════════════════════════════════════════════
   HERO SECTION
   ══════════════════════════════════════════════════════════════════ */
.nf-hero {
    position: relative;
    width: 100%;
    min-height: 60vh;
    background-size: cover;
    background-position: center 20%;
    display: flex;
    align-items: flex-end;
    padding-bottom: 80px;
    margin-top: -80px; /* pull up behind navbar */
}
.nf-hero-gradient {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        to right,
        rgba(0,0,0,0.85) 0%,
        rgba(0,0,0,0.6) 40%,
        rgba(0,0,0,0.15) 70%,
        transparent 100%
    ),
    linear-gradient(
        to top,
        rgba(20,20,20,1) 0%,
        rgba(20,20,20,0.6) 20%,
        transparent 60%
    );
}
.nf-hero-content {
    position: relative;
    z-index: 2;
    padding: 0 48px;
    max-width: 600px;
}
.nf-hero-title {
    font-size: clamp(1.8rem, 4vw, 3rem);
    font-weight: 700;
    color: var(--nf-white);
    margin-bottom: 12px;
    line-height: 1.1;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
}
.nf-hero-meta {
    font-size: 0.9rem;
    color: var(--nf-light);
    margin-bottom: 16px;
    opacity: 0.85;
}
.nf-hero-overview {
    font-size: 0.95rem;
    color: var(--nf-light);
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-shadow: 1px 1px 4px rgba(0,0,0,0.9);
    margin-bottom: 0;
}
.nf-hero-placeholder {
    min-height: 40vh;
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 5rem;
    margin-top: -80px;
    padding: 80px 0 40px;
}


/* ══════════════════════════════════════════════════════════════════
   MOVIE ROWS (horizontal scroll)
   ══════════════════════════════════════════════════════════════════ */
.nf-section {
    padding: 0 48px;
    margin-bottom: 40px;
}
.nf-section-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--nf-light);
    margin-bottom: 14px;
    letter-spacing: 0.01em;
}
.nf-section-title span {
    color: var(--nf-red);
}
.nf-row-scroll {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding-bottom: 12px;
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
}
.nf-card {
    flex: 0 0 160px;
    height: 240px;
    border-radius: 4px;
    overflow: hidden;
    position: relative;
    background: var(--nf-dark3);
    scroll-snap-align: start;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    cursor: default;
}
.nf-card:hover {
    transform: scale(1.08);
    z-index: 10;
    box-shadow: 0 12px 40px rgba(0,0,0,0.7);
}
.nf-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}
.nf-no-poster {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: linear-gradient(145deg, var(--nf-dark2), var(--nf-dark3));
    font-size: 2.5rem;
    color: var(--nf-gray);
    gap: 8px;
    padding: 12px;
    text-align: center;
}
.nf-no-poster-title {
    font-size: 0.7rem;
    color: var(--nf-gray);
    line-height: 1.3;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
}
.nf-card-overlay {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    background: linear-gradient(transparent, rgba(0,0,0,0.92));
    padding: 36px 10px 10px;
    opacity: 0;
    transition: opacity 0.25s ease;
}
.nf-card:hover .nf-card-overlay {
    opacity: 1;
}
.nf-card-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--nf-white);
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin-bottom: 4px;
}
.nf-card-meta {
    font-size: 0.65rem;
    color: var(--nf-gray);
}
.nf-card-rating {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-size: 0.65rem;
    color: #ffc107;
    font-weight: 600;
}
.nf-match-badge {
    display: inline-block;
    background: var(--nf-red);
    color: var(--nf-white);
    font-size: 0.6rem;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 3px;
    margin-bottom: 4px;
}


/* ══════════════════════════════════════════════════════════════════
   RECOMMENDATION SECTION (movie selector)
   ══════════════════════════════════════════════════════════════════ */
.nf-selector-section {
    background: linear-gradient(180deg, var(--nf-dark) 0%, #0d0d1a 100%);
    padding: 40px 48px;
    margin-bottom: 20px;
    border-top: 1px solid rgba(255,255,255,0.06);
}
.nf-selector-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--nf-white);
    margin-bottom: 8px;
}
.nf-selector-subtitle {
    font-size: 0.9rem;
    color: var(--nf-gray);
    margin-bottom: 24px;
}

/* Style Streamlit text_input to look Netflix-dark */
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 4px !important;
    color: var(--nf-white) !important;
    font-size: 1rem !important;
    padding: 14px 16px !important;
    transition: border-color 0.2s ease !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--nf-white) !important;
    background: rgba(255,255,255,0.12) !important;
    box-shadow: none !important;
}
[data-testid="stTextInput"] input::placeholder { color: var(--nf-gray) !important; }
[data-testid="stTextInput"] label { display: none !important; }

/* Autocomplete suggestion buttons */
.ac-movie-btn button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: var(--nf-light) !important;
    border-radius: 4px !important;
    text-align: left !important;
    font-size: 0.85rem !important;
    padding: 10px 14px !important;
    transition: all 0.2s ease !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
.ac-movie-btn button:hover {
    background: rgba(229,9,20,0.15) !important;
    border-color: rgba(229,9,20,0.4) !important;
    color: var(--nf-white) !important;
}

/* Selected movie chips */
.selected-movies-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 16px 0;
    min-height: 40px;
}
.nf-chip {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(229,9,20,0.15);
    border: 1px solid rgba(229,9,20,0.4);
    color: var(--nf-white);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 500;
}
.nf-chip-label { color: var(--nf-light); }

/* Remove buttons for chips */
.chip-remove button {
    background: transparent !important;
    border: none !important;
    color: var(--nf-gray) !important;
    padding: 0 4px !important;
    font-size: 0.85rem !important;
    min-height: unset !important;
    height: auto !important;
    width: auto !important;
    transition: color 0.2s !important;
}
.chip-remove button:hover { color: var(--nf-red) !important; }

/* Primary CTA — Get Recommendations */
.nf-cta button {
    background: var(--nf-red) !important;
    color: var(--nf-white) !important;
    border: none !important;
    border-radius: 4px !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    padding: 14px 32px !important;
    transition: background 0.2s ease, transform 0.15s ease !important;
    letter-spacing: 0.02em !important;
}
.nf-cta button:hover {
    background: var(--nf-red-dark) !important;
    transform: scale(1.02) !important;
}

/* Clear button */
.nf-clear button {
    background: rgba(255,255,255,0.1) !important;
    color: var(--nf-light) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 4px !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
}
.nf-clear button:hover {
    background: rgba(255,255,255,0.18) !important;
    color: var(--nf-white) !important;
}

/* ── Metrics row ── */
.nf-empty-state {
    text-align: center;
    padding: 40px;
    color: var(--nf-gray);
    font-size: 1rem;
}

/* ══════════════════════════════════════════════════════════════════
   GENRE BADGES (used in tooltips / detail views)
   ══════════════════════════════════════════════════════════════════ */
.genre-pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 600;
    background: rgba(255,255,255,0.1);
    color: var(--nf-light);
    margin-right: 4px;
    margin-bottom: 4px;
}


/* ══════════════════════════════════════════════════════════════════
   FOOTER
   ══════════════════════════════════════════════════════════════════ */
.nf-footer {
    text-align: center;
    color: var(--nf-gray);
    font-size: 0.78rem;
    padding: 24px 48px;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin-top: 60px;
    letter-spacing: 0.05em;
}
.nf-footer a { color: var(--nf-gray); text-decoration: none; }
.nf-footer a:hover { color: var(--nf-white); }

/* ══════════════════════════════════════════════════════════════════
   SPINNER / STATUS
   ══════════════════════════════════════════════════════════════════ */
[data-testid="stSpinner"] > div {
    border-top-color: var(--nf-red) !important;
}
.stAlert {
    background: rgba(229,9,20,0.1) !important;
    border: 1px solid rgba(229,9,20,0.3) !important;
    color: var(--nf-light) !important;
}

/* ══════════════════════════════════════════════════════════════════
   DIVIDER
   ══════════════════════════════════════════════════════════════════ */
.nf-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(229,9,20,0.3), transparent);
    margin: 8px 0 32px;
    border: none;
}

/* ══════════════════════════════════════════════════════════════════
   RESPONSIVE ADJUSTMENTS
   ══════════════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .nf-navbar, .nf-section, .nf-selector-section { padding-left: 16px; padding-right: 16px; }
    .nf-hero-content { padding: 0 16px; }
    .nf-card { flex: 0 0 130px; height: 195px; }
    .nf-hero { min-height: 45vh; }
}
</style>
"""
