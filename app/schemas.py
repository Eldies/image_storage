from pydantic import BaseModel


class PostImageRequest(BaseModel):
    file_name: str | None = None
    base64: bytes


class PostImageResponse(BaseModel):
    status: str = "ok"
    uuid: str


class ErrorResponse(BaseModel):
    status: str = "error"
    error: str
