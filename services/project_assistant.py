"""Tenant-scoped, local search over project guidance and persisted risk records."""

import json
import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models.candidate import CandidateAppListing, CandidateProfile
from db.models.finding import Finding

STOP_WORDS = {
    "about", "all", "and", "are", "can", "data", "did", "does", "for", "from",
    "give", "have", "help", "how", "into", "is", "list", "me", "my", "of", "our",
    "show", "tell", "the", "this", "what", "when", "where", "which", "who", "with",
}

PROJECT_GUIDANCE = {
    "overview": (
        "BrandPhantom monitors configured brands for possible impersonation across social profiles "
        "and mobile-app listings. It stores observations, explainable heuristic signals, risk findings, "
        "and analyst review status. A score is an indicator, not proof of malicious activity."
    ),
    "live": (
        "Live social-profile search is currently available only for public Bluesky profiles when "
        "LIVE_CONNECTORS_ENABLED is true. Apple App Store lookup is also opt-in. Searches are bounded "
        "and may be incomplete. Instagram, Snapchat, X, Facebook, TikTok, LinkedIn, and Telegram "
        "reference/demo profiles are not live account feeds."
    ),
    "demo": (
        "Synthetic examples are generated for demonstrations and are explicitly marked. They are not "
        "real accounts or verified threats. Use the source label and raw source metadata to distinguish "
        "them from live public observations."
    ),
    "scoring": (
        "Risk scores are deterministic heuristic assessments based on available signals such as name/"
        "handle similarity, suspicious language, publisher/package evidence, and logo hashes when "
        "available. Missing evidence reduces coverage; the score does not prove fraud. Analysts should "
        "review the signal rationales and evidence before changing a finding's disposition."
    ),
    "storage": (
        "Candidate profiles/listings, raw connector metadata, observations, findings, signals, "
        "assessments, and evidence are stored in the configured SQL database. Tenant and selected-brand "
        "filters constrain this assistant's record search. Streamlit Cloud SQLite is ephemeral; use "
        "configured PostgreSQL for durable hosted storage."
    ),
    "privacy": (
        "This assistant runs local keyword retrieval against the selected tenant's stored database "
        "records. It does not send questions or record data to Meta AI or another external LLM."
    ),
}


def _parse_raw_metadata(value: str | None) -> Any:
    if not value:
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {"unparsed_raw_metadata": value}


def _record_text(record: dict[str, Any]) -> str:
    return json.dumps(record, ensure_ascii=False, default=str).casefold()


def _finding_summary(finding: Finding | None) -> dict[str, Any] | None:
    if finding is None:
        return None
    return {
        "finding_id": finding.id,
        "severity": finding.severity,
        "risk_score": round(finding.risk_score, 1),
        "review_status": finding.review_status,
        "synthetic": finding.is_synthetic,
        "created_at": finding.created_at.isoformat() if finding.created_at else None,
        "explanation": finding.assessment.explanation if finding.assessment else None,
        "signals": [
            {
                "name": signal.signal_name,
                "value": signal.signal_value,
                "weight": signal.signal_weight,
                "rationale": signal.rationale,
            }
            for signal in finding.signals
        ],
        "evidence": [
            {
                "type": item.evidence_type,
                "title": item.title,
                "description": item.description,
                "candidate_value": item.candidate_value,
                "confidence": item.confidence,
            }
            for item in finding.evidence_items
        ],
    }


