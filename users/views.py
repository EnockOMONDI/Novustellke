from django.shortcuts import render,redirect,HttpResponse
from django.http import Http404

from django.contrib import messages
from adminside.models import *
from users.models import *
from .forms import UserRegisterForm
from django.http import HttpResponseRedirect
from django.http import JsonResponse
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

def holidays(request):
    
    return render(request, 'users/holidays.html')

def contactus(request):
    
    return render(request, 'users/contactus.html')
		
def home(request):
	dests1 = Destination.objects.all()  # Retrieve all destinations from the database
	dests=Destination.objects.all()
	package1=Package.objects.all()
	packs=Package.objects.all().order_by('number_of_times_booked')
	nights=[]
	price=[]
	travel=[]
	
		
	destinations=zip(dests)

	for i in packs:
		nights.append(i.number_of_days-1)
		price.append(i.adult_price+i.accomodation.price_per_room)
		mode=i.travel.travelling_mode
		if(mode=="TN"):
			travel.append("Train")
		elif(mode=="FT"):
			travel.append("Flight")
		else:
			travel.append("Bus")
		

	
	packages=zip(packs,nights,price,travel)
	

	context={'dests':destinations,'dests1': dests1, 'package1':package1, 'packages':packages}
	print(packs)

	
	return render(request,'users/index.html',context)




def destination(request,id):
	id=id
	dest=Destination.objects.get(id=id)
	packs=dest.package_set.all()
	nights=[]
	price=[]
	travel=[]
	
	for i in packs:
		nights.append(i.number_of_days-1)
		price.append(i.adult_price+i.accomodation.price_per_room)
		mode=i.travel.travelling_mode
		if(mode=="TN"):
			travel.append("Train")
		elif(mode=="FT"):
			travel.append("Flight")
		else:
			travel.append("Bus")
	
	
	packages=zip(packs,nights,price,travel)




	context={'dest':dest,'packages':packages}
	
	return render(request,'users/destination.html',context)



def search(request):
	try:
		name=request.POST.get('search','')
		name=name.lstrip()
		name=name.rstrip()
		dest=Destination.objects.filter(city__icontains=name) | Destination.objects.filter(state__icontains=name) | Destination.objects.filter(city__icontains=name)	
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
            package = Package.objects.get(pk=package_id)
            package_name = package.package_name
            destination_name = package.destination.name
            booked = package.number_of_times_booked
            no_of_days = package.number_of_days
            destination_description = package.destination.dtn_description
            package_description = package.description

            # Travelling details
            travel_mode = package.travel.travelling_mode
            travel_price = package.travel.price_per_person

            # Accommodation Details
            hotel_name = package.accomodation.hotel_name
            hotel_description = package.accomodation.hotel_description
            price_per_room = package.accomodation.price_per_room

            # Inclusive
            inclusive = package.inclusive
            exclusive = package.exclusive

            # Itinerary
            itinerary = Itinerary.objects.get(package=package)
            itinerary_description = itinerary.itinerarydescription_set.all() # list of itinerary days

            # Images
            package_image = package.Image

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

    return render(request, 'users/packagedetail.html', context)


def bookings(request):
	user_id=request.user.id
	context = {}
	if request.method == 'POST':
		user=user_id
		package=request.POST['package_id']
		package=Package.objects.get(pk=package)
		number_of_adults = request.POST['adults']
		number_of_children =request.POST['children']
		number_of_rooms =request.POST['rooms']
		booking_date=request.POST['date']
		include_travelling=request.POST.get('travel')
		if include_travelling:
			include_travelling=True
			total_amount=(package.adult_price * int(number_of_adults)) + (package.child_price * int(number_of_children)) + (package.travel.price_per_person *(int(number_of_adults)+int(number_of_children)))+(package.accomodation.price_per_room*int(number_of_rooms))
			print(total_amount)
		else:
			include_travelling=False
			total_amount=(package.adult_price * int(number_of_adults)) + (package.child_price * int(number_of_children)) + (package.accomodation.price_per_room*int(number_of_rooms))
			print(total_amount)
		bookings=UserBookings(user=request.user,package=package,number_of_adults=number_of_adults,number_of_children=number_of_children,number_of_rooms=number_of_rooms,booking_date=booking_date,include_travelling=include_travelling,paid=False,total_amount=total_amount)
		bookings.save()
		
		return redirect('users:users-home')
		
	else:
		return redirect('users:users-home')


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








     