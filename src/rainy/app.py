from fastapi import FastAPI

from rainy.api.endpoints.urls import router
from rainy.conf import settings
from tomorrow.utils.functional import import_string

app = FastAPI(title=settings.APP)
app.include_router(router)

for middleware_path in settings.MIDDLEWARE:
    middleware = import_string(middleware_path)
    app.middleware("http")(middleware)
