from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_core.models import AbstractBaseModel
from model_bakery import baker
from django.contrib.auth import get_user_model

from core.apps.api.enums.connectors import ConnectorStatusEnum
from core.apps.api.enums.transaction import TransactionStatusEnum
from core.apps.api.models.station import ConnectorModel


User = get_user_model()


class TransactionModel(AbstractBaseModel):
    tag = models.CharField(_("idTag"), null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    conn = models.ForeignKey("ConnectorModel", on_delete=models.CASCADE, related_name="transactions")
    status = models.CharField(
        max_length=50, choices=TransactionStatusEnum.choices, default=TransactionStatusEnum.PENDING.value
    )
    amount = models.DecimalField(default=Decimal("0.00"), max_digits=20, decimal_places=2)
    limit = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    soc = models.SmallIntegerField(_("SoC (percent)"), default=0, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    meter_start = models.DecimalField(default=Decimal("0.00"), max_digits=20, decimal_places=10)
    meter_stop = models.DecimalField(default=Decimal("0.00"), max_digits=20, decimal_places=10)
    # meter_consumed ishlatilgan energiya
    meter_consumed = models.DecimalField(
        verbose_name=_("Meter consumed (Wh)"), default=Decimal("0.00"), max_digits=20, decimal_places=10
    )
    # last_meter oxirig yangilanishdagi Wh
    last_meter = models.DecimalField(verbose_name=_("Last meter (Wh)"), default=0, max_digits=20, decimal_places=10)

    # Majburiy to'xtatilganmi
    is_force_stop = models.BooleanField(_("IS Force stop"), default=False)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.pk)

    @classmethod
    def _baker(cls):
        return baker.make(
            cls, conn=ConnectorModel._baker(status=ConnectorStatusEnum.PREPARING.value), _fill_optional=True
        )

    class Meta:
        db_table = "transaction"
        verbose_name = _("TransactionModel")
        verbose_name_plural = _("TransactionModels")
