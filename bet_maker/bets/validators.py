import time

from httpx import AsyncClient, RequestError
from core.config import settings
from core.logger import logger
from fastapi import status
from core.cache import cache
from core.utils import log_and_raise_error


async def check_event_in_cache(event_id: int, events: dict) -> dict:
    """Проверяет наличие события в кэше и возвращает событие."""
    event = events.get(event_id)
    if not event:
        log_and_raise_error(
            status_code=status.HTTP_404_NOT_FOUND,
            message_error="Такого события нет в системе.",
            message_log=f"События с id {event_id} нет в кэше.",
        )
    return event


async def check_event_deadline(event: dict) -> None:
    """Проверяет, не истёк ли срок действия события."""
    now = int(time.time())
    if event["deadline"] <= now:
        log_and_raise_error(
            status_code=status.HTTP_403_FORBIDDEN,
            message_error="На данное мероприятие больше нельзя зарегистрировать ставку.",
            message_log=f"Событие с id {event['event_id']} больше не принимает ставки.",
        )


async def fetch_and_update_cache() -> dict:
    """Обновляет кэш с данными о событиях."""
    logger.debug("Кэш устарел, происходит запрос для обновления.")
    async with AsyncClient() as client:
        try:
            response = await client.get(
                settings.event_url,
                headers={"Authorization": f"Bearer {settings.line_provider_token}"},
            )
            response.raise_for_status()
            events = response.json()
            cache["event_ids"] = {event["event_id"]: event for event in events}
            return cache["event_ids"]
        except RequestError as e:
            log_and_raise_error(
                status_code=status.HTTP_502_BAD_GATEWAY,
                message_error=f"Сервис недоступен: {str(e)}",
                message_log=f"Ошибка подключения к сервису: {str(e)}",
            )
        except Exception as e:
            log_and_raise_error(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message_error=f"Непредвиденное исключение: {str(e)}",
                message_log=f"Неожиданная ошибка: {str(e)}",
            )


async def check_cache(event_id: int) -> None:
    """Проверяет наличие события в кэше, обновляет кэш при необходимости."""
    events = cache.get("event_ids")
    if events is None:
        events = await fetch_and_update_cache()
    event = await check_event_in_cache(event_id, events)
    await check_event_deadline(event)
