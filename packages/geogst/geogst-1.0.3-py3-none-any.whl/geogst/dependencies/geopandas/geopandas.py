
from typing import Set

import shapely
import geopandas as gpd
from geopandas import GeoDataFrame

from geogst.core.geometries.points import *
from geogst.core.geology.faults import *


def geodataframe_geom_types(
    geodataframe: gpd.GeoDataFrame
) -> Set[str]:
    # Side effects: none
    """
    Return a set storing the geometric types in a GeoDataFrame instance.

    :param geodataframe: the input geodataframe
    :return: the set of geometric types values
    """

    return set(geodataframe.geom_type)


def containsPoints(
    geodataframe: gpd.GeoDataFrame
) -> bool:
    # Side effects: none
    """
    Check if a GeoDataFrame instance contains points.

    :param geodataframe: the input geodataframe
    :return: if a GeoDataFrame instance contains points
    """

    return 'Point' in geodataframe_geom_types(geodataframe)


def containsLines(
    geodataframe: gpd.GeoDataFrame
) -> bool:
    # Side effects: none
    """
    Check if a GeoDataFrame instance contains lines.

    :param geodataframe: the input geodataframe
    :return: if a GeoDataFrame instance contains line
    """

    return 'LineString' in geodataframe_geom_types(geodataframe)


def containsPolygons(
    geodataframe: gpd.GeoDataFrame
) -> bool:
    # Side effects: none
    """
    Check if a GeoDataFrame instance contains polygons.

    :param geodataframe: the input geodataframe
    :return: if a GeoDataFrame instance contains polygons
    """

    return 'Polygon' in geodataframe_geom_types(geodataframe)


def extract_geometries(
    geodataframe: gpd.GeoDataFrame
) -> gpd.geoseries.GeoSeries:
    # Side effects: none
    """
    Extract geometries from a GeoDataFrame instance.

    :param geodataframe: the input geodataframe
    :return: the geometries stored in the GeoDataFrame instance
    """

    return geodataframe.geometry


def extract_geometry(
    geodataframe: gpd.GeoDataFrame,
    ndx: numbers.Integral
) -> shapely.geometry.base.BaseGeometry:
    # Side effects: none
    """
    Extract a geometry from a GeoDataFrame instance,
    given the geometry index.

    :param geodataframe: the input geodataframe
    :param ndx: the geometry index
    :return: the geometry stored in the GeoDataFrame instance
    """

    return extract_geometries(geodataframe)[ndx]


def get_epsg(
    geodataframe: gpd.GeoDataFrame
) -> numbers.Integral:
    # Side effects: None
    """
    Extract the EPSG code of the data

    :param geodataframe: the input geodataframe
    :return: the EPSG code or -1
    """

    crs_dict = geodataframe.crs

    epsg = -1

    try:

        val = crs_dict["init"]
        if val.lower().startswith("epsg"):
            epsg = int(val.split(":", 1)[1])

    except Exception:

        pass

    return epsg


def extract_line_points(
    geodataframe: gpd.GeoDataFrame,
    ndx: numbers.Integral
) -> List[Point]:
    """
    Extract a geometry from a GeoDataFrame instance,
    given the geometry index.

    :param geodataframe: the input geodataframe
    :param ndx: the geometry index
    :return: the geometry stored in the GeoDataFrame instance
    """

    geometry = extract_geometry(
        geodataframe=geodataframe,
        ndx=ndx
    )

    xs, ys = geometry.cell_centers_xy_arrays

    pts = []

    for x, y in zip(xs, ys):
        pts.append(
            Point(
                x,
                y
            )
        )

    return pts


