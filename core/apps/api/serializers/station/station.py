from rest_framework import serializers

from core.apps.api.models import ChargerModel
from core.apps.api.serializers.station.connector import ListConnectorSerializer


class BaseChargerSerializer(serializers.ModelSerializer):
    connectors = ListConnectorSerializer(many=True)

    class Meta:
        model = ChargerModel
        fields = [
            "id",
            "name",
            "cp_id",
            "last_health",
            "connectors",
        ]


class ListChargerSerializer(BaseChargerSerializer):
    class Meta(BaseChargerSerializer.Meta): ...


class RetrieveChargerSerializer(BaseChargerSerializer):
    class Meta(BaseChargerSerializer.Meta): ...


class CreateChargerSerializer(BaseChargerSerializer):
    connectors = None

    class Meta(BaseChargerSerializer.Meta):
        fields = [
            "id",
            "name",
            "cp_id",
        ]
