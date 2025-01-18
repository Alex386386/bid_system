import enum


class EventState(int, enum.Enum):
    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3
