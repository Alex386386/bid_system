import json
import time
from functools import wraps
from typing import Optional

import aioredis
from fastapi import HTTPException, status

from core.config import settings
from core.logger import logger
from events.enums import EventState


def with_redis_connection(method):
    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        redis = await aioredis.from_url(
            settings.redis_connect_url, decode_responses=True
        )
        try:
            logger.debug("Открылось подключение к редису.")
            return await method(self, redis, *args, **kwargs)
        except aioredis.exceptions.ConnectionError as e:
            logger.error(f"Не удалось подключиться к Redis: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось подключиться к хранилищу Redis.",
            )
        finally:
            await redis.close()
            logger.debug("Закрыли подключение.")

    return wrapper


class RedisEventStorage:
    def __init__(
        self,
        redis_hash_name: str = "events",
        max_id_key: str = "max_event_id",
    ):
        self.redis_hash_name = redis_hash_name
        self.max_id_key = max_id_key

    async def _get_next_event_id(self, redis) -> int:
        max_id = await redis.get(self.max_id_key)
        if not max_id:
            max_id = 1
            await redis.set(self.max_id_key, max_id)
            logger.debug("Установлен первичный id.")
            return max_id
        else:
            max_id = int(max_id)

        next_id = max_id + 1
        await redis.set(self.max_id_key, next_id)
        return next_id

    async def _get_event(self, redis, event_id: int) -> Optional[dict]:
        event_data = await redis.hget(self.redis_hash_name, event_id)
        if not event_data:
            logger.error(
                f"Ошибка при получении события с id {event_id}, нет в системе."
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Такого события нет в системе!",
            )
        return json.loads(event_data)

    @with_redis_connection
    async def call_get_event(self, redis, event_id) -> Optional[dict]:
        logger.debug(f"Попытка получения события с id {event_id}.")
        return await self._get_event(redis, event_id)

    @with_redis_connection
    async def get_all_events(self, redis):
        events_data = await redis.hgetall(self.redis_hash_name)
        events = [json.loads(event) for event in events_data.values()]
        logger.debug("Получен список событий.")
        return events

    @with_redis_connection
    async def add_event(self, redis, event: dict) -> dict:
        event_id = await self._get_next_event_id(redis)
        event["event_id"] = event_id
        event["create_date"] = int(time.time())
        event["update_date"] = int(time.time())
        event["state"] = EventState.NEW.value
        await redis.hset(self.redis_hash_name, event_id, json.dumps(event))
        logger.debug("Сохранёно новое событие.")
        return event

    @with_redis_connection
    async def update_event(self, redis, event_id: int, new_status: int) -> dict:
        event = await self._get_event(redis, event_id=event_id)
        if event["state"] != EventState.NEW.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нельзя изменить статус уже законченного мероприятия.",
            )
        event["state"] = new_status
        event["update_date"] = int(time.time())
        await redis.hset(self.redis_hash_name, event_id, json.dumps(event))
        logger.debug(f"У события с id {event_id} обновлён статус.")
        return event

    @with_redis_connection
    async def delete_event(self, redis, event_id: int):
        result = await redis.hdel(self.redis_hash_name, event_id)
        logger.debug(f"События с id {event_id} удалено из системы.")
        return result > 0
