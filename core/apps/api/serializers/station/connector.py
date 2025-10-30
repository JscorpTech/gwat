from rest_framework import serializers

from core.apps.api.enums.transaction import TransactionStatusEnum
from core.apps.api.models import ConnectorModel
from core.apps.api.models.transaction import TransactionModel
from core.apps.api.serializers.transaction.transaction import RetrieveTransactionSerializer


class BaseConnectorSerializer(serializers.ModelSerializer):
    transaction = serializers.SerializerMethodField()

    def get_transaction(self, obj):
        transaction = (
            TransactionModel.objects.filter(conn=obj, status=TransactionStatusEnum.CHARGING.value)
            .order_by("-id")
            .first()
        )
        if transaction is None:
            return None
        return RetrieveTransactionSerializer(instance=transaction).data

    class Meta:
        model = ConnectorModel
        fields = (
            "id",
            "name",
            "status",
            "conn_id",
            "transaction",
        )


class ListConnectorSerializer(BaseConnectorSerializer):
    class Meta(BaseConnectorSerializer.Meta): ...


class RetrieveConnectorSerializer(BaseConnectorSerializer):
    class Meta(BaseConnectorSerializer.Meta): ...


class CreateConnectorSerializer(BaseConnectorSerializer):
    transaction = None

    class Meta(BaseConnectorSerializer.Meta):
        fields = [
            "id",
            "name",
            "conn_id",
        ]
