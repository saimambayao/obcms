# OBCMS Priority 1 Implementation Plan

**Document Status:** ✅ COMPREHENSIVE SPECIFICATION
**Created:** 2025-10-13
**Priority Level:** HIGH
**Target Completion:** CRITICAL

---

## EXECUTIVE SUMMARY

This document provides detailed implementation specifications for three HIGH-PRIORITY enhancements identified in the OBCMS Guidelines Alignment Report:

1. **Automated Quarterly Meeting Scheduler** - Automates MAO coordination meeting creation and reminders
2. **Service Catalog Public View** - Publishes MAO services for OBC community access
3. **OCM Coordination Dashboard** - Provides consolidated oversight of all MAO PPAs

These enhancements directly address gaps identified in the alignment analysis and will elevate system compliance to **95%+**.

---

## ENHANCEMENT 1: AUTOMATED QUARTERLY MEETING SCHEDULER

### Feature Overview

**Purpose:** Automate the creation of quarterly coordination meetings for all active MAOs, send reminders to focal persons, and track attendance/minutes as mandated by OBC Guidelines Section 2.

**Business Value:**
- Ensures 100% compliance with quarterly meeting mandate
- Reduces administrative overhead by 80%
- Improves MAO engagement through automated reminders
- Provides audit trail for coordination activities

### Detailed Specifications

#### 1.1 Database Schema Changes

**New Model: `QuarterlyMeetingSeries`**

```python
# File: src/coordination/models.py

class QuarterlyMeetingSeries(models.Model):
    """Manages quarterly meeting series for MAOs."""

    QUARTER_CHOICES = [
        ('Q1', 'Quarter 1 (January-March)'),
        ('Q2', 'Quarter 2 (April-June)'),
        ('Q3', 'Quarter 3 (July-September)'),
        ('Q4', 'Quarter 4 (October-December)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Core Fields
    fiscal_year = models.PositiveIntegerField(
        help_text="Fiscal year for this meeting series"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this series is currently active"
    )

    # Meeting Configuration
    default_venue = models.CharField(
        max_length=255,
        default="OOBC Conference Room",
        help_text="Default venue for quarterly meetings"
    )
    default_duration_minutes = models.IntegerField(
        default=120,
        help_text="Default meeting duration (minutes)"
    )

    # Reminder Configuration
    reminder_days_before = models.JSONField(
        default=list,  # [7, 1]
        help_text="Days before meeting to send reminders (e.g., [7, 1])"
    )

    # Facilitator Assignment
    default_facilitators = models.ManyToManyField(
        User,
        related_name='facilitated_quarterly_meetings',
        blank=True,
        help_text="Default OOBC staff to facilitate quarterly meetings"
    )

    # Auto-generation Settings
    auto_generate_enabled = models.BooleanField(
        default=True,
        help_text="Automatically generate meetings for new MAOs"
    )

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_quarterly_series'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['fiscal_year']]
        ordering = ['-fiscal_year']
        verbose_name = 'Quarterly Meeting Series'
        verbose_name_plural = 'Quarterly Meeting Series'

    def __str__(self):
        return f"Quarterly Meetings FY {self.fiscal_year}"

    def generate_meetings_for_mao(self, mao, created_by):
        """Generate Q1-Q4 meetings for a specific MAO."""
        pass  # Implementation in service layer
```

**Extended Fields for `StakeholderEngagement`**

```python
# Add to existing StakeholderEngagement model

class StakeholderEngagement(models.Model):
    # ... existing fields ...

    # Quarterly Meeting Extensions
    quarterly_series = models.ForeignKey(
        QuarterlyMeetingSeries,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='generated_meetings',
        help_text="Link to quarterly meeting series if auto-generated"
    )

    quarter = models.CharField(
        max_length=2,
        choices=QuarterlyMeetingSeries.QUARTER_CHOICES,
        blank=True,
        help_text="Fiscal quarter (Q1-Q4)"
    )

    meeting_sequence_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Meeting number in sequence for the MAO (1, 2, 3...)"
    )

    attendance_confirmed_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of confirmed attendees"
    )

    minutes_approved = models.BooleanField(
        default=False,
        help_text="Whether meeting minutes have been approved"
    )

    minutes_approved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_meeting_minutes',
        help_text="User who approved the minutes"
    )

    minutes_approved_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when minutes were approved"
    )
```

**New Model: `MeetingReminder`**

```python
# File: src/coordination/models.py

class MeetingReminder(models.Model):
    """Track reminders sent for stakeholder engagements."""

    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    engagement = models.ForeignKey(
        StakeholderEngagement,
        on_delete=models.CASCADE,
        related_name='reminders',
        help_text="Stakeholder engagement this reminder is for"
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meeting_reminders',
        help_text="User receiving the reminder"
    )

    focal_person = models.ForeignKey(
        'MAOFocalPerson',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='meeting_reminders',
        help_text="MAO focal person if applicable"
    )

    # Scheduling
    scheduled_send_datetime = models.DateTimeField(
        help_text="When this reminder should be sent"
    )
    days_before_meeting = models.PositiveIntegerField(
        help_text="Days before meeting this reminder is scheduled"
    )

    # Delivery Status
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    failed_reason = models.TextField(blank=True)

    # Content
    subject = models.CharField(max_length=255)
    message_body = models.TextField()

    # Tracking
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    in_app_notification_sent = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_send_datetime']
        indexes = [
            models.Index(fields=['status', 'scheduled_send_datetime']),
            models.Index(fields=['engagement', 'recipient']),
        ]
        verbose_name = 'Meeting Reminder'
        verbose_name_plural = 'Meeting Reminders'

    def __str__(self):
        return f"Reminder for {self.recipient.get_full_name()} - {self.engagement.title}"
```

#### 1.2 API Endpoints

**Base URL:** `/api/v1/coordination/quarterly-meetings/`

**Endpoint 1: Generate Quarterly Meetings**
```
POST /api/v1/coordination/quarterly-meetings/generate/
```

**Request Body:**
```json
{
  "fiscal_year": 2025,
  "mao_ids": ["uuid1", "uuid2"],  // Optional: specific MAOs, or all if omitted
  "quarter": "all",  // or "Q1", "Q2", "Q3", "Q4"
  "overwrite_existing": false
}
```

**Response:**
```json
{
  "success": true,
  "meetings_created": 48,
  "details": {
    "Q1": 12,
    "Q2": 12,
    "Q3": 12,
    "Q4": 12
  },
  "series_id": "uuid-series",
  "message": "Successfully generated 48 quarterly meetings for 12 MAOs"
}
```

**Endpoint 2: List Quarterly Meetings**
```
GET /api/v1/coordination/quarterly-meetings/
```

**Query Parameters:**
- `fiscal_year` (int): Filter by fiscal year
- `quarter` (str): Filter by quarter (Q1-Q4)
- `mao_id` (uuid): Filter by MAO
- `status` (str): Filter by status
- `upcoming` (bool): Only upcoming meetings

**Response:**
```json
{
  "count": 48,
  "results": [
    {
      "id": "uuid",
      "title": "MILF - Q1 2025 Coordination Meeting",
      "engagement_type": "Quarterly Coordination Meeting",
      "mao": {
        "id": "uuid",
        "name": "Moro Islamic Liberation Front",
        "acronym": "MILF"
      },
      "planned_date": "2025-01-15T10:00:00Z",
      "quarter": "Q1",
      "fiscal_year": 2025,
      "status": "scheduled",
      "focal_persons": [
        {
          "id": "uuid",
          "name": "Juan Dela Cruz",
          "role": "primary",
          "contact_email": "juan@milf.gov.ph"
        }
      ],
      "attendance_confirmed_count": 3,
      "meeting_sequence_number": 1
    }
  ]
}
```

