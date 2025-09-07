# airbnb-clone-project/amenities/admin.py

from django.contrib import admin

from amenities.models import Amenity


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    ordering = ("name",)
