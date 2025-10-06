"""Celery tasks for calendar notifications, reminders, and digests."""

from datetime import timedelta

from celery import shared_task, group
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import logging

from common.work_item_model import WorkItem
from common.models import (
    CalendarResourceBooking,
    StaffLeave,
    UserCalendarPreferences,
    CalendarNotification,
)

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def send_event_notification(event_id, participant_ids=None):
    """
    Send activity/event notification emails to assigned users.

    DEPRECATED: This function is maintained for backward compatibility.
    New code should use WorkItem-specific notification handlers.

    Args:
        event_id: UUID of the activity (WorkItem)
        participant_ids: List of user IDs (None = all assigned users)
    """
    try:
        # Get WorkItem (activity/event)
        activity = WorkItem.objects.get(pk=event_id, work_type='activity')

        # Get assigned users (participants)
        if participant_ids:
            assigned_users = activity.assigned_users.filter(id__in=participant_ids)
        else:
            assigned_users = activity.assigned_users.all()

        # Send email to each assigned user
        sent_count = 0
        for user in assigned_users:
            # Check user preferences
            try:
                prefs = user.calendar_preferences
                if not prefs.email_enabled:
                    continue
            except UserCalendarPreferences.DoesNotExist:
                pass  # No preferences = send email

            # Build email context
            context = {
                "user": user,
                "event": activity,  # Keep 'event' name for template compatibility
                "event_url": f"{settings.BASE_URL}{reverse('common:coordination_events')}",
                "current_year": timezone.now().year,
                "base_url": settings.BASE_URL,
            }

            # Render HTML email
            html_content = render_to_string(
                "common/email/event_notification.html", context
            )

            # Send email
            msg = EmailMultiAlternatives(
                subject=f"New Activity: {activity.title}",
                body=f"You've been assigned to: {activity.title}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            # Create notification record
            CalendarNotification.objects.create(
                user=user,
                notification_type="event_created",
                title=f"New Activity: {activity.title}",
                message=f"You've been assigned to {activity.title}",
                sent_at=timezone.now(),
            )

            sent_count += 1

        logger.info(f"Sent {sent_count} activity notifications for: {activity.title}")
        return f"Sent {sent_count} notifications"

    except WorkItem.DoesNotExist:
        logger.error(f"Activity {event_id} not found")
        return "Activity not found"
    except Exception as e:
        logger.error(f"Error sending activity notifications: {e}")
        raise


@shared_task
def send_event_reminder(event_id, minutes_before=60):
    """
    Send activity/event reminder emails based on user preferences.

    DEPRECATED: This function is maintained for backward compatibility.
    New code should use WorkItem-specific reminder handlers.

    Args:
        event_id: UUID of the activity (WorkItem)
        minutes_before: Minutes before activity (default: 60)
    """
    try:
        # Get WorkItem (activity/event)
        activity = WorkItem.objects.get(pk=event_id, work_type='activity')

        # Check if activity has start date/time
        if not activity.start_date:
            return "Activity has no start date"

        # Combine date and time for datetime comparison
        if activity.start_time:
            start_datetime = timezone.make_aware(
                timezone.datetime.combine(activity.start_date, activity.start_time)
            )
        else:
            start_datetime = timezone.make_aware(
                timezone.datetime.combine(activity.start_date, timezone.datetime.min.time())
            )

        # Check if activity is in the future
        if start_datetime <= timezone.now():
            return "Activity already started"

        # Get assigned users
        assigned_users = activity.assigned_users.all()

        sent_count = 0
        for user in assigned_users:
            # Check preferences
            try:
                prefs = user.calendar_preferences
                if not prefs.email_enabled:
                    continue

                # Check if user wants reminder at this time
                if minutes_before not in prefs.default_reminder_times:
                    continue

                # Check quiet hours
                now = timezone.now()
                if prefs.quiet_hours_start and prefs.quiet_hours_end:
                    current_time = now.time()
                    if prefs.quiet_hours_start <= current_time <= prefs.quiet_hours_end:
                        continue  # Skip during quiet hours

            except UserCalendarPreferences.DoesNotExist:
                pass

            # Calculate time until activity
            time_until = start_datetime - timezone.now()
            hours_until = int(time_until.total_seconds() // 3600)
            minutes_until = int((time_until.total_seconds() % 3600) // 60)

            context = {
                "user": user,
                "event": activity,  # Keep 'event' name for template compatibility
                "hours_until": hours_until if hours_until > 0 else None,
                "minutes_until": minutes_until if hours_until == 0 else None,
                "event_url": f"{settings.BASE_URL}{reverse('common:coordination_events')}",
                "current_year": timezone.now().year,
                "base_url": settings.BASE_URL,
            }

            html_content = render_to_string("common/email/event_reminder.html", context)

            msg = EmailMultiAlternatives(
                subject=f"Reminder: {activity.title}",
                body=f"Reminder: {activity.title} starts soon",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            sent_count += 1

        logger.info(f"Sent {sent_count} reminders for activity: {activity.title}")
        return f"Sent {sent_count} reminders"

    except WorkItem.DoesNotExist:
        logger.error(f"Activity {event_id} not found")
        return "Activity not found"
    except Exception as e:
        logger.error(f"Error sending reminders: {e}")
        raise


@shared_task
def send_daily_digest():
    """
    Send daily calendar digest to users who have it enabled.

    Shows user's assigned activities/events for today and upcoming week.
    """
    try:
        # Get users with daily digest enabled
        users_with_digest = UserCalendarPreferences.objects.filter(
            daily_digest=True, email_enabled=True
        ).select_related("user")

        sent_count = 0
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        week_from_now = today + timedelta(days=7)

        for prefs in users_with_digest:
            user = prefs.user

            # Get today's activities for user
            today_activities = WorkItem.objects.filter(
                work_type='activity',
                assigned_users=user,
                start_date=today
            ).order_by('start_time')

            # Get upcoming activities (next 7 days)
            upcoming_activities = WorkItem.objects.filter(
                work_type='activity',
                assigned_users=user,
                start_date__range=[tomorrow, week_from_now]
            ).order_by('start_date', 'start_time')[:10]

            # Skip if no activities
            if not today_activities.exists() and not upcoming_activities.exists():
                continue

            context = {
                "user": user,
                "date": today,
                "today_events": today_activities,  # Keep 'today_events' for template compatibility
                "upcoming_events": upcoming_activities,  # Keep 'upcoming_events' for template compatibility
                "calendar_url": f"{settings.BASE_URL}{reverse('common:oobc_calendar')}",
                "current_year": timezone.now().year,
                "base_url": settings.BASE_URL,
            }

            html_content = render_to_string("common/email/daily_digest.html", context)

            msg = EmailMultiAlternatives(
                subject=f"Daily Calendar Digest - {today.strftime('%B %d, %Y')}",
                body=f"Your calendar digest for {today.strftime('%B %d, %Y')}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            sent_count += 1

        logger.info(f"Sent {sent_count} daily digests")
        return f"Sent {sent_count} daily digests"

    except Exception as e:
        logger.error(f"Error sending daily digests: {e}")
        raise


@shared_task
def send_booking_notification(booking_id, notification_type="created"):
    """
    Send booking-related notifications.

    Args:
        booking_id: ID of the booking
        notification_type: 'created', 'approved', 'rejected'
    """
    try:
        booking = CalendarResourceBooking.objects.select_related(
            "resource", "booked_by", "approved_by"
        ).get(pk=booking_id)

        if notification_type == "created":
            # Notify resource admin
            template = "common/email/booking_request.html"
            subject = f"New Booking Request: {booking.resource.name}"
            recipient = (
                booking.resource.admin_email
                if hasattr(booking.resource, "admin_email")
                else settings.ADMINS[0][1]
            )
        else:
            # Notify requester
            template = "common/email/booking_status_update.html"
            subject = f"Booking {notification_type.title()}: {booking.resource.name}"
            recipient = booking.booked_by.email

        context = {
            "booking": booking,
            "recipient": booking.booked_by if notification_type != "created" else None,
            "status_display": notification_type.title(),
            "booking_url": f"{settings.BASE_URL}/oobc-management/calendar/bookings/",
            "current_year": timezone.now().year,
            "base_url": settings.BASE_URL,
        }

        html_content = render_to_string(template, context)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=f"Booking notification: {booking.resource.name}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        logger.info(
            f"Sent booking {notification_type} notification for: {booking.resource.name}"
        )
        return f"Sent {notification_type} notification"

    except CalendarResourceBooking.DoesNotExist:
        logger.error(f"Booking {booking_id} not found")
        return "Booking not found"
    except Exception as e:
        logger.error(f"Error sending booking notification: {e}")
        raise


@shared_task
def process_scheduled_reminders():
    """
    Process all scheduled reminders for upcoming activities.

    Called by Celery Beat every 15 minutes.
    Checks for activities starting at specific reminder intervals.
    """
    try:
        now = timezone.now()
        reminder_times = [15, 30, 60, 120, 1440]  # 15min, 30min, 1hr, 2hr, 1day

        sent_count = 0
        for minutes in reminder_times:
            target_datetime = now + timedelta(minutes=minutes)
            target_date = target_datetime.date()

            # Find activities on target date (activities may not have exact time)
            activities = WorkItem.objects.filter(
                work_type='activity',
                start_date=target_date
            )

            # Filter activities that have start_time matching target time (within tolerance)
            for activity in activities:
                if activity.start_time:
                    activity_datetime = timezone.make_aware(
                        timezone.datetime.combine(activity.start_date, activity.start_time)
                    )
                    # Check if within 1 minute tolerance
                    time_diff = abs((activity_datetime - target_datetime).total_seconds())
                    if time_diff <= 60:  # Within 1 minute
                        send_event_reminder.delay(str(activity.id), minutes_before=minutes)
                        sent_count += 1
                elif minutes == 1440:  # For all-day activities, send 1-day reminder
                    send_event_reminder.delay(str(activity.id), minutes_before=minutes)
                    sent_count += 1

        logger.info(f"Queued {sent_count} activity reminders")
        return f"Queued {sent_count} reminders"

    except Exception as e:
        logger.error(f"Error processing scheduled reminders: {e}")
        raise


@shared_task
def clean_expired_calendar_shares():
    """
    Clean up expired calendar share links.
    Called daily by Celery Beat.
    """
    try:
        from common.models import SharedCalendarLink

        now = timezone.now()
        expired_shares = SharedCalendarLink.objects.filter(expires_at__lt=now)

        count = expired_shares.count()
        expired_shares.delete()

        logger.info(f"Deleted {count} expired calendar shares")
        return f"Deleted {count} expired shares"

    except Exception as e:
        logger.error(f"Error cleaning expired shares: {e}")
        raise


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def send_single_calendar_notification(self, notification_id):
    """Deliver a single `CalendarNotification` to its recipient."""

    try:
        notification = CalendarNotification.objects.select_related("recipient").get(
            pk=notification_id
        )
    except CalendarNotification.DoesNotExist:
        logger.warning("Calendar notification %s no longer exists", notification_id)
        return "missing"

    recipient = notification.recipient

    try:
        if notification.delivery_method == CalendarNotification.DELIVERY_EMAIL:
            if not recipient.email:
                raise ValueError("Recipient has no email address configured")

            subject = f"OOBC Calendar: {notification.get_notification_type_display()}"
            body_lines = [
                "You have a new calendar update from the OOBCMS platform.",
                f"Notification type: {notification.get_notification_type_display()}",
            ]
            if notification.event_instance and hasattr(
                notification.event_instance, "title"
            ):
                body_lines.append(f"Event: {notification.event_instance.title}")

            send_mail(
                subject=subject,
                message="\n".join(body_lines),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False,
            )
        else:
            logger.info(
                "Skipping notification %s with unsupported delivery method %s",
                notification_id,
                notification.delivery_method,
            )

        notification.status = CalendarNotification.STATUS_SENT
        notification.sent_at = timezone.now()
        notification.error_message = ""
        notification.save(update_fields=["status", "sent_at", "error_message"])
        return "sent"

    except Exception as exc:  # pragma: no cover - Celery will retry
        notification.status = CalendarNotification.STATUS_FAILED
        notification.error_message = str(exc)
        notification.save(update_fields=["status", "error_message"])
        logger.error(
            "Failed to deliver calendar notification %s: %s", notification_id, exc
        )
        raise


@shared_task
def send_calendar_notifications_batch(batch_size=100):
    """Dispatch pending calendar notifications via Celery groups."""

    now = timezone.now()
    pending_ids = list(
        CalendarNotification.objects.filter(
            status=CalendarNotification.STATUS_PENDING,
            scheduled_for__lte=now,
        )
        .order_by("scheduled_for")
        .values_list("id", flat=True)[:batch_size]
    )

    if not pending_ids:
        return {"queued": 0}

    CalendarNotification.objects.filter(id__in=pending_ids).update(
        scheduled_for=now + timedelta(minutes=5)
    )

    group(
        send_single_calendar_notification.s(notification_id)
        for notification_id in pending_ids
    ).apply_async()
    logger.info("Queued %s calendar notifications for delivery", len(pending_ids))
    return {"queued": len(pending_ids)}
