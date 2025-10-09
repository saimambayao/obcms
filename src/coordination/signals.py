"""Signal handlers for coordination app.

Implements:
- Auto-registration of User accounts from OrganizationContact creation
- Welcome email with secure credentials to new MOA staff

Note: Legacy Event and ProjectWorkflow signals have been removed.
These models have been migrated to WorkItem.

For WorkItem signals, see: common/signals/workitem_sync.py
"""
import logging
import secrets
import string
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from coordination.models import OrganizationContact

logger = logging.getLogger(__name__)
User = get_user_model()


def _generate_secure_password():
    """
    Generate a cryptographically secure password.

    Requirements:
    - Minimum 12 characters
    - Contains uppercase, lowercase, digit, and special character
    - Uses secrets module for cryptographic randomness

    Returns:
        str: Secure password meeting all complexity requirements
    """
    # Character sets for password generation
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special_chars = '!@#$%^&*'

    # Combine all character sets
    all_chars = uppercase + lowercase + digits + special_chars

    # Generate password until requirements are met
    max_attempts = 100
    for _ in range(max_attempts):
        # Generate 12-character password
        password = ''.join(secrets.choice(all_chars) for _ in range(12))

        # Verify complexity requirements
        has_upper = any(c in uppercase for c in password)
        has_lower = any(c in lowercase for c in password)
        has_digit = any(c in digits for c in password)
        has_special = any(c in special_chars for c in password)

        if has_upper and has_lower and has_digit and has_special:
            return password

    # Fallback: Force complexity by ensuring at least one of each type
    password_parts = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(special_chars),
    ]
    # Fill remaining 8 characters randomly
    password_parts.extend(secrets.choice(all_chars) for _ in range(8))
    # Shuffle to avoid predictable pattern
    secrets.SystemRandom().shuffle(password_parts)
    return ''.join(password_parts)


def _send_welcome_email(user, plain_password):
    """
    Send welcome email to newly registered MOA staff.

    Includes:
    - Login credentials
    - Login URL
    - Password reset link
    - Security best practices

    Args:
        user: User instance
        plain_password: Plain-text password (only available during creation)
    """
    try:
        # Construct URLs (use settings.SITE_URL if available)
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        login_url = f"{site_url}{reverse('common:login')}"
        # Use admin password reset if available, otherwise use direct path
        try:
            password_reset_url = f"{site_url}{reverse('admin:password_change')}"
        except Exception:
            password_reset_url = f"{site_url}/admin/password_change/"

        # Email subject
        subject = 'Welcome to OBCMS - MOA Staff Access'

        # Email body
        message = f"""Dear {user.get_full_name()},

Welcome to the Office for Other Bangsamoro Communities Management System (OBCMS)!

Your organization has been registered as a stakeholder partner, and your account has been created automatically.

LOGIN CREDENTIALS:
------------------
Username: {user.username}
Email: {user.email}
Password: {plain_password}

Organization: {user.organization}
Position: {user.position}
User Type: {user.get_user_type_display()}

LOGIN URL:
----------
{login_url}

SECURITY RECOMMENDATIONS:
-------------------------
1. Change your password immediately after first login
2. Do not share your credentials with anyone
3. Use the password reset link if you forget your password: {password_reset_url}

ACCOUNT STATUS:
---------------
Your account has been automatically approved and is ready to use.

If you have any questions or need assistance, please contact the OOBC Office.

Best regards,
OOBC Management System
"""

        # Send email (fail_silently=True to prevent disrupting contact creation)
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,  # Don't raise exception if email fails
        )

        logger.info(f"Welcome email sent to {user.email} for organization contact registration")

    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        # Don't raise - email failure shouldn't prevent user creation


@receiver(post_save, sender=OrganizationContact)
def create_user_from_contact(sender, instance, created, **kwargs):
    """
    Automatically create User account when OrganizationContact is created.

    Workflow:
    1. Check if contact has email
    2. Check if user already exists with that email
    3. Determine user_type from organization.organization_type
    4. Generate secure password
    5. Create user with auto-approval
    6. Send welcome email with credentials

    User Type Mapping:
    - bmoa → bmoa
    - lgu → lgu
    - nga, ngo, private → nga
    - (default) → nga

    Args:
        sender: OrganizationContact model class
        instance: OrganizationContact instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional signal arguments
    """
    # Only process newly created contacts
    if not created:
        return

    # Must have email to create user account
    if not instance.email:
        logger.info(f"Skipping user creation for contact {instance.id} - no email provided")
        return

    # Check if user already exists with this email
    if User.objects.filter(email=instance.email).exists():
        logger.info(f"User already exists with email {instance.email} - skipping creation")
        return

    try:
        # Determine user type from organization type
        org = instance.organization
        user_type_mapping = {
            'bmoa': 'bmoa',
            'lgu': 'lgu',
            'nga': 'nga',
            'ngo': 'nga',
            'private': 'nga',
        }
        user_type = user_type_mapping.get(org.organization_type, 'nga')

        # Generate username from email (handle duplicates with counter)
        base_username = instance.email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # Generate secure password
        plain_password = _generate_secure_password()

        # Create user account
        user = User.objects.create(
            username=username,
            email=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            user_type=user_type,
            organization=org.name,
            position=instance.position,
            contact_number=instance.phone,
            is_approved=True,  # Auto-approved for MOA staff
            is_active=True,
        )

        # Set password (hashed)
        user.set_password(plain_password)
        user.save()

        logger.info(
            f"Created user {user.username} ({user.email}) from organization contact "
            f"{instance.id} - Organization: {org.name}, Type: {user_type}"
        )

        # Send welcome email with credentials
        _send_welcome_email(user, plain_password)

    except Exception as e:
        logger.error(
            f"Failed to create user from organization contact {instance.id}: {str(e)}",
            exc_info=True
        )
        # Don't raise - user creation failure shouldn't prevent contact save


# All legacy signals removed - WorkItem handles events via its own signal system
