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


class MiniTransactionSerializer(BaseTransactionSerializer):
    class Meta:
        model = TransactionModel
        fields = [
            "id",
            "status",
            "tag",
        ]


class StopTransactionSerializer(serializers.Serializer):
    transaction = serializers.PrimaryKeyRelatedField(queryset=TransactionModel.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # User faqat o'z stationidagi transactionlarni to'xtata oladi
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            if user.is_authenticated:
                if not user.is_superuser and user.station:
                    # Faqat o'z stationidagi transactionlar
                    self.fields["transaction"] = serializers.PrimaryKeyRelatedField(
                        queryset=TransactionModel.objects.filter(conn__charger__station=user.station)
                    )
                else:
                    # Barcha transactionlar
                    self.fields["transaction"] = serializers.PrimaryKeyRelatedField(
                        queryset=TransactionModel.objects.all()
                    )


class CreateTransactionSerializer(BaseTransactionSerializer):
    conn = None
    tag = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # User faqat o'z stationidagi connectorlarni tanlashi mumkin
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            from core.apps.api.models import ConnectorModel

            if user.is_authenticated:
                if not user.is_superuser and user.station:
                    # Faqat o'z stationidagi connectorlar
                    self.fields["conn"] = serializers.PrimaryKeyRelatedField(
                        queryset=ConnectorModel.objects.filter(charger__station=user.station)
                    )
                else:
                    # Barcha connectorlar
                    self.fields["conn"] = serializers.PrimaryKeyRelatedField(queryset=ConnectorModel.objects.all())

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
