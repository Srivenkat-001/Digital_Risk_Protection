"""
Normalization utilities for text, handles, URLs, and package identifiers.
"""

import re
from urllib.parse import urlsplit


def normalize_text(text: str) -> str:
    """Normalizes generic text by stripping whitespace, converting to lowercase, and collapsing spaces."""
    if not isinstance(text, str) or not text:
        return ""
    text = text.strip().lower()
    return re.sub(r"\s+", " ", text)

def normalize_handle(handle: str) -> str:
    """Normalizes social media handles by stripping '@', whitespace, and lowercasing."""
    if not isinstance(handle, str) or not handle:
        return ""
    handle = handle.strip().lower()
    handle = handle.lstrip("@")
    return re.sub(r"[^a-z0-9_.]", "", handle)

def normalize_url(url: str) -> str:
    """Normalizes URLs for canonical comparison."""
    if not isinstance(url, str) or not url.strip():
        return ""
    url = url.strip().lower()
    if "://" not in url:
        url = "https://" + url
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError:
        return ""
    if parsed.scheme not in ("http", "https") or not hostname or parsed.username or parsed.password:
        return ""
    try:
        hostname = hostname.encode("idna").decode("ascii").removeprefix("www.")
    except UnicodeError:
        return ""
    if ":" in hostname:
        hostname = f"[{hostname}]"
    netloc = f"{hostname}:{port}" if port is not None else hostname
    path = parsed.path.rstrip("/")
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{netloc}{path}{query}"


def normalize_package_id(package_id: str) -> str:
    """Normalizes mobile application bundle/package identifier (e.g. com.example.app)."""
    if not isinstance(package_id, str) or not package_id:
        return ""
    return package_id.strip().lower()

def extract_domain(url_or_domain: str) -> str:
    """Extracts base domain from a URL or domain string."""
    if not isinstance(url_or_domain, str) or not url_or_domain.strip():
        return ""
    normalized = normalize_url(url_or_domain)
    if not normalized:
        return ""
    try:
        return urlsplit(f"https://{normalized}").hostname or ""
    except ValueError:
        return ""
