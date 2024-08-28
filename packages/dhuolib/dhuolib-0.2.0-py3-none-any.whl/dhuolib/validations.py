from pydantic import BaseModel, Field, field_validator
from dhuolib.messages import (
    VALUE_NULL_OR_EMPTY,
    MODEL_STAGE_TYPE,
    EXPERIMENT_FIELD_DESCRIPTION,
)


class BaseModelWithConfig(BaseModel):
    class Config:
        protected_namespaces = ()


class ModelBody(BaseModelWithConfig):
    modelname: str = Field(..., description="Model Name")
    tags: dict = Field(None, description="Tags")
    stage: str = Field(..., description=MODEL_STAGE_TYPE)
    run_id: str = Field(..., description="Run ID")
    model_uri: str = Field(..., description="Model URI")

    @field_validator("modelname", "stage", "run_id", "model_uri")
    def validate_empty_values(cls, value):
        if not value:
            raise ValueError(VALUE_NULL_OR_EMPTY)
        return value


class RunExperiment(BaseModelWithConfig):
    type_model: str = Field(
        ..., description="RANDOM_FOREST|XGBOOST|LINEAR_REGRESSION|LOGISTIC_REGRESSION"
    )
    experiment_name: str = Field(..., description=EXPERIMENT_FIELD_DESCRIPTION)
    tags: dict = Field(None, description="Tags")

    @field_validator("type_model", "experiment_name")
    def validate_empty_values(cls, value):
        if value == "":
            raise ValueError(VALUE_NULL_OR_EMPTY)
        return value


class RunFiles(BaseModelWithConfig):
    modelpkl_path: str = Field(..., description="Path to model.pkl")
    requirements_path: str = Field(..., description="Path to requirements.txt")

    @field_validator("modelpkl_path", "requirements_path")
    def validate_empty_values(cls, value):
        if value == "":
            raise ValueError(VALUE_NULL_OR_EMPTY)
        return value


class ExperimentBody(BaseModelWithConfig):
    experiment_name: str = Field(..., description="Id")
    experiment_tags: dict = Field(None, description="Tags")


class PredictOnlineModelBody(BaseModelWithConfig):
    run_id: str = Field(None, description="Run ID")
    modelname: str = Field(..., description="DEPENDENCY|PREDICT")
    stage: str = Field(..., description=MODEL_STAGE_TYPE)

    @field_validator("modelname", "stage")
    def validate_empty_values(cls, value):
        if value == "":
            raise ValueError(VALUE_NULL_OR_EMPTY)
        return value


class PredictBatchModelBody(BaseModelWithConfig):
    run_id: str = Field(None, description="Run ID")
    modelname: str = Field(..., description="DEPENDENCY|PREDICT")
    stage: str = Field(None, description=MODEL_STAGE_TYPE)
    batch_model_dir: str = Field(..., description="Batch File")
    experiment_name: str = Field(..., description=EXPERIMENT_FIELD_DESCRIPTION)
    type_model: str = Field(
        ..., description="RANDOM_FOREST|XGBOOST|LINEAR_REGRESSION|LOGISTIC_REGRESSION"
    )

    @field_validator("modelname", "batch_model_dir", "experiment_name", "type_model")
    def validate_empty_values(cls, value):
        if value == "":
            raise ValueError(VALUE_NULL_OR_EMPTY)
        return value


class ConnectModel(BaseModelWithConfig):
    dialect_drive: str = Field(..., description="Dialect")
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    host: str = Field(..., description="Host")
    port: str = Field(..., description="Port")
    service_name: str = Field(..., description="Service Name")

    @field_validator(
        "dialect_drive", "username", "password", "host", "port", "service_name"
    )
    def validate_empty_values(cls, value):
        if value == "":
            raise ValueError(VALUE_NULL_OR_EMPTY)
        return value


class TransitionModel(BaseModelWithConfig):
    model_name: str = Field(..., description="Model Name")
    version: str = Field(..., description="Version")
    stage: str = Field(..., description=MODEL_STAGE_TYPE)

    @field_validator("model_name", "stage")
    def validate_empty_values(cls, value):
        if value == "":
            raise ValueError(VALUE_NULL_OR_EMPTY)
        return value


class RunSearch(BaseModelWithConfig):
    filter_string: str = Field(None, description="Filter String")
    max_results: int = Field(None, description="Max Results")
    page_token: str = Field(None, description="Page Token")
    experiment_name: str = Field(..., description=EXPERIMENT_FIELD_DESCRIPTION)

    @field_validator("filter_string", "experiment_name")
    def validate_empty_values(cls, value):
        if value == "":
            raise ValueError(VALUE_NULL_OR_EMPTY)
        return value
