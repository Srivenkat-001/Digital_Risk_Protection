"""Reusable BrandPhantom logo and wordmark."""

import streamlit as st


def render_brand_mark(*, centered: bool = False, compact: bool = False) -> None:
    """Render the product mark without requiring an external image asset."""
    classes = "bp-brand-lockup"
    if centered:
        classes += " bp-brand-lockup-centered"
    if compact:
        classes += " bp-brand-lockup-compact"

    st.markdown(
        f"""
        <div class="{classes}" role="img" aria-label="BrandPhantom digital risk protection">
            <svg class="bp-brand-icon" viewBox="0 0 48 48" aria-hidden="true">
                <defs>
                    <linearGradient id="bp-shield-gradient" x1="4" y1="4" x2="44" y2="44">
                        <stop stop-color="#72e4df"/>
                        <stop offset="1" stop-color="#8b7cff"/>
                    </linearGradient>
                </defs>
                <path d="M24 3 42 10v12c0 11-7.5 18.5-18 23C13.5 40.5 6 33 6 22V10L24 3Z"
                      fill="url(#bp-shield-gradient)"/>
                <path d="M24 9 36 13.7v8.1c0 7.2-4.4 13-12 17-7.6-4-12-9.8-12-17v-8.1L24 9Z"
                      fill="#101827"/>
                <path d="M15.5 24s3.1-5 8.5-5 8.5 5 8.5 5-3.1 5-8.5 5-8.5-5-8.5-5Z"
                      fill="none" stroke="#72e4df" stroke-width="2"/>
                <circle cx="24" cy="24" r="2.5" fill="#fff"/>
            </svg>
            <span class="bp-brand-copy">
                <strong>BrandPhantom</strong>
                <small>Digital Risk Protection</small>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
