# Novustell Travel Email System Architecture Documentation

**Complete Reference for Email System Recreation**  
**Last Updated:** December 2024  
**Django Version:** 5.0.14  

---

## 📧 **1. Email Configuration Settings**

### **Core Email Settings (settings.py)**
```python
# Email settings for Novustell Travel
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Novustell Travel email credentials
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'novustellke@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'vsmw vdut tanu gtdg')
DEFAULT_FROM_EMAIL = 'NOVUSTELL TRAVEL'

# Admin email for notifications
ADMIN_EMAIL = 'info@novustelltravel.com'

# Jobs email for career applications
JOBS_EMAIL = 'careers@novustelltravel.com'

# Newsletter email for subscriptions
NEWSLETTER_EMAIL = 'news@novustelltravel.com'
```

### **Production Settings (settings_prod.py)**
```python
# Production email backend - SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'novustellke@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'Novustell Travel <novustellke@gmail.com>')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'info@novustelltravel.com')
JOBS_EMAIL = os.getenv('JOBS_EMAIL', 'careers@novustelltravel.com')
NEWSLETTER_EMAIL = os.getenv('NEWSLETTER_EMAIL', 'news@novustelltravel.com')
```

### **Development Settings (settings_dev.py)**
```python
# Development email backend - Console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development email settings
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025  # For development email server
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = 'noreply@localhost'
ADMIN_EMAIL = 'admin@localhost'
```

### **Test Settings (test_settings.py)**
```python
# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
```

---

## 🌍 **2. Environment Variables**

### **Production Environment (.env.production)**
```bash
# Email Configuration (Gmail SMTP)
EMAIL_HOST_USER=novustellke@gmail.com
EMAIL_HOST_PASSWORD=vsmw vdut tanu gtdg
DEFAULT_FROM_EMAIL=Novustell Travel <novustellke@gmail.com>
ADMIN_EMAIL=info@novustelltravel.com
JOBS_EMAIL=careers@novustelltravel.com
NEWSLETTER_EMAIL=news@novustelltravel.com
```

### **Development Environment (.env.development)**
```bash
# Email Configuration
EMAIL_HOST_USER=novustellke@gmail.com
EMAIL_HOST_PASSWORD=vsmw vdut tanu gtdg
DEFAULT_FROM_EMAIL=Novustell Travel <novustellke@gmail.com>
ADMIN_EMAIL=info@novustelltravel.com
JOBS_EMAIL=careers@novustelltravel.com
NEWSLETTER_EMAIL=news@novustelltravel.com
```

### **Render Deployment (render.yaml)**
```yaml
# Email Configuration
- key: EMAIL_HOST_USER
  value: novustellke@gmail.com
- key: EMAIL_HOST_PASSWORD
  sync: false  # Set manually: iagt yans hoyd pavg
- key: DEFAULT_FROM_EMAIL
  value: Novustell Travel <novustellke@gmail.com>
- key: ADMIN_EMAIL
  value: info@novustelltravel.com
- key: JOBS_EMAIL
  value: careers@novustelltravel.com
- key: NEWSLETTER_EMAIL
  value: news@novustelltravel.com
```

**⚠️ IMPORTANT:** The actual Gmail app password for production is: `iagt yans hoyd pavg`

---

## 🔧 **3. Email Backend Configuration**

### **Backend Types by Environment**
- **Production:** `django.core.mail.backends.smtp.EmailBackend` (Gmail SMTP)
- **Development:** `django.core.mail.backends.console.EmailBackend` (Console output)
- **Testing:** `django.core.mail.backends.locmem.EmailBackend` (In-memory)

### **Gmail SMTP Configuration**
- **Host:** smtp.gmail.com
- **Port:** 587
- **Security:** TLS encryption
- **Authentication:** App password required (not regular password)

### **Third-Party Services**
- **Email Marketing:** Custom email_marketing app with EmailMultiAlternatives
- **No external services:** SendGrid, Mailgun, etc. (pure Django implementation)

---

## 📨 **4. Email Trigger Points - Complete Inventory**

### **4.1 Booking System Emails**

#### **Booking Confirmation Email**
- **Trigger:** `users/checkout_views.py` - `send_booking_confirmation_email()`
- **File:** `users/utils.py:16-52`
- **Template:** `users/booking_confirmation.html`
- **Recipient:** Customer email
- **Sender:** `settings.DEFAULT_FROM_EMAIL`
- **Subject:** `f'Web Booking - Booking ID {booking.id}'`
- **Context:** booking_id, full_name, package_name, number_of_adults, number_of_children, number_of_rooms, total_amount, include_travelling

#### **Legacy Booking Email (SMTP)**
- **Trigger:** `users/views.py` - `send_booking_email()`
- **File:** `users/views.py:828-844`
- **Template:** None (plain text)
- **Recipient:** info@novustelltravel.com
- **Sender:** Novustell Travel <novustellke@gmail.com>
- **Subject:** `f"New Booking: {booking.full_name} for {booking.package.name}"`

### **4.2 User Account Emails**

#### **Account Verification Email**
- **Trigger:** User registration
- **File:** `tours_travels/mail.py:8-42`
- **Template:** None (HTML string)
- **Recipient:** User email
- **Sender:** Novustell Travel <novustellke@gmail.com>
- **Subject:** "Welcome to Novustell Travel"
- **Context:** username, verification_link, directors_message, advantages_message

#### **Welcome Email (Auto-created accounts)**
- **Trigger:** `users/checkout_views.py` - `send_welcome_email()`
- **File:** `users/checkout_views.py:536-555`
- **Template:** `users/emails/welcome.html`
- **Recipient:** User email
- **Sender:** `settings.DEFAULT_FROM_EMAIL`
- **Subject:** "Welcome to Novustell Travel"
- **Context:** user, password

### **4.3 Contact Form Emails**

#### **General Contact Inquiry**
- **Trigger:** Contact form submission
- **File:** `users/views.py:290-340`
- **Templates:** 
  - Admin: `users/emails/contact_inquiry_admin.html` + `.txt`
  - Client: `users/emails/contact_inquiry_confirmation.html` + `.txt`
- **Recipients:** 
  - Admin: Info@novustelltravel.com
  - Client: inquiry.email
- **Sender:** `settings.DEFAULT_FROM_EMAIL`
- **Subject:** 
  - Admin: `f"New Contact Inquiry: {inquiry.subject} - {inquiry.full_name}"`
  - Client: "✅ Thank You! - Contact Inquiry Received"

#### **MICE Inquiry**
- **Trigger:** MICE form submission
- **File:** `users/views.py:111-158`
- **Templates:**
  - Admin: `users/emails/mice_inquiry_admin.html` + `.txt`
  - Client: `users/emails/mice_inquiry_confirmation.html` + `.txt`
- **Recipients:**
  - Admin: `settings.ADMIN_EMAIL`
  - Client: inquiry.email
- **Subject:**
  - Admin: `f'New MICE Inquiry from {inquiry.company_name}'`
  - Client: `f'MICE Inquiry Received - {inquiry.company_name}'`

#### **NGO Travel Inquiry**
- **Trigger:** NGO form submission
- **File:** `users/views.py:160-207`
- **Templates:**
  - Admin: `users/emails/ngo_travel_admin.html` + `.txt`
  - Client: `users/emails/ngo_travel_confirmation.html` + `.txt`
- **Recipients:**
  - Admin: `settings.ADMIN_EMAIL`
  - Client: inquiry.email

#### **Student Travel Inquiry**
- **Trigger:** Student form submission
- **File:** `users/views.py:218-265`
- **Templates:**
  - Admin: `users/emails/student_travel_admin.html` + `.txt`
  - Client: `users/emails/student_travel_confirmation.html` + `.txt`
- **Recipients:**
  - Admin: `settings.ADMIN_EMAIL`
  - Client: inquiry.email

### **4.4 Job Application Emails**

#### **Job Application Submission**
- **Trigger:** Job application form submission
- **File:** `users/views.py:350-410`
- **Templates:**
  - Admin: `users/emails/job_application_admin.html`
  - Applicant: `users/emails/job_application_confirmation.html`
- **Recipients:**
  - Admin: Both `settings.JOBS_EMAIL` AND `settings.ADMIN_EMAIL`
  - Applicant: application.email
- **Subject:**
  - Admin: `f'New Job Application - {job_application.get_position_display()}'`
  - Applicant: `f'Application Received - {job_application.get_position_display()}'`

### **4.5 Newsletter Emails**

#### **Newsletter Subscription**
- **Trigger:** Newsletter form submission
- **File:** `users/views.py:413-456`
- **Templates:**
  - Admin: `users/emails/newsletter_admin.html`
  - Subscriber: `users/emails/newsletter_confirmation.html`
- **Recipients:**
  - Admin: `settings.NEWSLETTER_EMAIL`
  - Subscriber: subscription.email
- **Subject:**
  - Admin: `f'New Newsletter Subscription - {subscription.email}'`
  - Subscriber: "Welcome to Novustell Travel Newsletter!"

### **4.6 Email Marketing System**

#### **Marketing Campaigns**
- **Trigger:** Email marketing campaigns
- **File:** `email_marketing/services.py:24-149`
- **Templates:** Dynamic from `EmailTemplate` model
- **Recipients:** From `RecipientList` and `Recipient` models
- **Sender:** `settings.DEFAULT_FROM_EMAIL`
- **Features:** Open tracking, click tracking, personalization

---

## 📁 **5. Email Templates**

### **Template Directory Structure**
```
users/templates/users/emails/
├── INDEX2025.HTML (unused)
├── admin_notification.html (generic)
├── booking_confirmation.html (booking system)
├── contact_inquiry_admin.html ✅ (ENHANCED - branded)
├── contact_inquiry_admin.txt ✅ (ENHANCED - branded)
├── contact_inquiry_confirmation.html ✅ (ENHANCED - branded)
├── contact_inquiry_confirmation.txt ✅ (ENHANCED - branded)
├── job_application_admin.html ⚠️ (basic branding)
├── job_application_confirmation.html ⚠️ (basic branding)
├── mice_inquiry_admin.html ✅ (ENHANCED - branded)
├── mice_inquiry_admin.txt ✅ (ENHANCED - branded)
├── mice_inquiry_confirmation.html ✅ (ENHANCED - branded)
├── mice_inquiry_confirmation.txt ✅ (ENHANCED - branded)
├── newsletter_admin.html ⚠️ (basic branding)
├── newsletter_confirmation.html ⚠️ (basic branding)
├── ngo_travel_admin.html ✅ (ENHANCED - branded)
├── ngo_travel_admin.txt ✅ (ENHANCED - branded)
├── ngo_travel_confirmation.html ✅ (ENHANCED - branded)
├── ngo_travel_confirmation.txt ✅ (ENHANCED - branded)
├── student_travel_admin.html ✅ (ENHANCED - branded)
├── student_travel_admin.txt ✅ (ENHANCED - branded)
├── student_travel_confirmation.html ✅ (ENHANCED - branded)
├── student_travel_confirmation.txt ✅ (ENHANCED - branded)
└── welcome.html (user registration)
```

### **Email Marketing Templates**
```
email_marketing/templates/email_marketing/
└── model_un_2025_campaign.html (marketing campaign)
```

### **Template Inheritance**
- **Base Template:** None (each template is standalone)
- **Branding Elements:** Novustell logo, colors (#170b2c, #ff9d00, white)
- **Logo URL:** `https://www.novustelltravel.com/static/assets/images/logo/logo-white.png`

### **Backup Templates**
- **Location:** No backup templates found in `users/templates/ignorethistemplate/users`
- **Note:** All templates are actively used and should be modified carefully

---

## 📋 **6. Forms and Email Integration**

### **Forms That Trigger Emails**
1. **ContactForm** (`users/forms.py:277-338`) → Contact inquiry emails
2. **MICEInquiryForm** (`users/forms.py:49-62`) → MICE inquiry emails
3. **NGOTravelInquiryForm** (`users/forms.py:81-101`) → NGO travel emails
4. **StudentTravelInquiryForm** (similar pattern) → Student travel emails
5. **JobApplicationForm** (`users/forms.py:103-151`) → Job application emails
6. **NewsletterSubscriptionForm** (`users/forms.py:211-247`) → Newsletter emails
7. **CheckoutForm** (`users/checkout_forms.py:69-100`) → Booking confirmation emails

### **Email Dispatch Pattern**
```python
# Standard pattern used across all forms
try:
    # Save form data
    inquiry = form.save()
    
    # Render email templates
    admin_html = render_to_string('template_admin.html', {'inquiry': inquiry})
    admin_txt = render_to_string('template_admin.txt', {'inquiry': inquiry})
    
    # Send admin email
    send_mail(
        subject=admin_subject,
        message=admin_txt,
        html_message=admin_html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[admin_email],
        fail_silently=False,
    )
    
    # Send client confirmation email
    # ... similar pattern
    
except Exception as e:
    # Error handling
    messages.error(request, 'Email sending failed')
```

### **AJAX Implementation**
- **No AJAX email sending** - All emails sent synchronously during form submission
- **Form validation** happens before email dispatch
- **Error handling** with Django messages framework

---

## 🔄 **7. Production vs Development Differences**

### **Development Environment**
- **Database:** SQLite (`db_development.sqlite3`)
- **Email Backend:** Console output (`django.core.mail.backends.console.EmailBackend`)
- **SMTP Settings:** Localhost:1025 (for development email server)
- **Security:** Relaxed (no SSL/TLS requirements)
- **Debug:** Enabled

### **Production Environment**
- **Database:** PostgreSQL (NeonDB)
- **Email Backend:** Gmail SMTP (`django.core.mail.backends.smtp.EmailBackend`)
- **SMTP Settings:** smtp.gmail.com:587 with TLS
- **Security:** Full SSL/TLS, secure cookies
- **Debug:** Disabled

### **Testing Environment**
- **Database:** SQLite in-memory (`:memory:`)
- **Email Backend:** In-memory (`django.core.mail.backends.locmem.EmailBackend`)
- **Migrations:** Disabled for speed
- **Logging:** Disabled

---

## 📦 **8. Dependencies and Requirements**

### **Core Email Dependencies (requirements.txt)**
```txt
# Core Django & Extensions
Django==5.0.14
django-crispy-forms>=2.1.0

# No additional email-specific packages required
# Django's built-in email system is used
```

### **Email-Related Python Packages**
- **smtplib** (built-in) - Used in `tours_travels/mail.py`
- **email.mime.multipart** (built-in) - Used for custom SMTP emails
- **email.mime.text** (built-in) - Used for email content
- **django.core.mail** (Django built-in) - Primary email system
- **django.template.loader** (Django built-in) - Template rendering

### **Version Compatibility**
- **Django 5.0.14** - Core framework
- **No conflicts** - Pure Django email implementation
- **Python 3.12** compatible

---

## 🔧 **9. Troubleshooting and Testing**

### **Email Testing Script**
- **File:** `test_email_credentials.py`
- **Functions:**
  - `test_smtp_connection()` - Test Gmail SMTP connection
  - `send_test_email()` - Send test email
  - `test_django_email_backend()` - Test Django email backend

### **Common Issues and Solutions**

#### **Gmail Authentication Issues**
- **Problem:** "Authentication failed" errors
- **Solution:** Use app password, not regular password
- **App Password:** `iagt yans hoyd pavg` (production)

#### **Development Email Testing**
- **Problem:** Emails not visible in development
- **Solution:** Use console backend or development SMTP server
- **Command:** `python -m smtpd -n -c DebuggingServer localhost:1025`

#### **Production Email Delivery**
- **Problem:** Emails not reaching recipients
- **Solution:** Check Gmail SMTP limits, verify app password
- **Monitoring:** Check Django logs and Gmail account activity

### **Testing Checklist**
1. ✅ SMTP connection test
2. ✅ Authentication verification
3. ✅ Test email sending
4. ✅ Template rendering
5. ✅ Form submission emails
6. ✅ Production deployment verification

---

## 📝 **10. Recreation Checklist**

### **Step 1: Environment Setup**
```bash
# 1. Install dependencies
pip install Django==5.0.14 django-crispy-forms>=2.1.0

# 2. Create environment files
cp .env.production.template .env.production
cp .env.development.template .env.development
```

### **Step 2: Gmail Configuration**
```bash
# 1. Set up Gmail app password
# 2. Update environment variables
EMAIL_HOST_USER=novustellke@gmail.com
EMAIL_HOST_PASSWORD=iagt yans hoyd pavg  # Production
EMAIL_HOST_PASSWORD=vsmw vdut tanu gtdg  # Development/Testing
```

### **Step 3: Django Settings**
```python
# 1. Add email settings to settings.py
# 2. Configure production settings in settings_prod.py
# 3. Set up development settings in settings_dev.py
# 4. Configure test settings in test_settings.py
```

### **Step 4: Email Templates**
```bash
# 1. Create template directory
mkdir -p users/templates/users/emails/

# 2. Copy all email templates
# 3. Update logo URLs and branding
# 4. Test template rendering
```

### **Step 5: Email Functions**
```python
# 1. Implement email utility functions in users/utils.py
# 2. Add email triggers in views
# 3. Configure form email integration
# 4. Set up email marketing system (optional)
```

### **Step 6: Testing and Verification**
```bash
# 1. Run email credential tests
python test_email_credentials.py

# 2. Test form submissions
python manage.py test users.tests.test_email_functionality

# 3. Verify production deployment
# 4. Monitor email delivery
```

### **Step 7: Deployment Configuration**
```yaml
# 1. Update render.yaml with email environment variables
# 2. Set Render dashboard environment variables
# 3. Deploy and test production email functionality
# 4. Monitor logs for email delivery confirmation
```

---

## 🎯 **Final Notes**

### **Critical Success Factors**
1. **Gmail App Password:** Must use app password, not regular password
2. **Environment Variables:** Properly configured for each environment
3. **Template Branding:** Consistent Novustell branding across all templates
4. **Error Handling:** Proper exception handling for email failures
5. **Testing:** Comprehensive testing before production deployment

### **Security Considerations**
- **App Passwords:** Store securely in environment variables
- **TLS Encryption:** Always enabled for production SMTP
- **Email Validation:** Proper validation in all forms
- **Rate Limiting:** Consider implementing for high-volume scenarios

### **Maintenance Tasks**
- **Monitor Gmail quotas** and delivery rates
- **Update email templates** with current branding
- **Test email functionality** after Django upgrades
- **Review email logs** for delivery issues
- **Backup email templates** before modifications

---

**Documentation Complete** ✅  
**Total Email Triggers:** 12 different email types  
**Template Files:** 24 email templates  
**Environments Covered:** Development, Testing, Production  
**Ready for Recreation:** Yes, with this documentation
