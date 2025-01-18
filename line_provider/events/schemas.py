import time
from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict

from events.enums import EventState


class Event(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    coefficient: float = Field(
        None, gt=0, lt=30, description="Коэффициент должен быть больше 0, но меньше 30."
    )
    deadline: int = Field(
        default_factory=lambda: int(time.time()) + 5000,
        gt=1737074285,
        description="Дата не должна быть меньше текущей.",
    )

    @field_validator("deadline", mode="before")
    def validate_deadline(cls, v: int) -> Optional[int]:
        current_timestamp = int(time.time())
        if v is not None and v < current_timestamp:
            raise ValueError(
                f"Дедлайн события должен быть позже текущего времени. Текущее время: {current_timestamp}"
            )
        return v


class EventRequest(BaseModel):
    event_id: int
    coefficient: float
    deadline: int
    state: EventState
    create_date: int
    update_date: int
