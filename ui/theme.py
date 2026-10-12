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
            --bp-bg: #09111f;
            --bp-surface: #111c2d;
            --bp-border: #293a52;
            --bp-text: #f1f5fb;
            --bp-muted: #b8c6d9;
            --bp-teal: #72dff2;
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
        [data-testid="stMainBlockContainer"] {
            max-width: 1560px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] > button {
            min-height: 2.7rem;
            justify-content: flex-start;
            padding-left: 1rem;
            border-color: transparent;
            background: transparent;
            color: #c8d5e8;
            transition: background .16s ease, border-color .16s ease, transform .16s ease;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
            background: rgba(114, 228, 223, .09);
            border-color: rgba(114, 228, 223, .22);
            color: #f4f8ff;
            transform: translateX(2px);
        }
        [data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(100deg, rgba(30, 153, 164, .25), rgba(113, 94, 211, .22));
            border: 1px solid rgba(114, 228, 223, .35);
            color: #f5fbff;
            box-shadow: inset 3px 0 #72e4df;
        }
        [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
            min-height: 2.7rem;
        }
        .bp-page-hero {
            position: relative;
            overflow: hidden;
            padding: 1.5rem 1.7rem;
            margin: 0 0 1.25rem;
            border: 1px solid rgba(105, 142, 183, .28);
            border-radius: 18px;
            background:
                radial-gradient(circle at 92% 5%, rgba(123, 102, 229, .25), transparent 34%),
                linear-gradient(115deg, rgba(21, 43, 63, .98), rgba(17, 26, 43, .98) 62%, rgba(25, 28, 57, .98));
            box-shadow: 0 18px 45px rgba(0, 0, 0, .2);
        }
        .bp-page-hero::after {
            position: absolute;
            right: -55px;
            bottom: -115px;
            width: 240px;
            height: 240px;
            border: 1px solid rgba(114, 228, 223, .13);
            border-radius: 50%;
            box-shadow: 0 0 0 26px rgba(114, 228, 223, .035), 0 0 0 54px rgba(114, 228, 223, .025);
            content: "";
            pointer-events: none;
        }
        .bp-hero-eyebrow {
            margin-bottom: .45rem;
            color: #80e7df;
            font-size: .7rem;
            font-weight: 800;
            letter-spacing: .16em;
            text-transform: uppercase;
        }
        .bp-page-hero h1 {
            position: relative;
            z-index: 1;
            margin: 0;
            color: #f4f8ff;
            font-size: clamp(1.55rem, 2.7vw, 2.25rem);
            font-weight: 800;
            letter-spacing: -.04em;
            line-height: 1.15;
        }
        .bp-page-hero p {
            position: relative;
            z-index: 1;
            max-width: 760px;
            margin: .6rem 0 0;
            color: #c1d0e3;
            font-size: .96rem;
            line-height: 1.55;
        }
        .bp-section-heading {
            margin: 1.45rem 0 .75rem;
            color: #eff5ff;
            font-size: 1.15rem;
            font-weight: 750;
            letter-spacing: -.02em;
        }
        .bp-card {
            position: relative;
            min-height: 130px;
            padding: 18px 19px;
        }
        .bp-card::before {
            position: absolute;
            top: 17px;
            right: 17px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #72e4df;
            box-shadow: 0 0 14px rgba(114, 228, 223, .55);
            content: "";
        }
        .bp-card-value { margin-top: 9px; font-size: 2rem; letter-spacing: -.04em; }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(145deg, rgba(21, 33, 52, .88), rgba(15, 24, 39, .9));
            border-color: rgba(105, 129, 160, .28);
            box-shadow: 0 10px 28px rgba(0, 0, 0, .12);
        }
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: rgba(114, 228, 223, .36);
        }
        [data-testid="stTextInput"] [data-baseweb="input"] > div,
        [data-testid="stTextArea"] [data-baseweb="textarea"],
        [data-testid="stNumberInput"] [data-baseweb="input"] > div,
        [data-testid="stDateInput"] [data-baseweb="input"] > div,
        [data-testid="stTimeInput"] [data-baseweb="input"] > div,
        [data-testid="stTextInputField"] [data-baseweb="input"] > div {
            background: #172338 !important;
            border: 1px solid #607794 !important;
            border-radius: 10px !important;
            box-shadow: inset 0 1px 2px rgba(0, 0, 0, .18);
        }
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stTimeInput"] input {
            color: #f4f8ff !important;
            -webkit-text-fill-color: #f4f8ff !important;
            caret-color: #72e4df !important;
        }
        [data-testid="stTextInput"] input::placeholder,
        [data-testid="stTextArea"] textarea::placeholder {
            color: #bdcbe0 !important;
            -webkit-text-fill-color: #bdcbe0 !important;
        }
        [data-testid="stTextInput"] [data-baseweb="input"]:focus-within > div,
        [data-testid="stTextArea"] [data-baseweb="textarea"]:focus-within,
        [data-testid="stNumberInput"] [data-baseweb="input"]:focus-within > div {
            border-color: #72e4df !important;
            box-shadow: 0 0 0 3px rgba(114, 228, 223, .14) !important;
        }
        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
            background: #172338 !important;
            border: 1px solid #607794 !important;
            border-radius: 10px !important;
        }
        [data-testid="stSelectbox"] [role="combobox"],
        [data-testid="stSelectbox"] [role="combobox"] *,
        [data-testid="stMultiSelect"] [role="combobox"],
        [data-testid="stMultiSelect"] [role="combobox"] * {
            color: #f4f8ff !important;
            -webkit-text-fill-color: #f4f8ff !important;
        }
        [role="listbox"], [role="option"] { background: #f8fbff !important; color: #172338 !important; }
        [role="option"] * { color: #172338 !important; }
        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label,
        [data-testid="stCheckbox"] label,
        [data-testid="stRadio"] label {
            color: #e3edf9 !important;
            font-weight: 600;
        }
        [data-testid="stTabs"] [role="tablist"] {
            gap: .35rem;
            border-bottom: 1px solid #2a3b52;
        }
        [data-testid="stTabs"] button[role="tab"] {
            min-height: 2.8rem;
            border-radius: 10px 10px 0 0;
            color: #bfcee1 !important;
            font-weight: 650;
        }
        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            background: rgba(114, 228, 223, .08);
            color: #85e8e1 !important;
        }
        .stButton > button, [data-testid="stFormSubmitButton"] > button {
            min-height: 2.65rem;
            border: 1px solid #40546f;
            border-radius: 10px;
            color: #edf4ff;
            font-weight: 700;
            transition: transform .15s ease, border-color .15s ease, background .15s ease;
        }
        .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
            border-color: #72e4df;
            color: #fff;
            transform: translateY(-1px);
        }
        .stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"] {
            border: 1px solid rgba(114, 228, 223, .35);
            background: linear-gradient(105deg, #148e98, #6859c9);
            color: #fff;
            box-shadow: 0 6px 18px rgba(42, 123, 157, .2);
        }
        [data-testid="stAlert"] {
            border-radius: 12px;
            border: 1px solid rgba(116, 153, 191, .28);
        }
        [data-testid="stAlert"] p,
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] { color: #edf4ff !important; }
        [data-testid="stExpander"] {
            overflow: hidden;
            border: 1px solid rgba(105, 129, 160, .32);
            border-radius: 11px;
            background: rgba(16, 26, 42, .6);
        }
        [data-testid="stExpander"] summary { color: #e6effb; font-weight: 650; }
        [data-testid="stDataFrame"] {
            border: 1px solid rgba(105, 129, 160, .32);
            border-radius: 10px;
            overflow: hidden;
        }
        [data-testid="stCode"] {
            border: 1px solid rgba(105, 129, 160, .25);
            border-radius: 9px;
        }
        .bp-demo-banner {
            border-color: rgba(238, 177, 96, .5);
            border-radius: 12px;
            background: rgba(125, 82, 23, .18);
            color: #ffe0aa;
        }
        .bp-source-status { border-radius: 12px; }
        .bp-badge { padding: 5px 10px; border-radius: 999px; }
        hr { border-color: rgba(105, 129, 160, .22); }
        @media (max-width: 850px) {
            [data-testid="stMainBlockContainer"] { padding: 1.1rem 1rem 2rem; }
            .bp-page-hero { padding: 1.2rem; border-radius: 14px; }
        }
        :root {
            --bp-bg: #0d0c1b;
            --bp-surface: #17162a;
            --bp-raised: #211f3b;
            --bp-border: #393553;
            --bp-text: #f5f2ff;
            --bp-muted: #c5c0dc;
            --bp-blue: #ad91ff;
            --bp-cyan: #5ce1d0;
        }
        .stApp {
            background:
                radial-gradient(ellipse at 8% 0%, rgba(116, 74, 208, .24), transparent 38%),
                radial-gradient(ellipse at 96% 8%, rgba(20, 176, 164, .13), transparent 32%),
                var(--bp-bg);
            color: var(--bp-text);
        }
        header[data-testid="stHeader"] {
            background: rgba(13, 12, 27, .96);
            border-bottom-color: rgba(156, 131, 224, .2);
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #17152c, #100f20 78%);
            border-right-color: rgba(156, 131, 224, .2);
        }
        .bp-user-card {
            padding: 10px 12px;
            margin-bottom: 14px;
            border: 1px solid rgba(156, 131, 224, .26);
            border-radius: 10px;
            background: linear-gradient(135deg, rgba(43, 35, 74, .55), rgba(22, 30, 49, .72));
        }
        .bp-user-name { color: var(--bp-text); font-size: .85rem; font-weight: 700; }
        .bp-user-email { color: var(--bp-muted); font-size: .75rem; overflow-wrap: anywhere; }
        .bp-user-role { margin-top: 7px; }
        .bp-demo-mode {
            padding: 9px 11px;
            border: 1px solid rgba(92, 225, 208, .26);
            border-radius: 10px;
            background: rgba(34, 128, 119, .13);
            color: #9cebdd;
            font-size: .75rem;
        }
        .bp-brand-icon { filter: drop-shadow(0 5px 17px rgba(151, 113, 255, .4)); }
        .bp-brand-copy small, .bp-hero-eyebrow { color: #70e6d6; }
        .bp-brand-copy strong { color: var(--bp-text); }
        .bp-page-hero {
            border-color: rgba(173, 145, 255, .36);
            background:
                radial-gradient(circle at 92% 0%, rgba(145, 88, 232, .38), transparent 39%),
                radial-gradient(circle at 0% 110%, rgba(30, 197, 177, .2), transparent 45%),
                linear-gradient(115deg, #211b3e, #17172d 58%, #142a38);
            box-shadow: 0 20px 48px rgba(5, 4, 18, .36), inset 0 1px rgba(255, 255, 255, .04);
        }
        .bp-page-hero::after {
            border-color: rgba(173, 145, 255, .2);
            box-shadow: 0 0 0 26px rgba(173, 145, 255, .06), 0 0 0 54px rgba(92, 225, 208, .035);
        }
        .bp-page-hero h1, .bp-section-heading { color: var(--bp-text); }
        .bp-page-hero p, .bp-card-title, .bp-card-caption { color: var(--bp-muted); }
        .bp-card {
            border-color: rgba(156, 131, 224, .24);
            background:
                radial-gradient(circle at 100% 0%, rgba(110, 75, 178, .13), transparent 48%),
                linear-gradient(145deg, rgba(29, 27, 51, .98), rgba(18, 25, 41, .98));
            box-shadow: 0 12px 30px rgba(5, 4, 18, .24), inset 0 1px rgba(255, 255, 255, .035);
        }
        .bp-card::before {
            background: linear-gradient(135deg, #5ce1d0, #ad91ff);
            box-shadow: 0 0 15px rgba(137, 112, 239, .58);
        }
        .bp-card:hover, [data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: rgba(173, 145, 255, .56);
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-color: rgba(126, 111, 169, .28);
            background: linear-gradient(145deg, rgba(27, 25, 46, .94), rgba(16, 23, 38, .97));
        }
        [data-testid="stSidebar"] [data-testid="stButton"] > button {
            color: #c4d0df;
        }
        [data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
            background: linear-gradient(90deg, rgba(148, 104, 225, .16), rgba(40, 189, 172, .08));
            border-color: rgba(173, 145, 255, .3);
        }
        [data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(100deg, rgba(125, 82, 205, .28), rgba(24, 150, 145, .2));
            border-color: rgba(173, 145, 255, .4);
            box-shadow: inset 3px 0 #ad91ff, 0 5px 18px rgba(6, 4, 22, .17);
        }
        [data-baseweb="input"] > div,
        [data-baseweb="select"] > div,
        [data-testid="stTextArea"] [data-baseweb="textarea"],
        [data-testid="stTextInput"] [data-baseweb="input"] > div,
        [data-testid="stNumberInput"] [data-baseweb="input"] > div,
        [data-testid="stDateInput"] [data-baseweb="input"] > div,
        [data-testid="stTimeInput"] [data-baseweb="input"] > div,
        [data-testid="stTextInputField"] [data-baseweb="input"] > div {
            background-color: #19182e !important;
            border-color: #655c83 !important;
        }
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input,
        [data-testid="stTimeInput"] input,
        [data-testid="stSelectbox"] [role="combobox"],
        [data-testid="stSelectbox"] [role="combobox"] *,
        [data-testid="stMultiSelect"] [role="combobox"],
        [data-testid="stMultiSelect"] [role="combobox"] * {
            color: var(--bp-text) !important;
            -webkit-text-fill-color: var(--bp-text) !important;
            caret-color: var(--bp-cyan) !important;
        }
        [data-testid="stTextInput"] input::placeholder,
        [data-testid="stTextArea"] textarea::placeholder {
            color: #b8b2cc !important;
            -webkit-text-fill-color: #b8b2cc !important;
        }
        [data-testid="stTextInput"] [data-baseweb="input"]:focus-within > div,
        [data-testid="stTextArea"] [data-baseweb="textarea"]:focus-within,
        [data-testid="stNumberInput"] [data-baseweb="input"]:focus-within > div,
        [data-testid="stSelectbox"] [data-baseweb="select"]:focus-within > div {
            border-color: var(--bp-blue) !important;
            box-shadow: 0 0 0 3px rgba(173, 145, 255, .2) !important;
        }
        [data-testid="stWidgetLabel"] *,
        [data-testid="stCheckbox"] label,
        [data-testid="stRadio"] label { color: #d6e0ed !important; }
        [data-testid="stTabs"] [role="tablist"] { border-bottom-color: var(--bp-border); }
        [data-testid="stTabs"] button[role="tab"] { color: #bdc9d9 !important; }
        [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            background: linear-gradient(90deg, rgba(173, 145, 255, .15), rgba(92, 225, 208, .08));
            color: var(--bp-blue) !important;
        }
        .stButton > button, [data-testid="stFormSubmitButton"] > button {
            border-color: #40536c;
            color: var(--bp-text);
        }
        .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
            border-color: var(--bp-blue);
        }
        .stButton > button[kind="primary"],
        [data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"] {
            border-color: rgba(196, 174, 255, .4);
            background: linear-gradient(105deg, #7750d4, #a64fc2 55%, #159e9d);
            box-shadow: 0 8px 23px rgba(105, 64, 195, .3);
        }
        [data-testid="stAlert"] {
            background: rgba(18, 31, 49, .92);
            border-color: rgba(107, 138, 174, .32);
        }
        [data-testid="stAlert"] p,
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] { color: #eaf1f9 !important; }
        [data-testid="stExpander"] {
            border-color: rgba(101, 128, 161, .28);
            background: rgba(15, 26, 42, .78);
        }
        [data-testid="stExpander"] summary { color: #e5edf7; }
        [data-testid="stDataFrame"] { border-color: rgba(101, 128, 161, .28); }
        [data-testid="stCode"] { border-color: rgba(101, 128, 161, .25); }
        .bp-demo-banner {
            border-color: rgba(224, 168, 83, .45);
            background: rgba(126, 83, 25, .17);
            color: #f4d6a2;
        }
        .bp-source-status-live { border-color: rgba(69, 201, 154, .42); }
        .bp-source-status-live .bp-source-dot { background: #45c99a; box-shadow: 0 0 11px rgba(69, 201, 154, .7); }
        .bp-source-status-off { border-color: rgba(224, 168, 83, .42); }
        .bp-source-dot { background: #e0a853; }
        .bp-status-new { background: rgba(173, 145, 255, .12); color: #c3adff; border-color: #755cb4; }
        .bp-status-threat { background: rgba(255, 107, 120, .12); color: #ff929b; border-color: #b8515d; }
        .bp-status-false-pos { background: rgba(168, 182, 202, .1); color: #c0cad8; border-color: #66778e; }
        .bp-status-investigating { background: rgba(244, 201, 107, .1); color: #f4cf7e; border-color: #ad8840; }
        .bp-badge-critical { background: rgba(255, 107, 120, .13); color: #ff929b; border-color: #b8515d; }
        .bp-badge-high { background: rgba(255, 159, 90, .13); color: #ffb47d; border-color: #b76b3d; }
        .bp-badge-medium { background: rgba(244, 201, 107, .13); color: #f4cf7e; border-color: #ad8840; }
        .bp-badge-low { background: rgba(69, 201, 154, .13); color: #72ddb3; border-color: #318d6f; }
        a { color: var(--bp-blue); }
        hr { border-color: rgba(101, 128, 161, .23); }
        :focus-visible { outline: 2px solid var(--bp-blue) !important; outline-offset: 2px; }
        button:disabled, [aria-disabled="true"] {
            opacity: .58 !important;
            cursor: not-allowed !important;
        }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
