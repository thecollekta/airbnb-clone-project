# airbnb-clone-project/properties/admin.py

from django.contrib import admin

from properties.models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "city",
        "country",
        "price_per_night",
        "bedrooms",
        "host",
        "created_at",
    )
    list_filter = ("city", "country", "bedrooms")
    search_fields = ("title", "city", "host__email")
    ordering = ("-created_at",)
