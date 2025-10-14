"""Celery tasks for the organizations app."""

from __future__ import annotations

import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_pilot_welcome_email(self, user_id: int, raw_password: str) -> None:
    """Send a welcome email to a newly created pilot user."""

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("Pilot welcome email skipped - user %s no longer exists", user_id)
        return

    context = {
        "user": user,
        "raw_password": raw_password,
        "login_url": f"{getattr(settings, 'BASE_URL', '').rstrip('/')}/login/" or "https://staging.bmms.gov.ph/login/",
        "support_email": getattr(settings, "PILOT_SUPPORT_EMAIL", "support@bmms.local"),
    }

    subject = f"Welcome to BMMS Pilot - {user.get_full_name() or user.username}"
    text_body = render_to_string("emails/pilot_welcome.txt", context)
    html_body = render_to_string("emails/pilot_welcome.html", context)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    message.attach_alternative(html_body, "text/html")
    message.send()

    logger.info("Sent pilot welcome email to %s", user.email)
