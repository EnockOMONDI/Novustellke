"""Small helpers for recording non-secret transactional email failures."""

import json
import logging
import os
from datetime import datetime, timezone


logger = logging.getLogger(__name__)

LAST_EMAIL_FAILURE_PATH = "/tmp/novustell_last_email_failure.json"


def _response_detail(response):
    if response is None:
        return ""

    try:
        payload = response.json()
    except (TypeError, ValueError):
        payload = getattr(response, "text", "")

    if isinstance(payload, dict):
        detail = payload.get("message") or payload.get("error") or payload
    else:
        detail = payload

    return str(detail)[:1000]


def build_email_error_details(exc):
    """Return a safe, non-secret summary of an email backend exception."""
    response = getattr(exc, "response", None)
    status_code = getattr(exc, "status_code", None) or getattr(
        response, "status_code", None
    )
    esp_name = getattr(exc, "esp_name", "") or "email_provider"
    detail = _response_detail(response) or str(exc)[:1000]

    code_parts = [esp_name.lower().replace(" ", "_")]
    if status_code:
        code_parts.append(str(status_code))
    code_parts.append(exc.__class__.__name__)

    return {
        "code": "-".join(code_parts),
        "provider": esp_name,
        "exception": exc.__class__.__name__,
        "status_code": status_code or "unknown",
        "detail": detail,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }


def record_last_email_failure(details):
    """Persist the latest non-secret email failure for staff diagnostics."""
    try:
        with open(LAST_EMAIL_FAILURE_PATH, "w", encoding="utf-8") as handle:
            json.dump(details, handle)
    except OSError as exc:
        logger.warning("Could not write email diagnostics file: %s", exc)


def get_last_email_failure():
    """Load the latest non-secret email failure, if this instance has one."""
    if not os.path.exists(LAST_EMAIL_FAILURE_PATH):
        return None

    try:
        with open(LAST_EMAIL_FAILURE_PATH, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read email diagnostics file: %s", exc)
        return {
            "code": "email-diagnostics-unavailable",
            "provider": "unknown",
            "exception": exc.__class__.__name__,
            "status_code": "unknown",
            "detail": "Could not read the last email diagnostic record.",
            "recorded_at": "unknown",
        }
