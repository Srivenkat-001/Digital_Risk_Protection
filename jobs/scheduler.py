"""
Scan scheduling interface and runner dispatch.
Documented limitation: Streamlit Community Cloud puts idle instances to sleep;
production automated recurring scans should be dispatched via external cron (e.g. GitHub Actions, AWS EventBridge).
"""


from sqlalchemy.orm import Session

from config.logging_config import logger
from jobs.scan_runner import run_brand_scan


class ScanScheduler:
    """Dispatches scheduled or automated monitoring scans."""

    @staticmethod
    def trigger_scan(
        db: Session,
        brand_id: str,
        organization_id: str,
        triggered_by_user_id: str | None = None,
        source_types: list[str] | None = None,
    ):
        """Immediately executes a scan synchronously within the transaction context."""
        logger.info(f"Triggering scan for brand {brand_id} in organization {organization_id}")
        return run_brand_scan(
            db=db,
            brand_id=brand_id,
            organization_id=organization_id,
            triggered_by_user_id=triggered_by_user_id,
            source_types=source_types,
        )
