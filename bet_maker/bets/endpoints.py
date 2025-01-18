from fastapi import APIRouter, status
from fastapi.params import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from bets.crud import bet_crud
from bets.schemas import BetCreate, BetDB
from bets.validators import check_cache
from core.db import get_async_session
from core.models import User
from core.utils import check_exists_and_get_or_return_error, log_and_raise_error
from users.authentication_utils import get_current_user

router = APIRouter(
    tags=["Bets"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "/bet",
    response_model=BetDB,
)
async def create_new_bet(
    bet_data: BetCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    await check_cache(bet_data.event_id)
    return await bet_crud.create(create_data=bet_data, user_id=user.id, session=session)


@router.get(
    "/bets",
    dependencies=[Depends(get_current_user)],
    response_model=list[BetDB],
)
async def get_all_bets(
    session: AsyncSession = Depends(get_async_session),
) -> list[BetDB]:
    try:
        return await bet_crud.get_multi(session=session)
    except Exception as e:
        log_and_raise_error(
            status_code=status.HTTP_404_NOT_FOUND,
            message_error=f"{e}",
            message_log=f"{e}",
        )


@router.get(
    "/get-one/{bet_id}",
    dependencies=[Depends(get_current_user)],
    response_model=BetDB,
)
async def get_bet_by_id(
    bet_id: int = Path(...),
    session: AsyncSession = Depends(get_async_session),
) -> BetDB:
    return await check_exists_and_get_or_return_error(
        db_id=bet_id,
        crud=bet_crud,
        method_name="get",
        error="Данной ставки нет в системе!",
        status_code=status.HTTP_404_NOT_FOUND,
        session=session,
    )


@router.get(
    "/my/bets",
    response_model=list[BetDB],
)
async def get_my_bets(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[BetDB]:
    try:
        return await bet_crud.get_multi_for_user(user_id=user.id, session=session)
    except Exception as e:
        log_and_raise_error(
            status_code=status.HTTP_404_NOT_FOUND,
            message_error=f"{e}",
            message_log=f"{e}",
        )


@router.delete(
    "/delete-bet/{bet_id}",
    dependencies=[Depends(get_current_user)],
)
async def delete_user_by_id(
    bet_id: int = Path(...),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    bet = await check_exists_and_get_or_return_error(
        db_id=bet_id,
        crud=bet_crud,
        method_name="get",
        error="Данной ставки нет в системе!",
        status_code=status.HTTP_404_NOT_FOUND,
        session=session,
    )
    try:
        await bet_crud.remove(db_obj=bet, session=session)
        return {"status": "Объект успешно удалён из БД"}
    except Exception as e:
        log_and_raise_error(
            status_code=status.HTTP_404_NOT_FOUND,
            message_error={"status": f"Ошибка при удалении: {e}"},
            message_log=f"{e}",
        )
