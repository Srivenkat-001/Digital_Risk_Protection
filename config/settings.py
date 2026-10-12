"""
Application configuration for BrandPhantom.
Loads settings from environment variables and provides typed constants.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Base directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file if it exists
load_dotenv(BASE_DIR / ".env")

class Settings:
    """Application settings class."""
    
    APP_NAME: str = os.getenv("APP_NAME", "BrandPhantom")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_SECRET_KEY: str = os.getenv("APP_SECRET_KEY", "development-only-key-not-for-production")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Database connection string
    # Supports PostgreSQL (Supabase) or SQLite fallback
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./brandphantom.db")
    
    # Normalize postgres:// to postgresql:// for SQLAlchemy compatibility
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        
    SESSION_EXPIRY_HOURS: int = int(os.getenv("SESSION_EXPIRY_HOURS", "24"))
    DEMO_MODE_ENABLED: bool = os.getenv("DEMO_MODE_ENABLED", "true").lower() in ("true", "1", "yes")

    if APP_ENV.lower() == "production":
        if (
            len(APP_SECRET_KEY) < 32
            or APP_SECRET_KEY == "development-only-key-not-for-production"
            or APP_SECRET_KEY.startswith("replace-with-")
        ):
            raise ValueError("Production requires APP_SECRET_KEY to be set to a unique value of at least 32 characters.")
        if DEMO_MODE_ENABLED:
            raise ValueError("DEMO_MODE_ENABLED must be false when APP_ENV=production.")

    # Roles
    ROLE_ADMIN: str = "admin"
    ROLE_ANALYST: str = "analyst"
    ROLE_VIEWER: str = "viewer"
    ALL_ROLES: list[str] = [ROLE_ADMIN, ROLE_ANALYST, ROLE_VIEWER]

    # Finding Review Statuses
    STATUS_NEW: str = "New"
    STATUS_NEEDS_REVIEW: str = "Needs Review"
    STATUS_INVESTIGATING: str = "Investigating"
    STATUS_CONFIRMED_THREAT: str = "Confirmed Threat"
    STATUS_FALSE_POSITIVE: str = "False Positive"
    STATUS_RESOLVED: str = "Resolved"
    STATUS_DISMISSED: str = "Dismissed"
    ALL_STATUSES: list[str] = [
        STATUS_NEW,
        STATUS_NEEDS_REVIEW,
        STATUS_INVESTIGATING,
        STATUS_CONFIRMED_THREAT,
        STATUS_FALSE_POSITIVE,
        STATUS_RESOLVED,
        STATUS_DISMISSED,
    ]

    # Severity Levels
    SEVERITY_LOW: str = "Low"
    SEVERITY_MEDIUM: str = "Medium"
    SEVERITY_HIGH: str = "High"
    SEVERITY_CRITICAL: str = "Critical"
    ALL_SEVERITIES: list[str] = [
        SEVERITY_LOW,
        SEVERITY_MEDIUM,
        SEVERITY_HIGH,
        SEVERITY_CRITICAL,
    ]

    # Scan Job Statuses
    SCAN_PENDING: str = "pending"
    SCAN_RUNNING: str = "running"
    SCAN_COMPLETED: str = "completed"
    SCAN_PARTIAL: str = "partial"
    SCAN_FAILED: str = "failed"

    # Risk Scoring Thresholds
    RISK_THRESHOLD_LOW: float = 30.0
    RISK_THRESHOLD_MEDIUM: float = 60.0
    RISK_THRESHOLD_HIGH: float = 80.0

    # Source Types
    SOURCE_SOCIAL: str = "social"
    SOURCE_APP: str = "app"

    # Platforms
    PLATFORM_TWITTER: str = "Twitter/X"
    PLATFORM_INSTAGRAM: str = "Instagram"
    PLATFORM_FACEBOOK: str = "Facebook"
    PLATFORM_LINKEDIN: str = "LinkedIn"
    PLATFORM_TELEGRAM: str = "Telegram"
    PLATFORM_TIKTOK: str = "TikTok"

    STORE_GOOGLE_PLAY: str = "Google Play"
    STORE_APPLE_APP_STORE: str = "Apple App Store"

settings = Settings()
