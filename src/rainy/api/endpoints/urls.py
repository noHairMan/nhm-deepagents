from fastapi import APIRouter

from .chat import router as chat_router
from .health import router as health_router

router = APIRouter(prefix="/api")

router.include_router(health_router)
router.include_router(chat_router)
