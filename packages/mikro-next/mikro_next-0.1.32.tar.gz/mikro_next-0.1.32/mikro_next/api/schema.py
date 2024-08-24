from mikro_next.funcs import execute, asubscribe, aexecute, subscribe
from mikro_next.rath import MikroNextRath
from mikro_next.traits import (
    EntityTrait,
    HasParquetStoreAccesor,
    HasZarrStoreAccessor,
    IsVectorizableTrait,
    HasZarrStoreTrait,
    OntologyTrait,
    HasPresignedDownloadAccessor,
    HasDownloadAccessor,
    EntityRelationKindTrait,
    HasParquestStoreTrait,
    EntityKindTrait,
)
from mikro_next.scalars import (
    Upload,
    ParquetLike,
    Milliseconds,
    FourByFourMatrix,
    ArrayLike,
    FiveDVector,
    FileLike,
    Micrometers,
)
from typing import List, Union, Literal, AsyncIterator, Tuple, Optional, Iterator, Any
from pydantic import Field, BaseModel
from datetime import datetime
from enum import Enum
from rath.scalars import ID


class RoiKind(str, Enum):
    ELLIPSIS = "ELLIPSIS"
    POLYGON = "POLYGON"
    LINE = "LINE"
    RECTANGLE = "RECTANGLE"
    SPECTRAL_RECTANGLE = "SPECTRAL_RECTANGLE"
    TEMPORAL_RECTANGLE = "TEMPORAL_RECTANGLE"
    CUBE = "CUBE"
    SPECTRAL_CUBE = "SPECTRAL_CUBE"
    TEMPORAL_CUBE = "TEMPORAL_CUBE"
    HYPERCUBE = "HYPERCUBE"
    SPECTRAL_HYPERCUBE = "SPECTRAL_HYPERCUBE"
    PATH = "PATH"
    FRAME = "FRAME"
    SLICE = "SLICE"
    POINT = "POINT"


class MetricDataType(str, Enum):
    INT = "INT"
    FLOAT = "FLOAT"
    DATETIME = "DATETIME"
    STRING = "STRING"


class ColorMap(str, Enum):
    VIRIDIS = "VIRIDIS"
    PLASMA = "PLASMA"
    INFERNO = "INFERNO"
    MAGMA = "MAGMA"
    RED = "RED"
    GREEN = "GREEN"
    BLUE = "BLUE"
    INTENSITY = "INTENSITY"


class Blending(str, Enum):
    ADDITIVE = "ADDITIVE"
    MULTIPLICATIVE = "MULTIPLICATIVE"


class RenderNodeKind(str, Enum):
    CONTEXT = "CONTEXT"
    OVERLAY = "OVERLAY"
    GRID = "GRID"
    SPIT = "SPIT"


