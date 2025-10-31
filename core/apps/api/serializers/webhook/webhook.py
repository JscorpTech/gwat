# type: ignore
from rest_framework import serializers

from core.apps.api.enums.connectors import ConnectorStatusEnum
from core.apps.api.enums.webhook import WebhookEvents
from core.apps.api.models.station import ConnectorModel, ChargerModel


class WebhookSerializer(serializers.Serializer):
    event = serializers.ChoiceField(choices=WebhookEvents.choices)
    data = serializers.DictField()


class ConnectorStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=ConnectorStatusEnum.choices)
    charger = serializers.PrimaryKeyRelatedField(queryset=ChargerModel.objects.all())
    connector = serializers.PrimaryKeyRelatedField(queryset=ConnectorModel.objects.all())
