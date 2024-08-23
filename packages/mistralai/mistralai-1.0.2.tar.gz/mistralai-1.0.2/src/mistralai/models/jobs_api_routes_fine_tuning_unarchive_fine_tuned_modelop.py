"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from mistralai.types import BaseModel
from mistralai.utils import FieldMetadata, PathParamMetadata
from typing import TypedDict
from typing_extensions import Annotated


class JobsAPIRoutesFineTuningUnarchiveFineTunedModelRequestTypedDict(TypedDict):
    model_id: str
    r"""The ID of the model to unarchive."""
    

class JobsAPIRoutesFineTuningUnarchiveFineTunedModelRequest(BaseModel):
    model_id: Annotated[str, FieldMetadata(path=PathParamMetadata(style="simple", explode=False))]
    r"""The ID of the model to unarchive."""
    
