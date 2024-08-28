"""Utility script containing functions used for flowtrace and splitcatchment modules."""
import json
import math
import os
import sys
import urllib.parse
import warnings
from typing import Any
from typing import TypedDict
from typing import Union

import numpy as np
import pyflwdir
import pyproj
import rasterio.mask
import rasterio.warp
import requests
import shapely.geometry
from shapely.geometry import GeometryCollection
from shapely.geometry import LineString
from shapely.geometry import MultiPolygon
from shapely.geometry import Point
from shapely.geometry import Polygon
from shapely.geometry import shape
from shapely.ops import split
from shapely.ops import transform
from shapely.ops import unary_union

from . import logger


# import this to ignore shapely deprecation error statements
warnings.filterwarnings("ignore")

# This is necessary to prevent pyproj.tranform from outputing 'inf' values
# os.environ["PROJ_NETWORK"] = "OFF"

# arguments
NLDI_URL = "https://labs.waterdata.usgs.gov/api/nldi/linked-data/comid/"
NLDI_GEOSERVER_URL = "https://labs.waterdata.usgs.gov/geoserver/wmadata/ows"
IN_FDR_COG = os.environ.get(
    "COG_URL",
    "/vsicurl/https://prod-is-usgs-sb-prod-publish.s3.amazonaws.com"
    "/5fe0d98dd34e30b9123eedb0/fdr.tif",
)
IN_FAC_COG = os.environ.get(
    "COG_URL",
    "/vsicurl/https://prod-is-usgs-sb-prod-publish.s3.amazonaws.com"
    "/5fe0d98dd34e30b9123eedb0/fac.tif",
)

verbose = True

# Hard coding the CRS for the NHD and rasters being used
wgs84 = pyproj.CRS("EPSG:4326")
dest_crs = pyproj.CRS("EPSG:5070")


# Classes defining JSON object type
class JsonFeatureType(TypedDict):
    """Class defining a Json feature."""

    type: str
    id: str
    geometry: dict[str, Union[list[list[list[float]]], str]]
    geometry_name: str
    properties: dict[Union[str, int, float, None], Union[str, int, float, None]]
    bbox: list[float]


class JsonFeatureCollectionType(TypedDict):
    """Class defining a Json feature collection."""

    type: str
    features: list[JsonFeatureType]
    totalFeatures: str  # noqa N815
    numberReturned: int  # noqa N815
    timeStamp: str  # noqa N815
    crs: dict[str, Union[str, dict[str, str]]]
    bbox: list[float]


# functions
def get_coordsys() -> tuple[pyproj.Transformer, pyproj.Transformer]:
    """Get coordinate system of input flow direction raster."""
    transform_to_raster = pyproj.Transformer.from_crs(wgs84, dest_crs, always_xy=True)

    transform_to_wgs84 = pyproj.Transformer.from_crs(dest_crs, wgs84, always_xy=True)

    return transform_to_raster, transform_to_wgs84


def check_coords(x: float, y: float) -> None:
    """Check the submitted point is formatted correctly, and inside CONUS."""
    if x > 0 or y < 0:
        logger.critical(
            "Improper coordinates submitted. Makes sure the coords are submited "
            "as longitude, latitude in decimal degrees."
        )
        # Kill program if point is not lon, lat.
        sys.exit(1)
    elif not -124.848974 < x < -66.885444 or not 24.396308 < y < 49.384358:
        logger.critical(
            "Coordinates outside of CONUS. Submit a point within (-124.848974, "
            "24.396308) and (-66.885444, 49.384358)."
        )
        # Kill program if point is outside CONUS.
        sys.exit(1)
    else:
        logger.info("Point is correctly formatted and within the boundng box of CONUS.")


def transform_geom(
    proj: pyproj.Transformer, geom: shapely.geometry
) -> shapely.geometry:
    """Transform geometry to input projection."""
    # This is necessary to prevent pyproj.tranform from outputing 'inf' values
    # os.environ["PROJ_NETWORK"] = "OFF"
    projected_geom = transform(proj.transform, geom)
    projected_geom = transform(proj.transform, geom)

    return projected_geom


