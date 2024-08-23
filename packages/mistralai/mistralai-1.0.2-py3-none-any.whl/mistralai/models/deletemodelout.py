"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from mistralai.types import BaseModel
from typing import Optional, TypedDict
from typing_extensions import NotRequired


class DeleteModelOutTypedDict(TypedDict):
    id: str
    r"""The ID of the deleted model."""
    object: NotRequired[str]
    r"""The object type that was deleted"""
    deleted: NotRequired[bool]
    r"""The deletion status"""
    

class DeleteModelOut(BaseModel):
    id: str
    r"""The ID of the deleted model."""
    object: Optional[str] = "model"
    r"""The object type that was deleted"""
    deleted: Optional[bool] = True
    r"""The deletion status"""
    
