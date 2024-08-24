
import unittest

from geogst.core.geometries.planes import *


class TestPlaneAxisIntersections(unittest.TestCase):

    def setUp(self):

        geolplane = Plane(36.97, 72.43)
        pt = Point(3525367.16, 7362533.654, 6353.97)

        self.cplane = CPlane3D.from_geol_plane(
          geol_plane=geolplane,
          pt=pt
        )

    def test_plane_axis_intersections(self):

        segm_pt1 = Point(4739428.36, 8379302.64, 2626.464)
        segm_pt2 = Point(7758322.25, 2568686.867, 7456.572)

        intersection_geom, err = verify_plane_line_intersection(
            segm_pt1,
            segm_pt2,
            self.cplane
        )

        assert isinstance(intersection_geom, Point)
        assert not bool(err)

        check_point_with_line(
            intersection_geom,
            segm_pt1,
            Segment(segm_pt1, segm_pt2).as_versor3d())

        check_point_within_plane(
            intersection_geom,
            self.cplane)

        segm_pt1 = Point(4365428.64, 8357502.37, 3536.3756)
        segm_pt2 = Point(7368963.7356, 8454332.746, 7563.37567)

        intersection_geom, err = verify_plane_line_intersection(
            segm_pt1,
            segm_pt2,
            self.cplane
        )

        assert isinstance(intersection_geom, Point)
        assert not bool(err)

        check_point_with_line(
            intersection_geom,
            segm_pt1,
            Segment(segm_pt1, segm_pt2).as_versor3d())

        check_point_within_plane(
            intersection_geom,
            self.cplane)

    def test_axis_within_plane(self):

        segm_pt1 = Point(6386333.9511, 5209421.2354, 5261.4463)
        segm_pt2 = Point(2295171.5965, 8290759.7612, 760.6713)

        atol = 1e-4
        check_point_within_plane(
            segm_pt1,
            self.cplane,
            distance_atol=atol)

        check_point_within_plane(
            segm_pt2,
            self.cplane,
            distance_atol=atol)

        intersection_geom, err = verify_plane_line_intersection(
            segm_pt1,
            segm_pt2,
            self.cplane
        )

        assert isinstance(intersection_geom, ParamLine3D)
        assert not bool(err)

    def test_axis_parallel_plane(self):

        pt1 = Point(6386333.9511, 5209421.2354, 5261.4463)
        pt2 = Point(2295171.5965, 8290759.7612, 760.6713)

        v_shift = Vect3D(1, 1, 1)

        pt1 = pt1.shift_by_vect(v_shift)
        pt2 = pt2.shift_by_vect(v_shift)

        intersection_geom, err = verify_plane_line_intersection(
            pt1,
            pt2,
            self.cplane
        )

        assert intersection_geom is None
        assert not bool(err)


def verify_plane_line_intersection(
    pt1: Point,
    pt2: Point,
    cplane: CPlane3D,
    distance_atol: numbers.Real = 1e-3,
    angular_atol: numbers.Real = 1e-3
):

    segm = Segment(pt1, pt2)
    versor = segm.as_versor3d()

    direct, err = Direct.from_vector(versor)

    axis = Axis.from_direction(direct)

    src_pt = pt1

    return intersect_plane_with_axis(
        plane=cplane,
        axis=axis,
        src_pt=src_pt,
        distance_atol=distance_atol,
        angular_atol=angular_atol
    )


def check_point_with_line(
    pt,
    src_pt,
    versor):

    # check point versus line

    l, m, n = versor.to_xyz()
    param_line = ParamLine3D(src_pt, l, m, n)

    online, _ = param_line.is_point_on_line(pt)
    assert online


def check_point_within_plane(
    pt,
    cplane,
    distance_atol=1e-5
):

    # check point versus plane

    distance = cplane.absolute_distance_to_point(pt)
    
    assert are_close(distance, 0.0, atol=distance_atol)




