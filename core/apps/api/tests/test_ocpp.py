import logging
from threading import Event
import pytest
from unittest.mock import MagicMock, patch
from core.apps.api.enums.connectors import ConnectorStatusEnum
from core.apps.api.enums.transaction import TransactionStatusEnum
from core.apps.api.models.station import ConnectorModel
from core.apps.api.models.transaction import TransactionModel
from core.apps.api.ocpp.handlers import OcppHandler
from core.apps.api.schemas.events import (
    ChangeConnectorStatus,
    ConnectCharger,
    DisconnectCharger,
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


@pytest.fixture(scope="module")
def send_event_patch():
    with patch("core.apps.api.services.ws.send_event") as mock_event:
        yield mock_event


@pytest.fixture
def handler():
    return OcppHandler()


@pytest.fixture
def instance(db, tenant_context_fixture):
    instance = ConnectorModel._baker()
    return instance


@pytest.fixture
def meter_value(transaction: TransactionModel, tenant_context_fixture):
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
def transaction(db, tenant_context_fixture):
    instance = TransactionModel._baker()
    return instance


def test_change_status(handler: OcppHandler, instance: ConnectorModel, send_event_patch):
    data = ChangeConnectorStatus(
        charger="test.localhost:%s" % instance.charger.cp_id,
        conn=instance.conn_id,
        status=ConnectorStatusEnum.AVAILABLE,
    )
    event = Events(event=EventsEnum.CHANGE_CONNECTOR_STATUS, data=data, domain="test.localhost")
    handler.change_connector_status(event, "test.localhost")
    send_event_patch.assert_called()


def test_start_transaction_event(handler: OcppHandler, transaction: TransactionModel, send_event_patch):
    data = StartTransaction(
        charger="test.localhost:%s" % transaction.conn.charger.cp_id,
        conn=transaction.conn.conn_id,
        tag=transaction.tag if transaction.tag is not None else generate_tag(),
        meter_start=transaction.meter_start,
    )
    event = Events(event=EventsEnum.START_TRANSACTION, data=data, domain="test.localhost")
    handler.start_transaction(event, "test.localhost")
    send_event_patch.assert_called()


def test_stop_transaction_event(handler: OcppHandler, transaction: TransactionModel, send_event_patch):
    data = StopTransaction(
        charger="test.localhost:%s" % transaction.conn.charger.cp_id,
        meter_stop=transaction.meter_stop,
        transaction_id=transaction.pk,
    )
    event = Events(event=EventsEnum.STOP_TRANSACTION, data=data, domain="test.localhost")
    handler.stop_transaction(event, "test.localhost")
    send_event_patch.assert_called()


def test_meter_value(handler: OcppHandler, meter_value, send_event_patch):
    data, _ = meter_value
    event = Events(event=EventsEnum.STOP_TRANSACTION, data=data, domain="test.localhost")
    handler.meter_value(event, "test.localhost")
    send_event_patch.assert_called()


def test_health(handler: OcppHandler, instance: ConnectorModel, send_event_patch):
    data = Health(charger="test.localhost:%s" % instance.charger.cp_id)
    event = Events(event=EventsEnum.HEALTH, data=data, domain="test.localhost")
    handler.health(event, "test.localhost")
    send_event_patch.assert_called()


@patch("core.apps.api.services.ocpp.send_command")
def test_remote_start_transaction(mock_send_command, transaction: TransactionModel):
    mock_send_command.return_value = {"status": "Accepted"}
    resp, msg = remote_start_transaction(transaction.conn.charger.pk, transaction.conn.pk, transaction.tag)
    assert resp is True
    mock_send_command.assert_called()


@patch("core.apps.api.services.ocpp.send_command")
def test_remote_stop_transaction(mock_send_command, transaction: TransactionModel):
    mock_send_command.return_value = {"status": "Accepted"}
    resp, msg = remote_stop_transaction(transaction.conn.charger.pk, transaction.pk)
    assert resp is True
    mock_send_command.assert_called()


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
        charger="test.localhost:%s" % transaction.conn.charger.cp_id,
        meter_stop=transaction.meter_stop,
        transaction_id=transaction.pk,
    )
    stop_transaction(transaction, TransactionStatusEnum.PENDING, "test.localhost", data)


def test_disconnect_charger(handler: OcppHandler, transaction: TransactionModel, send_event_patch):
    data = DisconnectCharger(charger="test.localhost:%s" % transaction.conn.charger.cp_id)
    event = Events(event=EventsEnum.DISCONNECT_CHARGER, data=data, domain="test.localhost")
    handler.disconnect_charger(event, "test.localhost")
    send_event_patch.assert_called()


def test_connect_charger(handler: OcppHandler, transaction: TransactionModel, send_event_patch):
    data = ConnectCharger(charger="test.localhost:%s" % transaction.conn.charger.cp_id)
    event = Events(event=EventsEnum.CONNECT_CHARGER, data=data, domain="test.localhost")
    handler.connect_charger(event)
    send_event_patch.assert_called()
