"""
Explanation generation module.
Produces transparent, human-readable rationales, highlights key risk drivers,
and outlines evidence gaps and analytical limitations.
"""

from typing import Any

from detection.scoring import ENGINE_VERSION


def generate_risk_explanation(
    score: float,
    severity: str,
    coverage: float,
    enriched_signals: dict[str, dict[str, Any]],
    candidate_type: str,
    brand_name: str,
) -> str:
    """
    Builds an explainable summary report describing why this candidate received
    the specified risk rating, which signals drove the score, and analytical limitations.
    """
    lines = [
        f"**Risk Assessment: {severity} ({score:.1f}/100)**",
        f"Evaluated against target brand **{brand_name}** using rule engine `{ENGINE_VERSION}`.",
        f"Signal coverage: **{int(coverage * 100)}%** of applicable indicators evaluated.",
        "",
        "### Key Risk Drivers:",
    ]

    # Find highest contributing active signals
    active_signals = [
        (name, data) for name, data in enriched_signals.items()
        if data.get("available") and data.get("value", 0.0) > 0.0
    ]
    # Sort by contribution descending
    active_signals.sort(key=lambda x: x[1].get("contribution", 0.0), reverse=True)

    if active_signals:
        for name, data in active_signals:
            val = data["value"]
            rationale = data["rationale"]
            lines.append(f"- **{name.replace('_', ' ').title()}** (Intensity: {int(val*100)}%): {rationale}")
    else:
        lines.append("- No positive adversarial signals or brand overlap detected.")

    # Missing evidence limitations
    missing = [
        (name, data) for name, data in enriched_signals.items()
        if not data.get("available")
    ]
    if missing:
        lines.append("")
        lines.append("### Evidence Gaps & Limitations:")
        for name, data in missing:
            lines.append(f"- *{name.replace('_', ' ').title()}*: {data.get('rationale')}")
        lines.append("*(Note: Missing data is not treated as evidence of maliciousness.)*")

    lines.append("")
    lines.append(
        "**Analyst Advisory**: This score represents automated heuristic risk indicator alignment, "
        "not confirmed fraud. Independent analyst review of evidence artifacts is required prior to enforcement."
    )

    return "\n".join(lines)
