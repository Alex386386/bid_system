from fastapi import APIRouter, Depends, status
from httpx import AsyncClient, RequestError

from core.cache import cache
from core.config import settings
from core.logger import logger
from core.utils import log_and_raise_error
from users.authentication_utils import get_current_user

router = APIRouter(
    tags=["Events"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/events")
async def get_events() -> list[dict]:
    async with AsyncClient() as client:
        try:
            response = await client.get(
                settings.event_url,
                headers={"Authorization": f"Bearer {settings.line_provider_token}"},
            )
            response.raise_for_status()
            events = response.json()

            cache["event_ids"] = {event["event_id"]: event for event in events}
            logger.debug("Кэш записан")

            return events
        except RequestError as e:
            log_and_raise_error(
                status_code=status.HTTP_502_BAD_GATEWAY,
                message_error=f"Сервис недоступен: {str(e)}",
                message_log=f"Сервис недоступен: {str(e)}",
            )
        except Exception as e:
            log_and_raise_error(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message_error=f"Непредвиденное исключение: {str(e)}",
                message_log=f"Непредвиденное исключение: {str(e)}",
            )
