from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Prefetch
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from .models import (
    Destination,
    Accommodation,
    TravelMode,
    Package,
    Itinerary,
    ItineraryDay,
    PackageBooking,
    Deal
)

# Destination Views
def destination_list(request):
    """List all destinations with hierarchy"""
    countries = Destination.objects.filter(
        destination_type=Destination.COUNTRY,
        is_active=True
    ).prefetch_related(
        Prefetch(
            'children',
            queryset=Destination.objects.filter(is_active=True).prefetch_related(
                Prefetch(
                    'children',
                    queryset=Destination.objects.filter(is_active=True)
                )
            )
        )
    ).order_by('display_order', 'name')

    context = {
        'countries': countries,
        'page_title': 'Destinations'
    }
    return render(request, 'adminside/destination_list.html', context)

def destination_detail(request, slug):
    """Detail view for a specific destination"""
    destination = get_object_or_404(
        Destination.objects.select_related('parent').prefetch_related('children'),
        slug=slug,
        is_active=True
    )

    # Get packages for this destination and its children
    destination_ids = [destination.id] + [child.id for child in destination.get_all_children()]
    packages = Package.objects.filter(
        main_destination_id__in=destination_ids,
        status=Package.PUBLISHED
    ).select_related('main_destination').prefetch_related('available_accommodations')[:12]

    # Get accommodations for this destination and its children
    accommodations = Accommodation.objects.filter(
        destination_id__in=destination_ids,
        is_active=True
    ).select_related('destination')[:12]

    context = {
        'destination': destination,
        'packages': packages,
        'accommodations': accommodations,
        'page_title': destination.name
    }
    return render(request, 'adminside/destination_detail.html', context)

