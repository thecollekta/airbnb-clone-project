# airbnb-clone-project/reviews/admin.py

from django.contrib import admin

from reviews.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("booking", "author", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("author__email", "booking__property__title")
    ordering = ("-created_at",)