class ProvenanceFilter(BaseModel):
    during: Optional[str] = None
    and_: Optional["ProvenanceFilter"] = Field(alias="AND", default=None)
    or_: Optional["ProvenanceFilter"] = Field(alias="OR", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class StrFilterLookup(BaseModel):
    exact: Optional[str] = None
    i_exact: Optional[str] = Field(alias="iExact", default=None)
    contains: Optional[str] = None
    i_contains: Optional[str] = Field(alias="iContains", default=None)
    in_list: Optional[Tuple[str, ...]] = Field(alias="inList", default=None)
    gt: Optional[str] = None
    gte: Optional[str] = None
    lt: Optional[str] = None
    lte: Optional[str] = None
    starts_with: Optional[str] = Field(alias="startsWith", default=None)
    i_starts_with: Optional[str] = Field(alias="iStartsWith", default=None)
    ends_with: Optional[str] = Field(alias="endsWith", default=None)
    i_ends_with: Optional[str] = Field(alias="iEndsWith", default=None)
    range: Optional[Tuple[str, ...]] = None
    is_null: Optional[bool] = Field(alias="isNull", default=None)
    regex: Optional[str] = None
    i_regex: Optional[str] = Field(alias="iRegex", default=None)
    n_exact: Optional[str] = Field(alias="nExact", default=None)
    n_i_exact: Optional[str] = Field(alias="nIExact", default=None)
    n_contains: Optional[str] = Field(alias="nContains", default=None)
    n_i_contains: Optional[str] = Field(alias="nIContains", default=None)
    n_in_list: Optional[Tuple[str, ...]] = Field(alias="nInList", default=None)
    n_gt: Optional[str] = Field(alias="nGt", default=None)
    n_gte: Optional[str] = Field(alias="nGte", default=None)
    n_lt: Optional[str] = Field(alias="nLt", default=None)
    n_lte: Optional[str] = Field(alias="nLte", default=None)
    n_starts_with: Optional[str] = Field(alias="nStartsWith", default=None)
    n_i_starts_with: Optional[str] = Field(alias="nIStartsWith", default=None)
    n_ends_with: Optional[str] = Field(alias="nEndsWith", default=None)
    n_i_ends_with: Optional[str] = Field(alias="nIEndsWith", default=None)
    n_range: Optional[Tuple[str, ...]] = Field(alias="nRange", default=None)
    n_is_null: Optional[bool] = Field(alias="nIsNull", default=None)
    n_regex: Optional[str] = Field(alias="nRegex", default=None)
    n_i_regex: Optional[str] = Field(alias="nIRegex", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class OffsetPaginationInput(BaseModel):
    offset: int
    limit: int

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class ImageFilter(BaseModel):
    name: Optional[StrFilterLookup] = None
    ids: Optional[Tuple[ID, ...]] = None
    store: Optional["ZarrStoreFilter"] = None
    dataset: Optional["DatasetFilter"] = None
    transformation_views: Optional["AffineTransformationViewFilter"] = Field(
        alias="transformationViews", default=None
    )
    timepoint_views: Optional["TimepointViewFilter"] = Field(
        alias="timepointViews", default=None
    )
    not_derived: Optional[bool] = Field(alias="notDerived", default=None)
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["ImageFilter"] = Field(alias="AND", default=None)
    or_: Optional["ImageFilter"] = Field(alias="OR", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class ZarrStoreFilter(BaseModel):
    shape: Optional["IntFilterLookup"] = None
    and_: Optional["ZarrStoreFilter"] = Field(alias="AND", default=None)
    or_: Optional["ZarrStoreFilter"] = Field(alias="OR", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class IntFilterLookup(BaseModel):
    exact: Optional[int] = None
    i_exact: Optional[int] = Field(alias="iExact", default=None)
    contains: Optional[int] = None
    i_contains: Optional[int] = Field(alias="iContains", default=None)
    in_list: Optional[Tuple[int, ...]] = Field(alias="inList", default=None)
    gt: Optional[int] = None
    gte: Optional[int] = None
    lt: Optional[int] = None
    lte: Optional[int] = None
    starts_with: Optional[int] = Field(alias="startsWith", default=None)
    i_starts_with: Optional[int] = Field(alias="iStartsWith", default=None)
    ends_with: Optional[int] = Field(alias="endsWith", default=None)
    i_ends_with: Optional[int] = Field(alias="iEndsWith", default=None)
    range: Optional[Tuple[int, ...]] = None
    is_null: Optional[bool] = Field(alias="isNull", default=None)
    regex: Optional[str] = None
    i_regex: Optional[str] = Field(alias="iRegex", default=None)
    n_exact: Optional[int] = Field(alias="nExact", default=None)
    n_i_exact: Optional[int] = Field(alias="nIExact", default=None)
    n_contains: Optional[int] = Field(alias="nContains", default=None)
    n_i_contains: Optional[int] = Field(alias="nIContains", default=None)
    n_in_list: Optional[Tuple[int, ...]] = Field(alias="nInList", default=None)
    n_gt: Optional[int] = Field(alias="nGt", default=None)
    n_gte: Optional[int] = Field(alias="nGte", default=None)
    n_lt: Optional[int] = Field(alias="nLt", default=None)
    n_lte: Optional[int] = Field(alias="nLte", default=None)
    n_starts_with: Optional[int] = Field(alias="nStartsWith", default=None)
    n_i_starts_with: Optional[int] = Field(alias="nIStartsWith", default=None)
    n_ends_with: Optional[int] = Field(alias="nEndsWith", default=None)
    n_i_ends_with: Optional[int] = Field(alias="nIEndsWith", default=None)
    n_range: Optional[Tuple[int, ...]] = Field(alias="nRange", default=None)
    n_is_null: Optional[bool] = Field(alias="nIsNull", default=None)
    n_regex: Optional[str] = Field(alias="nRegex", default=None)
    n_i_regex: Optional[str] = Field(alias="nIRegex", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class DatasetFilter(BaseModel):
    id: Optional[ID] = None
    name: Optional[StrFilterLookup] = None
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["DatasetFilter"] = Field(alias="AND", default=None)
    or_: Optional["DatasetFilter"] = Field(alias="OR", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class AffineTransformationViewFilter(BaseModel):
    is_global: Optional[bool] = Field(alias="isGlobal", default=None)
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["AffineTransformationViewFilter"] = Field(alias="AND", default=None)
    or_: Optional["AffineTransformationViewFilter"] = Field(alias="OR", default=None)
    stage: Optional["StageFilter"] = None
    pixel_size: Optional["FloatFilterLookup"] = Field(alias="pixelSize", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class StageFilter(BaseModel):
    ids: Optional[Tuple[ID, ...]] = None
    search: Optional[str] = None
    id: Optional[ID] = None
    kind: Optional[str] = None
    name: Optional[StrFilterLookup] = None
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["StageFilter"] = Field(alias="AND", default=None)
    or_: Optional["StageFilter"] = Field(alias="OR", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class FloatFilterLookup(BaseModel):
    exact: Optional[float] = None
    i_exact: Optional[float] = Field(alias="iExact", default=None)
    contains: Optional[float] = None
    i_contains: Optional[float] = Field(alias="iContains", default=None)
    in_list: Optional[Tuple[float, ...]] = Field(alias="inList", default=None)
    gt: Optional[float] = None
    gte: Optional[float] = None
    lt: Optional[float] = None
    lte: Optional[float] = None
    starts_with: Optional[float] = Field(alias="startsWith", default=None)
    i_starts_with: Optional[float] = Field(alias="iStartsWith", default=None)
    ends_with: Optional[float] = Field(alias="endsWith", default=None)
    i_ends_with: Optional[float] = Field(alias="iEndsWith", default=None)
    range: Optional[Tuple[float, ...]] = None
    is_null: Optional[bool] = Field(alias="isNull", default=None)
    regex: Optional[str] = None
    i_regex: Optional[str] = Field(alias="iRegex", default=None)
    n_exact: Optional[float] = Field(alias="nExact", default=None)
    n_i_exact: Optional[float] = Field(alias="nIExact", default=None)
    n_contains: Optional[float] = Field(alias="nContains", default=None)
    n_i_contains: Optional[float] = Field(alias="nIContains", default=None)
    n_in_list: Optional[Tuple[float, ...]] = Field(alias="nInList", default=None)
    n_gt: Optional[float] = Field(alias="nGt", default=None)
    n_gte: Optional[float] = Field(alias="nGte", default=None)
    n_lt: Optional[float] = Field(alias="nLt", default=None)
    n_lte: Optional[float] = Field(alias="nLte", default=None)
    n_starts_with: Optional[float] = Field(alias="nStartsWith", default=None)
    n_i_starts_with: Optional[float] = Field(alias="nIStartsWith", default=None)
    n_ends_with: Optional[float] = Field(alias="nEndsWith", default=None)
    n_i_ends_with: Optional[float] = Field(alias="nIEndsWith", default=None)
    n_range: Optional[Tuple[float, ...]] = Field(alias="nRange", default=None)
    n_is_null: Optional[bool] = Field(alias="nIsNull", default=None)
    n_regex: Optional[str] = Field(alias="nRegex", default=None)
    n_i_regex: Optional[str] = Field(alias="nIRegex", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class TimepointViewFilter(BaseModel):
    is_global: Optional[bool] = Field(alias="isGlobal", default=None)
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["TimepointViewFilter"] = Field(alias="AND", default=None)
    or_: Optional["TimepointViewFilter"] = Field(alias="OR", default=None)
    era: Optional["EraFilter"] = None
    ms_since_start: Optional[float] = Field(alias="msSinceStart", default=None)
    index_since_start: Optional[int] = Field(alias="indexSinceStart", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class EraFilter(BaseModel):
    id: Optional[ID] = None
    begin: Optional[datetime] = None
    provenance: Optional[ProvenanceFilter] = None
    and_: Optional["EraFilter"] = Field(alias="AND", default=None)
    or_: Optional["EraFilter"] = Field(alias="OR", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialChannelViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    channel: ID

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialAffineTransformationViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    stage: Optional[ID] = None
    affine_matrix: FourByFourMatrix = Field(alias="affineMatrix")

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialAcquisitionViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    description: Optional[str] = None
    acquired_at: Optional[datetime] = Field(alias="acquiredAt", default=None)
    operator: Optional[ID] = None

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialPixelViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    linked_view: Optional[ID] = Field(alias="linkedView", default=None)
    range_labels: Optional[Tuple["RangePixelLabel", ...]] = Field(
        alias="rangeLabels", default=None
    )

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class RangePixelLabel(BaseModel):
    group: Optional[ID] = None
    entity_kind: ID = Field(alias="entityKind")
    min: int
    max: int

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialSpecimenViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    specimen: Optional[ID] = None
    step: Optional[ID] = None

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialRGBViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    context: Optional[ID] = None
    gamma: Optional[float] = None
    contrast_limit_min: Optional[float] = Field(alias="contrastLimitMin", default=None)
    contrast_limit_max: Optional[float] = Field(alias="contrastLimitMax", default=None)
    rescale: Optional[bool] = None
    scale: Optional[float] = None
    active: Optional[bool] = None
    color_map: Optional[ColorMap] = Field(alias="colorMap", default=None)
    base_color: Optional[Tuple[float, ...]] = Field(alias="baseColor", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialTimepointViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    era: Optional[ID] = None
    ms_since_start: Optional[Milliseconds] = Field(alias="msSinceStart", default=None)
    index_since_start: Optional[int] = Field(alias="indexSinceStart", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialOpticsViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    instrument: Optional[ID] = None
    objective: Optional[ID] = None
    camera: Optional[ID] = None

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class PartialScaleViewInput(BaseModel):
    collection: Optional[ID] = None
    z_min: Optional[int] = Field(alias="zMin", default=None)
    z_max: Optional[int] = Field(alias="zMax", default=None)
    x_min: Optional[int] = Field(alias="xMin", default=None)
    x_max: Optional[int] = Field(alias="xMax", default=None)
    y_min: Optional[int] = Field(alias="yMin", default=None)
    y_max: Optional[int] = Field(alias="yMax", default=None)
    t_min: Optional[int] = Field(alias="tMin", default=None)
    t_max: Optional[int] = Field(alias="tMax", default=None)
    c_min: Optional[int] = Field(alias="cMin", default=None)
    c_max: Optional[int] = Field(alias="cMax", default=None)
    parent: Optional[ID] = None
    scale_x: Optional[float] = Field(alias="scaleX", default=None)
    scale_y: Optional[float] = Field(alias="scaleY", default=None)
    scale_z: Optional[float] = Field(alias="scaleZ", default=None)
    scale_t: Optional[float] = Field(alias="scaleT", default=None)
    scale_c: Optional[float] = Field(alias="scaleC", default=None)

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class TreeInput(BaseModel):
    id: Optional[str] = None
    children: Tuple["TreeNodeInput", ...]

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class TreeNodeInput(BaseModel):
    kind: RenderNodeKind
    label: Optional[str] = None
    context: Optional[str] = None
    gap: Optional[int] = None
    children: Optional[Tuple["TreeNodeInput", ...]] = None

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class EntityValuePairInput(BaseModel):
    entity: ID
    value: Any

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class OverlayInput(BaseModel):
    object: str
    identifier: str
    color: str
    x: int
    y: int

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class CreateRGBContextInput(BaseModel):
    name: Optional[str] = None
    thumbnail: Optional[ID] = None
    image: ID
    views: Optional[Tuple[PartialRGBViewInput, ...]] = None
    z: Optional[int] = None
    t: Optional[int] = None
    c: Optional[int] = None

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class UpdateRGBContextInput(BaseModel):
    id: ID
    name: Optional[str] = None
    thumbnail: Optional[ID] = None
    views: Optional[Tuple[PartialRGBViewInput, ...]] = None
    z: Optional[int] = None
    t: Optional[int] = None
    c: Optional[int] = None

    class Config:
        """A config class"""

        frozen = True
        extra = "forbid"
        allow_population_by_field_name = True
        use_enum_values = True


class ViewBase(BaseModel):
    z_min: Optional[int] = Field(alias="zMin")
    z_max: Optional[int] = Field(alias="zMax")


class ChannelView(ViewBase, BaseModel):
    typename: Optional[Literal["ChannelView"]] = Field(alias="__typename", exclude=True)
    id: ID
    channel: "Channel"

    class Config:
        """A config class"""

        frozen = True


class AffineTransformationViewStage(BaseModel):
    typename: Optional[Literal["Stage"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class AffineTransformationView(ViewBase, BaseModel):
    typename: Optional[Literal["AffineTransformationView"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    affine_matrix: FourByFourMatrix = Field(alias="affineMatrix")
    stage: AffineTransformationViewStage

    class Config:
        """A config class"""

        frozen = True


class TimepointView(ViewBase, BaseModel):
    typename: Optional[Literal["TimepointView"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    ms_since_start: Optional[Milliseconds] = Field(alias="msSinceStart")
    index_since_start: Optional[int] = Field(alias="indexSinceStart")
    era: "Era"

    class Config:
        """A config class"""

        frozen = True


class OpticsViewObjective(BaseModel):
    typename: Optional[Literal["Objective"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    serial_number: str = Field(alias="serialNumber")

    class Config:
        """A config class"""

        frozen = True


class OpticsViewCamera(BaseModel):
    typename: Optional[Literal["Camera"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    serial_number: str = Field(alias="serialNumber")

    class Config:
        """A config class"""

        frozen = True


class OpticsViewInstrument(BaseModel):
    typename: Optional[Literal["Instrument"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    serial_number: str = Field(alias="serialNumber")

    class Config:
        """A config class"""

        frozen = True


class OpticsView(ViewBase, BaseModel):
    typename: Optional[Literal["OpticsView"]] = Field(alias="__typename", exclude=True)
    objective: Optional[OpticsViewObjective]
    camera: Optional[OpticsViewCamera]
    instrument: Optional[OpticsViewInstrument]

    class Config:
        """A config class"""

        frozen = True


class LabelViewFluorophoreKind(EntityKindTrait, BaseModel):
    typename: Optional[Literal["EntityKind"]] = Field(alias="__typename", exclude=True)
    id: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class LabelViewFluorophore(EntityTrait, BaseModel):
    typename: Optional[Literal["Entity"]] = Field(alias="__typename", exclude=True)
    id: ID
    kind: LabelViewFluorophoreKind
    name: str

    class Config:
        """A config class"""

        frozen = True


class LabelViewPrimaryantibodyKind(EntityKindTrait, BaseModel):
    typename: Optional[Literal["EntityKind"]] = Field(alias="__typename", exclude=True)
    id: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class LabelViewPrimaryantibody(EntityTrait, BaseModel):
    typename: Optional[Literal["Entity"]] = Field(alias="__typename", exclude=True)
    id: ID
    kind: LabelViewPrimaryantibodyKind
    name: str

    class Config:
        """A config class"""

        frozen = True


class LabelViewSecondaryantibodyKind(EntityKindTrait, BaseModel):
    typename: Optional[Literal["EntityKind"]] = Field(alias="__typename", exclude=True)
    id: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class LabelViewSecondaryantibody(EntityTrait, BaseModel):
    typename: Optional[Literal["Entity"]] = Field(alias="__typename", exclude=True)
    id: ID
    kind: LabelViewSecondaryantibodyKind
    name: str

    class Config:
        """A config class"""

        frozen = True


class LabelView(ViewBase, BaseModel):
    typename: Optional[Literal["LabelView"]] = Field(alias="__typename", exclude=True)
    id: ID
    fluorophore: Optional[LabelViewFluorophore]
    primary_antibody: Optional[LabelViewPrimaryantibody] = Field(
        alias="primaryAntibody"
    )
    secondary_antibody: Optional[LabelViewSecondaryantibody] = Field(
        alias="secondaryAntibody"
    )

    class Config:
        """A config class"""

        frozen = True


class ScaleView(ViewBase, BaseModel):
    typename: Optional[Literal["ScaleView"]] = Field(alias="__typename", exclude=True)
    id: ID
    scale_x: float = Field(alias="scaleX")
    scale_y: float = Field(alias="scaleY")
    scale_z: float = Field(alias="scaleZ")
    scale_t: float = Field(alias="scaleT")
    scale_c: float = Field(alias="scaleC")

    class Config:
        """A config class"""

        frozen = True


class RGBView(ViewBase, BaseModel):
    typename: Optional[Literal["RGBView"]] = Field(alias="__typename", exclude=True)
    id: ID
    color_map: ColorMap = Field(alias="colorMap")
    contrast_limit_min: Optional[float] = Field(alias="contrastLimitMin")
    contrast_limit_max: Optional[float] = Field(alias="contrastLimitMax")
    gamma: Optional[float]
    rescale: bool
    active: bool
    c_min: Optional[int] = Field(alias="cMin")
    c_max: Optional[int] = Field(alias="cMax")
    full_colour: str = Field(alias="fullColour")
    base_color: Optional[Tuple[int, ...]] = Field(alias="baseColor")

    class Config:
        """A config class"""

        frozen = True


class Camera(BaseModel):
    typename: Optional[Literal["Camera"]] = Field(alias="__typename", exclude=True)
    sensor_size_x: Optional[int] = Field(alias="sensorSizeX")
    sensor_size_y: Optional[int] = Field(alias="sensorSizeY")
    pixel_size_x: Optional[Micrometers] = Field(alias="pixelSizeX")
    pixel_size_y: Optional[Micrometers] = Field(alias="pixelSizeY")
    name: str
    serial_number: str = Field(alias="serialNumber")

    class Config:
        """A config class"""

        frozen = True


class ProtocolStepMappingProtocolExperiment(BaseModel):
    typename: Optional[Literal["Experiment"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    description: Optional[str]

    class Config:
        """A config class"""

        frozen = True


class ProtocolStepMappingProtocol(BaseModel):
    typename: Optional[Literal["Protocol"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    experiment: ProtocolStepMappingProtocolExperiment

    class Config:
        """A config class"""

        frozen = True


class ProtocolStepMappingStep(BaseModel):
    typename: Optional[Literal["ProtocolStep"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class ProtocolStepMapping(BaseModel):
    typename: Optional[Literal["ProtocolStepMapping"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    t: Optional[int]
    protocol: ProtocolStepMappingProtocol
    step: ProtocolStepMappingStep

    class Config:
        """A config class"""

        frozen = True


class TableOrigins(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class Table(HasParquestStoreTrait, BaseModel):
    typename: Optional[Literal["Table"]] = Field(alias="__typename", exclude=True)
    origins: Tuple[TableOrigins, ...]
    id: ID
    name: str
    store: "ParquetStore"

    class Config:
        """A config class"""

        frozen = True


class RenderedPlotStore(HasPresignedDownloadAccessor, BaseModel):
    typename: Optional[Literal["MediaStore"]] = Field(alias="__typename", exclude=True)
    id: ID
    key: str

    class Config:
        """A config class"""

        frozen = True


class RenderedPlot(BaseModel):
    typename: Optional[Literal["RenderedPlot"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    store: RenderedPlotStore

    class Config:
        """A config class"""

        frozen = True


class ListRenderedPlotStore(HasPresignedDownloadAccessor, BaseModel):
    typename: Optional[Literal["MediaStore"]] = Field(alias="__typename", exclude=True)
    id: ID
    key: str

    class Config:
        """A config class"""

        frozen = True


class ListRenderedPlot(BaseModel):
    typename: Optional[Literal["RenderedPlot"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    store: ListRenderedPlotStore

    class Config:
        """A config class"""

        frozen = True


class Credentials(BaseModel):
    typename: Optional[Literal["Credentials"]] = Field(alias="__typename", exclude=True)
    access_key: str = Field(alias="accessKey")
    status: str
    secret_key: str = Field(alias="secretKey")
    bucket: str
    key: str
    session_token: str = Field(alias="sessionToken")
    store: str

    class Config:
        """A config class"""

        frozen = True


class AccessCredentials(BaseModel):
    typename: Optional[Literal["AccessCredentials"]] = Field(
        alias="__typename", exclude=True
    )
    access_key: str = Field(alias="accessKey")
    secret_key: str = Field(alias="secretKey")
    bucket: str
    key: str
    session_token: str = Field(alias="sessionToken")
    path: str

    class Config:
        """A config class"""

        frozen = True


class FileOrigins(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class File(BaseModel):
    typename: Optional[Literal["File"]] = Field(alias="__typename", exclude=True)
    origins: Tuple[FileOrigins, ...]
    id: ID
    name: str
    store: "BigFileStore"

    class Config:
        """A config class"""

        frozen = True


class EntityKindOntology(OntologyTrait, BaseModel):
    typename: Optional[Literal["Ontology"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class EntityKind(EntityKindTrait, BaseModel):
    typename: Optional[Literal["EntityKind"]] = Field(alias="__typename", exclude=True)
    id: ID
    label: str
    ontology: EntityKindOntology

    class Config:
        """A config class"""

        frozen = True


class Stage(BaseModel):
    typename: Optional[Literal["Stage"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class ROIImage(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class ROI(IsVectorizableTrait, BaseModel):
    typename: Optional[Literal["ROI"]] = Field(alias="__typename", exclude=True)
    id: ID
    image: ROIImage
    vectors: Tuple[FiveDVector, ...]
    kind: RoiKind

    class Config:
        """A config class"""

        frozen = True


class Objective(BaseModel):
    typename: Optional[Literal["Objective"]] = Field(alias="__typename", exclude=True)
    id: ID
    na: Optional[float]
    name: str
    serial_number: str = Field(alias="serialNumber")

    class Config:
        """A config class"""

        frozen = True


class RGBContextImage(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    id: ID
    store: "ZarrStore"
    "The store where the image data is stored."

    class Config:
        """A config class"""

        frozen = True


class RGBContext(BaseModel):
    typename: Optional[Literal["RGBContext"]] = Field(alias="__typename", exclude=True)
    id: ID
    views: Tuple[RGBView, ...]
    image: RGBContextImage
    pinned: bool
    name: str
    z: int
    t: int
    c: int
    blending: Blending

    class Config:
        """A config class"""

        frozen = True


class RelationMetric(BaseModel):
    typename: Optional[Literal["RelationMetric"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    kind: EntityKind
    data_kind: MetricDataType = Field(alias="dataKind")

    class Config:
        """A config class"""

        frozen = True


class ProtocolStepMappingsProtocol(BaseModel):
    typename: Optional[Literal["Protocol"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class ProtocolStepMappings(BaseModel):
    typename: Optional[Literal["ProtocolStepMapping"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    protocol: ProtocolStepMappingsProtocol

    class Config:
        """A config class"""

        frozen = True


class ProtocolStepReagents(EntityTrait, BaseModel):
    typename: Optional[Literal["Entity"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class ProtocolStepViewsSpecimen(BaseModel):
    typename: Optional[Literal["Specimen"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class ProtocolStepViewsImage(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class ProtocolStepViews(BaseModel):
    typename: Optional[Literal["SpecimenView"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    specimen: ProtocolStepViewsSpecimen
    image: ProtocolStepViewsImage

    class Config:
        """A config class"""

        frozen = True


class ProtocolStep(BaseModel):
    typename: Optional[Literal["ProtocolStep"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    mappings: Tuple[ProtocolStepMappings, ...]
    description: Optional[str]
    reagents: Tuple[ProtocolStepReagents, ...]
    views: Tuple[ProtocolStepViews, ...]

    class Config:
        """A config class"""

        frozen = True


class HistoryStuffApp(BaseModel):
    """An app."""

    typename: Optional[Literal["App"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class HistoryStuff(BaseModel):
    typename: Optional[Literal["History"]] = Field(alias="__typename", exclude=True)
    id: ID
    app: Optional[HistoryStuffApp]

    class Config:
        """A config class"""

        frozen = True


class Dataset(BaseModel):
    typename: Optional[Literal["Dataset"]] = Field(alias="__typename", exclude=True)
    name: str
    description: Optional[str]
    history: Tuple[HistoryStuff, ...]

    class Config:
        """A config class"""

        frozen = True


class SpecimenEntityKind(EntityKindTrait, BaseModel):
    typename: Optional[Literal["EntityKind"]] = Field(alias="__typename", exclude=True)
    id: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SpecimenEntityGroup(BaseModel):
    typename: Optional[Literal["EntityGroup"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class SpecimenEntity(EntityTrait, BaseModel):
    typename: Optional[Literal["Entity"]] = Field(alias="__typename", exclude=True)
    id: ID
    kind: SpecimenEntityKind
    name: str
    group: SpecimenEntityGroup

    class Config:
        """A config class"""

        frozen = True


class SpecimenProtocol(BaseModel):
    typename: Optional[Literal["Protocol"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class Specimen(BaseModel):
    typename: Optional[Literal["Specimen"]] = Field(alias="__typename", exclude=True)
    id: ID
    entity: SpecimenEntity
    protocol: SpecimenProtocol

    class Config:
        """A config class"""

        frozen = True


class Instrument(BaseModel):
    typename: Optional[Literal["Instrument"]] = Field(alias="__typename", exclude=True)
    id: ID
    model: Optional[str]
    name: str
    serial_number: str = Field(alias="serialNumber")

    class Config:
        """A config class"""

        frozen = True


class EntityRelationLeft(EntityTrait, BaseModel):
    typename: Optional[Literal["Entity"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class EntityRelationRight(EntityTrait, BaseModel):
    typename: Optional[Literal["Entity"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class EntityRelationKind(EntityRelationKindTrait, BaseModel):
    typename: Optional[Literal["EntityRelationKind"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID

    class Config:
        """A config class"""

        frozen = True


class EntityRelation(BaseModel):
    typename: Optional[Literal["EntityRelation"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    left: EntityRelationLeft
    right: EntityRelationRight
    kind: EntityRelationKind

    class Config:
        """A config class"""

        frozen = True


class EntityRelationKindLeftkind(EntityKindTrait, BaseModel):
    typename: Optional[Literal["EntityKind"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class EntityRelationKindRightkind(EntityKindTrait, BaseModel):
    typename: Optional[Literal["EntityKind"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class EntityRelationKindKind(EntityKindTrait, BaseModel):
    typename: Optional[Literal["EntityKind"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class EntityRelationKind(EntityRelationKindTrait, BaseModel):
    typename: Optional[Literal["EntityRelationKind"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    left_kind: EntityRelationKindLeftkind = Field(alias="leftKind")
    right_kind: EntityRelationKindRightkind = Field(alias="rightKind")
    kind: EntityRelationKindKind

    class Config:
        """A config class"""

        frozen = True


class EntityMetric(BaseModel):
    typename: Optional[Literal["EntityMetric"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    kind: EntityKind
    data_kind: MetricDataType = Field(alias="dataKind")

    class Config:
        """A config class"""

        frozen = True


class ImageOrigins(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class ImageViewsBase(BaseModel):
    pass

    class Config:
        """A config class"""

        frozen = True


class ImageViewsChannelView(ImageViewsBase, ChannelView):
    pass

    class Config:
        """A config class"""

        frozen = True


class ImageViewsAffineTransformationView(ImageViewsBase, AffineTransformationView):
    pass

    class Config:
        """A config class"""

        frozen = True


class ImageViewsLabelView(ImageViewsBase, LabelView):
    pass

    class Config:
        """A config class"""

        frozen = True


class ImageViewsTimepointView(ImageViewsBase, TimepointView):
    pass

    class Config:
        """A config class"""

        frozen = True


class ImageViewsOpticsView(ImageViewsBase, OpticsView):
    pass

    class Config:
        """A config class"""

        frozen = True


class ImageViewsScaleView(ImageViewsBase, ScaleView):
    pass

    class Config:
        """A config class"""

        frozen = True


class ImageDerivedscaleviewsImage(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    name: str
    store: "ZarrStore"
    "The store where the image data is stored."

    class Config:
        """A config class"""

        frozen = True


class ImageDerivedscaleviews(ScaleView, BaseModel):
    typename: Optional[Literal["ScaleView"]] = Field(alias="__typename", exclude=True)
    image: ImageDerivedscaleviewsImage

    class Config:
        """A config class"""

        frozen = True


class ImageRgbcontexts(BaseModel):
    typename: Optional[Literal["RGBContext"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    views: Tuple[RGBView, ...]

    class Config:
        """A config class"""

        frozen = True


class Image(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    origins: Tuple[ImageOrigins, ...]
    id: ID
    name: str
    store: "ZarrStore"
    "The store where the image data is stored."
    views: Tuple[
        Union[
            ImageViewsChannelView,
            ImageViewsAffineTransformationView,
            ImageViewsLabelView,
            ImageViewsTimepointView,
            ImageViewsOpticsView,
            ImageViewsScaleView,
        ],
        ...,
    ]
    derived_scale_views: Tuple[ImageDerivedscaleviews, ...] = Field(
        alias="derivedScaleViews"
    )
    rgb_contexts: Tuple[ImageRgbcontexts, ...] = Field(alias="rgbContexts")

    class Config:
        """A config class"""

        frozen = True


class EntityKindOntology(OntologyTrait, BaseModel):
    typename: Optional[Literal["Ontology"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class EntityKind(EntityKindTrait, BaseModel):
    typename: Optional[Literal["EntityKind"]] = Field(alias="__typename", exclude=True)
    id: ID
    label: str
    ontology: EntityKindOntology

    class Config:
        """A config class"""

        frozen = True


class EntityGroup(BaseModel):
    typename: Optional[Literal["EntityGroup"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class Entity(EntityTrait, BaseModel):
    typename: Optional[Literal["Entity"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    kind: EntityKind
    group: EntityGroup

    class Config:
        """A config class"""

        frozen = True


class Era(BaseModel):
    typename: Optional[Literal["Era"]] = Field(alias="__typename", exclude=True)
    id: ID
    begin: Optional[datetime]
    name: str

    class Config:
        """A config class"""

        frozen = True


class ProtocolExperiment(BaseModel):
    typename: Optional[Literal["Experiment"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    description: Optional[str]

    class Config:
        """A config class"""

        frozen = True


class Protocol(BaseModel):
    typename: Optional[Literal["Protocol"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    experiment: ProtocolExperiment

    class Config:
        """A config class"""

        frozen = True


class SnapshotStore(HasPresignedDownloadAccessor, BaseModel):
    typename: Optional[Literal["MediaStore"]] = Field(alias="__typename", exclude=True)
    key: str
    presigned_url: str = Field(alias="presignedUrl")

    class Config:
        """A config class"""

        frozen = True


class Snapshot(BaseModel):
    typename: Optional[Literal["Snapshot"]] = Field(alias="__typename", exclude=True)
    id: ID
    store: SnapshotStore
    name: str

    class Config:
        """A config class"""

        frozen = True


class Ontology(OntologyTrait, BaseModel):
    typename: Optional[Literal["Ontology"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class ZarrStore(HasZarrStoreAccessor, BaseModel):
    typename: Optional[Literal["ZarrStore"]] = Field(alias="__typename", exclude=True)
    id: ID
    key: str
    "The key where the data is stored."
    bucket: str
    "The bucket where the data is stored."
    path: Optional[str]
    "The path to the data. Relative to the bucket."

    class Config:
        """A config class"""

        frozen = True


class ParquetStore(HasParquetStoreAccesor, BaseModel):
    typename: Optional[Literal["ParquetStore"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    key: str
    bucket: str
    path: str

    class Config:
        """A config class"""

        frozen = True


class BigFileStore(HasDownloadAccessor, BaseModel):
    typename: Optional[Literal["BigFileStore"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    key: str
    bucket: str
    path: str
    presigned_url: str = Field(alias="presignedUrl")

    class Config:
        """A config class"""

        frozen = True


class Channel(BaseModel):
    typename: Optional[Literal["Channel"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    excitation_wavelength: Optional[float] = Field(alias="excitationWavelength")

    class Config:
        """A config class"""

        frozen = True


class Experiment(BaseModel):
    typename: Optional[Literal["Experiment"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    description: Optional[str]

    class Config:
        """A config class"""

        frozen = True


class CreateCameraMutationCreatecamera(BaseModel):
    typename: Optional[Literal["Camera"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class CreateCameraMutation(BaseModel):
    create_camera: CreateCameraMutationCreatecamera = Field(alias="createCamera")

    class Arguments(BaseModel):
        serial_number: str = Field(alias="serialNumber")
        name: Optional[str] = Field(default=None)
        pixel_size_x: Optional[Micrometers] = Field(alias="pixelSizeX", default=None)
        pixel_size_y: Optional[Micrometers] = Field(alias="pixelSizeY", default=None)
        sensor_size_x: Optional[int] = Field(alias="sensorSizeX", default=None)
        sensor_size_y: Optional[int] = Field(alias="sensorSizeY", default=None)

    class Meta:
        document = "mutation CreateCamera($serialNumber: String!, $name: String, $pixelSizeX: Micrometers, $pixelSizeY: Micrometers, $sensorSizeX: Int, $sensorSizeY: Int) {\n  createCamera(\n    input: {name: $name, pixelSizeX: $pixelSizeX, serialNumber: $serialNumber, pixelSizeY: $pixelSizeY, sensorSizeX: $sensorSizeX, sensorSizeY: $sensorSizeY}\n  ) {\n    id\n    name\n  }\n}"


class EnsureCameraMutationEnsurecamera(BaseModel):
    typename: Optional[Literal["Camera"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class EnsureCameraMutation(BaseModel):
    ensure_camera: EnsureCameraMutationEnsurecamera = Field(alias="ensureCamera")

    class Arguments(BaseModel):
        serial_number: str = Field(alias="serialNumber")
        name: Optional[str] = Field(default=None)
        pixel_size_x: Optional[Micrometers] = Field(alias="pixelSizeX", default=None)
        pixel_size_y: Optional[Micrometers] = Field(alias="pixelSizeY", default=None)
        sensor_size_x: Optional[int] = Field(alias="sensorSizeX", default=None)
        sensor_size_y: Optional[int] = Field(alias="sensorSizeY", default=None)

    class Meta:
        document = "mutation EnsureCamera($serialNumber: String!, $name: String, $pixelSizeX: Micrometers, $pixelSizeY: Micrometers, $sensorSizeX: Int, $sensorSizeY: Int) {\n  ensureCamera(\n    input: {name: $name, pixelSizeX: $pixelSizeX, serialNumber: $serialNumber, pixelSizeY: $pixelSizeY, sensorSizeX: $sensorSizeX, sensorSizeY: $sensorSizeY}\n  ) {\n    id\n    name\n  }\n}"


class MapProtocolStepMutation(BaseModel):
    map_protocol_step: ProtocolStepMapping = Field(alias="mapProtocolStep")

    class Arguments(BaseModel):
        step: ID
        protocol: ID
        t: int

    class Meta:
        document = "fragment ProtocolStepMapping on ProtocolStepMapping {\n  id\n  t\n  protocol {\n    id\n    name\n    experiment {\n      id\n      name\n      description\n    }\n  }\n  step {\n    id\n    name\n  }\n}\n\nmutation MapProtocolStep($step: ID!, $protocol: ID!, $t: Int!) {\n  mapProtocolStep(input: {protocol: $protocol, t: $t, step: $step}) {\n    ...ProtocolStepMapping\n  }\n}"


class CreateRenderTreeMutationCreaterendertree(BaseModel):
    typename: Optional[Literal["RenderTree"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class CreateRenderTreeMutation(BaseModel):
    create_render_tree: CreateRenderTreeMutationCreaterendertree = Field(
        alias="createRenderTree"
    )

    class Arguments(BaseModel):
        name: str
        tree: TreeInput

    class Meta:
        document = "mutation CreateRenderTree($name: String!, $tree: TreeInput!) {\n  createRenderTree(input: {name: $name, tree: $tree}) {\n    id\n  }\n}"


class From_parquet_likeMutation(BaseModel):
    from_parquet_like: Table = Field(alias="fromParquetLike")

    class Arguments(BaseModel):
        dataframe: ParquetLike
        name: str
        origins: Optional[List[ID]] = Field(default=None)
        dataset: Optional[ID] = Field(default=None)

    class Meta:
        document = "fragment ParquetStore on ParquetStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment Table on Table {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...ParquetStore\n  }\n}\n\nmutation from_parquet_like($dataframe: ParquetLike!, $name: String!, $origins: [ID!], $dataset: ID) {\n  fromParquetLike(\n    input: {dataframe: $dataframe, name: $name, origins: $origins, dataset: $dataset}\n  ) {\n    ...Table\n  }\n}"


class RequestTableUploadMutation(BaseModel):
    request_table_upload: Credentials = Field(alias="requestTableUpload")

    class Arguments(BaseModel):
        key: str
        datalayer: str

    class Meta:
        document = "fragment Credentials on Credentials {\n  accessKey\n  status\n  secretKey\n  bucket\n  key\n  sessionToken\n  store\n}\n\nmutation RequestTableUpload($key: String!, $datalayer: String!) {\n  requestTableUpload(input: {key: $key, datalayer: $datalayer}) {\n    ...Credentials\n  }\n}"


class RequestTableAccessMutation(BaseModel):
    request_table_access: AccessCredentials = Field(alias="requestTableAccess")

    class Arguments(BaseModel):
        store: ID
        duration: Optional[int] = Field(default=None)

    class Meta:
        document = "fragment AccessCredentials on AccessCredentials {\n  accessKey\n  secretKey\n  bucket\n  key\n  sessionToken\n  path\n}\n\nmutation RequestTableAccess($store: ID!, $duration: Int) {\n  requestTableAccess(input: {store: $store, duration: $duration}) {\n    ...AccessCredentials\n  }\n}"


class CreateRenderedPlotMutation(BaseModel):
    create_rendered_plot: RenderedPlot = Field(alias="createRenderedPlot")

    class Arguments(BaseModel):
        plot: Upload
        name: str
        overlays: Optional[List[OverlayInput]] = Field(default=None)

    class Meta:
        document = "fragment RenderedPlot on RenderedPlot {\n  id\n  store {\n    id\n    key\n  }\n}\n\nmutation CreateRenderedPlot($plot: Upload!, $name: String!, $overlays: [OverlayInput!]) {\n  createRenderedPlot(input: {plot: $plot, overlays: $overlays, name: $name}) {\n    ...RenderedPlot\n  }\n}"


class From_file_likeMutation(BaseModel):
    from_file_like: File = Field(alias="fromFileLike")

    class Arguments(BaseModel):
        file: FileLike
        name: str
        origins: Optional[List[ID]] = Field(default=None)
        dataset: Optional[ID] = Field(default=None)

    class Meta:
        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n}\n\nfragment File on File {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...BigFileStore\n  }\n}\n\nmutation from_file_like($file: FileLike!, $name: String!, $origins: [ID!], $dataset: ID) {\n  fromFileLike(\n    input: {file: $file, name: $name, origins: $origins, dataset: $dataset}\n  ) {\n    ...File\n  }\n}"


class RequestFileUploadMutation(BaseModel):
    request_file_upload: Credentials = Field(alias="requestFileUpload")

    class Arguments(BaseModel):
        key: str
        datalayer: str

    class Meta:
        document = "fragment Credentials on Credentials {\n  accessKey\n  status\n  secretKey\n  bucket\n  key\n  sessionToken\n  store\n}\n\nmutation RequestFileUpload($key: String!, $datalayer: String!) {\n  requestFileUpload(input: {key: $key, datalayer: $datalayer}) {\n    ...Credentials\n  }\n}"


class RequestFileAccessMutation(BaseModel):
    request_file_access: AccessCredentials = Field(alias="requestFileAccess")

    class Arguments(BaseModel):
        store: ID
        duration: Optional[int] = Field(default=None)

    class Meta:
        document = "fragment AccessCredentials on AccessCredentials {\n  accessKey\n  secretKey\n  bucket\n  key\n  sessionToken\n  path\n}\n\nmutation RequestFileAccess($store: ID!, $duration: Int) {\n  requestFileAccess(input: {store: $store, duration: $duration}) {\n    ...AccessCredentials\n  }\n}"


class CreateEntityKindMutationCreateentitykind(EntityKindTrait, BaseModel):
    typename: Optional[Literal["EntityKind"]] = Field(alias="__typename", exclude=True)
    id: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class CreateEntityKindMutation(BaseModel):
    create_entity_kind: CreateEntityKindMutationCreateentitykind = Field(
        alias="createEntityKind"
    )

    class Arguments(BaseModel):
        label: str
        ontology: Optional[ID] = Field(default=None)
        purl: Optional[str] = Field(default=None)
        description: Optional[str] = Field(default=None)
        color: Optional[List[int]] = Field(default=None)

    class Meta:
        document = "mutation CreateEntityKind($label: String!, $ontology: ID, $purl: String, $description: String, $color: [Int!]) {\n  createEntityKind(\n    input: {label: $label, ontology: $ontology, description: $description, purl: $purl, color: $color}\n  ) {\n    id\n    label\n  }\n}"


class CreateStageMutation(BaseModel):
    create_stage: Stage = Field(alias="createStage")

    class Arguments(BaseModel):
        name: str

    class Meta:
        document = "fragment Stage on Stage {\n  id\n  name\n}\n\nmutation CreateStage($name: String!) {\n  createStage(input: {name: $name}) {\n    ...Stage\n  }\n}"


class CreateRoiMutation(BaseModel):
    create_roi: ROI = Field(alias="createRoi")

    class Arguments(BaseModel):
        image: ID
        vectors: List[FiveDVector]
        kind: RoiKind
        entity: Optional[ID] = Field(default=None)
        entity_kind: Optional[ID] = Field(alias="entityKind", default=None)
        entity_parent: Optional[ID] = Field(alias="entityParent", default=None)

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  image {\n    id\n  }\n  vectors\n  kind\n}\n\nmutation CreateRoi($image: ID!, $vectors: [FiveDVector!]!, $kind: RoiKind!, $entity: ID, $entityKind: ID, $entityParent: ID) {\n  createRoi(\n    input: {image: $image, vectors: $vectors, kind: $kind, entity: $entity, entityKind: $entityKind, entityParent: $entityParent}\n  ) {\n    ...ROI\n  }\n}"


class DeleteRoiMutation(BaseModel):
    delete_roi: ID = Field(alias="deleteRoi")

    class Arguments(BaseModel):
        roi: ID

    class Meta:
        document = "mutation DeleteRoi($roi: ID!) {\n  deleteRoi(input: {id: $roi})\n}"


class CreateObjectiveMutationCreateobjective(BaseModel):
    typename: Optional[Literal["Objective"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class CreateObjectiveMutation(BaseModel):
    create_objective: CreateObjectiveMutationCreateobjective = Field(
        alias="createObjective"
    )

    class Arguments(BaseModel):
        serial_number: str = Field(alias="serialNumber")
        name: Optional[str] = Field(default=None)
        na: Optional[float] = Field(default=None)
        magnification: Optional[float] = Field(default=None)

    class Meta:
        document = "mutation CreateObjective($serialNumber: String!, $name: String, $na: Float, $magnification: Float) {\n  createObjective(\n    input: {name: $name, na: $na, serialNumber: $serialNumber, magnification: $magnification}\n  ) {\n    id\n    name\n  }\n}"


class EnsureObjectiveMutationEnsureobjective(BaseModel):
    typename: Optional[Literal["Objective"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class EnsureObjectiveMutation(BaseModel):
    ensure_objective: EnsureObjectiveMutationEnsureobjective = Field(
        alias="ensureObjective"
    )

    class Arguments(BaseModel):
        serial_number: str = Field(alias="serialNumber")
        name: Optional[str] = Field(default=None)
        na: Optional[float] = Field(default=None)
        magnification: Optional[float] = Field(default=None)

    class Meta:
        document = "mutation EnsureObjective($serialNumber: String!, $name: String, $na: Float, $magnification: Float) {\n  ensureObjective(\n    input: {name: $name, na: $na, serialNumber: $serialNumber, magnification: $magnification}\n  ) {\n    id\n    name\n  }\n}"


class CreateRelationMetricMutation(BaseModel):
    create_relation_metric: RelationMetric = Field(alias="createRelationMetric")

    class Arguments(BaseModel):
        kind: ID
        data_kind: MetricDataType = Field(alias="dataKind")

    class Meta:
        document = "fragment EntityKind on EntityKind {\n  id\n  label\n  ontology {\n    id\n    name\n  }\n}\n\nfragment RelationMetric on RelationMetric {\n  id\n  kind {\n    ...EntityKind\n  }\n  dataKind\n}\n\nmutation CreateRelationMetric($kind: ID!, $dataKind: MetricDataType!) {\n  createRelationMetric(input: {kind: $kind, dataKind: $dataKind}) {\n    ...RelationMetric\n  }\n}"


class AttachRelationMetricToRelationMutation(BaseModel):
    attach_relation_metric: EntityRelation = Field(alias="attachRelationMetric")

    class Arguments(BaseModel):
        relation: ID
        metric: ID
        value: Any

    class Meta:
        document = "fragment EntityRelation on EntityRelation {\n  id\n  left {\n    id\n  }\n  right {\n    id\n  }\n  kind {\n    id\n  }\n}\n\nmutation AttachRelationMetricToRelation($relation: ID!, $metric: ID!, $value: Metric!) {\n  attachRelationMetric(\n    input: {relation: $relation, metric: $metric, value: $value}\n  ) {\n    ...EntityRelation\n  }\n}"


class CreateProtocolStepMutation(BaseModel):
    create_protocol_step: ProtocolStep = Field(alias="createProtocolStep")

    class Arguments(BaseModel):
        name: str
        kind: ID
        reagents: Optional[List[ID]] = Field(default=None)
        description: Optional[str] = Field(default=None)

    class Meta:
        document = "fragment ProtocolStep on ProtocolStep {\n  id\n  mappings {\n    id\n    protocol {\n      id\n      name\n    }\n  }\n  description\n  reagents {\n    id\n    name\n  }\n  views {\n    id\n    specimen {\n      id\n    }\n    image {\n      id\n    }\n  }\n}\n\nmutation CreateProtocolStep($name: String!, $kind: ID!, $reagents: [ID!], $description: String) {\n  createProtocolStep(\n    input: {reagents: $reagents, description: $description, kind: $kind, name: $name}\n  ) {\n    ...ProtocolStep\n  }\n}"


class CreateDatasetMutationCreatedataset(BaseModel):
    typename: Optional[Literal["Dataset"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class CreateDatasetMutation(BaseModel):
    create_dataset: CreateDatasetMutationCreatedataset = Field(alias="createDataset")

    class Arguments(BaseModel):
        name: str

    class Meta:
        document = "mutation CreateDataset($name: String!) {\n  createDataset(input: {name: $name}) {\n    id\n    name\n  }\n}"


class UpdateDatasetMutationUpdatedataset(BaseModel):
    typename: Optional[Literal["Dataset"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class UpdateDatasetMutation(BaseModel):
    update_dataset: UpdateDatasetMutationUpdatedataset = Field(alias="updateDataset")

    class Arguments(BaseModel):
        id: ID
        name: str

    class Meta:
        document = "mutation UpdateDataset($id: ID!, $name: String!) {\n  updateDataset(input: {id: $id, name: $name}) {\n    id\n    name\n  }\n}"


class RevertDatasetMutationRevertdataset(BaseModel):
    typename: Optional[Literal["Dataset"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str
    description: Optional[str]

    class Config:
        """A config class"""

        frozen = True


class RevertDatasetMutation(BaseModel):
    revert_dataset: RevertDatasetMutationRevertdataset = Field(alias="revertDataset")

    class Arguments(BaseModel):
        dataset: ID
        history: ID

    class Meta:
        document = "mutation RevertDataset($dataset: ID!, $history: ID!) {\n  revertDataset(input: {id: $dataset, historyId: $history}) {\n    id\n    name\n    description\n  }\n}"


class CreateEntityGroupMutationCreateentitygroup(EntityTrait, BaseModel):
    typename: Optional[Literal["Entity"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class CreateEntityGroupMutation(BaseModel):
    create_entity_group: CreateEntityGroupMutationCreateentitygroup = Field(
        alias="createEntityGroup"
    )

    class Arguments(BaseModel):
        name: str
        image: Optional[ID] = Field(default=None)

    class Meta:
        document = "mutation CreateEntityGroup($name: String!, $image: ID) {\n  createEntityGroup(input: {name: $name, image: $image}) {\n    id\n    name\n  }\n}"


class CreateSpecimenMutation(BaseModel):
    create_specimen: Specimen = Field(alias="createSpecimen")

    class Arguments(BaseModel):
        entity: ID
        protocol: ID

    class Meta:
        document = "fragment Specimen on Specimen {\n  id\n  entity {\n    id\n    kind {\n      id\n      label\n    }\n    name\n    group {\n      id\n    }\n  }\n  protocol {\n    id\n  }\n}\n\nmutation CreateSpecimen($entity: ID!, $protocol: ID!) {\n  createSpecimen(input: {entity: $entity, protocol: $protocol}) {\n    ...Specimen\n  }\n}"


class CreateInstrumentMutationCreateinstrument(BaseModel):
    typename: Optional[Literal["Instrument"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class CreateInstrumentMutation(BaseModel):
    create_instrument: CreateInstrumentMutationCreateinstrument = Field(
        alias="createInstrument"
    )

    class Arguments(BaseModel):
        serial_number: str = Field(alias="serialNumber")
        name: Optional[str] = Field(default=None)
        model: Optional[str] = Field(default=None)

    class Meta:
        document = "mutation CreateInstrument($serialNumber: String!, $name: String, $model: String) {\n  createInstrument(\n    input: {name: $name, model: $model, serialNumber: $serialNumber}\n  ) {\n    id\n    name\n  }\n}"


class EnsureInstrumentMutationEnsureinstrument(BaseModel):
    typename: Optional[Literal["Instrument"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class EnsureInstrumentMutation(BaseModel):
    ensure_instrument: EnsureInstrumentMutationEnsureinstrument = Field(
        alias="ensureInstrument"
    )

    class Arguments(BaseModel):
        serial_number: str = Field(alias="serialNumber")
        name: Optional[str] = Field(default=None)
        model: Optional[str] = Field(default=None)

    class Meta:
        document = "mutation EnsureInstrument($serialNumber: String!, $name: String, $model: String) {\n  ensureInstrument(\n    input: {name: $name, model: $model, serialNumber: $serialNumber}\n  ) {\n    id\n    name\n  }\n}"


class CreateEntityRelationMutation(BaseModel):
    create_entity_relation: EntityRelation = Field(alias="createEntityRelation")

    class Arguments(BaseModel):
        left: ID
        right: ID
        kind: ID

    class Meta:
        document = "fragment EntityRelation on EntityRelation {\n  id\n  left {\n    id\n  }\n  right {\n    id\n  }\n  kind {\n    id\n  }\n}\n\nmutation CreateEntityRelation($left: ID!, $right: ID!, $kind: ID!) {\n  createEntityRelation(input: {left: $left, right: $right, kind: $kind}) {\n    ...EntityRelation\n  }\n}"


class CreateEntityRelationKindMutation(BaseModel):
    create_entity_relation_kind: EntityRelationKind = Field(
        alias="createEntityRelationKind"
    )

    class Arguments(BaseModel):
        left_kind: ID = Field(alias="leftKind")
        right_kind: ID = Field(alias="rightKind")
        kind: ID

    class Meta:
        document = "fragment EntityRelationKind on EntityRelationKind {\n  id\n  leftKind {\n    id\n  }\n  rightKind {\n    id\n  }\n  kind {\n    id\n  }\n}\n\nmutation CreateEntityRelationKind($leftKind: ID!, $rightKind: ID!, $kind: ID!) {\n  createEntityRelationKind(\n    input: {leftKind: $leftKind, rightKind: $rightKind, kind: $kind}\n  ) {\n    ...EntityRelationKind\n  }\n}"


class CreateEntityMetricMutation(BaseModel):
    create_entity_metric: EntityMetric = Field(alias="createEntityMetric")

    class Arguments(BaseModel):
        kind: ID
        data_kind: MetricDataType = Field(alias="dataKind")

    class Meta:
        document = "fragment EntityKind on EntityKind {\n  id\n  label\n  ontology {\n    id\n    name\n  }\n}\n\nfragment EntityMetric on EntityMetric {\n  id\n  kind {\n    ...EntityKind\n  }\n  dataKind\n}\n\nmutation CreateEntityMetric($kind: ID!, $dataKind: MetricDataType!) {\n  createEntityMetric(input: {kind: $kind, dataKind: $dataKind}) {\n    ...EntityMetric\n  }\n}"


class AttachEntityMetricToEntityMutation(BaseModel):
    attach_entity_metric: Entity = Field(alias="attachEntityMetric")

    class Arguments(BaseModel):
        entity: ID
        metric: ID
        value: Any

    class Meta:
        document = "fragment Entity on Entity {\n  id\n  name\n  kind {\n    id\n    label\n    ontology {\n      id\n      name\n    }\n  }\n  group {\n    id\n    name\n  }\n}\n\nmutation AttachEntityMetricToEntity($entity: ID!, $metric: ID!, $value: Metric!) {\n  attachEntityMetric(input: {entity: $entity, metric: $metric, value: $value}) {\n    ...Entity\n  }\n}"


class AttachMetricToEntitiesMutation(BaseModel):
    attach_metrics_to_entities: Tuple[Entity, ...] = Field(
        alias="attachMetricsToEntities"
    )

    class Arguments(BaseModel):
        metric: ID
        pairs: List[EntityValuePairInput]

    class Meta:
        document = "fragment Entity on Entity {\n  id\n  name\n  kind {\n    id\n    label\n    ontology {\n      id\n      name\n    }\n  }\n  group {\n    id\n    name\n  }\n}\n\nmutation AttachMetricToEntities($metric: ID!, $pairs: [EntityValuePairInput!]!) {\n  attachMetricsToEntities(input: {metric: $metric, pairs: $pairs}) {\n    ...Entity\n  }\n}"


class From_array_likeMutation(BaseModel):
    from_array_like: Image = Field(alias="fromArrayLike")

    class Arguments(BaseModel):
        array: ArrayLike
        name: str
        origins: Optional[List[ID]] = Field(default=None)
        channel_views: Optional[List[PartialChannelViewInput]] = Field(
            alias="channelViews", default=None
        )
        transformation_views: Optional[List[PartialAffineTransformationViewInput]] = (
            Field(alias="transformationViews", default=None)
        )
        pixel_views: Optional[List[PartialPixelViewInput]] = Field(
            alias="pixelViews", default=None
        )
        rgb_views: Optional[List[PartialRGBViewInput]] = Field(
            alias="rgbViews", default=None
        )
        acquisition_views: Optional[List[PartialAcquisitionViewInput]] = Field(
            alias="acquisitionViews", default=None
        )
        timepoint_views: Optional[List[PartialTimepointViewInput]] = Field(
            alias="timepointViews", default=None
        )
        optics_views: Optional[List[PartialOpticsViewInput]] = Field(
            alias="opticsViews", default=None
        )
        specimen_views: Optional[List[PartialSpecimenViewInput]] = Field(
            alias="specimenViews", default=None
        )
        scale_views: Optional[List[PartialScaleViewInput]] = Field(
            alias="scaleViews", default=None
        )
        tags: Optional[List[str]] = Field(default=None)
        file_origins: Optional[List[ID]] = Field(alias="fileOrigins", default=None)
        roi_origins: Optional[List[ID]] = Field(alias="roiOrigins", default=None)

    class Meta:
        document = "fragment Era on Era {\n  id\n  begin\n  name\n}\n\nfragment Channel on Channel {\n  id\n  name\n  excitationWavelength\n}\n\nfragment View on View {\n  zMin\n  zMax\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment TimepointView on TimepointView {\n  ...View\n  id\n  msSinceStart\n  indexSinceStart\n  era {\n    ...Era\n  }\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  cMin\n  cMax\n  fullColour\n  baseColor\n}\n\nfragment AffineTransformationView on AffineTransformationView {\n  ...View\n  id\n  affineMatrix\n  stage {\n    id\n  }\n}\n\nfragment OpticsView on OpticsView {\n  ...View\n  objective {\n    id\n    name\n    serialNumber\n  }\n  camera {\n    id\n    name\n    serialNumber\n  }\n  instrument {\n    id\n    name\n    serialNumber\n  }\n}\n\nfragment LabelView on LabelView {\n  ...View\n  id\n  fluorophore {\n    id\n    kind {\n      id\n      label\n    }\n    name\n  }\n  primaryAntibody {\n    id\n    kind {\n      id\n      label\n    }\n    name\n  }\n  secondaryAntibody {\n    id\n    kind {\n      id\n      label\n    }\n    name\n  }\n}\n\nfragment ScaleView on ScaleView {\n  ...View\n  id\n  scaleX\n  scaleY\n  scaleZ\n  scaleT\n  scaleC\n}\n\nfragment ChannelView on ChannelView {\n  ...View\n  id\n  channel {\n    ...Channel\n  }\n}\n\nfragment Image on Image {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...ZarrStore\n  }\n  views {\n    ...ChannelView\n    ...AffineTransformationView\n    ...LabelView\n    ...TimepointView\n    ...OpticsView\n    ...ScaleView\n  }\n  derivedScaleViews {\n    ...ScaleView\n    image {\n      name\n      store {\n        ...ZarrStore\n      }\n    }\n  }\n  rgbContexts {\n    id\n    name\n    views {\n      ...RGBView\n    }\n  }\n}\n\nmutation from_array_like($array: ArrayLike!, $name: String!, $origins: [ID!], $channelViews: [PartialChannelViewInput!], $transformationViews: [PartialAffineTransformationViewInput!], $pixelViews: [PartialPixelViewInput!], $rgbViews: [PartialRGBViewInput!], $acquisitionViews: [PartialAcquisitionViewInput!], $timepointViews: [PartialTimepointViewInput!], $opticsViews: [PartialOpticsViewInput!], $specimenViews: [PartialSpecimenViewInput!], $scaleViews: [PartialScaleViewInput!], $tags: [String!], $fileOrigins: [ID!], $roiOrigins: [ID!]) {\n  fromArrayLike(\n    input: {array: $array, name: $name, origins: $origins, channelViews: $channelViews, transformationViews: $transformationViews, acquisitionViews: $acquisitionViews, pixelViews: $pixelViews, timepointViews: $timepointViews, opticsViews: $opticsViews, rgbViews: $rgbViews, scaleViews: $scaleViews, tags: $tags, fileOrigins: $fileOrigins, roiOrigins: $roiOrigins, specimenViews: $specimenViews}\n  ) {\n    ...Image\n  }\n}"


class RequestUploadMutation(BaseModel):
    request_upload: Credentials = Field(alias="requestUpload")

    class Arguments(BaseModel):
        key: str
        datalayer: str

    class Meta:
        document = "fragment Credentials on Credentials {\n  accessKey\n  status\n  secretKey\n  bucket\n  key\n  sessionToken\n  store\n}\n\nmutation RequestUpload($key: String!, $datalayer: String!) {\n  requestUpload(input: {key: $key, datalayer: $datalayer}) {\n    ...Credentials\n  }\n}"


class RequestAccessMutation(BaseModel):
    request_access: AccessCredentials = Field(alias="requestAccess")
    "Request upload credentials for a given key"

    class Arguments(BaseModel):
        store: ID
        duration: Optional[int] = Field(default=None)

    class Meta:
        document = "fragment AccessCredentials on AccessCredentials {\n  accessKey\n  secretKey\n  bucket\n  key\n  sessionToken\n  path\n}\n\nmutation RequestAccess($store: ID!, $duration: Int) {\n  requestAccess(input: {store: $store, duration: $duration}) {\n    ...AccessCredentials\n  }\n}"


class CreateEntityMutation(BaseModel):
    create_entity: Entity = Field(alias="createEntity")

    class Arguments(BaseModel):
        kind: ID
        group: Optional[ID] = Field(default=None)
        name: Optional[str] = Field(default=None)
        parent: Optional[ID] = Field(default=None)
        instance_kind: Optional[str] = Field(default=None)

    class Meta:
        document = "fragment Entity on Entity {\n  id\n  name\n  kind {\n    id\n    label\n    ontology {\n      id\n      name\n    }\n  }\n  group {\n    id\n    name\n  }\n}\n\nmutation CreateEntity($kind: ID!, $group: ID, $name: String, $parent: ID, $instance_kind: String) {\n  createEntity(\n    input: {group: $group, kind: $kind, name: $name, parent: $parent, instanceKind: $instance_kind}\n  ) {\n    ...Entity\n  }\n}"


class CreateEraMutationCreateera(BaseModel):
    typename: Optional[Literal["Era"]] = Field(alias="__typename", exclude=True)
    id: ID
    begin: Optional[datetime]

    class Config:
        """A config class"""

        frozen = True


class CreateEraMutation(BaseModel):
    create_era: CreateEraMutationCreateera = Field(alias="createEra")

    class Arguments(BaseModel):
        name: str
        begin: Optional[datetime] = Field(default=None)

    class Meta:
        document = "mutation CreateEra($name: String!, $begin: DateTime) {\n  createEra(input: {name: $name, begin: $begin}) {\n    id\n    begin\n  }\n}"


class CreateProtocolMutation(BaseModel):
    create_protocol: Protocol = Field(alias="createProtocol")

    class Arguments(BaseModel):
        name: str
        experiment: ID
        description: Optional[str] = Field(default=None)

    class Meta:
        document = "fragment Protocol on Protocol {\n  id\n  name\n  experiment {\n    id\n    name\n    description\n  }\n}\n\nmutation CreateProtocol($name: String!, $experiment: ID!, $description: String) {\n  createProtocol(\n    input: {name: $name, experiment: $experiment, description: $description}\n  ) {\n    ...Protocol\n  }\n}"


class CreateSnapshotMutation(BaseModel):
    create_snapshot: Snapshot = Field(alias="createSnapshot")

    class Arguments(BaseModel):
        image: ID
        file: Upload

    class Meta:
        document = "fragment Snapshot on Snapshot {\n  id\n  store {\n    key\n    presignedUrl\n  }\n  name\n}\n\nmutation CreateSnapshot($image: ID!, $file: Upload!) {\n  createSnapshot(input: {file: $file, image: $image}) {\n    ...Snapshot\n  }\n}"


class CreateRgbViewMutationCreatergbview(BaseModel):
    typename: Optional[Literal["RGBView"]] = Field(alias="__typename", exclude=True)
    id: ID

    class Config:
        """A config class"""

        frozen = True


class CreateRgbViewMutation(BaseModel):
    create_rgb_view: CreateRgbViewMutationCreatergbview = Field(alias="createRgbView")

    class Arguments(BaseModel):
        image: ID
        context: ID
        gamma: Optional[float] = Field(default=None)
        contrast_limit_max: Optional[float] = Field(
            alias="contrastLimitMax", default=None
        )
        contrast_limit_min: Optional[float] = Field(
            alias="contrastLimitMin", default=None
        )
        rescale: Optional[bool] = Field(default=None)
        active: Optional[bool] = Field(default=None)
        color_map: Optional[ColorMap] = Field(alias="colorMap", default=None)
        base_color: Optional[List[float]] = Field(alias="baseColor", default=None)

    class Meta:
        document = "mutation CreateRgbView($image: ID!, $context: ID!, $gamma: Float, $contrastLimitMax: Float, $contrastLimitMin: Float, $rescale: Boolean, $active: Boolean, $colorMap: ColorMap, $baseColor: [Float!]) {\n  createRgbView(\n    input: {image: $image, context: $context, gamma: $gamma, contrastLimitMax: $contrastLimitMax, contrastLimitMin: $contrastLimitMin, rescale: $rescale, active: $active, colorMap: $colorMap, baseColor: $baseColor}\n  ) {\n    id\n  }\n}"


class CreateOntologyMutation(BaseModel):
    create_ontology: Ontology = Field(alias="createOntology")

    class Arguments(BaseModel):
        name: str
        purl: Optional[str] = Field(default=None)
        description: Optional[str] = Field(default=None)

    class Meta:
        document = "fragment Ontology on Ontology {\n  id\n  name\n}\n\nmutation CreateOntology($name: String!, $purl: String, $description: String) {\n  createOntology(input: {name: $name, purl: $purl, description: $description}) {\n    ...Ontology\n  }\n}"


class CreateRGBContextMutation(BaseModel):
    create_rgb_context: RGBContext = Field(alias="createRgbContext")

    class Arguments(BaseModel):
        input: CreateRGBContextInput

    class Meta:
        document = "fragment View on View {\n  zMin\n  zMax\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  cMin\n  cMax\n  fullColour\n  baseColor\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment RGBContext on RGBContext {\n  id\n  views {\n    ...RGBView\n  }\n  image {\n    id\n    store {\n      ...ZarrStore\n    }\n  }\n  pinned\n  name\n  z\n  t\n  c\n  blending\n}\n\nmutation CreateRGBContext($input: CreateRGBContextInput!) {\n  createRgbContext(input: $input) {\n    ...RGBContext\n  }\n}"


class UpdateRGBContextMutation(BaseModel):
    update_rgb_context: RGBContext = Field(alias="updateRgbContext")
    "Update RGB Context"

    class Arguments(BaseModel):
        input: UpdateRGBContextInput

    class Meta:
        document = "fragment View on View {\n  zMin\n  zMax\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  cMin\n  cMax\n  fullColour\n  baseColor\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment RGBContext on RGBContext {\n  id\n  views {\n    ...RGBView\n  }\n  image {\n    id\n    store {\n      ...ZarrStore\n    }\n  }\n  pinned\n  name\n  z\n  t\n  c\n  blending\n}\n\nmutation UpdateRGBContext($input: UpdateRGBContextInput!) {\n  updateRgbContext(input: $input) {\n    ...RGBContext\n  }\n}"


class CreateViewCollectionMutationCreateviewcollection(BaseModel):
    typename: Optional[Literal["ViewCollection"]] = Field(
        alias="__typename", exclude=True
    )
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class CreateViewCollectionMutation(BaseModel):
    create_view_collection: CreateViewCollectionMutationCreateviewcollection = Field(
        alias="createViewCollection"
    )

    class Arguments(BaseModel):
        name: str

    class Meta:
        document = "mutation CreateViewCollection($name: String!) {\n  createViewCollection(input: {name: $name}) {\n    id\n    name\n  }\n}"


class CreateChannelMutationCreatechannel(BaseModel):
    typename: Optional[Literal["Channel"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class CreateChannelMutation(BaseModel):
    create_channel: CreateChannelMutationCreatechannel = Field(alias="createChannel")

    class Arguments(BaseModel):
        name: str

    class Meta:
        document = "mutation CreateChannel($name: String!) {\n  createChannel(input: {name: $name}) {\n    id\n    name\n  }\n}"


class EnsureChannelMutationEnsurechannel(BaseModel):
    typename: Optional[Literal["Channel"]] = Field(alias="__typename", exclude=True)
    id: ID
    name: str

    class Config:
        """A config class"""

        frozen = True


class EnsureChannelMutation(BaseModel):
    ensure_channel: EnsureChannelMutationEnsurechannel = Field(alias="ensureChannel")

    class Arguments(BaseModel):
        name: str

    class Meta:
        document = "mutation EnsureChannel($name: String!) {\n  ensureChannel(input: {name: $name}) {\n    id\n    name\n  }\n}"


class CreateExperimentMutation(BaseModel):
    create_experiment: Experiment = Field(alias="createExperiment")

    class Arguments(BaseModel):
        name: str
        description: Optional[str] = Field(default=None)

    class Meta:
        document = "fragment Experiment on Experiment {\n  id\n  name\n  description\n}\n\nmutation CreateExperiment($name: String!, $description: String) {\n  createExperiment(input: {name: $name, description: $description}) {\n    ...Experiment\n  }\n}"


class GetCameraQuery(BaseModel):
    camera: Camera

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Camera on Camera {\n  sensorSizeX\n  sensorSizeY\n  pixelSizeX\n  pixelSizeY\n  name\n  serialNumber\n}\n\nquery GetCamera($id: ID!) {\n  camera(id: $id) {\n    ...Camera\n  }\n}"


class GetTableQuery(BaseModel):
    table: Table

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment ParquetStore on ParquetStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment Table on Table {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...ParquetStore\n  }\n}\n\nquery GetTable($id: ID!) {\n  table(id: $id) {\n    ...Table\n  }\n}"


class GetRenderedPlotQuery(BaseModel):
    rendered_plot: RenderedPlot = Field(alias="renderedPlot")

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment RenderedPlot on RenderedPlot {\n  id\n  store {\n    id\n    key\n  }\n}\n\nquery GetRenderedPlot($id: ID!) {\n  renderedPlot(id: $id) {\n    ...RenderedPlot\n  }\n}"


class ListRenderedPlotsQuery(BaseModel):
    rendered_plots: Tuple[ListRenderedPlot, ...] = Field(alias="renderedPlots")

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "fragment ListRenderedPlot on RenderedPlot {\n  id\n  store {\n    id\n    key\n  }\n}\n\nquery ListRenderedPlots {\n  renderedPlots {\n    ...ListRenderedPlot\n  }\n}"


class SearchRenderedPlotsQueryOptions(BaseModel):
    typename: Optional[Literal["RenderedPlot"]] = Field(
        alias="__typename", exclude=True
    )
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchRenderedPlotsQuery(BaseModel):
    options: Tuple[SearchRenderedPlotsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchRenderedPlots($search: String, $values: [ID!]) {\n  options: renderedPlots(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n  }\n}"


class GetFileQuery(BaseModel):
    file: File

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n}\n\nfragment File on File {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...BigFileStore\n  }\n}\n\nquery GetFile($id: ID!) {\n  file(id: $id) {\n    ...File\n  }\n}"


class SearchFilesQueryOptions(BaseModel):
    typename: Optional[Literal["File"]] = Field(alias="__typename", exclude=True)
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchFilesQuery(BaseModel):
    options: Tuple[SearchFilesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        document = "query SearchFiles($search: String, $values: [ID!], $pagination: OffsetPaginationInput) {\n  options: files(\n    filters: {search: $search, ids: $values}\n    pagination: $pagination\n  ) {\n    value: id\n    label: name\n  }\n}"


class GetEntityKindQuery(BaseModel):
    entity_kind: EntityKind = Field(alias="entityKind")

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment EntityKind on EntityKind {\n  id\n  label\n  ontology {\n    id\n    name\n  }\n}\n\nquery GetEntityKind($id: ID!) {\n  entityKind(id: $id) {\n    ...EntityKind\n  }\n}"


class SearchEntityKindQueryOptions(EntityKindTrait, BaseModel):
    typename: Optional[Literal["EntityKind"]] = Field(alias="__typename", exclude=True)
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchEntityKindQuery(BaseModel):
    options: Tuple[SearchEntityKindQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchEntityKind($search: String, $values: [ID!]) {\n  options: entityKinds(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n  }\n}"


class GetStageQuery(BaseModel):
    stage: Stage

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Stage on Stage {\n  id\n  name\n}\n\nquery GetStage($id: ID!) {\n  stage(id: $id) {\n    ...Stage\n  }\n}"


class SearchStagesQueryOptions(BaseModel):
    typename: Optional[Literal["Stage"]] = Field(alias="__typename", exclude=True)
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchStagesQuery(BaseModel):
    options: Tuple[SearchStagesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        document = "query SearchStages($search: String, $values: [ID!], $pagination: OffsetPaginationInput) {\n  options: stages(\n    filters: {search: $search, ids: $values}\n    pagination: $pagination\n  ) {\n    value: id\n    label: name\n  }\n}"


class GetRoisQuery(BaseModel):
    rois: Tuple[ROI, ...]

    class Arguments(BaseModel):
        image: ID

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  image {\n    id\n  }\n  vectors\n  kind\n}\n\nquery GetRois($image: ID!) {\n  rois(filters: {image: $image}) {\n    ...ROI\n  }\n}"


class GetRoiQuery(BaseModel):
    roi: ROI

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  image {\n    id\n  }\n  vectors\n  kind\n}\n\nquery GetRoi($id: ID!) {\n  roi(id: $id) {\n    ...ROI\n  }\n}"


class GetObjectiveQuery(BaseModel):
    objective: Objective

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Objective on Objective {\n  id\n  na\n  name\n  serialNumber\n}\n\nquery GetObjective($id: ID!) {\n  objective(id: $id) {\n    ...Objective\n  }\n}"


class GetProtocolStepQuery(BaseModel):
    protocol_step: ProtocolStep = Field(alias="protocolStep")

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment ProtocolStep on ProtocolStep {\n  id\n  mappings {\n    id\n    protocol {\n      id\n      name\n    }\n  }\n  description\n  reagents {\n    id\n    name\n  }\n  views {\n    id\n    specimen {\n      id\n    }\n    image {\n      id\n    }\n  }\n}\n\nquery GetProtocolStep($id: ID!) {\n  protocolStep(id: $id) {\n    ...ProtocolStep\n  }\n}"


class SearchProtocolStepsQueryOptions(BaseModel):
    typename: Optional[Literal["ProtocolStep"]] = Field(
        alias="__typename", exclude=True
    )
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchProtocolStepsQuery(BaseModel):
    options: Tuple[SearchProtocolStepsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchProtocolSteps($search: String, $values: [ID!]) {\n  options: protocolSteps(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n  }\n}"


class GetDatasetQuery(BaseModel):
    dataset: Dataset

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment HistoryStuff on History {\n  id\n  app {\n    id\n  }\n}\n\nfragment Dataset on Dataset {\n  name\n  description\n  history {\n    ...HistoryStuff\n  }\n}\n\nquery GetDataset($id: ID!) {\n  dataset(id: $id) {\n    ...Dataset\n  }\n}"


class GetSpecimenQuery(BaseModel):
    specimen: Specimen

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Specimen on Specimen {\n  id\n  entity {\n    id\n    kind {\n      id\n      label\n    }\n    name\n    group {\n      id\n    }\n  }\n  protocol {\n    id\n  }\n}\n\nquery GetSpecimen($id: ID!) {\n  specimen(id: $id) {\n    ...Specimen\n  }\n}"


class SearchSpecimensQueryOptions(BaseModel):
    typename: Optional[Literal["Specimen"]] = Field(alias="__typename", exclude=True)
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchSpecimensQuery(BaseModel):
    options: Tuple[SearchSpecimensQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchSpecimens($search: String, $values: [ID!]) {\n  options: specimens(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n  }\n}"


class GetInstrumentQuery(BaseModel):
    instrument: Instrument

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Instrument on Instrument {\n  id\n  model\n  name\n  serialNumber\n}\n\nquery GetInstrument($id: ID!) {\n  instrument(id: $id) {\n    ...Instrument\n  }\n}"


class GetEntityRelationQuery(BaseModel):
    entity_relation: EntityRelation = Field(alias="entityRelation")

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment EntityRelation on EntityRelation {\n  id\n  left {\n    id\n  }\n  right {\n    id\n  }\n  kind {\n    id\n  }\n}\n\nquery GetEntityRelation($id: ID!) {\n  entityRelation(id: $id) {\n    ...EntityRelation\n  }\n}"


class SearchEntityRelationsQueryOptions(BaseModel):
    typename: Optional[Literal["EntityRelation"]] = Field(
        alias="__typename", exclude=True
    )
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchEntityRelationsQuery(BaseModel):
    options: Tuple[SearchEntityRelationsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchEntityRelations($search: String, $values: [ID!]) {\n  options: entityRelations(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n  }\n}"


class GetImageQuery(BaseModel):
    image: Image

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Era on Era {\n  id\n  begin\n  name\n}\n\nfragment Channel on Channel {\n  id\n  name\n  excitationWavelength\n}\n\nfragment View on View {\n  zMin\n  zMax\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment TimepointView on TimepointView {\n  ...View\n  id\n  msSinceStart\n  indexSinceStart\n  era {\n    ...Era\n  }\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  cMin\n  cMax\n  fullColour\n  baseColor\n}\n\nfragment AffineTransformationView on AffineTransformationView {\n  ...View\n  id\n  affineMatrix\n  stage {\n    id\n  }\n}\n\nfragment OpticsView on OpticsView {\n  ...View\n  objective {\n    id\n    name\n    serialNumber\n  }\n  camera {\n    id\n    name\n    serialNumber\n  }\n  instrument {\n    id\n    name\n    serialNumber\n  }\n}\n\nfragment LabelView on LabelView {\n  ...View\n  id\n  fluorophore {\n    id\n    kind {\n      id\n      label\n    }\n    name\n  }\n  primaryAntibody {\n    id\n    kind {\n      id\n      label\n    }\n    name\n  }\n  secondaryAntibody {\n    id\n    kind {\n      id\n      label\n    }\n    name\n  }\n}\n\nfragment ScaleView on ScaleView {\n  ...View\n  id\n  scaleX\n  scaleY\n  scaleZ\n  scaleT\n  scaleC\n}\n\nfragment ChannelView on ChannelView {\n  ...View\n  id\n  channel {\n    ...Channel\n  }\n}\n\nfragment Image on Image {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...ZarrStore\n  }\n  views {\n    ...ChannelView\n    ...AffineTransformationView\n    ...LabelView\n    ...TimepointView\n    ...OpticsView\n    ...ScaleView\n  }\n  derivedScaleViews {\n    ...ScaleView\n    image {\n      name\n      store {\n        ...ZarrStore\n      }\n    }\n  }\n  rgbContexts {\n    id\n    name\n    views {\n      ...RGBView\n    }\n  }\n}\n\nquery GetImage($id: ID!) {\n  image(id: $id) {\n    ...Image\n  }\n}"


class GetRandomImageQuery(BaseModel):
    random_image: Image = Field(alias="randomImage")

    class Arguments(BaseModel):
        pass

    class Meta:
        document = "fragment Era on Era {\n  id\n  begin\n  name\n}\n\nfragment Channel on Channel {\n  id\n  name\n  excitationWavelength\n}\n\nfragment View on View {\n  zMin\n  zMax\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment TimepointView on TimepointView {\n  ...View\n  id\n  msSinceStart\n  indexSinceStart\n  era {\n    ...Era\n  }\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  cMin\n  cMax\n  fullColour\n  baseColor\n}\n\nfragment AffineTransformationView on AffineTransformationView {\n  ...View\n  id\n  affineMatrix\n  stage {\n    id\n  }\n}\n\nfragment OpticsView on OpticsView {\n  ...View\n  objective {\n    id\n    name\n    serialNumber\n  }\n  camera {\n    id\n    name\n    serialNumber\n  }\n  instrument {\n    id\n    name\n    serialNumber\n  }\n}\n\nfragment LabelView on LabelView {\n  ...View\n  id\n  fluorophore {\n    id\n    kind {\n      id\n      label\n    }\n    name\n  }\n  primaryAntibody {\n    id\n    kind {\n      id\n      label\n    }\n    name\n  }\n  secondaryAntibody {\n    id\n    kind {\n      id\n      label\n    }\n    name\n  }\n}\n\nfragment ScaleView on ScaleView {\n  ...View\n  id\n  scaleX\n  scaleY\n  scaleZ\n  scaleT\n  scaleC\n}\n\nfragment ChannelView on ChannelView {\n  ...View\n  id\n  channel {\n    ...Channel\n  }\n}\n\nfragment Image on Image {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...ZarrStore\n  }\n  views {\n    ...ChannelView\n    ...AffineTransformationView\n    ...LabelView\n    ...TimepointView\n    ...OpticsView\n    ...ScaleView\n  }\n  derivedScaleViews {\n    ...ScaleView\n    image {\n      name\n      store {\n        ...ZarrStore\n      }\n    }\n  }\n  rgbContexts {\n    id\n    name\n    views {\n      ...RGBView\n    }\n  }\n}\n\nquery GetRandomImage {\n  randomImage {\n    ...Image\n  }\n}"


class SearchImagesQueryOptions(HasZarrStoreTrait, BaseModel):
    typename: Optional[Literal["Image"]] = Field(alias="__typename", exclude=True)
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchImagesQuery(BaseModel):
    options: Tuple[SearchImagesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchImages($search: String, $values: [ID!]) {\n  options: images(\n    filters: {name: {contains: $search}, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n  }\n}"


class ImagesQuery(BaseModel):
    images: Tuple[Image, ...]

    class Arguments(BaseModel):
        filter: Optional[ImageFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)

    class Meta:
        document = "fragment Era on Era {\n  id\n  begin\n  name\n}\n\nfragment Channel on Channel {\n  id\n  name\n  excitationWavelength\n}\n\nfragment View on View {\n  zMin\n  zMax\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment TimepointView on TimepointView {\n  ...View\n  id\n  msSinceStart\n  indexSinceStart\n  era {\n    ...Era\n  }\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  cMin\n  cMax\n  fullColour\n  baseColor\n}\n\nfragment AffineTransformationView on AffineTransformationView {\n  ...View\n  id\n  affineMatrix\n  stage {\n    id\n  }\n}\n\nfragment OpticsView on OpticsView {\n  ...View\n  objective {\n    id\n    name\n    serialNumber\n  }\n  camera {\n    id\n    name\n    serialNumber\n  }\n  instrument {\n    id\n    name\n    serialNumber\n  }\n}\n\nfragment LabelView on LabelView {\n  ...View\n  id\n  fluorophore {\n    id\n    kind {\n      id\n      label\n    }\n    name\n  }\n  primaryAntibody {\n    id\n    kind {\n      id\n      label\n    }\n    name\n  }\n  secondaryAntibody {\n    id\n    kind {\n      id\n      label\n    }\n    name\n  }\n}\n\nfragment ScaleView on ScaleView {\n  ...View\n  id\n  scaleX\n  scaleY\n  scaleZ\n  scaleT\n  scaleC\n}\n\nfragment ChannelView on ChannelView {\n  ...View\n  id\n  channel {\n    ...Channel\n  }\n}\n\nfragment Image on Image {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...ZarrStore\n  }\n  views {\n    ...ChannelView\n    ...AffineTransformationView\n    ...LabelView\n    ...TimepointView\n    ...OpticsView\n    ...ScaleView\n  }\n  derivedScaleViews {\n    ...ScaleView\n    image {\n      name\n      store {\n        ...ZarrStore\n      }\n    }\n  }\n  rgbContexts {\n    id\n    name\n    views {\n      ...RGBView\n    }\n  }\n}\n\nquery Images($filter: ImageFilter, $pagination: OffsetPaginationInput) {\n  images(filters: $filter, pagination: $pagination) {\n    ...Image\n  }\n}"


class GetEntityQuery(BaseModel):
    entity: Entity

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Entity on Entity {\n  id\n  name\n  kind {\n    id\n    label\n    ontology {\n      id\n      name\n    }\n  }\n  group {\n    id\n    name\n  }\n}\n\nquery GetEntity($id: ID!) {\n  entity(id: $id) {\n    ...Entity\n  }\n}"


class SearchEntitiesQueryOptions(EntityTrait, BaseModel):
    typename: Optional[Literal["Entity"]] = Field(alias="__typename", exclude=True)
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchEntitiesQuery(BaseModel):
    options: Tuple[SearchEntitiesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchEntities($search: String, $values: [ID!]) {\n  options: entities(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n  }\n}"


class GetProtocolQuery(BaseModel):
    protocol: Protocol

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Protocol on Protocol {\n  id\n  name\n  experiment {\n    id\n    name\n    description\n  }\n}\n\nquery GetProtocol($id: ID!) {\n  protocol(id: $id) {\n    ...Protocol\n  }\n}"


class SearchProtocolsQueryOptions(BaseModel):
    typename: Optional[Literal["Protocol"]] = Field(alias="__typename", exclude=True)
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchProtocolsQuery(BaseModel):
    options: Tuple[SearchProtocolsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchProtocols($search: String, $values: [ID!]) {\n  options: protocols(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n  }\n}"


class GetSnapshotQuery(BaseModel):
    snapshot: Snapshot

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Snapshot on Snapshot {\n  id\n  store {\n    key\n    presignedUrl\n  }\n  name\n}\n\nquery GetSnapshot($id: ID!) {\n  snapshot(id: $id) {\n    ...Snapshot\n  }\n}"


class SearchSnapshotsQueryOptions(BaseModel):
    typename: Optional[Literal["Snapshot"]] = Field(alias="__typename", exclude=True)
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchSnapshotsQuery(BaseModel):
    options: Tuple[SearchSnapshotsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchSnapshots($search: String, $values: [ID!]) {\n  options: snapshots(\n    filters: {name: {contains: $search}, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n  }\n}"


class GetEntityRelationKindQuery(BaseModel):
    entity_relation_kind: EntityRelationKind = Field(alias="entityRelationKind")

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment EntityRelationKind on EntityRelationKind {\n  id\n  leftKind {\n    id\n  }\n  rightKind {\n    id\n  }\n  kind {\n    id\n  }\n}\n\nquery GetEntityRelationKind($id: ID!) {\n  entityRelationKind(id: $id) {\n    ...EntityRelationKind\n  }\n}"


class SearchEntityRelationKindsQueryOptions(EntityRelationKindTrait, BaseModel):
    typename: Optional[Literal["EntityRelationKind"]] = Field(
        alias="__typename", exclude=True
    )
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchEntityRelationKindsQuery(BaseModel):
    options: Tuple[SearchEntityRelationKindsQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchEntityRelationKinds($search: String, $values: [ID!]) {\n  options: entityRelationKinds(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: label\n  }\n}"


class GetOntologyQuery(BaseModel):
    ontology: Ontology

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment Ontology on Ontology {\n  id\n  name\n}\n\nquery GetOntology($id: ID!) {\n  ontology(id: $id) {\n    ...Ontology\n  }\n}"


class SearchOntologiesQueryOptions(OntologyTrait, BaseModel):
    typename: Optional[Literal["Ontology"]] = Field(alias="__typename", exclude=True)
    value: ID
    label: str

    class Config:
        """A config class"""

        frozen = True


class SearchOntologiesQuery(BaseModel):
    options: Tuple[SearchOntologiesQueryOptions, ...]

    class Arguments(BaseModel):
        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)

    class Meta:
        document = "query SearchOntologies($search: String, $values: [ID!]) {\n  options: ontologies(\n    filters: {search: $search, ids: $values}\n    pagination: {limit: 10}\n  ) {\n    value: id\n    label: name\n  }\n}"


class GetRGBContextQuery(BaseModel):
    rgbcontext: RGBContext

    class Arguments(BaseModel):
        id: ID

    class Meta:
        document = "fragment View on View {\n  zMin\n  zMax\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  cMin\n  cMax\n  fullColour\n  baseColor\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment RGBContext on RGBContext {\n  id\n  views {\n    ...RGBView\n  }\n  image {\n    id\n    store {\n      ...ZarrStore\n    }\n  }\n  pinned\n  name\n  z\n  t\n  c\n  blending\n}\n\nquery GetRGBContext($id: ID!) {\n  rgbcontext(id: $id) {\n    ...RGBContext\n  }\n}"


class WatchFilesSubscriptionFiles(BaseModel):
    typename: Optional[Literal["FileEvent"]] = Field(alias="__typename", exclude=True)
    create: Optional[File]
    delete: Optional[ID]
    update: Optional[File]

    class Config:
        """A config class"""

        frozen = True


class WatchFilesSubscription(BaseModel):
    files: WatchFilesSubscriptionFiles

    class Arguments(BaseModel):
        dataset: Optional[ID] = Field(default=None)

    class Meta:
        document = "fragment BigFileStore on BigFileStore {\n  id\n  key\n  bucket\n  path\n  presignedUrl\n}\n\nfragment File on File {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...BigFileStore\n  }\n}\n\nsubscription WatchFiles($dataset: ID) {\n  files(dataset: $dataset) {\n    create {\n      ...File\n    }\n    delete\n    update {\n      ...File\n    }\n  }\n}"


class WatchImagesSubscriptionImages(BaseModel):
    typename: Optional[Literal["ImageEvent"]] = Field(alias="__typename", exclude=True)
    create: Optional[Image]
    delete: Optional[ID]
    update: Optional[Image]

    class Config:
        """A config class"""

        frozen = True


class WatchImagesSubscription(BaseModel):
    images: WatchImagesSubscriptionImages

    class Arguments(BaseModel):
        dataset: Optional[ID] = Field(default=None)

    class Meta:
        document = "fragment Era on Era {\n  id\n  begin\n  name\n}\n\nfragment Channel on Channel {\n  id\n  name\n  excitationWavelength\n}\n\nfragment View on View {\n  zMin\n  zMax\n}\n\nfragment ZarrStore on ZarrStore {\n  id\n  key\n  bucket\n  path\n}\n\nfragment TimepointView on TimepointView {\n  ...View\n  id\n  msSinceStart\n  indexSinceStart\n  era {\n    ...Era\n  }\n}\n\nfragment RGBView on RGBView {\n  ...View\n  id\n  colorMap\n  contrastLimitMin\n  contrastLimitMax\n  gamma\n  rescale\n  active\n  cMin\n  cMax\n  fullColour\n  baseColor\n}\n\nfragment AffineTransformationView on AffineTransformationView {\n  ...View\n  id\n  affineMatrix\n  stage {\n    id\n  }\n}\n\nfragment OpticsView on OpticsView {\n  ...View\n  objective {\n    id\n    name\n    serialNumber\n  }\n  camera {\n    id\n    name\n    serialNumber\n  }\n  instrument {\n    id\n    name\n    serialNumber\n  }\n}\n\nfragment LabelView on LabelView {\n  ...View\n  id\n  fluorophore {\n    id\n    kind {\n      id\n      label\n    }\n    name\n  }\n  primaryAntibody {\n    id\n    kind {\n      id\n      label\n    }\n    name\n  }\n  secondaryAntibody {\n    id\n    kind {\n      id\n      label\n    }\n    name\n  }\n}\n\nfragment ScaleView on ScaleView {\n  ...View\n  id\n  scaleX\n  scaleY\n  scaleZ\n  scaleT\n  scaleC\n}\n\nfragment ChannelView on ChannelView {\n  ...View\n  id\n  channel {\n    ...Channel\n  }\n}\n\nfragment Image on Image {\n  origins {\n    id\n  }\n  id\n  name\n  store {\n    ...ZarrStore\n  }\n  views {\n    ...ChannelView\n    ...AffineTransformationView\n    ...LabelView\n    ...TimepointView\n    ...OpticsView\n    ...ScaleView\n  }\n  derivedScaleViews {\n    ...ScaleView\n    image {\n      name\n      store {\n        ...ZarrStore\n      }\n    }\n  }\n  rgbContexts {\n    id\n    name\n    views {\n      ...RGBView\n    }\n  }\n}\n\nsubscription WatchImages($dataset: ID) {\n  images(dataset: $dataset) {\n    create {\n      ...Image\n    }\n    delete\n    update {\n      ...Image\n    }\n  }\n}"


class WatchRoisSubscriptionRois(BaseModel):
    typename: Optional[Literal["RoiEvent"]] = Field(alias="__typename", exclude=True)
    create: Optional[ROI]
    delete: Optional[ID]
    update: Optional[ROI]

    class Config:
        """A config class"""

        frozen = True


class WatchRoisSubscription(BaseModel):
    rois: WatchRoisSubscriptionRois

    class Arguments(BaseModel):
        image: ID

    class Meta:
        document = "fragment ROI on ROI {\n  id\n  image {\n    id\n  }\n  vectors\n  kind\n}\n\nsubscription WatchRois($image: ID!) {\n  rois(image: $image) {\n    create {\n      ...ROI\n    }\n    delete\n    update {\n      ...ROI\n    }\n  }\n}"


async def acreate_camera(
    serial_number: str,
    name: Optional[str] = None,
    pixel_size_x: Optional[Micrometers] = None,
    pixel_size_y: Optional[Micrometers] = None,
    sensor_size_x: Optional[int] = None,
    sensor_size_y: Optional[int] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateCameraMutationCreatecamera:
    """CreateCamera



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        pixel_size_x (Optional[Micrometers], optional): pixelSizeX.
        pixel_size_y (Optional[Micrometers], optional): pixelSizeY.
        sensor_size_x (Optional[int], optional): sensorSizeX.
        sensor_size_y (Optional[int], optional): sensorSizeY.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateCameraMutationCreatecamera"""
    return (
        await aexecute(
            CreateCameraMutation,
            {
                "serialNumber": serial_number,
                "name": name,
                "pixelSizeX": pixel_size_x,
                "pixelSizeY": pixel_size_y,
                "sensorSizeX": sensor_size_x,
                "sensorSizeY": sensor_size_y,
            },
            rath=rath,
        )
    ).create_camera


def create_camera(
    serial_number: str,
    name: Optional[str] = None,
    pixel_size_x: Optional[Micrometers] = None,
    pixel_size_y: Optional[Micrometers] = None,
    sensor_size_x: Optional[int] = None,
    sensor_size_y: Optional[int] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateCameraMutationCreatecamera:
    """CreateCamera



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        pixel_size_x (Optional[Micrometers], optional): pixelSizeX.
        pixel_size_y (Optional[Micrometers], optional): pixelSizeY.
        sensor_size_x (Optional[int], optional): sensorSizeX.
        sensor_size_y (Optional[int], optional): sensorSizeY.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateCameraMutationCreatecamera"""
    return execute(
        CreateCameraMutation,
        {
            "serialNumber": serial_number,
            "name": name,
            "pixelSizeX": pixel_size_x,
            "pixelSizeY": pixel_size_y,
            "sensorSizeX": sensor_size_x,
            "sensorSizeY": sensor_size_y,
        },
        rath=rath,
    ).create_camera


async def aensure_camera(
    serial_number: str,
    name: Optional[str] = None,
    pixel_size_x: Optional[Micrometers] = None,
    pixel_size_y: Optional[Micrometers] = None,
    sensor_size_x: Optional[int] = None,
    sensor_size_y: Optional[int] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureCameraMutationEnsurecamera:
    """EnsureCamera



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        pixel_size_x (Optional[Micrometers], optional): pixelSizeX.
        pixel_size_y (Optional[Micrometers], optional): pixelSizeY.
        sensor_size_x (Optional[int], optional): sensorSizeX.
        sensor_size_y (Optional[int], optional): sensorSizeY.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureCameraMutationEnsurecamera"""
    return (
        await aexecute(
            EnsureCameraMutation,
            {
                "serialNumber": serial_number,
                "name": name,
                "pixelSizeX": pixel_size_x,
                "pixelSizeY": pixel_size_y,
                "sensorSizeX": sensor_size_x,
                "sensorSizeY": sensor_size_y,
            },
            rath=rath,
        )
    ).ensure_camera


def ensure_camera(
    serial_number: str,
    name: Optional[str] = None,
    pixel_size_x: Optional[Micrometers] = None,
    pixel_size_y: Optional[Micrometers] = None,
    sensor_size_x: Optional[int] = None,
    sensor_size_y: Optional[int] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureCameraMutationEnsurecamera:
    """EnsureCamera



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        pixel_size_x (Optional[Micrometers], optional): pixelSizeX.
        pixel_size_y (Optional[Micrometers], optional): pixelSizeY.
        sensor_size_x (Optional[int], optional): sensorSizeX.
        sensor_size_y (Optional[int], optional): sensorSizeY.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureCameraMutationEnsurecamera"""
    return execute(
        EnsureCameraMutation,
        {
            "serialNumber": serial_number,
            "name": name,
            "pixelSizeX": pixel_size_x,
            "pixelSizeY": pixel_size_y,
            "sensorSizeX": sensor_size_x,
            "sensorSizeY": sensor_size_y,
        },
        rath=rath,
    ).ensure_camera


async def amap_protocol_step(
    step: ID, protocol: ID, t: int, rath: Optional[MikroNextRath] = None
) -> ProtocolStepMapping:
    """MapProtocolStep



    Arguments:
        step (ID): step
        protocol (ID): protocol
        t (int): t
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ProtocolStepMapping"""
    return (
        await aexecute(
            MapProtocolStepMutation,
            {"step": step, "protocol": protocol, "t": t},
            rath=rath,
        )
    ).map_protocol_step


def map_protocol_step(
    step: ID, protocol: ID, t: int, rath: Optional[MikroNextRath] = None
) -> ProtocolStepMapping:
    """MapProtocolStep



    Arguments:
        step (ID): step
        protocol (ID): protocol
        t (int): t
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ProtocolStepMapping"""
    return execute(
        MapProtocolStepMutation, {"step": step, "protocol": protocol, "t": t}, rath=rath
    ).map_protocol_step


async def acreate_render_tree(
    name: str, tree: TreeInput, rath: Optional[MikroNextRath] = None
) -> CreateRenderTreeMutationCreaterendertree:
    """CreateRenderTree



    Arguments:
        name (str): name
        tree (TreeInput): tree
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateRenderTreeMutationCreaterendertree"""
    return (
        await aexecute(
            CreateRenderTreeMutation, {"name": name, "tree": tree}, rath=rath
        )
    ).create_render_tree


def create_render_tree(
    name: str, tree: TreeInput, rath: Optional[MikroNextRath] = None
) -> CreateRenderTreeMutationCreaterendertree:
    """CreateRenderTree



    Arguments:
        name (str): name
        tree (TreeInput): tree
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateRenderTreeMutationCreaterendertree"""
    return execute(
        CreateRenderTreeMutation, {"name": name, "tree": tree}, rath=rath
    ).create_render_tree


async def afrom_parquet_like(
    dataframe: ParquetLike,
    name: str,
    origins: Optional[List[ID]] = None,
    dataset: Optional[ID] = None,
    rath: Optional[MikroNextRath] = None,
) -> Table:
    """from_parquet_like



    Arguments:
        dataframe (ParquetLike): dataframe
        name (str): name
        origins (Optional[List[ID]], optional): origins.
        dataset (Optional[ID], optional): dataset.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Table"""
    return (
        await aexecute(
            From_parquet_likeMutation,
            {
                "dataframe": dataframe,
                "name": name,
                "origins": origins,
                "dataset": dataset,
            },
            rath=rath,
        )
    ).from_parquet_like


def from_parquet_like(
    dataframe: ParquetLike,
    name: str,
    origins: Optional[List[ID]] = None,
    dataset: Optional[ID] = None,
    rath: Optional[MikroNextRath] = None,
) -> Table:
    """from_parquet_like



    Arguments:
        dataframe (ParquetLike): dataframe
        name (str): name
        origins (Optional[List[ID]], optional): origins.
        dataset (Optional[ID], optional): dataset.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Table"""
    return execute(
        From_parquet_likeMutation,
        {"dataframe": dataframe, "name": name, "origins": origins, "dataset": dataset},
        rath=rath,
    ).from_parquet_like


async def arequest_table_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestTableUpload


     requestTableUpload: Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        key (str): key
        datalayer (str): datalayer
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials"""
    return (
        await aexecute(
            RequestTableUploadMutation, {"key": key, "datalayer": datalayer}, rath=rath
        )
    ).request_table_upload


def request_table_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestTableUpload


     requestTableUpload: Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        key (str): key
        datalayer (str): datalayer
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials"""
    return execute(
        RequestTableUploadMutation, {"key": key, "datalayer": datalayer}, rath=rath
    ).request_table_upload


async def arequest_table_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestTableAccess


     requestTableAccess: Temporary Credentials for a file download that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        store (ID): store
        duration (Optional[int], optional): duration.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials"""
    return (
        await aexecute(
            RequestTableAccessMutation,
            {"store": store, "duration": duration},
            rath=rath,
        )
    ).request_table_access


def request_table_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestTableAccess


     requestTableAccess: Temporary Credentials for a file download that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        store (ID): store
        duration (Optional[int], optional): duration.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials"""
    return execute(
        RequestTableAccessMutation, {"store": store, "duration": duration}, rath=rath
    ).request_table_access


async def acreate_rendered_plot(
    plot: Upload,
    name: str,
    overlays: Optional[List[OverlayInput]] = None,
    rath: Optional[MikroNextRath] = None,
) -> RenderedPlot:
    """CreateRenderedPlot



    Arguments:
        plot (Upload): plot
        name (str): name
        overlays (Optional[List[OverlayInput]], optional): overlays.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RenderedPlot"""
    return (
        await aexecute(
            CreateRenderedPlotMutation,
            {"plot": plot, "name": name, "overlays": overlays},
            rath=rath,
        )
    ).create_rendered_plot


def create_rendered_plot(
    plot: Upload,
    name: str,
    overlays: Optional[List[OverlayInput]] = None,
    rath: Optional[MikroNextRath] = None,
) -> RenderedPlot:
    """CreateRenderedPlot



    Arguments:
        plot (Upload): plot
        name (str): name
        overlays (Optional[List[OverlayInput]], optional): overlays.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RenderedPlot"""
    return execute(
        CreateRenderedPlotMutation,
        {"plot": plot, "name": name, "overlays": overlays},
        rath=rath,
    ).create_rendered_plot


async def afrom_file_like(
    file: FileLike,
    name: str,
    origins: Optional[List[ID]] = None,
    dataset: Optional[ID] = None,
    rath: Optional[MikroNextRath] = None,
) -> File:
    """from_file_like



    Arguments:
        file (FileLike): file
        name (str): name
        origins (Optional[List[ID]], optional): origins.
        dataset (Optional[ID], optional): dataset.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        File"""
    return (
        await aexecute(
            From_file_likeMutation,
            {"file": file, "name": name, "origins": origins, "dataset": dataset},
            rath=rath,
        )
    ).from_file_like


def from_file_like(
    file: FileLike,
    name: str,
    origins: Optional[List[ID]] = None,
    dataset: Optional[ID] = None,
    rath: Optional[MikroNextRath] = None,
) -> File:
    """from_file_like



    Arguments:
        file (FileLike): file
        name (str): name
        origins (Optional[List[ID]], optional): origins.
        dataset (Optional[ID], optional): dataset.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        File"""
    return execute(
        From_file_likeMutation,
        {"file": file, "name": name, "origins": origins, "dataset": dataset},
        rath=rath,
    ).from_file_like


async def arequest_file_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestFileUpload


     requestFileUpload: Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        key (str): key
        datalayer (str): datalayer
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials"""
    return (
        await aexecute(
            RequestFileUploadMutation, {"key": key, "datalayer": datalayer}, rath=rath
        )
    ).request_file_upload


def request_file_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestFileUpload


     requestFileUpload: Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        key (str): key
        datalayer (str): datalayer
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials"""
    return execute(
        RequestFileUploadMutation, {"key": key, "datalayer": datalayer}, rath=rath
    ).request_file_upload


async def arequest_file_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestFileAccess


     requestFileAccess: Temporary Credentials for a file download that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        store (ID): store
        duration (Optional[int], optional): duration.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials"""
    return (
        await aexecute(
            RequestFileAccessMutation, {"store": store, "duration": duration}, rath=rath
        )
    ).request_file_access


def request_file_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestFileAccess


     requestFileAccess: Temporary Credentials for a file download that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        store (ID): store
        duration (Optional[int], optional): duration.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials"""
    return execute(
        RequestFileAccessMutation, {"store": store, "duration": duration}, rath=rath
    ).request_file_access


async def acreate_entity_kind(
    label: str,
    ontology: Optional[ID] = None,
    purl: Optional[str] = None,
    description: Optional[str] = None,
    color: Optional[List[int]] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateEntityKindMutationCreateentitykind:
    """CreateEntityKind



    Arguments:
        label (str): label
        ontology (Optional[ID], optional): ontology.
        purl (Optional[str], optional): purl.
        description (Optional[str], optional): description.
        color (Optional[List[int]], optional): color.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateEntityKindMutationCreateentitykind"""
    return (
        await aexecute(
            CreateEntityKindMutation,
            {
                "label": label,
                "ontology": ontology,
                "purl": purl,
                "description": description,
                "color": color,
            },
            rath=rath,
        )
    ).create_entity_kind


def create_entity_kind(
    label: str,
    ontology: Optional[ID] = None,
    purl: Optional[str] = None,
    description: Optional[str] = None,
    color: Optional[List[int]] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateEntityKindMutationCreateentitykind:
    """CreateEntityKind



    Arguments:
        label (str): label
        ontology (Optional[ID], optional): ontology.
        purl (Optional[str], optional): purl.
        description (Optional[str], optional): description.
        color (Optional[List[int]], optional): color.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateEntityKindMutationCreateentitykind"""
    return execute(
        CreateEntityKindMutation,
        {
            "label": label,
            "ontology": ontology,
            "purl": purl,
            "description": description,
            "color": color,
        },
        rath=rath,
    ).create_entity_kind


async def acreate_stage(name: str, rath: Optional[MikroNextRath] = None) -> Stage:
    """CreateStage



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Stage"""
    return (await aexecute(CreateStageMutation, {"name": name}, rath=rath)).create_stage


def create_stage(name: str, rath: Optional[MikroNextRath] = None) -> Stage:
    """CreateStage



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Stage"""
    return execute(CreateStageMutation, {"name": name}, rath=rath).create_stage


async def acreate_roi(
    image: ID,
    vectors: List[FiveDVector],
    kind: RoiKind,
    entity: Optional[ID] = None,
    entity_kind: Optional[ID] = None,
    entity_parent: Optional[ID] = None,
    rath: Optional[MikroNextRath] = None,
) -> ROI:
    """CreateRoi



    Arguments:
        image (ID): image
        vectors (List[FiveDVector]): vectors
        kind (RoiKind): kind
        entity (Optional[ID], optional): entity.
        entity_kind (Optional[ID], optional): entityKind.
        entity_parent (Optional[ID], optional): entityParent.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ROI"""
    return (
        await aexecute(
            CreateRoiMutation,
            {
                "image": image,
                "vectors": vectors,
                "kind": kind,
                "entity": entity,
                "entityKind": entity_kind,
                "entityParent": entity_parent,
            },
            rath=rath,
        )
    ).create_roi


def create_roi(
    image: ID,
    vectors: List[FiveDVector],
    kind: RoiKind,
    entity: Optional[ID] = None,
    entity_kind: Optional[ID] = None,
    entity_parent: Optional[ID] = None,
    rath: Optional[MikroNextRath] = None,
) -> ROI:
    """CreateRoi



    Arguments:
        image (ID): image
        vectors (List[FiveDVector]): vectors
        kind (RoiKind): kind
        entity (Optional[ID], optional): entity.
        entity_kind (Optional[ID], optional): entityKind.
        entity_parent (Optional[ID], optional): entityParent.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ROI"""
    return execute(
        CreateRoiMutation,
        {
            "image": image,
            "vectors": vectors,
            "kind": kind,
            "entity": entity,
            "entityKind": entity_kind,
            "entityParent": entity_parent,
        },
        rath=rath,
    ).create_roi


async def adelete_roi(roi: ID, rath: Optional[MikroNextRath] = None) -> ID:
    """DeleteRoi


     deleteRoi: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.


    Arguments:
        roi (ID): roi
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ID"""
    return (await aexecute(DeleteRoiMutation, {"roi": roi}, rath=rath)).delete_roi


def delete_roi(roi: ID, rath: Optional[MikroNextRath] = None) -> ID:
    """DeleteRoi


     deleteRoi: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID.


    Arguments:
        roi (ID): roi
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ID"""
    return execute(DeleteRoiMutation, {"roi": roi}, rath=rath).delete_roi


async def acreate_objective(
    serial_number: str,
    name: Optional[str] = None,
    na: Optional[float] = None,
    magnification: Optional[float] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateObjectiveMutationCreateobjective:
    """CreateObjective



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        na (Optional[float], optional): na.
        magnification (Optional[float], optional): magnification.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateObjectiveMutationCreateobjective"""
    return (
        await aexecute(
            CreateObjectiveMutation,
            {
                "serialNumber": serial_number,
                "name": name,
                "na": na,
                "magnification": magnification,
            },
            rath=rath,
        )
    ).create_objective


def create_objective(
    serial_number: str,
    name: Optional[str] = None,
    na: Optional[float] = None,
    magnification: Optional[float] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateObjectiveMutationCreateobjective:
    """CreateObjective



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        na (Optional[float], optional): na.
        magnification (Optional[float], optional): magnification.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateObjectiveMutationCreateobjective"""
    return execute(
        CreateObjectiveMutation,
        {
            "serialNumber": serial_number,
            "name": name,
            "na": na,
            "magnification": magnification,
        },
        rath=rath,
    ).create_objective


async def aensure_objective(
    serial_number: str,
    name: Optional[str] = None,
    na: Optional[float] = None,
    magnification: Optional[float] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureObjectiveMutationEnsureobjective:
    """EnsureObjective



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        na (Optional[float], optional): na.
        magnification (Optional[float], optional): magnification.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureObjectiveMutationEnsureobjective"""
    return (
        await aexecute(
            EnsureObjectiveMutation,
            {
                "serialNumber": serial_number,
                "name": name,
                "na": na,
                "magnification": magnification,
            },
            rath=rath,
        )
    ).ensure_objective


def ensure_objective(
    serial_number: str,
    name: Optional[str] = None,
    na: Optional[float] = None,
    magnification: Optional[float] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureObjectiveMutationEnsureobjective:
    """EnsureObjective



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        na (Optional[float], optional): na.
        magnification (Optional[float], optional): magnification.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureObjectiveMutationEnsureobjective"""
    return execute(
        EnsureObjectiveMutation,
        {
            "serialNumber": serial_number,
            "name": name,
            "na": na,
            "magnification": magnification,
        },
        rath=rath,
    ).ensure_objective


async def acreate_relation_metric(
    kind: ID, data_kind: MetricDataType, rath: Optional[MikroNextRath] = None
) -> RelationMetric:
    """CreateRelationMetric



    Arguments:
        kind (ID): kind
        data_kind (MetricDataType): dataKind
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RelationMetric"""
    return (
        await aexecute(
            CreateRelationMetricMutation,
            {"kind": kind, "dataKind": data_kind},
            rath=rath,
        )
    ).create_relation_metric


def create_relation_metric(
    kind: ID, data_kind: MetricDataType, rath: Optional[MikroNextRath] = None
) -> RelationMetric:
    """CreateRelationMetric



    Arguments:
        kind (ID): kind
        data_kind (MetricDataType): dataKind
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RelationMetric"""
    return execute(
        CreateRelationMetricMutation, {"kind": kind, "dataKind": data_kind}, rath=rath
    ).create_relation_metric


async def aattach_relation_metric_to_relation(
    relation: ID, metric: ID, value: Any, rath: Optional[MikroNextRath] = None
) -> EntityRelation:
    """AttachRelationMetricToRelation



    Arguments:
        relation (ID): relation
        metric (ID): metric
        value (Any): value
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EntityRelation"""
    return (
        await aexecute(
            AttachRelationMetricToRelationMutation,
            {"relation": relation, "metric": metric, "value": value},
            rath=rath,
        )
    ).attach_relation_metric


def attach_relation_metric_to_relation(
    relation: ID, metric: ID, value: Any, rath: Optional[MikroNextRath] = None
) -> EntityRelation:
    """AttachRelationMetricToRelation



    Arguments:
        relation (ID): relation
        metric (ID): metric
        value (Any): value
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EntityRelation"""
    return execute(
        AttachRelationMetricToRelationMutation,
        {"relation": relation, "metric": metric, "value": value},
        rath=rath,
    ).attach_relation_metric


async def acreate_protocol_step(
    name: str,
    kind: ID,
    reagents: Optional[List[ID]] = None,
    description: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> ProtocolStep:
    """CreateProtocolStep



    Arguments:
        name (str): name
        kind (ID): kind
        reagents (Optional[List[ID]], optional): reagents.
        description (Optional[str], optional): description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ProtocolStep"""
    return (
        await aexecute(
            CreateProtocolStepMutation,
            {
                "name": name,
                "kind": kind,
                "reagents": reagents,
                "description": description,
            },
            rath=rath,
        )
    ).create_protocol_step


def create_protocol_step(
    name: str,
    kind: ID,
    reagents: Optional[List[ID]] = None,
    description: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> ProtocolStep:
    """CreateProtocolStep



    Arguments:
        name (str): name
        kind (ID): kind
        reagents (Optional[List[ID]], optional): reagents.
        description (Optional[str], optional): description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ProtocolStep"""
    return execute(
        CreateProtocolStepMutation,
        {"name": name, "kind": kind, "reagents": reagents, "description": description},
        rath=rath,
    ).create_protocol_step


async def acreate_dataset(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateDatasetMutationCreatedataset:
    """CreateDataset



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateDatasetMutationCreatedataset"""
    return (
        await aexecute(CreateDatasetMutation, {"name": name}, rath=rath)
    ).create_dataset


def create_dataset(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateDatasetMutationCreatedataset:
    """CreateDataset



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateDatasetMutationCreatedataset"""
    return execute(CreateDatasetMutation, {"name": name}, rath=rath).create_dataset


async def aupdate_dataset(
    id: ID, name: str, rath: Optional[MikroNextRath] = None
) -> UpdateDatasetMutationUpdatedataset:
    """UpdateDataset



    Arguments:
        id (ID): id
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        UpdateDatasetMutationUpdatedataset"""
    return (
        await aexecute(UpdateDatasetMutation, {"id": id, "name": name}, rath=rath)
    ).update_dataset


def update_dataset(
    id: ID, name: str, rath: Optional[MikroNextRath] = None
) -> UpdateDatasetMutationUpdatedataset:
    """UpdateDataset



    Arguments:
        id (ID): id
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        UpdateDatasetMutationUpdatedataset"""
    return execute(
        UpdateDatasetMutation, {"id": id, "name": name}, rath=rath
    ).update_dataset


async def arevert_dataset(
    dataset: ID, history: ID, rath: Optional[MikroNextRath] = None
) -> RevertDatasetMutationRevertdataset:
    """RevertDataset



    Arguments:
        dataset (ID): dataset
        history (ID): history
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RevertDatasetMutationRevertdataset"""
    return (
        await aexecute(
            RevertDatasetMutation, {"dataset": dataset, "history": history}, rath=rath
        )
    ).revert_dataset


def revert_dataset(
    dataset: ID, history: ID, rath: Optional[MikroNextRath] = None
) -> RevertDatasetMutationRevertdataset:
    """RevertDataset



    Arguments:
        dataset (ID): dataset
        history (ID): history
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RevertDatasetMutationRevertdataset"""
    return execute(
        RevertDatasetMutation, {"dataset": dataset, "history": history}, rath=rath
    ).revert_dataset


async def acreate_entity_group(
    name: str, image: Optional[ID] = None, rath: Optional[MikroNextRath] = None
) -> CreateEntityGroupMutationCreateentitygroup:
    """CreateEntityGroup



    Arguments:
        name (str): name
        image (Optional[ID], optional): image.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateEntityGroupMutationCreateentitygroup"""
    return (
        await aexecute(
            CreateEntityGroupMutation, {"name": name, "image": image}, rath=rath
        )
    ).create_entity_group


def create_entity_group(
    name: str, image: Optional[ID] = None, rath: Optional[MikroNextRath] = None
) -> CreateEntityGroupMutationCreateentitygroup:
    """CreateEntityGroup



    Arguments:
        name (str): name
        image (Optional[ID], optional): image.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateEntityGroupMutationCreateentitygroup"""
    return execute(
        CreateEntityGroupMutation, {"name": name, "image": image}, rath=rath
    ).create_entity_group


async def acreate_specimen(
    entity: ID, protocol: ID, rath: Optional[MikroNextRath] = None
) -> Specimen:
    """CreateSpecimen



    Arguments:
        entity (ID): entity
        protocol (ID): protocol
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Specimen"""
    return (
        await aexecute(
            CreateSpecimenMutation, {"entity": entity, "protocol": protocol}, rath=rath
        )
    ).create_specimen


def create_specimen(
    entity: ID, protocol: ID, rath: Optional[MikroNextRath] = None
) -> Specimen:
    """CreateSpecimen



    Arguments:
        entity (ID): entity
        protocol (ID): protocol
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Specimen"""
    return execute(
        CreateSpecimenMutation, {"entity": entity, "protocol": protocol}, rath=rath
    ).create_specimen


async def acreate_instrument(
    serial_number: str,
    name: Optional[str] = None,
    model: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateInstrumentMutationCreateinstrument:
    """CreateInstrument



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        model (Optional[str], optional): model.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateInstrumentMutationCreateinstrument"""
    return (
        await aexecute(
            CreateInstrumentMutation,
            {"serialNumber": serial_number, "name": name, "model": model},
            rath=rath,
        )
    ).create_instrument


def create_instrument(
    serial_number: str,
    name: Optional[str] = None,
    model: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateInstrumentMutationCreateinstrument:
    """CreateInstrument



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        model (Optional[str], optional): model.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateInstrumentMutationCreateinstrument"""
    return execute(
        CreateInstrumentMutation,
        {"serialNumber": serial_number, "name": name, "model": model},
        rath=rath,
    ).create_instrument


async def aensure_instrument(
    serial_number: str,
    name: Optional[str] = None,
    model: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureInstrumentMutationEnsureinstrument:
    """EnsureInstrument



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        model (Optional[str], optional): model.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureInstrumentMutationEnsureinstrument"""
    return (
        await aexecute(
            EnsureInstrumentMutation,
            {"serialNumber": serial_number, "name": name, "model": model},
            rath=rath,
        )
    ).ensure_instrument


def ensure_instrument(
    serial_number: str,
    name: Optional[str] = None,
    model: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> EnsureInstrumentMutationEnsureinstrument:
    """EnsureInstrument



    Arguments:
        serial_number (str): serialNumber
        name (Optional[str], optional): name.
        model (Optional[str], optional): model.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureInstrumentMutationEnsureinstrument"""
    return execute(
        EnsureInstrumentMutation,
        {"serialNumber": serial_number, "name": name, "model": model},
        rath=rath,
    ).ensure_instrument


async def acreate_entity_relation(
    left: ID, right: ID, kind: ID, rath: Optional[MikroNextRath] = None
) -> EntityRelation:
    """CreateEntityRelation



    Arguments:
        left (ID): left
        right (ID): right
        kind (ID): kind
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EntityRelation"""
    return (
        await aexecute(
            CreateEntityRelationMutation,
            {"left": left, "right": right, "kind": kind},
            rath=rath,
        )
    ).create_entity_relation


def create_entity_relation(
    left: ID, right: ID, kind: ID, rath: Optional[MikroNextRath] = None
) -> EntityRelation:
    """CreateEntityRelation



    Arguments:
        left (ID): left
        right (ID): right
        kind (ID): kind
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EntityRelation"""
    return execute(
        CreateEntityRelationMutation,
        {"left": left, "right": right, "kind": kind},
        rath=rath,
    ).create_entity_relation


async def acreate_entity_relation_kind(
    left_kind: ID, right_kind: ID, kind: ID, rath: Optional[MikroNextRath] = None
) -> EntityRelationKind:
    """CreateEntityRelationKind



    Arguments:
        left_kind (ID): leftKind
        right_kind (ID): rightKind
        kind (ID): kind
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EntityRelationKind"""
    return (
        await aexecute(
            CreateEntityRelationKindMutation,
            {"leftKind": left_kind, "rightKind": right_kind, "kind": kind},
            rath=rath,
        )
    ).create_entity_relation_kind


def create_entity_relation_kind(
    left_kind: ID, right_kind: ID, kind: ID, rath: Optional[MikroNextRath] = None
) -> EntityRelationKind:
    """CreateEntityRelationKind



    Arguments:
        left_kind (ID): leftKind
        right_kind (ID): rightKind
        kind (ID): kind
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EntityRelationKind"""
    return execute(
        CreateEntityRelationKindMutation,
        {"leftKind": left_kind, "rightKind": right_kind, "kind": kind},
        rath=rath,
    ).create_entity_relation_kind


async def acreate_entity_metric(
    kind: ID, data_kind: MetricDataType, rath: Optional[MikroNextRath] = None
) -> EntityMetric:
    """CreateEntityMetric



    Arguments:
        kind (ID): kind
        data_kind (MetricDataType): dataKind
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EntityMetric"""
    return (
        await aexecute(
            CreateEntityMetricMutation, {"kind": kind, "dataKind": data_kind}, rath=rath
        )
    ).create_entity_metric


def create_entity_metric(
    kind: ID, data_kind: MetricDataType, rath: Optional[MikroNextRath] = None
) -> EntityMetric:
    """CreateEntityMetric



    Arguments:
        kind (ID): kind
        data_kind (MetricDataType): dataKind
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EntityMetric"""
    return execute(
        CreateEntityMetricMutation, {"kind": kind, "dataKind": data_kind}, rath=rath
    ).create_entity_metric


async def aattach_entity_metric_to_entity(
    entity: ID, metric: ID, value: Any, rath: Optional[MikroNextRath] = None
) -> Entity:
    """AttachEntityMetricToEntity



    Arguments:
        entity (ID): entity
        metric (ID): metric
        value (Any): value
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Entity"""
    return (
        await aexecute(
            AttachEntityMetricToEntityMutation,
            {"entity": entity, "metric": metric, "value": value},
            rath=rath,
        )
    ).attach_entity_metric


def attach_entity_metric_to_entity(
    entity: ID, metric: ID, value: Any, rath: Optional[MikroNextRath] = None
) -> Entity:
    """AttachEntityMetricToEntity



    Arguments:
        entity (ID): entity
        metric (ID): metric
        value (Any): value
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Entity"""
    return execute(
        AttachEntityMetricToEntityMutation,
        {"entity": entity, "metric": metric, "value": value},
        rath=rath,
    ).attach_entity_metric


async def aattach_metric_to_entities(
    metric: ID, pairs: List[EntityValuePairInput], rath: Optional[MikroNextRath] = None
) -> List[Entity]:
    """AttachMetricToEntities



    Arguments:
        metric (ID): metric
        pairs (List[EntityValuePairInput]): pairs
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[Entity]"""
    return (
        await aexecute(
            AttachMetricToEntitiesMutation,
            {"metric": metric, "pairs": pairs},
            rath=rath,
        )
    ).attach_metrics_to_entities


def attach_metric_to_entities(
    metric: ID, pairs: List[EntityValuePairInput], rath: Optional[MikroNextRath] = None
) -> List[Entity]:
    """AttachMetricToEntities



    Arguments:
        metric (ID): metric
        pairs (List[EntityValuePairInput]): pairs
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[Entity]"""
    return execute(
        AttachMetricToEntitiesMutation, {"metric": metric, "pairs": pairs}, rath=rath
    ).attach_metrics_to_entities


async def afrom_array_like(
    array: ArrayLike,
    name: str,
    origins: Optional[List[ID]] = None,
    channel_views: Optional[List[PartialChannelViewInput]] = None,
    transformation_views: Optional[List[PartialAffineTransformationViewInput]] = None,
    pixel_views: Optional[List[PartialPixelViewInput]] = None,
    rgb_views: Optional[List[PartialRGBViewInput]] = None,
    acquisition_views: Optional[List[PartialAcquisitionViewInput]] = None,
    timepoint_views: Optional[List[PartialTimepointViewInput]] = None,
    optics_views: Optional[List[PartialOpticsViewInput]] = None,
    specimen_views: Optional[List[PartialSpecimenViewInput]] = None,
    scale_views: Optional[List[PartialScaleViewInput]] = None,
    tags: Optional[List[str]] = None,
    file_origins: Optional[List[ID]] = None,
    roi_origins: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Image:
    """from_array_like



    Arguments:
        array (ArrayLike): array
        name (str): name
        origins (Optional[List[ID]], optional): origins.
        channel_views (Optional[List[PartialChannelViewInput]], optional): channelViews.
        transformation_views (Optional[List[PartialAffineTransformationViewInput]], optional): transformationViews.
        pixel_views (Optional[List[PartialPixelViewInput]], optional): pixelViews.
        rgb_views (Optional[List[PartialRGBViewInput]], optional): rgbViews.
        acquisition_views (Optional[List[PartialAcquisitionViewInput]], optional): acquisitionViews.
        timepoint_views (Optional[List[PartialTimepointViewInput]], optional): timepointViews.
        optics_views (Optional[List[PartialOpticsViewInput]], optional): opticsViews.
        specimen_views (Optional[List[PartialSpecimenViewInput]], optional): specimenViews.
        scale_views (Optional[List[PartialScaleViewInput]], optional): scaleViews.
        tags (Optional[List[str]], optional): tags.
        file_origins (Optional[List[ID]], optional): fileOrigins.
        roi_origins (Optional[List[ID]], optional): roiOrigins.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image"""
    return (
        await aexecute(
            From_array_likeMutation,
            {
                "array": array,
                "name": name,
                "origins": origins,
                "channelViews": channel_views,
                "transformationViews": transformation_views,
                "pixelViews": pixel_views,
                "rgbViews": rgb_views,
                "acquisitionViews": acquisition_views,
                "timepointViews": timepoint_views,
                "opticsViews": optics_views,
                "specimenViews": specimen_views,
                "scaleViews": scale_views,
                "tags": tags,
                "fileOrigins": file_origins,
                "roiOrigins": roi_origins,
            },
            rath=rath,
        )
    ).from_array_like


def from_array_like(
    array: ArrayLike,
    name: str,
    origins: Optional[List[ID]] = None,
    channel_views: Optional[List[PartialChannelViewInput]] = None,
    transformation_views: Optional[List[PartialAffineTransformationViewInput]] = None,
    pixel_views: Optional[List[PartialPixelViewInput]] = None,
    rgb_views: Optional[List[PartialRGBViewInput]] = None,
    acquisition_views: Optional[List[PartialAcquisitionViewInput]] = None,
    timepoint_views: Optional[List[PartialTimepointViewInput]] = None,
    optics_views: Optional[List[PartialOpticsViewInput]] = None,
    specimen_views: Optional[List[PartialSpecimenViewInput]] = None,
    scale_views: Optional[List[PartialScaleViewInput]] = None,
    tags: Optional[List[str]] = None,
    file_origins: Optional[List[ID]] = None,
    roi_origins: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> Image:
    """from_array_like



    Arguments:
        array (ArrayLike): array
        name (str): name
        origins (Optional[List[ID]], optional): origins.
        channel_views (Optional[List[PartialChannelViewInput]], optional): channelViews.
        transformation_views (Optional[List[PartialAffineTransformationViewInput]], optional): transformationViews.
        pixel_views (Optional[List[PartialPixelViewInput]], optional): pixelViews.
        rgb_views (Optional[List[PartialRGBViewInput]], optional): rgbViews.
        acquisition_views (Optional[List[PartialAcquisitionViewInput]], optional): acquisitionViews.
        timepoint_views (Optional[List[PartialTimepointViewInput]], optional): timepointViews.
        optics_views (Optional[List[PartialOpticsViewInput]], optional): opticsViews.
        specimen_views (Optional[List[PartialSpecimenViewInput]], optional): specimenViews.
        scale_views (Optional[List[PartialScaleViewInput]], optional): scaleViews.
        tags (Optional[List[str]], optional): tags.
        file_origins (Optional[List[ID]], optional): fileOrigins.
        roi_origins (Optional[List[ID]], optional): roiOrigins.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image"""
    return execute(
        From_array_likeMutation,
        {
            "array": array,
            "name": name,
            "origins": origins,
            "channelViews": channel_views,
            "transformationViews": transformation_views,
            "pixelViews": pixel_views,
            "rgbViews": rgb_views,
            "acquisitionViews": acquisition_views,
            "timepointViews": timepoint_views,
            "opticsViews": optics_views,
            "specimenViews": specimen_views,
            "scaleViews": scale_views,
            "tags": tags,
            "fileOrigins": file_origins,
            "roiOrigins": roi_origins,
        },
        rath=rath,
    ).from_array_like


async def arequest_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestUpload


     requestUpload: Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        key (str): key
        datalayer (str): datalayer
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials"""
    return (
        await aexecute(
            RequestUploadMutation, {"key": key, "datalayer": datalayer}, rath=rath
        )
    ).request_upload


def request_upload(
    key: str, datalayer: str, rath: Optional[MikroNextRath] = None
) -> Credentials:
    """RequestUpload


     requestUpload: Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        key (str): key
        datalayer (str): datalayer
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Credentials"""
    return execute(
        RequestUploadMutation, {"key": key, "datalayer": datalayer}, rath=rath
    ).request_upload


async def arequest_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestAccess


     requestAccess: Temporary Credentials for a file download that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        store (ID): store
        duration (Optional[int], optional): duration.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials"""
    return (
        await aexecute(
            RequestAccessMutation, {"store": store, "duration": duration}, rath=rath
        )
    ).request_access


def request_access(
    store: ID, duration: Optional[int] = None, rath: Optional[MikroNextRath] = None
) -> AccessCredentials:
    """RequestAccess


     requestAccess: Temporary Credentials for a file download that can be used by a Client (e.g. in a python datalayer)


    Arguments:
        store (ID): store
        duration (Optional[int], optional): duration.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        AccessCredentials"""
    return execute(
        RequestAccessMutation, {"store": store, "duration": duration}, rath=rath
    ).request_access


async def acreate_entity(
    kind: ID,
    group: Optional[ID] = None,
    name: Optional[str] = None,
    parent: Optional[ID] = None,
    instance_kind: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> Entity:
    """CreateEntity



    Arguments:
        kind (ID): kind
        group (Optional[ID], optional): group.
        name (Optional[str], optional): name.
        parent (Optional[ID], optional): parent.
        instance_kind (Optional[str], optional): instance_kind.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Entity"""
    return (
        await aexecute(
            CreateEntityMutation,
            {
                "kind": kind,
                "group": group,
                "name": name,
                "parent": parent,
                "instance_kind": instance_kind,
            },
            rath=rath,
        )
    ).create_entity


def create_entity(
    kind: ID,
    group: Optional[ID] = None,
    name: Optional[str] = None,
    parent: Optional[ID] = None,
    instance_kind: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> Entity:
    """CreateEntity



    Arguments:
        kind (ID): kind
        group (Optional[ID], optional): group.
        name (Optional[str], optional): name.
        parent (Optional[ID], optional): parent.
        instance_kind (Optional[str], optional): instance_kind.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Entity"""
    return execute(
        CreateEntityMutation,
        {
            "kind": kind,
            "group": group,
            "name": name,
            "parent": parent,
            "instance_kind": instance_kind,
        },
        rath=rath,
    ).create_entity


async def acreate_era(
    name: str, begin: Optional[datetime] = None, rath: Optional[MikroNextRath] = None
) -> CreateEraMutationCreateera:
    """CreateEra



    Arguments:
        name (str): name
        begin (Optional[datetime], optional): begin.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateEraMutationCreateera"""
    return (
        await aexecute(CreateEraMutation, {"name": name, "begin": begin}, rath=rath)
    ).create_era


def create_era(
    name: str, begin: Optional[datetime] = None, rath: Optional[MikroNextRath] = None
) -> CreateEraMutationCreateera:
    """CreateEra



    Arguments:
        name (str): name
        begin (Optional[datetime], optional): begin.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateEraMutationCreateera"""
    return execute(
        CreateEraMutation, {"name": name, "begin": begin}, rath=rath
    ).create_era


async def acreate_protocol(
    name: str,
    experiment: ID,
    description: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> Protocol:
    """CreateProtocol



    Arguments:
        name (str): name
        experiment (ID): experiment
        description (Optional[str], optional): description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Protocol"""
    return (
        await aexecute(
            CreateProtocolMutation,
            {"name": name, "experiment": experiment, "description": description},
            rath=rath,
        )
    ).create_protocol


def create_protocol(
    name: str,
    experiment: ID,
    description: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> Protocol:
    """CreateProtocol



    Arguments:
        name (str): name
        experiment (ID): experiment
        description (Optional[str], optional): description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Protocol"""
    return execute(
        CreateProtocolMutation,
        {"name": name, "experiment": experiment, "description": description},
        rath=rath,
    ).create_protocol


async def acreate_snapshot(
    image: ID, file: Upload, rath: Optional[MikroNextRath] = None
) -> Snapshot:
    """CreateSnapshot



    Arguments:
        image (ID): image
        file (Upload): file
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Snapshot"""
    return (
        await aexecute(
            CreateSnapshotMutation, {"image": image, "file": file}, rath=rath
        )
    ).create_snapshot


def create_snapshot(
    image: ID, file: Upload, rath: Optional[MikroNextRath] = None
) -> Snapshot:
    """CreateSnapshot



    Arguments:
        image (ID): image
        file (Upload): file
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Snapshot"""
    return execute(
        CreateSnapshotMutation, {"image": image, "file": file}, rath=rath
    ).create_snapshot


async def acreate_rgb_view(
    image: ID,
    context: ID,
    gamma: Optional[float] = None,
    contrast_limit_max: Optional[float] = None,
    contrast_limit_min: Optional[float] = None,
    rescale: Optional[bool] = None,
    active: Optional[bool] = None,
    color_map: Optional[ColorMap] = None,
    base_color: Optional[List[float]] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateRgbViewMutationCreatergbview:
    """CreateRgbView



    Arguments:
        image (ID): image
        context (ID): context
        gamma (Optional[float], optional): gamma.
        contrast_limit_max (Optional[float], optional): contrastLimitMax.
        contrast_limit_min (Optional[float], optional): contrastLimitMin.
        rescale (Optional[bool], optional): rescale.
        active (Optional[bool], optional): active.
        color_map (Optional[ColorMap], optional): colorMap.
        base_color (Optional[List[float]], optional): baseColor.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateRgbViewMutationCreatergbview"""
    return (
        await aexecute(
            CreateRgbViewMutation,
            {
                "image": image,
                "context": context,
                "gamma": gamma,
                "contrastLimitMax": contrast_limit_max,
                "contrastLimitMin": contrast_limit_min,
                "rescale": rescale,
                "active": active,
                "colorMap": color_map,
                "baseColor": base_color,
            },
            rath=rath,
        )
    ).create_rgb_view


def create_rgb_view(
    image: ID,
    context: ID,
    gamma: Optional[float] = None,
    contrast_limit_max: Optional[float] = None,
    contrast_limit_min: Optional[float] = None,
    rescale: Optional[bool] = None,
    active: Optional[bool] = None,
    color_map: Optional[ColorMap] = None,
    base_color: Optional[List[float]] = None,
    rath: Optional[MikroNextRath] = None,
) -> CreateRgbViewMutationCreatergbview:
    """CreateRgbView



    Arguments:
        image (ID): image
        context (ID): context
        gamma (Optional[float], optional): gamma.
        contrast_limit_max (Optional[float], optional): contrastLimitMax.
        contrast_limit_min (Optional[float], optional): contrastLimitMin.
        rescale (Optional[bool], optional): rescale.
        active (Optional[bool], optional): active.
        color_map (Optional[ColorMap], optional): colorMap.
        base_color (Optional[List[float]], optional): baseColor.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateRgbViewMutationCreatergbview"""
    return execute(
        CreateRgbViewMutation,
        {
            "image": image,
            "context": context,
            "gamma": gamma,
            "contrastLimitMax": contrast_limit_max,
            "contrastLimitMin": contrast_limit_min,
            "rescale": rescale,
            "active": active,
            "colorMap": color_map,
            "baseColor": base_color,
        },
        rath=rath,
    ).create_rgb_view


async def acreate_ontology(
    name: str,
    purl: Optional[str] = None,
    description: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> Ontology:
    """CreateOntology



    Arguments:
        name (str): name
        purl (Optional[str], optional): purl.
        description (Optional[str], optional): description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Ontology"""
    return (
        await aexecute(
            CreateOntologyMutation,
            {"name": name, "purl": purl, "description": description},
            rath=rath,
        )
    ).create_ontology


def create_ontology(
    name: str,
    purl: Optional[str] = None,
    description: Optional[str] = None,
    rath: Optional[MikroNextRath] = None,
) -> Ontology:
    """CreateOntology



    Arguments:
        name (str): name
        purl (Optional[str], optional): purl.
        description (Optional[str], optional): description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Ontology"""
    return execute(
        CreateOntologyMutation,
        {"name": name, "purl": purl, "description": description},
        rath=rath,
    ).create_ontology


async def acreate_rgb_context(
    input: CreateRGBContextInput, rath: Optional[MikroNextRath] = None
) -> RGBContext:
    """CreateRGBContext



    Arguments:
        input (CreateRGBContextInput): input
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext"""
    return (
        await aexecute(CreateRGBContextMutation, {"input": input}, rath=rath)
    ).create_rgb_context


def create_rgb_context(
    input: CreateRGBContextInput, rath: Optional[MikroNextRath] = None
) -> RGBContext:
    """CreateRGBContext



    Arguments:
        input (CreateRGBContextInput): input
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext"""
    return execute(
        CreateRGBContextMutation, {"input": input}, rath=rath
    ).create_rgb_context


async def aupdate_rgb_context(
    input: UpdateRGBContextInput, rath: Optional[MikroNextRath] = None
) -> RGBContext:
    """UpdateRGBContext



    Arguments:
        input (UpdateRGBContextInput): input
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext"""
    return (
        await aexecute(UpdateRGBContextMutation, {"input": input}, rath=rath)
    ).update_rgb_context


def update_rgb_context(
    input: UpdateRGBContextInput, rath: Optional[MikroNextRath] = None
) -> RGBContext:
    """UpdateRGBContext



    Arguments:
        input (UpdateRGBContextInput): input
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext"""
    return execute(
        UpdateRGBContextMutation, {"input": input}, rath=rath
    ).update_rgb_context


async def acreate_view_collection(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateViewCollectionMutationCreateviewcollection:
    """CreateViewCollection



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateViewCollectionMutationCreateviewcollection"""
    return (
        await aexecute(CreateViewCollectionMutation, {"name": name}, rath=rath)
    ).create_view_collection


def create_view_collection(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateViewCollectionMutationCreateviewcollection:
    """CreateViewCollection



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateViewCollectionMutationCreateviewcollection"""
    return execute(
        CreateViewCollectionMutation, {"name": name}, rath=rath
    ).create_view_collection


async def acreate_channel(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateChannelMutationCreatechannel:
    """CreateChannel



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateChannelMutationCreatechannel"""
    return (
        await aexecute(CreateChannelMutation, {"name": name}, rath=rath)
    ).create_channel


def create_channel(
    name: str, rath: Optional[MikroNextRath] = None
) -> CreateChannelMutationCreatechannel:
    """CreateChannel



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        CreateChannelMutationCreatechannel"""
    return execute(CreateChannelMutation, {"name": name}, rath=rath).create_channel


async def aensure_channel(
    name: str, rath: Optional[MikroNextRath] = None
) -> EnsureChannelMutationEnsurechannel:
    """EnsureChannel



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureChannelMutationEnsurechannel"""
    return (
        await aexecute(EnsureChannelMutation, {"name": name}, rath=rath)
    ).ensure_channel


def ensure_channel(
    name: str, rath: Optional[MikroNextRath] = None
) -> EnsureChannelMutationEnsurechannel:
    """EnsureChannel



    Arguments:
        name (str): name
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EnsureChannelMutationEnsurechannel"""
    return execute(EnsureChannelMutation, {"name": name}, rath=rath).ensure_channel


async def acreate_experiment(
    name: str, description: Optional[str] = None, rath: Optional[MikroNextRath] = None
) -> Experiment:
    """CreateExperiment



    Arguments:
        name (str): name
        description (Optional[str], optional): description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Experiment"""
    return (
        await aexecute(
            CreateExperimentMutation,
            {"name": name, "description": description},
            rath=rath,
        )
    ).create_experiment


def create_experiment(
    name: str, description: Optional[str] = None, rath: Optional[MikroNextRath] = None
) -> Experiment:
    """CreateExperiment



    Arguments:
        name (str): name
        description (Optional[str], optional): description.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Experiment"""
    return execute(
        CreateExperimentMutation, {"name": name, "description": description}, rath=rath
    ).create_experiment


async def aget_camera(id: ID, rath: Optional[MikroNextRath] = None) -> Camera:
    """GetCamera



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Camera"""
    return (await aexecute(GetCameraQuery, {"id": id}, rath=rath)).camera


def get_camera(id: ID, rath: Optional[MikroNextRath] = None) -> Camera:
    """GetCamera



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Camera"""
    return execute(GetCameraQuery, {"id": id}, rath=rath).camera


async def aget_table(id: ID, rath: Optional[MikroNextRath] = None) -> Table:
    """GetTable



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Table"""
    return (await aexecute(GetTableQuery, {"id": id}, rath=rath)).table


def get_table(id: ID, rath: Optional[MikroNextRath] = None) -> Table:
    """GetTable



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Table"""
    return execute(GetTableQuery, {"id": id}, rath=rath).table


async def aget_rendered_plot(
    id: ID, rath: Optional[MikroNextRath] = None
) -> RenderedPlot:
    """GetRenderedPlot



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RenderedPlot"""
    return (await aexecute(GetRenderedPlotQuery, {"id": id}, rath=rath)).rendered_plot


def get_rendered_plot(id: ID, rath: Optional[MikroNextRath] = None) -> RenderedPlot:
    """GetRenderedPlot



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RenderedPlot"""
    return execute(GetRenderedPlotQuery, {"id": id}, rath=rath).rendered_plot


async def alist_rendered_plots(
    rath: Optional[MikroNextRath] = None,
) -> List[ListRenderedPlot]:
    """ListRenderedPlots



    Arguments:
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[ListRenderedPlot]"""
    return (await aexecute(ListRenderedPlotsQuery, {}, rath=rath)).rendered_plots


def list_rendered_plots(rath: Optional[MikroNextRath] = None) -> List[ListRenderedPlot]:
    """ListRenderedPlots



    Arguments:
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[ListRenderedPlot]"""
    return execute(ListRenderedPlotsQuery, {}, rath=rath).rendered_plots


async def asearch_rendered_plots(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchRenderedPlotsQueryOptions]:
    """SearchRenderedPlots



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchRenderedPlotsQueryRenderedplots]"""
    return (
        await aexecute(
            SearchRenderedPlotsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_rendered_plots(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchRenderedPlotsQueryOptions]:
    """SearchRenderedPlots



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchRenderedPlotsQueryRenderedplots]"""
    return execute(
        SearchRenderedPlotsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_file(id: ID, rath: Optional[MikroNextRath] = None) -> File:
    """GetFile



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        File"""
    return (await aexecute(GetFileQuery, {"id": id}, rath=rath)).file


def get_file(id: ID, rath: Optional[MikroNextRath] = None) -> File:
    """GetFile



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        File"""
    return execute(GetFileQuery, {"id": id}, rath=rath).file


async def asearch_files(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchFilesQueryOptions]:
    """SearchFiles



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        pagination (Optional[OffsetPaginationInput], optional): pagination.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchFilesQueryFiles]"""
    return (
        await aexecute(
            SearchFilesQuery,
            {"search": search, "values": values, "pagination": pagination},
            rath=rath,
        )
    ).options


def search_files(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchFilesQueryOptions]:
    """SearchFiles



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        pagination (Optional[OffsetPaginationInput], optional): pagination.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchFilesQueryFiles]"""
    return execute(
        SearchFilesQuery,
        {"search": search, "values": values, "pagination": pagination},
        rath=rath,
    ).options


async def aget_entity_kind(id: ID, rath: Optional[MikroNextRath] = None) -> EntityKind:
    """GetEntityKind



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EntityKind"""
    return (await aexecute(GetEntityKindQuery, {"id": id}, rath=rath)).entity_kind


def get_entity_kind(id: ID, rath: Optional[MikroNextRath] = None) -> EntityKind:
    """GetEntityKind



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EntityKind"""
    return execute(GetEntityKindQuery, {"id": id}, rath=rath).entity_kind


async def asearch_entity_kind(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchEntityKindQueryOptions]:
    """SearchEntityKind



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchEntityKindQueryEntitykinds]"""
    return (
        await aexecute(
            SearchEntityKindQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_entity_kind(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchEntityKindQueryOptions]:
    """SearchEntityKind



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchEntityKindQueryEntitykinds]"""
    return execute(
        SearchEntityKindQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_stage(id: ID, rath: Optional[MikroNextRath] = None) -> Stage:
    """GetStage



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Stage"""
    return (await aexecute(GetStageQuery, {"id": id}, rath=rath)).stage


def get_stage(id: ID, rath: Optional[MikroNextRath] = None) -> Stage:
    """GetStage



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Stage"""
    return execute(GetStageQuery, {"id": id}, rath=rath).stage


async def asearch_stages(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchStagesQueryOptions]:
    """SearchStages



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        pagination (Optional[OffsetPaginationInput], optional): pagination.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchStagesQueryStages]"""
    return (
        await aexecute(
            SearchStagesQuery,
            {"search": search, "values": values, "pagination": pagination},
            rath=rath,
        )
    ).options


def search_stages(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchStagesQueryOptions]:
    """SearchStages



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        pagination (Optional[OffsetPaginationInput], optional): pagination.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchStagesQueryStages]"""
    return execute(
        SearchStagesQuery,
        {"search": search, "values": values, "pagination": pagination},
        rath=rath,
    ).options


async def aget_rois(image: ID, rath: Optional[MikroNextRath] = None) -> List[ROI]:
    """GetRois



    Arguments:
        image (ID): image
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[ROI]"""
    return (await aexecute(GetRoisQuery, {"image": image}, rath=rath)).rois


def get_rois(image: ID, rath: Optional[MikroNextRath] = None) -> List[ROI]:
    """GetRois



    Arguments:
        image (ID): image
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[ROI]"""
    return execute(GetRoisQuery, {"image": image}, rath=rath).rois


async def aget_roi(id: ID, rath: Optional[MikroNextRath] = None) -> ROI:
    """GetRoi



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ROI"""
    return (await aexecute(GetRoiQuery, {"id": id}, rath=rath)).roi


def get_roi(id: ID, rath: Optional[MikroNextRath] = None) -> ROI:
    """GetRoi



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ROI"""
    return execute(GetRoiQuery, {"id": id}, rath=rath).roi


async def aget_objective(id: ID, rath: Optional[MikroNextRath] = None) -> Objective:
    """GetObjective



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Objective"""
    return (await aexecute(GetObjectiveQuery, {"id": id}, rath=rath)).objective


def get_objective(id: ID, rath: Optional[MikroNextRath] = None) -> Objective:
    """GetObjective



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Objective"""
    return execute(GetObjectiveQuery, {"id": id}, rath=rath).objective


async def aget_protocol_step(
    id: ID, rath: Optional[MikroNextRath] = None
) -> ProtocolStep:
    """GetProtocolStep



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ProtocolStep"""
    return (await aexecute(GetProtocolStepQuery, {"id": id}, rath=rath)).protocol_step


def get_protocol_step(id: ID, rath: Optional[MikroNextRath] = None) -> ProtocolStep:
    """GetProtocolStep



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        ProtocolStep"""
    return execute(GetProtocolStepQuery, {"id": id}, rath=rath).protocol_step


async def asearch_protocol_steps(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchProtocolStepsQueryOptions]:
    """SearchProtocolSteps



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchProtocolStepsQueryProtocolsteps]"""
    return (
        await aexecute(
            SearchProtocolStepsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_protocol_steps(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchProtocolStepsQueryOptions]:
    """SearchProtocolSteps



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchProtocolStepsQueryProtocolsteps]"""
    return execute(
        SearchProtocolStepsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_dataset(id: ID, rath: Optional[MikroNextRath] = None) -> Dataset:
    """GetDataset



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Dataset"""
    return (await aexecute(GetDatasetQuery, {"id": id}, rath=rath)).dataset


def get_dataset(id: ID, rath: Optional[MikroNextRath] = None) -> Dataset:
    """GetDataset



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Dataset"""
    return execute(GetDatasetQuery, {"id": id}, rath=rath).dataset


async def aget_specimen(id: ID, rath: Optional[MikroNextRath] = None) -> Specimen:
    """GetSpecimen



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Specimen"""
    return (await aexecute(GetSpecimenQuery, {"id": id}, rath=rath)).specimen


def get_specimen(id: ID, rath: Optional[MikroNextRath] = None) -> Specimen:
    """GetSpecimen



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Specimen"""
    return execute(GetSpecimenQuery, {"id": id}, rath=rath).specimen


async def asearch_specimens(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchSpecimensQueryOptions]:
    """SearchSpecimens



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchSpecimensQuerySpecimens]"""
    return (
        await aexecute(
            SearchSpecimensQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_specimens(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchSpecimensQueryOptions]:
    """SearchSpecimens



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchSpecimensQuerySpecimens]"""
    return execute(
        SearchSpecimensQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_instrument(id: ID, rath: Optional[MikroNextRath] = None) -> Instrument:
    """GetInstrument



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Instrument"""
    return (await aexecute(GetInstrumentQuery, {"id": id}, rath=rath)).instrument


def get_instrument(id: ID, rath: Optional[MikroNextRath] = None) -> Instrument:
    """GetInstrument



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Instrument"""
    return execute(GetInstrumentQuery, {"id": id}, rath=rath).instrument


async def aget_entity_relation(
    id: ID, rath: Optional[MikroNextRath] = None
) -> EntityRelation:
    """GetEntityRelation



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EntityRelation"""
    return (
        await aexecute(GetEntityRelationQuery, {"id": id}, rath=rath)
    ).entity_relation


def get_entity_relation(id: ID, rath: Optional[MikroNextRath] = None) -> EntityRelation:
    """GetEntityRelation



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EntityRelation"""
    return execute(GetEntityRelationQuery, {"id": id}, rath=rath).entity_relation


async def asearch_entity_relations(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchEntityRelationsQueryOptions]:
    """SearchEntityRelations



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchEntityRelationsQueryEntityrelations]"""
    return (
        await aexecute(
            SearchEntityRelationsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_entity_relations(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchEntityRelationsQueryOptions]:
    """SearchEntityRelations



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchEntityRelationsQueryEntityrelations]"""
    return execute(
        SearchEntityRelationsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_image(id: ID, rath: Optional[MikroNextRath] = None) -> Image:
    """GetImage



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image"""
    return (await aexecute(GetImageQuery, {"id": id}, rath=rath)).image


def get_image(id: ID, rath: Optional[MikroNextRath] = None) -> Image:
    """GetImage



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image"""
    return execute(GetImageQuery, {"id": id}, rath=rath).image


async def aget_random_image(rath: Optional[MikroNextRath] = None) -> Image:
    """GetRandomImage



    Arguments:
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image"""
    return (await aexecute(GetRandomImageQuery, {}, rath=rath)).random_image


def get_random_image(rath: Optional[MikroNextRath] = None) -> Image:
    """GetRandomImage



    Arguments:
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Image"""
    return execute(GetRandomImageQuery, {}, rath=rath).random_image


async def asearch_images(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchImagesQueryOptions]:
    """SearchImages



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchImagesQueryImages]"""
    return (
        await aexecute(
            SearchImagesQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_images(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchImagesQueryOptions]:
    """SearchImages



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchImagesQueryImages]"""
    return execute(
        SearchImagesQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aimages(
    filter: Optional[ImageFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[Image]:
    """Images



    Arguments:
        filter (Optional[ImageFilter], optional): filter.
        pagination (Optional[OffsetPaginationInput], optional): pagination.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[Image]"""
    return (
        await aexecute(
            ImagesQuery, {"filter": filter, "pagination": pagination}, rath=rath
        )
    ).images


def images(
    filter: Optional[ImageFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[Image]:
    """Images



    Arguments:
        filter (Optional[ImageFilter], optional): filter.
        pagination (Optional[OffsetPaginationInput], optional): pagination.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[Image]"""
    return execute(
        ImagesQuery, {"filter": filter, "pagination": pagination}, rath=rath
    ).images


async def aget_entity(id: ID, rath: Optional[MikroNextRath] = None) -> Entity:
    """GetEntity



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Entity"""
    return (await aexecute(GetEntityQuery, {"id": id}, rath=rath)).entity


def get_entity(id: ID, rath: Optional[MikroNextRath] = None) -> Entity:
    """GetEntity



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Entity"""
    return execute(GetEntityQuery, {"id": id}, rath=rath).entity


async def asearch_entities(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchEntitiesQueryOptions]:
    """SearchEntities



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchEntitiesQueryEntities]"""
    return (
        await aexecute(
            SearchEntitiesQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_entities(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchEntitiesQueryOptions]:
    """SearchEntities



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchEntitiesQueryEntities]"""
    return execute(
        SearchEntitiesQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_protocol(id: ID, rath: Optional[MikroNextRath] = None) -> Protocol:
    """GetProtocol



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Protocol"""
    return (await aexecute(GetProtocolQuery, {"id": id}, rath=rath)).protocol


def get_protocol(id: ID, rath: Optional[MikroNextRath] = None) -> Protocol:
    """GetProtocol



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Protocol"""
    return execute(GetProtocolQuery, {"id": id}, rath=rath).protocol


async def asearch_protocols(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchProtocolsQueryOptions]:
    """SearchProtocols



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchProtocolsQueryProtocols]"""
    return (
        await aexecute(
            SearchProtocolsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_protocols(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchProtocolsQueryOptions]:
    """SearchProtocols



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchProtocolsQueryProtocols]"""
    return execute(
        SearchProtocolsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_snapshot(id: ID, rath: Optional[MikroNextRath] = None) -> Snapshot:
    """GetSnapshot



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Snapshot"""
    return (await aexecute(GetSnapshotQuery, {"id": id}, rath=rath)).snapshot


def get_snapshot(id: ID, rath: Optional[MikroNextRath] = None) -> Snapshot:
    """GetSnapshot



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Snapshot"""
    return execute(GetSnapshotQuery, {"id": id}, rath=rath).snapshot


async def asearch_snapshots(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchSnapshotsQueryOptions]:
    """SearchSnapshots



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchSnapshotsQuerySnapshots]"""
    return (
        await aexecute(
            SearchSnapshotsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_snapshots(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchSnapshotsQueryOptions]:
    """SearchSnapshots



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchSnapshotsQuerySnapshots]"""
    return execute(
        SearchSnapshotsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_entity_relation_kind(
    id: ID, rath: Optional[MikroNextRath] = None
) -> EntityRelationKind:
    """GetEntityRelationKind



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EntityRelationKind"""
    return (
        await aexecute(GetEntityRelationKindQuery, {"id": id}, rath=rath)
    ).entity_relation_kind


def get_entity_relation_kind(
    id: ID, rath: Optional[MikroNextRath] = None
) -> EntityRelationKind:
    """GetEntityRelationKind



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        EntityRelationKind"""
    return execute(
        GetEntityRelationKindQuery, {"id": id}, rath=rath
    ).entity_relation_kind


async def asearch_entity_relation_kinds(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchEntityRelationKindsQueryOptions]:
    """SearchEntityRelationKinds



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchEntityRelationKindsQueryEntityrelationkinds]"""
    return (
        await aexecute(
            SearchEntityRelationKindsQuery,
            {"search": search, "values": values},
            rath=rath,
        )
    ).options


def search_entity_relation_kinds(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchEntityRelationKindsQueryOptions]:
    """SearchEntityRelationKinds



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchEntityRelationKindsQueryEntityrelationkinds]"""
    return execute(
        SearchEntityRelationKindsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_ontology(id: ID, rath: Optional[MikroNextRath] = None) -> Ontology:
    """GetOntology



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Ontology"""
    return (await aexecute(GetOntologyQuery, {"id": id}, rath=rath)).ontology


def get_ontology(id: ID, rath: Optional[MikroNextRath] = None) -> Ontology:
    """GetOntology



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        Ontology"""
    return execute(GetOntologyQuery, {"id": id}, rath=rath).ontology


async def asearch_ontologies(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchOntologiesQueryOptions]:
    """SearchOntologies



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchOntologiesQueryOntologies]"""
    return (
        await aexecute(
            SearchOntologiesQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def search_ontologies(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[MikroNextRath] = None,
) -> List[SearchOntologiesQueryOptions]:
    """SearchOntologies



    Arguments:
        search (Optional[str], optional): search.
        values (Optional[List[ID]], optional): values.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        List[SearchOntologiesQueryOntologies]"""
    return execute(
        SearchOntologiesQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aget_rgb_context(id: ID, rath: Optional[MikroNextRath] = None) -> RGBContext:
    """GetRGBContext



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext"""
    return (await aexecute(GetRGBContextQuery, {"id": id}, rath=rath)).rgbcontext


def get_rgb_context(id: ID, rath: Optional[MikroNextRath] = None) -> RGBContext:
    """GetRGBContext



    Arguments:
        id (ID): id
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        RGBContext"""
    return execute(GetRGBContextQuery, {"id": id}, rath=rath).rgbcontext


async def awatch_files(
    dataset: Optional[ID] = None, rath: Optional[MikroNextRath] = None
) -> AsyncIterator[WatchFilesSubscriptionFiles]:
    """WatchFiles



    Arguments:
        dataset (Optional[ID], optional): dataset.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        WatchFilesSubscriptionFiles"""
    async for event in asubscribe(
        WatchFilesSubscription, {"dataset": dataset}, rath=rath
    ):
        yield event.files


def watch_files(
    dataset: Optional[ID] = None, rath: Optional[MikroNextRath] = None
) -> Iterator[WatchFilesSubscriptionFiles]:
    """WatchFiles



    Arguments:
        dataset (Optional[ID], optional): dataset.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        WatchFilesSubscriptionFiles"""
    for event in subscribe(WatchFilesSubscription, {"dataset": dataset}, rath=rath):
        yield event.files


async def awatch_images(
    dataset: Optional[ID] = None, rath: Optional[MikroNextRath] = None
) -> AsyncIterator[WatchImagesSubscriptionImages]:
    """WatchImages



    Arguments:
        dataset (Optional[ID], optional): dataset.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        WatchImagesSubscriptionImages"""
    async for event in asubscribe(
        WatchImagesSubscription, {"dataset": dataset}, rath=rath
    ):
        yield event.images


def watch_images(
    dataset: Optional[ID] = None, rath: Optional[MikroNextRath] = None
) -> Iterator[WatchImagesSubscriptionImages]:
    """WatchImages



    Arguments:
        dataset (Optional[ID], optional): dataset.
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        WatchImagesSubscriptionImages"""
    for event in subscribe(WatchImagesSubscription, {"dataset": dataset}, rath=rath):
        yield event.images


async def awatch_rois(
    image: ID, rath: Optional[MikroNextRath] = None
) -> AsyncIterator[WatchRoisSubscriptionRois]:
    """WatchRois



    Arguments:
        image (ID): image
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        WatchRoisSubscriptionRois"""
    async for event in asubscribe(WatchRoisSubscription, {"image": image}, rath=rath):
        yield event.rois


def watch_rois(
    image: ID, rath: Optional[MikroNextRath] = None
) -> Iterator[WatchRoisSubscriptionRois]:
    """WatchRois



    Arguments:
        image (ID): image
        rath (mikro_next.rath.MikroNextRath, optional): The mikro rath client

    Returns:
        WatchRoisSubscriptionRois"""
    for event in subscribe(WatchRoisSubscription, {"image": image}, rath=rath):
        yield event.rois


AffineTransformationViewFilter.update_forward_refs()
ChannelView.update_forward_refs()
DatasetFilter.update_forward_refs()
EraFilter.update_forward_refs()
File.update_forward_refs()
Image.update_forward_refs()
ImageDerivedscaleviewsImage.update_forward_refs()
ImageFilter.update_forward_refs()
PartialPixelViewInput.update_forward_refs()
ProvenanceFilter.update_forward_refs()
RGBContextImage.update_forward_refs()
StageFilter.update_forward_refs()
Table.update_forward_refs()
TimepointView.update_forward_refs()
TimepointViewFilter.update_forward_refs()
TreeInput.update_forward_refs()
TreeNodeInput.update_forward_refs()
ZarrStoreFilter.update_forward_refs()
