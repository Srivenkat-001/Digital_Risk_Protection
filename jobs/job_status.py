"""
Scan job status tracking and inspection helpers.
"""

from datetime import datetime, timezone
from typing import Any

from db.models.scan import ScanJob


def format_job_status(job: ScanJob) -> dict[str, Any]:
    """Formats scan job attributes for UI rendering."""
    duration = None
    if job.started_at:
        end_time = job.completed_at or datetime.now(timezone.utc)
        start = job.started_at
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)
        duration = round((end_time - start).total_seconds(), 1)

    return {
        "id": job.id,
        "brand_name": job.brand.name if job.brand else "Unknown",
        "status": job.status,
        "sources": job.source_types,
        "candidates": job.total_candidates_found,
        "excluded": job.excluded_assets_count,
        "findings": job.new_findings_count,
        "duration_seconds": duration,
        "error": job.error_message,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
    }
