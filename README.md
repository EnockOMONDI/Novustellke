# Novustell Travel - Tours and Travel Management System

A comprehensive Django-based web application for managing travel packages, bookings, and email marketing campaigns for Novustell Travel.

## 🌟 Features

- **Travel Package Management** - Create and manage travel packages with detailed itineraries
- **Booking System** - Handle customer bookings with payment integration
- **Email Marketing System** - Professional email campaigns with Mailtrap HTTP API and Celery background processing
- **Admin Dashboard** - Comprehensive admin interface with Django Unfold
- **Responsive Design** - Mobile-first design with Bootstrap and custom styling
- **Image Management** - Uploadcare integration for efficient image handling

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL (for production) or SQLite (for development)
- Redis (for Celery background tasks)
- Mailtrap account for email sending

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Novustellke
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.development .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

## 📧 Email Marketing System

### Overview

The email marketing system provides professional email campaign management with the following features:

- **Mailtrap HTTP API Integration** - Reliable email delivery without SMTP issues
- **Celery Background Processing** - Asynchronous email sending for large campaigns
- **Rate Limiting** - Prevents email sending abuse and respects provider limits
- **Email Tracking** - Track email opens and clicks with unique tokens
- **Template Management** - Rich text email templates with variable substitution
- **Recipient Management** - Organize recipients into lists with subscription management
- **Campaign Analytics** - Track campaign performance and delivery statistics

### Architecture

```
Django Admin → Queue Task → Celery Worker → Mailtrap HTTP API → Recipients
     ↓              ↓            ↓              ↓
Database ← Email Logs ← Task Status ← API Response ← Delivery Status
```

### Key Components

#### 1. Mailtrap HTTP API Integration

**Replaced SMTP with HTTP API for reliability:**
- No connection timeouts or SMTP server issues
- Better error handling and delivery tracking
- Faster email sending with HTTP requests
- Production-ready email delivery

**Configuration:**
```python
# settings.py
MAILTRAP_API_TOKEN = 'd766975d57a7ef1acf2f750a36247a37'
```

#### 2. Celery Background Processing

**Asynchronous email sending:**
- Large campaigns don't block the web interface
- Retry logic for failed emails
- Progress tracking and status updates
- Scalable worker processes

**Key Tasks:**
- `send_campaign_emails_task()` - Process entire email campaigns
- `send_single_email_task()` - Send individual emails with retry logic
- `process_scheduled_campaigns_task()` - Handle scheduled campaigns
- `cleanup_old_email_logs_task()` - Maintenance and cleanup

#### 3. Redis Configuration

**Using Upstash Redis for production:**
- Celery broker and result backend
- Django cache backend for rate limiting
- SSL/TLS encrypted connections
- Managed Redis service for reliability

#### 4. Rate Limiting

**Prevents abuse and respects email provider limits:**
- Production: 60 emails/minute, 1000 emails/hour
- Development: 10 emails/minute, 100 emails/hour
- Redis-based counters with automatic expiration
- Per-user rate limiting

### Development Setup

#### 1. Install Dependencies

```bash
pip install celery>=5.3.0 redis>=4.5.0 django-redis>=6.0.0 bleach>=6.0.0 django-ratelimit>=4.1.0 flower>=2.0.0
```

#### 2. Environment Variables

Add to your `.env.development`:
```bash
# Celery Configuration
CELERY_BROKER_URL=rediss://default:AWAXAAIncDI4ZTNlNjRkMDEyOWI0OTdkODI4Nzk0ZTZlMTc1ZmQxOXAyMjQ1OTk@popular-condor-24599.upstash.io:6379
CELERY_RESULT_BACKEND=rediss://default:AWAXAAIncDI4ZTNlNjRkMDEyOWI0OTdkODI4Nzk0ZTZlMTc1ZmQxOXAyMjQ1OTk@popular-condor-24599.upstash.io:6379

# Email Rate Limiting
EMAIL_RATE_LIMIT_PER_MINUTE=10
EMAIL_RATE_LIMIT_PER_HOUR=100

# Mailtrap HTTP API
MAILTRAP_API_TOKEN=d766975d57a7ef1acf2f750a36247a37
DEFAULT_FROM_EMAIL="Novustell Travel <info@novustelltravel.com>"
```

