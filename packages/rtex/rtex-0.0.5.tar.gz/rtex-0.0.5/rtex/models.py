from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field, RootModel, conint

RenderFormat = Literal["png", "jpg", "pdf"]
RenderQuality = Annotated[int, conint(gt=0, le=100)]
RenderDensity = int


class CreateLaTeXDocumentRequest(BaseModel):
    code: str
    format: RenderFormat
    quality: Optional[RenderQuality]
    density: Optional[RenderDensity] = None


class CreateLaTeXDocumentSuccessResponse(BaseModel):
    status: Literal["success"]
    log: str
    filename: str


class CreateLaTeXDocumentErrorResponse(BaseModel):
    status: Literal["error"]
    log: str
    description: str


class CreateLaTeXDocumentResponse(RootModel):
    root: Union[
        CreateLaTeXDocumentSuccessResponse,
        CreateLaTeXDocumentErrorResponse,
    ] = Field(discriminator="status")
