from django_core.mixins import BaseViewSetMixin
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from core.apps.api.models import StationModel
from core.apps.api.serializers.station import CreateStationSerializer, ListStationSerializer, RetrieveStationSerializer


@extend_schema(tags=["station"])
class StationView(BaseViewSetMixin, ReadOnlyModelViewSet):
    queryset = StationModel.objects.all()
    serializer_class = ListStationSerializer
    permission_classes = [AllowAny]

    action_permission_classes = {}
    action_serializer_class = {
        "list": ListStationSerializer,
        "retrieve": RetrieveStationSerializer,
        "create": CreateStationSerializer,
    }
