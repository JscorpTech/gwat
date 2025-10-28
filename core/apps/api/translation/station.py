from modeltranslation.translator import TranslationOptions, register

from core.apps.api.models import ConnectorModel, StationModel


@register(StationModel)
class StationTranslation(TranslationOptions):
    fields = []


@register(ConnectorModel)
class ConnectorTranslation(TranslationOptions):
    fields = []
