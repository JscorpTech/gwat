from rest_framework import serializers
from rest_framework.fields import ValidationError

from core.apps.api.enums.connectors import ConnectorStatusEnum
from core.apps.api.models import TransactionModel
from core.apps.api.serializers.station.connector import RetrieveConnectorSerializer


class BaseTransactionSerializer(serializers.ModelSerializer):
    conn = RetrieveConnectorSerializer()

    class Meta:
        model = TransactionModel
        fields = [
            "id",
            "conn",
            "status",
            "amount",
            "energy",
            "tag",
            "start_date",
            "end_date",
        ]


class ListTransactionSerializer(BaseTransactionSerializer):
    class Meta(BaseTransactionSerializer.Meta): ...


class RetrieveTransactionSerializer(BaseTransactionSerializer):
    class Meta(BaseTransactionSerializer.Meta): ...


class CreateTransactionSerializer(BaseTransactionSerializer):
    conn = None
    tag = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)

    def validate(self, attrs):
        conn = attrs.get("conn")
        if conn.status not in ConnectorStatusEnum.active():
            raise ValidationError(detail={"conn": "Connector quvvatlash uchun mos statusda emas"})
        return attrs

    class Meta(BaseTransactionSerializer.Meta):
        fields = [
            "id",
            "conn",
            "limit",
            "tag",
            "status",
        ]
