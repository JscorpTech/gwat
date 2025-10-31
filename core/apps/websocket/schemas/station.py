from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict


class WsEventsEnum(Enum):
    CHARGER_STATUS = "charger_status"


class WsEvents(BaseModel):
    event: WsEventsEnum
    data: Any

    model_config = ConfigDict(use_enum_values=True)
