from modeltranslation.translator import TranslationOptions, register

from core.apps.api.models import ConnectorModel, ChargerModel


@register(ChargerModel)
class ChargerTranslation(TranslationOptions):
    fields = []


@register(ConnectorModel)
class ConnectorTranslation(TranslationOptions):
    fields = []
