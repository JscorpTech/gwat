from pydantic import BaseModel, ConfigDict


class TransactionUpdate(BaseModel):
    transaction: int
    conn: int
    charger: int

    model_config = ConfigDict(use_enum_values=True)
