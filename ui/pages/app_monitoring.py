"""
Mobile Application Monitoring page.
Displays observed store listings, verified excluded official apps,
publisher mismatch evaluations, package identifier checks, and evidence comparisons.
"""


import streamlit as st
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.candidate import CandidateAppListing
from services.auth import AuthService
from services.finding_service import FindingService
from ui.components.evidence_panel import render_evidence_panel
from ui.components.risk_badges import render_risk_badge, render_status_badge


def render(db: Session, organization_id: str, brand_id: str | None = None):
    finding_service = FindingService(db)
    can_triage = AuthService.is_authorized(st.session_state.get("role", "viewer"), "analyst")

    st.markdown("## 📱 Mobile App Store Threat Monitoring")
    st.caption("Review observed store listings. The included source is synthetic demo data; live store collection is not implemented.")

    # Filters Row
    f_col1, f_col2, f_col3 = st.columns([2, 2, 2])
    with f_col1:
        store_filter = st.selectbox("App Store Filter", ["All App Stores", "Google Play", "Apple App Store"])
    with f_col2:
        view_mode = st.radio("Display View", ["Suspicious App Candidates", "Official Excluded Apps", "All Discovered Apps"], horizontal=True)
    with f_col3:
        search_query = st.text_input("🔍 Search App Title, Package, or Publisher", placeholder="e.g. fastcash or novapay")

    stmt = select(CandidateAppListing).where(CandidateAppListing.organization_id == organization_id)
    if brand_id:
        stmt = stmt.where(CandidateAppListing.brand_id == brand_id)
    if store_filter != "All App Stores":
        stmt = stmt.where(CandidateAppListing.store == store_filter)

    if view_mode == "Suspicious App Candidates":
        stmt = stmt.where(CandidateAppListing.is_excluded == False)
    elif view_mode == "Official Excluded Apps":
        stmt = stmt.where(CandidateAppListing.is_excluded == True)

    candidates = list(db.scalars(stmt.order_by(CandidateAppListing.last_observed_at.desc())).all())

    # Text search
    if search_query:
        sq = search_query.lower().strip()
        candidates = [
            c for c in candidates
            if sq in c.app_name.lower() or sq in c.package_id.lower() or sq in c.publisher_name.lower()
        ]

    st.markdown(f"**Showing {len(candidates)} mobile application listings**")

    if not candidates:
        st.info("No mobile applications found matching the active filters.")
        return

    for c in candidates:
        finding = None
        if not c.is_excluded:
            finding = finding_service.repo.get_by_candidate("app", c.id)

        with st.container(border=True):
            header_col, badge_col = st.columns([3, 1])

            with header_col:
                st.text(c.app_name)
                st.markdown(
                    f"Store: `{c.store}` | Package ID: `{c.package_id}` | Publisher: **{c.publisher_name}**"
                )
                rating_str = f"⭐ {c.rating:.1f}/5.0" if c.rating else "No rating"
                st.caption(f"Version: `{c.version or 'N/A'}` | Rating: {rating_str} | Store listing URL:")
                st.code(c.store_url, language=None)
                if c.is_synthetic:
                    st.caption("🧪 *Synthetic Demo Record*")

            with badge_col:
                if c.is_excluded:
                    st.markdown('<span class="bp-badge bp-status-false-pos">🛡️ EXCLUDED (OFFICIAL)</span>', unsafe_allow_html=True)
                    st.caption(f"Reason: {c.exclusion_reason or 'Verified Official App'}")
                elif finding:
                    st.markdown(render_risk_badge(finding.severity, finding.risk_score), unsafe_allow_html=True)
                    st.markdown(render_status_badge(finding.review_status), unsafe_allow_html=True)

            if c.description:
                st.text(f"Description: {c.description[:280]}")

            # Inspect Signals & Evidence
            if finding:
                with st.expander("🔎 Inspect Detection Signals, Publisher Mismatch & Evidence"):
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

                    # Quick Triage Actions
                    if can_triage:
                        st.markdown("##### Analyst Quick Actions")
                        qb1, qb2, qb3 = st.columns(3)
                        with qb1:
                            if st.button("Mark Confirmed Threat", key=f"app_threat_{finding.id}"):
                                finding_service.update_status(finding.id, organization_id, "Confirmed Threat")
                                st.rerun()
                        with qb2:
                            if st.button("Mark False Positive", key=f"app_fp_{finding.id}"):
                                finding_service.update_status(finding.id, organization_id, "False Positive")
                                st.rerun()
                        with qb3:
                            if st.button("Open Full Investigation", key=f"app_inv_{finding.id}", type="primary"):
                                st.session_state["current_page"] = "Findings Triage"
                                st.session_state["focus_finding_id"] = finding.id
                                st.rerun()
                    else:
                        st.caption("Read-only role: analyst actions are restricted.")
