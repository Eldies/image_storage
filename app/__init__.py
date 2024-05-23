# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from logging.config import dictConfig

from starlette.requests import Request
from starlette.responses import JSONResponse

from . import views
from .logging_config import LogConfig


dictConfig(LogConfig().dict())

app = FastAPI()


@app.exception_handler(400)
@app.exception_handler(401)
@app.exception_handler(404)
async def exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=dict(
            status="error",
            error=exc.detail,
        ),
    )


@app.get("/ping", response_model=str)
def ping():
    return "pong"


app.include_router(views.router_api)
