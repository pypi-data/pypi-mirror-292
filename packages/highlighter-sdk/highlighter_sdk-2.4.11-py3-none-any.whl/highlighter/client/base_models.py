from collections import defaultdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from uuid import UUID, uuid4
from warnings import warn

import numpy as np
from numpy.typing import NDArray
from pydantic import (
    ConfigDict,
    Field,
    PrivateAttr,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    field_validator,
)
from shapely import affinity
from shapely import geometry as geom
from shapely.wkt import loads as wkt_loads
from typing_extensions import Annotated

from highlighter.core.geometry import (
    get_top_left_bottom_right_coordinates,
    polygon_from_coords,
    polygon_from_tlbr,
)

from ..core import (
    DATA_FILE_ATTRIBUTE_UUID,
    EMBEDDING_ATTRIBUTE_UUID,
    OBJECT_CLASS_ATTRIBUTE_UUID,
    PIXEL_LOCATION_ATTRIBUTE_UUID,
    TRACK_ATTRIBUTE_UUID,
    HLBaseModel,
    LabeledUUID,
)

UUID_STR = Union[str, UUID]

__all__ = [
    "AccountType",
    "AgentType",
    "Annotation",
    "AnnotationType",
    "AttributeValue",
    "CaseType",
    "CompleteFileMultipartUploadPayload",
    "DataFileAttributeValue",
    "DatasetSubmissionType",
    "DatasetSubmissionTypeConnection",
    "DatumSource",
    "EAVT",
    "EmbeddingAttributeValue",
    "Entity",
    "EntityAttributeEnumType",
    "EntityAttributeType",
    "EntityAttributeValueType",
    "EnumAttributeValue",
    "ExperimentResult",
    "ExperimentType",
    "ImagePresignedType",
    "ImagePresignedType",
    "ImageQueueType",
    "ImageType",
    "ImageTypeConnection",
    "ObjectClass",
    "ObjectClassAttributeValue",
    "ObjectClassType",
    "ObjectClassTypeConnection",
    "PageInfo",
    "PipelineInstanceType",
    "PipelineType",
    "PixelLocationAttributeValue",
    "PluginType",
    "Point2d",
    "Polygon",
    "PresignedUrlType",
    "ProjectObjectClassType",
    "ProjectOrderType",
    "ProjectType",
    "ProjectTypeType",
    "ResearchPlanType",
    "ResearchPlanType",
    "ScalarAttributeValue",
    "StepType",
    "SubmissionType",
    "SubmissionTypeConnection",
    "TaskStatusEnum",
    "TaskType",
    "UserType",
]


def _get_uuid_str():
    return str(uuid4())


def _validate_uuid(v):
    if isinstance(v, UUID):
        return str(v)

    if v is None:
        warn("entity_id was not provided, generating one")
        return _get_uuid_str()

    try:
        _ = UUID(v)
        return v
    except:  # noqa
        raise ValueError("Invalid UUID string")


class PageInfo(HLBaseModel):
    has_next_page: bool
    end_cursor: Optional[str] = None


class ObjectClass(HLBaseModel):
    id: str
    uuid: str
    name: str


class ObjectClassTypeConnection(HLBaseModel):
    page_info: PageInfo
    nodes: List[ObjectClass]


class ImageType(HLBaseModel):
    id: str
    width: Optional[int] = None
    height: Optional[int] = None
    original_source_url: str
    mime_type: str


class ImagePresignedType(ImageType):
    file_url_original: str


class ImageTypeConnection(HLBaseModel):
    page_info: PageInfo
    nodes: List[ImageType]


class EntityAttributeType(HLBaseModel):
    id: str
    name: str


class EntityAttributeEnumType(HLBaseModel):
    id: str
    value: str


class DatumSource(HLBaseModel):
    """How did a piece-of-data 'datum' come to be."""

    frame_id: Optional[int] = None
    host_id: Optional[str] = None
    pipeline_element_name: Optional[str] = None
    pipeline_id: Optional[int] = None
    training_run_id: Optional[int] = None
    confidence: float


class EntityAttributeValueType(HLBaseModel):

    annotation_uuid: Optional[UUID] = None
    entity_attribute: EntityAttributeType
    entity_attribute_enum: Optional[EntityAttributeEnumType] = None
    entity_attribute_id: str
    entity_datum_source: Optional[DatumSource] = None
    entity_id: Optional[str] = Field(default_factory=_get_uuid_str)
    file_uuid: Optional[str] = None
    occurred_at: str
    related_entity_id: Optional[str] = None
    value: Optional[Any] = None

    @field_validator("entity_id")
    @classmethod
    def is_valid_uuid(cls, v):
        return _validate_uuid(v)

    def to_eavt(self):
        """
        self.annotation_uuid is lost in the conversion, make sure you're handling that separately.
        """
        value_count = (
            (0 if self.value is None else 1)
            + (0 if self.entity_attribute_enum is None else 1)
            + (0 if self.related_entity_id is None else 1)
        )
        if value_count == 0:
            raise ValueError(f"EntityAttributeValueType is invalid: Some value must be specified {self}")
        if value_count > 1:
            raise ValueError(f"EntityAttributeValueType is invalid: Multiple values specified {self}")
        value = (
            self.value if self.value is not None else self.related_entity_id or self.entity_attribute_enum.id
        )
        return EAVT(
            entity_id=self.entity_id,
            attribute_id=self.entity_attribute_id,
            value=value,
            time=self.occurred_at,
            datum_source=self.entity_datum_source,
        )


