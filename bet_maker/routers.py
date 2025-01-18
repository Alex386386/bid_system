from fastapi import APIRouter

from users.endpoints import router as user_router
from bets.endpoints import router as bet_router
from events.endpoints import router as event_router

main_router = APIRouter(prefix="/api")
main_router.include_router(user_router)
main_router.include_router(bet_router)
main_router.include_router(event_router)
