from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.http import Http404
import os
import smtplib
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserBookings, UserProfile, BucketList, Booking
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q
from django.http import JsonResponse


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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
from .forms import MICEInquiryForm, StudentTravelInquiryForm, NGOTravelInquiryForm
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

# users/views.py


def micepage(request):
    if request.method == 'POST':
        form = MICEInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save()

            try:
                # Setup SMTP
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()

                # Use email credentials from settings
                sender_email = settings.EMAIL_HOST_USER
                password = settings.EMAIL_HOST_PASSWORD

                s.login(sender_email, password)
                msg = MIMEMultipart()

                # Email headers
                msg['From'] = f"Novustell Travel <{sender_email}>"
                msg['To'] = "technical@novustelltravel.com"
                msg['Subject'] = f"New MICE Inquiry from {inquiry.company_name}"

                # Create HTML content with better formatting
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                    <h2 style="color: #170b2c;">New MICE Inquiry</h2>
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
                        <p><strong>Company Name:</strong> {inquiry.company_name}</p>
                        <p><strong>Contact Person:</strong> {inquiry.contact_person}</p>
                        <p><strong>Email:</strong> {inquiry.email}</p>
                        <p><strong>Phone:</strong> {inquiry.phone_number}</p>
                        <p><strong>Event Type:</strong> {inquiry.event_type}</p>
                        <p><strong>Expected Attendees:</strong> {inquiry.attendees}</p>
                        <h3 style="color: #170b2c;">Event Details:</h3>
                        <p style="white-space: pre-wrap;">{inquiry.event_details}</p>
                    </div>
                    <p style="color: #666; font-size: 12px; margin-top: 20px;">
                        This inquiry was submitted through the MICE form on Novustell Travel website.
                    </p>
                </body>
                </html>
                """

                # Attach HTML content
                msg.attach(MIMEText(html_content, 'html'))

                # Send email
                s.send_message(msg)
                s.quit()

                messages.success(request, 'Thank you! Your MICE inquiry has been submitted successfully. We will contact you soon.')
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
                # Setup SMTP
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()

                # Use email credentials from settings
                sender_email = settings.EMAIL_HOST_USER
                password = settings.EMAIL_HOST_PASSWORD

                s.login(sender_email, password)
                msg = MIMEMultipart()

                # Email headers
                msg['From'] = f"Novustell Travel <{sender_email}>"
                msg['To'] = "technical@novustelltravel.com"
                msg['Subject'] = f"New Student Travel Inquiry from {inquiry.school_name}"

                # Create HTML content with better formatting
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                    <h2 style="color: #170b2c;">New Student Travel Inquiry</h2>
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
                        <p><strong>School Name:</strong> {inquiry.school_name}</p>
                        <p><strong>Contact Person:</strong> {inquiry.contact_person}</p>
                        <p><strong>Email:</strong> {inquiry.email}</p>
                        <p><strong>Phone:</strong> {inquiry.phone_number}</p>
                        <p><strong>Program Stage:</strong> {inquiry.program_stage}</p>
                        <p><strong>Number of Students:</strong> {inquiry.number_of_students}</p>
                        <h3 style="color: #170b2c;">Travel Details:</h3>
                        <p style="white-space: pre-wrap;">{inquiry.travel_details}</p>
                    </div>
                    <p style="color: #666; font-size: 12px; margin-top: 20px;">
                        This inquiry was submitted through the Student Travel form on Novustell Travel website.
                    </p>
                </body>
                </html>
                """

                # Attach HTML content
                msg.attach(MIMEText(html_content, 'html'))

                # Send email
                s.send_message(msg)
                s.quit()

                messages.success(request, 'Thank you! Your student travel inquiry has been submitted successfully. We will contact you soon.')
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
                # Setup SMTP
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()

                # Use email credentials from settings
                sender_email = settings.EMAIL_HOST_USER
                password = settings.EMAIL_HOST_PASSWORD

                s.login(sender_email, password)
                msg = MIMEMultipart()

                # Email headers
                msg['From'] = f"Novustell Travel <{sender_email}>"
                msg['To'] = "technical@novustelltravel.com"
                msg['Subject'] = f"New NGO Travel Inquiry from {inquiry.organization_name}"

                # Create HTML content with better formatting
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                    <h2 style="color: #170b2c;">New NGO Travel Inquiry</h2>
                    <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px;">
                        <p><strong>Organization Name:</strong> {inquiry.organization_name}</p>
                        <p><strong>Contact Person:</strong> {inquiry.contact_person}</p>
                        <p><strong>Email:</strong> {inquiry.email}</p>
                        <p><strong>Phone:</strong> {inquiry.phone_number}</p>
                        <p><strong>Organization Type:</strong> {inquiry.organization_type}</p>
                        <p><strong>Travel Purpose:</strong> {inquiry.travel_purpose}</p>
                        <p><strong>Number of Travelers:</strong> {inquiry.number_of_travelers}</p>
                        <p><strong>Sustainability Requirements:</strong> {'Yes' if inquiry.sustainability_requirements else 'No'}</p>
                        <h3 style="color: #170b2c;">Travel Details:</h3>
                        <p style="white-space: pre-wrap;">{inquiry.travel_details}</p>
                    </div>
                    <p style="color: #666; font-size: 12px; margin-top: 20px;">
                        This inquiry was submitted through the NGO Travel form on Novustell Travel website.
                    </p>
                </body>
                </html>
                """

                # Attach HTML content
                msg.attach(MIMEText(html_content, 'html'))

                # Send email
                s.send_message(msg)
                s.quit()

                messages.success(request, 'Thank you! Your NGO travel inquiry has been submitted successfully. We will contact you soon.')
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

    return render(request, 'users/contactus.html')

def home(request):
	dests1 = Destination.objects.all()  # Retrieve all destinations from the database
	dests=Destination.objects.all()
	package1=Package.objects.all()
	packs=Package.objects.filter(status=Package.PUBLISHED).order_by('total_bookings')
	nights=[]
	price=[]
	travel=[]


	destinations=zip(dests)

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

	# Get featured destinations for homepage
	featured_destinations = Destination.objects.filter(is_featured=True, is_active=True).order_by('name')

	context={'dests':destinations,'dests1': dests1, 'package1':package1, 'packages':packages, 'featured_destinations': featured_destinations}
	print(packs)


	return render(request,'users/index.html',context)






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

def all_packages(request):
    packages = Package.objects.all()
    return render(request, 'users/package_list.html', {'packages': packages})

def detail_package(request, package_id):
    if request.user.is_authenticated:
        try:
            package = get_object_or_404(Package, id=package_id)
            package_name = package.name
            destination_name = package.main_destination.name
            booked = package.total_bookings
            no_of_days = package.duration_days
            destination_description = package.main_destination.description
            package_description = package.description

            # Travelling details - get first available travel mode
            travel_mode = package.available_travel_modes.first().name if package.available_travel_modes.exists() else "N/A"
            travel_price = package.available_travel_modes.first().price_per_person if package.available_travel_modes.exists() else 0

            # accommodation Details - get first available accommodation
            first_accommodation = package.available_accommodations.first()
            hotel_name = first_accommodation.name if first_accommodation else "N/A"
            hotel_description = first_accommodation.description if first_accommodation else "N/A"
            price_per_room = first_accommodation.price_per_room_per_night if first_accommodation else 0

            # Inclusive
            inclusive = package.inclusions
            exclusive = package.exclusions

            # Itinerary
            try:
                itinerary = Itinerary.objects.get(package=package)
                itinerary_description = itinerary.days.all().order_by('day_number') # list of itinerary days
            except Itinerary.DoesNotExist:
                itinerary_description = []

            # Images
            package_image = package.featured_image

            context = {
                'package': package,
                'package_name': package_name,
                'destination_name': destination_name,
                'no_of_days': no_of_days,
                'destination_description': destination_description,
                'package_description': package_description,
                'travel_mode': travel_mode,
                'travel_price': travel_price,
                'hotel_name': hotel_name,
                'hotel_description': hotel_description,
                'price_per_room': price_per_room,
                'inclusive': inclusive,
                'exclusive': exclusive,
                'itinerary_description': itinerary_description,
                'package_image': package_image,
                'booked': booked  # Use the variable 'booked' here
            }
        except Package.DoesNotExist:
            raise Http404("Package does not exist.")
        except Itinerary.DoesNotExist:
            raise Http404("Itinerary does not exist.")
        except Exception as e:
            return HttpResponse(f"<h1>An error occurred in the database: {str(e)}</h1>")
    else:
        # Handle the case when the user is not authenticated
        return HttpResponse("<h1>You need to be logged in to view this page.</h1>")

    return render(request, 'users/packagedetail2.html', context)





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
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()

        # Use email credentials from settings
        sender_email = settings.EMAIL_HOST_USER
        password = settings.EMAIL_HOST_PASSWORD

        s.login(sender_email, password)

        # Email content
        msg = MIMEMultipart()
        msg['From'] = f"Novustell Travel <{sender_email}>"
        msg['To'] = "technical@novustelltravel.com"
        msg['Subject'] = f"New Booking: {booking.full_name} for {booking.package.name}"

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

        msg.attach(MIMEText(message, 'html'))

        # Send the email
        s.send_message(msg)
        s.quit()
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
        'page_title': 'Project Documentation',
        'page_description': 'Comprehensive documentation for the Novustell Travel Django project including architecture, user guides, and technical specifications.',
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
