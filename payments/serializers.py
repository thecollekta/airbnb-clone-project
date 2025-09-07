# airbnb-clone-project/payments/serializers.py

from rest_framework import serializers

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "booking",
            "amount",
            "payment_method",
            "transaction_id",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
