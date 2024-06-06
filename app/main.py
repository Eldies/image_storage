# -*- coding: utf-8 -*-
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException
from starlette.concurrency import run_in_threadpool
from starlette.requests import Request
from starlette.responses import JSONResponse

from . import views
from .settings import settings
from .storage_manager import S3StorageManager, StorageManager

logger = logging.getLogger("image-storage")


async def put_images_to_s3() -> None:
    file_sm = StorageManager()
    s3_sm = S3StorageManager()
    all_uuids = await run_in_threadpool(s3_sm.list_uuids)
    for file1 in os.listdir(settings.upload_folder):
        await asyncio.sleep(0)
        path1 = os.path.join(settings.upload_folder, file1)
        for file2 in os.listdir(path1):
            await asyncio.sleep(0)
            uuid = [file1, file2]
            if uuid in all_uuids:
                logger.debug(f"Already exists {uuid}")
                continue
            image = file_sm.get_image(uuid)
            s3_sm.save_image(uuid, image.data)
            logger.debug(f"Moved {uuid}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
    # noinspection PyAsyncCall
    asyncio.create_task(put_images_to_s3())
    yield


app = FastAPI(lifespan=lifespan)


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
def ping() -> str:
    return "pong"


app.include_router(views.router_api)
