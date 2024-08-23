"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from .completionchunk import CompletionChunk, CompletionChunkTypedDict
from mistralai_gcp.types import BaseModel
from typing import TypedDict


class CompletionEventTypedDict(TypedDict):
    data: CompletionChunkTypedDict
    

class CompletionEvent(BaseModel):
    data: CompletionChunk
    
