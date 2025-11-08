from django_core.mixins import BaseViewSetMixin
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from core.apps.api.models import ChargerModel
from core.apps.api.serializers.station import CreateChargerSerializer, ListChargerSerializer, RetrieveChargerSerializer


@extend_schema(tags=["charger"])
class ChargerView(BaseViewSetMixin, ReadOnlyModelViewSet):
    queryset = ChargerModel.objects.order_by("name")
    serializer_class = ListChargerSerializer
    permission_classes = [IsAuthenticated]

    action_permission_classes = {}
    action_serializer_class = {
        "list": ListChargerSerializer,
        "retrieve": RetrieveChargerSerializer,
        "create": CreateChargerSerializer,
    }
    
    def get_queryset(self):
        """API user faqat o'z stationidagi chargerlarni ko'radi"""
        queryset = super().get_queryset()
        user = self.request.user
        
        if user.is_superuser or not user.station:
            # Superuser yoki station bog'lanmagan userlar hamma chargerlarni ko'radi
            return queryset
        
        # Oddiy user faqat o'z stationidagi chargerlarni ko'radi
        return queryset.filter(station=user.station)
