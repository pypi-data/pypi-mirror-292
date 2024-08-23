from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field

from picsellia.types.enums import (
    AnnotationStatus,
    DataType,
    DataUploadStatus,
    ExperimentStatus,
    Framework,
    InferenceType,
    JobRunStatus,
    JobStatus,
    LogType,
    ProcessingType,
    TagTarget,
)


class DaoSchema(BaseModel):
    # Might not be defined if refresh is done manually
    id: Optional[UUID] = None


class DatalakeSchema(DaoSchema):
    name: str
    connector_id: Optional[UUID] = None


class OrganizationSchema(DaoSchema):
    name: str
    default_connector_id: Optional[UUID] = None


class DatasetSchema(DaoSchema):
    name: str


class DatasetVersionSchema(DaoSchema):
    name: str = Field(alias="origin_name")
    origin_id: UUID = Field(alias="origin_id")
    version: str
    type: InferenceType


class AnnotationCampaignSchema(DaoSchema):
    name: str
    dataset_version_id: UUID


class DatasetVersionStats(BaseModel):
    label_repartition: Dict[str, int]
    nb_objects: int
    nb_annotations: int


class ModelSchema(DaoSchema):
    name: str
    type: InferenceType
    framework: Framework
    private: bool


class ModelVersionSchema(DaoSchema):
    origin: ModelSchema
    name: str
    version: int
    labels: Optional[dict] = None
    type: InferenceType
    framework: Framework


class ModelDataSchema(DaoSchema):
    name: str
    version_id: UUID
    repartition: dict


class ModelContextSchema(DaoSchema):
    experiment_id: Optional[UUID] = None
    datas: List[ModelDataSchema]
    parameters: dict


class ModelFileSchema(DaoSchema):
    name: str
    object_name: str
    filename: str
    large: bool
    url: Optional[str] = Field(alias="presigned_url", default=None)


class ProjectSchema(DaoSchema):
    name: str


class DeploymentSchema(DaoSchema):
    name: str
    type: InferenceType
    oracle_host: Optional[str] = None
    serving_host: Optional[str] = None


class ImageMetaSchema(BaseModel):
    width: int
    height: int


class VideoMetaSchema(BaseModel):
    width: int
    height: int


class DataSchema(DaoSchema):
    object_name: str
    filename: str
    type: DataType
    upload_status: DataUploadStatus
    url: Optional[str] = Field(alias="presigned_url", default=None)
    metadata: Optional[dict] = None


class ImageSchema(DataSchema):
    meta: ImageMetaSchema


class VideoSchema(DataSchema):
    meta: VideoMetaSchema


class DataSourceSchema(DaoSchema):
    name: str


class AssetSchema(DaoSchema):
    data: Union[ImageSchema, VideoSchema]


class PredictedAssetSchema(DaoSchema):
    data: ImageSchema


class ExperimentSchema(DaoSchema):
    name: str
    status: ExperimentStatus


class EvaluationSchema(DaoSchema):
    asset_id: UUID


class UserSchema(DaoSchema):
    username: str


class CollaboratorSchema(DaoSchema):
    user: UserSchema
    organization_id: UUID


class UsernameCollaboratorSchema(DaoSchema):
    username: str


class WorkerSchema(DaoSchema):
    collaborator: UsernameCollaboratorSchema


class ArtifactSchema(DaoSchema):
    name: str
    object_name: str
    filename: str
    large: bool
    url: Optional[str] = Field(alias="presigned_url", default=None)


class LoggingFileSchema(DaoSchema):
    object_name: str
    url: Optional[str] = Field(alias="presigned_url", default=None)


LogDataType = Union[list, dict, float, int, str]


class LogSchema(DaoSchema):
    name: str
    type: LogType
    data: LogDataType


class TagSchema(DaoSchema):
    name: str
    target_type: TagTarget


class LabelSchema(DaoSchema):
    name: str


class AnnotationSchema(DaoSchema):
    worker_id: UUID
    duration: float
    status: AnnotationStatus


class ShapeSchema(DaoSchema):
    label: LabelSchema
    text: Optional[str] = None


class RectangleSchema(ShapeSchema):
    x: int
    y: int
    w: int
    h: int


class PolygonSchema(ShapeSchema):
    coords: List = Field(alias="polygon")


class LineSchema(ShapeSchema):
    coords: List = Field(alias="line")


class PointSchema(ShapeSchema):
    coords: List = Field(alias="point")
    order: int


class ClassificationSchema(ShapeSchema):
    pass


class JobSchema(DaoSchema):
    status: JobStatus


class JobRunSchema(DaoSchema):
    status: JobRunStatus


class ProcessingSchema(DaoSchema):
    name: str
    type: ProcessingType
    docker_image: str
    docker_tag: str
