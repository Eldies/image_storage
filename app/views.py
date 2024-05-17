# -*- coding: utf-8 -*-
import base64
import json
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from .logic import (
    get_client_info_by_api_key,
    generate_image_uuid,
)
from .storage_manager import (
    get_storage_manager,
    StorageManagerException,
)


router_api = APIRouter(prefix="/v1")
logger = logging.getLogger("image-storage")


class PostImageRequest(BaseModel):
    file_name: str = None
    base64: bytes = None


@router_api.post("/image/")
def post_image(
    request: Request,
    params: PostImageRequest,
):
    api_key = request.headers.get('X-API-KEY')
    logger.debug('Provided api_key: "{}"'.format(api_key))
    client = None
    if api_key is not None:
        client = get_client_info_by_api_key(api_key)

    if client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    if not params.base64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No file',
        )

    filename = generate_image_uuid(params.file_name)
    logger.debug('Saving image with uuid "{}" for client "{}"'.format(filename, client.id))

    get_storage_manager().save_image(
        uuid=[client.id, filename],
        file_content=base64.b64decode(params.base64),
        data=json.dumps(dict(
            mimetype='image/jpeg',
        )),
    )

    return dict(
        status='ok',
        uuid='{}/{}'.format(client.id, filename),
    )


@router_api.get("/image/{client_id}/{uuid}")
def get_image(client_id: str, uuid: str):
    try:
        bytes, data = get_storage_manager().get_file([client_id, uuid])
        return Response(content=bytes, media_type=data.get('mimetype'))
    except StorageManagerException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(*e.args),
        )
