"""
Findings Triage & Decision-Support page.
Comprehensive analyst console for triaging alerts, inspecting evidence,
changing statuses, and opening formal investigation cases.
"""


import streamlit as st
from sqlalchemy.orm import Session

from config.settings import settings
from services.auth import AuthService
from services.case_service import CaseService
from services.finding_service import FindingService
from ui.components.evidence_panel import render_evidence_panel
from ui.components.risk_badges import render_risk_badge, render_status_badge


def render(db: Session, organization_id: str, brand_id: str | None = None):
    finding_service = FindingService(db)
    case_service = CaseService(db)
    user = st.session_state.get("user")
    user_role = st.session_state.get("role", "viewer")
    can_triage = AuthService.is_authorized(user_role, "analyst")

    st.markdown("## 🛡️ Findings Triage & Decision Support")
    st.caption("Investigate suspicious candidate sightings, review explainable evidence, and assign disposition.")

    # Filter row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sev_filter = st.selectbox("Severity Filter", ["All Severities"] + settings.ALL_SEVERITIES)
    with c2:
        stat_filter = st.selectbox("Status Filter", ["All Statuses"] + settings.ALL_STATUSES)
    with c3:
        type_filter = st.selectbox("Candidate Type", ["All Types", "social", "app"])
    with c4:
        search_kw = st.text_input("Finding ID / Keyword", placeholder="Search...")

    # Load findings
    sev_arg = None if sev_filter == "All Severities" else sev_filter
    stat_arg = None if stat_filter == "All Statuses" else stat_filter
    type_arg = None if type_filter == "All Types" else type_filter

    findings_list = finding_service.list_findings(
        organization_id=organization_id,
        brand_id=brand_id,
        severity=sev_arg,
        review_status=stat_arg,
        candidate_type=type_arg,
        limit=100,
    )

    if search_kw:
        sk = search_kw.lower().strip()
        findings_list = [
            f for f in findings_list
            if sk in f.id.lower() or (f.assessment and sk in f.assessment.explanation.lower())
        ]

    st.markdown(f"**Showing {len(findings_list)} actionable findings**")

    if not findings_list:
        st.info("No findings match the selected criteria.")
        return

    # Check if a specific finding was selected from another page
    focus_id = st.session_state.get("focus_finding_id")

    for f in findings_list:
        candidate_obj = finding_service.get_candidate_for_finding(f)
        is_focused = (focus_id == f.id)

        border_style = True
        with st.container(border=border_style):
            top_col1, top_col2 = st.columns([3, 1])

            with top_col1:
                cand_title = ""
                cand_sub = ""
                if f.candidate_type == "social" and candidate_obj:
                    cand_title = f"Social Profile: {candidate_obj.display_name} (@{candidate_obj.username})"
                    cand_sub = f"Platform: {candidate_obj.platform}"
                elif f.candidate_type == "app" and candidate_obj:
                    cand_title = f"Mobile App: {candidate_obj.app_name}"
                    cand_sub = f"Store: {candidate_obj.store} | Package ID: {candidate_obj.package_id} | Publisher: {candidate_obj.publisher_name}"

                st.markdown(f"### Finding `#{f.id[:8]}`")
                st.text(cand_title)
                st.text(cand_sub)
                if f.candidate_type == "social" and candidate_obj:
                    st.code(candidate_obj.profile_url, language=None)
                st.caption(f"Brand: **{f.brand.name}** | Observed: {f.created_at.strftime('%Y-%m-%d %H:%M')}")
                if f.is_synthetic:
                    st.caption("🧪 *Synthetic Demo Finding*")

            with top_col2:
                st.markdown(render_risk_badge(f.severity, f.risk_score), unsafe_allow_html=True)
                st.markdown(render_status_badge(f.review_status), unsafe_allow_html=True)

            # Explainable assessment
            if f.assessment:
                st.markdown(f.assessment.explanation)

            # Signal meters
            st.markdown("##### Evaluated Detection Signals")
            sig_cols = st.columns(min(len(f.signals), 4) or 1)
            for idx, sig in enumerate(f.signals[:4]):
                with sig_cols[idx % 4]:
                    st.metric(
                        label=sig.signal_name.replace("_", " ").title(),
                        value=f"{int(sig.signal_value * 100)}%",
                        delta=f"Weight: {int(sig.signal_weight * 100)}%",
                    )

            # Evidence artifacts
            render_evidence_panel(f.evidence_items)

            # Triage & Case Actions
            st.markdown("---")
            act_col1, act_col2 = st.columns([2, 1])

            with act_col1:
                st.markdown("##### Update Triage Disposition")
                if not can_triage:
                    st.caption("🔒 Read-Only role: Status changes and case operations restricted.")
                else:
                    new_status = st.selectbox(
                        "Set Review Status",
                        options=settings.ALL_STATUSES,
                        index=settings.ALL_STATUSES.index(f.review_status) if f.review_status in settings.ALL_STATUSES else 0,
                        key=f"status_sel_{f.id}",
                    )
                    notes_text = st.text_input("Analyst Disposition Note", key=f"notes_in_{f.id}", placeholder="Reason for status change...")

                    if st.button("Apply Status Change", key=f"apply_btn_{f.id}"):
                        finding_service.update_status(
                            finding_id=f.id,
                            organization_id=organization_id,
                            review_status=new_status,
                            user_id=user.id if user else None,
                            notes=notes_text,
                        )
                        st.success(f"Updated status of finding #{f.id[:8]} to '{new_status}'")
                        st.rerun()

            with act_col2:
                st.markdown("##### Case Management")
                # Check if case exists
                existing_case = case_service.repo.get_by_finding_id(f.id)
                if existing_case:
                    st.markdown(f"**Linked Investigation:** `{existing_case.case_number}`")
                    st.caption(f"Status: **{existing_case.status.upper()}** | Priority: **{existing_case.priority.upper()}**")
                    if st.button("Go to Investigation", key=f"view_case_{existing_case.id}", use_container_width=True):
                        st.session_state["current_page"] = "Investigations"
                        st.rerun()
                else:
                    if can_triage:
                        if st.button("📁 Open Investigation Case", key=f"open_case_{f.id}", type="primary", use_container_width=True):
                            case = case_service.open_investigation_from_finding(
                                organization_id=organization_id,
                                finding_id=f.id,
                                title=f"Investigation into {cand_title[:60]}",
                                priority="high" if f.severity in ("High", "Critical") else "medium",
                                summary=f"Formal security investigation opened for finding #{f.id[:8]} (Risk Score: {f.risk_score:.1f}).",
                                assigned_to_user_id=user.id if user else None,
                                user_id=user.id if user else None,
                            )
                            st.success(f"Investigation case {case.case_number} created!")
                            st.rerun()