# Package Views
def package_list(request):
    """Professional packages listing with category filtering and search"""
    packages = Package.objects.filter(status=Package.PUBLISHED).select_related('main_destination')

    # Category filtering
    category = request.GET.get('category', 'all')
    if category and category != 'all':
        if category == 'uganda':
            packages = packages.filter(main_destination__name__icontains='uganda')
        elif category == 'kenya':
            packages = packages.filter(main_destination__name__icontains='kenya')
        elif category == 'tanzania':
            packages = packages.filter(main_destination__name__icontains='tanzania')
        elif category == 'beach':
            packages = packages.filter(
                Q(name__icontains='beach') |
                Q(description__icontains='beach') |
                Q(name__icontains='coast') |
                Q(description__icontains='coast')
            )
        elif category == 'cultural':
            packages = packages.filter(
                Q(name__icontains='cultural') |
                Q(description__icontains='cultural') |
                Q(name__icontains='culture') |
                Q(description__icontains='culture')
            )
        elif category == 'adventure':
            packages = packages.filter(
                Q(name__icontains='adventure') |
                Q(description__icontains='adventure') |
                Q(name__icontains='hiking') |
                Q(description__icontains='hiking')
            )
        elif category == 'safari':
            packages = packages.filter(
                Q(name__icontains='safari') |
                Q(description__icontains='safari') |
                Q(name__icontains='wildlife') |
                Q(description__icontains='wildlife')
            )

    # Legacy destination filtering (for backward compatibility)
    destination_id = request.GET.get('destination')
    if destination_id:
        try:
            destination = Destination.objects.get(id=destination_id, is_active=True)
            # Include packages from this destination and all its children
            destination_ids = [destination.id] + [child.id for child in destination.get_all_children()]
            packages = packages.filter(main_destination_id__in=destination_ids)
        except Destination.DoesNotExist:
            pass

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        packages = packages.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(main_destination__name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(packages, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get destination hierarchy for sidebar
    countries = Destination.objects.filter(
        destination_type=Destination.COUNTRY,
        is_active=True
    ).prefetch_related(
        Prefetch(
            'children',
            queryset=Destination.objects.filter(is_active=True).prefetch_related(
                Prefetch(
                    'children',
                    queryset=Destination.objects.filter(is_active=True)
                )
            )
        )
    ).order_by('display_order', 'name')

    context = {
        'page_obj': page_obj,
        'countries': countries,
        'current_destination_id': destination_id,
        'search_query': search_query,
        'current_category': category,
        'page_title': 'Travel Packages'
    }
    return render(request, 'adminside/package_list.html', context)

def package_detail(request, slug):
    """Detail view for a specific package"""
    package = get_object_or_404(
        Package.objects.select_related('main_destination').prefetch_related(
            'available_accommodations',
            'available_travel_modes',
            'itinerary__days__destination',
            'itinerary__days__accommodation'
        ),
        slug=slug,
        status=Package.PUBLISHED
    )

    context = {
        'package': package,
        'page_title': package.name
    }
    return render(request, 'adminside/package_detail.html', context)

# Accommodation Views
def accommodation_list(request):
    """List accommodations with filtering by destination hierarchy"""
    accommodations = Accommodation.objects.filter(is_active=True).select_related('destination')

    # Filter by destination if provided
    destination_id = request.GET.get('destination')
    if destination_id:
        try:
            destination = Destination.objects.get(id=destination_id, is_active=True)
            # Include accommodations from this destination and all its children
            destination_ids = [destination.id] + [child.id for child in destination.get_all_children()]
            accommodations = accommodations.filter(destination_id__in=destination_ids)
        except Destination.DoesNotExist:
            pass

    # Filter by accommodation type
    accommodation_type = request.GET.get('type')
    if accommodation_type:
        accommodations = accommodations.filter(accommodation_type=accommodation_type)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        accommodations = accommodations.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(destination__name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(accommodations, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get destination hierarchy for sidebar
    countries = Destination.objects.filter(
        destination_type=Destination.COUNTRY,
        is_active=True
    ).prefetch_related(
        Prefetch(
            'children',
            queryset=Destination.objects.filter(is_active=True).prefetch_related(
                Prefetch(
                    'children',
                    queryset=Destination.objects.filter(is_active=True)
                )
            )
        )
    ).order_by('display_order', 'name')

    context = {
        'page_obj': page_obj,
        'countries': countries,
        'current_destination_id': destination_id,
        'current_type': accommodation_type,
        'search_query': search_query,
        'accommodation_types': Accommodation.ACCOMMODATION_TYPES,
        'page_title': 'Accommodations'
    }
    return render(request, 'adminside/accommodation_list.html', context)

def accommodation_detail(request, slug):
    """Detail view for a specific accommodation"""
    accommodation = get_object_or_404(
        Accommodation.objects.select_related('destination'),
        slug=slug,
        is_active=True
    )

    # Get related packages that include this accommodation
    related_packages = Package.objects.filter(
        available_accommodations=accommodation,
        status=Package.PUBLISHED
    ).select_related('main_destination')[:6]

    context = {
        'accommodation': accommodation,
        'related_packages': related_packages,
        'page_title': accommodation.name
    }
    return render(request, 'adminside/accommodation_detail.html', context)

# Travel Mode Views
def travel_mode_list(request):
    """List travel modes"""
    travel_modes = TravelMode.objects.filter(is_active=True)

    # Filter by transport type
    transport_type = request.GET.get('type')
    if transport_type:
        travel_modes = travel_modes.filter(transport_type=transport_type)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        travel_modes = travel_modes.filter(
            Q(name__icontains=search_query) |
            Q(departure_location__icontains=search_query) |
            Q(arrival_location__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(travel_modes, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'current_type': transport_type,
        'search_query': search_query,
        'transport_types': TravelMode.TRANSPORT_TYPES,
        'page_title': 'Travel Options'
    }
    return render(request, 'adminside/travel_mode_list.html', context)

# AJAX Views for dynamic filtering
def get_destinations_ajax(request):
    """AJAX endpoint to get destinations hierarchy"""
    parent_id = request.GET.get('parent_id')

    if parent_id:
        destinations = Destination.objects.filter(
            parent_id=parent_id,
            is_active=True
        ).order_by('display_order', 'name')
    else:
        destinations = Destination.objects.filter(
            destination_type=Destination.COUNTRY,
            is_active=True
        ).order_by('display_order', 'name')

    data = [{
        'id': dest.id,
        'name': dest.name,
        'type': dest.destination_type,
        'has_children': dest.children.filter(is_active=True).exists()
    } for dest in destinations]

    return JsonResponse({'destinations': data})

def get_packages_by_destination_ajax(request):
    """AJAX endpoint to get packages filtered by destination"""
    destination_id = request.GET.get('destination_id')

    if destination_id:
        try:
            destination = Destination.objects.get(id=destination_id, is_active=True)
            destination_ids = [destination.id] + [child.id for child in destination.get_all_children()]
            packages = Package.objects.filter(
                main_destination_id__in=destination_ids,
                status=Package.PUBLISHED
            ).select_related('main_destination')[:20]
        except Destination.DoesNotExist:
            packages = Package.objects.none()
    else:
        packages = Package.objects.filter(status=Package.PUBLISHED).select_related('main_destination')[:20]

    data = [{
        'id': pkg.id,
        'name': pkg.name,
        'slug': pkg.slug,
        'destination': pkg.main_destination.name,
        'duration_days': pkg.duration_days,
        'adult_price': pkg.adult_price,
        'image_url': pkg.featured_image.cdn_url if pkg.featured_image else None
    } for pkg in packages]

    return JsonResponse({'packages': data})

def get_accommodations_by_destination_ajax(request):
    """AJAX endpoint to get accommodations filtered by destination"""
    destination_id = request.GET.get('destination_id')

    if destination_id:
        try:
            destination = Destination.objects.get(id=destination_id, is_active=True)
            destination_ids = [destination.id] + [child.id for child in destination.get_all_children()]
            accommodations = Accommodation.objects.filter(
                destination_id__in=destination_ids,
                is_active=True
            ).select_related('destination')[:20]
        except Destination.DoesNotExist:
            accommodations = Accommodation.objects.none()
    else:
        accommodations = Accommodation.objects.filter(is_active=True).select_related('destination')[:20]

    data = [{
        'id': acc.id,
        'name': acc.name,
        'slug': acc.slug,
        'type': acc.accommodation_type,
        'destination': acc.destination.name,
        'price_per_room': acc.price_per_room_per_night,
        'rating': float(acc.rating),
        'image_url': acc.image.cdn_url if acc.image else None
    } for acc in accommodations]

    return JsonResponse({'accommodations': data})


def user_package_list(request):
    """User-friendly package list with enhanced navigation"""
    # Get all countries with their hierarchical structure
    countries = Destination.objects.filter(
        destination_type=Destination.COUNTRY,
        is_active=True
    ).prefetch_related(
        Prefetch(
            'children',
            queryset=Destination.objects.filter(is_active=True).prefetch_related(
                Prefetch(
                    'children',
                    queryset=Destination.objects.filter(is_active=True)
                )
            )
        )
    ).order_by('display_order', 'name')

    # Get all published packages with their destinations
    packages = Package.objects.filter(
        status=Package.PUBLISHED
    ).select_related(
        'main_destination'
    ).prefetch_related(
        'available_accommodations',
        'available_travel_modes'
    ).order_by('-is_featured', 'main_destination__name', 'name')

    # Apply search filter if provided
    search_query = request.GET.get('search', '').strip()
    if search_query:
        packages = packages.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(main_destination__name__icontains=search_query)
        )

    # Apply destination filter if provided
    destination_id = request.GET.get('destination')
    if destination_id:
        try:
            destination = Destination.objects.get(id=destination_id)
            # Include packages for this destination and all its children
            destination_ids = [destination.id] + [child.id for child in destination.get_all_children()]
            packages = packages.filter(
                main_destination_id__in=destination_ids
            ).distinct()
        except Destination.DoesNotExist:
            pass

    context = {
        'packages': packages,
        'countries': countries,
        'search_query': search_query,
        'current_destination_id': destination_id,
        'page_title': 'Holiday Packages'
    }

    return render(request, 'adminside/user_package_list.html', context)


# Deal Views
def deals_list(request):
    """List all active deals with filtering and pagination"""
    from django.utils import timezone

    deals = Deal.objects.filter(is_active=True).select_related().prefetch_related('related_packages')

    # Filter by validity
    show_expired = request.GET.get('show_expired', 'false').lower() == 'true'
    if not show_expired:
        deals = deals.filter(valid_until__gte=timezone.now())

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        deals = deals.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Filter by featured
    featured_only = request.GET.get('featured', 'false').lower() == 'true'
    if featured_only:
        deals = deals.filter(is_featured=True)

    # Order by featured first, then by creation date
    deals = deals.order_by('-is_featured', '-created_at')

    # Pagination
    paginator = Paginator(deals, 12)  # Show 12 deals per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'show_expired': show_expired,
        'featured_only': featured_only,
        'page_title': 'Special Deals & Offers'
    }
    return render(request, 'adminside/deals_list.html', context)


def deal_detail(request, slug):
    """Display individual deal details with related packages"""
    deal = get_object_or_404(Deal, slug=slug, is_active=True)

    # Get related packages
    related_packages = deal.related_packages.filter(status=Package.PUBLISHED)

    context = {
        'deal': deal,
        'related_packages': related_packages,
        'page_title': deal.title
    }
    return render(request, 'adminside/deal_detail.html', context)