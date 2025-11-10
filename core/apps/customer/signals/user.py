# type: ignore
from django.dispatch import receiver
from django.db.models.signals import post_save
from django_tenants.utils import schema_context

from core.apps.customer.models.tenants import Client
from django.contrib.auth import get_user_model
import logging
from django.db import transaction


User = get_user_model()


@receiver(post_save, sender=Client)
def client_signal(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: create_user(instance))


def create_user(instance):
    with schema_context(instance.schema_name):
        try:
            user = User.objects.create_superuser("998901234567", "changeme")
            logging.info("customer user created phone=%s" % user.phone)
        except Exception as e:
            logging.error("customer user create error: %s", e)