def get_local_catchment(x: float, y: float) -> tuple[str, Union[MultiPolygon, Polygon]]:
    """Perform point in polygon query to NLDI geoserver to get local catchment geometry."""
    logger.info("requesting local catchment...")

    wkt_point = f"POINT({x} {y})"
    cql_filter = f"INTERSECTS(the_geom, {wkt_point})"

    payload = {
        "service": "wfs",
        "version": "1.0.0",
        "request": "GetFeature",
        "typeName": "wmadata:catchmentsp",
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        "CQL_FILTER": cql_filter,
    }

    # Convert spaces in query to '%20' instead of '+'
    fixed_payload: str = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)

    # request catchment geometry from point in polygon query from NLDI geoserver
    r: requests.models.Response = requests.get(
        NLDI_GEOSERVER_URL, params=fixed_payload, timeout=5
    )

    try:
        # Try to  convert response to json
        resp = r.json()

        # get catchment id
        catchment_id = json.dumps(resp["features"][0]["properties"]["featureid"])

    except ValueError:
        if r.status_code == 200:
            logger.critical(
                "Get local catchment request failed. Check to make sure query was \
                submitted with lon, lat coords. Quiting nldi_flowtools query."
            )

        else:
            logger.critical(
                "Quiting nldi_flowtools query. Error requesting catchment from Geoserver:",
                r.status_code,
            )

        # Kill program if request fails or if the response is not what is expected.
        sys.exit(1)

    features = resp["features"][0]
    number_of_polygons = len(features["geometry"]["coordinates"])
    if (
        number_of_polygons > 1
    ):  # Catchments can be multipoly (I know, this is SUPER annoying)
        logger.warning(
            f"Multipolygon catchment found: \
                {json.dumps(features['properties']['featureid'])} \
                Number of polygons: {number_of_polygons}"
        )
        i: int = 0
        catchment_geom = []
        while i < number_of_polygons:
            catchment_geom.append(Polygon(features["geometry"]["coordinates"][i][0]))
            i += 1
        catchment_geom = MultiPolygon(catchment_geom)
    else:  # Else, the catchment is a single polygon (as it should be)
        catchment_geom = Polygon(features["geometry"]["coordinates"][0][0])

    logger.info(f"got local catchment: {catchment_id}")

    return catchment_id, catchment_geom


def get_local_flowline(
    catchment_id: str,
) -> tuple[JsonFeatureCollectionType, LineString]:
    """Request NDH Flowline from NLDI with Catchment ID."""
    cql_filter = f"comid={catchment_id}"

    payload = {
        "service": "wfs",
        "version": "1.0.0",
        "request": "GetFeature",
        "typeName": "wmadata:nhdflowline_network",
        "maxFeatures": "500",
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
        "CQL_FILTER": cql_filter,
    }
    # Convert spaces in query to '%20' instead of '+'
    fixed_payload = urllib.parse.urlencode(payload, quote_via=urllib.parse.quote)

    # request flowline geometry from NLDI geoserver using catchment ID
    r: requests.models.Response = requests.get(
        NLDI_GEOSERVER_URL, params=fixed_payload, timeout=5
    )
    try:
        # Try to  convert response to json
        flowline_json = r.json()
        # check json response for geometry
        nhd_geom = flowline_json["features"][0]["geometry"]

    except ValueError:
        if r.status_code == 200:
            logger.critical(
                "Get local flowline request failed. Check to make sure query "
                "was submitted with lon, lat coords. Quiting nldi_flowtools query."
            )

        else:
            logger.critical(
                "Quiting nldi_flowtools query. Error requesting flowline from Geoserver:",
                r.status_code,
            )

        # Kill program if request fails.
        sys.exit(1)

    logger.info("got local flowline")

    # Convert xyz to xy and return as a shapely LineString
    flowline_geom = LineString([i[0:2] for i in nhd_geom["coordinates"][0]])

    return flowline_json, flowline_geom


def get_total_basin(catchment_id: str) -> GeometryCollection:
    """Use local catchment identifier to get local upstream basin geometry from NLDI."""
    logger.info("getting upstream basin...")

    # request upstream basin
    payload = {"f": "json", "simplified": "false"}

    # request upstream basin from NLDI using comid of catchment point is in
    r: requests.models.Response = requests.get(
        NLDI_URL + catchment_id + "/basin", params=payload, timeout=5
    )

    try:
        # Try to  convert response to json
        resp = r.json()

        # convert geojson to ogr geom
        features = resp["features"]
        total_basin_geom = GeometryCollection(
            [shape(feature["geometry"]).buffer(0) for feature in features]
        )

    except ValueError:
        if r.status_code == 200:
            ValueError(
                "Get upstream basin request failed. Check to make sure query "
                "was submitted with lon, lat coords. Quiting nldi_flowtools query."
            )

        else:
            ValueError(
                "Quiting nldi_flowtools query. Error requesting upstream basin from the NLDI:",
                r.status_code,
            )

        # Kill program if request fails.
        sys.exit(1)

    logger.info("finished getting upstream basin")

    return total_basin_geom


