"""
Social profile detection signal extractor.
Evaluates social media candidates against brand profiles and generates signals and evidence.
"""

from typing import Any

from db.models.brand import Brand
from db.models.candidate import CandidateProfile
from detection.logo_similarity import compute_logo_similarity
from detection.name_similarity import compute_handle_similarity, compute_name_similarity
from detection.text_similarity import compute_text_similarity, detect_scam_intent
from schemas.evidence import EvidenceItemSchema


def extract_social_signals(
    candidate: CandidateProfile,
    brand: Brand,
) -> tuple[dict[str, dict[str, Any]], list[EvidenceItemSchema]]:
    """
    Extracts structured detection signals and evidence items for a social media candidate.
    """
    signals = {}
    evidence_items = []

    aliases = [a.alias for a in brand.aliases] if brand.aliases else []
    official_handles = [acc.handle for acc in brand.official_social_accounts if acc.is_verified]
    logo_hashes = [logo.perceptual_hash for logo in brand.logos if logo.perceptual_hash]

    # 1. Display Name Similarity
    name_score, name_details = compute_name_similarity(
        candidate.display_name,
        brand.name,
        aliases
    )
    signals["name_similarity"] = {
        "value": name_score,
        "weight": 0.25,
        "available": True,
        "rationale": f"Candidate display name '{candidate.display_name}' has {int(name_score*100)}% match with '{name_details.get('matched_target', brand.name)}'.",
    }
    evidence_items.append(EvidenceItemSchema(
        evidence_type="name_comparison",
        title="Display Name Comparison",
        description=signals["name_similarity"]["rationale"],
        official_value=brand.name,
        candidate_value=candidate.display_name,
        confidence=0.9,
    ))

    # 2. Handle / Username Similarity
    primary_off_handle = official_handles[0] if official_handles else None
    handle_score, handle_details = compute_handle_similarity(
        candidate.username,
        brand.name,
        primary_off_handle,
        aliases
    )
    signals["username_similarity"] = {
        "value": handle_score,
        "weight": 0.25,
        "available": True,
        "rationale": f"Candidate handle '@{candidate.username}' similarity is {int(handle_score*100)}% to brand reference.",
    }
    evidence_items.append(EvidenceItemSchema(
        evidence_type="handle_comparison",
        title="Username Similarity Analysis",
        description=signals["username_similarity"]["rationale"],
        official_value=f"@{primary_off_handle}" if primary_off_handle else brand.name,
        candidate_value=f"@{candidate.username}",
        confidence=0.95,
    ))

    # 3. Leetspeak / Character Substitution
    if handle_details.get("has_leetspeak"):
        signals["leetspeak_detected"] = {
            "value": 1.0,
            "weight": 0.15,
            "available": True,
            "rationale": f"Deliberate character substitution detected in username '@{candidate.username}' (de-leeted: '{handle_details.get('de_leeted_handle')}').",
        }
        evidence_items.append(EvidenceItemSchema(
            evidence_type="leetspeak_substitution",
            title="Character Substitution (Homoglyph) Detected",
            description=signals["leetspeak_detected"]["rationale"],
            official_value=brand.name.lower(),
            candidate_value=candidate.username,
            confidence=0.95,
        ))
    else:
        signals["leetspeak_detected"] = {
            "value": 0.0,
            "weight": 0.15,
            "available": True,
            "rationale": "No character substitution or homoglyphs observed in handle.",
        }

    # 4. Suspicious Affixes (Fake Support / Official Claims)
    if handle_details.get("has_suspicious_affix"):
        affixes_str = ", ".join(handle_details.get("detected_affixes", []))
        signals["fake_support_affix"] = {
            "value": 1.0,
            "weight": 0.20,
            "available": True,
            "rationale": f"High-risk impersonation affix detected in handle: [{affixes_str}]. Commonly used in fake support scams.",
        }
        evidence_items.append(EvidenceItemSchema(
            evidence_type="suspicious_affix",
            title="Misleading Support/Service Affix",
            description=signals["fake_support_affix"]["rationale"],
            official_value="Official verified brand presence",
            candidate_value=f"@{candidate.username}",
            confidence=0.9,
        ))
    else:
        signals["fake_support_affix"] = {
            "value": 0.0,
            "weight": 0.20,
            "available": True,
            "rationale": "No misleading support affixes detected in username.",
        }

    # 5. Logo / Avatar Perceptual Hash Similarity
    if candidate.avatar_hash and logo_hashes:
        avatar_sim, matched_logo = compute_logo_similarity(candidate.avatar_hash, logo_hashes)
        if avatar_sim is not None:
            signals["logo_similarity"] = {
                "value": avatar_sim,
                "weight": 0.20,
                "available": True,
                "rationale": f"Candidate avatar has {int(avatar_sim*100)}% perceptual hash match with official brand logo.",
            }
            if avatar_sim >= 0.75:
                evidence_items.append(EvidenceItemSchema(
                    evidence_type="avatar_hash_match",
                    title="Visual Brand Logo Match",
                    description=signals["logo_similarity"]["rationale"],
                    official_value=f"Official Logo Hash: {matched_logo[:12]}...",
                    candidate_value=f"Candidate Avatar Hash: {candidate.avatar_hash[:12]}...",
                    confidence=avatar_sim,
                    file_path_or_url=candidate.avatar_url,
                ))
    else:
        # Missing data explicitly handled
        signals["logo_similarity"] = {
            "value": 0.0,
            "weight": 0.20,
            "available": False,
            "rationale": "Logo perceptual comparison unavailable (candidate avatar or official brand logo hash missing).",
        }

    # 6. Bio / Description Similarity & Scam Keywords
    if candidate.bio:
        bio_sim = compute_text_similarity(candidate.bio, brand.description or "")
        scam_score, scam_keywords = detect_scam_intent(candidate.bio)

        signals["bio_similarity"] = {
            "value": bio_sim,
            "weight": 0.10,
            "available": True,
            "rationale": f"Candidate bio shares {int(bio_sim*100)}% lexical overlap with official company description.",
        }

        if scam_score > 0.0:
            kw_str = ", ".join(scam_keywords)
            signals["scam_intent"] = {
                "value": scam_score,
                "weight": 0.25,
                "available": True,
                "rationale": f"High-risk social engineering or phishing triggers found in bio: [{kw_str}].",
            }
            evidence_items.append(EvidenceItemSchema(
                evidence_type="scam_intent_keywords",
                title="Phishing / Scam Social Engineering Triggers",
                description=signals["scam_intent"]["rationale"],
                official_value="Official customer advisory channels",
                candidate_value=candidate.bio[:200] + ("..." if len(candidate.bio) > 200 else ""),
                confidence=0.85,
            ))
        else:
            signals["scam_intent"] = {
                "value": 0.0,
                "weight": 0.25,
                "available": True,
                "rationale": "No known phishing or credential solicitation patterns found in bio.",
            }
    else:
        signals["bio_similarity"] = {
            "value": 0.0,
            "weight": 0.10,
            "available": False,
            "rationale": "Bio text similarity unavailable (no candidate bio provided).",
        }
        signals["scam_intent"] = {
            "value": 0.0,
            "weight": 0.25,
            "available": False,
            "rationale": "Scam pattern analysis unavailable (no bio content).",
        }

    return signals, evidence_items
