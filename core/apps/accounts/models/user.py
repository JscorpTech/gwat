from django.contrib.auth import models as auth_models
from django.db import models

from ..choices import RoleChoice
from ..managers import UserManager


class User(auth_models.AbstractUser):
    phone = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    role = models.CharField(
        max_length=255,
        choices=RoleChoice,
        default=RoleChoice.USER,
    )
    station = models.ForeignKey(
        'api.StationModel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name='Station',
        help_text='Hodim biriktirilgan station (Faqat hodimlar uchun)'
    )

    USERNAME_FIELD = "phone"
    objects = UserManager()

    def __str__(self):
        return self.phone
    
    def get_accessible_stations(self):
        """User uchun accessible stationlarni qaytaradi"""
        if self.is_superuser or not self.station:
            # Superuser yoki station bog'lanmagan userlar hamma stationni ko'radi
            return None
        # Oddiy hodim faqat o'z stationini ko'radi
        return [self.station.id]
    
    def get_accessible_chargers(self):
        """User uchun accessible chargerlarni qaytaradi"""
        if self.is_superuser or not self.station:
            return None
        # Hodim faqat o'z stationidagi chargerlarni ko'radi
        from core.apps.api.models.station import ChargerModel
        return ChargerModel.objects.filter(station=self.station).values_list('id', flat=True)
    
    def get_accessible_connectors(self):
        """User uchun accessible connectorlarni qaytaradi"""
        if self.is_superuser or not self.station:
            return None
        # Hodim faqat o'z stationidagi connectorlarni ko'radi
        from core.apps.api.models.station import ConnectorModel
        return ConnectorModel.objects.filter(charger__station=self.station).values_list('id', flat=True)
    
    def get_accessible_transactions(self):
        """User uchun accessible transactionlarni qaytaradi"""
        if self.is_superuser or not self.station:
            return None
        # Hodim faqat o'z stationidagi transactionlarni ko'radi
        from core.apps.api.models.transaction import TransactionModel
        return TransactionModel.objects.filter(conn__charger__station=self.station).values_list('id', flat=True)
