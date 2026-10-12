"""Local project help and tenant-scoped raw-data search."""

import json

import streamlit as st
from sqlalchemy.orm import Session

from services.project_assistant import search_project_data


def render(db: Session, organization_id: str, brand_id: str | None = None) -> None:
    st.markdown("## 🤖 BrandPhantom AI Project Help & Raw Data")
    st.caption(
        "Search project guidance and the selected tenant's saved findings, evidence, and connector metadata."
    )
    st.info(
        "This is a private, database-grounded search assistant—not Meta AI or a generative LLM. "
        "Questions and raw records stay in this app and are not sent to an external AI provider."
    )

    with st.form("project_assistant_search"):
        question = st.text_input(
            "Ask about the project or search its saved records",
            placeholder="e.g. Show fake Instagram accounts with high risk and their raw source metadata",
        )
        result_limit = st.selectbox("Maximum matching records to show", [20, 50, 100], index=1)
        submitted = st.form_submit_button("Search project and raw data", type="primary")

    if submitted:
        try:
            result = search_project_data(
                db,
                organization_id=organization_id,
                question=question,
                brand_id=brand_id,
                limit=result_limit,
            )
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.session_state["assistant_result"] = result
            st.session_state["assistant_question"] = question

    result = st.session_state.get("assistant_result")
    if not result:
        st.markdown("### What this assistant can help with")
        st.markdown(
            "- Explain live versus synthetic sources, detection signals, scoring limitations, and storage.\n"
            "- Find stored social profiles and app listings by platform, name, handle, package, or evidence text.\n"
            "- Inspect each matching record's raw connector metadata, risk assessment, signals, and evidence."
        )
        st.caption(
            f"Current scope contains {organization_id and 'this organization'}'s records"
            f"{' for the selected brand' if brand_id else ''}. Access is tenant-scoped."
        )
        return

    st.markdown(f"**Question:** {st.session_state.get('assistant_question', '')}")
    st.markdown(result["guidance"])
    metric_cols = st.columns(3)
    metric_cols[0].metric("Saved candidate records", result["organization_record_count"])
    metric_cols[1].metric("Saved findings", result["finding_count"])
    metric_cols[2].metric("Matching records", result["match_count"])

    if not result["matched_records"]:
        st.info("No saved records matched those terms in the current organization/brand scope.")
        return

    st.markdown(f"### Matching saved records (showing {len(result['matched_records'])})")
    for record in result["matched_records"]:
        status = "Synthetic demo" if record["synthetic"] else "Live-source observation"
        finding = record["finding"]
        finding_label = (
            f"{finding['severity']} · {finding['risk_score']:.1f} · {finding['review_status']}"
            if finding
            else "No finding attached"
        )
        title = (
            f"{record['platform']} · {record['name']} · {status} · {finding_label}"
        )
        with st.expander(title):
            st.write(f"**Record type:** {record['record_type']}")
            st.write(f"**Handle / package:** {record.get('username') or 'Not recorded'}")
            st.write(f"**URL:** {record.get('url') or 'Not recorded'}")
            st.write(f"**Excluded as official:** {'Yes' if record['excluded'] else 'No'}")
            if record.get("bio"):
                st.write(f"**Bio / description:** {record['bio']}")
            if record.get("publisher"):
                st.write(f"**Publisher:** {record['publisher']}")
            if finding:
                if finding.get("explanation"):
                    st.markdown("**Assessment explanation**")
                    st.write(finding["explanation"])
                if finding["signals"]:
                    st.markdown("**Detection signals**")
                    st.dataframe(finding["signals"], use_container_width=True, hide_index=True)
                if finding["evidence"]:
                    st.markdown("**Evidence**")
                    st.dataframe(finding["evidence"], use_container_width=True, hide_index=True)
            st.markdown("**Raw stored record (JSON)**")
            st.code(
                json.dumps(record, ensure_ascii=False, indent=2, default=str),
                language="json",
            )
