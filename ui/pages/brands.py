"""
Brand Profile Management page.
Allows registering corporate brands, attaching verified official digital assets,
and configuring trusted exclusion references.
"""

import streamlit as st
from sqlalchemy.orm import Session

from detection.logo_similarity import compute_dhash
from jobs.scan_runner import run_brand_scan
from schemas.brand import (
    BrandCreate,
    OfficialAppListingBase,
    OfficialSocialAccountBase,
)
from services.auth import AuthService
from services.brand_service import BrandService


def render(db: Session, organization_id: str):
    brand_service = BrandService(db)
    user = st.session_state.get("user")
    user_role = st.session_state.get("role", "viewer")
    can_edit = AuthService.is_authorized(user_role, "analyst")
    can_delete = AuthService.is_authorized(user_role, "admin")

    st.markdown("## 🏢 Brand Profile Management")
    st.caption("Configure official corporate identities, verified assets, and approved digital presence.")
    st.info("Included scan connectors return synthetic demo candidates only; no social network or app store is queried.")

    tab_list, tab_create = st.tabs(["📋 Registered Brands", "➕ Register New Brand"])

    # --- TAB 1: REGISTERED BRANDS ---
    with tab_list:
        brands = brand_service.list_brands(organization_id)
        if not brands:
            st.info("No brands registered yet in this organization. Use the 'Register New Brand' tab to add your first brand.")
        else:
            for b in brands:
                with st.container(border=True):
                    col_info, col_actions = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"### {b.display_name} (`{b.name}`)")
                        st.markdown(f"🌐 Official Website | Industry: `{b.industry or 'General'}`")
                        st.code(b.official_website, language=None)
                        if b.legal_name:
                            st.caption(f"Legal Entity: {b.legal_name}")
                        if b.description:
                            st.write(b.description)

                        # Asset Badges
                        soc_count = len(b.official_social_accounts)
                        app_count = len(b.official_app_listings)
                        dom_count = len(b.approved_domains)
                        alias_count = len(b.aliases)
                        logo_count = len(b.logos)

                        st.markdown(
                            f"""
                            <div style="display:flex; gap:8px; margin-top:8px;">
                                <span class="bp-badge bp-status-new">📱 {soc_count} Verified Social Handles</span>
                                <span class="bp-badge bp-status-new">📦 {app_count} Official Apps</span>
                                <span class="bp-badge bp-status-false-pos">🌐 {dom_count} Approved Domains</span>
                                <span class="bp-badge bp-status-false-pos">🏷️ {alias_count} Aliases</span>
                                <span class="bp-badge bp-status-false-pos">🖼️ {logo_count} Reference Logos</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    with col_actions:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if can_edit and st.button("🚀 Run Scan", key=f"scan_btn_{b.id}", type="primary", use_container_width=True):
                            with st.spinner(f"Running automated scan for {b.name}..."):
                                job = run_brand_scan(
                                    db=db,
                                    brand_id=b.id,
                                    organization_id=organization_id,
                                    triggered_by_user_id=user.id if user else None,
                                )
                                st.success(f"Scan complete! Discovered {job.total_candidates_found} candidates, {job.new_findings_count} new findings, {job.excluded_assets_count} excluded official assets.")
                                st.rerun()
                        elif not can_edit:
                            st.caption("Read-only role: scan initiation is restricted.")

                        if can_delete:
                            if st.button("🗑️ Delete Brand", key=f"del_btn_{b.id}", use_container_width=True):
                                brand_service.delete_brand(b.id, organization_id, user_id=user.id if user else None)
                                st.warning(f"Brand '{b.name}' deleted.")
                                st.rerun()

                    # View Verified Assets Expander
                    with st.expander(f"Inspect Verified Assets for {b.name}"):
                        c_soc, c_app = st.columns(2)
                        with c_soc:
                            st.markdown("##### Verified Social Accounts (Trusted Exclusion)")
                            if not b.official_social_accounts:
                                st.caption("No official social handles configured.")
                            for acc in b.official_social_accounts:
                                st.markdown(f"- **{acc.platform}**: `@{acc.handle}`")
                                st.code(acc.account_url, language=None)
                                if acc.platform_account_id:
                                    st.caption(f"Platform ID: `{acc.platform_account_id}`")
                        with c_app:
                            st.markdown("##### Verified Mobile App Listings (Trusted Exclusion)")
                            if not b.official_app_listings:
                                st.caption("No official mobile apps configured.")
                            for app in b.official_app_listings:
                                st.markdown(f"- **{app.store}**: `{app.package_id}`")
                                st.caption(f"Publisher: {app.publisher_name} | Name: {app.app_name}")

    # --- TAB 2: REGISTER NEW BRAND ---
    with tab_create:
        if not can_edit:
            st.warning("🔒 You have Read-Only permissions. Administrator or Threat Analyst role required to register brands.")
            return

        st.markdown("### Register Brand Identity")
        with st.form("create_brand_form"):
            c1, c2 = st.columns(2)
            with c1:
                brand_name = st.text_input("Brand Identifier / Common Name*", placeholder="e.g. AcmePay")
                display_name = st.text_input("Public Display Name*", placeholder="e.g. AcmePay Global")
                legal_name = st.text_input("Legal Entity Name", placeholder="e.g. Acme Financial Holdings Inc.")
            with c2:
                official_website = st.text_input("Primary Official Website*", placeholder="https://acmepay.io")
                industry = st.selectbox("Industry", ["Fintech & Payments", "Banking", "E-Commerce", "Healthcare", "Technology", "Social Media", "Gaming", "Other"])
                description = st.text_area("Brand Summary & Business Description", placeholder="Brief description of legitimate business offerings...")

            st.markdown("#### Approved Aliases & Domains")
            aliases_raw = st.text_input("Brand Aliases / Alternative Spellings (comma separated)", placeholder="Acme Pay, AcmePayment, AcmeWallet")
            domains_raw = st.text_input("Approved Legitimate Domains (comma separated)", placeholder="acmepay.io, checkout.acmepay.io, auth.acmepay.io")

            st.markdown("#### Primary Verified Social Handle (For Trusted Exclusion)")
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                social_platform = st.selectbox("Social Platform", ["Twitter/X", "Instagram", "Facebook", "LinkedIn", "Telegram", "TikTok"])
            with sc2:
                social_handle = st.text_input("Official Handle", placeholder="e.g. AcmePayOfficial")
            with sc3:
                social_url = st.text_input("Profile URL", placeholder="https://twitter.com/AcmePayOfficial")

            st.markdown("#### Primary Verified Mobile App Listing (For Trusted Exclusion)")
            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                app_store = st.selectbox("App Store", ["Google Play", "Apple App Store"])
            with ac2:
                app_package = st.text_input("Official Package / Bundle ID", placeholder="e.g. com.acmepay.wallet")
            with ac3:
                app_publisher = st.text_input("Official Publisher Name", placeholder="e.g. Acme Technologies Inc.")

            app_title = st.text_input("App Title", placeholder="e.g. AcmePay: Send Money & Pay")
            app_store_url = st.text_input("Store URL", placeholder="https://play.google.com/store/apps/details?id=com.acmepay.wallet")

            st.markdown("#### Official Brand Logo Reference")
            logo_upload = st.file_uploader(
                "Upload official logo (PNG, JPEG, or WebP; optional, maximum 5 MB)",
                type=["png", "jpg", "jpeg", "webp"],
                help="The image is used to calculate a perceptual hash; the uploaded image itself is not retained.",
            )

            submit_btn = st.form_submit_button("Register Brand & Save Official Assets", type="primary", use_container_width=True)

            if submit_btn:
                logo_hash = None
                logo_error = None
                if logo_upload:
                    logo_bytes = logo_upload.getvalue()
                    if len(logo_bytes) > 5 * 1024 * 1024:
                        logo_error = "Logo images must be 5 MB or smaller."
                    else:
                        logo_hash = compute_dhash(logo_bytes)
                        if not logo_hash:
                            logo_error = "The uploaded logo is not a supported, readable image or exceeds the image-size limit."

                if not brand_name or not display_name or not official_website:
                    st.error("Brand Identifier, Display Name, and Primary Website are required fields.")
                elif logo_error:
                    st.error(logo_error)
                else:
                    try:
                        aliases_list = [a.strip() for a in aliases_raw.split(",") if a.strip()]
                        domains_list = [d.strip() for d in domains_raw.split(",") if d.strip()]

                        social_accounts = []
                        if social_handle and social_url:
                            social_accounts.append(OfficialSocialAccountBase(
                                platform=social_platform,
                                handle=social_handle.lstrip("@"),
                                account_url=social_url,
                                is_verified=True,
                                notes="Configured during registration",
                            ))

                        app_listings = []
                        if app_package and app_publisher and app_store_url:
                            app_listings.append(OfficialAppListingBase(
                                store=app_store,
                                app_name=app_title or display_name,
                                package_id=app_package,
                                publisher_name=app_publisher,
                                store_url=app_store_url,
                                is_verified=True,
                                notes="Configured during registration",
                            ))

                        b_create = BrandCreate(
                            name=brand_name,
                            display_name=display_name,
                            legal_name=legal_name,
                            industry=industry,
                            official_website=official_website,
                            description=description,
                            aliases=aliases_list,
                            approved_domains=domains_list,
                            official_social_accounts=social_accounts,
                            official_app_listings=app_listings,
                        )

                        new_brand = brand_service.create_brand(
                            organization_id=organization_id,
                            brand_data=b_create,
                            user_id=user.id if user else None,
                        )

                        if logo_hash:
                            brand_service.repo.add_logo(
                                brand_id=new_brand.id,
                                perceptual_hash=logo_hash,
                                is_primary=True,
                            )

                        st.success(f"Successfully registered brand '{new_brand.name}' with verified exclusion assets!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"Failed to register brand: {e}")
