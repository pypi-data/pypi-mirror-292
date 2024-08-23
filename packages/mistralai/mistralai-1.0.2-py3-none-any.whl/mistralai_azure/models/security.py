"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from mistralai_azure.types import BaseModel
from mistralai_azure.utils import FieldMetadata, SecurityMetadata
from typing import TypedDict
from typing_extensions import Annotated


class SecurityTypedDict(TypedDict):
    api_key: str
    

class Security(BaseModel):
    api_key: Annotated[str, FieldMetadata(security=SecurityMetadata(scheme=True, scheme_type="http", sub_type="bearer", field_name="Authorization"))]
    
