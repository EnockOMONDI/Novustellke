from django.contrib import admin
from django import forms
from .models import UserBookings, MICEInquiry, StudentTravelInquiry, NGOTravelInquiry
from ckeditor.widgets import CKEditorWidget

class UserBookingsAdminForm(forms.ModelForm):
    class Meta:
        model = UserBookings
        fields = '__all__'
        widgets = {
            'special_requests': CKEditorWidget(config_name='minimal'),
        }

class MICEInquiryAdminForm(forms.ModelForm):
    class Meta:
        model = MICEInquiry
        fields = '__all__'
        widgets = {
            'event_details': CKEditorWidget(config_name='default'),
        }

class StudentTravelInquiryAdminForm(forms.ModelForm):
    class Meta:
        model = StudentTravelInquiry
        fields = '__all__'
        widgets = {
            'travel_details': CKEditorWidget(config_name='default'),
        }

class NGOTravelInquiryAdminForm(forms.ModelForm):
    class Meta:
        model = NGOTravelInquiry
        fields = '__all__'
        widgets = {
            'travel_details': CKEditorWidget(config_name='default'),
        }

@admin.register(UserBookings)
class UserBookingsAdmin(admin.ModelAdmin):
    form = UserBookingsAdminForm
    list_display = ('full_name', 'package', 'user', 'booking_date', 'paid')
    list_filter = ('paid', 'booking_date', 'package')
    search_fields = ('full_name', 'phone_number', 'user__username', 'package__name')
    readonly_fields = ('booking_date',)
    date_hierarchy = 'booking_date'

    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'package', 'full_name', 'phone_number', 'booking_date')
        }),
        ('Trip Details', {
            'fields': ('number_of_adults', 'number_of_children', 'number_of_rooms',
                      'include_travelling')
        }),
        ('Additional Information', {
            'fields': ('special_requests', 'paid'),
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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'package')

@admin.register(MICEInquiry)
class MICEInquiryAdmin(admin.ModelAdmin):
    form = MICEInquiryAdminForm
    list_display = ('company_name', 'contact_person', 'event_type', 'attendees', 'created_at')
    list_filter = ('event_type', 'created_at')
    search_fields = ('company_name', 'contact_person', 'email')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'contact_person', 'email', 'phone_number')
        }),
        ('Event Details', {
            'fields': ('event_type', 'attendees', 'event_details'),
            'classes': ('wide',)
        }),
        ('System Information', {
            'fields': ('created_at',),
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

@admin.register(StudentTravelInquiry)
class StudentTravelInquiryAdmin(admin.ModelAdmin):
    form = StudentTravelInquiryAdminForm
    list_display = ('school_name', 'contact_person', 'program_stage', 'number_of_students', 'created_at')
    list_filter = ('program_stage', 'created_at')
    search_fields = ('school_name', 'contact_person', 'email')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('School Information', {
            'fields': ('school_name', 'contact_person', 'email', 'phone_number')
        }),
        ('Program Details', {
            'fields': ('program_stage', 'number_of_students', 'travel_details'),
            'classes': ('wide',)
        }),
        ('System Information', {
            'fields': ('created_at',),
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

@admin.register(NGOTravelInquiry)
class NGOTravelInquiryAdmin(admin.ModelAdmin):
    form = NGOTravelInquiryAdminForm
    list_display = ('organization_name', 'contact_person', 'travel_purpose', 'number_of_travelers', 'sustainability_requirements', 'created_at')
    list_filter = ('travel_purpose', 'sustainability_requirements', 'created_at')
    search_fields = ('organization_name', 'contact_person', 'email')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Organization Information', {
            'fields': ('organization_name', 'contact_person', 'email', 'phone_number')
        }),
        ('Travel Details', {
            'fields': ('travel_purpose', 'number_of_travelers', 'travel_details', 'sustainability_requirements'),
            'classes': ('wide',)
        }),
        ('System Information', {
            'fields': ('created_at',),
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