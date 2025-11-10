import logging
from core.apps.api.models.transaction import TransactionModel
from core.apps.api.services.ocpp import generate_str, generate_tag
import pytest


@pytest.fixture
def instance(db, tenant_context_fixture):
    return TransactionModel._baker()


def test_generate_str():
    res = generate_str()
    assert len(res) == 10


@pytest.mark.parametrize("length", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 100])
def test_generate_tag(db, length):
    res = generate_tag(length)
    assert len(res) == length
