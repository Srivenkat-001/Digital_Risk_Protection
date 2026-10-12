"""
Risk severity and review status badge rendering helpers.
"""

from html import escape


def render_risk_badge(severity: str, score: float | None = None) -> str:
    """Returns styled HTML string for risk badge."""
    sev_clean = (severity or "Low").capitalize()
    cls = escape(f"bp-badge bp-badge-{sev_clean.lower()}", quote=True)
    score_str = f" ({score:.1f})" if score is not None else ""
    return f'<span class="{cls}">{escape(sev_clean)}{score_str}</span>'

def render_status_badge(status: str) -> str:
    """Returns styled HTML string for review status badge."""
    stat_clean = status or "New"
    badge_style = "bp-status-new"
    if stat_clean == "Confirmed Threat":
        badge_style = "bp-status-threat"
    elif stat_clean == "False Positive":
        badge_style = "bp-status-false-pos"
    elif stat_clean == "Investigating":
        badge_style = "bp-status-investigating"
    elif stat_clean in ("Resolved", "Dismissed"):
        badge_style = "bp-status-false-pos"

    return f'<span class="bp-badge {badge_style}">{escape(stat_clean)}</span>'
