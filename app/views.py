# -*- coding: utf-8 -*-
import base64
import functools
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader
from starlette import status
from starlette.responses import Response

from .image import Image
from .logic import generate_uuid
from .schemas import ErrorResponse, PostImageRequest, PostImageResponse
from .settings import ClientInfo, settings
from .storage_manager import get_storage_manager, save_image_retrying

router_api = APIRouter(prefix="/v1")
logger = logging.getLogger("image-storage")


def validate_client(api_key: str = Depends(APIKeyHeader(name="X-API-KEY"))) -> ClientInfo:
    client = settings.clients.by_api_key.get(api_key)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return client


@router_api.post(
    "/image/",
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
)
def post_image(
    client: Annotated[ClientInfo, Depends(validate_client)],
    params: PostImageRequest,
) -> PostImageResponse:
    uuid_generator = functools.partial(generate_uuid, suggested_filename=params.file_name, client=client)
    uuid = save_image_retrying(uuid_generator, image=Image(data=base64.b64decode(params.base64)))
    return PostImageResponse(uuid="/".join(uuid))


@router_api.get(
    "/image/{client_id}/{uuid}",
    response_class=Response,
    responses={404: {"model": ErrorResponse}},
)
def get_image(client_id: str, uuid: str) -> Response:
    image = get_storage_manager().get_image([client_id, uuid])
    return Response(content=image.data, media_type=image.mimetype)
