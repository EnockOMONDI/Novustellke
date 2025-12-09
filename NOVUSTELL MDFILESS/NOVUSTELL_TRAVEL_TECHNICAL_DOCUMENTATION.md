# Novustell Travel - Comprehensive Technical Documentation

## Table of Contents
1. [Project Architecture Overview](#project-architecture-overview)
2. [Blog App](#blog-app)
3. [Contact System](#contact-system)
4. [Settings Configuration](#settings-configuration)
5. [Environment Files](#environment-files)
6. [Deployment Configuration](#deployment-configuration)
7. [Dependencies and Package Management](#dependencies-and-package-management)
8. [Key Code Snippets](#key-code-snippets)
9. [Migration and Update Guide](#migration-and-update-guide)

---

## 1. Project Architecture Overview

### Django Framework Details
- **Django Version**: 5.0.14
- **Admin Interface**: Django Unfold (version 0.22+)
- **Rich Text Editor**: CKEditor 5 (django-ckeditor-5>=0.2.12)
- **Database**: NeonDB PostgreSQL (production) / PostgreSQL (development)
- **Deployment**: Render.com platform

### App Structure
```
novustellke/
├── tours_travels/          # Main project settings
├── adminside/             # Travel packages, destinations, bookings
├── users/                 # User management, forms, contact system
├── blog/                  # Blog posts, categories, comments
├── status/                # System status and health checks
└── email_marketing/       # Email campaigns (EXCLUDED FROM DOCS)
```

### Key Dependencies Between Apps
- **adminside** ↔ **users**: Package bookings, user profiles
- **blog** → **users**: Author relationships, user comments
- **users** → **adminside**: Contact forms reference packages/destinations
- **All apps** → **tours_travels**: Shared settings and configurations

### Database Setup
**Production (NeonDB PostgreSQL)**:
```python
DATABASES = {
    'default': dj_database_url.parse(
        os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}
```

**Development**:
```python
DATABASE_URL=postgresql://EnockOMONDI:iuXReO7TL0rs@ep-ancient-rice-27299843-pooler.eu-central-1.aws.neon.tech:5432/neondb?sslmode=require
```

---

## 2. Blog App

### Model Structure

#### Category Model (`blog/models.py`)
```python
class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = CKEditor5Field(config_name='default', blank=True, null=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
```

#### Post Model (`blog/models.py`)
```python
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    image = ImageField(blank=True, null=True, manual_crop="4:4")
    title = models.CharField(max_length=1000)
    slug = models.SlugField(max_length=1000, unique=True, blank=True)
    excerpt = CKEditor5Field(config_name='default', blank=True, null=True)
    content = CKEditor5Field(config_name='default')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = TaggableManager()
    status = models.CharField(choices=BLOG_PUBLISH_STATUS, max_length=100, default="in_review")
    featured = models.BooleanField(default=False)
    trending = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    pid = ShortUUIDField(length=10, max_length=25)
```

### URL Patterns (`blog/urls.py`)
```python
urlpatterns = [
    path('', views.blog_list, name="blog-list"),
    path('search/', views.blog_search, name="blog-search"),
    path('category/<slug:slug>/', views.category_detail, name="category-detail"),
    path('post/<slug:slug>/', views.blog_detail, name="blog-detail"),
    path('p/<str:pid>/', views.blog_detail_redirect, name="blog-detail-redirect"),
    path('rss/', views.blog_rss, name="blog-rss"),
    path('sitemap/', views.blog_sitemap, name="blog-sitemap"),
]
```

### Admin Interface Configuration (`blog/admin.py`)
```python
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'slug', 'status', 'category', 'user', 'featured', 'trending', 'views', 'date')
    list_editable = ['status', 'category', 'featured', 'trending']
    list_filter = ('category', 'status', 'featured', 'trending', 'date', 'updated')
    search_fields = ['title', 'content', 'excerpt', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'excerpt', 'category', 'tags', 'image')
        }),
        ('Content', {
            'fields': ('content',),
            'classes': ('wide',)
        }),
        ('Publishing', {
            'fields': ('status', 'featured', 'trending', 'user'),
            'classes': ('collapse',)
        }),
    )
```

### Rich Text Editor Integration
- **Editor**: CKEditor 5 via `django-ckeditor-5`
- **Fields**: `content` and `excerpt` fields use `CKEditor5Field`
- **Configuration**: Uses `config_name='default'` for consistent styling

---

## 3. Contact System

### Contact Form Models (`users/models.py`)

#### ContactInquiry Model
```python
class ContactInquiry(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    privacy_consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
```

#### Specialized Inquiry Models
```python
class MICEInquiry(models.Model):
    company_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    event_type = models.CharField(max_length=100)
    attendees = models.PositiveIntegerField()
    event_details = models.TextField()

class StudentTravelInquiry(models.Model):
    school_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    program_stage = models.CharField(max_length=100)
    number_of_students = models.PositiveIntegerField()
    travel_details = models.TextField()

class NGOTravelInquiry(models.Model):
    organization_name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    organization_type = models.CharField(max_length=100)
    travel_purpose = models.TextField()
    number_of_travelers = models.PositiveIntegerField()
    travel_details = models.TextField()
    sustainability_requirements = models.BooleanField(default=False)
```

### Contact Forms (`users/forms.py`)

#### Main Contact Form
```python
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ['full_name', 'email', 'phone', 'company', 'subject', 'message', 'privacy_consent']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['full_name'].widget.attrs.update({
            'class': 'form-control premium-input',
            'placeholder': 'Enter your full name',
            'required': True
        })
        
        self.fields['message'].widget.attrs.update({
            'class': 'form-control premium-input',
            'placeholder': 'Tell us about your travel requirements...',
            'rows': 6,
            'required': True
        })
```

### Email Notification Workflow
Contact form submissions trigger email notifications using the Mailtrap HTTP API:

1. **Admin Notification**: Sent to `info@novustelltravel.com`
2. **User Confirmation**: Sent to the form submitter
3. **Specialized Routing**:
   - MICE inquiries → `info@novustelltravel.com`
   - Job applications → `careers@novustelltravel.com` + `info@novustelltravel.com`
   - Newsletter → `news@novustelltravel.com`

---

## 4. Settings Configuration

### Development Settings (`tours_travels/settings.py`)
```python
INSTALLED_APPS = [
    'unfold',  # Django Unfold admin interface
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_ckeditor_5',  # CKEditor 5 for rich text editing
    'import_export',
    'adminside',
    'users',
    'blog',
    'status',
    'email_marketing',  # Email marketing campaigns
    'taggit',
    'django_ratelimit',  # Rate limiting
    'crispy_forms',
    'pyuploadcare.dj',
]

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'neondb'),
        'USER': os.getenv('DB_USER', 'EnockOMONDI'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'iuXReO7TL0rs'),
        'HOST': os.getenv('DB_HOST', 'ep-ancient-rice-27299843-pooler.eu-central-1.aws.neon.tech'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

### Production Settings (`tours_travels/settings_prod.py`)
```python
from .settings import *
import dj_database_url

DEBUG = False

# Production database - NeonDB PostgreSQL
DATABASES = {
    'default': dj_database_url.parse(
        os.getenv('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Mailtrap HTTP API configuration
MAILTRAP_API_TOKEN = os.getenv('MAILTRAP_API_TOKEN', 'd766975d57a7ef1acf2f750a36247a37')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Novustell Travel <info@novustelltravel.com>')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'info@novustelltravel.com')
JOBS_EMAIL = os.getenv('JOBS_EMAIL', 'careers@novustelltravel.com')
NEWSLETTER_EMAIL = os.getenv('NEWSLETTER_EMAIL', 'news@novustelltravel.com')

# Production security settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Key Differences Between Environments
| Setting | Development | Production |
|---------|-------------|------------|
| DEBUG | True | False |
| SSL Redirect | False | True |
| Database | Direct PostgreSQL | dj_database_url parsed |
| Email Backend | Mailtrap HTTP API | Mailtrap HTTP API |
| Static Files | Django dev server | WhiteNoise + compression |
| Security Headers | Relaxed | Strict HSTS, CSP |

---

## 5. Environment Files

### Development Environment (`.env`)
```bash
# Django Core Settings
DEBUG=True
SECRET_KEY=djngo-iiamysing30ochatachterxfoatensedonfgssooeyyspw--EDIGIQDFNNNWDEJJJWEDFRTCVF
ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://EnockOMONDI:iuXReO7TL0rs@ep-ancient-rice-27299843-pooler.eu-central-1.aws.neon.tech:5432/neondb?sslmode=require

# Email Configuration - Mailtrap HTTP API
EMAIL_HOST=live.smtp.mailtrap.io
EMAIL_HOST_USER=api
EMAIL_HOST_PASSWORD=d766975d57a7ef1acf2f750a36247a37
DEFAULT_FROM_EMAIL=Novustell Travel <info@novustelltravel.com>
ADMIN_EMAIL=info@novustelltravel.com
JOBS_EMAIL=careers@novustelltravel.com
NEWSLETTER_EMAIL=news@novustelltravel.com
MAILTRAP_API_TOKEN=d766975d57a7ef1acf2f750a36247a37

# Uploadcare Configuration
UPLOADCARE_PUBLIC_KEY=ee9d364d0155cae58db7
UPLOADCARE_SECRET_KEY=23d12b50d22b09097026

# Site Configuration
SITE_URL=http://127.0.0.1:8005
WHATSAPP_PHONE=+254701363551
TIME_ZONE=Africa/Nairobi
```

### Production Environment Variables (render.yaml)
```yaml
envVars:
  # Django Core
  - key: DJANGO_SETTINGS_MODULE
    value: tours_travels.settings_prod
  - key: SECRET_KEY
    generateValue: true
  - key: DEBUG
    value: False
  - key: ALLOWED_HOSTS
    value: novustelltravel.onrender.com,.onrender.com,novustelltravel.com,www.novustelltravel.com

  # Database
  - key: DATABASE_URL
    fromDatabase:
      name: novustell-db
      property: connectionString

  # Email Configuration
  - key: MAILTRAP_API_TOKEN
    value: d766975d57a7ef1acf2f750a36247a37
  - key: DEFAULT_FROM_EMAIL
    value: Novustell Travel <info@novustelltravel.com>
  - key: ADMIN_EMAIL
    value: info@novustelltravel.com
  - key: JOBS_EMAIL
    value: careers@novustelltravel.com
  - key: NEWSLETTER_EMAIL
    value: news@novustelltravel.com

  # Site Configuration
  - key: SITE_URL
    value: https://www.novustelltravel.com
  - key: WHATSAPP_PHONE
    value: +254701363551
  - key: TIME_ZONE
    value: Africa/Nairobi
```

---

## 6. Deployment Configuration (render.yaml)

### Web Service Configuration
```yaml
services:
  - type: web
    name: novustellke
    env: python
    region: oregon
    plan: starter
    branch: novustell4
    buildCommand: |
      echo "🚀 Starting Novustell Travel build process..."
      pip install --upgrade pip
      pip install -r requirements.txt
      python manage.py collectstatic --noinput --settings=tours_travels.settings_prod
      python manage.py migrate --settings=tours_travels.settings_prod
      python manage.py createcachetable --settings=tours_travels.settings_prod
    startCommand: |
      gunicorn tours_travels.wsgi:application \
        --bind 0.0.0.0:$PORT \
        --workers $WEB_CONCURRENCY \
        --timeout $GUNICORN_TIMEOUT
    healthCheckPath: /health/
    autoDeploy: true
```

### Database Configuration
```yaml
databases:
  - name: novustell-db
    databaseName: novustell_travel
    user: novustell_user
    region: oregon
    plan: free
    postgresMajorVersion: 15
```

---

## 7. Dependencies and Package Management

### Core Requirements (`requirements.txt`)
```txt
# Django Framework
Django==5.0.14
django-unfold>=0.22.0
django-ckeditor-5>=0.2.12
django-crispy-forms>=2.1.0
django-import-export>=3.3.7
django-taggit>=5.0.1
djangorestframework>=3.14.0

# Database
dj-database-url>=2.1.0
psycopg2-binary>=2.9.6

# Image & File Processing
Pillow>=10.2.0
pyuploadcare>=6.0.0
pydantic>=2.5.0  # Required for Mailtrap compatibility

# Email & Communication
mailtrap>=2.0.0

# Server & Deployment
gunicorn>=21.2.0
whitenoise>=6.6.0

# Background Tasks (Email Marketing)
celery>=5.3.0
redis>=4.5.0
django-redis>=6.0.0
django-ratelimit>=4.1.0

# Utilities
python-decouple>=3.8
python-dotenv>=1.0.1
requests>=2.31.0
shortuuid>=1.0.13
```

### Critical Package Versions
- **Django 5.0.14**: Latest stable version with security updates
- **pydantic>=2.5.0**: Required for Mailtrap 2.x compatibility (TypeAdapter class)
- **pyuploadcare>=6.0.0**: Compatible with Pydantic 2.x
- **django-unfold>=0.22.0**: Modern admin interface
- **mailtrap>=2.0.0**: HTTP API for email sending

### Pydantic 2.x Migration Considerations
The project was upgraded from Pydantic 1.x to 2.x for Mailtrap compatibility:
- **Breaking Change**: `TypeAdapter` class only available in Pydantic 2.x
- **Dependency Conflict**: Old pyuploadcare versions require Pydantic <2.0.0
- **Solution**: Upgrade both packages simultaneously

---

## 8. Key Code Snippets

### Email Sending Function (`users/tasks.py`)
```python
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
        # Initialize Mailtrap client
        client = MailtrapClient(token=settings.MAILTRAP_API_TOKEN)
        
        # Parse from_email to extract name and email
        if '<' in from_email and '>' in from_email:
            from_name = from_email.split('<')[0].strip()
            from_email_addr = from_email.split('<')[1].split('>')[0].strip()
        else:
            from_name = "Novustell Travel"
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
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email via Mailtrap API: {e}")
        return False
```

### Novustell Branding Constants
```python
# Brand Colors
PRIMARY_COLOR = "#0f238d"      # Deep blue
SECONDARY_COLOR = "#ff9d00"    # Orange
ACCENT_COLOR = "#ffffff"       # White

# Contact Information
WHATSAPP_PHONE = "+254701363551"
ADMIN_EMAIL = "info@novustelltravel.com"
CAREERS_EMAIL = "careers@novustelltravel.com"
NEWSLETTER_EMAIL = "news@novustelltravel.com"

# Business Details
COMPANY_NAME = "Novustell Travel"
TAGLINE = "Think Convenience, Think Novustell"
OFFICE_LOCATION = "New Peoples Media Center (Kilimani), Elgeyo Marakwet & Kilimani Rd Junction (Off Ngong Rd)"
```

---

## 9. Migration and Update Guide

### Building This System from Scratch

#### Step 1: Django Project Setup
```bash
# Create virtual environment
python3 -m venv env
source env/bin/activate

# Install Django and create project
pip install Django==5.0.14
django-admin startproject tours_travels
cd tours_travels

# Create apps
python manage.py startapp adminside
python manage.py startapp users
python manage.py startapp blog
python manage.py startapp status
```

#### Step 2: Install Dependencies
```bash
# Install all requirements
pip install -r requirements.txt

# Handle Pydantic compatibility
pip install --force-reinstall pydantic>=2.5.0
pip install --force-reinstall pyuploadcare>=6.0.0
```

#### Step 3: Configure Settings
1. Copy `tours_travels/settings.py` configuration
2. Copy `tours_travels/settings_prod.py` for production
3. Set up environment files (`.env` for development)
4. Configure Django Unfold admin interface
5. Set up CKEditor 5 configuration

#### Step 4: Database Setup
```bash
# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create cache table (for production)
python manage.py createcachetable
```

#### Step 5: Configure Email System
1. Set up Mailtrap account and get API token
2. Configure `MAILTRAP_API_TOKEN` in environment
3. Test email functionality with `send_email_via_mailtrap()`

#### Step 6: Deploy to Render
1. Copy `render.yaml` configuration
2. Set up NeonDB PostgreSQL database
3. Configure environment variables in Render dashboard
4. Deploy from GitHub repository

### Updating an Existing Django Project

#### Compatibility Checklist
- [ ] Django version compatibility (5.0.14)
- [ ] Python version (3.12+)
- [ ] Pydantic 2.x compatibility
- [ ] PostgreSQL database setup
- [ ] Mailtrap HTTP API integration

#### Migration Steps
1. **Backup existing data**
2. **Update requirements.txt** with new package versions
3. **Handle Pydantic migration** (1.x → 2.x)
4. **Update settings files** with new configurations
5. **Migrate database schema**
6. **Test email functionality**
7. **Deploy with new render.yaml**

### Verification Steps

#### Development Environment
```bash
# Test database connection
python manage.py dbshell

# Test email sending
python manage.py shell
>>> from users.tasks import send_email_via_mailtrap
>>> send_email_via_mailtrap("Test", "<h1>Test</h1>", "test@example.com", ["recipient@example.com"])

# Run development server
python manage.py runserver 0.0.0.0:8005
```

#### Production Environment
```bash
# Check deployment status
curl https://novustelltravel.onrender.com/health/

# Test contact form submission
# Test blog post creation
# Test admin interface access
```

---

## Novustell Travel Context

### Brand Identity
- **Primary Color**: #0f238d (Deep Blue)
- **Secondary Color**: #ff9d00 (Orange)
- **WhatsApp**: +254701363551
- **Email Addresses**:
  - General: info@novustelltravel.com
  - Careers: careers@novustelltravel.com
  - Newsletter: news@novustelltravel.com

### Image Management
- **Platform**: UploadCare integration
- **Fallback**: Custom Novustell placeholder SVG
- **Formats**: Automatic optimization and cropping

### Admin Interface
- **Theme**: Django Unfold (modern, clean interface)
- **Rich Text**: CKEditor 5 for all content fields
- **Import/Export**: Django Import-Export for data management

---

This documentation provides a complete reference for replicating or updating the Novustell Travel Django system. Each section includes practical code examples, configuration details, and step-by-step instructions for implementation.
