""" This module contains the STAC specification version 1.0.0 implemented 
as pydantic models. The STAC specification documentation can be found at
https://github.com/radiantearth/stac-spec/blob/master/collection-spec/collection-spec.md.
The optional fields 'stac_version', 'summaries' and 'assets' are not implemented 
as they are not required for the ML-STAC specification.  The fields are 
organized into required and optional fields.  The required fields are 
those that are required by the STAC specification in order to create a 
valid STAC Collection.
"""

import re
from typing import Any, Dict, List, Literal, Optional

import pydantic

# Required fields -------------------------------------------------------------


class Type(pydantic.BaseModel):
    """REQUIRED. Must be set to Collection to be a valid Collection."""

    field: Literal["Collection"]


class Version(pydantic.BaseModel):
    """REQUIRED. In the ML-STAC specification, the STAC version is
    fixed to 1.0.0.

    Fields:
        stac_version (Literal["1.0.0"]): The version of the STAC
        specification.
    """

    field: Literal["1.0.0"]


class Id(pydantic.BaseModel):
    """REQUIRED. It is important that Collection identifiers
    are unique across the provider. And providers should strive as much as
    possible to make their Collection ids 'globally' unique, prefixing any
    common information with a unique string. This could be the provider's
    name if it is a fairly unique name, or their name combined with the domain
    they operate in.
    """

    field: str

    @pydantic.field_validator("field")
    def check_id(cls, v):
        if len(v) < 1:
            raise ValueError("Must be at least 1 characters")
        return v


class Description(pydantic.BaseModel):
    """REQUIRED. Detailed multi-line description to fully explain the Collection.
    CommonMark 0.29 syntax MAY be used for rich text representation.
    """

    field: str

    @pydantic.field_validator("field")
    def check_id(cls, v):
        if len(v) < 1:
            raise ValueError("Must be at least 1 characters")
        return v


class License(pydantic.BaseModel):
    """REQUIRED. Collection's license(s), either a SPDX License identifier, various
    if multiple licenses apply or proprietary for all other cases.
    """

    field: str

    @pydantic.field_validator("field")
    def check_license(cls, v):
        regex_exp = re.compile("^[\\w\\-\\.\\+]+$")
        if not re.match(regex_exp, v):
            raise ValueError("Must be a valid SPDX License identifier")
        return v


class SpatialExtent(pydantic.BaseModel):
    """REQUIRED. The object describes the spatial extents of the Collection.
    bbox: Each outer array element can be a separate spatial extent describing
    the bounding boxes of the assets represented by this Collection using either
    2D or 3D geometries.

    The first bounding box always describes the overall spatial extent of the data.
    All subsequent bounding boxes can be used to provide a more precise description
    of the extent and identify clusters of data. Clients only interested in the overall
    spatial extent will only need to access the first item in each array. It is recommended
    to only use multiple bounding boxes if a union of them would then include a large uncovered
    area (e.g. the union of Germany and Chile).

    The length of the inner array must be 2*n where n is the number of dimensions. The array
    contains all axes of the southwesterly most extent followed by all axes of the
    northeasterly most extent specified in Longitude/Latitude or Longitude/Latitude/Elevation
    based on WGS 84. When using 3D geometries, the elevation of the southwesterly most extent
    is the minimum depth/height in meters and the elevation of the northeasterly most extent
    is the maximum.

    The coordinate reference system of the values is WGS 84 longitude/latitude. Example that
    covers the whole Earth: [[-180.0, -90.0, 180.0, 90.0]]. Example that covers the whole
    earth with a depth of 100 meters to a height of 150 meters: [[-180.0, -90.0, -100.0,
    180.0, 90.0, 150.0]].
    """

    bbox: List[List[float]]

    @pydantic.field_validator("bbox")
    def check_spatial_extent(cls, v):
        for item in v:
            for value in item:
                if value < -180 or value > 180:
                    raise ValueError("Longitude must be between -180 and 180")
        return v

    @pydantic.field_validator("bbox")
    def check_spatial_length(cls, v):
        if len(v) < 1:
            raise ValueError("Must be at least 1 spatial extent")
        return v

    @pydantic.field_validator("bbox")
    def check_spatial_dimension(cls, v):
        for item in v:
            if not (len(item) == 4 or len(item) == 6):
                raise ValueError("Must be 2D or 3D geometries")
        return v


