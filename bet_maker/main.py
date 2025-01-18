from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings
from core.db import get_async_session
from core.logger import logger, request_log
from core.rabbitmq_consumer import RabbitMQConsumer
from routers import main_router
from users.authentication_utils import (
    authenticate_user,
    create_access_token,
)
from users.first_user import create_first_user

rabbitmq_consumer = RabbitMQConsumer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Создаётся первый суперпользователь или проверяется его наличие.")
    await create_first_user()
    logger.info("Происходит инициализация потребителя сообщений.")
    await rabbitmq_consumer.start_consume()
    yield
    logger.info("Закрытие соединения с RabbitMQ")
    await rabbitmq_consumer.close()


app = FastAPI(title="Bet Maker", lifespan=lifespan)

origins = ["*"]
app.add_middleware(BaseHTTPMiddleware, dispatch=request_log)

app.include_router(main_router)

logger.info("API is starting up")


@app.get("/")
async def root() -> JSONResponse:
    return JSONResponse(content={"detail": "This route is disabled"}, status_code=403)


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    user = await authenticate_user(
        username=form_data.username, password=form_data.password, session=session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.token_expired_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