def get_upstream_basin(
    catchment_geom: Union[MultiPolygon, Polygon],
    split_catchment_geom: Polygon,
    total_basin_geom: GeometryCollection,
) -> Union[MultiPolygon, Polygon]:
    """Get the upstream basin geometry.

    This is done by subtracting the local catchment geometry from the total basin geometry
    (what is returned from the NLDI basin query) and then merging this to the
    splitcatchment geometry.
    """
    # Clip the local catchment off of the total basin geometry
    upstream_basin_geom = total_basin_geom.difference(catchment_geom.buffer(0.00001))
    # Smooth out the split catchment before merging it
    simplified_split_catchment_geom = split_catchment_geom.buffer(0.0002).simplify(
        0.00025
    )
    # Merge the splitcatchment and upstream basin
    drainage_basin = simplified_split_catchment_geom.union(
        upstream_basin_geom.buffer(0.0002)
    ).buffer(-0.0002)

    return drainage_basin


def project_point(
    x: float, y: float, transform: pyproj.Transformer
) -> tuple[float, float]:
    """Project point to flow direction raster crs."""
    # Adjust lon value from -180 - 180 to 0 - 360
    # adjust_x: float = 360 - abs(x)
    point_geom: Point = Point(x, y)
    logger.info(f"original point: {point_geom.wkt}")

    projected_point = transform_geom(transform, point_geom)
    logger.info(f"projected point: {projected_point.wkt}")

    projected_xy: tuple[float, float] = projected_point.coords[:][0]

    # Test if one of the project point coordinates is infinity. If this is the case
    # then the point was not properly projected to the CRS of the DEM. This has happened
    # when proj version is greater than 6.2.1
    projected_x = projected_point.coords[:][0][0]
    if math.isinf(projected_x) is True:
        logger.critical(
            "Input point was not properly projected. This could be an error caused by PROJ."
        )

    return projected_xy


def get_flowgrid(
    catchment_geom: Union[MultiPolygon, Polygon],
) -> tuple[np.ndarray, rasterio.profiles.Profile]:
    """Get the FDR for the local catchment area.

    Use a 90 meter buffer of the local catchment to clip the
    NHD Plus v2 flow direction raster.

    Args:
        catchment_geom (Polygon or MultiPolygon): Polygon geometry for which to return the
            fdr raster.

    Returns:
        A tuple containing a Numpy array and a rasterio Profile.
    """
    logger.info("start clip of fdr raster")
    with rasterio.open(IN_FDR_COG, "r") as ds:
        fdr_profile = ds.profile

        # buffer catchment geometry by 90m before clipping flow direction raster
        buffer_catchment_geom = GeometryCollection([catchment_geom.buffer(90)])

        # clip input fd
        flwdir, flwdir_transform = rasterio.mask.mask(
            ds, buffer_catchment_geom.geoms, crop=True
        )
        logger.info("finish clip of fdr raster")

        fdr_profile.update(
            {
                "height": flwdir.shape[1],
                "width": flwdir.shape[2],
                "transform": flwdir_transform,
            }
        )

    return flwdir, fdr_profile


def get_facgrid(
    catchment_geom: Union[MultiPolygon, Polygon],
) -> tuple[np.ndarray, rasterio.profiles.Profile]:
    """Get the FAC for the local catchment area.

    Use a 90 meter buffer of the local catchment to clip the
    NHD Plus v2 flow accumulation raster.

    Args:
        catchment_geom (Polygon or MultiPolygon): Shapely Polygon geometry for which to
            return the fac raster.

    Returns:
        A tuple containing a Numpy array and a rasterio Profile.
    """
    logger.info("start clip of fac raster")
    with rasterio.open(IN_FAC_COG, "r") as ds:
        fac_profile = ds.profile

        # buffer catchment geometry by 90m before clipping flow direction raster
        buffer_catchment_geom = GeometryCollection([catchment_geom.buffer(90)])

        # clip input fd
        fac, fac_transform = rasterio.mask.mask(
            ds, buffer_catchment_geom.geoms, crop=True
        )

        fac_profile.update(
            {
                "height": fac.shape[1],
                "width": fac.shape[2],
                "transform": fac_transform,
            }
        )

    logger.info("finished clip of the fac raster")

    return fac, fac_profile


