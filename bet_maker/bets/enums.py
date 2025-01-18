from strenum import StrEnum


class BetStatuses(StrEnum):
    """Доступные для пользователей административного пространства роли."""

    NOT_PLAYED = "Ставка ещё не сыграла."
    WON = "Ставка выиграла."
    LOST = "Ставка проиграла."
