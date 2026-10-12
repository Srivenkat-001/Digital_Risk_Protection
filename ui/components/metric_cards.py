from html import escape
from typing import Any

import streamlit as st


def render_metric_card(title: str, value: Any, caption: str = "", help_text: str = ""):
    """Renders a styled cybersecurity KPI card."""
    help_attr = f'title="{escape(str(help_text), quote=True)}"' if help_text else ""
    html = f"""
    <div class="bp-card" {help_attr}>
        <div class="bp-card-title">{escape(str(title))}</div>
        <div class="bp-card-value">{escape(str(value))}</div>
        <div class="bp-card-caption">{escape(str(caption))}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
