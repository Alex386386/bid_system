from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Depends
from starlette.middleware.base import BaseHTTPMiddleware

from core.authentication_utils import check_bot_token
from core.logger import request_log, logger
from events.crud import RedisEventStorage
from events.enums import EventState
from core.rabbit_producer import RabbitMQProducer
from events.schemas import Event, EventRequest

rabbitmq_producer = RabbitMQProducer()


@asynccontextmanager
async def rabbitmq_lifespan(app: FastAPI):
    logger.info("Подключение к RabbitMQ...")
    await rabbitmq_producer.connect()
    yield
    logger.info("Закрытие соединения RabbitMQ...")
    await rabbitmq_producer.close()


app = FastAPI(lifespan=rabbitmq_lifespan)
app.add_middleware(BaseHTTPMiddleware, dispatch=request_log)

redis_storage = RedisEventStorage()


@app.post(
    "/event",
    response_model=EventRequest,
    dependencies=[Depends(check_bot_token)],
)
async def create_event(event: Event) -> dict:
    event = event.model_dump()
    new_event = await redis_storage.add_event(event)
    return new_event


@app.get(
    "/events",
    response_model=list[EventRequest],
    dependencies=[Depends(check_bot_token)],
)
async def get_all_events() -> list[dict]:
    return await redis_storage.get_all_events()


@app.get(
    "/event/{event_id}",
    response_model=EventRequest,
    dependencies=[Depends(check_bot_token)],
)
async def get_event(event_id: int) -> dict:
    event = await redis_storage.call_get_event(event_id)
    return event


@app.patch(
    "/event/{event_id}/status",
    response_model=EventRequest,
    dependencies=[Depends(check_bot_token)],
)
async def update_event_status(event_id: int, new_status: EventState) -> dict:
    event = await redis_storage.update_event(event_id, new_status)

    message = {"event_id": event_id, "state": new_status}
    await rabbitmq_producer.publish_message(message)
    return event


@app.delete(
    "/event/{event_id}",
    dependencies=[Depends(check_bot_token)],
)
async def delete_event(event_id: int) -> dict:
    event = await redis_storage.delete_event(event_id)
    if event:
        return {"status": "Событие успешно удалено из системы."}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Такого события нет в системе."
    )