class UserType(HLBaseModel):
    id: int
    display_name: Optional[str] = None
    email: str
    uuid: Optional[UUID] = None


class AnnotationType(HLBaseModel):
    # location and confidence are guarantee to exist on AnnotationType
    location: str
    confidence: float = 1.0
    agent_name: Optional[str] = None
    data_type: str
    user_id: int
    user: UserType
    correlation_id: str
    is_inference: bool
    object_class: ObjectClass
    frame_id: Optional[int] = 0
    entity_id: Optional[str] = Field(default_factory=_get_uuid_str)
    uuid: UUID
    track_id: Optional[UUID] = None
    data_file_id: Optional[UUID] = None

    @field_validator("entity_id")
    @classmethod
    def is_valid_uuid(cls, v):
        return _validate_uuid(v)


class SubmissionType(HLBaseModel):
    id: int
    image_id: int
    annotations: List[AnnotationType]
    entity_attribute_values: List[EntityAttributeValueType]
    created_at: str
    image: ImageType
    hash_signature: Optional[str] = None
    user: UserType
    background_info_layer_file_data: Optional[Dict[str, Any]] = None
    background_info_layer_file_cacheable_url: Optional[str] = None


class SubmissionTypeConnection(HLBaseModel):
    page_info: PageInfo
    nodes: List[SubmissionType]


class DatasetSubmissionType(HLBaseModel):
    submission: SubmissionType


class DatasetSubmissionTypeConnection(HLBaseModel):
    page_info: PageInfo
    nodes: List[DatasetSubmissionType]


class ResearchPlanType(HLBaseModel):
    id: int
    title: str
    # ToDo: Probs need more fields


class ExperimentType(HLBaseModel):
    id: int
    research_plan: ResearchPlanType
    title: Optional[str] = None
    description: Optional[str] = None
    hypothesis: Optional[str] = None
    observation: Optional[str] = None
    conclusion: Optional[str] = None

    def to_markdown(self, save_path: str):
        def add_markdown_heading(s, heading):
            return f"## {heading}\n{s}\n"

        with open(str(save_path), "w") as f:
            f.write(f"# {self.title}\n")
            f.write(f"- **Experiment ID: {self.id}**\n")
            f.write(f"- **Research Plan ID: {self.researchPlan.id}**\n")
            f.write("\n---\n\n")

            f.write(
                add_markdown_heading(
                    self.description,
                    "Description",
                )
            )

            f.write(
                add_markdown_heading(
                    self.hypothesis,
                    "Hypothesis",
                )
            )

            f.write(
                add_markdown_heading(
                    self.observation,
                    "Observation",
                )
            )

            f.write(
                add_markdown_heading(
                    self.conclusion,
                    "Conclusion",
                )
            )


class PresignedUrlType(HLBaseModel):
    fields: Dict
    key: str
    storage: str
    url: str


class CompleteFileMultipartUploadPayload(HLBaseModel):
    errors: List[str]
    url: str


class PipelineInstanceType(HLBaseModel):
    id: str


class PipelineType(HLBaseModel):
    id: str


