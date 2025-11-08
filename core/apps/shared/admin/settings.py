from django.contrib import admin
from unfold.admin import ModelAdmin, StackedInline
from core.apps.shared.models import SettingsModel, OptionsModel
from unfold.contrib.forms.widgets import ArrayWidget
from django.contrib.postgres.fields import ArrayField

from core.apps.shared.models.settings import PriceRangeModel


class OptionsInline(StackedInline):
    model = OptionsModel
    extra = 1
    formfield_overrides = {
        ArrayField: {"widget": ArrayWidget},
    }


@admin.register(SettingsModel)
class SettingsAdmin(ModelAdmin):
    list_display = ["id", "key"]
    inlines = [OptionsInline]


@admin.register(PriceRangeModel)
class PriceRangeAdmin(ModelAdmin):
    list_display = ["id", "price", "start", "stop"]
