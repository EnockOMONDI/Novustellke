from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import (
    Destination,
    Accommodation,
    TravelMode,
    Package,
    Itinerary,
    ItineraryDay,
    PackageBooking
)
# CKEditor5Field automatically handles CKEditor 5 widgets based on config_name
# No need for explicit widget overrides

class DestinationAdminForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = '__all__'
        # RichTextField widgets are automatically configured

class AccommodationAdminForm(forms.ModelForm):
    class Meta:
        model = Accommodation
        fields = '__all__'
        # RichTextField widgets are automatically configured

class PackageAdminForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = '__all__'
        # RichTextField widgets are automatically configured

class ItineraryDayAdminForm(forms.ModelForm):
    class Meta:
        model = ItineraryDay
        fields = '__all__'
        # RichTextField widgets are automatically configured

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    form = DestinationAdminForm
    list_display = ('name', 'destination_type', 'parent', 'display_image', 'starting_price', 'display_order', 'is_featured', 'is_active')
    list_filter = ('destination_type', 'is_featured', 'is_active', 'parent')
    search_fields = ('name', 'description', 'meta_title')

    class Media:
        css = {
            'all': ('assets/css/ckeditor5-admin.css',)
        }
    list_per_page = 20
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('display_order', 'is_featured', 'is_active')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'destination_type', 'parent')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('wide',)
        }),
        ('Pricing', {
            'fields': ('starting_price',),
            'description': 'Set the starting price for packages to this destination'
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Display Options', {
            'fields': ('display_order', 'is_featured', 'is_active')
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/ckeditor5-admin.css',)
        }

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.image.cdn_url)
        return "No Image"
    display_image.short_description = 'Image'

@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    form = AccommodationAdminForm
    list_display = ('name', 'accommodation_type', 'destination', 'price_per_room_per_night', 'rating', 'is_featured', 'is_active')
    search_fields = ('name', 'description', 'destination__name')
    list_filter = ('accommodation_type', 'destination', 'is_featured', 'is_active', 'rating')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured', 'is_active')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'accommodation_type', 'destination')
        }),
        ('Location', {
            'fields': ('address',)
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('wide',)
        }),
        ('Pricing & Capacity', {
            'fields': ('price_per_room_per_night', 'max_occupancy_per_room', 'total_rooms')
        }),
        ('Features', {
            'fields': ('amenities',),
            'classes': ('wide',)
        }),
        ('Ratings & Status', {
            'fields': ('rating', 'total_reviews', 'is_featured', 'is_active')
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/ckeditor5-admin.css',)
        }

    def short_description(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    short_description.short_description = 'Description'

@admin.register(TravelMode)
class TravelModeAdmin(admin.ModelAdmin):
    list_display = ('name', 'transport_type', 'departure_location', 'arrival_location', 'departure_time', 'price_per_person', 'is_active')
    list_filter = ('transport_type', 'is_active', 'departure_location', 'arrival_location')
    search_fields = ('name', 'departure_location', 'arrival_location', 'description')
    list_editable = ('price_per_person', 'is_active')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'transport_type')
        }),
        ('Route', {
            'fields': ('departure_location', 'arrival_location')
        }),
        ('Timing', {
            'fields': ('departure_time', 'arrival_time', 'duration_minutes')
        }),
        ('Pricing', {
            'fields': ('price_per_person', 'child_discount_percentage')
        }),
        ('Details', {
            'fields': ('description', 'terms_and_conditions'),
            'classes': ('wide',)
        }),
        ('Capacity & Status', {
            'fields': ('total_capacity', 'is_active')
        }),
    )