**Endpoint 3: Send Manual Reminder**
```
POST /api/v1/coordination/quarterly-meetings/{meeting_id}/remind/
```

**Request Body:**
```json
{
  "recipient_ids": ["uuid1", "uuid2"],  // Optional: specific recipients
  "send_immediately": true,
  "include_sms": false
}
```

**Response:**
```json
{
  "success": true,
  "reminders_sent": 5,
  "failed": 0,
  "details": [
    {
      "recipient": "Juan Dela Cruz",
      "email": "sent",
      "sms": "skipped"
    }
  ]
}
```

**Endpoint 4: Update Attendance**
```
PATCH /api/v1/coordination/quarterly-meetings/{meeting_id}/attendance/
```

**Request Body:**
```json
{
  "attendance_list": [
    {
      "name": "Juan Dela Cruz",
      "organization": "MILF",
      "designation": "Planning Officer",
      "attended": true,
      "remarks": "Participated fully"
    }
  ],
  "actual_participants": 8
}
```

**Endpoint 5: Approve Meeting Minutes**
```
POST /api/v1/coordination/quarterly-meetings/{meeting_id}/approve-minutes/
```

**Request Body:**
```json
{
  "meeting_minutes": "Detailed minutes text...",
  "key_outcomes": "Summary of outcomes...",
  "action_items": "List of action items...",
  "next_meeting_date": "2025-04-15"
}
```

#### 1.3 Celery Background Tasks

**File:** `src/coordination/tasks.py`

```python
from celery import shared_task
from django.utils import timezone
from datetime import timedelta

@shared_task(name='coordination.generate_quarterly_meetings')
def generate_quarterly_meetings_task(fiscal_year, mao_ids=None, quarter='all'):
    """
    Celery task to generate quarterly meetings for MAOs.

    Args:
        fiscal_year (int): Fiscal year to generate meetings for
        mao_ids (list): Optional list of MAO UUIDs
        quarter (str): 'all', 'Q1', 'Q2', 'Q3', or 'Q4'

    Returns:
        dict: Summary of meetings created
    """
    from coordination.services import QuarterlyMeetingService

    service = QuarterlyMeetingService()
    result = service.generate_meetings(
        fiscal_year=fiscal_year,
        mao_ids=mao_ids,
        quarter=quarter
    )

    return {
        'status': 'completed',
        'meetings_created': result['meetings_created'],
        'fiscal_year': fiscal_year
    }


@shared_task(name='coordination.send_meeting_reminders')
def send_meeting_reminders_task():
    """
    Celery periodic task to send meeting reminders.
    Runs every hour to check for reminders due.

    Returns:
        dict: Summary of reminders sent
    """
    from coordination.models import MeetingReminder
    from coordination.services import ReminderService

    # Get pending reminders due within the next hour
    now = timezone.now()
    due_reminders = MeetingReminder.objects.filter(
        status=MeetingReminder.STATUS_PENDING,
        scheduled_send_datetime__lte=now + timedelta(hours=1)
    )

    service = ReminderService()
    sent_count = 0
    failed_count = 0

    for reminder in due_reminders:
        success = service.send_reminder(reminder)
        if success:
            sent_count += 1
        else:
            failed_count += 1

    return {
        'status': 'completed',
        'reminders_sent': sent_count,
        'reminders_failed': failed_count,
        'timestamp': now.isoformat()
    }


@shared_task(name='coordination.create_reminders_for_meeting')
def create_reminders_for_meeting_task(meeting_id):
    """
    Create reminder records for a specific meeting.

    Args:
        meeting_id (str): UUID of StakeholderEngagement

    Returns:
        dict: Summary of reminders created
    """
    from coordination.services import ReminderService

    service = ReminderService()
    result = service.create_meeting_reminders(meeting_id)

    return {
        'status': 'completed',
        'meeting_id': meeting_id,
        'reminders_created': result['count']
    }


@shared_task(name='coordination.check_overdue_meetings')
def check_overdue_meetings_task():
    """
    Periodic task to flag overdue meetings and send alerts.
    Runs daily.

    Returns:
        dict: Summary of overdue meetings
    """
    from coordination.models import StakeholderEngagement
    from coordination.services import MeetingAlertService

    # Get meetings that are overdue (status=scheduled, planned_date < today)
    overdue_meetings = StakeholderEngagement.objects.filter(
        status='scheduled',
        planned_date__lt=timezone.now().date(),
        quarterly_series__isnull=False  # Only quarterly meetings
    )

    service = MeetingAlertService()
    alerts_sent = 0

    for meeting in overdue_meetings:
        service.send_overdue_alert(meeting)
        alerts_sent += 1

    return {
        'status': 'completed',
        'overdue_meetings': overdue_meetings.count(),
        'alerts_sent': alerts_sent
    }
```

**Celery Beat Schedule:**

```python
# File: src/obc_management/celery.py

from celery.schedules import crontab

app.conf.beat_schedule = {
    'send-meeting-reminders-hourly': {
        'task': 'coordination.send_meeting_reminders',
        'schedule': crontab(minute=0),  # Every hour at :00
    },
    'check-overdue-meetings-daily': {
        'task': 'coordination.check_overdue_meetings',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8:00 AM
    },
    # Auto-generate meetings for next fiscal year
    'auto-generate-next-year-meetings': {
        'task': 'coordination.generate_quarterly_meetings',
        'schedule': crontab(month_of_year=10, day_of_month=1, hour=0, minute=0),  # October 1 at midnight
        'kwargs': {'fiscal_year': 'next', 'quarter': 'all'}
    },
}
```

#### 1.4 UI/UX Implementation

**Admin Interface: Quarterly Meeting Dashboard**

**Route:** `/coordination/quarterly-meetings/`

**Wireframe Description:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Quarterly Coordination Meetings - FY 2025           [Generate]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Filters: [All Quarters ▼] [All MAOs ▼] [All Status ▼]         │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ Q1 2025 (January - March)                  12 meetings   │   │
│ │                                                            │   │
│ │  ✓ MILF - Jan 15, 2025        Completed   [View]         │   │
│ │  ⏰ MNLF - Jan 18, 2025         Upcoming   [Remind] [Edit]│   │
│ │  📅 Ministry of Health - Jan 22  Scheduled [Remind] [Edit]│   │
│ │  ...                                                       │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ Q2 2025 (April - June)                    12 meetings    │   │
│ │                                                            │   │
│ │  📅 MILF - Apr 15, 2025        Scheduled  [Remind] [Edit] │   │
│ │  📅 MNLF - Apr 18, 2025        Scheduled  [Remind] [Edit] │   │
│ │  ...                                                       │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Meeting Detail View (HTMX Powered)**

**Route:** `/coordination/quarterly-meetings/{meeting_id}/`

**Key Sections:**
1. Meeting Information Card
2. MAO Focal Persons (with contact buttons)
3. Agenda Items (editable)
4. Attendance Tracker (real-time updates)
5. Meeting Minutes (rich text editor)
6. Action Items (task tracker)
7. Document Attachments

**HTMX Interactions:**
- **Confirm Attendance**: `hx-post="/api/v1/coordination/quarterly-meetings/{id}/attendance/"` → Update attendance count badge
- **Approve Minutes**: `hx-post="/api/v1/coordination/quarterly-meetings/{id}/approve-minutes/"` → Show approval badge
- **Send Reminder**: `hx-post="/api/v1/coordination/quarterly-meetings/{id}/remind/"` → Show toast notification

**Notification Template (Email)**

