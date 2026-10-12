"""Bounded JSON requests for public monitoring APIs."""

import json
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

import requests

MAX_RESPONSE_BYTES = 2 * 1024 * 1024
MAX_RETRIES = 2


class SourceRequestError(RuntimeError):
    """Raised when a public source cannot return a safe, valid JSON response."""


def get_json(url: str, params: dict[str, Any]) -> dict[str, Any]:
    """Fetch a small JSON response with timeouts and bounded retry/backoff."""
    for attempt in range(MAX_RETRIES + 1):
        try:
            with requests.get(
                url,
                params=params,
                timeout=(3.05, 10),
                stream=True,
                allow_redirects=False,
                headers={"Accept": "application/json", "User-Agent": "BrandPhantom-Demo/1.0"},
            ) as response:
                if 300 <= response.status_code < 400:
                    raise SourceRequestError("Public source returned a redirect; redirects are not followed.")
                if response.status_code == 429 or response.status_code >= 500:
                    if attempt < MAX_RETRIES:
                        time.sleep(_retry_delay(response.headers.get("Retry-After"), attempt))
                        continue
                if response.status_code >= 400:
                    raise SourceRequestError(f"Public source returned HTTP {response.status_code}.")
                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > MAX_RESPONSE_BYTES:
                    raise SourceRequestError("Public source response exceeded the 2 MiB size limit.")
                body = bytearray()
                for chunk in response.iter_content(chunk_size=64 * 1024):
                    body.extend(chunk)
                    if len(body) > MAX_RESPONSE_BYTES:
                        raise SourceRequestError("Public source response exceeded the 2 MiB size limit.")
                try:
                    payload = json.loads(body)
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise SourceRequestError("Public source returned invalid JSON.") from exc
                if not isinstance(payload, dict):
                    raise SourceRequestError("Public source returned an unexpected JSON shape.")
                return payload
        except (requests.Timeout, requests.ConnectionError) as exc:
            if attempt == MAX_RETRIES:
                raise SourceRequestError(f"Public source request failed ({type(exc).__name__}).") from exc
            time.sleep(0.5 * (2**attempt))
    raise SourceRequestError("Public source request failed after retries.")


def _retry_delay(retry_after: str | None, attempt: int) -> float:
    if retry_after:
        try:
            return min(max(float(retry_after), 0), 2)
        except ValueError:
            try:
                retry_at = parsedate_to_datetime(retry_after)
                return min(max((retry_at - datetime.now(timezone.utc)).total_seconds(), 0), 2)
            except (TypeError, ValueError, OverflowError):
                pass
    return 0.5 * (2**attempt)


def collected_at() -> str:
    return datetime.now(timezone.utc).isoformat()