#### 3. Run Celery Services

**Terminal 1: Django Development Server**
```bash
python manage.py runserver
```

**Terminal 2: Celery Worker**
```bash
celery -A tours_travels worker --loglevel=info
```

**Terminal 3: Celery Beat (for scheduled campaigns)**
```bash
celery -A tours_travels beat --loglevel=info
```

**Terminal 4: Flower Monitoring (optional)**
```bash
celery -A tours_travels flower
# Visit: http://localhost:5555
```

### Testing Email Campaigns

#### 1. Create Test Campaign

1. Go to Django Admin → Email Marketing → Email Campaigns
2. Create a new campaign with test template and recipient list
3. Set status to "draft"
4. Click "Send selected campaigns" action

#### 2. Monitor Progress

- **Django Admin**: Check campaign status and email counts
- **Flower Dashboard**: Real-time task monitoring at http://localhost:5555
- **Email Logs**: View detailed sending logs in admin

#### 3. Test Email Delivery

```python
# Django shell test
python manage.py shell

from email_marketing.models import EmailCampaign
from email_marketing.tasks import send_campaign_emails_task

# Send test campaign
campaign = EmailCampaign.objects.get(name='Test Campaign')
task = send_campaign_emails_task.delay(campaign.id)
print(f"Task ID: {task.id}")
```

### Production Deployment (Render.com)

#### 1. Environment Variables

Set in Render dashboard:
```bash
CELERY_BROKER_URL=rediss://default:AWAXAAIncDI4ZTNlNjRkMDEyOWI0OTdkODI4Nzk0ZTZlMTc1ZmQxOXAyMjQ1OTk@popular-condor-24599.upstash.io:6379
CELERY_RESULT_BACKEND=rediss://default:AWAXAAIncDI4ZTNlNjRkMDEyOWI0OTdkODI4Nzk0ZTZlMTc1ZmQxOXAyMjQ1OTk@popular-condor-24599.upstash.io:6379
EMAIL_RATE_LIMIT_PER_MINUTE=60
EMAIL_RATE_LIMIT_PER_HOUR=1000
MAILTRAP_API_TOKEN=d766975d57a7ef1acf2f750a36247a37
```

#### 2. Services Configuration

The `render.yaml` includes three services:

**Web Service** - Django application
```yaml
- type: web
  name: novustellke
  startCommand: gunicorn tours_travels.wsgi:application
```

**Celery Worker** - Email processing
```yaml
- type: worker
  name: novustell-celery-worker
  startCommand: celery -A tours_travels worker --loglevel=info --concurrency=2
```

**Celery Beat** - Scheduled campaigns
```yaml
- type: worker
  name: novustell-celery-beat
  startCommand: celery -A tours_travels beat --loglevel=info
```

#### 3. Deployment Steps

1. **Push to GitHub** with updated `render.yaml`
2. **Deploy services** in Render dashboard
3. **Set environment variables** in each service
4. **Run migrations** in web service console:
   ```bash
   python manage.py migrate
   ```
5. **Test email campaigns** through admin interface

### Database Models

#### EmailCampaign (Enhanced)

New fields for task management:
```python
celery_task_id = models.CharField(max_length=255, blank=True, null=True)
task_status = models.CharField(max_length=20, default='pending')
emails_sent_count = models.IntegerField(default=0)
emails_failed_count = models.IntegerField(default=0)
started_at = models.DateTimeField(null=True, blank=True)
completed_at = models.DateTimeField(null=True, blank=True)
```

#### EmailLog

