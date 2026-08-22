"""Staff-only diagnostics for Render environment configuration."""

import logging
import os

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET


logger = logging.getLogger(__name__)


ENVIRONMENT_GROUPS = (
    (
        "Django",
        (
            ("DJANGO_SETTINGS_MODULE", True),
            ("SECRET_KEY", True),
            ("DEBUG", False),
            ("ALLOWED_HOSTS", True),
            ("SITE_URL", False),
        ),
    ),
    (
        "Database",
        (
            ("DATABASE_URL", True),
            ("DB_CONN_MAX_AGE", False),
            ("DB_CONN_HEALTH_CHECKS", False),
        ),
    ),
    (
        "Email",
        (
            ("EMAIL_BACKEND", True),
            ("RESEND_API_KEY", True),
            ("DEFAULT_FROM_EMAIL", True),
            ("ADMIN_EMAIL", True),
            ("JOBS_EMAIL", False),
            ("NEWSLETTER_EMAIL", False),
            ("EMAIL_MARKETING_BATCH_LIMIT", False),
            ("EMAIL_RATE_LIMIT_PER_MINUTE", False),
            ("EMAIL_RATE_LIMIT_PER_HOUR", False),
        ),
    ),
    (
        "Storage and monitoring",
        (
            ("UPLOADCARE_PUBLIC_KEY", False),
            ("UPLOADCARE_SECRET_KEY", False),
            ("SENTRY_DSN", False),
            ("GOOGLE_ANALYTICS_ID", False),
            ("GOOGLE_TAG_MANAGER_ID", False),
        ),
    ),
    (
        "Render runtime",
        (
            ("RENDER", False),
            ("RENDER_EXTERNAL_HOSTNAME", False),
            ("RENDER_GIT_BRANCH", False),
            ("RENDER_GIT_COMMIT", False),
            ("WEB_CONCURRENCY", False),
            ("GUNICORN_TIMEOUT", False),
            ("PYTHON_VERSION", False),
        ),
    ),
    (
        "Security",
        (
            ("SECURE_SSL_REDIRECT", False),
            ("SECURE_HSTS_SECONDS", False),
            ("SECURE_HSTS_INCLUDE_SUBDOMAINS", False),
            ("SECURE_HSTS_PRELOAD", False),
            ("SESSION_COOKIE_SECURE", False),
            ("CSRF_COOKIE_SECURE", False),
        ),
    ),
)


def _environment_status():
    groups = []
    present = []
    missing_required = []
    absent_optional = []

    for group_name, variables in ENVIRONMENT_GROUPS:
        rows = []
        for variable_name, required in variables:
            configured = bool(os.environ.get(variable_name, "").strip())
            if configured:
                status = "Present"
                status_class = "present"
                present.append(variable_name)
            elif required:
                status = "Missing"
                status_class = "missing"
                missing_required.append(variable_name)
            else:
                status = "Not set (optional/default)"
                status_class = "optional"
                absent_optional.append(variable_name)

            rows.append(
                {
                    "name": variable_name,
                    "required": required,
                    "status": status,
                    "status_class": status_class,
                }
            )
        groups.append({"name": group_name, "variables": rows})

    return groups, present, missing_required, absent_optional


@never_cache
@require_GET
@staff_member_required(login_url="admin:login")
def environment_diagnostics(request):
    """Show an allowlisted presence check without revealing environment values."""
    groups, present, missing_required, absent_optional = _environment_status()

    logger.info(
        "Environment diagnostics user_id=%s present=%s missing_required=%s "
        "not_set_optional=%s",
        request.user.pk,
        sorted(present),
        sorted(missing_required),
        sorted(absent_optional),
    )

    response = render(
        request,
        "admin/environment_diagnostics.html",
        {
            "title": "Environment diagnostics",
            "groups": groups,
            "present_count": len(present),
            "missing_required": missing_required,
            "missing_required_count": len(missing_required),
            "optional_count": len(absent_optional),
            "runtime": {
                "settings_module": os.environ.get(
                    "DJANGO_SETTINGS_MODULE", "Not set"
                ),
                "debug": settings.DEBUG,
                "email_backend": getattr(settings, "EMAIL_BACKEND", "Not set"),
                "database_engine": settings.DATABASES["default"]["ENGINE"],
            },
        },
    )
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response
