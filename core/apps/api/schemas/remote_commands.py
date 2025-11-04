from enum import Enum

from pydantic import BaseModel


class RemoteCommands(Enum):
    REMOTE_START_TRANSACTION = "remote_start_transaction"
    REMOTE_STOP_TRANSACTION = "remote_stop_transaction"


class RemoteCommandStatus(Enum):
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class RemoteStartTransaction(BaseModel):
    tag: str
    connector_id: str


class RemoteStopTransaction(BaseModel):
    transaction_id: int
