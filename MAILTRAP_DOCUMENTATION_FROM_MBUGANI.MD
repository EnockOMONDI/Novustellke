# 🚀 KIPEKEE EMAIL SYSTEM
## Synchronous Email Architecture Using Mailtrap HTTP API

**Version:** 1.0  
**Last Updated:** 2025-10-18  
**Project:** Mbugani Luxe Adventures  
**Purpose:** Production-ready synchronous email system for Django applications

---



---

## 📖 OVERVIEW

### What is Kipekee Email System?

**Kipekee** (Swahili for "unique/special") is a synchronous email architecture that:
- ✅ Sends emails **immediately** during HTTP request (no background workers)
- ✅ Uses **Mailtrap HTTP API** instead of SMTP
- ✅ Provides **instant feedback** to users on email delivery status
- ✅ Simplifies infrastructure to **single deployment** (Render.com)

### Trade-offs

---

## 🏗️ ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  User Submits    │
                    │  Form (Quote,    │
                    │  Newsletter, etc)│
                    └──────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO WEB APPLICATION                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  VIEW (users/views.py)                                     │ │
│  │  - Validate form data                                      │ │
│  │  - Save to database (QuoteRequest, etc.)                   │ │
│  │  - Call send_quote_request_emails(id) SYNCHRONOUSLY        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  TASKS (users/tasks.py)                                    │ │
│  │  - send_quote_request_emails(quote_id)                     │ │
│  │  - Fetch data from database                                │ │
│  │  - Render HTML email templates                             │ │
│  │  - Call send_email_via_mailtrap()                          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  MAILTRAP CLIENT (users/tasks.py)                          │ │
│  │  - Initialize MailtrapClient(token=MAILTRAP_API_TOKEN)     │ │
│  │  - Create Mail object with sender, recipients, HTML        │ │
│  │  - client.send(mail) → HTTP POST to Mailtrap API           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP POST
┌─────────────────────────────────────────────────────────────────┐
│                    MAILTRAP API                                  │
│  Endpoint: https://send.api.mailtrap.io/api/send                │
│  - Receives email via HTTP API                                  │
│  - Validates sender domain                                      │
│  - Queues for delivery                                          │
│  - Returns success/failure response                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EMAIL DELIVERY                                │
│  - Mailtrap delivers to recipient inbox                         │
│  - User receives email                                          │
│  - Admin receives notification                                  │
└─────────────────────────────────────────────────────────────────┘

TIMING: Total process takes 1-4 seconds (user waits during form submission)
```

---

## 🔧 KEY COMPONENTS

### File Structure

```
your_project/
├── users/
│   ├── views.py              # Form handling & email triggering
│   ├── tasks.py              # Email sending functions
│   ├── models.py             # QuoteRequest, JobApplication, etc.
│   └── templates/
│       └── users/
│           └── emails/       # Email HTML templates
│               ├── quote_request_admin.html
│               ├── quote_request_user.html
│               ├── job_application_admin.html
│               └── newsletter_welcome.html
├── tours_travels/
│   ├── settings.py           # Base settings (development)
│   ├── settings_prod.py      # Production settings (Mailtrap config)
│   └── wsgi.py
├── requirements.txt          # Python dependencies
├── render.yaml               # Render.com deployment config

```

### Dependencies

```txt
# requirements.txt
Django>=5.0.0
mailtrap>=2.0.0              # Mailtrap HTTP API SDK
gunicorn>=21.0.0             # WSGI server for production
psycopg2-binary>=2.9.0       # PostgreSQL adapter
python-decouple>=3.8         # Environment variable management
```

### Core Files

| File | Purpose | Lines of Code |
|------|---------|---------------|
| `users/tasks.py` | Email sending logic | ~440 lines |
| `users/views.py` | Form handling & email triggering | ~1300 lines |
| `tours_travels/settings_prod.py` | Production configuration | ~260 lines |
| `render.yaml` | Deployment configuration | ~210 lines |

---



### Current Architecture (Sync with Mailtrap HTTP API)

```
User → Django Web App → Mailtrap HTTP API → Email
       (Render.com)
       
