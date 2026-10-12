"""
Sidebar navigation and session status component.
"""


from html import escape

import streamlit as st

from config.settings import settings
from db.models.brand import Brand
from ui.components.brand_mark import render_brand_mark

PAGES = [
    ("Dashboard", "📊"),
    ("Brands", "🏢"),
    ("Social Monitoring", "🌐"),
    ("Mobile App Monitoring", "📱"),
    ("Findings Triage", "🛡️"),
    ("Investigations", "🔍"),
    ("Scan History", "⏱️"),
    ("Reports & Exports", "📑"),
    ("AI Help & Raw Data", "🤖"),
    ("Settings", "⚙️"),
]

def render_sidebar(brands: list[Brand]) -> str:
    """Renders the left navigation bar and returns the selected page."""
    with st.sidebar:
        render_brand_mark(compact=True)

        user = st.session_state.get("user")
        role = st.session_state.get("role", "viewer")
        org = st.session_state.get("org")

        if user:
            display_name = escape(user.full_name)
            email = escape(user.email)
            role_badge = f'<span class="bp-badge bp-status-new">{escape(role.upper())}</span>'
            st.markdown(
                f"""
                <div style="background:#161b22; border:1px solid #30363d; border-radius:6px; padding:8px 12px; margin-bottom:14px;">
                    <div style="font-size:0.85rem; font-weight:600; color:#f0f6fc;">{display_name}</div>
                    <div style="font-size:0.75rem; color:#8b949e;">{email}</div>
                    <div style="margin-top:6px;">{role_badge}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # Target Brand Filter
        brand_options = {"all": "All Registered Brands"}
        for b in brands:
            brand_options[b.id] = b.name

        current_brand = st.session_state.get("selected_brand_id", "all")
        # Ensure current_brand exists in options
        if current_brand not in brand_options:
            current_brand = "all"

        selected_b_id = st.selectbox(
            "Target Brand Scope",
            options=list(brand_options.keys()),
            format_func=lambda k: brand_options[k],
            index=list(brand_options.keys()).index(current_brand),
            key="brand_scope_selector",
        )
        st.session_state["selected_brand_id"] = selected_b_id

        st.markdown("---")
        st.markdown("<div style='font-size:0.75rem; color:#8b949e; font-weight:600; text-transform:uppercase; margin-bottom:6px;'>Navigation</div>", unsafe_allow_html=True)

        current_page = st.session_state.get("current_page", "Dashboard")
        for page_name, icon in PAGES:
            is_active = (current_page == page_name)
            btn_type = "primary" if is_active else "secondary"
            if st.button(f"{icon}  {page_name}", key=f"nav_{page_name}", use_container_width=True, type=btn_type):
                st.session_state["current_page"] = page_name
                st.rerun()

        st.markdown("---")

        # Synthetic Demo Mode Badge
        if settings.DEMO_MODE_ENABLED:
            st.markdown(
                """
                <div style="background:#1c2128; border:1px solid #388bfd44; border-radius:6px; padding:8px 10px; font-size:0.75rem; color:#79c0ff;">
                    🧪 <strong>Demo Mode Active</strong><br>
                    Synthetic data included
                </div>
                """,
                unsafe_allow_html=True,
            )

        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            st.session_state["user"] = None
            st.session_state["role"] = None
            st.session_state["org"] = None
            st.rerun()

    return st.session_state.get("current_page", "Dashboard")
