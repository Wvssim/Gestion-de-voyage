from django.contrib import admin
from .models import Travel, Booking

@admin.register(Travel)
class TravelAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'start_date', 'end_date', 'price', 'available_seats')
    list_filter = ('destination', 'start_date')
    search_fields = ('name', 'destination', 'description')
    date_hierarchy = 'start_date'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'travel', 'booking_date', 'num_seats', 'status')
    list_filter = ('status', 'booking_date')
    search_fields = ('user__username', 'travel__name')
    date_hierarchy = 'booking_date'