class TemporalExtent(pydantic.BaseModel):
    """REQUIRED. The object describes the temporal extents of the Collection. interval: Each outer array
    element can be a separate temporal extent. The first time interval always describes the
    overall temporal extent of the data. All subsequent time intervals can be used to provide a
    more precise description of the extent and identify clusters of data. Clients only interested
    in the overall extent will only need to access the first item in each array. It is recommended
    to only use multiple temporal extents if a union of them would then include a large uncovered
    time span (e.g. only having data for the years 2000, 2010 and 2020).

    Each inner array consists of exactly two elements, either a timestamp or null.

    Timestamps consist of a date and time in UTC and MUST be formatted according to RFC 3339,
    section 5.6. The temporal reference system is the Gregorian calendar.

    Open date ranges are supported by setting the start and/or the end time to null. Example
    for data from the beginning of 2019 until now: [["2019-01-01T00:00:00Z", null]]. It is recommended
    to provide at least a rough guideline on the temporal extent and thus it's not recommended to
    set both start and end time to null. Nevertheless, this is possible if there's a strong use case
    for an open date range to both sides.
    """

    interval: List[List[Optional[str]]]

    @pydantic.field_validator("interval")
    def check_temporal_extent(cls, v):
        if v[0][0] is None and v[0][1] is None:
            raise ValueError("Both start and end time cannot be None")
        return v

    @pydantic.field_validator("interval")
    def check_temporal_length(cls, v):
        if len(v) < 1:
            raise ValueError("Must be at least 1 temporal extent")
        return v

    @pydantic.field_validator("interval")
    def check_temporal_dimension(cls, v):
        for item in v:
            if not (len(item) == 2):
                raise ValueError("Must be a length of 2")
        return v

    @pydantic.field_validator("interval")
    def check_temporal_regex(cls, v):
        regex_exp = re.compile("(\\+00:00|Z)$")
        for item in v:
            for value in item:
                if value is not None:
                    if not regex_exp.search(value):
                        raise ValueError("Must be a valid RFC 3339 timestamp")
        return v


class Extent(pydantic.BaseModel):
    """REQUIRED. The object describes the spatio-temporal extents of the Collection.
    Both spatial and temporal extents are required to be specified.
    """

    spatial: SpatialExtent
    temporal: TemporalExtent


class Link(pydantic.BaseModel):
    """This object describes a relationship with another entity. Data
    providers are advised to be liberal with links. For a full discussion of the
    situations where relative and absolute links are recommended see the 'Use of links'
    section of the STAC best practices.
    https://github.com/radiantearth/stac-spec/blob/master/best-practices.md#use-of-links
    """

    href: str
    rel: str
    type: Optional[str] = None
    title: Optional[str] = None


class Links(pydantic.BaseModel):
    """REQUIRED. A list of links related to this Collection. The relationships
    of the links are defined by the link object with the relation type.
    """

    field: List[dict]


# Optional fields -------------------------------------------------------------
class Title(pydantic.BaseModel):
    """OPTIONAL: A short descriptive one-line title for the Collection."""

    field: str


class Keywords(pydantic.BaseModel):
    """OPTIONAL: A list of keywords describing the Collection."""

    field: List[str]


class Provider(pydantic.BaseModel):
    """A STAC required field.  A provider is any of the
    organizations that captures or processes the content
    of the Collection and therefore influences the data
    offered by this Collection. May also include information
    about the final storage provider hosting the data.

    Fields:
        name (str):  REQUIRED. The name of the organization or the individual
        description (str):  Multi-line description to add further provider
            information such as processing details for processors and
            producers, hosting details for hosts or basic contact information.
            CommonMark 0.29 syntax MAY be used for rich text representation.
        roles (List[Literal["licensor", "producer", "processor", "host"]]):
            Roles of the provider.
        url (str):  A URL to a web page with more information about the
            provider.
    """

    name: str
    description: Optional[str] = None
    roles: Optional[List[Literal["licensor", "producer", "processor", "host"]]] = None
    url: Optional[str] = None


class Providers(pydantic.BaseModel):
    """A STAC required field. A list of providers, which may include
    all organizations capturing or processing the data or the hosting
    provider. Providers should be listed in chronological order with
    the most recent provider being the last element of the list. See
    the STAC Provider Extension for more information.
    """

    field: List[Provider]


class Assets(pydantic.BaseModel):
    """OPTIONAL. A dictionary of asset objects that can
    be downloaded.
    """

    href: str
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    roles: Optional[List[str]] = None


class ItemAsset(pydantic.BaseModel):
    """OPTIONAL. A dictionary of asset objects that can
    be downloaded.
    """

    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    roles: Optional[List[str]] = None


class STACCollection(pydantic.BaseModel):
    """A STAC required field. The object describes the spatio-temporal
    extents of the Collection. Both spatial and temporal extents are
    required to be specified.
    """

    type: str = Type(field="Collection").field
    stac_version: str = Version(field="1.0.0").field
    stac_extensions: Optional[List[str]] = None

    id: str
    description: str
    license: str
    extent: Extent
    links: Optional[List[Link]] = [
        Link(
            rel="self",
            href="collection.json",
            type="application/json",
            title="An ML-STAC Collection JSON file",
        )
    ]
    item_assets: Optional[Dict[str, ItemAsset]] = {
        "collection": ItemAsset(
            title="An ML-STAC Item JSON file",
            type="application/json",
            roles=["mlstac-collection"],
        ),
        "data": ItemAsset(
            title="A collection of .mls files",
            type="application/mls; profile=cloud-optimized",
            roles=["data"],
        ),
        "metadata": ItemAsset(
            title="A collection of .parquet files",
            type="application/parquet",
            roles=["metadata"],
        ),
    }

    # Optional STAC fields -------------------------------
    title: Optional[str] = None
    keywords: Optional[List[str]] = None
    providers: Optional[Providers] = None
    summaries: Optional[Any] = None
    assets: Optional[Dict[str, Assets]] = None
