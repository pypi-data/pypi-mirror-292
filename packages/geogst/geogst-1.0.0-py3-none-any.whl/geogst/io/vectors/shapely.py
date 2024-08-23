
from shapely.geometry import Polygon as ShapelyPolyg, MultiPolygon as ShapelyMultiPolyg, LineString

from geogst.core.geometries.lines import *


def line2d_from_shapely(
        shapely_geom: LineString
) -> Ln:
    # Side effects: none
    """
    Create a Ln instance from a shapely Linestring instance.

    :param shapely_geom: the shapely input LineString instance
    :return: the converted Ln instance
    """

    return Ln(np.array(shapely_geom.coords))


def line2d_to_shapely(
        src_line: Ln
) -> LineString:
    """
    Create a shapely.LineString instance from a Ln one.

    :param src_line: the source line to convert to the shapely format
    :return: the shapely LineString instance and the EPSG code
    """

    return LineString(src_line.xy_zipped())


class MPolygon2D:
    """
    A shapely (multi)polygon.

    """

    def __init__(self,
                 shapely_geom: Union[ShapelyPolyg, ShapelyMultiPolyg]
                 ):
        """
        :param shapely_geom: the (multi)polygon
        """

        self._geom = shapely_geom

    @property
    def geom(self):
        return self._geom

    def intersect_line(self,
                       line: LineString,
                       ) -> List[Ln]:
        """
        Determine the intersections between a mpolygon and a line.

        :param line: the line
        :return: the intersecting lines.
        """

        lines = []

        intersections = line.intersection(self.geom)

        if intersections:

            if intersections.geom_type == "LineString":

                inters_ln = line2d_from_shapely(
                    shapely_geom=intersections
                )

                lines.append(inters_ln)

            elif intersections.geom_type == "MultiLineString":

                for intersection_line in intersections:

                    inters_ln = line2d_from_shapely(
                        shapely_geom=intersection_line
                    )

                    lines.append(inters_ln)

            else:

                pass

        return lines

