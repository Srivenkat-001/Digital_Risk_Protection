"""
Scan runner orchestration engine.
Executes end-to-end monitoring scans:
Brand config -> Connector collection -> Normalization -> Deduplication ->
Official asset exclusion -> Signal extraction -> Risk scoring -> Evidence generation -> Persistence.
"""


from sqlalchemy.orm import Session

from config.logging_config import logger
from connectors.registry import connector_registry
from db.models.scan import ScanJob
from db.repositories.audit_repo import AuditRepository
from db.repositories.brand_repo import BrandRepository
from db.repositories.candidate_repo import CandidateRepository
from db.repositories.finding_repo import FindingRepository
from db.repositories.scan_repo import ScanRepository
from detection.apps import extract_app_signals
from detection.explanations import generate_risk_explanation
from detection.official_asset_match import (
    check_app_official_exclusion,
    check_social_official_exclusion,
)
from detection.scoring import compute_risk_score
from detection.social import extract_social_signals


def run_brand_scan(
    db: Session,
    brand_id: str,
    organization_id: str,
    triggered_by_user_id: str | None = None,
    source_types: list[str] | None = None,
    include_demo_sources: bool = True,
    include_live_sources: bool = True,
) -> ScanJob:
    """
    Executes a complete monitoring scan for a brand across configured sources.
    Strictly enforces official asset exclusion prior to generating risk findings.
    """
    if source_types is None:
        source_types = ["social", "app"]

    brand_repo = BrandRepository(db)
    candidate_repo = CandidateRepository(db)
    finding_repo = FindingRepository(db)
    scan_repo = ScanRepository(db)
    audit_repo = AuditRepository(db)

    brand = brand_repo.get_by_id(brand_id, organization_id)
    if not brand:
        raise ValueError(f"Brand ID '{brand_id}' not found in organization.")

    sources_str = ",".join(source_types)
    scan_job = scan_repo.create(
        organization_id=organization_id,
        brand_id=brand_id,
        triggered_by_user_id=triggered_by_user_id,
        source_types=sources_str,
    )

    total_candidates = 0
    excluded_count = 0
    new_findings = 0
    error_notes = []

    try:
        connectors = connector_registry.get_connectors(only_active_or_demo=True)
        # Filter by selected source types
        active_connectors = [c for c in connectors if c.source_type in source_types]
        if not include_demo_sources:
            active_connectors = [c for c in active_connectors if not c.is_demo]
        if not include_live_sources:
            active_connectors = [c for c in active_connectors if c.is_demo]

        if not active_connectors:
            logger.warning("No active connectors found for selected source types.")
            error_notes.append("No active connectors configured for selected types.")

        for connector in active_connectors:
            try:
                is_healthy, status_msg = connector.health_check()
                if not is_healthy and not connector.is_demo:
                    error_notes.append(f"{connector.name}: {status_msg}")
                    continue

                raw_records = connector.collect_candidates(brand)

                if connector.source_type == "social":
                    for raw in raw_records:
                        total_candidates += 1
                        # 1. Normalization & Deduplication
                        candidate, is_new = candidate_repo.upsert_social_candidate(
                            organization_id=organization_id,
                            brand_id=brand.id,
                            platform=raw["platform"],
                            profile_url=raw["profile_url"],
                            username=raw["username"],
                            display_name=raw["display_name"],
                            bio=raw.get("bio"),
                            platform_account_id=raw.get("platform_account_id"),
                            avatar_url=raw.get("avatar_url"),
                            avatar_hash=raw.get("avatar_hash"),
                            follower_count=raw.get("follower_count", 0),
                            raw_metadata=raw.get("raw_metadata"),
                            is_synthetic=raw.get("is_synthetic", False),
                        )
                        candidate_repo.record_observation(scan_job.id, "social", candidate.id)

                        # 2. Official Asset Exclusion
                        is_excluded, reason, _ = check_social_official_exclusion(
                            platform=candidate.platform,
                            username=candidate.username,
                            profile_url=candidate.profile_url,
                            platform_account_id=candidate.platform_account_id,
                            official_accounts=brand.official_social_accounts,
                        )

                        if is_excluded:
                            candidate_repo.mark_social_excluded(candidate.id, reason or "Verified Official Social Asset")
                            excluded_count += 1
                            # Excluded from generating adversarial finding
                            continue

                        # 3. Detection Signal Extraction & Risk Scoring
                        signals, evidence_list = extract_social_signals(candidate, brand)
                        score, severity, coverage, enriched_signals = compute_risk_score(signals)
                        explanation = generate_risk_explanation(
                            score=score,
                            severity=severity,
                            coverage=coverage,
                            enriched_signals=enriched_signals,
                            candidate_type="social",
                            brand_name=brand.name,
                        )

                        # 4. Save Finding & Evidence
                        existing_finding = finding_repo.get_by_candidate("social", candidate.id)
                        if not existing_finding:
                            finding = finding_repo.create(
                                organization_id=organization_id,
                                brand_id=brand.id,
                                candidate_type="social",
                                candidate_id=candidate.id,
                                risk_score=score,
                                severity=severity,
                                scan_job_id=scan_job.id,
                                is_synthetic=candidate.is_synthetic,
                            )
                            # Save signals
                            for sig_name, sig_data in enriched_signals.items():
                                finding_repo.add_signal(
                                    finding_id=finding.id,
                                    signal_name=sig_name,
                                    signal_value=sig_data["value"],
                                    signal_weight=sig_data["weight"],
                                    contribution=sig_data["contribution"],
                                    rationale=sig_data["rationale"],
                                )
                            # Save assessment
                            finding_repo.set_assessment(
                                finding_id=finding.id,
                                score=score,
                                severity=severity,
                                explanation=explanation,
                            )
                            # Save evidence items
                            for ev in evidence_list:
                                finding_repo.add_evidence(
                                    finding_id=finding.id,
                                    evidence_type=ev.evidence_type,
                                    title=ev.title,
                                    description=ev.description,
                                    official_value=ev.official_value,
                                    candidate_value=ev.candidate_value,
                                    confidence=ev.confidence,
                                    file_path_or_url=ev.file_path_or_url,
                                )
                            new_findings += 1
                        else:
                            finding_repo.refresh_existing_finding(
                                finding=existing_finding,
                                scan_job_id=scan_job.id,
                                is_synthetic=candidate.is_synthetic,
                                score=score,
                                severity=severity,
                                enriched_signals=enriched_signals,
                                explanation=explanation,
                                evidence_items=evidence_list,
                            )

                elif connector.source_type == "app":
                    for raw in raw_records:
                        total_candidates += 1
                        # 1. Normalization & Deduplication
                        candidate, is_new = candidate_repo.upsert_app_candidate(
                            organization_id=organization_id,
                            brand_id=brand.id,
                            store=raw["store"],
                            app_name=raw["app_name"],
                            package_id=raw["package_id"],
                            publisher_name=raw["publisher_name"],
                            store_url=raw["store_url"],
                            description=raw.get("description"),
                            icon_url=raw.get("icon_url"),
                            icon_hash=raw.get("icon_hash"),
                            version=raw.get("version"),
                            rating=raw.get("rating"),
                            raw_metadata=raw.get("raw_metadata"),
                            is_synthetic=raw.get("is_synthetic", False),
                        )
                        candidate_repo.record_observation(scan_job.id, "app", candidate.id)

                        # 2. Official Asset Exclusion
                        is_excluded, reason, _ = check_app_official_exclusion(
                            store=candidate.store,
                            package_id=candidate.package_id,
                            store_url=candidate.store_url,
                            official_apps=brand.official_app_listings,
                        )

                        if is_excluded:
                            candidate_repo.mark_app_excluded(candidate.id, reason or "Verified Official Mobile Application")
                            excluded_count += 1
                            continue

                        # 3. Detection Signal Extraction & Risk Scoring
                        signals, evidence_list = extract_app_signals(candidate, brand)
                        score, severity, coverage, enriched_signals = compute_risk_score(signals)
                        explanation = generate_risk_explanation(
                            score=score,
                            severity=severity,
                            coverage=coverage,
                            enriched_signals=enriched_signals,
                            candidate_type="app",
                            brand_name=brand.name,
                        )

                        # 4. Save Finding & Evidence
                        existing_finding = finding_repo.get_by_candidate("app", candidate.id)
                        if not existing_finding:
                            finding = finding_repo.create(
                                organization_id=organization_id,
                                brand_id=brand.id,
                                candidate_type="app",
                                candidate_id=candidate.id,
                                risk_score=score,
                                severity=severity,
                                scan_job_id=scan_job.id,
                                is_synthetic=candidate.is_synthetic,
                            )
                            # Save signals
                            for sig_name, sig_data in enriched_signals.items():
                                finding_repo.add_signal(
                                    finding_id=finding.id,
                                    signal_name=sig_name,
                                    signal_value=sig_data["value"],
                                    signal_weight=sig_data["weight"],
                                    contribution=sig_data["contribution"],
                                    rationale=sig_data["rationale"],
                                )
                            # Save assessment
                            finding_repo.set_assessment(
                                finding_id=finding.id,
                                score=score,
                                severity=severity,
                                explanation=explanation,
                            )
                            # Save evidence items
                            for ev in evidence_list:
                                finding_repo.add_evidence(
                                    finding_id=finding.id,
                                    evidence_type=ev.evidence_type,
                                    title=ev.title,
                                    description=ev.description,
                                    official_value=ev.official_value,
                                    candidate_value=ev.candidate_value,
                                    confidence=ev.confidence,
                                    file_path_or_url=ev.file_path_or_url,
                                )
                            new_findings += 1
                        else:
                            finding_repo.refresh_existing_finding(
                                finding=existing_finding,
                                scan_job_id=scan_job.id,
                                is_synthetic=candidate.is_synthetic,
                                score=score,
                                severity=severity,
                                enriched_signals=enriched_signals,
                                explanation=explanation,
                                evidence_items=evidence_list,
                            )

            except Exception as conn_err:
                logger.error("Error executing connector %s (%s).", connector.name, type(conn_err).__name__)
                error_notes.append(f"{connector.name}: collection failed ({type(conn_err).__name__}).")

        final_status = "partial" if error_notes else "completed"
        err_msg = "; ".join(error_notes) if error_notes else None

        scan_repo.complete(
            scan_job_id=scan_job.id,
            status=final_status,
            total_candidates=total_candidates,
            new_findings=new_findings,
            excluded_assets=excluded_count,
            error_message=err_msg,
        )

        audit_repo.log(
            organization_id=organization_id,
            action="SCAN_EXECUTION_COMPLETED",
            target_type="scan",
            target_id=scan_job.id,
            user_id=triggered_by_user_id,
            details={
                "brand_id": brand.id,
                "status": final_status,
                "total_candidates": total_candidates,
                "excluded_count": excluded_count,
                "new_findings": new_findings,
            },
        )

        return scan_job

    except Exception as e:
        logger.error("Scan job %s failed catastrophically (%s).", scan_job.id, type(e).__name__)
        scan_repo.complete(
            scan_job_id=scan_job.id,
            status="failed",
            total_candidates=total_candidates,
            new_findings=new_findings,
            excluded_assets=excluded_count,
            error_message=f"Scan failed ({type(e).__name__}).",
        )
        raise