class ItineraryDayInline(admin.TabularInline):
    form = ItineraryDayAdminForm
    model = ItineraryDay
    extra = 1
    ordering = ['day_number']
    fields = ('day_number', 'title', 'destination', 'accommodation', 'breakfast', 'lunch', 'dinner', 'description')

    class Media:
        css = {
            'all': ('admin/css/ckeditor5-admin.css',)
        }

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ('title', 'package', 'days_count')
    search_fields = ('title', 'package__name', 'overview')
    inlines = [ItineraryDayInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('package', 'title')
        }),
        ('Overview', {
            'fields': ('overview',),
            'classes': ('wide',)
        }),
    )

    def days_count(self, obj):
        return obj.days.count()
    days_count.short_description = 'Number of Days'

class PackageBookingInline(admin.TabularInline):
    model = PackageBooking
    extra = 0
    readonly_fields = ('created_at', 'total_amount')
    fields = ('user', 'selected_accommodation', 'selected_travel_mode', 'adults_count',
             'children_count', 'travel_date', 'status', 'total_amount', 'created_at')
    can_delete = False

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    form = PackageAdminForm
    list_display = ('name', 'display_image', 'main_destination', 'adult_price',
                   'child_price', 'duration_days', 'status', 'is_featured', 'total_bookings')
    list_filter = ('main_destination', 'status', 'is_featured', 'duration_days')
    search_fields = ('name', 'description', 'inclusions', 'exclusions')
    filter_horizontal = ('available_accommodations', 'available_travel_modes')
    readonly_fields = ('total_bookings', 'total_reviews')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('status', 'is_featured')
    inlines = [PackageBookingInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'main_destination', 'duration_days', 'duration_nights')
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('wide',)
        }),
        ('Pricing', {
            'fields': ('adult_price', 'child_price')
        }),
        ('Available Options', {
            'fields': ('available_accommodations', 'available_travel_modes')
        }),
        ('Package Details', {
            'fields': ('inclusions', 'exclusions'),
            'classes': ('wide',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Status & Statistics', {
            'fields': ('status', 'is_featured', 'published_at', 'total_bookings', 'rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/ckeditor5-admin.css',)
        }

    def display_image(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.featured_image.cdn_url)
        return "No Image"
    display_image.short_description = 'Image'

    def get_queryset(self, request):
        """Optimize queries by prefetching related fields"""
        return super().get_queryset(request).prefetch_related(
            'available_accommodations',
            'available_travel_modes',
            'package_bookings'
        ).select_related(
            'main_destination'
        )

@admin.register(ItineraryDay)
class ItineraryDayAdmin(admin.ModelAdmin):
    list_display = ('itinerary', 'day_number', 'title', 'destination', 'accommodation', 'meals_summary')
    list_filter = ('itinerary', 'destination', 'accommodation', 'breakfast', 'lunch', 'dinner')
    search_fields = ('itinerary__title', 'title', 'description')
    ordering = ['itinerary', 'day_number']

    def short_description(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    short_description.short_description = 'Description'

    def meals_summary(self, obj):
        meals = []
        if obj.breakfast: meals.append('B')
        if obj.lunch: meals.append('L')
        if obj.dinner: meals.append('D')
        return ', '.join(meals) if meals else 'No meals'
    meals_summary.short_description = 'Meals'

@admin.register(PackageBooking)
class PackageBookingAdmin(admin.ModelAdmin):
    list_display = ('package', 'user', 'travel_date', 'adults_count', 'children_count', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'travel_date', 'package', 'created_at')
    search_fields = ('package__name', 'user__username', 'user__email', 'special_requests')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'travel_date'

    fieldsets = (
        ('Booking Information', {
            'fields': ('package', 'user', 'travel_date')
        }),
        ('Selected Options', {
            'fields': ('selected_accommodation', 'selected_travel_mode')
        }),
        ('Guest Details', {
            'fields': ('adults_count', 'children_count')
        }),
        ('Pricing & Status', {
            'fields': ('total_amount', 'status')
        }),
        ('Additional Information', {
            'fields': ('special_requests',),
            'classes': ('wide',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Customize admin site header and title
admin.site.site_header = 'Novustell Travel Administration'
admin.site.site_title = 'Novustell Travel Admin Portal'
admin.site.index_title = 'Welcome to Novustell Travel Admin Portal'