"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from mistralai.types import BaseModel, Nullable, OptionalNullable, UNSET, UNSET_SENTINEL
import pydantic
from pydantic import model_serializer
from typing import Final, Literal, Optional, TypedDict
from typing_extensions import Annotated, NotRequired


GithubRepositoryInType = Literal["github"]

class GithubRepositoryInTypedDict(TypedDict):
    name: str
    owner: str
    token: str
    ref: NotRequired[Nullable[str]]
    weight: NotRequired[float]
    

class GithubRepositoryIn(BaseModel):
    name: str
    owner: str
    token: str
    TYPE: Annotated[Final[Optional[GithubRepositoryInType]], pydantic.Field(alias="type")] = "github" # type: ignore
    ref: OptionalNullable[str] = UNSET
    weight: Optional[float] = 1
    
    @model_serializer(mode="wrap")
    def serialize_model(self, handler):
        optional_fields = ["type", "ref", "weight"]
        nullable_fields = ["ref"]
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
        
