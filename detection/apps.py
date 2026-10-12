"""
Mobile application detection signal extractor.
Evaluates app store candidates against brand profiles and generates signals and evidence.
"""

from typing import Any

from rapidfuzz import fuzz

from db.models.brand import Brand
from db.models.candidate import CandidateAppListing
from detection.logo_similarity import compute_logo_similarity
from detection.name_similarity import compute_name_similarity
from detection.text_similarity import compute_text_similarity, detect_scam_intent
from schemas.evidence import EvidenceItemSchema


def extract_app_signals(
    candidate: CandidateAppListing,
    brand: Brand,
) -> tuple[dict[str, dict[str, Any]], list[EvidenceItemSchema]]:
    """
    Extracts structured detection signals and evidence items for a mobile application candidate.
    """
    signals = {}
    evidence_items = []

    aliases = [a.alias for a in brand.aliases] if brand.aliases else []
    official_publishers = [app.publisher_name for app in brand.official_app_listings if app.is_verified]
    official_packages = [app.package_id for app in brand.official_app_listings if app.is_verified]
    logo_hashes = [logo.perceptual_hash for logo in brand.logos if logo.perceptual_hash]

    # 1. App Name Similarity
    name_score, name_details = compute_name_similarity(
        candidate.app_name,
        brand.name,
        aliases
    )
    signals["name_similarity"] = {
        "value": name_score,
        "weight": 0.25,
        "available": True,
        "rationale": f"Candidate app title '{candidate.app_name}' has {int(name_score*100)}% match with '{name_details.get('matched_target', brand.name)}'.",
    }
    evidence_items.append(EvidenceItemSchema(
        evidence_type="app_title_comparison",
        title="Application Name Comparison",
        description=signals["name_similarity"]["rationale"],
        official_value=brand.name,
        candidate_value=candidate.app_name,
        confidence=0.9,
    ))

    # 2. Package / Bundle Identifier Analysis
    pkg_norm = candidate.package_id.lower()
    b_norm = brand.name.lower().replace(" ", "")
    brand_in_pkg = b_norm in pkg_norm.replace(".", "")

    pkg_score = 0.0
    if brand_in_pkg:
        pkg_score = 0.85
        rationale = f"Package identifier '{candidate.package_id}' embeds brand name '{brand.name}' without official asset authorization."
    else:
        # Check partial similarity
        pr = fuzz.partial_ratio(b_norm, pkg_norm) / 100.0
        pkg_score = pr * 0.7
        rationale = f"Package identifier '{candidate.package_id}' partial match: {int(pkg_score*100)}%."

    signals["package_similarity"] = {
        "value": round(pkg_score, 3),
        "weight": 0.20,
        "available": True,
        "rationale": rationale,
    }
    evidence_items.append(EvidenceItemSchema(
        evidence_type="package_identifier_analysis",
        title="Package / Bundle ID Analysis",
        description=rationale,
        official_value=", ".join(official_packages) if official_packages else "Authorized domain package convention",
        candidate_value=candidate.package_id,
        confidence=0.9,
    ))

    # 3. Publisher / Developer Mismatch
    # If app name matches brand but publisher does NOT match official publisher
    is_mismatch = False
    mismatch_score = 0.0
    pub_norm = candidate.publisher_name.strip().lower()

    if official_publishers:
        matches_any_official = any(pub_norm == off_pub.strip().lower() for off_pub in official_publishers)
        if not matches_any_official and name_score >= 0.5:
            is_mismatch = True
            mismatch_score = 1.0
            pub_rationale = (
                f"PUBLISHER MISMATCH: Published by '{candidate.publisher_name}', which is NOT an authorized "
                f"brand developer entity (Official: {', '.join(official_publishers)})."
            )
        else:
            pub_rationale = f"Publisher '{candidate.publisher_name}' matches or aligns with legitimate publisher criteria."
    else:
        # No official publisher configured - handle missing data explicitly
        pub_rationale = f"No official developer profile registered to verify against candidate publisher '{candidate.publisher_name}'."
        signals["publisher_mismatch"] = {
            "value": 0.0,
            "weight": 0.25,
            "available": False,
            "rationale": pub_rationale,
        }

    if official_publishers:
        signals["publisher_mismatch"] = {
            "value": mismatch_score,
            "weight": 0.25,
            "available": True,
            "rationale": pub_rationale,
        }
        if is_mismatch:
            evidence_items.append(EvidenceItemSchema(
                evidence_type="publisher_mismatch",
                title="Unauthorized Developer / Publisher",
                description=pub_rationale,
                official_value=", ".join(official_publishers),
                candidate_value=candidate.publisher_name,
                confidence=0.95,
            ))

    # 4. Icon Perceptual Hash Similarity
    if candidate.icon_hash and logo_hashes:
        icon_sim, matched_logo = compute_logo_similarity(candidate.icon_hash, logo_hashes)
        if icon_sim is not None:
            signals["icon_similarity"] = {
                "value": icon_sim,
                "weight": 0.20,
                "available": True,
                "rationale": f"Candidate app icon has {int(icon_sim*100)}% perceptual hash match with official brand logo.",
            }
            if icon_sim >= 0.70:
                evidence_items.append(EvidenceItemSchema(
                    evidence_type="icon_hash_match",
                    title="Visual App Icon Brand Imitation",
                    description=signals["icon_similarity"]["rationale"],
                    official_value=f"Official Logo Hash: {matched_logo[:12]}...",
                    candidate_value=f"Candidate Icon Hash: {candidate.icon_hash[:12]}...",
                    confidence=icon_sim,
                    file_path_or_url=candidate.icon_url,
                ))
    else:
        signals["icon_similarity"] = {
            "value": 0.0,
            "weight": 0.20,
            "available": False,
            "rationale": "Icon perceptual comparison unavailable (candidate icon or official logo hash missing).",
        }

    # 5. Description Analysis & Scam Keywords
    if candidate.description:
        desc_sim = compute_text_similarity(candidate.description, brand.description or "")
        scam_score, scam_keywords = detect_scam_intent(candidate.description)

        signals["description_similarity"] = {
            "value": desc_sim,
            "weight": 0.10,
            "available": True,
            "rationale": f"Candidate listing description shares {int(desc_sim*100)}% lexical overlap with official company profile.",
        }

        if scam_score > 0.0:
            kw_str = ", ".join(scam_keywords)
            signals["scam_intent"] = {
                "value": scam_score,
                "weight": 0.20,
                "available": True,
                "rationale": f"Suspicious predatory or deceptive patterns detected in app description: [{kw_str}].",
            }
            evidence_items.append(EvidenceItemSchema(
                evidence_type="scam_intent_keywords",
                title="Deceptive App Store Claims",
                description=signals["scam_intent"]["rationale"],
                official_value="Official product listing standards",
                candidate_value=candidate.description[:200] + ("..." if len(candidate.description) > 200 else ""),
                confidence=0.85,
            ))
        else:
            signals["scam_intent"] = {
                "value": 0.0,
                "weight": 0.20,
                "available": True,
                "rationale": "No predatory or high-risk keywords detected in app description.",
            }
    else:
        signals["description_similarity"] = {
            "value": 0.0,
            "weight": 0.10,
            "available": False,
            "rationale": "Description analysis unavailable (no listing description text).",
        }
        signals["scam_intent"] = {
            "value": 0.0,
            "weight": 0.20,
            "available": False,
            "rationale": "Scam pattern analysis unavailable (no description).",
        }

    return signals, evidence_items