Tracks individual email sending:
```python
campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE)
recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
status = models.CharField(max_length=20)  # sent, failed, bounced
tracking_token = models.UUIDField(default=uuid.uuid4, unique=True)
sent_at = models.DateTimeField(auto_now_add=True)
opened_at = models.DateTimeField(null=True, blank=True)
```

### Troubleshooting

#### Common Issues

**1. Celery Worker Not Starting**
```bash
# Check Redis connection
redis-cli -u $CELERY_BROKER_URL ping

# Check Celery configuration
python manage.py shell -c "from tours_travels.celery import app; print(app.conf.broker_url)"
```

**2. Emails Not Sending**
```bash
# Test Mailtrap API directly
python manage.py shell -c "
from users.tasks import send_email_via_mailtrap
result = send_email_via_mailtrap('Test', '<p>Test</p>', 'test@novustelltravel.com', ['your-email@example.com'])
print(f'Success: {result}')
"
```

**3. Rate Limiting Issues**
```bash
# Check Redis cache
python manage.py shell -c "
from django.core.cache import cache
print(cache.get('email_rate_minute_1', 'Not found'))
"
```

#### Monitoring

**Celery Tasks:**
- Use Flower dashboard for real-time monitoring
- Check Django admin for campaign status
- Monitor Redis for task queues

**Email Delivery:**
- Check Mailtrap dashboard for delivery statistics
- Monitor EmailLog model for detailed sending logs
- Set up alerts for failed campaigns

### Performance Optimization

#### Celery Configuration

```python
# tours_travels/celery.py
app.conf.update(
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_acks_late=True,          # Acknowledge after completion
    worker_max_tasks_per_child=1000,  # Restart workers periodically
    result_expires=3600,          # Clean up results after 1 hour
)
```

#### Email Sending Optimization

- **Batch Processing**: Send emails in batches to respect rate limits
- **Retry Logic**: Automatic retry for failed emails with exponential backoff
- **Connection Pooling**: Reuse HTTP connections for Mailtrap API
- **Error Handling**: Graceful handling of API errors and timeouts

### Security Considerations

#### Email Content Validation

```python
# Implemented with bleach package
import bleach

def sanitize_html_content(html_content):
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'a', 'img']
    allowed_attributes = {'a': ['href'], 'img': ['src', 'alt']}
    return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attributes)
```

#### Rate Limiting

- Per-user rate limiting prevents abuse
- Redis-based counters with automatic expiration
- Configurable limits for different environments

#### API Security

- Mailtrap API token stored in environment variables
- SSL/TLS encryption for all Redis connections
- Secure handling of recipient email addresses

## 🛠️ Technology Stack

### Backend
- **Django 5.0.14** - Web framework
- **PostgreSQL** - Production database
- **SQLite** - Development database
- **Celery 5.3.0** - Background task processing
- **Redis** - Message broker and cache
- **Mailtrap** - Email delivery service

### Frontend
- **Bootstrap 5** - CSS framework
- **JavaScript/jQuery** - Interactive features
- **FontAwesome** - Icons
- **Custom CSS** - Novustell branding

### Email Marketing
- **Mailtrap HTTP API** - Email delivery
- **Celery** - Asynchronous processing
- **Redis** - Task queue and rate limiting
- **django-ratelimit** - Rate limiting
- **bleach** - HTML sanitization

### Development Tools
- **Django Unfold** - Enhanced admin interface
- **django-ckeditor-5** - Rich text editing
- **Flower** - Celery monitoring
- **pyuploadcare** - Image management

### Deployment
- **Render.com** - Hosting platform
- **Gunicorn** - WSGI server
- **Upstash Redis** - Managed Redis service
- **NeonDB** - Managed PostgreSQL

## 📝 License

This project is proprietary software developed for Novustell Travel.

## 🤝 Support

For technical support or questions about the email marketing system:
- Email: info@novustelltravel.com
- Phone: +254701363551
- WhatsApp: +254701363551
