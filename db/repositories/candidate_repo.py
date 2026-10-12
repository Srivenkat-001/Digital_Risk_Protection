"""
Repository for discovered candidates and observations.
Handles deduplication and observation tracking.
"""

import json
from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from db.models.candidate import CandidateAppListing, CandidateObservation, CandidateProfile


class CandidateRepository:
    """Handles Candidate Profiles and Apps persistence and deduplication."""

    def __init__(self, db: Session):
        self.db = db

    def upsert_social_candidate(
        self,
        organization_id: str,
        brand_id: str,
        platform: str,
        profile_url: str,
        username: str,
        display_name: str,
        bio: str | None = None,
        platform_account_id: str | None = None,
        avatar_url: str | None = None,
        avatar_hash: str | None = None,
        follower_count: int = 0,
        raw_metadata: dict | None = None,
        is_synthetic: bool = False,
    ) -> tuple[CandidateProfile, bool]:
        """Upserts a candidate profile based on brand_id, platform, and username/profile_url."""
        norm_url = profile_url.strip().lower().rstrip("/")
        norm_user = username.strip().lower().lstrip("@")
        if not norm_user and not norm_url:
            raise ValueError("Social candidates require a username or profile URL.")

        identity_match = []
        if norm_user:
            identity_match.append(func.lower(CandidateProfile.username) == norm_user)
        if norm_url:
            identity_match.append(func.lower(CandidateProfile.profile_url) == norm_url)
        stmt = select(CandidateProfile).where(
            CandidateProfile.brand_id == brand_id,
            CandidateProfile.platform == platform,
            or_(*identity_match),
        )
        existing = self.db.scalars(stmt).first()

        metadata_str = json.dumps(raw_metadata) if raw_metadata else None
        now = datetime.now(timezone.utc)

        if existing:
            # Update observation timestamp and potentially changed dynamic data
            existing.last_observed_at = now
            existing.is_synthetic = is_synthetic
            existing.profile_url = profile_url.strip()
            existing.display_name = display_name
            existing.bio = bio or existing.bio
            if avatar_url:
                existing.avatar_url = avatar_url
            if avatar_hash:
                existing.avatar_hash = avatar_hash
            if follower_count:
                existing.follower_count = follower_count
            if metadata_str:
                existing.raw_metadata = metadata_str
            self.db.flush()
            return existing, False
        else:
            candidate = CandidateProfile(
                organization_id=organization_id,
                brand_id=brand_id,
                platform=platform,
                profile_url=profile_url.strip(),
                platform_account_id=platform_account_id,
                username=norm_user,
                display_name=display_name.strip(),
                bio=bio,
                avatar_url=avatar_url,
                avatar_hash=avatar_hash,
                follower_count=follower_count,
                raw_metadata=metadata_str,
                is_synthetic=is_synthetic,
                first_observed_at=now,
                last_observed_at=now,
            )
            self.db.add(candidate)
            self.db.flush()
            return candidate, True

    def upsert_app_candidate(
        self,
        organization_id: str,
        brand_id: str,
        store: str,
        app_name: str,
        package_id: str,
        publisher_name: str,
        store_url: str,
        description: str | None = None,
        icon_url: str | None = None,
        icon_hash: str | None = None,
        version: str | None = None,
        rating: float | None = None,
        raw_metadata: dict | None = None,
        is_synthetic: bool = False,
    ) -> tuple[CandidateAppListing, bool]:
        """Upserts a candidate mobile app based on brand_id, store, and package_id."""
        norm_pkg = package_id.strip().lower()
        if not norm_pkg:
            raise ValueError("App candidates require a package identifier.")

        stmt = select(CandidateAppListing).where(
            CandidateAppListing.brand_id == brand_id,
            CandidateAppListing.store == store,
            func.lower(CandidateAppListing.package_id) == norm_pkg,
        )
        existing = self.db.scalars(stmt).first()

        metadata_str = json.dumps(raw_metadata) if raw_metadata else None
        now = datetime.now(timezone.utc)

        if existing:
            existing.last_observed_at = now
            existing.is_synthetic = is_synthetic
            existing.app_name = app_name
            existing.publisher_name = publisher_name
            existing.description = description or existing.description
            if icon_url:
                existing.icon_url = icon_url
            if icon_hash:
                existing.icon_hash = icon_hash
            if version:
                existing.version = version
            if rating is not None:
                existing.rating = rating
            if metadata_str:
                existing.raw_metadata = metadata_str
            self.db.flush()
            return existing, False
        else:
            candidate = CandidateAppListing(
                organization_id=organization_id,
                brand_id=brand_id,
                store=store,
                app_name=app_name.strip(),
                package_id=norm_pkg,
                publisher_name=publisher_name.strip(),
                store_url=store_url.strip(),
                description=description,
                icon_url=icon_url,
                icon_hash=icon_hash,
                version=version,
                rating=rating,
                raw_metadata=metadata_str,
                is_synthetic=is_synthetic,
                first_observed_at=now,
                last_observed_at=now,
            )
            self.db.add(candidate)
            self.db.flush()
            return candidate, True

    def mark_social_excluded(self, candidate_id: str, reason: str) -> None:
        candidate = self.db.get(CandidateProfile, candidate_id)
        if candidate:
            candidate.is_excluded = True
            candidate.exclusion_reason = reason
            self.db.flush()

    def mark_app_excluded(self, candidate_id: str, reason: str) -> None:
        candidate = self.db.get(CandidateAppListing, candidate_id)
        if candidate:
            candidate.is_excluded = True
            candidate.exclusion_reason = reason
            self.db.flush()

    def record_observation(self, scan_job_id: str, candidate_type: str, candidate_id: str) -> CandidateObservation:
        obs = CandidateObservation(
            scan_job_id=scan_job_id,
            candidate_type=candidate_type,
            candidate_id=candidate_id,
        )
        self.db.add(obs)
        self.db.flush()
        return obs

    def get_social_by_id(self, candidate_id: str) -> CandidateProfile | None:
        return self.db.get(CandidateProfile, candidate_id)

    def get_app_by_id(self, candidate_id: str) -> CandidateAppListing | None:
        return self.db.get(CandidateAppListing, candidate_id)

    def list_social_by_brand(self, brand_id: str, include_excluded: bool = True) -> list[CandidateProfile]:
        stmt = select(CandidateProfile).where(CandidateProfile.brand_id == brand_id)
        if not include_excluded:
            stmt = stmt.where(CandidateProfile.is_excluded == False)
        return list(self.db.scalars(stmt).all())

    def list_apps_by_brand(self, brand_id: str, include_excluded: bool = True) -> list[CandidateAppListing]:
        stmt = select(CandidateAppListing).where(CandidateAppListing.brand_id == brand_id)
        if not include_excluded:
            stmt = stmt.where(CandidateAppListing.is_excluded == False)
        return list(self.db.scalars(stmt).all())
