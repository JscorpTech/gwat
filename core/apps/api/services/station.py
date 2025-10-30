from core.apps.api.models.transaction import TransactionModel
from random import randrange


def generate_tag(length=10):
    chars = "1234567890qwertyuiopasdfghjklzxcvbnm"
    tag = "".join([chars[randrange(1, len(chars))] for _ in range(length)])
    if TransactionModel.objects.filter(tag=tag).exists():
        return generate_tag()
    return tag
