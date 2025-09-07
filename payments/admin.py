# airbnb-clone-project/payments/admin.py

from django.contrib import admin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "booking",
        "amount",
        "payment_method",
        "status",
        "transaction_id",
        "created_at",
    )
    list_filter = ("payment_method", "status")
    search_fields = ("transaction_id",)
    ordering = ("-created_at",)
