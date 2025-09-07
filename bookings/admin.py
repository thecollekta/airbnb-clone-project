# airbnb-clone-project/bookings/admin.py

from django.contrib import admin

from bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "property",
        "guest",
        "check_in_date",
        "check_out_date",
        "status",
        "total_price",
    )
    list_filter = ("status", "check_in_date")
    search_fields = ("property__title", "guest__email")
    ordering = ("-check_in_date",)
