from django.db.models import TextChoices


class WebhookEvents(TextChoices):
    CHANGE_CONNECTOR_STATUS = "change_connector_status"