def split_catchment(
    projected_xy: tuple[float, float],
    flwdir: np.array,
    flwdir_transform: rasterio.Affine,
) -> Polygon:
    """Produce split catchment delienation from X,Y."""
    logger.info("start split catchment...")

    # import clipped fdr into pyflwdir
    flw = pyflwdir.from_array(flwdir[0], ftype="d8", transform=flwdir_transform)

    # used for snapping click point
    stream_order = flw.stream_order()
    logger.info("Calculated Stream Order")

    # delineate subbasins
    subbasins = flw.basins(
        xy=projected_xy, streams=stream_order > 2
    )  # streams=stream_order>4

    # convert subbasins from uint32
    subbasins = subbasins.astype(np.int32)

    # convert raster to features
    mask = subbasins != 0
    polys = rasterio.features.shapes(subbasins, transform=flwdir_transform, mask=mask)

    # Loop thru all the polygons that are returned from pyflwdir
    transformed_polys = []
    for poly, _ in polys:
        # project back to wgs84
        geom = rasterio.warp.transform_geom("EPSG:5070", "EPSG:4326", poly, precision=6)

        transformed_polys.append(Polygon(geom["coordinates"][0]))

    # Merge polygons, if there are more than one
    split_geom = unary_union(transformed_polys)

    logger.info("finish split catchment.")

    return split_geom


def get_row_column(
    point: tuple[float, float], raster_transform: rasterio.Affine
) -> tuple[int, int]:
    """Given a x,y point and a raster Affine, return the indices of the row and column."""
    col, row = ~raster_transform * (point)
    row = int(row)
    column = int(col)

    return row, column


def get_cell_corner(
    row: int, column: int, raster_transform: rasterio.Affine
) -> tuple[float, float]:
    """Given a row column pair, return the coords of the top left corner of a raster cell."""
    origin_x = raster_transform[2]
    origin_y = raster_transform[5]
    cell_size = raster_transform[0]

    return (origin_x + column * cell_size), (origin_y - row * cell_size)


def get_cell_center(
    row: int, column: int, raster_transform: rasterio.Affine
) -> tuple[float, float]:
    """Given an row column pair, return the coordinates of the raster cell center."""
    origin_x = raster_transform[2]
    origin_y = raster_transform[5]
    cell_size = raster_transform[0]

    return (origin_x + (column + 0.5) * cell_size), (origin_y - (row + 0.5) * cell_size)


def create_cell_polygon(
    row: int,
    col: int,
    raster_transform: rasterio.Affine,
) -> Polygon:
    """Given a row, column pair and rasterio affine, return an outline of the raster cell."""
    top_left_x, top_left_y = get_cell_corner(row, col, raster_transform)
    top_right_x, top_right_y = get_cell_corner(row, col + 1, raster_transform)
    bottom_left_x, bottom_left_y = get_cell_corner(row + 1, col, raster_transform)
    bottom_right_x, bottom_right_y = get_cell_corner(row + 1, col + 1, raster_transform)

    cell_geom = Polygon(
        (
            (top_left_x, top_left_y),
            (top_right_x, top_right_y),
            (bottom_right_x, bottom_right_y),
            (bottom_left_x, bottom_left_y),
        )
    ).normalize()

    return cell_geom


def get_on_flowline(
    row: int,
    col: int,
    flowline: LineString,
    raster_transform: rasterio.Affine,
    fac: np.array,
) -> bool:
    """Determine whether the raster cell 'intersects' the given flowline geometry.

    This is not exactly straightforward. The cell needs to both intersect the line geoemtry
    and the Flow Accumultion value needs to be above 1100. Only when both of these are true
    does the function return a boolean value of 'True'.
    """
    cell_geom = create_cell_polygon(row, col, raster_transform)

    cell_intersect = flowline.intersects(cell_geom)

    fac_val = fac[0][row, col]
    # TODO: pick a better method, this is an arbitrary FAC value
    if fac_val > 1100 and cell_intersect:
        logger.info("point is on a flowline")
        return True
    else:
        logger.info("point not on a flowline")
        return False


