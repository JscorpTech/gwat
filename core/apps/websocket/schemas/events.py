from enum import Enum
from typing import Any, Optional, Union
from pydantic import BaseModel, ConfigDict

from core.apps.api.enums.connectors import ConnectorStatusEnum
from core.apps.api.enums.transaction import TransactionStatusEnum


class WsEventsEnum(Enum):
    CHARGER_STATUS = "charger_status"
    CONNECTOR_STATUS = "connector_status"
    TRANSACTION_METRICS = "transaction_metrics"
    HEALTH = "health"


class WsEvents(BaseModel):
    event: WsEventsEnum
    data: Any

    model_config = ConfigDict(use_enum_values=True)


class TransactionMetrics(BaseModel):
    id: int
    conn: int
    charger: int
    price: str
    meter_consumed: int
    power: int
    limit: Optional[Union[int, str]]
    status: TransactionStatusEnum

    model_config = ConfigDict(use_enum_values=True)


class ConnectorStatus(BaseModel):
    conn: int
    charger: int
    status: ConnectorStatusEnum

    model_config = ConfigDict(use_enum_values=True)


class Health(BaseModel):
    charger: int
    last_health: str
