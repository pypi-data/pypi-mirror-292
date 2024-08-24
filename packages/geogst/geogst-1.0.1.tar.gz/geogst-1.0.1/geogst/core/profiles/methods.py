
from geogst.core.geometries.grids.rasters import *


z_padding = 0.2


class PointsInput(Enum):
    POINTS = 1
    ATTITUDES = 2
    FAULTS = 3
    FOCAL_MECHANISMS = 4


class ProjectionMethod(Enum):
    NEAREST = 1
    COMMON_AXIS = 2
    INDIVIDUAL_AXES = 3
    ALONG_PLANE = 4


def attitudes_3d_from_grid(
        structural_data: List[Tuple[Category, Point, Plane]],
        height_source: Grid,
) -> Union[Error, List[Tuple[Category, Point, Plane]]]:
    """
    Create a set of 3D attitudes, extracting heights from a grid.

    :param structural_data: the set of attitudes
    :param height_source: the elevation source
    :return: list of attitudes values
    """

    attitudes_3d = []

    try:

        for rec_id, pt2d, plane in structural_data:

            pt3d = height_source.interpolate_bilinear_point(
                pt=pt2d
            )

            if pt3d:
                attitudes_3d.append(
                    (
                        rec_id,
                        pt3d,
                        plane
                    )
                )

        return attitudes_3d

    except Exception as e:

        return Error(
                True,
                caller_name(),
                e,
                traceback.format_exc()
            )


def calculate_profile_lines_intersection(
        multilines2d_list,
        id_list,
        profile_line2d
):

    profile_segment2d_list = profile_line2d.segments()

    profile_segment2d = profile_segment2d_list[0]

    intersection_list = []
    for ndx, multiline2d in enumerate(multilines2d_list):
        if id_list is None:
            multiline_id = ''
        else:
            multiline_id = id_list[ndx]
        for line2d in multiline2d.lines():
            for line_segment2d in line2d.segments():
                try:
                    intersection_point2d = profile_segment2d.intersection_2d_pt(line_segment2d)
                except ZeroDivisionError:
                    continue
                if intersection_point2d is None:
                    continue
                if line_segment2d.contains_2d_pt(intersection_point2d) and \
                   profile_segment2d.contains_2d_pt(intersection_point2d):
                    intersection_list.append([intersection_point2d, multiline_id])

    return intersection_list


def intersection_distances_by_profile_start_list(
        profile_line,
        intersections
):

    # convert the profile line
    # from a CartesianLine2DT to a CartesianSegment2DT
    profile_segment2d_list = profile_line.segments()

    if len(profile_segment2d_list) != 1:
        raise Exception(f"Profile 2D segments list should have just one element but {len(profile_segment2d_list)} got")

    profile_segment2d = profile_segment2d_list[0]

    # determine distances for each point in intersection list
    # creating a list of float values
    distance_from_profile_start_list = []
    for intersection in intersections:
        distance_from_profile_start_list.append(profile_segment2d.start_pt.distance_2d(intersection[0]))

    return distance_from_profile_start_list




