"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from mistralai.types import BaseModel, Nullable, OptionalNullable, UNSET, UNSET_SENTINEL
from pydantic import model_serializer
from typing import TypedDict
from typing_extensions import NotRequired


class MetricOutTypedDict(TypedDict):
    r"""Metrics at the step number during the fine-tuning job. Use these metrics to assess if the training is going smoothly (loss should decrease, token accuracy should increase)."""
    
    train_loss: NotRequired[Nullable[float]]
    valid_loss: NotRequired[Nullable[float]]
    valid_mean_token_accuracy: NotRequired[Nullable[float]]
    

class MetricOut(BaseModel):
    r"""Metrics at the step number during the fine-tuning job. Use these metrics to assess if the training is going smoothly (loss should decrease, token accuracy should increase)."""
    
    train_loss: OptionalNullable[float] = UNSET
    valid_loss: OptionalNullable[float] = UNSET
    valid_mean_token_accuracy: OptionalNullable[float] = UNSET
    
    @model_serializer(mode="wrap")
    def serialize_model(self, handler):
        optional_fields = ["train_loss", "valid_loss", "valid_mean_token_accuracy"]
        nullable_fields = ["train_loss", "valid_loss", "valid_mean_token_accuracy"]
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
        