```html
Subject: Reminder: Quarterly Coordination Meeting with OOBC - {{ quarter }} {{ fiscal_year }}

Dear {{ focal_person_name }},

This is a reminder that the quarterly coordination meeting between {{ mao_name }} and the Office for Other Bangsamoro Communities (OOBC) is scheduled on:

📅 Date: {{ meeting_date }}
⏰ Time: {{ meeting_time }}
📍 Venue: {{ venue }}

Meeting Agenda:
1. Review of Q{{ previous_quarter }} PPAs and accomplishments
2. Planning for Q{{ current_quarter }} activities
3. OBC assistance updates and coordination
4. Issues, concerns, and support needed

Please confirm your attendance by clicking the link below:
[Confirm Attendance]

For questions or schedule conflicts, please contact:
{{ oobc_contact_name }}
{{ oobc_contact_email }}
{{ oobc_contact_phone }}

Best regards,
OOBC Coordination Team
```

#### 1.5 Integration Points

**With Existing Models:**

1. **MAOFocalPerson** → Recipient list for reminders
2. **Organization** (type='bmoa') → List of active MAOs
3. **StakeholderEngagement** → Base model for meetings
4. **RecurringEventPattern** → Optional: advanced recurrence rules
5. **CommunicationSchedule** → Reminder scheduling
6. **EngagementFacilitator** → OOBC staff assignment

**With Calendar System:**

```python
# Automatically create calendar events
from common.models import CalendarNotification

def create_calendar_integration(meeting):
    """Create calendar notifications for quarterly meeting."""
    for focal_person in meeting.get_mao_focal_persons():
        CalendarNotification.objects.create(
            content_type=ContentType.objects.get_for_model(StakeholderEngagement),
            object_id=meeting.id,
            recipient=focal_person.user,
            notification_type='invitation',
            delivery_method='email',
            scheduled_for=meeting.planned_date - timedelta(days=7)
        )
```

#### 1.6 Testing Requirements

**Unit Tests:**
- Test `QuarterlyMeetingSeries.generate_meetings_for_mao()`
- Test reminder scheduling logic
- Test attendance tracking updates
- Test minutes approval workflow

**Integration Tests:**
- Test full meeting generation workflow (FY creation → MAO meetings)
- Test reminder delivery (email + SMS)
- Test HTMX attendance update flow
- Test calendar integration

**End-to-End Tests:**
1. Admin generates Q1-Q4 meetings for all MAOs
2. System sends 7-day reminder to focal persons
3. Focal person clicks "Confirm Attendance"
4. Meeting date arrives, status auto-updates to "in_progress"
5. Staff records attendance and minutes
6. Supervisor approves minutes
7. Meeting marked as "completed"

#### 1.7 Acceptance Criteria

✅ System automatically generates Q1-Q4 meetings for all active MAOs when fiscal year is created
✅ Reminders sent at configured intervals (7 days, 1 day before)
✅ MAO focal persons can confirm attendance via email link or dashboard
✅ OOBC staff can record attendance, minutes, and action items in real-time
✅ Meeting minutes require supervisor approval before finalization
✅ Overdue meetings are flagged and alerts sent to administrators
✅ Calendar integration creates events in user calendars
✅ Audit log tracks all meeting activities (creation, updates, approvals)
✅ Dashboard provides fiscal year overview with completion metrics
✅ Mobile-responsive interface for attendance recording on-site

---

## ENHANCEMENT 2: SERVICE CATALOG PUBLIC VIEW

### Feature Overview

**Purpose:** Provide a publicly accessible catalog of MAO services (PPAs) available to OBC communities, including eligibility criteria, application procedures, and success stories.

**Business Value:**
- Transparency: Communities can discover available services
- Accessibility: Direct request submission reduces barriers
- Efficiency: Reduces information-seeking phone calls by 60%
- Empowerment: Communities make informed assistance requests

### Detailed Specifications

#### 2.1 Database Schema Changes

**New Model: `ServiceCatalogEntry`**

```python
# File: src/monitoring/models.py

class ServiceCatalogEntry(models.Model):
    """Public-facing catalog of services available to OBCs."""

    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_ARCHIVED, 'Archived'),
    ]

    ACCESSIBILITY_CHOICES = [
        ('direct_application', 'Direct Application'),
        ('nomination_required', 'Nomination Required'),
        ('referral_only', 'Referral Only'),
        ('competitive_selection', 'Competitive Selection'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to PPA
    ppa = models.OneToOneField(
        'MonitoringEntry',
        on_delete=models.CASCADE,
        related_name='service_catalog_entry',
        help_text="Underlying PPA this service represents"
    )

    # Public-Facing Information
    service_name = models.CharField(
        max_length=255,
        help_text="Public-facing service name (may differ from PPA title)"
    )

    short_description = models.TextField(
        max_length=500,
        help_text="Brief description for catalog listing (500 chars max)"
    )

    full_description = models.TextField(
        help_text="Complete service description"
    )

    # Eligibility
    eligibility_criteria = models.TextField(
        help_text="Who can access this service (clear language)"
    )

    target_beneficiaries = models.TextField(
        help_text="Specific beneficiary groups (OBC leaders, youth, farmers, etc.)"
    )

    geographic_scope = models.TextField(
        help_text="Geographic coverage (Regions, provinces, municipalities)"
    )

    # Application Process
    application_procedure = models.TextField(
        help_text="Step-by-step application process"
    )

    required_documents = models.JSONField(
        default=list,
        help_text="List of required documents: [{name, description, sample_url}]"
    )

    application_deadlines = models.TextField(
        blank=True,
        help_text="Application windows or deadlines"
    )

    accessibility_type = models.CharField(
        max_length=30,
        choices=ACCESSIBILITY_CHOICES,
        default='direct_application'
    )

    # Service Details
    service_delivery_method = models.CharField(
        max_length=255,
        blank=True,
        help_text="How service is delivered (training, grants, goods, etc.)"
    )

    expected_duration = models.CharField(
        max_length=100,
        blank=True,
        help_text="Expected service duration or timeline"
    )

    slots_available = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Total slots available (from PPA obc_slots)"
    )

    slots_remaining = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Remaining slots (updated automatically)"
    )

    # Contact Information
    contact_person = models.CharField(
        max_length=255,
        help_text="Name of contact person"
    )

    contact_designation = models.CharField(
        max_length=150,
        help_text="Position/designation"
    )

    contact_organization = models.ForeignKey(
        'coordination.Organization',
        on_delete=models.PROTECT,
        related_name='published_services'
    )

    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=50)
    contact_mobile = models.CharField(max_length=50, blank=True)

    # Success Stories
    success_stories = models.TextField(
        blank=True,
        help_text="Success stories and case studies (rich text)"
    )

    testimonials = models.JSONField(
        default=list,
        blank=True,
        help_text="List of testimonials: [{name, location, quote, date}]"
    )

    # Media
    featured_image = models.ImageField(
        upload_to='service_catalog/images/%Y/%m/',
        null=True,
        blank=True,
        help_text="Featured image for catalog card"
    )

    photo_gallery = models.JSONField(
        default=list,
        blank=True,
        help_text="List of image URLs for gallery"
    )

    video_url = models.URLField(
        blank=True,
        help_text="YouTube or video URL"
    )

    # Publication Status
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT
    )

    is_featured = models.BooleanField(
        default=False,
        help_text="Show in featured services section"
    )

    is_accepting_applications = models.BooleanField(
        default=True,
        help_text="Whether currently accepting new applications"
    )

    published_date = models.DateField(null=True, blank=True)
    archived_date = models.DateField(null=True, blank=True)

    # SEO & Discoverability
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for filtering (livelihood, education, health, etc.)"
    )

    search_keywords = models.TextField(
        blank=True,
        help_text="Keywords for search optimization"
    )

    # Analytics
    view_count = models.PositiveIntegerField(default=0)
    application_count = models.PositiveIntegerField(default=0)

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_service_entries'
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='updated_service_entries'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-published_date', 'service_name']
        indexes = [
            models.Index(fields=['status', 'is_accepting_applications']),
            models.Index(fields=['contact_organization', 'status']),
        ]
        verbose_name = 'Service Catalog Entry'
        verbose_name_plural = 'Service Catalog Entries'

    def __str__(self):
        return f"{self.service_name} - {self.contact_organization.acronym}"

    @property
    def is_available(self):
        """Check if service is currently available."""
        return (
            self.status == self.STATUS_PUBLISHED and
            self.is_accepting_applications and
            (self.slots_remaining is None or self.slots_remaining > 0)
        )
```

