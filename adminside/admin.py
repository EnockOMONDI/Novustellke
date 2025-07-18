from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import (
    Destination,
    Accomodation,
    Travel,
    Package,
    Itinerary,
    ItineraryDescription
)
from users.models import UserBookings
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from ckeditor.widgets import CKEditorWidget

class DestinationAdminForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = '__all__'
        widgets = {
            'dtn_description': CKEditorWidget(config_name='default'),
        }

class AccomodationAdminForm(forms.ModelForm):
    class Meta:
        model = Accomodation
        fields = '__all__'
        widgets = {
            'hotel_description': CKEditorWidget(config_name='default'),
        }

class PackageAdminForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = '__all__'
        widgets = {
            'description': CKEditorWidget(config_name='default'),
            'inclusive': CKEditorWidget(config_name='default'),
            'exclusive': CKEditorWidget(config_name='default'),
        }

class ItineraryDescriptionAdminForm(forms.ModelForm):
    class Meta:
        model = ItineraryDescription
        fields = '__all__'
        widgets = {
            'itinerary_description': CKEditorWidget(config_name='default'),
        }

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    form = DestinationAdminForm
    list_display = ('name', 'state', 'city', 'display_image', 'parent', 'is_country')
    list_filter = ('state', 'parent')
    search_fields = ('name', 'state', 'city', 'dtn_description')
    list_per_page = 20

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'state', 'city', 'parent')
        }),
        ('Media', {
            'fields': ('Image',)
        }),
        ('Description', {
            'fields': ('dtn_description',),
            'classes': ('wide',)
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/ckeditor-admin.css',)
        }
        js = (
            'ckeditor/ckeditor/ckeditor.js',
        )
    
    def display_image(self, obj):
        if obj.Image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.Image.cdn_url)
        return "No Image"
    display_image.short_description = 'Image'

@admin.register(Accomodation)
class AccomodationAdmin(admin.ModelAdmin):
    form = AccomodationAdminForm
    list_display = ('hotel_name', 'price_per_room', 'short_description')
    search_fields = ('hotel_name', 'hotel_description')
    list_filter = ('price_per_room',)

    fieldsets = (
        ('Hotel Information', {
            'fields': ('hotel_name', 'price_per_room')
        }),
        ('Description', {
            'fields': ('hotel_description',),
            'classes': ('wide',)
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/ckeditor-admin.css',)
        }
        js = (
            'ckeditor/ckeditor/ckeditor.js',
        )

    def short_description(self, obj):
        return obj.hotel_description[:100] + '...' if len(obj.hotel_description) > 100 else obj.hotel_description
    short_description.short_description = 'Description'

@admin.register(Travel)
class TravelAdmin(admin.ModelAdmin):
    list_display = ('departure', 'arrival', 'travelling_mode', 'start_time', 'end_time', 'price_per_person')
    list_filter = ('travelling_mode', 'departure', 'arrival')
    search_fields = ('departure', 'arrival')
    list_editable = ('price_per_person',)
    date_hierarchy = 'start_time'

class ItineraryDescriptionInline(admin.TabularInline):
    form = ItineraryDescriptionAdminForm
    model = ItineraryDescription
    extra = 1
    ordering = ['day_number']

    class Media:
        css = {
            'all': ('admin/css/ckeditor-admin.css',)
        }
        js = (
            'ckeditor/ckeditor/ckeditor.js',
        )

@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ('itinerary_name', 'package', 'days_count')
    search_fields = ('itinerary_name', 'package__package_name')
    inlines = [ItineraryDescriptionInline]
    
    def days_count(self, obj):
        return obj.itinerarydescription_set.count()
    days_count.short_description = 'Number of Days'

class UserBookingsInline(admin.TabularInline):
    model = UserBookings
    extra = 0
    readonly_fields = ('booking_date',)
    fields = ('user', 'full_name', 'phone_number', 'number_of_adults', 
             'number_of_children', 'number_of_rooms', 'include_travelling', 
             'special_requests', 'paid', 'booking_date')
    can_delete = False

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    form = PackageAdminForm
    list_display = ('package_name', 'display_image', 'main_destination', 'adult_price',
                   'child_price', 'number_of_days', 'number_of_times_booked')
    list_filter = ('main_destination', 'number_of_days', 'accomodation')
    search_fields = ('package_name', 'description', 'inclusive', 'exclusive')
    filter_horizontal = ('sub_destinations',)
    readonly_fields = ('number_of_times_booked',)
    inlines = [UserBookingsInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('package_name', 'Image', 'number_of_days')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('wide',)
        }),
        ('Destinations', {
            'fields': ('main_destination', 'sub_destinations')
        }),
        ('Pricing', {
            'fields': ('adult_price', 'child_price')
        }),
        ('Services', {
            'fields': ('accomodation', 'travel')
        }),
        ('Package Details', {
            'fields': ('inclusive', 'exclusive'),
            'classes': ('wide',)
        }),
        ('Statistics', {
            'fields': ('number_of_times_booked',),
            'classes': ('collapse',)
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/ckeditor-admin.css',)
        }
        js = (
            'ckeditor/ckeditor/ckeditor.js',
        )
    
    def display_image(self, obj):
        if obj.Image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.Image.cdn_url)
        return "No Image"
    display_image.short_description = 'Image'

    def get_queryset(self, request):
        """Optimize queries by prefetching related fields"""
        return super().get_queryset(request).prefetch_related(
            'sub_destinations', 
            'bookings'
        ).select_related(
            'main_destination',
            'accomodation',
            'travel'
        )

@admin.register(ItineraryDescription)
class ItineraryDescriptionAdmin(admin.ModelAdmin):
    list_display = ('itinerary', 'day_number', 'short_description')
    list_filter = ('itinerary', 'day_number')
    search_fields = ('itinerary__itinerary_name', 'itinerary_description')
    ordering = ['itinerary', 'day_number']
    
    def short_description(self, obj):
        return obj.itinerary_description[:100] + '...' if len(obj.itinerary_description) > 100 else obj.itinerary_description
    short_description.short_description = 'Description'

# Customize admin site header and title
admin.site.site_header = 'Novustell Travel Administration'
admin.site.site_title = 'Novustell Travel Admin Portal'
admin.site.index_title = 'Welcome to Novustell Travel Admin Portal'