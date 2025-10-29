from django.db import models
from django.utils.translation import gettext_lazy as _
from django_core.models import AbstractBaseModel
from model_bakery import baker

from core.apps.api.enums.connectors import ConnectorStatusEnum


class StationModel(AbstractBaseModel):
    name = models.CharField(_("name"))
    cp_id = models.PositiveBigIntegerField(editable=False, unique=True)

    def save(self, *args, **kwargs):
        if not self.cp_id:
            last = StationModel.objects.order_by("-cp_id").first()
            self.cp_id = (last.cp_id + 1) if last else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.pk)

    @classmethod
    def _baker(cls):
        return baker.make(cls)

    class Meta:
        db_table = "station"
        verbose_name = _("StationModel")
        verbose_name_plural = _("StationModels")


class ConnectorModel(AbstractBaseModel):
    conn_id = models.IntegerField()
    name = models.CharField(_("name"), max_length=10, null=True, blank=True)
    station = models.ForeignKey("StationModel", on_delete=models.CASCADE, related_name="connectors")
    status = models.CharField(
        _("status"), choices=ConnectorStatusEnum.choices, default=ConnectorStatusEnum.SUSPENDED_EV.value
    )

    def __str__(self):
        return str(self.pk)

    @classmethod
    def _baker(cls):
        return baker.make(cls)

    class Meta:
        db_table = "connector"
        verbose_name = _("ConnectorModel")
        verbose_name_plural = _("ConnectorModels")