**New Model: `ServiceRequest`**

```python
# File: src/monitoring/models.py

class ServiceRequest(models.Model):
    """Community request for a catalog service."""

    STATUS_SUBMITTED = 'submitted'
    STATUS_UNDER_REVIEW = 'under_review'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_UNDER_REVIEW, 'Under Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Service & Requester
    service = models.ForeignKey(
        ServiceCatalogEntry,
        on_delete=models.PROTECT,
        related_name='service_requests'
    )

    requester_name = models.CharField(max_length=255)
    requester_position = models.CharField(max_length=150)
    requester_organization = models.CharField(max_length=255)
    requester_contact_number = models.CharField(max_length=50)
    requester_email = models.EmailField()

    community = models.ForeignKey(
        'communities.OBCCommunity',
        on_delete=models.PROTECT,
        related_name='service_requests'
    )

    # Request Details
    request_details = models.TextField(
        help_text="Detailed request description"
    )

    beneficiary_count = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Expected number of beneficiaries"
    )

    submitted_documents = models.JSONField(
        default=list,
        help_text="List of uploaded document references"
    )

    # Status & Review
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_SUBMITTED
    )

    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_service_requests'
    )

    reviewed_date = models.DateField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    rejection_reason = models.TextField(blank=True)

    # Linked PPA Request
    created_monitoring_entry = models.ForeignKey(
        'MonitoringEntry',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='source_service_requests',
        help_text="MonitoringEntry (OBC request) created from this service request"
    )

    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['status', 'submitted_at']),
            models.Index(fields=['service', 'status']),
            models.Index(fields=['community', 'status']),
        ]
        verbose_name = 'Service Request'
        verbose_name_plural = 'Service Requests'

    def __str__(self):
        return f"{self.requester_name} - {self.service.service_name}"
```

#### 2.2 API Endpoints

**Public API (No Authentication Required):**

**Endpoint 1: List Published Services**
```
GET /api/v1/public/service-catalog/
```

**Query Parameters:**
- `sector` (str): Filter by sector
- `mao` (uuid): Filter by MAO organization
- `region` (str): Filter by region
- `search` (str): Full-text search
- `tags` (str): Comma-separated tags
- `featured` (bool): Only featured services
- `accepting_applications` (bool): Only accepting applications

**Response:**
```json
{
  "count": 24,
  "results": [
    {
      "id": "uuid",
      "service_name": "Livelihood Skills Training for OBC Youth",
      "short_description": "6-month vocational training program...",
      "featured_image": "/media/service_catalog/images/2025/01/training.jpg",
      "implementing_mao": {
        "id": "uuid",
        "name": "Ministry of Social Services",
        "acronym": "MSS"
      },
      "sector": "social",
      "tags": ["livelihood", "youth", "training"],
      "slots_remaining": 45,
      "is_available": true,
      "application_deadline": "2025-03-31"
    }
  ]
}
```

**Endpoint 2: Service Detail**
```
GET /api/v1/public/service-catalog/{service_id}/
```

**Response:**
```json
{
  "id": "uuid",
  "service_name": "Livelihood Skills Training for OBC Youth",
  "full_description": "Comprehensive description...",
  "eligibility_criteria": "Must be OBC youth aged 18-30...",
  "application_procedure": "Step 1: Fill out application form...",
  "required_documents": [
    {
      "name": "Valid ID",
      "description": "Government-issued ID",
      "sample_url": "/media/samples/valid-id-sample.pdf"
    }
  ],
  "contact_person": "Maria Santos",
  "contact_email": "maria.santos@mss.gov.ph",
  "contact_phone": "+63 912 345 6789",
  "success_stories": "<p>In 2024, 120 OBC youth completed...</p>",
  "testimonials": [
    {
      "name": "Juan Dela Cruz",
      "location": "Barangay Peaceful, Zamboanga City",
      "quote": "This training changed my life...",
      "date": "2024-12-15"
    }
  ],
  "photo_gallery": ["/media/...", "/media/..."],
  "video_url": "https://youtube.com/watch?v=...",
  "view_count": 342
}
```

**Endpoint 3: Submit Service Request (Public)**
```
POST /api/v1/public/service-catalog/{service_id}/request/
```

**Request Body:**
```json
{
  "requester_name": "Juan Dela Cruz",
  "requester_position": "Barangay Captain",
  "requester_organization": "Barangay Peaceful",
  "requester_contact_number": "+63 912 345 6789",
  "requester_email": "juan@email.com",
  "community_id": "uuid",
  "request_details": "We have 30 youth interested in livelihood training...",
  "beneficiary_count": 30,
  "submitted_documents": [
    {
      "document_type": "endorsement_letter",
      "file_url": "/uploads/...",
      "filename": "endorsement.pdf"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "request_id": "uuid",
  "tracking_code": "SR-2025-00123",
  "message": "Your request has been submitted successfully. You will receive an email confirmation shortly.",
  "estimated_review_time": "5-7 business days"
}
```

**Authenticated API (OOBC Staff/MAO):**

**Endpoint 4: Manage Service Catalog Entry**
```
POST /api/v1/coordination/service-catalog/
PATCH /api/v1/coordination/service-catalog/{service_id}/
DELETE /api/v1/coordination/service-catalog/{service_id}/
```

**Endpoint 5: Publish/Unpublish Service**
```
POST /api/v1/coordination/service-catalog/{service_id}/publish/
POST /api/v1/coordination/service-catalog/{service_id}/unpublish/
```

**Endpoint 6: Review Service Requests**
```
GET /api/v1/coordination/service-requests/
PATCH /api/v1/coordination/service-requests/{request_id}/review/
```

#### 2.3 UI/UX Implementation

**Public Service Catalog Homepage**

**Route:** `/services/` (public, no authentication)

**Wireframe Description:**

