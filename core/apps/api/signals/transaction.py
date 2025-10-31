from django.db.models.signals import post_save
from django.dispatch import receiver

from core.apps.api.models import TransactionModel


@receiver(post_save, sender=TransactionModel)
def TransactionSignal(sender, instance, created, **kwargs):
    if created:
        TransactionModel.objects.filter(is_active=True).exclude(pk=instance.pk).update(is_active=False)
