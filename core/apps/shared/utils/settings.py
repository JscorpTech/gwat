from decimal import Decimal
import logging
from core.apps.shared.models import OptionsModel
from typing import Optional
from django.utils.translation import gettext_lazy as _
from core.apps.shared.models import PriceRangeModel
from django.utils import timezone


def get_config(settings: str, key: str, default=None) -> Optional[str]:
    config = OptionsModel.objects.filter(settings__key=settings, key=key)
    if not config.exists():
        return default
    return config.first().value


def get_exchange_rate():
    exchange_rate = get_config("currency", "exchange_rate")
    if exchange_rate is None:
        raise Exception(_("USD kursi kiritilmagan iltimos adminga murojat qiling"))
    return float(exchange_rate[0])


def energy_price() -> Decimal:
    now = timezone.now()
    price = PriceRangeModel.objects.filter(start__lte=now, stop__gte=now).first()
    if price is not None:
        return price.price
    price = get_config("energy", "price", [0.0])
    if price is None:
        return Decimal("0.0")
    return Decimal(price[0])