```
┌─────────────────────────────────────────────────────────────────┐
│ OOBC Service Catalog - Assistance for Bangsamoro Communities   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ [Search services...                    ] [Search Button]        │
│                                                                  │
│ Filter by:  [All Sectors ▼] [All MAOs ▼] [All Regions ▼]      │
│                                                                  │
│ ┌───────────────────────── FEATURED SERVICES ─────────────────┐│
│ │ ┌───────────┐  ┌───────────┐  ┌───────────┐                ││
│ │ │   [IMG]   │  │   [IMG]   │  │   [IMG]   │                ││
│ │ │ Livelihood│  │   Health  │  │ Education │                ││
│ │ │ Training  │  │ Services  │  │ Support   │                ││
│ │ │ 45 slots  │  │ Ongoing   │  │ 20 slots  │                ││
│ │ │ [Apply]   │  │ [Learn More]│ │ [Apply]   │                ││
│ │ └───────────┘  └───────────┘  └───────────┘                ││
│ └───────────────────────────────────────────────────────────────┘│
│                                                                  │
│ ALL SERVICES (24 available)                                     │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ 🌱 Livelihood Skills Training for OBC Youth                  ││
│ │    Ministry of Social Services | Economic Development        ││
│ │    6-month vocational training program for youth aged 18-30  ││
│ │    📍 Regions IX, XII | 👥 45 slots remaining                ││
│ │    [View Details] [Apply Now]                                ││
│ └──────────────────────────────────────────────────────────────┘│
│                                                                  │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ 🏥 Primary Health Care Services                              ││
│ │    Ministry of Health | Social Development                   ││
│ │    Free health consultations and medicines for OBC residents ││
│ │    📍 All Regions | 👥 Ongoing program                        ││
│ │    [View Details] [Request Service]                          ││
│ └──────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Service Detail Page**

**Route:** `/services/{service-id}/`

**Key Sections:**
1. Hero Section (image, title, MAO, availability status)
2. Service Overview
3. Eligibility Requirements (checklist format)
4. Application Process (numbered steps)
5. Required Documents (downloadable samples)
6. Success Stories & Testimonials
7. Photo/Video Gallery
8. Contact Information
9. **Apply Now Button** (sticky footer on mobile)

**Application Form (Multi-Step)**

**Route:** `/services/{service-id}/apply/`

**Step 1: Requester Information**
- Full Name
- Position/Designation
- Organization/Community
- Contact Number
- Email Address

**Step 2: Community & Beneficiary Details**
- Select OBC Community (dropdown)
- Number of Beneficiaries
- Request Details (rich text)

**Step 3: Document Upload**
- Upload required documents (drag-and-drop)
- Document verification status indicators

**Step 4: Review & Submit**
- Summary of application
- Terms & Conditions
- Submit button → Success page with tracking code

**HTMX Interactions:**
- **Search**: `hx-get="/api/v1/public/service-catalog/?search={query}"` → Live search results
- **Filter**: `hx-get="/api/v1/public/service-catalog/?sector={sector}"` → Filtered cards
- **Apply Modal**: `hx-get="/services/{id}/apply/"` → Load application form in modal
- **Document Upload**: `hx-post="/api/v1/uploads/"` → Upload progress + preview

#### 2.4 Integration Points

**With Existing Models:**

1. **MonitoringEntry** → Source PPA data (budget, schedule, beneficiaries)
2. **Organization** → MAO contact and details
3. **OBCCommunity** → Community selection dropdown
4. **MAOFocalPerson** → Contact information for services
5. **MonitoringEntry (category=obc_request)** → Convert ServiceRequest to formal OBC request

**With Communication System:**

```python
# Auto-send confirmation email
def send_service_request_confirmation(service_request):
    """Send email confirmation to requester."""
    from coordination.models import Communication

    Communication.objects.create(
        organization=service_request.service.contact_organization,
        communication_type='email',
        direction='outgoing',
        subject=f"Service Request Received - {service_request.service.service_name}",
        content=f"""
        Dear {service_request.requester_name},

        Your request for "{service_request.service.service_name}" has been received.

        Tracking Code: SR-{service_request.id}
        Submitted: {service_request.submitted_at}
        Estimated Review: 5-7 business days

        You will receive updates via email as your request is processed.

        Thank you,
        {service_request.service.contact_person}
        {service_request.service.contact_organization.name}
        """,
        status='sent',
        recorded_by=None  # System-generated
    )
```

#### 2.5 Testing Requirements

**Unit Tests:**
- Test `ServiceCatalogEntry.is_available` property
- Test slot availability calculations
- Test service request validation
- Test document upload processing

**Integration Tests:**
- Test service search and filtering
- Test application submission workflow
- Test email confirmation delivery
- Test conversion from ServiceRequest to MonitoringEntry

**End-to-End Tests:**
1. Public user searches for "livelihood training"
2. User views service detail page
3. User clicks "Apply Now"
4. User fills multi-step application form
5. User uploads required documents
6. User submits application
7. System sends confirmation email
8. OOBC staff reviews request
9. Staff approves and creates MonitoringEntry
10. User receives approval notification

#### 2.6 Acceptance Criteria

✅ Public can browse services without authentication
✅ Services display eligibility criteria in plain language
✅ Application form is mobile-responsive (80%+ of requests via mobile)
✅ Document upload supports drag-and-drop and mobile camera
✅ Tracking code provided immediately upon submission
✅ Email confirmation sent within 5 minutes
✅ OOBC staff can publish/unpublish services from admin panel
✅ Analytics track page views and application conversion rates
✅ Success stories display with images and testimonials
✅ Services automatically mark "No longer accepting" when slots=0

---

## ENHANCEMENT 3: OCM COORDINATION DASHBOARD

### Feature Overview

**Purpose:** Provide the Office of the Chief Minister (OCM) with a consolidated, real-time view of all MAO PPAs targeting OBCs, including geographic coverage, budget allocation, beneficiary overlap detection, and service gap analysis.

**Business Value:**
- Transparency: OCM has complete oversight of OBC assistance
- Efficiency: Identify duplication and gaps in service delivery
- Strategic Planning: Data-driven resource allocation decisions
- Accountability: Monitor MAO performance and budget utilization

### Detailed Specifications

#### 3.1 Database Schema Changes

**New Model: `OCMDashboardSnapshot`**

```python
# File: src/monitoring/models.py