def search_project_data(
    db: Session,
    organization_id: str,
    question: str,
    brand_id: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Return grounded project guidance and relevant tenant-owned raw records."""
    normalized_question = question.strip()
    if not normalized_question:
        raise ValueError("Enter a question or search term.")
    if limit < 1 or limit > 100:
        raise ValueError("Result limit must be between 1 and 100.")

    query = normalized_question.casefold()
    tokens = {
        token
        for token in re.findall(r"[\w.-]+", query, flags=re.UNICODE)
        if len(token) > 2 and token not in STOP_WORDS
    }

    if any(word in query for word in ("live", "platform", "instagram", "snapchat", "bluesky", "twitter")):
        guidance = PROJECT_GUIDANCE["live"]
    elif any(word in query for word in ("synthetic", "demo", "sample", "fake")):
        guidance = PROJECT_GUIDANCE["demo"]
    elif any(word in query for word in ("score", "risk", "severity", "detect", "signal")):
        guidance = PROJECT_GUIDANCE["scoring"]
    elif any(word in query for word in ("database", "stored", "storage", "raw", "metadata")):
        guidance = PROJECT_GUIDANCE["storage"]
    elif any(word in query for word in ("private", "privacy", "external", "meta", "ai")):
        guidance = PROJECT_GUIDANCE["privacy"]
    else:
        guidance = PROJECT_GUIDANCE["overview"]

    finding_stmt = select(Finding).where(Finding.organization_id == organization_id)
    social_stmt = select(CandidateProfile).where(
        CandidateProfile.organization_id == organization_id
    )
    app_stmt = select(CandidateAppListing).where(
        CandidateAppListing.organization_id == organization_id
    )
    if brand_id:
        finding_stmt = finding_stmt.where(Finding.brand_id == brand_id)
        social_stmt = social_stmt.where(CandidateProfile.brand_id == brand_id)
        app_stmt = app_stmt.where(CandidateAppListing.brand_id == brand_id)

    findings = list(db.scalars(finding_stmt).all())
    finding_by_candidate = {
        (finding.candidate_type, finding.candidate_id): finding for finding in findings
    }
    records: list[dict[str, Any]] = []
    for candidate in db.scalars(social_stmt).all():
        records.append(
            {
                "record_id": candidate.id,
                "record_type": "social",
                "brand_id": candidate.brand_id,
                "platform": candidate.platform,
                "name": candidate.display_name,
                "username": candidate.username,
                "url": candidate.profile_url,
                "bio": candidate.bio,
                "followers": candidate.follower_count,
                "synthetic": candidate.is_synthetic,
                "excluded": candidate.is_excluded,
                "source_metadata": _parse_raw_metadata(candidate.raw_metadata),
                "finding": _finding_summary(
                    finding_by_candidate.get(("social", candidate.id))
                ),
                "last_observed_at": candidate.last_observed_at.isoformat()
                if candidate.last_observed_at
                else None,
            }
        )

    for candidate in db.scalars(app_stmt).all():
        records.append(
            {
                "record_id": candidate.id,
                "record_type": "app",
                "brand_id": candidate.brand_id,
                "platform": candidate.store,
                "name": candidate.app_name,
                "username": candidate.package_id,
                "publisher": candidate.publisher_name,
                "url": candidate.store_url,
                "description": candidate.description,
                "synthetic": candidate.is_synthetic,
                "excluded": candidate.is_excluded,
                "source_metadata": _parse_raw_metadata(candidate.raw_metadata),
                "finding": _finding_summary(finding_by_candidate.get(("app", candidate.id))),
                "last_observed_at": candidate.last_observed_at.isoformat()
                if candidate.last_observed_at
                else None,
            }
        )

    ranked: list[tuple[int, dict[str, Any]]] = []
    for record in records:
        content = _record_text(record)
        score = sum(content.count(token) for token in tokens)
        if score:
            ranked.append((score, record))
    ranked.sort(
        key=lambda item: (
            item[0],
            item[1]["last_observed_at"] or "",
        ),
        reverse=True,
    )

    matched = [record for _, record in ranked[:limit]]
    return {
        "guidance": guidance,
        "organization_record_count": len(records),
        "finding_count": len(findings),
        "matched_records": matched,
        "match_count": len(ranked),
        "result_limit": limit,
        "scope_brand_id": brand_id,
        "external_ai_used": False,
    }
