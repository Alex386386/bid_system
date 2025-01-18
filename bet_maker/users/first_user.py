from sqlalchemy import select

from core.config import settings
from core.db import AsyncSessionLocal
from core.logger import logger
from core.models import User
from users.authentication_utils import get_password_hash


async def create_first_user():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == settings.first_user_username)
        )
        existing_user = result.scalars().first()

        if existing_user:
            logger.debug("Пользователь уже существует, пропускаем создание.")
            return

        first_user = User(
            name=settings.first_user_name,
            username=settings.first_user_username,
            password=get_password_hash(settings.first_user_name),
            email=settings.first_user_email,
        )

        session.add(first_user)
        await session.commit()
        logger.debug("Первый пользователь создан.")
