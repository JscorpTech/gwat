from datetime import datetime
from django_core.mixins import BaseViewSetMixin
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.apps.api.models import TransactionModel
from core.apps.api.serializers.transaction import (
    CreateTransactionSerializer,
    ListTransactionSerializer,
    RetrieveTransactionSerializer,
)
from core.apps.api.services.station import generate_tag


@extend_schema(tags=["transaction"])
class TransactionView(BaseViewSetMixin, ModelViewSet):
    queryset = TransactionModel.objects.order_by("-id")
    serializer_class = ListTransactionSerializer
    permission_classes = [IsAuthenticated]

    action_permission_classes = {}
    action_serializer_class = {
        "list": ListTransactionSerializer,
        "retrieve": RetrieveTransactionSerializer,
        "create": CreateTransactionSerializer,
    }

    def perform_create(self, serializer):
        serializer.save(start_date=datetime.now(), user=self.request.user, tag=generate_tag())
