import logging
import pytest
from unittest.mock import MagicMock, patch
from core.apps.api.enums.connectors import ConnectorStatusEnum
from core.apps.api.enums.transaction import TransactionStatusEnum
from core.apps.api.models.station import ConnectorModel
from core.apps.api.models.transaction import TransactionModel
from core.apps.api.ocpp.handlers import OcppHandler
from core.apps.api.schemas.events import (
    ChangeConnectorStatus,
    Events,
    EventsEnum,
    Health,
    MeterValue,
    MeterValueData,
    SampledValue,
    StartTransaction,
    StopTransaction,
)
from core.apps.api.services.ocpp import (
    generate_tag,
    get_meter,
    parse_meter_values,
    remote_start_transaction,
    remote_stop_transaction,
    stop_transaction,
)


@pytest.fixture(autouse=True, scope="module")
def send_event_patch():
    with patch("core.apps.api.services.ws.send_event") as mock_event:
        yield mock_event


@pytest.fixture
def handler():
    return OcppHandler()


@pytest.fixture
def instance(db):
    instance = ConnectorModel._baker()
    return instance


@pytest.fixture
def meter_value(transaction: TransactionModel):
    return (
        MeterValue(
            conn=transaction.conn.pk,
            transaction_id=transaction.pk,
            meter_value=[
                MeterValueData(
                    sampledValue=[
                        SampledValue(
                            context="",
                            format="",
                            location="",
                            measurand="Energy.Active.Import.Register",
                            phase="",
                            unit="",
                            value="1000",
                        )
                    ],
                    timestamp="",
                )
            ],
        ),
        transaction,
    )


@pytest.fixture
def transaction(db):
    instance = TransactionModel._baker()
    return instance


def test_chage_status(handler: OcppHandler, instance: ConnectorModel):
    data = ChangeConnectorStatus(
        charger=instance.charger.cp_id,
        conn=instance.conn_id,
        status=ConnectorStatusEnum.AVAILABLE,
    )
    event = Events(event=EventsEnum.CHANGE_CONNECTOR_STATUS, data=data)
    handler.change_connector_status(event)


def test_start_transaction_event(handler: OcppHandler, transaction: TransactionModel):
    data = StartTransaction(
        charger=transaction.conn.charger.cp_id,
        conn=transaction.conn.conn_id,
        tag=transaction.tag if transaction.tag is not None else generate_tag(),
        meter_start=transaction.meter_start,
    )
    event = Events(event=EventsEnum.START_TRANSACTION, data=data)
    handler.start_transaction(event)


def test_stop_transaction_event(handler: OcppHandler, transaction: TransactionModel):
    data = StopTransaction(
        charger=transaction.conn.charger.cp_id,
        meter_stop=transaction.meter_stop,
        transaction_id=transaction.pk,
    )
    event = Events(event=EventsEnum.STOP_TRANSACTION, data=data)
    handler.stop_transaction(event)


def test_meter_value(handler: OcppHandler, meter_value):
    data, _ = meter_value
    event = Events(event=EventsEnum.STOP_TRANSACTION, data=data)
    handler.meter_value(event)


def test_health(handler: OcppHandler, instance: ConnectorModel):
    data = Health(charger=str(instance.charger.cp_id))
    event = Events(event=EventsEnum.HEALTH, data=data)
    handler.health(event)


@patch("core.apps.api.services.ocpp.client")
def test_remote_start_transaction(mock_client, transaction: TransactionModel):
    mock_client.rpush = MagicMock()
    remote_start_transaction(transaction.conn.charger.pk, transaction.conn.pk, transaction.tag)
    mock_client.rpush.assert_called()


@patch("core.apps.api.services.ocpp.client")
def test_remote_stop_transaction(mock_client, transaction: TransactionModel):
    mock_client.rpush = MagicMock()
    remote_stop_transaction(transaction.conn.charger.pk, transaction.pk)
    mock_client.rpush.assert_called()


def test_parse_meter_values(meter_value):
    res = parse_meter_values(meter_value[0].meter_value)
    assert len(res) > 0
    assert "Energy.Active.Import.Register" in res[0]


def test_get_meter(meter_value):
    values = parse_meter_values(meter_value[0].meter_value)
    res = get_meter(values[0])
    assert 1000 == res


def test_stop_transaction(transaction: TransactionModel):
    data = StopTransaction(
        charger=transaction.conn.charger.cp_id,
        meter_stop=transaction.meter_stop,
        transaction_id=transaction.pk,
    )
    stop_transaction(transaction, TransactionStatusEnum.PENDING, data)
