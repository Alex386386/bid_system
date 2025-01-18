from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from bets.enums import BetStatuses


class BetBase(BaseModel):
    bet_amount: float = Field(..., gt=0, description="Ставка должна быть больше нуля.")
    event_id: int = Field(
        ..., gt=0, description="ID события не может быть меньше или равным нулю."
    )


class BetCreate(BetBase):
    pass


class BetUpdate(BetBase):
    bet_amount: Optional[float] = Field(
        None, gt=0, description="Ставка должна быть больше нуля."
    )
    event_id: Optional[int] = Field(
        None, gt=0, description="ID события не может быть меньше или равным нулю."
    )


class BetDB(BetBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bet_amount: float
    event_id: int
    user_id: int
    status: BetStatuses
    create_date: int
    update_date: int
