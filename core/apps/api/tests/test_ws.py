from unittest.mock import patch
import pytest

from core.apps.api.models.station import ChargerModel, ConnectorModel
from core.apps.api.models.transaction import TransactionModel
from core.apps.api.services.ws import ws_connector_event, ws_health_event, ws_transaction_event


@pytest.fixture
def instance(db, tenant_context_fixture):
    return TransactionModel._baker()


@pytest.fixture
def charger(db, tenant_context_fixture):
    return ChargerModel._baker()


@pytest.fixture
def conn(db, tenant_context_fixture):
    return ConnectorModel._baker()


@pytest.fixture(autouse=True)
def mock_send_event():
    with patch("core.apps.api.services.ws.send_event") as mock_send_event:
        yield mock_send_event


def test_ws_transaction_event(instance: TransactionModel):
    ws_transaction_event(instance)


def test_ws_health_event(charger: ChargerModel):
    ws_health_event(charger)


def test_ws_connector_event(conn):
    ws_connector_event(conn)
