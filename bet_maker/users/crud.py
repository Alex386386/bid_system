from fastapi import status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.crud_foundation import CRUDBase
from core.models import User
from core.utils import log_and_raise_error
from users.authentication_utils import get_password_hash
from users.schemas import UserCreate, UserUpdate


class UserCRUD(CRUDBase):

    async def handle_integrity_error(self, e: IntegrityError) -> None:
        """Обрабатывает ошибки IntegrityError при работе с базой данных."""
        error_message = str(e.orig)
        if "users_username_key" in error_message:
            log_and_raise_error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message_error="Данный username уже занят.",
                message_log="Данный username уже занят.",
            )
        elif "users_email_key" in error_message:
            log_and_raise_error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message_error="Данный email уже зарегистрирован.",
                message_log="Данный email уже зарегистрирован.",
            )
        else:
            log_and_raise_error(
                status_code=status.HTTP_400_BAD_REQUEST,
                message_error=f"{error_message}",
                message_log=f"{error_message}",
            )

    async def create(self, create_data: UserCreate, session: AsyncSession):
        create_data = create_data.model_dump()
        hashed_password = get_password_hash(create_data["password"])
        create_data["password"] = hashed_password
        admin_user = self.model(**create_data)
        session.add(admin_user)
        try:
            await session.commit()
            await session.refresh(admin_user)
            return admin_user
        except IntegrityError as e:
            await session.rollback()
            await self.handle_integrity_error(e)

    async def update(
        self,
        db_obj: User,
        obj_in: UserUpdate,
        session: AsyncSession,
    ):
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.model_dump(exclude_unset=True)
        if update_data.get("password", None) is not None:
            hashed_password = get_password_hash(update_data["password"])
            update_data["password"] = hashed_password

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        try:
            await session.commit()
            await session.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await session.rollback()
            await self.handle_integrity_error(e)


user_crud = UserCRUD(User)
