from rest_framework import serializers

from core.apps.api.models import ConnectorModel


class BaseConnectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectorModel
        fields = [
            "id",
            "name",
            "conn_id",
        ]


class ListConnectorSerializer(BaseConnectorSerializer):
    class Meta(BaseConnectorSerializer.Meta): ...


class RetrieveConnectorSerializer(BaseConnectorSerializer):
    class Meta(BaseConnectorSerializer.Meta): ...


class CreateConnectorSerializer(BaseConnectorSerializer):
    class Meta(BaseConnectorSerializer.Meta):
        fields = [
            "id",
            "name",
            "conn_id",
        ]
