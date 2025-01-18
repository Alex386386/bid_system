import json
from typing import Optional

from aio_pika import connect_robust, Message, Channel, Connection

from core.config import settings
from core.logger import logger


class RabbitMQProducer:
    def __init__(self):
        self.connection: Optional[Connection] = None
        self.channel: Optional[Channel] = None

    async def connect(self):
        """Установить соединение с RabbitMQ и открыть канал."""
        try:
            self.connection = await connect_robust(
                host=settings.rabbit_host, port=settings.rabbit_port
            )
            self.channel = await self.connection.channel()
            await self.channel.declare_queue(settings.rabbit_queue, durable=True)
            logger.info(
                "Подключение к RabbitMQ и инициализация очереди прошли успешно."
            )
        except Exception as e:
            logger.error(f"Ошибка при попытке подключения к RabbitMQ: {e}")
            raise

    async def publish_message(self, message: dict):
        """Публикация сообщения в очередь."""
        if not self.channel:
            raise RuntimeError("Канал подключения к RabbitMQ не инициализирован.")

        try:
            message_body = json.dumps(message).encode("utf-8")
            await self.channel.default_exchange.publish(
                Message(body=message_body),
                routing_key=settings.rabbit_queue,
            )
            logger.debug(f"Публикация сообщения в RabbitMQ: {message}")
        except Exception as e:
            logger.error(f"Ошибка при публикации сообщения в RabbitMQ: {e}")
            raise

    async def close(self):
        """Закрытие соединения с RabbitMQ."""
        if self.connection:
            await self.connection.close()
            logger.info("Закрытие соединения с RabbitMQ.")
