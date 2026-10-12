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
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