def get_downstream_cell(row: int, col: int, fdr_val: np.uint8) -> tuple[int, int]:
    """Return the row, column indices of the next cell downstream given the flow direction."""
    if fdr_val == 128:  # NE
        return row - 1, col + 1

    elif fdr_val == 64:  # N
        return row - 1, col

    elif fdr_val == 32:  # NW
        return row - 1, col - 1

    elif fdr_val == 16:  # W
        return row, col - 1

    elif fdr_val == 8:  # SW
        return row + 1, col - 1

    elif fdr_val == 4:  # S
        return row + 1, col

    elif fdr_val == 2:  # SE
        return row + 1, col + 1

    elif fdr_val == 1:  # E
        return row, col + 1

    else:
        # logger.critical("Flowtrace intersected a nodata FDR value; cannot continue downhill.")
        raise ValueError(
            "Flowtrace intersected a nodata FDR value; cannot continue downhill."
        )


def trace_downhill(
    on_flowline: bool,
    point: tuple[float, float],
    raster_transform: rasterio.Affine,
    fdr: np.array,
    fac: np.array,
    flowline: LineString,
) -> list[tuple[float, float]]:
    """Given a starting point, trace down the flow direction grid.

    The function returns a list of x,y coords. The first coord pair is the input
    coord. The next is the cell center of the cell the point falls in. As the trace
    proceeds downstream, each cell center gets added to the coord list.
    Once the trace gets to a cell that overlaps the input flowline geometry and the
    flow accumulation value is greater that 900, the trace stops. It grabs the closest
    point on the flowline and adds it to the coord list.
    """
    # The first flowpath point is the clip point
    flowpath_coords = [point]

    row, col = get_row_column(point, raster_transform)

    while not on_flowline:
        # Add the first cell center to the flowpath
        flowpath_coords.append(get_cell_center(row, col, raster_transform))
        # Get the flow direction
        fdr_val = fdr[0][row, col]
        # Get the the downstream cell and add it to the coords list
        row, col = get_downstream_cell(row, col, fdr_val)
        next_point = get_cell_center(row, col, raster_transform)
        flowpath_coords.append(next_point)
        # Check if this next cell is on the flowline, is so, stop the loop. If not, continue
        on_flowline = get_on_flowline(row, col, flowline, raster_transform, fac)

    # Go downstream and extra cell, just for good measure
    fdr_val = fdr[0][row, col]
    row, col = get_downstream_cell(row, col, fdr_val)

    # Clip the NHD flowline to the current raster cell
    cell_geom = create_cell_polygon(row, col, raster_transform)
    clipped_line = flowline.intersection(cell_geom)
    # Take the midpoint of the clipped flowline, add to the flowpath coords
    flowpath_coords.append(clipped_line.centroid.__geo_interface__["coordinates"])

    return flowpath_coords


