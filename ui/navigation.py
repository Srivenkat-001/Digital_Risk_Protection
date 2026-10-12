"""
Authentication routing, page dispatcher, and permission enforcement.
"""

import streamlit as st
from sqlalchemy.orm import Session

from config.settings import settings as app_settings
from services.auth import AuthService
from services.brand_service import BrandService
from ui.components.sidebar import render_sidebar
from ui.pages import (
    app_monitoring,
    brands,
    dashboard,
    findings,
    investigations,
    reports,
    scan_history,
    settings,
    social_monitoring,
)


def render_login_view(db: Session):
    """Renders the secure authentication gateway with fast role switching for evaluation."""
    auth_service = AuthService(db)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 50px; margin-bottom: 25px;">
                <span style="font-size: 3.5rem;">👻</span>
                <h1 style="color: #58a6ff; margin: 0; font-size: 2.2rem; font-weight: 800;">BrandPhantom</h1>
                <p style="color: #8b949e; font-size: 1.0rem;">AI-Powered Digital Risk Protection Platform</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.markdown("### Secure Sign-In")
            email = st.text_input("Corporate Email")
            password = st.text_input("Password", type="password")

            if st.button("Authenticate", type="primary", use_container_width=True):
                user = auth_service.authenticate_user(email, password)
                if user:
                    orgs = auth_service.user_repo.get_user_organizations(user.id)
                    if orgs:
                        org, role = orgs[0]
                        st.session_state["user"] = user
                        st.session_state["org"] = org
                        st.session_state["role"] = role
                        st.success(f"Authenticated as {user.full_name} ({role})")
                        st.rerun()
                    else:
                        st.error("No active organization membership associated with this user account.")
                else:
                    st.error("Invalid credentials. Please verify your email and password.")

            if app_settings.DEMO_MODE_ENABLED and app_settings.APP_ENV.lower() != "production":
                st.markdown("---")
                st.caption("Local demo role selection only. These passwordless shortcuts are disabled in production.")
                c1, c2, c3 = st.columns(3)
                for column, label, demo_email in (
                    (c1, "Admin", "admin@brandphantom.io"),
                    (c2, "Analyst", "analyst@brandphantom.io"),
                    (c3, "Viewer", "viewer@brandphantom.io"),
                ):
                    with column:
                        if st.button(label, use_container_width=True):
                            demo_user = auth_service.authenticate_demo_user(demo_email)
                            memberships = auth_service.user_repo.get_user_organizations(demo_user.id) if demo_user else []
                            if memberships:
                                org, role = memberships[0]
                                st.session_state["user"] = demo_user
                                st.session_state["org"] = org
                                st.session_state["role"] = role
                                st.rerun()
                            st.error("Demo account is unavailable. Check that the demo environment was seeded.")

def dispatch_page(db: Session):
    """Main authenticated router."""
    org = st.session_state["org"]
    brand_service = BrandService(db)
    tenant_brands = brand_service.list_brands(org.id)

    current_page = render_sidebar(tenant_brands)

    selected_brand_id = st.session_state.get("selected_brand_id")
    effective_brand_id = None if selected_brand_id == "all" else selected_brand_id

    # Route to page
    if current_page == "Dashboard":
        dashboard.render(db, org.id, effective_brand_id)
    elif current_page == "Brands":
        brands.render(db, org.id)
    elif current_page == "Social Monitoring":
        social_monitoring.render(db, org.id, effective_brand_id)
    elif current_page == "Mobile App Monitoring":
        app_monitoring.render(db, org.id, effective_brand_id)
    elif current_page == "Findings Triage":
        findings.render(db, org.id, effective_brand_id)
    elif current_page == "Investigations":
        investigations.render(db, org.id, effective_brand_id)
    elif current_page == "Scan History":
        scan_history.render(db, org.id, effective_brand_id)
    elif current_page == "Reports & Exports":
        reports.render(db, org.id, effective_brand_id)
    elif current_page == "Settings":
        settings.render(db, org.id)
    else:
        dashboard.render(db, org.id, effective_brand_id)
