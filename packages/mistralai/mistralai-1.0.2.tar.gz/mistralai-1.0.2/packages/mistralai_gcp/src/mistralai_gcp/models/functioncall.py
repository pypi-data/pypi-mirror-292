"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from mistralai_gcp.types import BaseModel
from typing import Any, Dict, TypedDict, Union


ArgumentsTypedDict = Union[Dict[str, Any], str]


Arguments = Union[Dict[str, Any], str]


class FunctionCallTypedDict(TypedDict):
    name: str
    arguments: ArgumentsTypedDict
    

class FunctionCall(BaseModel):
    name: str
    arguments: Arguments
    
