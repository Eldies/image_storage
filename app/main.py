# -*- coding: utf-8 -*-
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.requests import Request
from starlette.responses import JSONResponse

from . import views
from .schemas import ErrorResponse
from .settings import settings

logger = logging.getLogger("image-storage")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    instrumentator.expose(app, tags=["metrics"])
    yield


sentry_sdk.init(
    dsn=settings.sentry.dsn,
    release=settings.version,
    environment=settings.environment,
)

app = FastAPI(lifespan=lifespan)
instrumentator = Instrumentator().instrument(app)


@app.exception_handler(400)
@app.exception_handler(401)
@app.exception_handler(403)
@app.exception_handler(404)
async def exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.detail).dict(),
    )


@app.get("/ping", response_model=str)
def ping() -> str:
    return "pong"


app.include_router(views.router_api)
