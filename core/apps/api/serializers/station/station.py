from rest_framework import serializers

from core.apps.api.models import StationModel
from core.apps.api.serializers.station.connector import ListConnectorSerializer


class BaseStationSerializer(serializers.ModelSerializer):
    connectors = ListConnectorSerializer(many=True)

    class Meta:
        model = StationModel
        fields = [
            "id",
            "name",
            "cp_id",
            "connectors",
        ]


class ListStationSerializer(BaseStationSerializer):
    class Meta(BaseStationSerializer.Meta): ...


class RetrieveStationSerializer(BaseStationSerializer):
    class Meta(BaseStationSerializer.Meta): ...


class CreateStationSerializer(BaseStationSerializer):
    connectors = None

    class Meta(BaseStationSerializer.Meta):
        fields = [
            "id",
            "name",
            "cp_id",
        ]
