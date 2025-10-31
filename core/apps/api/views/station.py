from django_core.mixins import BaseViewSetMixin
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from core.apps.api.models import ChargerModel
from core.apps.api.serializers.station import CreateChargerSerializer, ListChargerSerializer, RetrieveChargerSerializer


@extend_schema(tags=["charger"])
class ChargerView(BaseViewSetMixin, ReadOnlyModelViewSet):
    queryset = ChargerModel.objects.order_by("name")
    serializer_class = ListChargerSerializer
    permission_classes = [AllowAny]

    action_permission_classes = {}
    action_serializer_class = {
        "list": ListChargerSerializer,
        "retrieve": RetrieveChargerSerializer,
        "create": CreateChargerSerializer,
    }
