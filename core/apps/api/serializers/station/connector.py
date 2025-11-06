from rest_framework import serializers

from core.apps.api.models import ConnectorModel
from core.apps.api.serializers.transaction.transaction import RetrieveTransactionSerializer
from core.apps.api.services.ocpp import connector_active_transaction


class BaseConnectorSerializer(serializers.ModelSerializer):
    transaction = serializers.SerializerMethodField()

    def get_transaction(self, obj):
        transaction = connector_active_transaction(obj)
        if transaction is None:
            return None
        return RetrieveTransactionSerializer(instance=transaction).data

    class Meta:
        model = ConnectorModel
        fields = (
            "id",
            "name",
            "status",
            "power",
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
