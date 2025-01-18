import asyncio
import json
from typing import Optional

from aio_pika import connect, IncomingMessage, Connection
from sqlalchemy import update

from bets.enums import BetStatuses
from core.config import settings
from core.db import AsyncSessionLocal
from core.logger import logger
from core.models import Bet


class RabbitMQConsumer:
    def __init__(self):
        self.rabbit_host = settings.rabbit_host
        self.rabbit_port = settings.rabbit_port
        self.connection: Optional[Connection] = None
        self.consume_task: Optional[asyncio.Task] = None

    async def connect(self):
        if not self.connection:
            self.connection = await connect(
                host=self.rabbit_host, port=self.rabbit_port
            )
            logger.info("Подключение к RabbitMQ установлено")

    async def process_message(self, message: IncomingMessage) -> None:
        """Обрабатываем полученное сообщение"""
        async with message.process(ignore_processed=True):
            try:
                message_body = message.body.decode()
                event_data = json.loads(message_body)
                event_id = event_data["event_id"]
                new_status = event_data["state"]

                await self._update_bets_status(event_id, new_status)

                await message.ack()
                logger.debug("Сообщение обработано.")

            except Exception as e:
                logger.error(f"Ошибка при обработке сообщения: {e}")
                await message.reject(requeue=True)

    @staticmethod
    async def _update_bets_status(event_id: int, new_status: int) -> None:
        """Обновляем статус ставок для события"""
        async with AsyncSessionLocal() as session:
            if new_status == 2:
                status_to_set = BetStatuses.WON.value
            elif new_status == 3:
                status_to_set = BetStatuses.LOST.value
            else:
                raise ValueError("В сообщении передан некорректный статус!")

            await session.execute(
                update(Bet).where(Bet.event_id == event_id).values(status=status_to_set)
            )
            await session.commit()
            logger.debug(f"Статус ставок для мероприятия {event_id} обновлен.")

    async def consume(self):
        """Подключаемся к RabbitMQ и начинаем потреблять сообщения"""
        await self.connect()
        channel = await self.connection.channel()
        queue = await channel.declare_queue(settings.rabbit_queue, durable=True)
        await queue.consume(self.process_message, no_ack=False)
        logger.info("Начат прием сообщений из очереди RabbitMQ")

    async def start_consume(self):
        """Запускаем фоновую задачу для потребления сообщений"""
        self.consume_task = asyncio.create_task(self.consume())

    async def close(self):
        """Закрываем соединение с RabbitMQ"""
        if self.consume_task:
            self.consume_task.cancel()
            try:
                await self.consume_task
            except asyncio.CancelledError:
                pass
        if self.connection:
            await self.connection.close()
            logger.info("Соединение с RabbitMQ закрыто")
