from django_core.mixins import BaseViewSetMixin
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from core.apps.api.enums.transaction import TransactionStatusEnum
from core.apps.api.models import TransactionModel
from core.apps.api.serializers.transaction import (
    CreateTransactionSerializer,
    ListTransactionSerializer,
    RetrieveTransactionSerializer,
)
from core.apps.api.serializers.transaction.transaction import StopTransactionSerializer
from core.apps.api.services.ocpp import generate_tag, remote_start_transaction, remote_stop_transaction
from django.utils import timezone
from rest_framework.decorators import action

from core.apps.api.services.ws import ws_transaction_event


@extend_schema(tags=["transaction"])
class TransactionView(BaseViewSetMixin, ModelViewSet):
    queryset = TransactionModel.objects.order_by("-id")
    serializer_class = ListTransactionSerializer
    permission_classes = [IsAuthenticated]

    action_permission_classes = {"get_transaction_from_tag": [AllowAny]}
    action_serializer_class = {
        "list": ListTransactionSerializer,
        "retrieve": RetrieveTransactionSerializer,
        "get_transaction_from_tag": RetrieveTransactionSerializer,
        "create": CreateTransactionSerializer,
        "start": CreateTransactionSerializer,
        "stop": StopTransactionSerializer,
        "clear": StopTransactionSerializer,
    }

    def perform_create(self, serializer):
        conn = serializer.validated_data.get("conn")
        if conn is None:
            raise ValidationError(detail={"conn": "Connector is not found"})
        tag = generate_tag()
        remote_start_transaction(conn.charger.cp_id, conn.pk, tag)
        instance = serializer.save(start_date=timezone.now(), user=self.request.user, tag=tag)
        ws_transaction_event(instance)

    @action(methods=["GET"], detail=False, url_name="tag", url_path="tag/(?P<tag>[^/.]+)")
    def get_transaction_from_tag(self, request, tag):
        queryset = self.filter_queryset(self.get_queryset())
        instance = get_object_or_404(queryset, tag=tag)
        return Response(data=self.get_serializer(instance=instance).data)

    @action(methods=["POST"], detail=False, url_name="start", url_path="start")
    def start(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=["POST"], detail=False, url_name="stop", url_path="stop")
    def stop(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        transaction = data.get("transaction")
        transaction.status = TransactionStatusEnum.PENDING.value
        transaction.save()
        ws_transaction_event(transaction)
        remote_stop_transaction(transaction.conn.charger.cp_id, transaction.pk)
        return Response(data={"detail": _("transaction to'xtatildi")})

    @action(methods=["POST"], detail=False, url_name="clear", url_path="clear")
    def clear(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        transaction = data.get("transaction")
        transaction.status = TransactionStatusEnum.COMPLATE.value
        transaction.is_active = False
        transaction.save()
        return Response(data={"detail": _("tozalandi")})
