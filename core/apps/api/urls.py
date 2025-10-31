from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ChargerView, TransactionView, WebhookView

router = DefaultRouter()
router.register("transaction", TransactionView, basename="transaction")
router.register("charger", ChargerView, basename="charger")
router.register("webhook", WebhookView, basename="webhook")
urlpatterns = [path("", include(router.urls))]
