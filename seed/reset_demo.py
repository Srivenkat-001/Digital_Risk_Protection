"""
Safe demo data reset mechanism.
Selectively purges synthetic candidates and findings and re-seeds the demo environment.
Never resets non-synthetic production data.
"""

from sqlalchemy import delete
from sqlalchemy.orm import Session

from config.logging_config import logger
from db.models.candidate import CandidateAppListing, CandidateProfile
from db.models.finding import DetectionSignal, Evidence, Finding, RiskAssessment
from db.models.investigation import Investigation, InvestigationNote
from seed.demo_data import seed_demo_environment


def reset_demo_data(db: Session, organization_id: str) -> bool:
    """
    Safely resets synthetic demo findings, cases, and candidates for the given organization.
    Ensures non-synthetic records are left intact.
    """
    logger.info(f"Initiating safe demo data reset for organization {organization_id}")

    # 1. Delete investigation notes attached to synthetic finding cases
    synthetic_findings = db.query(Finding.id).filter(
        Finding.organization_id == organization_id,
        Finding.is_synthetic == True
    ).all()
    syn_f_ids = [f[0] for f in synthetic_findings]

    if syn_f_ids:
        # Find cases attached to these findings
        cases = db.query(Investigation.id).filter(Investigation.finding_id.in_(syn_f_ids)).all()
        case_ids = [c[0] for c in cases]
        if case_ids:
            db.execute(delete(InvestigationNote).where(InvestigationNote.investigation_id.in_(case_ids)))
            db.execute(delete(Investigation).where(Investigation.id.in_(case_ids)))

        # Delete signals, assessments, evidence, and findings
        db.execute(delete(Evidence).where(Evidence.finding_id.in_(syn_f_ids)))
        db.execute(delete(DetectionSignal).where(DetectionSignal.finding_id.in_(syn_f_ids)))
        db.execute(delete(RiskAssessment).where(RiskAssessment.finding_id.in_(syn_f_ids)))
        db.execute(delete(Finding).where(Finding.id.in_(syn_f_ids)))

    # 2. Delete synthetic candidates
    db.execute(
        delete(CandidateProfile).where(
            CandidateProfile.organization_id == organization_id,
            CandidateProfile.is_synthetic == True
        )
    )
    db.execute(
        delete(CandidateAppListing).where(
            CandidateAppListing.organization_id == organization_id,
            CandidateAppListing.is_synthetic == True
        )
    )

    db.commit()
    logger.info("Purged existing synthetic findings and candidates.")

    # 3. Re-seed demo environment
    seed_demo_environment(db)
    logger.info("Successfully re-seeded demo environment.")
    return True
