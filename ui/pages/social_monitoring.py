"""
Social Media Monitoring page.
Displays observed social profiles, verified excluded assets,
adversarial detection signals, and evidence comparisons.
"""


import streamlit as st
from sqlalchemy import select
from sqlalchemy.orm import Session

from config.settings import settings
from db.models.candidate import CandidateProfile
from jobs.scan_runner import run_brand_scan
from services.auth import AuthService
from services.brand_service import BrandService
from services.finding_service import FindingService
from ui.components.evidence_panel import render_evidence_panel
from ui.components.risk_badges import render_risk_badge, render_status_badge


def render(db: Session, organization_id: str, brand_id: str | None = None):
    finding_service = FindingService(db)
    can_triage = AuthService.is_authorized(st.session_state.get("role", "viewer"), "analyst")
    can_scan = AuthService.is_authorized(st.session_state.get("role", "viewer"), "analyst")

    st.markdown("## 🌐 Social Media Threat Monitoring")
    st.caption(
        "Run on-demand searches of public Bluesky profiles and review clearly labeled synthetic examples "
        "for additional social platforms."
    )

    live_enabled = settings.LIVE_CONNECTORS_ENABLED
    st.markdown(
        f'<div class="bp-source-status {"bp-source-status-live" if live_enabled else "bp-source-status-off"}">'
        f'<span class="bp-source-dot"></span><strong>Bluesky live search {"enabled" if live_enabled else "disabled"}</strong>'
        '<span>Public profiles only · no login · results are not comprehensive</span></div>',
        unsafe_allow_html=True,
    )
    if not live_enabled:
        st.info(
            "To enable real Bluesky searches, set `LIVE_CONNECTORS_ENABLED=true` in your local `.env` "
            "or Streamlit Cloud App settings → Secrets, then restart/reboot the app. "
            "This public search does not require an API key."
        )

    brands = BrandService(db).list_brands(organization_id)
    eligible_brands = [brand for brand in brands if brand_id is None or brand.id == brand_id]
    selected_brand_id = None
    if not eligible_brands:
        st.info("Register an active brand before searching for related public profiles.")
    elif not can_scan:
        st.warning("Analyst or Administrator access is required to run searches or generate sample profiles.")
    else:
        if len(eligible_brands) == 1:
            selected_brand = eligible_brands[0]
            selected_brand_id = selected_brand.id
            st.markdown(f"**Search target:** {selected_brand.name}")
        else:
            brand_options = {brand.name: brand.id for brand in eligible_brands}
            selected_name = st.selectbox("Brand to search", list(brand_options))
            selected_brand_id = brand_options[selected_name]

        live_col, demo_col = st.columns(2)
        with live_col:
            if st.button(
                "Search live Bluesky profiles",
                type="primary",
                disabled=not live_enabled or not selected_brand_id,
                help="Queries Bluesky's public profile-search API and stores real results separately from demo records.",
            ):
                with st.spinner("Searching public Bluesky profiles and evaluating results..."):
                    scan = run_brand_scan(
                        db=db,
                        brand_id=selected_brand_id,
                        organization_id=organization_id,
                        triggered_by_user_id=(
                            st.session_state["user"].id if st.session_state.get("user") else None
                        ),
                        source_types=["social"],
                        include_demo_sources=False,
                    )
                if scan.status == "failed":
                    st.error(f"Live search failed: {scan.error_message or 'No details were provided.'}")
                elif scan.status == "partial":
                    st.warning(
                        f"Search completed with a source error. {scan.total_candidates_found} live profiles "
                        f"were collected. Details: {scan.error_message}"
                    )
                else:
                    st.success(
                        f"Live Bluesky search complete: {scan.total_candidates_found} public profiles found, "
                        f"{scan.new_findings_count} new findings, {scan.excluded_assets_count} verified official accounts excluded."
                    )
        with demo_col:
            if st.button(
                "Generate sample profiles for all platforms",
                disabled=not settings.DEMO_MODE_ENABLED or not selected_brand_id,
                help="Creates clearly labeled synthetic examples for Bluesky, X, Instagram, Facebook, TikTok, LinkedIn, and Telegram. No external service is queried.",
            ):
                with st.spinner("Creating clearly labeled sample profiles..."):
                    scan = run_brand_scan(
                        db=db,
                        brand_id=selected_brand_id,
                        organization_id=organization_id,
                        triggered_by_user_id=(
                            st.session_state["user"].id if st.session_state.get("user") else None
                        ),
                        source_types=["social"],
                        include_live_sources=False,
                    )
                if scan.status == "failed":
                    st.error(f"Sample generation failed: {scan.error_message or 'No details were provided.'}")
                else:
                    st.session_state["social_view_mode"] = "All Discovered Records"
                    st.session_state["social_source_filter"] = "Synthetic demo only"
                    st.success(
                        f"Synthetic samples ready: {scan.total_candidates_found} example profiles across "
                        "seven platforms. These are not real accounts."
                    )

    # Platform & Search Filter Row
    f_col1, f_col2, f_col3, f_col4 = st.columns([2, 2, 2, 2])
    with f_col1:
        platform_filter = st.selectbox(
            "Platform Filter",
            [
                "All Platforms",
                "Bluesky",
                "Twitter/X",
                "Instagram",
                "Facebook",
                "TikTok",
                "LinkedIn",
                "Telegram",
                "Snapchat",
            ],
        )
    with f_col2:
        view_mode = st.radio(
            "Display View",
            ["Suspicious Candidates (Findings)", "Official Excluded Accounts", "All Discovered Records"],
            horizontal=True,
            key="social_view_mode",
        )
    with f_col3:
        search_query = st.text_input("🔍 Search Handle or Name", placeholder="e.g. NovaPay_Help")
    with f_col4:
        source_filter = st.selectbox(
            "Record Source",
            ["All records", "Live only", "Synthetic demo only"],
            key="social_source_filter",
        )

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
        candidates = [c for c in candidates if sq in (c.username or "").lower() or sq in (c.display_name or "").lower()]
    if source_filter == "Live only":
        candidates = [candidate for candidate in candidates if not candidate.is_synthetic]
    elif source_filter == "Synthetic demo only":
        candidates = [candidate for candidate in candidates if candidate.is_synthetic]

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
                    st.caption(
                        "🧪 Synthetic demo example — not a real account and not collected from this platform."
                    )
                elif c.platform == "Bluesky":
                    st.caption("Live public profile metadata from the Bluesky AppView API.")

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
