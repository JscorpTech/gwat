from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ConnectorView, StationView

router = DefaultRouter()
router.register("connector", ConnectorView, basename="connector")
router.register("station", StationView, basename="station")
urlpatterns = [path("", include(router.urls))]
