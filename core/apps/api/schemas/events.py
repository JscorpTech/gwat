from typing import Any, List
from pydantic import BaseModel, ConfigDict
from core.apps.api.enums import ConnectorStatusEnum
from enum import Enum


class EventsEnum(Enum):
    CHANGE_CONNECTOR_STATUS = "change_connector_status"
    START_TRANSACTION = "start_transaction"
    STOP_TRANSACTION = "stop_transaction"
    METER_VALUE = "meter_value"
    HEALTH = "health"
    DATA_TRANSFER = "data_transfer"


class Events(BaseModel):
    event: EventsEnum
    data: Any

    model_config = ConfigDict(use_enum_values=True)


class ChangeConnectorStatus(BaseModel):
    charger: int
    conn: int
    status: ConnectorStatusEnum

    model_config = ConfigDict(use_enum_values=True)


class StartTransaction(BaseModel):
    charger: int
    conn: int
    tag: str
    meter_start: int

    model_config = ConfigDict(use_enum_values=True)


class StopTransaction(BaseModel):
    charger: int
    transaction_id: int
    reason: str = ""
    meter_stop: int

    model_config = ConfigDict(use_enum_values=True)


class SampledValue(BaseModel):
    context: str
    format: str
    location: str
    measurand: str
    phase: str
    unit: str
    value: str


class MeterValueData(BaseModel):
    timestamp: str
    sampledValue: List[SampledValue]


class MeterValue(BaseModel):
    conn: int
    transaction_id: int
    meter_value: List[MeterValueData]


class Health(BaseModel):
    charger: str


class DataTransferValue(BaseModel):
    vendorId: str
    messageId: str
    data: str


class DataTransfer(BaseModel):
    charger: str
    data: DataTransferValue
