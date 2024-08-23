"""Code generated by Speakeasy (https://speakeasy.com). DO NOT EDIT."""

from __future__ import annotations
from .checkpointout import CheckpointOut, CheckpointOutTypedDict
from .eventout import EventOut, EventOutTypedDict
from .finetuneablemodel import FineTuneableModel
from .githubrepositoryout import GithubRepositoryOut, GithubRepositoryOutTypedDict
from .jobmetadataout import JobMetadataOut, JobMetadataOutTypedDict
from .trainingparameters import TrainingParameters, TrainingParametersTypedDict
from .wandbintegrationout import WandbIntegrationOut, WandbIntegrationOutTypedDict
from mistralai.types import BaseModel, Nullable, OptionalNullable, UNSET, UNSET_SENTINEL
import pydantic
from pydantic import model_serializer
from typing import Final, List, Literal, Optional, TypedDict
from typing_extensions import Annotated, NotRequired


DetailedJobOutStatus = Literal["QUEUED", "STARTED", "VALIDATING", "VALIDATED", "RUNNING", "FAILED_VALIDATION", "FAILED", "SUCCESS", "CANCELLED", "CANCELLATION_REQUESTED"]

DetailedJobOutObject = Literal["job"]

DetailedJobOutIntegrationsTypedDict = WandbIntegrationOutTypedDict


DetailedJobOutIntegrations = WandbIntegrationOut


DetailedJobOutRepositoriesTypedDict = GithubRepositoryOutTypedDict


DetailedJobOutRepositories = GithubRepositoryOut


class DetailedJobOutTypedDict(TypedDict):
    id: str
    auto_start: bool
    hyperparameters: TrainingParametersTypedDict
    model: FineTuneableModel
    r"""The name of the model to fine-tune."""
    status: DetailedJobOutStatus
    job_type: str
    created_at: int
    modified_at: int
    training_files: List[str]
    validation_files: NotRequired[Nullable[List[str]]]
    fine_tuned_model: NotRequired[Nullable[str]]
    suffix: NotRequired[Nullable[str]]
    integrations: NotRequired[Nullable[List[DetailedJobOutIntegrationsTypedDict]]]
    trained_tokens: NotRequired[Nullable[int]]
    repositories: NotRequired[List[DetailedJobOutRepositoriesTypedDict]]
    metadata: NotRequired[Nullable[JobMetadataOutTypedDict]]
    events: NotRequired[List[EventOutTypedDict]]
    r"""Event items are created every time the status of a fine-tuning job changes. The timestamped list of all events is accessible here."""
    checkpoints: NotRequired[List[CheckpointOutTypedDict]]
    

class DetailedJobOut(BaseModel):
    id: str
    auto_start: bool
    hyperparameters: TrainingParameters
    model: FineTuneableModel
    r"""The name of the model to fine-tune."""
    status: DetailedJobOutStatus
    job_type: str
    created_at: int
    modified_at: int
    training_files: List[str]
    validation_files: OptionalNullable[List[str]] = UNSET
    OBJECT: Annotated[Final[Optional[DetailedJobOutObject]], pydantic.Field(alias="object")] = "job" # type: ignore
    fine_tuned_model: OptionalNullable[str] = UNSET
    suffix: OptionalNullable[str] = UNSET
    integrations: OptionalNullable[List[DetailedJobOutIntegrations]] = UNSET
    trained_tokens: OptionalNullable[int] = UNSET
    repositories: Optional[List[DetailedJobOutRepositories]] = None
    metadata: OptionalNullable[JobMetadataOut] = UNSET
    events: Optional[List[EventOut]] = None
    r"""Event items are created every time the status of a fine-tuning job changes. The timestamped list of all events is accessible here."""
    checkpoints: Optional[List[CheckpointOut]] = None
    
    @model_serializer(mode="wrap")
    def serialize_model(self, handler):
        optional_fields = ["validation_files", "object", "fine_tuned_model", "suffix", "integrations", "trained_tokens", "repositories", "metadata", "events", "checkpoints"]
        nullable_fields = ["validation_files", "fine_tuned_model", "suffix", "integrations", "trained_tokens", "metadata"]
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
        
