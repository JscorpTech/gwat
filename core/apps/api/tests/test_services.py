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


def test_generate_tag(db):
    res = generate_tag(11)
    assert len(res) == 11
