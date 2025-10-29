# type: ignore
from rest_framework import serializers

from core.apps.api.enums.connectors import ConnectorStatusEnum
from core.apps.api.enums.webhook import WebhookEvents
from core.apps.api.models.station import ConnectorModel, StationModel


class WebhookSerializer(serializers.Serializer):
    event = serializers.ChoiceField(choices=WebhookEvents.choices)
    data = serializers.DictField()


class ConnectorStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ConnectorStatusEnum.choices)
    station = serializers.PrimaryKeyRelatedField(queryset=StationModel.objects.all())
    connector = serializers.PrimaryKeyRelatedField(queryset=ConnectorModel.objects.all())
