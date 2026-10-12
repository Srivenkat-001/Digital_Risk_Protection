"""
Custom CSS and visual theming for BrandPhantom.
Dark-mode cybersecurity SaaS aesthetics with high contrast and crisp indicators.
"""

import streamlit as st


def apply_theme():
    """Injects custom CSS styling into the Streamlit app."""
    custom_css = """
    <style>
        /* Base page adjustments */
        .stApp {
            background-color: #0d1117;
            color: #c9d1d9;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        /* Top header bar */
        header[data-testid="stHeader"] {
            background-color: #161b22;
            border-bottom: 1px solid #30363d;
        }

        /* Metric cards */
        .bp-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            transition: transform 0.15s ease-in-out, border-color 0.15s ease-in-out;
        }
        .bp-card:hover {
            border-color: #58a6ff;
            transform: translateY(-2px);
        }
        .bp-card-title {
            color: #8b949e;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }
        .bp-card-value {
            color: #f0f6fc;
            font-size: 1.85rem;
            font-weight: 700;
            line-height: 1.2;
        }
        .bp-card-caption {
            color: #8b949e;
            font-size: 0.78rem;
            margin-top: 6px;
        }

        /* Risk Badges */
        .bp-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }
        .bp-badge-critical {
            background-color: rgba(248, 81, 73, 0.2);
            color: #ff7b72;
            border: 1px solid #f85149;
        }
        .bp-badge-high {
            background-color: rgba(210, 153, 34, 0.2);
            color: #d29922;
            border: 1px solid #d29922;
        }
        .bp-badge-medium {
            background-color: rgba(227, 179, 65, 0.2);
            color: #e3b341;
            border: 1px solid #e3b341;
        }
        .bp-badge-low {
            background-color: rgba(63, 185, 80, 0.2);
            color: #56d364;
            border: 1px solid #3fb950;
        }

        /* Status Badges */
        .bp-status-new {
            background: #1f6feb22;
            color: #58a6ff;
            border: 1px solid #1f6feb;
        }
        .bp-status-threat {
            background: #da363322;
            color: #f85149;
            border: 1px solid #da3633;
        }
        .bp-status-false-pos {
            background: #8b949e22;
            color: #8b949e;
            border: 1px solid #6e7681;
        }
        .bp-status-investigating {
            background: #bf870022;
            color: #d29922;
            border: 1px solid #bf8700;
        }

        /* Synthetic demo warning banner */
        .bp-demo-banner {
            background: rgba(88, 166, 255, 0.1);
            border: 1px solid #388bfd;
            border-radius: 6px;
            padding: 10px 14px;
            margin-bottom: 20px;
            color: #79c0ff;
            font-size: 0.88rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* Evidence comparison box */
        .bp-evidence-box {
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 12px;
            margin-top: 8px;
            font-size: 0.85rem;
        }

        /* Button refinements */
        .stButton>button {
            border-radius: 6px;
            font-weight: 600;
            transition: all 0.15s ease;
        }
        :root {
            --bp-bg: #0b1120;
            --bp-surface: #111a2b;
            --bp-border: #293750;
            --bp-text: #edf4ff;
            --bp-muted: #a6b5ca;
            --bp-teal: #72e4df;
        }
        .stApp {
            background:
                radial-gradient(ellipse at 12% 0%, rgba(44, 112, 151, .17), transparent 36%),
                radial-gradient(ellipse at 92% 4%, rgba(107, 78, 178, .13), transparent 32%),
                var(--bp-bg);
            color: var(--bp-text);
        }
        header[data-testid="stHeader"] {
            background: rgba(11, 17, 32, .88);
            border-bottom: 1px solid var(--bp-border);
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #111a2b, #0e1625 72%);
            border-right: 1px solid var(--bp-border);
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: var(--bp-text); letter-spacing: -.025em; }
        .stMarkdown p, [data-testid="stCaptionContainer"] { color: var(--bp-muted); }
        .bp-brand-lockup {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 4px 0 22px;
        }
        .bp-brand-lockup-centered { justify-content: center; margin: 34px 0 28px; }
        .bp-brand-lockup-compact { gap: 10px; margin: 4px 0 18px; }
        .bp-brand-icon {
            width: 48px;
            height: 48px;
            flex: 0 0 auto;
            filter: drop-shadow(0 5px 14px rgba(76, 216, 218, .2));
        }
        .bp-brand-lockup-centered .bp-brand-icon { width: 58px; height: 58px; }
        .bp-brand-copy { display: flex; flex-direction: column; gap: 3px; text-align: left; }
        .bp-brand-copy strong {
            color: var(--bp-text);
            font-size: 1.38rem;
            font-weight: 800;
            letter-spacing: -.045em;
            line-height: 1.05;
        }
        .bp-brand-copy small {
            color: var(--bp-teal);
            font-size: .67rem;
            font-weight: 700;
            letter-spacing: .11em;
            text-transform: uppercase;
        }
        .bp-brand-lockup-centered .bp-brand-copy strong { font-size: 2rem; }
        .bp-brand-lockup-centered .bp-brand-copy small { font-size: .72rem; }
        .bp-source-status {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 9px;
            border: 1px solid var(--bp-border);
            border-radius: 12px;
            padding: 12px 15px;
            margin: 12px 0 18px;
            background: rgba(17, 26, 43, .82);
            color: var(--bp-text);
        }
        .bp-source-status > span:last-child { color: var(--bp-muted); margin-left: auto; font-size: .83rem; }
        .bp-source-status-live { border-color: rgba(72, 211, 171, .48); }
        .bp-source-status-off { border-color: rgba(238, 177, 96, .5); }
        .bp-source-dot { width: 9px; height: 9px; border-radius: 50%; background: #eeb160; }
        .bp-source-status-live .bp-source-dot { background: #48d3ab; box-shadow: 0 0 12px #48d3ab; }
        .bp-card {
            background: linear-gradient(145deg, rgba(23, 35, 56, .96), rgba(17, 26, 43, .96));
            border-color: var(--bp-border);
            border-radius: 14px;
            box-shadow: 0 12px 28px rgba(0, 0, 0, .18);
            transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
        }
        .bp-card:hover {
            border-color: rgba(114, 228, 223, .66);
            transform: translateY(-3px);
            box-shadow: 0 16px 34px rgba(0, 0, 0, .27);
        }
        .bp-card-title, .bp-card-caption { color: var(--bp-muted); }
        .bp-card-value { color: var(--bp-text); }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(17, 26, 43, .56);
            border-color: var(--bp-border);
            border-radius: 12px;
        }
        .stButton>button { border-color: var(--bp-border); border-radius: 9px; }
        .stButton>button[kind="primary"] {
            background: linear-gradient(100deg, #168e98, #6655c7);
            border: 0;
            color: #fff;
        }
        .stButton>button[kind="primary"]:hover {
            background: linear-gradient(100deg, #20a8ad, #796be0);
            border: 0;
        }
        [data-baseweb="input"] > div, [data-baseweb="select"] > div {
            border-color: var(--bp-border);
            border-radius: 9px;
        }
        [data-testid="stTextInputField"],
        [data-testid="stTextInputField"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stTimeInput"] input,
        [data-testid="stSelectbox"] input {
            background-color: #172338 !important;
            color: #f4f8ff !important;
            -webkit-text-fill-color: #f4f8ff !important;
            caret-color: #f4f8ff !important;
            border-color: #7890ad !important;
            border-radius: 9px !important;
            opacity: 1 !important;
        }
        [data-testid="stTextInputField"]::placeholder,
        [data-testid="stTextInputField"] input::placeholder,
        [data-testid="stTextArea"] textarea::placeholder,
        [data-testid="stNumberInput"] input::placeholder {
            color: #c1cde0 !important;
            -webkit-text-fill-color: #c1cde0 !important;
            opacity: 1 !important;
        }
        [data-testid="stTextInputField"] [data-baseweb="input"] > div,
        [data-testid="stTextArea"] [data-baseweb="textarea"],
        [data-testid="stNumberInput"] [data-baseweb="input"] > div,
        [data-testid="stSelectbox"] [data-baseweb="select"] > div {
            background-color: #172338 !important;
            color: #f4f8ff !important;
            border-color: #7890ad !important;
            border-radius: 9px !important;
        }
        [data-testid="stSelectbox"] [role="combobox"] *,
        [data-testid="stMultiSelect"] [role="combobox"] *,
        [data-testid="stSelectbox"] [role="combobox"],
        [data-testid="stMultiSelect"] [role="combobox"] {
            color: #f4f8ff !important;
        }
        [role="listbox"] *, [role="option"] {
            color: #172338 !important;
        }
        [data-testid="stWidgetLabel"] *,
        [data-testid="stCheckbox"] label,
        [data-testid="stRadioOption"] label,
        [data-testid="stRadioOption"] p {
            color: #eaf2ff !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] p,
        [data-testid="stVerticalBlockBorderWrapper"] label,
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stCaptionContainer"],
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stText"] {
            color: #dce8f7 !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetricValue"] {
            color: #f7faff !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] code,
        [data-testid="stCode"] {
            color: #eaf2ff !important;
        }
        [data-testid="stVerticalBlockBorderWrapper"] pre {
            background-color: #0b1321 !important;
            border: 1px solid #344660;
        }
        [data-testid="stAlert"] p,
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] {
            color: #f0f5ff !important;
        }
        [data-testid="stTabs"] button[role="tab"] {
            color: #cfdaeb !important;
        }
        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: #72e4df !important;
        }
        a { color: var(--bp-teal); }
        @media (max-width: 700px) {
            .bp-source-status > span:last-child { margin-left: 18px; }
            .bp-brand-lockup-centered .bp-brand-copy strong { font-size: 1.65rem; }
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
