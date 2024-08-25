
import unittest

from geogst.core.geometries.planes import *


class TestCartesianPlanesIntersections(unittest.TestCase):

    def setUp(self):

        # dataset constructed using
        # planes defined in Stereonet by Allmendinger

        self.plane_a_rhr_strike = 320.0
        self.plane_a_dip_angle = 17.0

        self.plane_b_rhr_strike = 39.0
        self.plane_b_dip_angle = 63.0

        self.intersection_trend = 48.0
        self.intersection_plunge = 17.0

        self.intersection_axis = Axis(
            self.intersection_trend,
            self.intersection_plunge)

    def test_cartesian_planes_intersection(self):

        geol_plane_a = Plane(
            azim=self.plane_a_rhr_strike,
            dip_ang=self.plane_a_dip_angle,
            is_rhr_strike=True
        )
        geol_plane_b = Plane(
            azim=self.plane_b_rhr_strike,
            dip_ang=self.plane_b_dip_angle,
            is_rhr_strike=True
        )

        cplane_a = CPlane3D.from_geol_plane(
            geol_plane_a,
            Point(0, 0, 0))

        cplane_b = CPlane3D.from_geol_plane(
            geol_plane_b,
            Point(0, 0, 0))

        versor, err = cplane_a.intersects_other(
            another=cplane_b)

        assert(not err)

        assert isinstance(versor, Vect3D)

        assert versor.is_close_to_1

        cplane_a_normal, err = cplane_a.normal_versor()
        assert not err

        cplane_b_normal, err = cplane_b.normal_versor()
        assert not err

        assert are_close(versor.angle_with(cplane_a_normal), 90.0)
        assert are_close(versor.angle_with(cplane_b_normal), 90.0)

    def test_coincident_planes_intersection(self):

        geol_plane_a = Plane(
            azim=self.plane_a_rhr_strike,
            dip_ang=self.plane_a_dip_angle,
            is_rhr_strike=True
        )

        cplane_a = CPlane3D.from_geol_plane(
            geol_plane_a,
            Point(0, 0, 0))

        intersection, err = cplane_a.intersects_other(
            another=cplane_a)

        assert(not err)

        assert isinstance(intersection, CPlane3D)

        assert cplane_a.is_coincident_with_plane(intersection)

    def test_parallel_planes_intersections(self):

        geol_plane_a = Plane(
            azim=self.plane_a_rhr_strike,
            dip_ang=self.plane_a_dip_angle,
            is_rhr_strike=True
        )

        cplane_a = CPlane3D.from_geol_plane(
            geol_plane_a,
            Point(0, 0, 0))

        cplane_b = CPlane3D.from_geol_plane(
            geol_plane_a,
            Point(1, 0, 0))

        intersection, err = cplane_a.intersects_other(
            another=cplane_b)

        assert(not err)

        assert intersection is None


class TestCartesianPlanesIntersectionsAsPoint(unittest.TestCase):

    def setUp(self):

        # dataset constructed using
        # planes defined in Stereonet by Allmendinger

        self.plane_a_rhr_strike = 320.0
        self.plane_a_dip_angle = 17.0

        self.plane_b_rhr_strike = 39.0
        self.plane_b_dip_angle = 63.0

        self.intersection_trend = 48.0
        self.intersection_plunge = 17.0

        self.intersection_axis = Axis(
            self.intersection_trend,
            self.intersection_plunge)

    def test_other_as_point(self):

        geol_plane_a = Plane(
            azim=self.plane_a_rhr_strike,
            dip_ang=self.plane_a_dip_angle,
            is_rhr_strike=True
        )

        cplane_a = CPlane3D.from_geol_plane(
            geol_plane_a,
            Point(0, 0, 0))

        geol_plane_b = Plane(
            azim=self.plane_b_rhr_strike,
            dip_ang=self.plane_b_dip_angle,
            is_rhr_strike=True
        )

        point_plane_b = Point(1527, 3252435, 6256)

        cplane_b = CPlane3D.from_geol_plane(
            geol_plane_b,
            point_plane_b)

        result, err = cplane_a.intersects_other_as_pt(
               another=cplane_b)

        assert not err

        assert result is not None

        assert isinstance(result, Point)

        assert cplane_a.contains_point(result)
        assert cplane_b.contains_point(result)

