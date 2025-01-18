from fastapi import status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from bets.schemas import BetCreate
from core.crud_foundation import CRUDBase
from core.models import Bet
from core.utils import log_and_raise_error


class BetCRUD(CRUDBase):

    async def handle_integrity_error(self, e: IntegrityError) -> None:
        """Обрабатывает ошибки IntegrityError при работе с базой данных."""
        error_message = str(e.orig)
        if "fk_user_id" in error_message:
            log_and_raise_error(
                status_code=status.HTTP_404_NOT_FOUND,
                message_error="Такого пользователя нет в системе.",
                message_log="Такого пользователя нет в системе.",
            )
        else:
            log_and_raise_error(
                status_code=status.HTTP_404_NOT_FOUND,
                message_error=f"{error_message}",
                message_log=f"{error_message}",
            )

    async def get_multi_for_user(self, user_id: int, session: AsyncSession):
        db_objs = await session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return db_objs.scalars().all()

    async def create(self, create_data: BetCreate, user_id: int, session: AsyncSession):
        create_data = create_data.model_dump()
        create_data["user_id"] = user_id
        new_obj = self.model(**create_data)
        try:
            session.add(new_obj)
            await session.commit()
            await session.refresh(new_obj)
            return new_obj
        except IntegrityError as e:
            await session.rollback()
            await self.handle_integrity_error(e)


bet_crud = BetCRUD(Bet)