def get_reach_measure(  # noqa C901
    intersection_point: Point,
    flowline: JsonFeatureCollectionType,
    *raindrop_path: LineString,
) -> dict[str, Union[Any, str, float, None]]:
    """Collect NHD Flowline Reach Code and Measure."""
    # Set Geoid to measure distances in meters
    geod = pyproj.Geod(ellps="WGS84")

    # Convert the flowline to a geometry collection to be exported
    nhd_geom = flowline["features"][0]["geometry"]
    nhd_flowline = GeometryCollection([shape(nhd_geom)]).geoms[0]
    nhd_flowline = LineString(
        [xy[0:2] for xy in list(nhd_flowline.geoms[0].coords)]
    )  # Convert xyz to xy

    # Select the stream name from the NHD Flowline
    stream_name = flowline["features"][0]["properties"]["gnis_name"]
    if stream_name == " ":
        stream_name = "none"

    # Create stream_info dict and add some data
    stream_info = {
        "gnis_name": stream_name,
        "comid": flowline["features"][0]["properties"][
            "comid"
        ],  # 'lengthkm': flowline['features'][0]['properties']['lengthkm'],
        "intersection_point": (intersection_point.coords[0]),
        "reachcode": flowline["features"][0]["properties"]["reachcode"],
    }

    # Add more data to the stream_info dict
    if raindrop_path:
        stream_info["raindrop_pathDist"] = round(
            geod.geometry_length(raindrop_path[0]), 2
        )

    # If the intersection_point is on the NHD Flowline, split the flowline at the point
    if nhd_flowline.intersects(intersection_point) is True:
        split_nhd_flowline = split(nhd_flowline, intersection_point)

    # If they don't intersect (weird right?) buffer the intersection_point
    # and then split the flowline
    if nhd_flowline.intersects(intersection_point) is False:
        buff_dist = intersection_point.distance(nhd_flowline) * 1.01
        buff_intersection_point = intersection_point.buffer(buff_dist)
        split_nhd_flowline = split(nhd_flowline, buff_intersection_point)

    # If the NHD Flowline was split, then calculate measure
    if len(split_nhd_flowline.geoms) > 1:
        last_line_id = len(split_nhd_flowline.geoms) - 1
        dist_to_outlet = round(
            geod.geometry_length(split_nhd_flowline.geoms[last_line_id]), 2
        )
        flowline_leng = round(geod.geometry_length(nhd_flowline), 2)
        stream_info["measure"] = round((dist_to_outlet / flowline_leng) * 100, 2)
    else:  # If NHDFlowline was not split, then the intersection_point is either the
        # first or last point on the NHDFlowline
        start_pnt = Point(nhd_flowline.coords[0][0], nhd_flowline.coords[0][1])
        last_pnt_id = len(nhd_flowline.coords) - 1
        last_pnt = Point(
            nhd_flowline.coords[last_pnt_id][0],
            nhd_flowline.coords[last_pnt_id][1],
        )
        if intersection_point == start_pnt:
            stream_info["measure"] = 100
            error = "The point of intersection is the first point on the NHD Flowline."
        elif intersection_point == last_pnt:
            stream_info["measure"] = 0
            error = "The point of intersection is the last point on the NHD Flowline."
        elif intersection_point != start_pnt and intersection_point != last_pnt:
            error = "Error: NHD Flowline measure not calculated"
            stream_info["measure"] = "null"
        logger.warning(error)

    logger.info("calculated measure and reach")

    return stream_info


def split_flowline(
    intersection_point: Point,
    nhd_flowline: LineString,
) -> tuple[LineString, LineString]:
    """Split the NHD Flowline at the intersection point.

    Args:
        intersection_point (Point): The Shapely point at which to split the flowline
        nhd_flowline (LineString): The flowline to split

    Returns:
        A tuple containing two shapely LineString. The first is the upstream portion
        and the second is the donwstream portion of the input flowline.

    """
    # If the intersection_point is on the NHD Flowline, split the flowline at the point
    if nhd_flowline.intersects(intersection_point) is True:
        split_nhd_flowline = split(nhd_flowline, intersection_point)

    # If they don't intersect (weird right?), buffer the intersection_point
    # and then split the flowline
    if nhd_flowline.intersects(intersection_point) is False:
        buff_dist = intersection_point.distance(nhd_flowline) * 1.01
        buff_intersection_point = intersection_point.buffer(buff_dist)
        split_nhd_flowline = split(nhd_flowline, buff_intersection_point)

    # If the NHD Flowline was split, then calculate measure
    if len(split_nhd_flowline.geoms) > 1:
        last_line_id = len(split_nhd_flowline.geoms) - 1
        upstream_flowline = split_nhd_flowline.geoms[0]
        downstream_flowline = split_nhd_flowline.geoms[last_line_id]

    else:  # If NHDFlowline was not split, then the intersection_point is either the
        # first or last point on the NHDFlowline
        start_pnt = Point(nhd_flowline.coords[0][0], nhd_flowline.coords[0][1])
        last_pnt_id = len(nhd_flowline.coords) - 1
        last_pnt = Point(
            nhd_flowline.coords[last_pnt_id][0],
            nhd_flowline.coords[last_pnt_id][1],
        )
        if intersection_point == start_pnt:
            upstream_flowline = GeometryCollection()
            downstream_flowline = split_nhd_flowline
            error = "The point of intersection is the first point on the NHD Flowline."
        elif intersection_point == last_pnt:
            downstream_flowline = GeometryCollection()
            upstream_flowline = split_nhd_flowline
            error = "The point of intersection is the last point on the NHD Flowline."
        elif intersection_point != start_pnt and intersection_point != last_pnt:
            error = "Error: NHD Flowline measure not calculated"
            downstream_flowline = GeometryCollection()
            upstream_flowline = GeometryCollection()
        logger.warning(error)

    logger.info("split NHD Flowline")

    return upstream_flowline, downstream_flowline