- 1 deployment
- Simple infrastructure
- No background workers
- Synchronous email sending
- Slower form response (1-4s)
- No automatic retries
```

### Migration Rationale


## ⚙️ CONFIGURATION STEPS

### Step 1: Install Dependencies

```bash
pip install mailtrap>=2.0.0
pip install Django>=5.0.0
pip install gunicorn>=21.0.0
```

Update `requirements.txt`:
```txt
mailtrap>=2.0.0
Django>=5.0.0
gunicorn>=21.0.0
psycopg2-binary>=2.9.0
```

### Step 2: Set Up Mailtrap Account

1. **Create Mailtrap Account**
   - Go to https://mailtrap.io/signup
   - Choose **Email Sending** (not Email Testing)

2. **Add Your Domain**
   - Go to https://mailtrap.io/sending/domains
   - Click "Add Domain"
   - Enter your domain (e.g., `novustelltravel.com`)

3. **Verify Domain**
   - Add DNS records provided by Mailtrap:
     ```
     TXT record: mailtrap-verify=xxxxx
     DKIM record: mailtrap._domainkey
     SPF record: v=spf1 include:mailtrap.io ~all
     ```
   - Wait for verification (up to 48 hours)

4. **Get API Token**
   - Go to https://mailtrap.io/api-tokens
   - Copy your **Email Sending API Token**
   - Format: 32-character hexadecimal string
   - Example: `956b51c090fc5c1320bca0c26a394fd5`

### Step 3: Configure Django Settings

Create/update `tours_travels/settings_prod.py`:

```python
"""
Production settings with Mailtrap HTTP API
"""
import os
from .settings import *

# Force production environment
os.environ['DJANGO_ENV'] = 'production'
DEBUG = False

# Mailtrap HTTP API Configuration
MAILTRAP_API_TOKEN = os.getenv('MAILTRAP_API_TOKEN', 'your-token-here')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Your App <info@yourdomain.com>')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'info@yourdomain.com')
JOBS_EMAIL = os.getenv('JOBS_EMAIL', 'careers@yourdomain.com')
NEWSLETTER_EMAIL = os.getenv('NEWSLETTER_EMAIL', 'news@yourdomain.com')

# Database configuration (example with Supabase)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': '6543',  # Connection pooling port
        'OPTIONS': {'sslmode': 'require'},
        'CONN_MAX_AGE': 600,
        'CONN_HEALTH_CHECKS': True,
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Step 4: Create Email Sending Functions

Create `users/tasks.py`:

```python
"""
Email sending functions using Mailtrap HTTP API
Synchronous email delivery for production
"""
import logging
from mailtrap import Mail, Address, MailtrapClient
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


def send_email_via_mailtrap(subject, html_message, from_email, recipient_list):
    """
    Send email using Mailtrap HTTP API

    Args:
        subject (str): Email subject
        html_message (str): HTML message content
        from_email (str): From email (e.g., "App Name <info@domain.com>")
        recipient_list (list): List of recipient email addresses

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        logger.info(f"Sending email via Mailtrap API: subject='{subject}', recipients={recipient_list}")

        # Initialize Mailtrap client
        client = MailtrapClient(token=settings.MAILTRAP_API_TOKEN)

        # Parse from_email to extract name and email
        if '<' in from_email and '>' in from_email:
            from_name = from_email.split('<')[0].strip()
            from_email_addr = from_email.split('<')[1].split('>')[0].strip()
        else:
            from_name = "Your App Name"
            from_email_addr = from_email.strip()

        # Create mail object
        mail = Mail(
            sender=Address(email=from_email_addr, name=from_name),
            to=[Address(email=email.strip()) for email in recipient_list],
            subject=subject,
            html=html_message,
        )

        # Send email
        response = client.send(mail)

        logger.info(f"Email sent successfully via Mailtrap API: {response}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email via Mailtrap API: {e}")
        return False


def send_quote_request_emails(quote_request_id):
    """
    Send email notifications for quote requests

    Args:
        quote_request_id (int): ID of the QuoteRequest object

    Returns:
        dict: Status of email sending with details
    """
    try:
        from users.models import QuoteRequest

        # Get the quote request object
        try:
            quote_request = QuoteRequest.objects.get(id=quote_request_id)
        except QuoteRequest.DoesNotExist:
            error_msg = f"QuoteRequest with ID {quote_request_id} not found"
            logger.error(error_msg)
            return {'success': False, 'error': error_msg}

        logger.info(f"Sending emails for quote request {quote_request_id}")

        # Track email sending status
        admin_sent = False
        user_sent = False

        # Send admin notification email
        try:
            admin_subject = f'New Quote Request from {quote_request.full_name}'
            admin_message_html = render_to_string('users/emails/quote_request_admin.html', {
                'quote_request': quote_request
            })

            admin_sent = send_email_via_mailtrap(
                subject=admin_subject,
                html_message=admin_message_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
            )

            if admin_sent:
                logger.info(f"Admin notification sent for quote request {quote_request_id}")
            else:
                logger.error(f"Failed to send admin email for quote request {quote_request_id}")

        except Exception as e:
            logger.error(f"Failed to send admin email for quote request {quote_request_id}: {e}")

        # Send user confirmation email
        try:
            user_subject = 'Quote Request Received - Your App Name'
            user_message_html = render_to_string('users/emails/quote_request_user.html', {
                'quote_request': quote_request
            })

            user_sent = send_email_via_mailtrap(
                subject=user_subject,
                html_message=user_message_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[quote_request.email],
            )

            if user_sent:
                logger.info(f"User confirmation sent for quote request {quote_request_id}")
            else:
                logger.error(f"Failed to send user email for quote request {quote_request_id}")

        except Exception as e:
            logger.error(f"Failed to send user email for quote request {quote_request_id}: {e}")

        # Update email status in database
        quote_request.admin_email_sent = admin_sent
        quote_request.user_email_sent = user_sent
        quote_request.save()

        # Return status
        success = admin_sent and user_sent
        if not success:
            logger.warning(f"Some emails failed for quote request {quote_request_id}: admin={admin_sent}, user={user_sent}")

        return {
            'success': success,
            'admin_email_sent': admin_sent,
            'user_email_sent': user_sent,
        }

    except Exception as e:
        error_msg = f"Unexpected error sending emails for quote request {quote_request_id}: {e}"
        logger.error(error_msg)
        return {'success': False, 'error': error_msg}
```

### Step 5: Integrate with Views

Update `users/views.py`:

```python
def quote_request_view(request):
    """
    Handle quote request form submission
    """
    import logging
    logger = logging.getLogger(__name__)

    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            # Save quote request to database
            quote_request = form.save()
            logger.info(f"Quote request created: ID {quote_request.id} for {quote_request.full_name}")

            # Send email notifications SYNCHRONOUSLY
            try:
                from users.tasks import send_quote_request_emails

                # This call blocks until emails are sent (1-4 seconds)
                result = send_quote_request_emails(quote_request.id)

                if result.get('success'):
                    logger.info(f"Quote request emails sent successfully: quote_id={quote_request.id}")
                else:
                    logger.warning(f"Some quote request emails failed: quote_id={quote_request.id}")

            except Exception as email_error:
                logger.error(f"Failed to send email for quote {quote_request.id}: {email_error}")
                # Don't fail the entire request if email sending fails

            # Show success message
            messages.success(request, "Thank you! Your quote request has been submitted successfully.")
            logger.info(f"Quote request {quote_request.id} submitted successfully")

            # Redirect to success page
            return redirect('quote_success')
    else:
        form = QuoteRequestForm()

    return render(request, 'users/quote_request.html', {'form': form})
```

### Step 6: Configure Render Deployment

Create/update `render.yaml`: