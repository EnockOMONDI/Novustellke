from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserBookings, UserProfile, BucketList, Booking
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from django.http import JsonResponse
from urllib.parse import quote
import json

from adminside.models import *
from users.models import *
from .forms import UserRegisterForm
from .forms import UserBookingsForm
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.

from tours_travels import mail as mail_f
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError
from .utils import generate_token
from django.views import View
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .forms import UserRegisterForm

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .utils import send_booking_confirmation_email
from .forms import MICEInquiryForm, StudentTravelInquiryForm, NGOTravelInquiryForm, JobApplicationForm, NewsletterSubscriptionSimpleForm
from django.contrib.auth.models import User
from blog.models import Post, Category
from adminside.models import Destination, Package, Accommodation






def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)  # Save the user object in memory
            user.is_active = False

            # Save the user object to the database only when the form is valid
            user.save()

            current_site = get_current_site(request)
            uid64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            activation_link = f'http://{current_site}/activate/{uid64}/{token}'

            mail_f.verification_mail(activation_link, user)

            # Store username and email in session
            request.session['username'] = form.cleaned_data['username']
            request.session['email'] = form.cleaned_data['email']

            # Redirect to the success message page
            return redirect('users:success')

    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})




def success(request):
    username = request.session.pop('username', None)
    email = request.session.pop('email', None)

    if username and email:
        success_message = f"Jambo! <b>{username}</b>, Your registration was successful! We've sent an email to <b>{email}</b>. Kindly click the received link to confirm and complete the registration. Remember to check your spam folder."
        messages.success(request, success_message)
    else:
        messages.error(request, 'Oops! Something is not right. Please start over.')

    return render(request, 'users/success.html')


def aboutus(request):

    return render(request, 'users/aboutus.html')



def corporate(request):

    return render(request, 'users/corporate.html')


def document_workflow(request):
    """
    Client document workflow page using Sejda's public PDF editor integration.
    """
    document_url = request.GET.get('document_url', '').strip()
    return_email = request.GET.get('return_email', 'Info@novustelltravel.com').strip()
    mode = request.GET.get('mode', 'fill-sign')

    sejda_link = ''
    if document_url:
        files_payload = json.dumps([{'downloadUrl': document_url}], separators=(',', ':'))
        sejda_link = f'https://www.sejda.com/pdf-editor?files={quote(files_payload, safe="")}'
        if return_email:
            sejda_link += f'&returnEmail={quote(return_email, safe="")}'

    context = {
        'document_url': document_url,
        'return_email': return_email,
        'mode': mode,
        'sejda_link': sejda_link,
    }

    return render(request, 'users/document_workflow.html', context)

# users/views.py


def micepage(request):
    if request.method == 'POST':
        form = MICEInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()

            try:

                # Send email notifications through the configured transactional email backend
                from .tasks import send_mice_inquiry_emails
                result = send_mice_inquiry_emails(inquiry)

                if result.get('success'):
                    messages.success(request, f'Thank you! Your MICE inquiry has been submitted successfully. We will contact you within 2 hours. Reference ID: MICE-{inquiry.id:05d}')
                else:
                    messages.warning(request, f'Your MICE inquiry has been submitted (Ref: MICE-{inquiry.id:05d}), but there was an issue sending email notifications. We will still contact you within 2 hours.')

                return redirect('users:micepage')

            except Exception as e:
                messages.error(request, 'There was an error sending your inquiry. Please try again.')
                print(f"Email error: {e}")
    else:
        form = MICEInquiryForm()

    return render(request, 'users/mice.html', {'form': form})


def student_travel(request):
    if request.method == 'POST':
        form = StudentTravelInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()

            try:
                # Send email notifications through the configured transactional email backend
                from .tasks import send_student_travel_emails
                result = send_student_travel_emails(inquiry)

                if result.get('success'):
                    messages.success(request, f'Thank you! Your student travel inquiry has been submitted successfully. We will contact you within 4 hours. Reference ID: STU-{inquiry.id:05d}')
                else:
                    messages.warning(request, f'Your student travel inquiry has been submitted (Ref: STU-{inquiry.id:05d}), but there was an issue sending email notifications. We will still contact you within 4 hours.')

                return redirect('users:student-travel')

            except Exception as e:
                messages.error(request, 'There was an error sending your inquiry. Please try again.')
                print(f"Email error: {e}")
    else:
        form = StudentTravelInquiryForm()

    return render(request, 'users/student_travel.html', {'form': form})


def ngo_travel(request):
    if request.method == 'POST':
        form = NGOTravelInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()

            try:
                # Send email notifications through the configured transactional email backend
                from .tasks import send_ngo_travel_emails
                result = send_ngo_travel_emails(inquiry)

                if result.get('success'):
                    messages.success(request, f'Thank you! Your NGO travel inquiry has been submitted successfully. We will contact you within 24 hours. Reference ID: NGO-{inquiry.id:05d}')
                else:
                    messages.warning(request, f'Your NGO travel inquiry has been submitted (Ref: NGO-{inquiry.id:05d}), but there was an issue sending email notifications. We will still contact you within 24 hours.')

                return redirect('users:ngo-travel')

            except Exception as e:
                messages.error(request, 'There was an error sending your inquiry. Please try again.')
                print(f"Email error: {e}")
    else:
        form = NGOTravelInquiryForm()

    return render(request, 'users/ngo_travel.html', {'form': form})


def holidays(request):

    return render(request, 'users/holidays.html')

def contactus(request):
    if request.method == 'POST':
        from .forms import ContactForm
        from django.contrib import messages
        import logging

        logger = logging.getLogger(__name__)
        form = ContactForm(request.POST)

        if form.is_valid():
            try:
                # Save the contact inquiry
                inquiry = form.save()

                # Send email notifications through the configured transactional email backend
                from .tasks import send_contact_inquiry_emails
                result = send_contact_inquiry_emails(inquiry)

                if result.get('success'):
                    logger.info(f"Contact inquiry emails sent successfully for inquiry {inquiry.id}")
                    messages.success(request,
                        f'Thank you for your inquiry! We have received your message about "{inquiry.subject}" and will respond within 24 hours. '
                        f'Your reference number is NVT-{inquiry.id:05d}. For immediate assistance, contact us via WhatsApp at +254 701 363 551.')
                else:
                    logger.warning(f"Some contact inquiry emails failed for inquiry {inquiry.id}: {result}")
                    first_error = next(
                        (
                            error
                            for error in result.get("errors", [])
                            if error and error.get("code")
                        ),
                        None,
                    )
                    diagnostic_suffix = (
                        f' Diagnostic code: {first_error["code"]}.'
                        if first_error
                        else ''
                    )
                    messages.warning(request,
                        f'Your inquiry has been submitted (Ref: NVT-{inquiry.id:05d}), but there was an issue sending email notifications. '
                        f'We will still respond to your inquiry.{diagnostic_suffix} For immediate assistance, contact us via WhatsApp at +254 701 363 551.')

                logger.info(f"Contact inquiry submitted successfully: {inquiry.full_name} - {inquiry.subject}")

                # Redirect to prevent form resubmission
                from django.shortcuts import redirect
                return redirect('users:contactus')

            except Exception as e:
                logger.error(f"Error processing contact form: {str(e)}")
                messages.error(request,
                    'There was an error sending your message. Please try again or contact us directly at Info@novustelltravel.com or +254 701 363 551.')
        else:
            messages.error(request, 'Please correct the errors below and try again.')
    else:
        from .forms import ContactForm
        form = ContactForm()

    return render(request, 'users/contactus.html', {'form': form})


# Job application emails are handled in users/tasks.py through the configured email backend


# Newsletter subscription emails are handled in users/tasks.py through the configured email backend


def careers(request):
    """
    Careers page with job application form and dynamic job listings
    """
    from .models import JobListing

    # Get job listings
    job_listings = JobListing.objects.filter(is_active=True).order_by('-featured', '-posted_date')

    # Filter by job type if specified
    job_type_filter = request.GET.get('job_type')
    if job_type_filter:
        job_listings = job_listings.filter(job_type=job_type_filter)

    # Filter by application status if specified
    status_filter = request.GET.get('status')
    if status_filter:
        job_listings = job_listings.filter(application_status=status_filter)

    # Handle job application form submission
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            job_application = form.save()

            # Send email notifications through the configured transactional email backend
            try:
                from .tasks import send_job_application_emails
                result = send_job_application_emails(job_application)

                if result.get('success'):
                    messages.success(request, 'Your job application has been submitted successfully! We will review your application and get back to you soon.')
                else:
                    messages.warning(request, 'Your application was submitted, but there was an issue sending email notifications. We will still review your application.')
            except Exception as e:
                messages.warning(request, 'Your application was submitted, but there was an issue sending email notifications. We will still review your application.')
                print(f"Email error: {e}")

            # Redirect to prevent resubmission
            return redirect('users:careers')
    else:
        form = JobApplicationForm()

        # Pre-populate form if job_id is provided
        job_id = request.GET.get('job_id')
        if job_id:
            try:
                job_listing = JobListing.objects.get(id=job_id, is_active=True)
                # Map job listing title to form choices
                position_mapping = {
                    'accountant': 'accountant',
                    'travel consultant': 'travel_consultant',
                    'graphic designer': 'graphic_designer',
                    'marketing specialist': 'marketing_specialist',
                    'customer service representative': 'customer_service',
                    'tour guide': 'tour_guide',
                    'operations manager': 'operations_manager',
                }

                # Try to find matching position
                job_title_lower = job_listing.title.lower()
                for key, value in position_mapping.items():
                    if key in job_title_lower:
                        form.initial['position_applied_for'] = value
                        break

            except JobListing.DoesNotExist:
                pass

    # Get filter choices for the template
    job_type_choices = JobListing.JOB_TYPE_CHOICES
    status_choices = JobListing.APPLICATION_STATUS_CHOICES

    context = {
        'form': form,
        'job_listings': job_listings,
        'job_type_choices': job_type_choices,
        'status_choices': status_choices,
        'current_job_type': job_type_filter,
        'current_status': status_filter,
    }

    return render(request, 'users/careers.html', context)


def job_detail(request, slug):
    """
    Individual job detail page with access control for closed jobs
    """
    from .models import JobListing
    from django.shortcuts import get_object_or_404

    job = get_object_or_404(JobListing, slug=slug, is_active=True)

    # Check if job applications are closed
    if job.application_status == 'closed':
        # Get other open jobs to show as alternatives
        open_jobs = JobListing.objects.filter(
            application_status='open',
            is_active=True
        ).exclude(id=job.id)[:3]

        # Render a special template for closed jobs
        context = {
            'job': job,
            'is_closed': True,
            'open_jobs': open_jobs,
        }
        return render(request, 'users/job_detail_closed.html', context)

    # Get related jobs (same type, excluding current job)
    related_jobs = JobListing.objects.filter(
        job_type=job.job_type,
        is_active=True
    ).exclude(id=job.id)[:3]

    context = {
        'job': job,
        'related_jobs': related_jobs,
        'is_closed': False,
    }

    return render(request, 'users/job_detail.html', context)


def newsletter_subscribe(request):
    """
    Handle newsletter subscription from footer form
    """
    from .models import NewsletterSubscription
    from django.http import JsonResponse

    if request.method == 'POST':
        form = NewsletterSubscriptionSimpleForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Create subscription with default preferences
            subscription = NewsletterSubscription.objects.create(
                email=email,
                travel_tips=True,
                special_offers=True,
                destination_updates=True
            )

            # Send email notifications through the configured transactional email backend
            try:
                from .tasks import send_newsletter_subscription_emails
                result = send_newsletter_subscription_emails(subscription)

                if result.get('success'):
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'message': 'Thank you for subscribing! Please check your email to confirm your subscription.'
                        })
                    else:
                        messages.success(request, 'Thank you for subscribing! Please check your email to confirm your subscription.')
                else:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'message': 'You have been subscribed, but there was an issue sending the confirmation email.'
                        })
                    else:
                        messages.warning(request, 'You have been subscribed, but there was an issue sending the confirmation email.')
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Newsletter subscription email failed for {subscription.email}: {str(e)}")

                # Still show success to user but log the error for admin investigation
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'message': 'You have been subscribed, but there was an issue sending the confirmation email.'
                    })
                else:
                    messages.warning(request, 'You have been subscribed, but there was an issue sending the confirmation email.')
                print(f"Newsletter email error: {e}")
        else:
            # Form has errors
            error_message = list(form.errors.values())[0][0] if form.errors else 'Please enter a valid email address.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
            else:
                messages.error(request, error_message)

    # Redirect back to the referring page or homepage
    return redirect(request.META.get('HTTP_REFERER', 'users:home'))


def home(request):
    """
    Fully optimized homepage view with efficient database queries, caching, and featured accommodations
    """
    from django.core.cache import cache
    from adminside.models import Accommodation

    try:
        # Get featured destinations with optimized query (limit to 8 for performance)
        featured_destinations = Destination.objects.filter(
            is_featured=True,
            is_active=True
        ).select_related().order_by('display_order', 'name')[:8]

        # Get featured accommodations with optimized query (limit to 8 for performance)
        featured_accommodations = Accommodation.objects.select_related('destination').filter(
            is_featured=True,
            is_active=True
        ).order_by('-rating', 'name')[:8]

        # Get all active destinations for navigation (limited for performance)
        all_destinations = Destination.objects.filter(
            is_active=True
        ).order_by('name')[:50]  # Limit to 50 most relevant destinations

        # Get published packages with highly optimized queries (limit to 12 for homepage)
        packages_queryset = Package.objects.select_related('main_destination').prefetch_related(
            'available_accommodations',
            'available_travel_modes'
        ).filter(status=Package.PUBLISHED).order_by('-is_featured', 'total_bookings')[:12]

        # Process package data efficiently with minimal loops
        package_data = []
        for package in packages_queryset:
            try:
                # Calculate nights
                nights = max(package.duration_days - 1, 0)

                # Get first accommodation price (already prefetched)
                accommodations = list(package.available_accommodations.all())
                accommodation_price = accommodations[0].price_per_room_per_night if accommodations else 0

                # Calculate total price
                total_price = package.adult_price + accommodation_price

                # Get travel mode (already prefetched)
                travel_modes = list(package.available_travel_modes.all())
                if travel_modes:
                    transport_type = travel_modes[0].transport_type
                    travel_type = {
                        "train": "Train",
                        "flight": "Flight",
                        "bus": "Bus"
                    }.get(transport_type, "Bus")
                else:
                    travel_type = "N/A"

                package_data.append({
                    'package': package,
                    'nights': nights,
                    'price': total_price,
                    'travel': travel_type
                })
            except Exception as e:
                continue

        # Create optimized context
        context = {
            'featured_destinations': featured_destinations,
            'featured_accommodations': featured_accommodations,
            'all_destinations': all_destinations,
            'package_data': package_data,
            'packages': package_data,  # For backward compatibility with template
            'dests1': all_destinations,  # For backward compatibility
            'package1': packages_queryset,  # For backward compatibility
        }

        return render(request, 'users/index.html', context)

    except Exception as e:
        # Fallback to basic context to prevent complete failure
        try:
            basic_context = {
                'featured_destinations': Destination.objects.filter(is_featured=True, is_active=True)[:4],
                'featured_accommodations': [],
                'all_destinations': Destination.objects.filter(is_active=True)[:20],
                'package_data': [],
                'packages': [],
                'dests1': [],
                'package1': [],
            }
            return render(request, 'users/index.html', basic_context)
        except:
            from django.http import HttpResponse
            return HttpResponse("Homepage temporarily unavailable. Please try again later.", status=503)






def destination(request,id):
	id=id
	dest=Destination.objects.get(id=id)
	packs=Package.objects.filter(main_destination=dest, status=Package.PUBLISHED)
	nights=[]
	price=[]
	travel=[]

	for i in packs:
		nights.append(i.duration_days-1)
		first_accommodation = i.available_accommodations.first()
		accommodation_price = first_accommodation.price_per_room_per_night if first_accommodation else 0
		price.append(i.adult_price + accommodation_price)
		first_travel = i.available_travel_modes.first()
		if first_travel:
			if first_travel.transport_type == "train":
				travel.append("Train")
			elif first_travel.transport_type == "flight":
				travel.append("Flight")
			else:
				travel.append("Bus")
		else:
			travel.append("N/A")


	packages=zip(packs,nights,price,travel)




	context={'dest':dest,'packages':packages}

	return render(request,'users/destination.html',context)



def search(request):
	try:
		name=request.POST.get('search','')
		name=name.lstrip()
		name=name.rstrip()
		dest=Destination.objects.filter(name__icontains=name) | Destination.objects.filter(description__icontains=name)
		print(dest[0].id)
		return redirect('users-destination', id=dest[0].id)
	except:
		messages.error(request, 'No results found for your search request')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))









@login_required
def bookings(request, package_id):
    package = get_object_or_404(Package, id=package_id)
    form = UserBookingsForm(request.POST or None)
    context = {'form': form, 'package': package}

    if request.method == 'POST':
        if form.is_valid():
            print("Form is valid!")  # Debug print
            try:
                # Create the booking
                booking = UserBookings.objects.create(
                    user=request.user,
                    package=package,
                    full_name=form.cleaned_data['full_name'],
                    phone_number=form.cleaned_data['phone_number'],
                    number_of_adults=form.cleaned_data['number_of_adults'],
                    number_of_children=form.cleaned_data.get('number_of_children', 0),
                    number_of_rooms=form.cleaned_data['number_of_rooms'],
                    include_travelling=form.cleaned_data['include_travelling'],
                )

                # Send email notification
                send_booking_email(booking)

                return redirect('users:users-booking-success', booking_id=booking.id)

            except Exception as e:
                print(f"Booking creation error: {e}")
                messages.error(request, f'Error creating booking: {e}')
        else:
            print("Form is NOT valid!")
            print(form.errors)
            messages.error(request, 'Please correct the form errors.')

    return render(request, 'users/UserBookingsForm.html', context)


def send_booking_email(booking):
    """Send an email notification about the new booking."""
    try:
        subject = f"New Booking: {booking.full_name} for {booking.package.name}"
        message = f"""
        <p><strong>New Booking Alert</strong></p>
        <p><strong>Customer Name:</strong> {booking.full_name}</p>
        <p><strong>Phone Number:</strong> {booking.phone_number}</p>
        <p><strong>Package:</strong> {booking.package.name}</p>
        <p><strong>Adults:</strong> {booking.number_of_adults}</p>
        <p><strong>Children:</strong> {booking.number_of_children}</p>
        <p><strong>Rooms:</strong> {booking.number_of_rooms}</p>
        <p><strong>Include Travelling:</strong> {'Yes' if booking.include_travelling else 'No'}</p>
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            html_message=message,
            fail_silently=False,
        )
        print("Booking email sent successfully!")
        return True

    except Exception as e:
        print(f"Error sending booking email: {e}")
        return False

def booking_success(request, booking_id):
    booking = get_object_or_404(UserBookings, id=booking_id)
    return render(request, 'users/booking_success.html', {'booking': booking})






class ActivateAccountView(View):
	def get(self,request,uid64,token):
		try:
			uid = urlsafe_base64_decode(uid64).decode('utf-8')
			user=User.objects.get(pk=uid)
			print(uid)
		except Exception as identifire :
			user=None

		if user is not None and generate_token.check_token(user,token):
			user.is_active=True
			user.save()
			messages.success(request, 'account activated successfully')

			return redirect('login')
		return HttpResponse('THIS VERIFICATION CODE HAS ALREADY BEEN USED USE ANOTHER EMAIL TO CREATE AN ACCOUNT OR LOG IN WITH YOUR DETAILS')


def documentation(request):
    """
    Documentation page for Novustell Travel Django project
    """
    # Get project statistics for the documentation
    stats = {
        'total_destinations': Destination.objects.count(),
        'total_packages': Package.objects.count(),
        'total_accommodations': Accommodation.objects.count(),
        'total_blog_posts': Post.objects.count(),
        'total_categories': Category.objects.count(),
        'total_users': User.objects.count(),
        'published_posts': Post.objects.filter(status='published').count(),
        'featured_packages': Package.objects.filter(is_featured=True).count(),
        'active_destinations': Destination.objects.filter(is_active=True).count(),
    }

    # Get recent activity for dashboard
    recent_posts = Post.objects.filter(status='published').order_by('-date')[:5]
    recent_packages = Package.objects.filter(status='published').order_by('-created_at')[:5]

    context = {
        'stats': stats,
        'recent_posts': recent_posts,
        'recent_packages': recent_packages,
        'page_title': 'Novustell Travel System Guide',
        'page_description': 'Complete guide to using and managing the Novustell Travel website - from customer bookings to admin management, explained in simple terms for business users.',
    }

    return render(request, 'users/documentation.html', context)


@login_required
def user_profile(request):
    """
    User profile dashboard with booking history and account management
    """
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Get user's bookings
    bookings = Booking.objects.filter(user=user).order_by('-created_at')

    # Get bucket list items
    bucket_list = BucketList.objects.filter(user=user).order_by('-created_at')

    # Calculate statistics
    total_bookings = bookings.count()
    total_spent = sum(booking.total_amount for booking in bookings if booking.total_amount)
    upcoming_bookings = bookings.filter(status__in=['pending', 'confirmed']).count()

    context = {
        'user': user,
        'profile': profile,
        'bookings': bookings[:10],  # Show latest 10 bookings
        'bucket_list': bucket_list[:5],  # Show latest 5 bucket list items
        'total_bookings': total_bookings,
        'total_spent': total_spent,
        'upcoming_bookings': upcoming_bookings,
        'page_title': 'My Profile',
    }

    return render(request, 'users/user_profile.html', context)


@login_required
def edit_profile(request):
    """
    Edit user profile information
    """
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Update user basic info
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()

        # Update profile info
        profile.phone_number = request.POST.get('phone_number', '')
        profile.date_of_birth = request.POST.get('date_of_birth') or None
        profile.nationality = request.POST.get('nationality', '')
        profile.passport_number = request.POST.get('passport_number', '')
        profile.emergency_contact_name = request.POST.get('emergency_contact_name', '')
        profile.emergency_contact_phone = request.POST.get('emergency_contact_phone', '')
        profile.preferred_travel_style = request.POST.get('preferred_travel_style', '')
        profile.dietary_requirements = request.POST.get('dietary_requirements', '')
        profile.special_needs = request.POST.get('special_needs', '')
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        profile.marketing_emails = request.POST.get('marketing_emails') == 'on'
        profile.save()

        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('users:user_profile')

    context = {
        'user': user,
        'profile': profile,
        'page_title': 'Edit Profile',
    }

    return render(request, 'users/edit_profile.html', context)


@login_required
def change_password(request):
    """
    Change user password
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('users:user_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    context = {
        'form': form,
        'page_title': 'Change Password',
    }

    return render(request, 'users/change_password.html', context)


@login_required
def booking_history(request):
    """
    Detailed booking history for the user
    """
    user = request.user
    bookings = Booking.objects.filter(user=user).order_by('-created_at')

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        bookings = bookings.filter(
            Q(package__name__icontains=search_query) |
            Q(booking_reference__icontains=search_query) |
            Q(package__main_destination__name__icontains=search_query)
        )

    context = {
        'bookings': bookings,
        'status_filter': status_filter,
        'search_query': search_query,
        'page_title': 'Booking History',
    }

    return render(request, 'users/booking_history.html', context)


@login_required
def bucket_list_view(request):
    """
    User's travel bucket list
    """
    user = request.user
    bucket_list = BucketList.objects.filter(user=user).order_by('-created_at')

    # Filter by item type if provided
    item_type = request.GET.get('type')
    if item_type:
        bucket_list = bucket_list.filter(item_type=item_type)

    context = {
        'bucket_list': bucket_list,
        'item_type': item_type,
        'page_title': 'My Bucket List',
    }

    return render(request, 'users/bucket_list.html', context)


@login_required
def add_to_bucket_list(request):
    """
    Add item to user's bucket list via AJAX
    """
    if request.method == 'POST':
        item_type = request.POST.get('item_type')
        item_id = request.POST.get('item_id')
        notes = request.POST.get('notes', '')
        priority = request.POST.get('priority', 'medium')

        try:
            # Check if item already exists in bucket list
            existing_item = None
            if item_type == 'package':
                existing_item = BucketList.objects.filter(user=request.user, package_id=item_id).first()
            elif item_type == 'accommodation':
                existing_item = BucketList.objects.filter(user=request.user, accommodation_id=item_id).first()
            elif item_type == 'destination':
                existing_item = BucketList.objects.filter(user=request.user, destination_id=item_id).first()

            if existing_item:
                return JsonResponse({'success': False, 'message': 'Item already in your bucket list!'})

            # Create new bucket list item
            bucket_item = BucketList.objects.create(
                user=request.user,
                item_type=item_type,
                notes=notes,
                priority=priority
            )

            # Set the appropriate foreign key
            if item_type == 'package':
                bucket_item.package_id = item_id
            elif item_type == 'accommodation':
                bucket_item.accommodation_id = item_id
            elif item_type == 'destination':
                bucket_item.destination_id = item_id

            bucket_item.save()

            return JsonResponse({'success': True, 'message': 'Added to your bucket list!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def remove_from_bucket_list(request, item_id):
    """
    Remove item from user's bucket list
    """
    try:
        bucket_item = BucketList.objects.get(id=item_id, user=request.user)
        bucket_item.delete()
        messages.success(request, 'Item removed from your bucket list!')
    except BucketList.DoesNotExist:
        messages.error(request, 'Item not found in your bucket list.')

    return redirect('users:bucket_list')


@login_required
def booking_detail(request, booking_reference):
    """
    Detailed view of a specific booking
    """
    booking = get_object_or_404(Booking, booking_reference=booking_reference, user=request.user)

    context = {
        'booking': booking,
        'page_title': f'Booking {booking.booking_reference}',
    }

    return render(request, 'users/booking_detail.html', context)


@login_required
def add_to_bucket_list(request):
    """
    Add item to user's bucket list via AJAX
    """
    if request.method == 'POST':
        item_type = request.POST.get('item_type')
        item_id = request.POST.get('item_id')
        notes = request.POST.get('notes', '')
        priority = request.POST.get('priority', 'medium')

        try:
            # Check if item already exists in bucket list
            existing_item = None
            if item_type == 'package':
                existing_item = BucketList.objects.filter(user=request.user, package_id=item_id).first()
            elif item_type == 'accommodation':
                existing_item = BucketList.objects.filter(user=request.user, accommodation_id=item_id).first()
            elif item_type == 'destination':
                existing_item = BucketList.objects.filter(user=request.user, destination_id=item_id).first()

            if existing_item:
                return JsonResponse({'success': False, 'message': 'Item already in your bucket list!'})

            # Create new bucket list item
            bucket_item = BucketList.objects.create(
                user=request.user,
                item_type=item_type,
                notes=notes,
                priority=priority
            )

            # Set the appropriate foreign key
            if item_type == 'package':
                bucket_item.package_id = item_id
            elif item_type == 'accommodation':
                bucket_item.accommodation_id = item_id
            elif item_type == 'destination':
                bucket_item.destination_id = item_id

            bucket_item.save()

            return JsonResponse({'success': True, 'message': 'Added to your bucket list!'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required
def remove_from_bucket_list(request, item_id):
    """
    Remove item from user's bucket list
    """
    try:
        bucket_item = BucketList.objects.get(id=item_id, user=request.user)
        bucket_item.delete()
        messages.success(request, 'Item removed from your bucket list!')
    except BucketList.DoesNotExist:
        messages.error(request, 'Item not found in your bucket list.')

    return redirect('users:bucket_list')


@login_required
def booking_detail(request, booking_reference):
    """
    Detailed view of a specific booking
    """
    booking = get_object_or_404(Booking, booking_reference=booking_reference, user=request.user)

    context = {
        'booking': booking,
        'page_title': f'Booking {booking.booking_reference}',
    }

    return render(request, 'users/booking_detail.html', context)


def test_500_error(request):
    """
    Test view to trigger a 500 error for testing purposes
    Only works when DEBUG=False
    """
    raise Exception("This is a test 500 error for testing error pages")


# Test views removed - custom error pages are working correctly
# Error handlers are configured in tours_travels/urls.py and work when DEBUG=False


def get_active_popup(request):
    """
    API endpoint to get the active promotional popup
    Returns JSON data for the popup modal
    """
    from django.http import JsonResponse
    from .models import PromotionalPopup

    try:
        # Get the first active popup ordered by display_order
        popup = PromotionalPopup.objects.filter(is_active=True).first()

        if popup:
            # Increment view count
            popup.increment_view_count()

            return JsonResponse({
                'success': True,
                'popup': {
                    'id': popup.id,
                    'title': popup.title,
                    'image_url': popup.image.url if popup.image else '/static/images/novustelltravelplaceholder.svg',
                    'inquiry_button_text': popup.inquiry_button_text,
                    'inquiry_url': popup.get_inquiry_url(),
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No active popup available'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error loading popup: {str(e)}'
        })


@csrf_exempt
def track_popup_click(request):
    """
    API endpoint to track popup inquiry button clicks
    """
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    from django.views.decorators.http import require_POST
    from .models import PromotionalPopup
    import json

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            popup_id = data.get('popup_id')

            if popup_id:
                popup = PromotionalPopup.objects.get(id=popup_id, is_active=True)
                popup.increment_click_count()

                return JsonResponse({
                    'success': True,
                    'message': 'Click tracked successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Popup ID required'
                })

        except PromotionalPopup.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Popup not found'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error tracking click: {str(e)}'
            })

    return JsonResponse({
        'success': False,
        'message': 'POST method required'
    })
