from django.db import models, connections
from django_tenants.models import TenantMixin, DomainMixin, post_schema_sync, schema_needs_to_be_sync
from django_tenants.utils import get_tenant_database_alias, schema_exists


class Client(TenantMixin):
    name = models.CharField(max_length=100)
    paid_until = models.DateField()
    on_trial = models.BooleanField()
    created_on = models.DateField(auto_now_add=True)

    auto_create_schema = True


class Domain(DomainMixin):
    pass
