from modeltranslation.translator import TranslationOptions, register

from core.apps.api.models import TransactionModel


@register(TransactionModel)
class TransactionTranslation(TranslationOptions):
    fields = []
