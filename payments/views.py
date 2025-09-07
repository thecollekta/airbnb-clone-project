# airbnb-clone-project/payments/views.py

from rest_framework import permissions, viewsets

from payments.models import Payment
from payments.serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("booking").all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    filterset_fields = ["payment_method", "status", "booking"]
    search_fields = ["transaction_id"]
    ordering_fields = ["created_at", "amount"]
    ordering = ["-created_at"]
