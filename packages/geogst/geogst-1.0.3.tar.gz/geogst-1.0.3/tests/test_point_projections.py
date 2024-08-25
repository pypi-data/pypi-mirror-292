
import unittest

from geogst.core.geometries.planes import *


class TestPointProjections(unittest.TestCase):

    def setUp(self):

        geolplane = Plane(36.97, 72.43)
        pt = Point(3525367.16, 7362533.654, 6353.97)

        self.cplane = CPlane3D.from_geol_plane(
            geol_plane=geolplane,
            pt=pt
        )

    def test_point_projection_outside_plane(self):

        pt1 = Point(4739428.36, 8379302.64, 2626.464)

        projected_point, error = project_point_perpendicular_to_plane(
            plane=self.cplane,
            point=pt1
        )

        assert not error

        assert isinstance(projected_point, Point)

        assert self.cplane.absolute_distance_to_point(projected_point) < 1e-3

        segment = Segment(
            start_pt=projected_point,
            end_pt=pt1)

        versor = segment.as_versor3d()

        plane_normal_versor, error = self.cplane.normal_versor()

        assert not error

        angle_between_versors = plane_normal_versor.angle_with(versor)

        if angle_between_versors < 90.0:
            assert are_close(angle_between_versors, 0.0, atol=1e-3)
        else:
            assert are_close(angle_between_versors, 180.0, atol=1e-3)

    def test_point_projection_in_plane(self):

        pt1 = Point(6386333.9511, 5209421.2354, 5261.4463)

        assert self.cplane.absolute_distance_to_point(pt1) < 1e-3

        projected_point, error = project_point_perpendicular_to_plane(
            plane=self.cplane,
            point=pt1
        )

        assert not error

        assert isinstance(projected_point, Point)

        assert self.cplane.absolute_distance_to_point(projected_point) < 1e-3

        assert are_close(pt1.distance(projected_point), 0.0, atol=1e-3)

