from rest_framework import serializers
from rest_framework.fields import ValidationError

from core.apps.api.enums.connectors import ConnectorStatusEnum
from core.apps.api.models import TransactionModel


class BaseTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = TransactionModel
        fields = [
            "id",
            "conn",
            "status",
            "limit",
            "amount",
            "is_active",
            "tag",
            "meter_start",
            "meter_stop",
            "meter_consumed",
            "amount",
            "soc",
            "start_date",
            "end_date",
        ]


class ListTransactionSerializer(BaseTransactionSerializer):
    class Meta(BaseTransactionSerializer.Meta): ...


class RetrieveTransactionSerializer(BaseTransactionSerializer):
    class Meta(BaseTransactionSerializer.Meta): ...


class StopTransactionSerializer(serializers.Serializer):
    transaction = serializers.PrimaryKeyRelatedField(queryset=TransactionModel.objects.all())


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
