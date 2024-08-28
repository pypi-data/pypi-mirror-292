"""Generate Raindrop Trace path using NLDI and user-defined point."""
from typing import Any
from typing import Tuple
from typing import Union

import geojson
from shapely.geometry import LineString
from shapely.geometry import Point

from nldi_flowtools.utils import check_coords
from nldi_flowtools.utils import get_coordsys
from nldi_flowtools.utils import get_facgrid
from nldi_flowtools.utils import get_flowgrid
from nldi_flowtools.utils import get_local_catchment
from nldi_flowtools.utils import get_local_flowline
from nldi_flowtools.utils import get_on_flowline
from nldi_flowtools.utils import get_reach_measure
from nldi_flowtools.utils import get_row_column
from nldi_flowtools.utils import JsonFeatureCollectionType
from nldi_flowtools.utils import project_point
from nldi_flowtools.utils import split_flowline
from nldi_flowtools.utils import trace_downhill
from nldi_flowtools.utils import transform_geom


class Flowtrace:
    """Trace downhill from a point to a stream.

    Given an longitude and latitude coordinate pair, the flow path will be trace
    downhill until it intersects a stream.
    This NHD stream can be cut at this point of intersection. With the
    third parameter, the user can specify whether they want the downstream or upstream
    portion of this stream, or its entire geometry. The flowpath from the query point
    to the stream will be returned as the second feature in the output.

    Args:
        x (float): Longitude coordinate as a float
        y (float): Latitude coordiante as a float
        direction (str): Either 'down', 'up' or 'none'

    Returns:
        A GeoJSON FeatureCollection containing two features; the first is the NHD stream segment
        and the second is the flowtrace path.
    """

    def __init__(self, x: float, y: float, direction: str) -> None:
        """Initialize Flowtrace."""
        self.x = x
        self.y = y
        self.direction = direction

        # outputs
        self.raindropPath: JsonFeatureCollectionType
        self.nhdFlowline: JsonFeatureCollectionType
        self.streamInfo: dict[str, Union[Tuple[Any, Any], str, float, None]]
        self.upstreamFlowline: JsonFeatureCollectionType
        self.downstreamFlowline: JsonFeatureCollectionType

        # kick off
        self.run()

    def serialize(self) -> geojson.feature.FeatureCollection:  # noqa C901
        """Convert returns to GeoJSON to be exported."""
        if self.direction == "up":
            nhd_feature = geojson.Feature(
                geometry=self.upstreamFlowline,
                id="upstreamFlowline",
                properties=self.streamInfo,
            )
            flowtrace_feature = geojson.Feature(
                geometry=self.raindropPath, id="raindropPath"
            )

            return geojson.FeatureCollection([nhd_feature, flowtrace_feature])

        if self.direction == "down":
            nhd_feature = geojson.Feature(
                geometry=self.downstreamFlowline,
                id="downstreamFlowline",
                properties=self.streamInfo,
            )
            flowtrace_feature = geojson.Feature(
                geometry=self.raindropPath, id="raindropPath"
            )

            return geojson.FeatureCollection([nhd_feature, flowtrace_feature])

        if self.direction == "none":
            nhd_feature = geojson.Feature(
                geometry=self.nhdFlowline,
                id="nhdFlowline",
                properties=self.streamInfo,
            )
            flowtrace_feature = geojson.Feature(
                geometry=self.raindropPath, id="raindropPath"
            )

            return geojson.FeatureCollection([nhd_feature, flowtrace_feature])

    # main functions
    def run(self) -> None:  # noqa C901
        """Run Flowtrace module."""
        # Fetch the NHD catchment and flowline
        check_coords(self.x, self.y)
        transform_to_raster, transform_to_wgs84 = get_coordsys()
        catchment_id, catchment_geom = get_local_catchment(self.x, self.y)
        projected_catchment_geom = transform_geom(transform_to_raster, catchment_geom)
        flowline_json, flowline_geom = get_local_flowline(catchment_id)
        projected_flowline_geom = transform_geom(transform_to_raster, flowline_geom)
        projected_xy = project_point(self.x, self.y, transform_to_raster)

        # Open the flow direction and flow accumulation grids
        flw, fdr_profile = get_flowgrid(projected_catchment_geom)
        fac, fac_profile = get_facgrid(projected_catchment_geom)

        # Find the raster cell that the query point fall within
        start_row, start_col = get_row_column(projected_xy, fdr_profile["transform"])

        # Is that point on an NHD flowline?
        on_flowline = get_on_flowline(
            start_row, start_col, projected_flowline_geom, fdr_profile["transform"], fac
        )
        # Trace from the point to the NHD flowline (this will always run and return a flowpath)
        flowpath_coords = trace_downhill(
            on_flowline,
            projected_xy,
            fdr_profile["transform"],
            flw,
            fac,
            projected_flowline_geom,
        )

        # The intersection point is the last point on the raindrop path, project back to WGS84
        raindrop_geom = transform_geom(transform_to_wgs84, LineString(flowpath_coords))
        raindrop_path = raindrop_geom.__geo_interface__
        intersection_point_geom = Point(raindrop_path["coordinates"][-1])

        # Outputs
        self.raindropPath = raindrop_path

        self.streamInfo = get_reach_measure(
            intersection_point_geom, flowline_json, raindrop_geom
        )

        if self.direction == "none":
            self.nhdFlowline = flowline_geom.__geo_interface__

        else:
            upstream_geom, downstream_geom = split_flowline(
                intersection_point_geom, flowline_geom
            )

            if self.direction == "up":
                self.upstreamFlowline = upstream_geom.__geo_interface__

            if self.direction == "down":
                self.downstreamFlowline = downstream_geom.__geo_interface__
