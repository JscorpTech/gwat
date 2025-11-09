from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    paid_until = models.DateField()
    on_trial = models.BooleanField()
    logo = models.FileField(upload_to="logo/", null=True, blank=True)
    created_on = models.DateField(auto_now_add=True)

    auto_create_schema = True


class Domain(DomainMixin):
    pass
