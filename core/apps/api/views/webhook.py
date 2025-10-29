# type: ignore
from rest_framework.fields import ValidationError
from rest_framework.views import Response
from rest_framework.viewsets import GenericViewSet

from core.apps.api.enums.webhook import WebhookEvents
from core.apps.api.serializers.webhook.webhook import ConnectorStatusSerializer, WebhookSerializer
from django_core.mixins import BaseViewSetMixin


class WebhookView(BaseViewSetMixin, GenericViewSet):

    def create(self, request, *args, **kwargs):
        ser = WebhookSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        event_name = data.get("event")
        events = {
            WebhookEvents.CHANGE_CONNECTOR_STATUS.value: {
                "ser": ConnectorStatusSerializer,
                "handler": lambda m: "💀",
            },
        }
        event = events.get(event_name)
        if event is None:
            raise ValidationError(detail={"event": "invalid event"})
        ser = event.get("ser")(data=data.get("data"))
        if not ser.is_valid():
            return Response(data={"data": ser.errors})
        result = event.get("handler")(1)
        return Response(data={"detail": result})