class OCMDashboardSnapshot(models.Model):
    """Cached snapshot of OCM dashboard aggregated data."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    fiscal_year = models.PositiveIntegerField()
    quarter = models.CharField(
        max_length=2,
        choices=[('Q1', 'Q1'), ('Q2', 'Q2'), ('Q3', 'Q3'), ('Q4', 'Q4')],
        blank=True,
        help_text="Specific quarter or blank for full year"
    )

    # Aggregated Metrics
    total_ppas = models.PositiveIntegerField(default=0)
    total_budget_allocated = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_budget_utilized = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_beneficiaries = models.PositiveIntegerField(default=0)
    total_communities_served = models.PositiveIntegerField(default=0)

    # By Sector
    sector_breakdown = models.JSONField(
        default=dict,
        help_text="Budget and PPA count per sector"
    )

    # By MAO
    mao_breakdown = models.JSONField(
        default=dict,
        help_text="Performance metrics per MAO"
    )

    # By Region
    regional_coverage = models.JSONField(
        default=dict,
        help_text="PPAs and budget per region"
    )

    # Gap Analysis
    underserved_communities = models.JSONField(
        default=list,
        help_text="Communities with no PPAs or low coverage"
    )

    underrepresented_sectors = models.JSONField(
        default=list,
        help_text="Sectors with insufficient budget allocation"
    )

    # Beneficiary Overlap
    potential_overlaps = models.JSONField(
        default=list,
        help_text="Detected beneficiary overlaps between MAOs"
    )

    # Performance Indicators
    avg_ppa_progress = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    on_track_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    budget_utilization_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Metadata
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ['-fiscal_year', '-generated_at']
        unique_together = [['fiscal_year', 'quarter']]
        indexes = [
            models.Index(fields=['fiscal_year', 'quarter']),
        ]
        verbose_name = 'OCM Dashboard Snapshot'
        verbose_name_plural = 'OCM Dashboard Snapshots'

    def __str__(self):
        quarter_str = f" {self.quarter}" if self.quarter else ""
        return f"OCM Snapshot FY{self.fiscal_year}{quarter_str}"
```

**New Model: `BeneficiaryOverlapDetection`**

```python
# File: src/monitoring/models.py

class BeneficiaryOverlapDetection(models.Model):
    """Track potential beneficiary overlaps between MAO PPAs."""

    OVERLAP_TYPE_INDIVIDUAL = 'individual'
    OVERLAP_TYPE_HOUSEHOLD = 'household'
    OVERLAP_TYPE_ORGANIZATION = 'organization'
    OVERLAP_TYPE_COMMUNITY = 'community'

    OVERLAP_TYPE_CHOICES = [
        (OVERLAP_TYPE_INDIVIDUAL, 'Individual Beneficiary'),
        (OVERLAP_TYPE_HOUSEHOLD, 'Household'),
        (OVERLAP_TYPE_ORGANIZATION, 'Organization'),
        (OVERLAP_TYPE_COMMUNITY, 'Community-wide'),
    ]

    STATUS_DETECTED = 'detected'
    STATUS_REVIEWED = 'reviewed'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_FALSE_POSITIVE = 'false_positive'
    STATUS_RESOLVED = 'resolved'

    STATUS_CHOICES = [
        (STATUS_DETECTED, 'Detected'),
        (STATUS_REVIEWED, 'Under Review'),
        (STATUS_CONFIRMED, 'Confirmed Overlap'),
        (STATUS_FALSE_POSITIVE, 'False Positive'),
        (STATUS_RESOLVED, 'Resolved'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # PPAs with potential overlap
    ppa_a = models.ForeignKey(
        'MonitoringEntry',
        on_delete=models.CASCADE,
        related_name='overlap_detections_a'
    )
    ppa_b = models.ForeignKey(
        'MonitoringEntry',
        on_delete=models.CASCADE,
        related_name='overlap_detections_b'
    )

    # Overlap Details
    overlap_type = models.CharField(
        max_length=15,
        choices=OVERLAP_TYPE_CHOICES
    )

    overlap_count = models.PositiveIntegerField(
        help_text="Number of overlapping beneficiaries"
    )

    overlap_details = models.JSONField(
        default=dict,
        help_text="Detailed overlap information"
    )

    community = models.ForeignKey(
        'communities.OBCCommunity',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='beneficiary_overlaps'
    )

    confidence_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        help_text="Detection confidence (0.00-1.00)"
    )

    # Review Status
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default=STATUS_DETECTED
    )

    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_overlaps'
    )

    reviewed_date = models.DateField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    resolution_action = models.TextField(
        blank=True,
        help_text="Action taken to resolve overlap"
    )

    # Metadata
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['status', 'detected_at']),
            models.Index(fields=['ppa_a', 'ppa_b']),
            models.Index(fields=['community', 'status']),
        ]
        verbose_name = 'Beneficiary Overlap Detection'
        verbose_name_plural = 'Beneficiary Overlap Detections'

    def __str__(self):
        return f"Overlap: {self.ppa_a.title} ↔ {self.ppa_b.title}"
```

#### 3.2 API Endpoints

**OCM Dashboard API (Requires OCM or Executive Permissions):**

**Endpoint 1: Dashboard Overview**
```
GET /api/v1/ocm/dashboard/overview/
```

**Query Parameters:**
- `fiscal_year` (int, required)
- `quarter` (str, optional): Q1-Q4
- `refresh` (bool): Force recalculation

**Response:**
```json
{
  "fiscal_year": 2025,
  "quarter": "Q1",
  "snapshot_date": "2025-01-15T10:00:00Z",
  "summary": {
    "total_ppas": 156,
    "total_budget_allocated": "450000000.00",
    "total_budget_utilized": "320000000.00",
    "utilization_rate": 71.11,
    "total_beneficiaries": 45230,
    "communities_served": 312,
    "avg_ppa_progress": 68.5,
    "on_track_count": 120,
    "at_risk_count": 25,
    "delayed_count": 11
  },
  "by_sector": [
    {
      "sector": "economic",
      "sector_display": "Economic Development",
      "ppa_count": 45,
      "budget_allocated": "150000000.00",
      "budget_utilized": "105000000.00",
      "beneficiaries": 12500
    }
  ],
  "by_mao": [
    {
      "mao_id": "uuid",
      "mao_name": "Ministry of Social Services",
      "mao_acronym": "MSS",
      "ppa_count": 28,
      "budget_allocated": "80000000.00",
      "budget_utilized": "60000000.00",
      "utilization_rate": 75.0,
      "avg_progress": 72.3,
      "performance_rating": "good"
    }
  ]
}
```

**Endpoint 2: Geographic Coverage Map Data**
```
GET /api/v1/ocm/dashboard/geographic-coverage/
```

**Query Parameters:**
- `fiscal_year` (int, required)
- `level` (str): region, province, municipality, barangay

**Response:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[lng, lat], [lng, lat], ...]]
      },
      "properties": {
        "region_code": "IX",
        "region_name": "Zamboanga Peninsula",
        "ppa_count": 42,
        "budget_allocated": "120000000.00",
        "communities_served": 85,
        "coverage_intensity": "high"
      }
    }
  ]
}
```

**Endpoint 3: Beneficiary Overlap Report**
```
GET /api/v1/ocm/dashboard/beneficiary-overlaps/
```

**Query Parameters:**
- `fiscal_year` (int, required)
- `status` (str): detected, confirmed, resolved
- `mao_id` (uuid): Filter by MAO

**Response:**
```json
{
  "count": 15,
  "overlaps": [
    {
      "id": "uuid",
      "ppa_a": {
        "id": "uuid",
        "title": "Livelihood Training Program",
        "mao": "Ministry of Social Services"
      },
      "ppa_b": {
        "id": "uuid",
        "title": "Skills Development Initiative",
        "mao": "Ministry of Labor and Employment"
      },
      "overlap_type": "individual",
      "overlap_count": 35,
      "confidence_score": 0.92,
      "community": "Barangay Peaceful, Zamboanga City",
      "status": "detected",
      "detected_at": "2025-01-10T08:00:00Z"
    }
  ]
}
```

**Endpoint 4: Service Gap Analysis**
```
GET /api/v1/ocm/dashboard/service-gaps/
```

**Query Parameters:**
- `fiscal_year` (int, required)
- `gap_type` (str): geographic, sectoral, population

**Response:**
```json
{
  "underserved_communities": [
    {
      "community_id": "uuid",
      "community_name": "Barangay Remote, Maguindanao",
      "region": "XII",
      "ppa_count": 0,
      "last_service_date": "2023-06-15",
      "priority_score": 9.2,
      "recommended_sectors": ["health", "infrastructure"]
    }
  ],
  "underrepresented_sectors": [
    {
      "sector": "environment",
      "sector_display": "Environment & DRRM",
      "ppa_count": 8,
      "budget_allocated": "15000000.00",
      "percentage_of_total": 3.3,
      "target_percentage": 10.0,
      "gap": -6.7
    }
  ],
  "underallocated_maos": [
    {
      "mao_id": "uuid",
      "mao_name": "Ministry of Environment",
      "mao_acronym": "MoE",
      "ppa_count": 3,
      "budget_allocated": "8000000.00",
      "obc_allocation_percentage": 2.1,
      "capacity_score": 7.5,
      "recommendation": "Increase OBC allocation to 5%"
    }
  ]
}
```

**Endpoint 5: Real-Time Status Updates**
```
GET /api/v1/ocm/dashboard/real-time-updates/
```

**WebSocket Alternative:** `/ws/ocm/dashboard/`

**Response:**
```json
{
  "last_updated": "2025-01-15T14:30:00Z",
  "recent_updates": [
    {
      "timestamp": "2025-01-15T14:28:00Z",
      "type": "ppa_status_change",
      "ppa_id": "uuid",
      "ppa_title": "Health Services Expansion",
      "mao": "Ministry of Health",
      "old_status": "ongoing",
      "new_status": "completed",
      "updated_by": "Dr. Maria Santos"
    },
    {
      "timestamp": "2025-01-15T14:15:00Z",
      "type": "budget_disbursement",
      "ppa_id": "uuid",
      "amount": "2500000.00",
      "mao": "MSS",
      "description": "Q1 Livelihood Training disbursement"
    }
  ]
}
```

#### 3.3 Celery Background Tasks

**File:** `src/monitoring/tasks.py`

```python
from celery import shared_task

@shared_task(name='monitoring.generate_ocm_dashboard_snapshot')
def generate_ocm_dashboard_snapshot_task(fiscal_year, quarter=None):
    """
    Generate comprehensive OCM dashboard snapshot.

    Runs daily or on-demand.
    """
    from monitoring.services import OCMDashboardService

    service = OCMDashboardService()
    snapshot = service.generate_snapshot(fiscal_year, quarter)

    return {
        'snapshot_id': str(snapshot.id),
        'fiscal_year': fiscal_year,
        'quarter': quarter,
        'total_ppas': snapshot.total_ppas
    }


@shared_task(name='monitoring.detect_beneficiary_overlaps')
def detect_beneficiary_overlaps_task(fiscal_year):
    """
    Analyze PPAs for potential beneficiary overlaps.

    Runs weekly.
    """
    from monitoring.services import BeneficiaryOverlapService

    service = BeneficiaryOverlapService()
    overlaps = service.detect_overlaps(fiscal_year)

    return {
        'overlaps_detected': overlaps['count'],
        'high_confidence': overlaps['high_confidence_count']
    }


@shared_task(name='monitoring.analyze_service_gaps')
def analyze_service_gaps_task(fiscal_year):
    """
    Identify underserved communities and sectors.

    Runs weekly.
    """
    from monitoring.services import ServiceGapAnalysisService

    service = ServiceGapAnalysisService()
    gaps = service.analyze_gaps(fiscal_year)

    return {
        'underserved_communities': len(gaps['communities']),
        'underrepresented_sectors': len(gaps['sectors'])
    }
```

**Celery Beat Schedule:**

```python
# File: src/obc_management/celery.py

app.conf.beat_schedule.update({
    'generate-ocm-dashboard-daily': {
        'task': 'monitoring.generate_ocm_dashboard_snapshot',
        'schedule': crontab(hour=6, minute=0),  # Daily at 6:00 AM
        'kwargs': {'fiscal_year': 'current'}
    },
    'detect-beneficiary-overlaps-weekly': {
        'task': 'monitoring.detect_beneficiary_overlaps',
        'schedule': crontab(day_of_week=1, hour=7, minute=0),  # Mondays at 7:00 AM
        'kwargs': {'fiscal_year': 'current'}
    },
    'analyze-service-gaps-weekly': {
        'task': 'monitoring.analyze_service_gaps',
        'schedule': crontab(day_of_week=1, hour=8, minute=0),  # Mondays at 8:00 AM
        'kwargs': {'fiscal_year': 'current'}
    },
})
```

#### 3.4 UI/UX Implementation

**OCM Dashboard Homepage**

**Route:** `/ocm/dashboard/` (Requires OCM permissions)

**Wireframe Description:**

```
┌─────────────────────────────────────────────────────────────────┐
│ OCM Coordination Dashboard - FY 2025 Q1          [Export PDF]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ OVERVIEW METRICS                                                 │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│ │ 156 PPAs │ │ ₱450M    │ │ 45,230   │ │ 312      │           │
│ │ Active   │ │ Allocated│ │ Benefic. │ │ Communit.│           │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│                                                                  │
│ BUDGET UTILIZATION                        71.1% ██████░░░      │
│ PPA PROGRESS (Avg)                        68.5% █████░░░░      │
│                                                                  │
│ ┌─── BUDGET BY SECTOR ────┐ ┌─── GEOGRAPHIC COVERAGE ───┐     │
│ │ [Pie Chart]             │ │ [Interactive Map]          │     │
│ │ Economic: 33%           │ │ Region IX: High            │     │
│ │ Social: 28%             │ │ Region XII: Medium         │     │
│ │ Infrastructure: 22%     │ │ [Click regions for detail] │     │
│ └─────────────────────────┘ └────────────────────────────┘     │
│                                                                  │
│ ┌─── MAO PERFORMANCE ────────────────────────────────────────┐ │
│ │ MAO                     PPAs  Budget  Utilized  Progress  │ │
│ │ Ministry of Social Svc   28   ₱80M    75.0%     72.3%    │ │
│ │ Ministry of Health       24   ₱65M    68.0%     65.1%    │ │
│ │ Ministry of Agriculture  18   ₱45M    82.5%     78.9%    │ │
│ │ ...                                                        │ │
│ └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ⚠ ALERTS & INSIGHTS                                             │
│ • 15 potential beneficiary overlaps detected  [Review]          │
│ • 8 underserved communities identified         [View Report]    │
│ • Environment sector underallocated (3.3% vs 10% target)       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Interactive Geographic Coverage Map**

**Technology:** Leaflet.js + Choropleth Layer

**Features:**
- **Color-coded regions** by coverage intensity:
  - Dark green: High coverage (>30 PPAs)
  - Light green: Medium coverage (10-30 PPAs)
  - Yellow: Low coverage (1-9 PPAs)
  - Red: No coverage (0 PPAs)
- **Click region** → Popup with:
  - PPA count
  - Budget allocated
  - Communities served
  - Top 3 sectors
  - [View Details] button
- **Heat map toggle**: Switch between PPA count, budget, beneficiaries

**Beneficiary Overlap Review Interface**

**Route:** `/ocm/dashboard/overlaps/`

**Features:**
- Table of detected overlaps sorted by confidence score
- Side-by-side PPA comparison
- Community beneficiary list comparison
- Action buttons: Confirm, False Positive, Resolve
- Resolution workflow: Coordinate with MAOs, merge programs, or split beneficiaries

**Service Gap Analysis Report**

**Route:** `/ocm/dashboard/gaps/`

**Sections:**
1. **Underserved Communities** (map + table)
2. **Underrepresented Sectors** (bar chart + recommendations)
3. **Underallocated MAOs** (performance vs. capacity analysis)
4. **Actionable Recommendations** (AI-generated suggestions)

**HTMX Interactions:**
- **Filter Dashboard**: `hx-get="/api/v1/ocm/dashboard/overview/?fiscal_year={year}&quarter={q}"` → Update all cards
- **Map Region Click**: `hx-get="/api/v1/ocm/dashboard/regional-detail/{region_id}/"` → Load detail modal
- **Overlap Review**: `hx-post="/api/v1/ocm/dashboard/beneficiary-overlaps/{id}/confirm/"` → Update status badge
- **Export PDF**: Generate PDF report with current filter state

#### 3.5 Integration Points

**With Existing Models:**

1. **MonitoringEntry** → Source of all PPA data
2. **Organization** (type='bmoa') → MAO performance metrics
3. **OBCCommunity** → Geographic coverage and gap analysis
4. **MonitoringEntryFunding** → Budget utilization calculations
5. **Region, Province, Municipality, Barangay** → Geographic hierarchy for mapping

**With Analytics Services:**

```python
# File: src/monitoring/services/ocm_dashboard_service.py

class OCMDashboardService:
    """Service for OCM dashboard data aggregation."""

    def generate_snapshot(self, fiscal_year, quarter=None):
        """Generate comprehensive dashboard snapshot."""
        pass

    def calculate_sector_breakdown(self, fiscal_year):
        """Calculate budget and PPA count per sector."""
        pass

    def calculate_mao_performance(self, fiscal_year):
        """Calculate performance metrics per MAO."""
        pass

    def calculate_regional_coverage(self, fiscal_year):
        """Calculate geographic coverage intensity."""
        pass
```

#### 3.6 Testing Requirements

**Unit Tests:**
- Test snapshot generation logic
- Test overlap detection algorithm
- Test gap analysis calculations
- Test performance metric calculations

**Integration Tests:**
- Test dashboard API response structure
- Test real-time update WebSocket
- Test PDF export generation
- Test map data GeoJSON output

**End-to-End Tests:**
1. OCM user logs in
2. Dashboard loads with current fiscal year data
3. User filters by Q1
4. User clicks Region IX on map
5. Regional detail modal loads
6. User reviews beneficiary overlap
7. User confirms overlap and adds resolution notes
8. User exports PDF report

#### 3.7 Acceptance Criteria

✅ Dashboard aggregates data from all 44 MAOs in real-time
✅ Geographic heat map visualizes service distribution by region/province
✅ Beneficiary overlap detection achieves >85% accuracy
✅ Service gap analysis identifies communities with <2 PPAs/year
✅ MAO performance comparison includes utilization rate and progress
✅ Dashboard loads in <3 seconds (with caching)
✅ PDF export generates comprehensive report with all charts
✅ Real-time updates reflect PPA status changes within 5 minutes
✅ Mobile-responsive interface for OCM executives on tablets
✅ Role-based access control (OCM Executive, OOBC Executive only)

---

## IMPLEMENTATION ROADMAP

### Phase 1: Foundation (Priority: CRITICAL)
- ✅ Create database migrations for all new models
- ✅ Set up Celery tasks and beat schedules
- ✅ Configure permissions and role-based access
- ✅ Create base API serializers

### Phase 2: Enhancement 1 - Quarterly Meetings (Priority: HIGH)
- ✅ Implement `QuarterlyMeetingSeries` model and admin
- ✅ Build meeting generation service
- ✅ Create reminder notification system
- ✅ Develop meeting dashboard UI
- ✅ Test automated reminders

### Phase 3: Enhancement 2 - Service Catalog (Priority: HIGH)
- ✅ Implement `ServiceCatalogEntry` model
- ✅ Build public service catalog frontend
- ✅ Create application submission workflow
- ✅ Implement document upload system
- ✅ Test end-to-end application flow

### Phase 4: Enhancement 3 - OCM Dashboard (Priority: HIGH)
- ✅ Implement snapshot generation service
- ✅ Build overlap detection algorithm
- ✅ Create gap analysis service
- ✅ Develop interactive dashboard UI
- ✅ Implement geographic heat map
- ✅ Test dashboard performance

### Phase 5: Integration & Testing (Priority: MEDIUM)
- ✅ Integration testing across all three enhancements
- ✅ Performance optimization and caching
- ✅ Security audit and penetration testing
- ✅ Accessibility compliance verification (WCAG 2.1 AA)
- ✅ User acceptance testing with OOBC staff

### Phase 6: Deployment & Training (Priority: MEDIUM)
- ✅ Staging environment deployment
- ✅ Production deployment
- ✅ User training sessions
- ✅ Documentation updates
- ✅ Monitoring and support

---

## CROSS-CUTTING CONCERNS

### Security Requirements

**Authentication & Authorization:**
- All admin endpoints require authentication
- Public service catalog is read-only without authentication
- OCM dashboard requires specific user type (`cm_office`)
- Row-level security for MAO data isolation

**Data Privacy:**
- Beneficiary data anonymized in public views
- PII fields encrypted at rest
- Audit logging for all sensitive operations
- Data Privacy Act 2012 compliance

**Input Validation:**
- All user inputs sanitized (XSS prevention)
- File upload virus scanning
- SQL injection prevention (parameterized queries)
- CSRF token validation

### Performance Requirements

**Response Times:**
- Dashboard page load: <3 seconds
- API endpoints: <500ms (95th percentile)
- Search results: <1 second
- Geographic map rendering: <2 seconds

**Caching Strategy:**
- Dashboard snapshot: Redis cache, 15-minute TTL
- Service catalog list: 5-minute TTL
- Geographic map data: 30-minute TTL
- Database query optimization (indexes, select_related)

**Scalability:**
- Support 100+ concurrent users
- Handle 10,000+ PPAs in system
- Process 1,000+ service requests/month
- Generate reports for 44 MAOs simultaneously

### Accessibility Requirements (WCAG 2.1 AA)

- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **Screen Reader Support**: Semantic HTML, ARIA labels
- **Color Contrast**: 4.5:1 minimum contrast ratio
- **Touch Targets**: Minimum 48x48px on mobile
- **Responsive Design**: Mobile-first, works on 320px width
- **Form Labels**: All inputs have explicit labels
- **Error Messages**: Clear, actionable error messages

### Monitoring & Observability

**Application Monitoring:**
- Celery task success/failure rates
- API endpoint response times
- Error rates and exception tracking
- User session analytics

**Business Metrics:**
- Quarterly meeting completion rate
- Service request conversion rate
- Dashboard usage by OCM users
- Beneficiary overlap resolution time

**Alerting:**
- Failed Celery tasks (email alert)
- API error rate >5% (Slack alert)
- Dashboard load time >5s (monitoring dashboard)

---

## DEPLOYMENT CHECKLIST

### Pre-Deployment

- [ ] All database migrations tested in staging
- [ ] Celery workers and beat scheduler configured
- [ ] Redis cache configured and tested
- [ ] Static files collected and uploaded to CDN
- [ ] Environment variables configured (SECRET_KEY, EMAIL settings)
- [ ] Database backups automated
- [ ] SSL certificates configured

### Deployment Steps

1. Run database migrations: `python manage.py migrate`
2. Create initial QuarterlyMeetingSeries for FY 2025
3. Generate test OCM dashboard snapshot
4. Schedule Celery beat tasks
5. Restart Celery workers
6. Clear Redis cache
7. Collect static files: `python manage.py collectstatic`
8. Run smoke tests on production
9. Enable monitoring alerts

### Post-Deployment

- [ ] Verify quarterly meeting generation
- [ ] Test public service catalog accessibility
- [ ] Verify OCM dashboard loads correctly
- [ ] Check Celery task execution logs
- [ ] Monitor error rates for 24 hours
- [ ] User training sessions scheduled
- [ ] Documentation updated in wiki

---

## SUCCESS METRICS

### Enhancement 1: Quarterly Meetings
- **Target:** 100% of MAOs receive automated meeting invitations
- **Metric:** Reminder delivery success rate >95%
- **Target:** Meeting completion rate >80% per quarter
- **Metric:** Avg. time to record minutes <48 hours

### Enhancement 2: Service Catalog
- **Target:** 50+ services published within 3 months
- **Metric:** Service request submission rate >100/month
- **Target:** Application conversion rate >60%
- **Metric:** Avg. time to review requests <7 days

### Enhancement 3: OCM Dashboard
- **Target:** OCM executives access dashboard weekly
- **Metric:** Dashboard load time <3 seconds
- **Target:** Overlap detection accuracy >85%
- **Metric:** Service gap reports generated monthly

---

## DOCUMENTATION REQUIREMENTS

### Technical Documentation
- API endpoint documentation (OpenAPI/Swagger)
- Database schema diagrams (ERD)
- Celery task documentation
- Deployment guide

### User Documentation
- Admin guide: Managing quarterly meetings
- Public guide: Applying for services
- OCM guide: Using the coordination dashboard
- FAQ and troubleshooting

### Training Materials
- Video tutorials (screen recordings)
- Step-by-step guides with screenshots
- Webinar presentations
- Quick reference cards

---

**Document Status:** ✅ READY FOR IMPLEMENTATION
**Prepared by:** AI Implementation Planning Agent
**Review Date:** 2025-01-15
**Approval:** Pending OOBC Executive Review

**Next Steps:**
1. Review and approve implementation plan
2. Assign development team
3. Set sprint schedule
4. Begin Phase 1 foundation work