class TaskStatusEnum(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"


class StepType(HLBaseModel):
    id: str


class AgentType(HLBaseModel):
    id: str
    machine_agent_version_id: Optional[str] = None


class CaseType(HLBaseModel):
    id: str
    created_at: str


class TaskType(HLBaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str
    account_id: int
    created_at: str
    description: Optional[str] = None
    image: Optional[ImageType] = None
    leased_by_agent: Optional[AgentType] = None
    leased_by_pipeline_instance: Optional[PipelineInstanceType] = None
    leased_until: Optional[str] = None
    message: Optional[str] = None
    name: Optional[str] = None
    parameters: Optional[Any] = None
    pipeline: Optional[PipelineType] = None
    pipeline_id: Optional[str] = None
    requested_by: Optional[UserType] = None
    status: Optional[TaskStatusEnum] = None
    step: Optional[StepType] = None
    step_id: Optional[str] = None
    submission: Optional[SubmissionType] = None
    tags: Optional[List[str]] = None
    updated_at: str
    case: Optional[CaseType] = None


class ObjectClassType(HLBaseModel):
    id: int
    name: str
    color: Optional[str] = None
    annotations_count: Optional[int] = None
    account_id: Optional[int] = None
    default: bool
    parent_id: Optional[int] = None
    entity_attribute_enum: EntityAttributeEnumType
    uuid: str
    created_at: str
    updated_at: str


class ProjectObjectClassType(HLBaseModel):
    id: int
    object_class: ObjectClassType
    project_id: int
    created_at: str
    updated_at: str
    localised: bool
    entity_attributes: List[EntityAttributeType]
    sort_order: str


class PluginType(HLBaseModel):
    id: int
    account_id: int
    name: str
    description: str
    url: str
    default: bool
    module: str
    config: Any = None
    created_at: str
    updated_at: str
    project_id: int


class ProjectTypeType(HLBaseModel):
    id: int
    name: str
    created_at: str
    updated_at: str


class AccountType(HLBaseModel):
    id: int
    name: str
    subdomain: str
    data_usage: Optional[int] = None
    organisation_name: Optional[str] = None
    organisation_acn: Optional[str] = None
    hl_serving_mqtt_host: Optional[str] = None
    hl_serving_mqtt_port: Optional[int] = None
    hl_serving_mqtt_username: Optional[str] = None
    hl_serving_mqtt_ssl: bool
    users: List[UserType]
    created_at: str
    updated_at: str


class ImageQueueType(HLBaseModel):
    id: int
    created_at: str
    updated_at: str
    account: AccountType
    projectId: int
    name: str
    project_stage_id: str
    object_classes: List[ObjectClassType]
    submissions: List[SubmissionType]
    latest_submissions: List[SubmissionType]
    images: List[ImageType]
    all_images: List[ImageType]
    users: List[UserType]
    matched_image_count: int
    remaining_image_count: int
    locked_image_count: int
    available_image_count: int


class ProjectType(HLBaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: int
    name: str
    description: Optional[str] = None
    created_by_id: int
    account_id: int
    parent_id: Optional[int] = None
    object_classes: List[ObjectClassType]
    project_object_classes: List[ProjectObjectClassType]
    plugins: List[PluginType]
    project_type: Optional[ProjectTypeType] = None
    created_at: str
    updated_at: str
    owned_by_id: int
    model_id: Optional[int] = None
    active_checkpoint_id: Optional[int] = None
    batches_count: int
    metadata: Optional[Any] = None
    settings: Optional[Any] = None
    required_attributes: Optional[Any] = None
    multiline_attributes: Optional[Any] = None
    entity_attribute_taxon_groups: Optional[Any] = None
    ancestry: Optional[str] = None
    default_search_query: Optional[str] = None
    load_machine_submissions: bool
    project_type_id: Optional[int] = None
    submissions: List[SubmissionType]
    latest_submissions: List[SubmissionType]
    image_queues: List[ImageQueueType]


class ProjectOrderType(HLBaseModel):
    id: str


class ExperimentResult(HLBaseModel):
    baseline_dataset_id: Optional[int] = None
    comparison_dataset_id: Optional[int] = None
    created_at: str
    entity_attribute_id: Optional[str] = None
    experiment_id: int
    object_class_id: Optional[int] = None
    occured_at: str
    overlap_threshold: Optional[float] = None
    research_plan_metric_id: str
    result: float
    updated_at: str


# TODO: Validate points in polygon are in the right order
# TODO: Validate points do infact make a rectangle (as needed)
class Polygon(HLBaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    _compare_tolerance = PrivateAttr(0)
    _dtype = PrivateAttr(np.int64)
    _to_coordinates = PrivateAttr(
        {
            list: lambda x: np.array(x, dtype=Polygon._dtype.default),
            np.ndarray: lambda x: x.astype(Polygon._dtype.default),
        }
    )

    coordinates: Union[NDArray[np.int64], List[Tuple[int, int]]]

    def __init__(self, **data):
        super().__init__(**data)
        # this could also be done with default_factory

    @field_validator("coordinates", mode="before")
    @classmethod
    def cast_coords(cls, v):
        """Cast list or wkt_str to np.array coordinates
        pre=True tell the validator to run before the standard validation
        so it potential the v could be a string is taken care of

        """
        if isinstance(v, list):
            v = np.array(v, dtype=cls._dtype.default)
            assert (len(v.shape) == 2) and (v.shape[1] == 2)
        elif isinstance(v, str):
            from shapely import wkt

            shapely_poly = wkt.loads(v)
            points = [[int(x), int(y)] for x, y in shapely_poly.exterior.coords][:-1]
            v = np.array(points, dtype=cls._dtype.default)

        assert isinstance(v, np.ndarray) and (len(v.shape) == 2) and (v.shape[1] == 2)
        return v

    def __eq__(self, other):
        if not isinstance(other, Polygon):
            return False
        return np.allclose(self.coordinates, other.coordinates, rtol=0, atol=self._compare_tolerance.default)

    # Replaces from_numpy and from_list
    @classmethod
    def from_coordinates(cls, coordinates: Union[List[Tuple[int, int]], np.ndarray]):
        """Create Polygon BaseModel from list or np.array of points

        coordinates in form: [[x0,y0],...,[xn,yn]]

        Do not close the polygon. ie: [x0, y0] != [xn, yn]
        """
        to_coords_fn = cls._to_coordinates.default[type(coordinates)]
        coordinates = to_coords_fn(coordinates)
        return cls(coordinates=coordinates)

    @classmethod
    def from_wkt(cls, wkt_str):
        """Convert well-known text geometry string into HL polygons"""
        # simple polygons only; no interior boundaries
        shapely_poly = wkt_loads(wkt_str)
        points = [[int(x), int(y)] for x, y in shapely_poly.exterior.coords][:-1]
        return cls.from_coordinates(points)

    def to_list(self, t=int):
        return [[t(x), t(y)] for x, y in self.coordinates]

    # Transform into WKT Geometry: "POLYGON ((x0 y0, x1 y0, x1 y1, x0 y1, x0 y0))"
    def to_wkt(self):
        wkt_str = "POLYGON (("
        for x, y in self.coordinates:
            wkt_str += f"{x} {y},"

        # Close the polygon
        wkt_str += f"{self.coordinates[0][0]} {self.coordinates[0][1]}))"
        return wkt_str

    def scale(self, scale: float):
        self.coordinates = self.coordinates * scale
        return self

    def to_shapely_polygon(self, scale: float = 1.0, pad: int = 0) -> geom.Polygon:
        coords = self.coordinates.tolist()
        coords.append(coords[0])

        poly: geom.Polygon = geom.Polygon(coords)
        if scale != 1.0:
            poly = affinity.scale(poly, xfact=scale, yfact=scale, origin=(0, 0, 0))

        if pad != 0:
            poly = poly.buffer(pad, join_style=2)

        return poly

    def get_top_left_bottom_right_coordinates(
        self, scale: float = 1.0, scale_about_origin: bool = True, pad: int = 0
    ) -> Tuple[int, int, int, int]:
        """
        to top left bottom right format

        for embedding
        """
        if len(self.coordinates) < 2:
            raise ValueError(f"self.coordinates is malformed {self.coordinates}")
        if scale_about_origin:
            xs = self.coordinates[:, 0] * scale
            ys = self.coordinates[:, 1] * scale
        else:
            xs = self.coordinates[:, 0]
            ys = self.coordinates[:, 1]

            xmean = xs.mean()
            ymean = ys.mean()

            xs = ((xs - xmean) * scale) + xmean
            ys = ((ys - ymean) * scale) + ymean

        x0 = np.min(xs) - pad
        y0 = np.min(ys) - pad
        x1 = np.max(xs) + pad
        y1 = np.max(ys) + pad
        return x0, y0, x1, y1

    def is_valid(self) -> bool:
        return geom.Polygon(self.coordinates).is_valid

    def area(self) -> float:
        return geom.Polygon(self.coordinates).area

    def dict(self):
        return dict(
            coordinates=self.to_wkt(),
        )

    def __str__(self):
        return self.to_wkt()

    @classmethod
    def from_tlbr(cls, x: Tuple[int, int, int, int]) -> "Polygon":
        """
        from top left bottom right format
        """
        top_left = x[0], x[1]
        top_right = x[2], x[1]
        bottom_right = x[2], x[3]
        bottom_left = x[0], x[3]
        return Polygon(coordinates=np.array([top_left, top_right, bottom_right, bottom_left]))


class Point2d(HLBaseModel):
    x: int
    y: int

    @classmethod
    def from_xy(cls, xy: Tuple[int, int]):
        x, y = xy
        return cls(x=x, y=y)

    def to_wkt(self) -> str:
        return f"POINT({self.x} {self.y})"

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise KeyError(f"Expected 0|1 got: {key}")


class AttributeValue(HLBaseModel):
    attribute_id: LabeledUUID
    value: Any = None
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0

    def attribute_label(self):
        if isinstance(self.attribute_id, LabeledUUID):
            return self.attribute_id.label
        else:
            return str(self.attribute_id)[:8]

    def serialize_value(self):
        return self.value


class ObjectClassAttributeValue(AttributeValue):
    attribute_id: Union[LabeledUUID, UUID] = Field(default_factory=lambda: OBJECT_CLASS_ATTRIBUTE_UUID)
    value: UUID

    def serialize_value(self):
        return str(self.value)


class PixelLocationAttributeValue(AttributeValue):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    attribute_id: Union[LabeledUUID, UUID] = Field(default_factory=lambda: PIXEL_LOCATION_ATTRIBUTE_UUID)

    value: Union[geom.Polygon, geom.MultiPolygon, geom.LineString, geom.Point]

    def serialize_value(self):
        return self.value.wkt

    @field_validator("value")
    @classmethod
    def validate_geometry(cls, v):
        assert v.is_valid, f"Invalid Geometry: {v}"
        return v

    @classmethod
    def from_geom(
        cls,
        geom: Union[geom.Polygon, geom.MultiPolygon, geom.LineString, geom.Point],
        attribute_id: Union[LabeledUUID, UUID] = PIXEL_LOCATION_ATTRIBUTE_UUID,
        confidence: float = 1.0,
    ):
        """Create a LocationAttributeValue"""
        return cls(attribute_id=attribute_id, value=geom, confidence=confidence)

    def get_top_left_bottom_right_coordinates(
        self, scale: float = 1.0, scale_about_origin: bool = True, pad: int = 0
    ) -> Tuple[int, int, int, int]:
        """
        to top left bottom right format

        for embedding
        """
        return get_top_left_bottom_right_coordinates(self.value, scale, scale_about_origin, pad)


class EmbeddingAttributeValue(AttributeValue):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    attribute_id: Union[LabeledUUID, UUID] = Field(default_factory=lambda: EMBEDDING_ATTRIBUTE_UUID)
    value: Union[Sequence[float], np.ndarray]

    def serialize_value(self):
        return [float(i) for i in self.value]


class DataFileAttributeValue(AttributeValue):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    attribute_id: Union[LabeledUUID, UUID] = Field(default_factory=lambda: DATA_FILE_ATTRIBUTE_UUID)
    value: np.ndarray

    def serialize_value(self):
        raise NotImplementedError()


class EnumAttributeValue(AttributeValue):
    attribute_id: Union[LabeledUUID, UUID]
    value: Union[UUID, LabeledUUID]

    def serialize_value(self):
        raise str(self.value)


class ScalarAttributeValue(AttributeValue):
    attribute_id: Union[LabeledUUID, UUID]
    value: Union[float, int]


class EAVT(HLBaseModel):
    """
    entity_id and attribute_id are global
    value is tied to the attribute, and we have unit for it, so it doesn't appear here
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    entity_id: UUID
    attribute_id: LabeledUUID
    value: Union[
        LabeledUUID,
        UUID,
        Polygon,  # TODO remove as location is handled by Annotation
        Point2d,  # TODO remove as location is handled by Annotation
        List[StrictInt],
        StrictStr,
        StrictBool,
        StrictFloat,
        StrictInt,
        List[StrictStr],
        List[StrictFloat],
        np.ndarray,
        PixelLocationAttributeValue,  # TODO remove as location is handled by Annotation
    ]
    time: datetime = Field(
        ..., default_factory=lambda: datetime.now(timezone.utc)
    )  # TODO change to occurred_at
    datum_source: DatumSource
    unit: Optional[str] = None

    def model_dump(self, *args, **kwargs):
        value = self.value
        if isinstance(value, Polygon):
            value = value.dict()

        if isinstance(value, UUID):
            value = str(value)

        return dict(
            entity_id=str(self.entity_id),
            attribute_id=str(self.attribute_id),
            value=value,
            time=self.time.isoformat(),
            datum_source=self.datum_source.model_dump(),
        )

    def is_pixel_location(self):
        return str(self.attribute_id) == PIXEL_LOCATION_ATTRIBUTE_UUID

    def is_object_class(self):
        return str(self.attribute_id) == OBJECT_CLASS_ATTRIBUTE_UUID

    def is_track(self):
        return str(self.attribute_id) == TRACK_ATTRIBUTE_UUID

    def is_embedding(self):
        return str(self.attribute_id) == EMBEDDING_ATTRIBUTE_UUID

    def get_confidence(self):
        return self.datum_source.confidence

    @classmethod
    def make_scalar_eavt(
        cls,
        entity_id: UUID,
        value: Union[int, float, tuple, list],
        attribute_id: LabeledUUID,
        time: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
        unit: Optional[str] = None,
    ):
        datum_source = DatumSource(
            confidence=1.0,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
        )
        if isinstance(value, tuple):
            value = list(value)

        return cls(
            entity_id=entity_id,
            attribute_id=attribute_id,
            value=value,
            datum_source=datum_source,
            time=time,
            unit=unit,
        )

    @classmethod
    def make_image_eavt(
        cls,
        entity_id: UUID,
        image: np.ndarray,
        time: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
    ):
        datum_source = DatumSource(
            confidence=1.0,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
        )
        return cls(
            entity_id=entity_id,
            attribute_id=DATA_FILE_ATTRIBUTE_UUID,
            value=image,
            datum_source=datum_source,
            time=time,
        )

    @classmethod
    def make_embedding_eavt(
        cls,
        entity_id: UUID,
        embedding: List[float],
        time: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
    ):
        if not isinstance(embedding, list):
            t = type(embedding)
            raise ValueError(f"embedding must be list of float not {t}")

        datum_source = DatumSource(
            confidence=1.0,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
        )
        return cls(
            entity_id=entity_id,
            attribute_id=EMBEDDING_ATTRIBUTE_UUID,
            value=embedding,
            datum_source=datum_source,
            time=time,
        )

    @classmethod
    def make_pixel_location_eavt(
        cls,
        location_points: Union[
            Polygon,
            List[Tuple[int, int]],
            Point2d,
            Tuple[int, int],
            geom.Polygon,
            geom.MultiPolygon,
            geom.LineString,
            geom.Point,
            str,
        ],
        confidence: float,
        time: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
        entity_id: Optional[Union[str, UUID]] = None,
    ):
        """Create a new entity_id and assign a pixel_location
        attribute to the EAVT.

        The make_pixel_location_eavt is the only make_*
        method that will create a new entity_id.
        """
        if entity_id is None:
            entity_id = uuid4()

        if isinstance(location_points, Polygon):
            geometry = wkt_loads(location_points.to_wkt())
            value = PixelLocationAttributeValue.from_geom(geometry)
        elif isinstance(location_points, (geom.Polygon, geom.MultiPolygon)):
            value = PixelLocationAttributeValue.from_geom(location_points)
        elif isinstance(location_points, list):
            poly = polygon_from_coords(location_points)
            value = PixelLocationAttributeValue.from_geom(poly)
        elif isinstance(location_points, Point2d):
            geometry = wkt_loads(location_points.to_wkt())
            value = PixelLocationAttributeValue.from_geom(geometry)
        elif isinstance(location_points, tuple):
            value = PixelLocationAttributeValue.from_geom(geom.Point(location_points))
        elif isinstance(location_points, str):
            geometry = wkt_loads(location_points)
            value = PixelLocationAttributeValue.from_geom(geometry)
        else:
            raise ValueError(f"Invalid location_points: {location_points}")

        datum_source = DatumSource(
            confidence=confidence,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
        )

        return cls(
            entity_id=entity_id,
            attribute_id=PIXEL_LOCATION_ATTRIBUTE_UUID,
            value=value,
            datum_source=datum_source,
            time=time,
        )

    @classmethod
    def make_enum_eavt(
        cls,
        entity_id: UUID,
        attribute_uuid: UUID,
        attribute_label: str,
        enum_value: str,
        enum_id: UUID,
        confidence: float,
        time: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
    ):
        """Make an EAVT with an enum attribute for the given entity_id"""
        datum_source = DatumSource(
            confidence=confidence,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
        )

        return cls(
            entity_id=entity_id,
            attribute_id=LabeledUUID(
                attribute_uuid,
                label=attribute_label,
            ),
            value=LabeledUUID(
                enum_id,
                label=enum_value,
            ),
            datum_source=datum_source,
            time=time,
        )

    @classmethod
    def make_object_class_eavt(
        cls,
        entity_id: UUID,
        object_class_uuid: UUID,
        object_class_value: str,
        confidence: float,
        time: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
    ):
        """Convienence method to make an EAVT with an object_class attribute
        for the given entity_id
        """
        datum_source = DatumSource(
            confidence=confidence,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
        )

        return cls(
            entity_id=entity_id,
            attribute_id=OBJECT_CLASS_ATTRIBUTE_UUID,
            value=LabeledUUID(
                object_class_uuid,
                label=object_class_value,
            ),
            datum_source=datum_source,
            time=time,
        )

    @classmethod
    def make_boolean_eavt(
        cls,
        entity_id: UUID,
        attribute_uuid: UUID,
        attribute_label: str,
        value: bool,
        confidence: float,
        time: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
    ):
        """Convienence method to make an EAVT with an object_class attribute
        for the given entity_id
        """
        if not isinstance(value, bool):
            raise ValueError(
                "make_boolean_eavt expects value arg to be of type bool "
                f"got: {value} of type: {type(value)}"
            )

        datum_source = DatumSource(
            confidence=confidence,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
        )

        return cls(
            entity_id=entity_id,
            attribute_id=LabeledUUID(
                attribute_uuid,
                label=attribute_label,
            ),
            value=value,
            datum_source=datum_source,
            time=time,
        )

    @classmethod
    def make_detection_eavt_pair(
        cls,
        location_points: Union[
            Polygon, List[Tuple[int, int]], Point2d, Tuple[int, int], geom.Polygon, geom.MultiPolygon, str
        ],
        object_class_value: str,
        object_class_uuid: UUID,
        confidence: float,
        time: datetime,
        pipeline_element_name: Optional[str] = None,
        training_run_id: Optional[int] = None,
        host_id: Optional[str] = None,
        frame_id: Optional[int] = None,
    ):
        """Convienence method to make both a pixel_location and
        object_class attribute, returning them both in a list
        """
        pixel_location_eavt = EAVT.make_pixel_location_eavt(
            location_points,
            confidence,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
            time=time,
        )

        entity_id = pixel_location_eavt.entity_id

        object_class_eavt = EAVT.make_object_class_eavt(
            entity_id,
            object_class_uuid,
            object_class_value,
            confidence,
            pipeline_element_name=pipeline_element_name,
            training_run_id=training_run_id,
            host_id=host_id,
            frame_id=frame_id,
            time=time,
        )
        return [pixel_location_eavt, object_class_eavt]


class Annotation(HLBaseModel):
    id: UUID
    entity_id: UUID
    location: Optional[Union[geom.Polygon, geom.MultiPolygon, geom.LineString, geom.Point]] = None
    track_id: Optional[UUID] = None
    observations: List[EAVT]
    # TODO update HL Web to refer to data-sources (e.g. webrtc streams) as well as files
    data_file_id: Optional[UUID] = None
    datum_source: DatumSource
    correlation_id: Optional[UUID] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Required for shapely geometry types

    @field_validator("location")
    @classmethod
    def validate_geometry(cls, v):
        if v is not None:
            assert v.is_valid, f"Invalid Geometry: {v}"
        return v

    def gql_dict(self, data_file_id):
        try:
            object_class_observation = [
                observation
                for observation in self.observations
                if observation.attribute_id == OBJECT_CLASS_ATTRIBUTE_UUID
            ][-1]
        except IndexError:
            raise ValueError(
                "Annotation must have an object-class observation in order to submit to Highlighter"
            )

        if isinstance(self.location, geom.Polygon):
            data_type = "polygon"
        elif isinstance(self.location, geom.LineString):
            data_type = "line"
        elif isinstance(self.location, geom.Point):
            data_type = "point"
        else:
            data_type = "polygon"
        return {
            "objectClassUuid": str(object_class_observation.value),
            "location": self.location.wkt if self.location is not None else None,
            "confidence": self.datum_source.confidence,
            "dataType": data_type,
            "correlationId": str(self.correlation_id),
            "frameId": self.datum_source.frame_id,
            "trackId": self.track_id,
            "entityId": str(self.entity_id),
            "dataFileId": data_file_id,
            "uuid": str(self.id),
        }


class Entity(HLBaseModel):
    id: UUID
    annotations: List[Annotation] = []
    global_observations: List[EAVT] = []

    def to_eavts(self) -> List[EAVT]:
        eavts = []
        eavts.extend(self.global_observations)
        for annotation in self.annotations:
            eavts.extend(annotation.observations)
            if annotation.location is not None:
                eavts.append(
                    EAVT.make_pixel_location_eavt(
                        entity_id=annotation.entity_id,
                        location_points=annotation.location,
                        confidence=annotation.datum_source.confidence,
                        time=datetime.now(timezone.utc),
                        frame_id=annotation.datum_source.frame_id,
                    )
                )
        return eavts

    def to_deprecated_entity(self) -> "DeprecatedEntity":
        from haplomic.entity_attributes import Entity as DeprecatedEntity

        return DeprecatedEntity(
            entity_id=self.id,
            attributes={eavt.attribute_id: eavt for eavt in self.to_eavts()},
        )

    @staticmethod
    def entities_from_assessment(assessment: SubmissionType) -> Dict[UUID, "Entity"]:
        # Step 1: Group annotations and observations by entity, and further group observations by annotation
        grouped_entities = defaultdict(
            lambda: {"annotations": [], "observations": defaultdict(list), "global_observations": []}
        )
        for annotation in assessment.annotations:
            grouped_entities[annotation.entity_id]["annotations"].append(annotation)
        for observation in assessment.entity_attribute_values:
            if observation.annotation_uuid is not None:
                grouped_entities[observation.entity_id]["observations"][observation.annotation_uuid].append(
                    observation
                )
            else:
                grouped_entities[observation.entity_id]["global_observations"].append(observation)
        # Step 2: Convert Hl Web representations into our local representations
        entities = {}
        for entity_id, entity_data in grouped_entities.items():
            entity_id = entity_id
            annotations = []
            for annotation in entity_data["annotations"]:
                observations = [
                    EAVT(
                        entity_id=entity_id,
                        attribute_id=OBJECT_CLASS_ATTRIBUTE_UUID,
                        value=annotation.object_class.uuid,
                        time=datetime.now(
                            timezone.utc
                        ),  # TODO store with annotation in hl web or infer from source data file
                        datum_source=DatumSource(
                            frame_id=annotation.frame_id,
                            confidence=annotation.confidence,
                        ),
                    )
                ]
                for observation in entity_data["observations"][annotation.uuid]:
                    observations.append(observation.to_eavt())
                annotations.append(
                    Annotation(
                        id=uuid4(),  # Annotations need a fresh ID to be re-submitted
                        entity_id=entity_id,
                        location=wkt_loads(annotation.location),
                        track_id=annotation.track_id,
                        data_file_id=annotation.data_file_id,
                        datum_source=DatumSource(
                            frame_id=annotation.frame_id,
                            confidence=annotation.confidence,
                        ),
                        correlation_id=annotation.correlation_id,
                        observations=observations,
                    )
                )
            global_observations = []
            for observation in entity_data["global_observations"]:
                global_observations.append(
                    EAVT(
                        entity_id=observation.entity_id,
                        attribute_id=observation.attribute_id,
                        value=observation.value,
                        time=observation.time,
                        datum_source=DatumSource(confidence=observation.entity_datum_source.confidence),
                    )
                )
            entities[entity_id] = Entity(
                id=entity_id, annotations=annotations, global_observations=global_observations
            )
        return entities

    @staticmethod
    def frame_indexed_entities_from_avro(
        avro_entities, data_file_id: UUID
    ) -> List[Tuple[int, Dict[UUID, "Entity"]]]:
        """See Avro schema at highlighter.entity_avro_schema"""
        frame_indexed_entities = defaultdict(dict)  # Outer index is frame ID, inner index is entity ID
        for entity in avro_entities:
            # TODO handle embeddings
            # TODO handle eavts
            for track in entity.tracks:
                for detection in track.detections:
                    observations = [
                        EAVT(
                            entity_id=entity.id,
                            attribute_id=OBJECT_CLASS_ATTRIBUTE_UUID,
                            value=entity.object_class,
                            time=datetime.now(timezone.utc),  # TODO change to correct occurred_at
                            datum_source=DatumSource(
                                confidence=1.0,
                                frame_id=detection.frame_id,
                            ),
                        )
                    ]
                    annotations = [
                        Annotation(
                            id=uuid4(),
                            entity_id=entity.id,
                            location=polygon_from_tlbr(detection.bounds),
                            track_id=track.track_id,
                            observations=observations,
                            data_file_id=data_file_id,
                            datum_source=DatumSource(
                                confidence=1.0,
                                frame_id=detection.frame_id,
                            ),
                        )
                    ]
                    global_observations = []
                    frame_indexed_entities[detection.frame_id][entity.id] = Entity(
                        entity_id=entity.id,
                        annotations=annotations,
                        global_observations=global_observations,
                    )
        raise NotImplementedError("This implementation is a sketch, don't use without adding tests")
        return sorted(frame_indexed_entities.items(), key=lambda kv: kv[0])

    @staticmethod
    def entities_from_eavts(eavts: List[EAVT]) -> Dict[UUID, "Entity"]:
        entities = {}
        if len(eavts) > 0:
            grouped = defaultdict(list)
            for eavt in eavts:
                grouped[eavt.entity_id].append(eavt)
            for group in grouped.values():
                entity_id = group[0].entity_id
                location_eavts = [e for e in group if e.attribute_id == PIXEL_LOCATION_ATTRIBUTE_UUID]
                if len(location_eavts) == 0:
                    entities[entity_id] = Entity(
                        id=entity_id,
                        global_observations=group,
                        annotations=[],
                    )
                elif len(location_eavts) == 1:
                    location_eavt = location_eavts[0]
                    entities[entity_id] = Entity(
                        id=entity_id,
                        global_observations=[],
                        annotations=[
                            Annotation(
                                id=uuid4(),
                                entity_id=entity_id,
                                # The EAVT 'value' is a PixelLocationAttributeValue
                                # which has a shapely geometry as its 'value'
                                location=location_eavt.value.value,
                                datum_source=location_eavt.datum_source,
                                observations=[
                                    eavt
                                    for eavt in group
                                    if eavt.attribute_id != PIXEL_LOCATION_ATTRIBUTE_UUID
                                ],
                            )
                        ],
                    )
                else:
                    raise ValueError(
                        f"Can't handle {len(location_eavts)} pixel locations for a single entity"
                    )
        return entities

    @staticmethod
    def eavts_from_entities(entities: Dict[UUID, "Entity"]) -> List[EAVT]:
        eavts = []
        for entity in entities.values():
            eavts.extend(entity.to_eavts())
        return eavts

    @staticmethod
    def to_deprecated_entities(entities: Dict[UUID, "Entity"]) -> "DeprecatedEntities":
        from haplomic.entity_attributes import Entities as DeprecatedEntities

        deprecated_entities = DeprecatedEntities()
        for entity in entities.values():
            deprecated_entities.add_entity(entity.to_deprecated_entity())
        return deprecated_entities
