from fastapi import APIRouter, status
from fastapi.params import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_async_session
from core.utils import check_exists_and_get_or_return_error, log_and_raise_error
from users.authentication_utils import get_current_user
from users.crud import user_crud
from users.schemas import UserCreate, UserUpdate, UserDB

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_current_user)],
)


@router.get(
    "/get-one/{user_id}",
    response_model=UserDB,
)
async def get_user_by_id(
    user_id: int = Path(...),
    session: AsyncSession = Depends(get_async_session),
) -> UserDB:
    return await check_exists_and_get_or_return_error(
        db_id=user_id,
        crud=user_crud,
        method_name="get",
        error="Пользователь не найден!",
        status_code=status.HTTP_404_NOT_FOUND,
        session=session,
    )


@router.get(
    "/get-all",
    response_model=list[UserDB],
)
async def get_all_users(
    session: AsyncSession = Depends(get_async_session),
) -> list[UserDB]:
    try:
        return await user_crud.get_multi(session=session)
    except Exception as e:
        log_and_raise_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message_error=f"{e}",
            message_log=f"{e}",
        )


@router.post(
    "/create",
    response_model=UserDB,
)
async def create_new_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_async_session),
) -> UserDB:
    return await user_crud.create(create_data=user_data, session=session)


@router.patch(
    "/update/{user_id}",
    response_model=UserDB,
)
async def update_user(
    user_data: UserUpdate,
    user_id: int = Path(...),
    session: AsyncSession = Depends(get_async_session),
) -> UserDB:
    user = await check_exists_and_get_or_return_error(
        db_id=user_id,
        crud=user_crud,
        method_name="get",
        error="Пользователь не найден!",
        status_code=status.HTTP_404_NOT_FOUND,
        session=session,
    )
    return await user_crud.update(db_obj=user, obj_in=user_data, session=session)


@router.delete("/delete-user-by-id/{user_id}")
async def delete_user_by_id(
    user_id: int = Path(...),
    session: AsyncSession = Depends(get_async_session),
) -> dict:
    user = await check_exists_and_get_or_return_error(
        db_id=user_id,
        crud=user_crud,
        method_name="get",
        error="Пользователь не найден!",
        status_code=status.HTTP_404_NOT_FOUND,
        session=session,
    )
    try:
        await user_crud.remove(db_obj=user, session=session)
        return {"status": "Объект успешно удалён из БД"}
    except Exception as e:
        log_and_raise_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message_error={"status": f"Ошибка при удалении: {e}"},
            message_log=f"{e}",
        )
