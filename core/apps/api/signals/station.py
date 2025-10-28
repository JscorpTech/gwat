from django.db.models.signals import post_save
from django.dispatch import receiver

from core.apps.api.models import ConnectorModel, StationModel


@receiver(post_save, sender=StationModel)
def StationSignal(sender, instance, created, **kwargs): ...


@receiver(post_save, sender=ConnectorModel)
def ConnectorSignal(sender, instance, created, **kwargs): ...
