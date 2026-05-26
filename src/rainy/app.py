from fastapi import FastAPI

from rainy.api.endpoints.urls import router
from rainy.conf import settings

app = FastAPI(title=settings.APP)
app.include_router(router)
