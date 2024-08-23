"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from .ftmodelcapabilitiesout import FTModelCapabilitiesOut, FTModelCapabilitiesOutTypedDict
from mistralai.types import BaseModel, Nullable, OptionalNullable, UNSET, UNSET_SENTINEL
import pydantic
from pydantic import model_serializer
from typing import Final, List, Literal, Optional, TypedDict
from typing_extensions import Annotated, NotRequired


FTModelOutObject = Literal["model"]

class FTModelOutTypedDict(TypedDict):
    id: str
    created: int
    owned_by: str
    root: str
    archived: bool
    capabilities: FTModelCapabilitiesOutTypedDict
    job: str
    name: NotRequired[Nullable[str]]
    description: NotRequired[Nullable[str]]
    max_context_length: NotRequired[int]
    aliases: NotRequired[List[str]]
    

class FTModelOut(BaseModel):
    id: str
    created: int
    owned_by: str
    root: str
    archived: bool
    capabilities: FTModelCapabilitiesOut
    job: str
    OBJECT: Annotated[Final[Optional[FTModelOutObject]], pydantic.Field(alias="object")] = "model" # type: ignore
    name: OptionalNullable[str] = UNSET
    description: OptionalNullable[str] = UNSET
    max_context_length: Optional[int] = 32768
    aliases: Optional[List[str]] = None
    
    @model_serializer(mode="wrap")
    def serialize_model(self, handler):
        optional_fields = ["object", "name", "description", "max_context_length", "aliases"]
        nullable_fields = ["name", "description"]
        null_default_fields = []

        serialized = handler(self)

        m = {}

        for n, f in self.model_fields.items():
            k = f.alias or n
            val = serialized.get(k)

            optional_nullable = k in optional_fields and k in nullable_fields
            is_set = (self.__pydantic_fields_set__.intersection({n}) or k in null_default_fields) # pylint: disable=no-member

            if val is not None and val != UNSET_SENTINEL:
                m[k] = val
            elif val != UNSET_SENTINEL and (
                not k in optional_fields or (optional_nullable and is_set)
            ):
                m[k] = val

        return m
        
