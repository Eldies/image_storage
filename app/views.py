# -*- coding: utf-8 -*-
import base64
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from starlette import status
from starlette.responses import Response

from .image import Image
from .logic import generate_image_uuid, get_client_info_by_api_key
from .settings import ClientInfo
from .storage_manager import StorageManagerException, get_storage_manager

router_api = APIRouter(prefix="/v1")
logger = logging.getLogger("image-storage")


class PostImageRequest(BaseModel):
    file_name: str | None = None
    base64: bytes | None = None


def validate_client(api_key: str = Depends(APIKeyHeader(name="X-API-KEY"))) -> ClientInfo:
    logger.debug('Provided api_key: "{}"'.format(api_key))
    client = get_client_info_by_api_key(api_key)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return client


@router_api.post("/image/")
def post_image(
    client: Annotated[ClientInfo, Depends(validate_client)],
    params: PostImageRequest,
) -> dict[str, str]:
    if not params.base64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file",
        )

    filename = generate_image_uuid(params.file_name)
    logger.debug('Saving image with uuid "{}" for client "{}"'.format(filename, client.id))

    get_storage_manager().save_image(
        uuid=[client.id, filename],
        image=Image(data=base64.b64decode(params.base64)),
    )

    return dict(
        status="ok",
        uuid="{}/{}".format(client.id, filename),
    )


@router_api.get("/image/{client_id}/{uuid}")
def get_image(client_id: str, uuid: str) -> Response:
    try:
        image = get_storage_manager().get_image([client_id, uuid])
        return Response(content=image.data, media_type=image.mimetype)
    except StorageManagerException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(*e.args),
        )
