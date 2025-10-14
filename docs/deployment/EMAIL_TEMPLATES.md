# Pilot Email Templates

Pilot welcome emails follow BMMS branding and accessibility standards. Templates reside
in `src/templates/emails/` and are rendered by `organizations.tasks.send_pilot_welcome_email`.

## Files
- `pilot_welcome.html` – Rich HTML email with CTA button
- `pilot_welcome.txt` – Plain text fallback for accessibility/compliance

## Placeholders
- `{{ user.get_full_name }}` – recipient name
- `{{ raw_password }}` – temporary password generated during creation
- `{{ login_url }}` – staging login URL from settings
- `{{ support_email }}` – support desk contact (defaults to `PILOT_SUPPORT_EMAIL`)

## Preview
Render templates locally via Django shell:
```python
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
User = get_user_model()
user = User(username="demo", first_name="Demo", last_name="User", email="demo@example.com")
render_to_string("emails/pilot_welcome.html", {
    "user": user,
    "raw_password": "TempPass123!",
    "login_url": "https://staging.bmms.gov.ph/login/",
    "support_email": "support@staging.bmms.gov.ph",
})
```

## Delivery
Messages are sent asynchronously through Celery. Configure SMTP credentials in `.env`
and ensure `DEFAULT_FROM_EMAIL` reflects the support desk identity.
