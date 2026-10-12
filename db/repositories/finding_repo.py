"""
Repository for Finding, DetectionSignal, RiskAssessment, and Evidence management.
"""

from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, selectinload

from db.models.finding import DetectionSignal, Evidence, Finding, RiskAssessment
from schemas.evidence import EvidenceItemSchema


class FindingRepository:
    """Handles Finding persistence, filtering, and metric aggregations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, finding_id: str, organization_id: str | None = None) -> Finding | None:
        stmt = (
            select(Finding)
            .where(Finding.id == finding_id)
            .options(
                selectinload(Finding.signals),
                selectinload(Finding.assessment),
                selectinload(Finding.evidence_items),
                selectinload(Finding.brand),
                selectinload(Finding.assigned_to),
                selectinload(Finding.investigations),
            )
        )
        if organization_id:
            stmt = stmt.where(Finding.organization_id == organization_id)
        return self.db.scalars(stmt).first()

    def get_by_candidate(self, candidate_type: str, candidate_id: str) -> Finding | None:
        stmt = (
            select(Finding)
            .where(Finding.candidate_type == candidate_type, Finding.candidate_id == candidate_id)
            .options(
                selectinload(Finding.signals),
                selectinload(Finding.assessment),
                selectinload(Finding.evidence_items),
            )
        )
        return self.db.scalars(stmt).first()

    def create(
        self,
        organization_id: str,
        brand_id: str,
        candidate_type: str,
        candidate_id: str,
        risk_score: float,
        severity: str,
        scan_job_id: str | None = None,
        is_synthetic: bool = False,
        review_status: str = "New",
    ) -> Finding:
        finding = Finding(
            organization_id=organization_id,
            brand_id=brand_id,
            scan_job_id=scan_job_id,
            candidate_type=candidate_type,
            candidate_id=candidate_id,
            risk_score=risk_score,
            severity=severity,
            review_status=review_status,
            is_synthetic=is_synthetic,
        )
        self.db.add(finding)
        self.db.flush()
        return finding

    def add_signal(
        self,
        finding_id: str,
        signal_name: str,
        signal_value: float,
        signal_weight: float,
        contribution: float,
        rationale: str,
    ) -> DetectionSignal:
        sig = DetectionSignal(
            finding_id=finding_id,
            signal_name=signal_name,
            signal_value=signal_value,
            signal_weight=signal_weight,
            contribution=contribution,
            rationale=rationale,
        )
        self.db.add(sig)
        self.db.flush()
        return sig

    def set_assessment(
        self,
        finding_id: str,
        score: float,
        severity: str,
        explanation: str,
        model_version: str = "v1.2.0",
    ) -> RiskAssessment:
        assessment = RiskAssessment(
            finding_id=finding_id,
            score=score,
            severity=severity,
            explanation=explanation,
            model_version=model_version,
        )
        self.db.add(assessment)
        self.db.flush()
        return assessment

    def add_evidence(
        self,
        finding_id: str,
        evidence_type: str,
        title: str,
        description: str,
        official_value: str | None = None,
        candidate_value: str | None = None,
        confidence: float = 1.0,
        file_path_or_url: str | None = None,
    ) -> Evidence:
        ev = Evidence(
            finding_id=finding_id,
            evidence_type=evidence_type,
            title=title,
            description=description,
            official_value=official_value,
            candidate_value=candidate_value,
            confidence=confidence,
            file_path_or_url=file_path_or_url,
        )
        self.db.add(ev)
        self.db.flush()
        return ev

    def refresh_existing_finding(
        self,
        finding: Finding,
        scan_job_id: str,
        is_synthetic: bool,
        score: float,
        severity: str,
        enriched_signals: dict[str, dict[str, Any]],
        explanation: str,
        evidence_items: list[EvidenceItemSchema],
    ) -> None:
        """Replace stale detection details while preserving analyst disposition."""
        finding.risk_score = score
        finding.severity = severity
        finding.scan_job_id = scan_job_id
        finding.is_synthetic = is_synthetic

        for signal in list(finding.signals):
            self.db.delete(signal)
        if finding.assessment:
            self.db.delete(finding.assessment)
        for evidence in list(finding.evidence_items):
            self.db.delete(evidence)
        self.db.flush()

        for signal_name, signal_data in enriched_signals.items():
            self.add_signal(
                finding_id=finding.id,
                signal_name=signal_name,
                signal_value=signal_data["value"],
                signal_weight=signal_data["weight"],
                contribution=signal_data["contribution"],
                rationale=signal_data["rationale"],
            )
        self.set_assessment(
            finding_id=finding.id,
            score=score,
            severity=severity,
            explanation=explanation,
        )
        for item in evidence_items:
            self.add_evidence(
                finding_id=finding.id,
                evidence_type=item.evidence_type,
                title=item.title,
                description=item.description,
                official_value=item.official_value,
                candidate_value=item.candidate_value,
                confidence=item.confidence,
                file_path_or_url=item.file_path_or_url,
            )
        self.db.expire(finding, ["signals", "assessment", "evidence_items"])

    def update_status(
        self,
        finding_id: str,
        review_status: str,
        assigned_to_user_id: str | None = None,
    ) -> Finding | None:
        finding = self.get_by_id(finding_id)
        if finding:
            finding.review_status = review_status
            if assigned_to_user_id is not None:
                finding.assigned_to_user_id = assigned_to_user_id
            self.db.flush()
        return finding

    def list_findings(
        self,
        organization_id: str,
        brand_id: str | None = None,
        severity: str | None = None,
        review_status: str | None = None,
        candidate_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Finding]:
        stmt = (
            select(Finding)
            .where(Finding.organization_id == organization_id)
            .options(
                selectinload(Finding.signals),
                selectinload(Finding.assessment),
                selectinload(Finding.evidence_items),
                selectinload(Finding.brand),
                selectinload(Finding.assigned_to),
            )
            .order_by(Finding.risk_score.desc(), Finding.created_at.desc())
        )
        if brand_id:
            stmt = stmt.where(Finding.brand_id == brand_id)
        if severity:
            stmt = stmt.where(Finding.severity == severity)
        if review_status:
            stmt = stmt.where(Finding.review_status == review_status)
        if candidate_type:
            stmt = stmt.where(Finding.candidate_type == candidate_type)

        stmt = stmt.limit(limit).offset(offset)
        return list(self.db.scalars(stmt).all())

    def get_metrics_summary(self, organization_id: str, brand_id: str | None = None) -> dict[str, Any]:
        """Calculates dashboard metrics from actual database records."""
        base_filter = [Finding.organization_id == organization_id]
        if brand_id:
            base_filter.append(Finding.brand_id == brand_id)

        # Count total findings
        total = self.db.scalar(select(func.count(Finding.id)).where(and_(*base_filter))) or 0

        # Counts by severity
        severity_counts = {}
        sev_rows = self.db.execute(
            select(Finding.severity, func.count(Finding.id))
            .where(and_(*base_filter))
            .group_by(Finding.severity)
        ).all()
        for sev, cnt in sev_rows:
            severity_counts[sev] = cnt

        # Counts by status
        status_counts = {}
        status_rows = self.db.execute(
            select(Finding.review_status, func.count(Finding.id))
            .where(and_(*base_filter))
            .group_by(Finding.review_status)
        ).all()
        for stat, cnt in status_rows:
            status_counts[stat] = cnt

        return {
            "total_findings": total,
            "severity_counts": severity_counts,
            "status_counts": status_counts,
            "new_count": status_counts.get("New", 0),
            "confirmed_threats": status_counts.get("Confirmed Threat", 0),
            "false_positives": status_counts.get("False Positive", 0),
            "investigating_count": status_counts.get("Investigating", 0),
        }
