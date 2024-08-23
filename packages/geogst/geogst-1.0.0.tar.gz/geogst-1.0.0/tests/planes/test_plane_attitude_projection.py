
import unittest

from geogst.core.geometries.planes import *


class TestCartesianPlanesAttitudeProjection(unittest.TestCase):

    def setUp(self):

        # dataset constructed using
        # planes defined in Stereonet by Allmendinger

        self.plane_a_rhr_strike = 320.0
        self.plane_a_dip_angle = 17.0

        self.plane_b_rhr_strike = 39.0
        self.plane_b_dip_angle = 63.0

        self.intersection_trend = 48.0
        self.intersection_plunge = 17.0

        self.intersection_dir = Direct(
            self.intersection_trend,
            self.intersection_plunge)

        self.intersection_vector = self.intersection_dir.as_versor()

    def test_cartesian_plane_attitude_projection(self):

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

        result, err = intersect_plane_with_attitude(
            cartes_plane=cplane_a,
            attitude=geol_plane_b,
            point=point_plane_b
        )

        assert not err

        assert result is not None

        assert isinstance(result, tuple)

        assert len(result) == 2

        intersection_versor, intersection_pt = result

        assert isinstance(intersection_versor, Vect3D)
        assert isinstance(intersection_pt, Point)

        assert self.intersection_vector.is_par_or_antipar_with(intersection_versor, angular_tol=1e-1)

        assert cplane_b.contains_point(intersection_pt)
        assert cplane_a.contains_point(intersection_pt)

        # checking the angle between the attitude_intersection versor and the points-segment

        checked_versor = Segment(intersection_pt, point_plane_b).as_versor3d()
        angle = intersection_versor.angle_with(checked_versor)
        assert are_close(angle, 90)

        # checking whether the attitude_intersection point represent a minimum of distance

        min_dist = point_plane_b.distance(intersection_pt)

        pt_inters_shift_plus = intersection_pt.shift_by_vect(intersection_versor.scale(0.1))  # cannot be too fine-grained, f.i. 0.01 does not work
        pt_inters_shift_minus = intersection_pt.shift_by_vect(intersection_versor.scale(-0.1))

        dist_plus = point_plane_b.distance(pt_inters_shift_plus)
        dist_minus = point_plane_b.distance(pt_inters_shift_minus)

        assert min_dist < dist_plus
        assert min_dist < dist_minus

        pt_inters_shift_2plus = intersection_pt.shift_by_vect(intersection_versor.scale(0.2))
        pt_inters_shift_2minus = intersection_pt.shift_by_vect(intersection_versor.scale(-0.2))

        dist_2plus = point_plane_b.distance(pt_inters_shift_2plus)
        dist_2minus = point_plane_b.distance(pt_inters_shift_2minus)

        assert min_dist < dist_2plus
        assert min_dist < dist_2minus
