"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from .function import Function, FunctionTypedDict
from mistralai_azure.types import BaseModel, UnrecognizedStr
from mistralai_azure.utils import validate_open_enum
from pydantic.functional_validators import PlainValidator
from typing import Literal, Optional, TypedDict, Union
from typing_extensions import Annotated, NotRequired


ToolToolTypes = Union[Literal["function"], UnrecognizedStr]

class ToolTypedDict(TypedDict):
    function: FunctionTypedDict
    type: NotRequired[ToolToolTypes]
    

class Tool(BaseModel):
    function: Function
    type: Annotated[Optional[ToolToolTypes], PlainValidator(validate_open_enum(False))] = "function"
    
