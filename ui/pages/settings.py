"""
Platform Settings, Connectors Configuration & Audit Logs page.
"""

from html import escape

import streamlit as st
from sqlalchemy.orm import Session

from connectors.registry import connector_registry
from seed.reset_demo import reset_demo_data
from services.audit_service import AuditService
from services.auth import AuthService


def render(db: Session, organization_id: str):
    auth_service = AuthService(db)
    audit_service = AuditService(db)
    user = st.session_state.get("user")
    user_role = st.session_state.get("role", "viewer")
    org = st.session_state.get("org")
    is_admin = AuthService.is_authorized(user_role, "admin")

    st.markdown("## ⚙️ Platform Settings & Administration")
    st.caption("Manage tenant organization, source connectors, compliance audit logs, and demo environment.")

    tab_org, tab_conn, tab_demo, tab_audit = st.tabs([
        "🏢 Organization & Access",
        "🔌 Source Connectors",
        "🧪 Demo Sandbox Management",
        "📜 Compliance Audit Logs",
    ])

    # --- TAB 1: ORGANIZATION & ACCESS ---
    with tab_org:
        st.markdown("### Organization Profile")
        with st.container(border=True):
            st.markdown(f"**Tenant Name:** {org.name if org else 'Primary Tenant'}")
            st.markdown(f"**Tenant ID:** `{organization_id}`")
            st.markdown(f"**Your Current Role:** `{user_role.upper()}`")

        st.markdown("### Role Permissions Matrix")
        matrix_data = {
            "Permission / Action": [
                "View Dashboards, Findings & Reports",
                "Export Filtered Findings (CSV)",
                "Change Finding Review Status",
                "Open & Update Investigations",
                "Execute On-Demand Monitoring Scans",
                "Register & Delete Brand Profiles",
                "Reset Demo Environment",
            ],
            "Viewer": ["✅ Allowed", "✅ Allowed", "❌ Restricted", "❌ Restricted", "❌ Restricted", "❌ Restricted", "❌ Restricted"],
            "Analyst": ["✅ Allowed", "✅ Allowed", "✅ Allowed", "✅ Allowed", "✅ Allowed", "❌ Restricted", "❌ Restricted"],
            "Administrator": ["✅ Allowed", "✅ Allowed", "✅ Allowed", "✅ Allowed", "✅ Allowed", "✅ Allowed", "✅ Allowed"],
        }
        st.table(matrix_data)

    # --- TAB 2: SOURCE CONNECTORS ---
    with tab_conn:
        st.markdown("### Configured Monitoring Connectors")
        st.caption("Status of live platform adapters and synthetic sandbox connectors")

        report = connector_registry.get_health_report()
        for c in report:
            with st.container(border=True):
                col_c1, col_c2 = st.columns([3, 1])
                with col_c1:
                    st.markdown(f"**{escape(str(c['name']))}** (`{escape(str(c['type']).upper())}` / `{escape(str(c['platform']))}`)")
                    st.caption(f"Details: {c['details']}")
                with col_c2:
                    if c["is_healthy"]:
                        st.markdown('<span class="bp-badge bp-badge-low">ACTIVE</span>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span class="bp-badge bp-badge-critical">UNAVAILABLE</span>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### How to Enable Live Monitoring Sources")
        st.info(
            """
            Live social and app-store collection is not implemented. Connector entries are adapter placeholders;
            configuring credentials alone will not enable collection. The runnable scan workflow uses clearly
            labeled synthetic demo connectors and does not contact social networks or app stores.
            """
        )

    # --- TAB 3: DEMO SANDBOX MANAGEMENT ---
    with tab_demo:
        st.markdown("### Demo Environment & Safe Reset")
        st.caption("Safely resets synthetic candidate profiles, simulated findings, and sample cases.")

        if not is_admin:
            st.warning("🔒 Administrator role required to reset the demo environment.")
        else:
            st.markdown(
                """
                <div class="bp-demo-banner">
                    <div>
                        <strong>Safe Demo Reset Protocol:</strong>
                        This operation only purges synthetic records tagged with <code>is_synthetic=True</code>.
                        Production registered brands and genuine non-synthetic records are permanently preserved.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            confirm = st.checkbox("I confirm that I want to re-seed the synthetic NovaPay demonstration environment.")
            if st.button("🔄 Execute Safe Demo Reset", type="primary", disabled=not confirm):
                with st.spinner("Resetting synthetic demo candidates and re-running NovaPay scan..."):
                    reset_demo_data(db, organization_id)
                    st.success("Demo environment successfully reset and re-scanned!")
                    st.rerun()

    # --- TAB 4: COMPLIANCE AUDIT LOGS ---
    with tab_audit:
        st.markdown("### Security Audit Trail")
        st.caption("Immutable tamper-evident record of all status changes, scan executions, and administrative events.")

        logs = audit_service.list_logs(organization_id, limit=50)
        if not logs:
            st.info("No audit logs recorded yet.")
        else:
            for log in logs:
                with st.container(border=True):
                    c_l1, c_l2 = st.columns([3, 1])
                    with c_l1:
                        user_label = log.user.full_name if log.user else "System Automation"
                        st.markdown(f"**{log.action}** on `{log.target_type}` (`{log.target_id[:8]}`)")
                        st.caption(f"Actor: **{user_label}** | Timestamp: {log.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                        if log.details:
                            st.code(log.details, language="json")
                    with c_l2:
                        st.markdown(f"<span class='bp-badge bp-status-new'>{escape(log.target_type.upper())}</span>", unsafe_allow_html=True)
