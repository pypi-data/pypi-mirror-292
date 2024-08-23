"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from mistralai.types import BaseModel
from typing import Optional, TypedDict
from typing_extensions import NotRequired


class ModelCapabilitiesTypedDict(TypedDict):
    completion_chat: NotRequired[bool]
    completion_fim: NotRequired[bool]
    function_calling: NotRequired[bool]
    fine_tuning: NotRequired[bool]
    

class ModelCapabilities(BaseModel):
    completion_chat: Optional[bool] = True
    completion_fim: Optional[bool] = False
    function_calling: Optional[bool] = True
    fine_tuning: Optional[bool] = False
    
