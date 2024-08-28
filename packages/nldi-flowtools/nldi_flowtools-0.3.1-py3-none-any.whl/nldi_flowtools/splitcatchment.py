"""Delineate drainage basin using NLDI and user-defined point."""
import geojson

from nldi_flowtools.utils import check_coords
from nldi_flowtools.utils import get_coordsys
from nldi_flowtools.utils import get_facgrid
from nldi_flowtools.utils import get_flowgrid
from nldi_flowtools.utils import get_local_catchment
from nldi_flowtools.utils import get_local_flowline
from nldi_flowtools.utils import get_on_flowline
from nldi_flowtools.utils import get_row_column
from nldi_flowtools.utils import get_total_basin
from nldi_flowtools.utils import get_upstream_basin
from nldi_flowtools.utils import JsonFeatureCollectionType
from nldi_flowtools.utils import project_point
from nldi_flowtools.utils import split_catchment
from nldi_flowtools.utils import transform_geom


class SplitCatchment:
    """Define inputs and outputs for the main SplitCatchment class."""

    def __init__(self: "SplitCatchment", x: float, y: float, upstream: bool) -> None:
        """Initialize Splitcatchment class."""
        self.x = x
        self.y = y
        self.catchmentIdentifier: str
        self.onFlowline: bool
        self.upstream = upstream

        # outputs
        self.catchment: JsonFeatureCollectionType
        self.splitCatchment: JsonFeatureCollectionType
        self.drainageBasin: JsonFeatureCollectionType

        # kick off
        self.run()

    def serialize(self) -> geojson.feature.FeatureCollection:
        """Convert returns to GeoJSON to be exported."""
        # If upstream == False, only return the local catchment
        # and the splitcatchment geometries
        if self.upstream is False:
            nhd_feature = geojson.Feature(
                geometry=self.catchment,
                id="catchment",
                properties={"catchmentID": self.catchmentIdentifier},
            )
            split_feature = geojson.Feature(
                geometry=self.splitCatchment, id="splitCatchment"
            )

            return geojson.FeatureCollection([nhd_feature, split_feature])

        # If upstream == True and the clickpoint is on a NHD FLowline,
        # return the local catchment and the drainage basin
        # (splitcatchment merged with all upstream basins)
        elif self.upstream is True and self.onFlowline is True:
            nhd_feature = geojson.Feature(
                geometry=self.catchment,
                id="catchment",
                properties={"catchmentID": self.catchmentIdentifier},
            )
            split_feature = geojson.Feature(
                geometry=self.drainageBasin, id="drainageBasin"
            )

            return geojson.FeatureCollection([nhd_feature, split_feature])

        # If upstream == True and the clickpoint is NOT on a NHD FLowline,
        # return the local catchment and splitcatchment
        elif self.upstream is True and self.onFlowline is False:
            nhd_feature = geojson.Feature(
                geometry=self.catchment,
                id="catchment",
                properties={"catchmentID": self.catchmentIdentifier},
            )
            split_feature = geojson.Feature(
                geometry=self.splitCatchment, id="splitCatchment"
            )

            return geojson.FeatureCollection([nhd_feature, split_feature])

    # main functions
    def run(self) -> None:
        """Run splitcatchment module functions."""
        # Fetch the NHD catchment and flowline
        check_coords(self.x, self.y)
        transform_to_raster, _ = get_coordsys()
        self.catchmentIdentifier, catchment_geom = get_local_catchment(self.x, self.y)
        projected_catchment_geom = transform_geom(transform_to_raster, catchment_geom)
        projected_xy = project_point(self.x, self.y, transform_to_raster)

        # Open the flow direction and flow accumulation grids
        flw, fdr_profile = get_flowgrid(projected_catchment_geom)
        fac, fac_profile = get_facgrid(projected_catchment_geom)

        # Find the raster cell that the query point fall within
        start_row, start_col = get_row_column(projected_xy, fdr_profile["transform"])

        # Is that point on an NHD flowline?
        flowline_json, flowline_geom = get_local_flowline(self.catchmentIdentifier)
        projected_flowline_geom = transform_geom(transform_to_raster, flowline_geom)
        self.onFlowline = get_on_flowline(
            start_row, start_col, projected_flowline_geom, fdr_profile["transform"], fac
        )

        # Get the upstream portion of the catchment
        splitcatchment_geom = split_catchment(
            projected_xy, flw, fdr_profile["transform"]
        )

        # outputs
        self.catchment = catchment_geom.__geo_interface__
        self.splitCatchment = splitcatchment_geom.__geo_interface__

        if self.upstream is True and self.onFlowline is True:
            total_basin_geom = get_total_basin(self.catchmentIdentifier)
            upstream_basin_geom = get_upstream_basin(
                catchment_geom, splitcatchment_geom, total_basin_geom
            )
            self.drainageBasin = upstream_basin_geom.__geo_interface__
