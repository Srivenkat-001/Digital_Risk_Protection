"""
Investigations & Case Management page.
Provides case tracking, analyst notes, decision logging, and case resolution.
"""


from html import escape

import streamlit as st
from sqlalchemy.orm import Session

from services.auth import AuthService
from services.case_service import CaseService

CASE_STATUSES = ["open", "investigating", "escalated", "resolved", "dismissed"]
CASE_PRIORITIES = ["low", "medium", "high", "critical"]

def render(db: Session, organization_id: str, brand_id: str | None = None):
    case_service = CaseService(db)
    user = st.session_state.get("user")
    user_role = st.session_state.get("role", "viewer")
    can_manage = AuthService.is_authorized(user_role, "analyst")

    st.markdown("## 🔍 Security Case Investigations")
    st.caption("Collaborative incident investigation, threat actor attribution, and decision record tracking.")

    # Status filter
    col_stat, col_search = st.columns([2, 4])
    with col_stat:
        status_filter = st.selectbox("Case Status", ["All Statuses"] + CASE_STATUSES)
    with col_search:
        search_kw = st.text_input("Search Case Title or Case Number", placeholder="e.g. CASE-2026...")

    status_arg = None if status_filter == "All Statuses" else status_filter
    cases = case_service.list_cases(organization_id, brand_id=brand_id, status=status_arg)

    if search_kw:
        sk = search_kw.lower().strip()
        cases = [c for c in cases if sk in c.case_number.lower() or sk in c.title.lower()]

    st.markdown(f"**Showing {len(cases)} investigation cases**")

    if not cases:
        st.info("No investigation cases found matching the criteria. Cases can be opened from the Findings Triage console.")
        return

    for c in cases:
        with st.container(border=True):
            h_col1, h_col2 = st.columns([3, 1])
            with h_col1:
                st.markdown(f"### {c.case_number}: {c.title}")
                st.caption(
                    f"Created: {c.created_at.strftime('%Y-%m-%d %H:%M')} | "
                    f"Lead Analyst: **{c.assigned_to.full_name if c.assigned_to else 'Unassigned'}**"
                )
                if c.summary:
                    st.write(c.summary)

            with h_col2:
                pri_color = "#f85149" if c.priority == "high" else ("#d29922" if c.priority == "medium" else "#3fb950")
                priority = escape(c.priority.upper())
                case_status = escape(c.status.upper())
                st.markdown(
                    f"""
                    <div style="text-align:right;">
                        <span class="bp-badge" style="background:{pri_color}22; color:{pri_color}; border:1px solid {pri_color};">
                            {priority} PRIORITY
                        </span><br>
                        <span class="bp-badge bp-status-new" style="margin-top:4px;">
                            STATUS: {case_status}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Finding summary preview
            if c.finding:
                with st.expander("🔗 Associated Finding Details"):
                    st.markdown(f"**Finding ID:** `#{c.finding.id[:8]}` | Severity: **{c.finding.severity}** (Score: {c.finding.risk_score:.1f})")
                    if c.finding.assessment:
                        st.markdown(c.finding.assessment.explanation)

            # Chronological Analyst Notes
            st.markdown("##### 📝 Case Activity & Investigation Notes")
            if not c.notes:
                st.caption("No notes recorded yet.")
            else:
                for n in c.notes:
                    author_name = n.author.full_name if n.author else "Analyst"
                    safe_author_name = escape(author_name)
                    safe_note_text = escape(n.note_text)
                    st.markdown(
                        f"""
                        <div style="background:#0d1117; border-left:3px solid #58a6ff; padding:8px 12px; margin-bottom:8px; border-radius:0 6px 6px 0;">
                            <div style="font-size:0.75rem; color:#8b949e; margin-bottom:4px;">
                                <strong>{safe_author_name}</strong> • {n.created_at.strftime('%Y-%m-%d %H:%M:%S')}
                            </div>
                            <div style="font-size:0.85rem; color:#f0f6fc;">
                                {safe_note_text}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Add Note & Case Updates Form
            if can_manage:
                with st.expander("✏️ Add Note / Update Case Status"):
                    note_input = st.text_area("Analyst Observation / Telemetry Update", key=f"note_txt_{c.id}")
                    col_u1, col_u2 = st.columns(2)
                    with col_u1:
                        new_case_stat = st.selectbox(
                            "Update Status",
                            options=CASE_STATUSES,
                            index=CASE_STATUSES.index(c.status) if c.status in CASE_STATUSES else 0,
                            key=f"c_stat_{c.id}",
                        )
                    with col_u2:
                        res_reason = st.text_input("Resolution Rationale (if closing)", key=f"res_{c.id}", placeholder="e.g. Account suspended by platform")

                    if st.button("Save Case Updates", key=f"save_c_{c.id}", type="primary"):
                        if note_input.strip():
                            case_service.add_note(
                                case_id=c.id,
                                organization_id=organization_id,
                                note_text=note_input.strip(),
                                author_user_id=user.id if user else None,
                            )
                        if new_case_stat != c.status or res_reason.strip():
                            case_service.update_case_status(
                                case_id=c.id,
                                organization_id=organization_id,
                                status=new_case_stat,
                                resolution_reason=res_reason.strip() or None,
                                user_id=user.id if user else None,
                            )
                        st.success("Case updated successfully!")
                        st.rerun()