def extract_attitudes(
        geodataframe: GeoDataFrame,
        azim_fldnm: str,
        dip_ang_fldnm: str,
        id_fldnm: Optional[str] = None,
        is_rhrstrike: bool = False
) -> Tuple[List[Tuple[Category, Point, Plane]], Optional[str]]:
    """
    Try extracting geological attitudes from a geopandas point GeoDataFrame instance.

    :param geodataframe: the source geodataframe.
    :param azim_fldnm: the name of the azimuth field in the geodataframe.
    :param dip_ang_fldnm: the name of the dipang rot_angle field in the geodataframe.
    :param id_fldnm: the name of the id field in the geodataframe.
    :param is_rhrstrike: whether the dipang azimuth is strike RHR.
    :return: the collection of georeferenced attitudes, one for each source record, plus an optional message.
    """

    attitudes = []

    try:

        for ndx, row in geodataframe.iterrows():

            pt = row['geometry']
            x, y = pt.x, pt.y

            if id_fldnm:
                azimuth, dip_ang, rec_id = row[azim_fldnm], row[dip_ang_fldnm], row[id_fldnm]
            else:
                azimuth, dip_ang, rec_id = row[azim_fldnm], row[dip_ang_fldnm], ndx + 1

            if is_rhrstrike:
                azimuth = (azimuth + 90.0) % 360.0

            attitudes.append(
                (
                    rec_id,
                    Point(x, y),
                    Plane(azimuth, dip_ang)
                )
            )

        return attitudes, None

    except Exception as e:

        return attitudes, f"{e!r}"


def extract_fault_points(
    geodataframe: GeoDataFrame,
    azim_fldnm: str,
    dip_ang_fldnm: str,
    rake_fldnm: str,
    id_fldnm: Optional[str] = None,
    is_rhrstrike: bool = False
) -> Tuple[List[Tuple[Category, Point, Fault]], Union[type(None), str]]:
    """
    Try extracting geological faults from a geopandas point GeoDataFrame instance.

    :param geodataframe: the source geodataframe.
    :param azim_fldnm: the name of the azimuth field in the geodataframe.
    :param dip_ang_fldnm: the name of the dip angle field in the geodataframe.
    :param rake_fldnm: the name of the rake (Aki & Richards 1980) field in the geodataframe.
    :param id_fldnm: the name of the id field in the geodataframe.
    :param is_rhrstrike: whether the azimuth value is in RHR strike format.
    :return: the collection of georeferenced faults, one for each source record, plus an optional message.
    """

    faults = []

    try:

        for ndx, row in geodataframe.iterrows():

            pt = row['geometry']
            x, y, z = pt.x, pt.y, pt.z

            if id_fldnm:
                azimuth, dip_ang, rake, rec_id = row[azim_fldnm], row[dip_ang_fldnm], row[rake_fldnm], row[id_fldnm]
            else:
                azimuth, dip_ang, rake, rec_id = row[azim_fldnm], row[dip_ang_fldnm], row[rake_fldnm], ndx + 1

            if is_rhrstrike:
                azimuth = (azimuth + 90.0) % 360.0
            faults.append(
                (
                    rec_id,
                    Point(x, y, z),
                    Fault(azimuth, dip_ang, rake)
                )
            )

        return faults, None

    except Exception as e:

        return faults, f"{e!r}"


def extract_seism_points(
    geodataframe: GeoDataFrame,
    azim_fldnm: str,
    dip_ang_fldnm: str,
    rake_fldnm: str,
    is_rhrstrike: bool = False,
    category_fldnm: Optional[str] = None,
) -> Tuple[List[Tuple[Category, Point, Fault]], Union[type(None), str]]:
    """
    Try extracting geological faults from a geopandas point GeoDataFrame instance.

    :param geodataframe: the source geodataframe.
    :param azim_fldnm: the name of the azimuth field in the geodataframe.
    :param dip_ang_fldnm: the name of the dip angle field in the geodataframe.
    :param rake_fldnm: the name of the rake (Aki & Richards 1980) field in the geodataframe.
    :param is_rhrstrike: whether the azimuth value is in RHR strike format.
    :param category_fldnm: the name of the category field in the geodataframe.

    :return: the collection of georeferenced faults, one for each source record, plus an optional message.
    """

    data = []

    try:

        for ndx, row in geodataframe.iterrows():

            pt = row['geometry']
            x, y, z = pt.x, pt.y, pt.z

            if category_fldnm:
                azimuth, dip_ang, rake, category = row[azim_fldnm], row[dip_ang_fldnm], row[rake_fldnm], row[category_fldnm]
            else:
                azimuth, dip_ang, rake, category = row[azim_fldnm], row[dip_ang_fldnm], row[rake_fldnm], ndx + 1

            if is_rhrstrike:
                azimuth = (azimuth + 90.0) % 360.0
            data.append(
                (
                    category,
                    Point(x, y, z),
                    Fault(azimuth, dip_ang, rake)
                )
            )

        return data, None

    except Exception as e:

        return data, f"{e!r}"

