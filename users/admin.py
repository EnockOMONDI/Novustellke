from django.contrib import admin
from .models import UserBookings

@admin.register(UserBookings)
class UserBookingsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'package', 'user', 'booking_date', 'paid')
    list_filter = ('paid', 'booking_date', 'package')
    search_fields = ('full_name', 'phone_number', 'user__username', 'package__package_name')
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
            'fields': ('special_requests', 'paid')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'package')