from django.db.models import TextChoices


class TransactionStatusEnum(TextChoices):
    CHARGING = "charging"
    FAIL = "fail"
    COMPLATE = "complate"
    STOP = "stop"
    PENDING = "pending"
