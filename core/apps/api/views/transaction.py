from urllib.parse import urlsplit
from django_core.mixins import BaseViewSetMixin
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework import status
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response

from core.apps.api.enums.transaction import TransactionStatusEnum
from core.apps.api.filters.transaction import TransactionFilter
from core.apps.api.models import TransactionModel
from core.apps.api.serializers.transaction import (
    CreateTransactionSerializer,
    ListTransactionSerializer,
    RetrieveTransactionSerializer,
)
from core.apps.api.serializers.transaction.transaction import MiniTransactionSerializer, StopTransactionSerializer
from core.apps.api.services.ocpp import generate_tag, remote_start_transaction, remote_stop_transaction
from django.utils import timezone
from rest_framework.decorators import action

from core.apps.api.services.ws import ws_transaction_event
from django_filters.rest_framework.backends import DjangoFilterBackend


@extend_schema(tags=["transaction"])
class TransactionView(BaseViewSetMixin, ListModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = TransactionModel.objects.order_by("-id")
    serializer_class = ListTransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TransactionFilter

    action_permission_classes = {"get_transaction_from_tag": [AllowAny]}
    action_serializer_class = {
        "list": ListTransactionSerializer,
        "retrieve": RetrieveTransactionSerializer,
        "get_transaction_from_tag": MiniTransactionSerializer,
        "start": CreateTransactionSerializer,
        "stop": StopTransactionSerializer,
        "clear": StopTransactionSerializer,
    }

    def get_queryset(self):
        """API user faqat o'z stationidagi transactionlarni ko'radi"""
        queryset = super().get_queryset()
        user = self.request.user
        if self.action == "get_transaction_from_tag":
            return queryset
        if user.is_authenticated:
            if user.is_superuser or not user.station:
                return queryset
            return queryset.filter(conn__charger__station=user.station)
        return queryset.none()

    @action(methods=["GET"], detail=False, url_name="tag", url_path="tag/(?P<tag>[^/.]+)")
    def get_transaction_from_tag(self, request, tag):
        queryset = self.filter_queryset(self.get_queryset())
        instance = get_object_or_404(queryset, tag=tag)
        return Response(data=self.get_serializer(instance=instance).data)

    @action(methods=["POST"], detail=False, url_name="start", url_path="start")
    def start(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        host = urlsplit(f"//{request.get_host()}").hostname
        conn = serializer.validated_data.get("conn")
        if conn is None:
            raise ValidationError(detail={"conn": "Connector is not found"})

        # User faqat o'z stationidagi connector orqali transaction boshlashi mumkin
        user = request.user
        if not user.is_superuser and user.station:
            if conn.charger.station != user.station:
                raise ValidationError(
                    detail={"conn": "You don't have permission to start transaction on this connector"}
                )

        tag = generate_tag()
        instance = serializer.save(start_date=timezone.now(), user=self.request.user, tag=tag)
        resp, msg = remote_start_transaction(host, conn.charger.cp_id, conn.conn_id, tag)
        if resp is not True:
            instance.status = TransactionStatusEnum.FAIL.value
            instance.is_active = False
            instance.save()
            return Response(data={"detail": msg, "status": resp}, status=status.HTTP_406_NOT_ACCEPTABLE)
        ws_transaction_event(instance, host)
        return Response({"detail": msg, "status": resp, "id": instance.pk}, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_name="stop", url_path="stop")
    def stop(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        host = urlsplit(f"//{request.get_host()}").hostname
        data = ser.validated_data
        transaction = data.get("transaction")

        # User faqat o'z stationidagi transactionni to'xtata oladi
        user = request.user
        if not user.is_superuser and user.station:
            if transaction.conn.charger.station != user.station:
                raise ValidationError(detail={"transaction": "You don't have permission to stop this transaction"})

        transaction.status = TransactionStatusEnum.PENDING.value
        transaction.save()
        resp, msg = remote_stop_transaction(host, transaction.conn.charger.cp_id, transaction.pk)
        if resp is not True:
            return Response(data={"detail": msg, "status": resp}, status=status.HTTP_406_NOT_ACCEPTABLE)
        ws_transaction_event(transaction, host)
        return Response(data={"status": resp, "detail": msg}, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_name="clear", url_path="clear")
    def clear(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        transaction = data.get("transaction")

        # User faqat o'z stationidagi transactionni clear qila oladi
        user = request.user
        if not user.is_superuser and user.station:
            if transaction.conn.charger.station != user.station:
                raise ValidationError(detail={"transaction": "You don't have permission to clear this transaction"})

        transaction.status = TransactionStatusEnum.COMPLATE.value
        transaction.is_active = False
        transaction.save()
        return Response(data={"detail": _("tozalandi")})
