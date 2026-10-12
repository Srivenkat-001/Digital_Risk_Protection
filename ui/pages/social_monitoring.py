"""
Social Media Monitoring page.
Displays observed social profiles, verified excluded assets,
adversarial detection signals, and evidence comparisons.
"""


import streamlit as st
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.candidate import CandidateProfile
from services.auth import AuthService
from services.finding_service import FindingService
from ui.components.evidence_panel import render_evidence_panel
from ui.components.risk_badges import render_risk_badge, render_status_badge


def render(db: Session, organization_id: str, brand_id: str | None = None):
    finding_service = FindingService(db)
    can_triage = AuthService.is_authorized(st.session_state.get("role", "viewer"), "analyst")

    st.markdown("## 🌐 Social Media Threat Monitoring")
    st.caption("Review observed social profiles. The included source is a synthetic demo connector; live platform collection is not implemented.")

    # Platform & Search Filter Row
    f_col1, f_col2, f_col3 = st.columns([2, 2, 2])
    with f_col1:
        platform_filter = st.selectbox("Platform Filter", ["All Platforms", "Twitter/X", "Instagram", "Facebook", "Telegram"])
    with f_col2:
        view_mode = st.radio("Display View", ["Suspicious Candidates (Findings)", "Official Excluded Accounts", "All Discovered Records"], horizontal=True)
    with f_col3:
        search_query = st.text_input("🔍 Search Handle or Name", placeholder="e.g. NovaPay_Help")

    # Fetch candidates based on filters
    stmt = select(CandidateProfile).where(CandidateProfile.organization_id == organization_id)
    if brand_id:
        stmt = stmt.where(CandidateProfile.brand_id == brand_id)
    if platform_filter != "All Platforms":
        stmt = stmt.where(CandidateProfile.platform == platform_filter)

    if view_mode == "Suspicious Candidates (Findings)":
        stmt = stmt.where(CandidateProfile.is_excluded == False)
    elif view_mode == "Official Excluded Accounts":
        stmt = stmt.where(CandidateProfile.is_excluded == True)

    candidates = list(db.scalars(stmt.order_by(CandidateProfile.last_observed_at.desc())).all())

    # Apply text filter if provided
    if search_query:
        sq = search_query.lower().strip()
        candidates = [c for c in candidates if sq in c.username.lower() or sq in c.display_name.lower()]

    st.markdown(f"**Showing {len(candidates)} social profile records**")

    if not candidates:
        st.info("No social profile candidates found matching the active filters.")
        return

    for c in candidates:
        # Find associated finding if not excluded
        finding = None
        if not c.is_excluded:
            finding = finding_service.repo.get_by_candidate("social", c.id)

        with st.container(border=True):
            header_col, badge_col = st.columns([3, 1])

            with header_col:
                st.text(f"{c.display_name} (@{c.username})")
                st.markdown(f"Platform: `{c.platform}` | Followers: `{c.follower_count:,}`")
                st.code(c.profile_url, language=None)
                st.caption(f"First Observed: {c.first_observed_at.strftime('%Y-%m-%d %H:%M')} | Last Observed: {c.last_observed_at.strftime('%Y-%m-%d %H:%M')}")
                if c.is_synthetic:
                    st.caption("🧪 *Synthetic Demo Record*")

            with badge_col:
                if c.is_excluded:
                    st.markdown('<span class="bp-badge bp-status-false-pos">🛡️ EXCLUDED (OFFICIAL)</span>', unsafe_allow_html=True)
                    st.caption(f"Reason: {c.exclusion_reason or 'Verified Brand Asset'}")
                elif finding:
                    st.markdown(render_risk_badge(finding.severity, finding.risk_score), unsafe_allow_html=True)
                    st.markdown(render_status_badge(finding.review_status), unsafe_allow_html=True)

            if c.bio:
                st.text(f"Bio: {c.bio}")

            # Expandable Signal & Evidence inspection
            if finding:
                with st.expander("🔎 Inspect Detection Signals, Risk Explanation & Evidence"):
                    if finding.assessment:
                        st.markdown(finding.assessment.explanation)

                    st.markdown("##### Extracted Signal Breakdown")
                    sig_cols = st.columns(3)
                    for idx, sig in enumerate(finding.signals):
                        with sig_cols[idx % 3]:
                            st.metric(
                                label=sig.signal_name.replace("_", " ").title(),
                                value=f"{int(sig.signal_value * 100)}%",
                                delta=f"Weight: {int(sig.signal_weight * 100)}%",
                            )
                            st.caption(sig.rationale)

                    # Evidence Panel
                    render_evidence_panel(finding.evidence_items)

                    # Quick Triage Button
                    if can_triage:
                        st.markdown("##### Analyst Quick Actions")
                        qb1, qb2, qb3 = st.columns(3)
                        with qb1:
                            if st.button("Mark Confirmed Threat", key=f"soc_threat_{finding.id}"):
                                finding_service.update_status(finding.id, organization_id, "Confirmed Threat")
                                st.rerun()
                        with qb2:
                            if st.button("Mark False Positive", key=f"soc_fp_{finding.id}"):
                                finding_service.update_status(finding.id, organization_id, "False Positive")
                                st.rerun()
                        with qb3:
                            if st.button("Open Full Investigation", key=f"soc_inv_{finding.id}", type="primary"):
                                st.session_state["current_page"] = "Findings Triage"
                                st.session_state["focus_finding_id"] = finding.id
                                st.rerun()
                    else:
                        st.caption("Read-only role: analyst actions are restricted.")
