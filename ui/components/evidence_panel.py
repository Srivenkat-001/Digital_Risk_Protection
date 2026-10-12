"""
Evidence inspection panel component.
Displays side-by-side comparison of official brand reference vs candidate values.
"""


from html import escape

import streamlit as st

from db.models.finding import Evidence


def render_evidence_panel(evidence_items: list[Evidence]):
    """Renders structured evidence cards for analyst review."""
    if not evidence_items:
        st.info("No explicit evidence artifacts generated for this item.")
        return

    st.markdown("#### Supporting Evidence Artifacts")
    for idx, ev in enumerate(evidence_items):
        with st.container():
            st.markdown(f"**{idx + 1}. {ev.title}** (`{ev.evidence_type}`)")
            st.caption(ev.description)

            col1, col2 = st.columns(2)
            with col1:
                official_value = escape(ev.official_value or "N/A")
                st.markdown(
                    f"""
                    <div class="bp-evidence-box">
                        <div style="color: #3fb950; font-weight:600; margin-bottom:4px;">Official Reference</div>
                        <div>{official_value}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col2:
                candidate_value = escape(ev.candidate_value or "N/A")
                st.markdown(
                    f"""
                    <div class="bp-evidence-box">
                        <div style="color: #f85149; font-weight:600; margin-bottom:4px;">Candidate Observed</div>
                        <div>{candidate_value}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.caption(f"Signal Confidence: **{int(ev.confidence * 100)}%**")
            st.markdown("---")
