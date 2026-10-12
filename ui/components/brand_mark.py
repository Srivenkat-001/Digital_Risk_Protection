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
                    <linearGradient id="bp-shield-gradient" x1="5" y1="4" x2="43" y2="44">
                        <stop stop-color="#69e2f5"/>
                        <stop offset=".48" stop-color="#528eff"/>
                        <stop offset="1" stop-color="#8b68ff"/>
                    </linearGradient>
                </defs>
                <path d="M24 2.8 42.2 9.7v12.6c0 11.1-7 18.5-18.2 23C12.8 40.8 5.8 33.4 5.8 22.3V9.7L24 2.8Z"
                      fill="url(#bp-shield-gradient)"/>
                <path d="M24 8.1 37 13v9.1c0 8-4.8 13.8-13 17.5-8.2-3.7-13-9.5-13-17.5V13l13-4.9Z"
                      fill="#101a2b"/>
                <path d="M18.2 16.2h7.1c3 0 4.8 1.6 4.8 4 0 1.7-.9 2.9-2.4 3.5 2 .5 3.2 1.9 3.2 4 0 2.9-2.1 4.8-5.6 4.8h-7.1V16.2Zm3.1 2.8v3.5h3.4c1.5 0 2.3-.6 2.3-1.8 0-1.1-.8-1.7-2.3-1.7h-3.4Zm0 6.2v4.4h3.9c1.7 0 2.6-.8 2.6-2.2 0-1.4-.9-2.2-2.6-2.2h-3.9Z"
                      fill="#f4f8ff"/>
                <path d="M13.8 24h3.1" stroke="#69e2f5" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
            <span class="bp-brand-copy">
                <strong>BrandPhantom</strong>
                <small>Digital Risk Protection</small>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
