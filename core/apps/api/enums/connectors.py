from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class ConnectorStatusEnum(TextChoices):
    AVAILABLE = "Available", _("Available")  # Zaryad porti tayyor, ishlatish mumkin
    PREPARING = "Preparing", _("Preparing")  # Zaryadlash jarayoniga tayyorlanmoqda
    CHARGING = "Charging", _("Charging")  # Zaryadlash jarayoni ketmoqda
    SUSPENDED_EV = "SuspendedEV", _("Suspended EV")  # Mashina tomonidan zaryad to‘xtatilgan
    SUSPENDED_EVSE = "SuspendedEVSE", _("Suspended EVSE")  # Stansiya tomonidan zaryad to‘xtatilgan
    FINISHING = "Finishing", _("Finishing")  # Zaryad tugayapti (kabel uzilmoqda)
    RESERVED = "Reserved", _("Reserved")  # Ushbu port oldindan bron qilingan
    UNAVAILABLE = "Unavailable", _("Unavailable")  # Port vaqtincha ishlamaydi (xizmatda)
    FAULTED = "Faulted", _("Faulted")  # Portda nosozlik mavjud
