
import unittest

from geogst.core.geometries.planes import *
from geogst.core.mathematics.utils import are_close


class TestOrientations(unittest.TestCase):

    def setUp(self):

        pass

    def test_direct_general(self):
        """
        Check expected OrienM results for downward dipang.
        """

        assert Direct(90, 90).is_downward
        assert Direct(90, -45).is_upward
        assert are_close(Direct(90, 90).as_versor().z, -1.0)
        assert are_close(Direct(90, -90).as_versor().z, 1.0)
        assert are_close(Direct(0, 90).upward().as_versor().z, 1.0)
        assert are_close(Direct(0, -90).downward().as_versor().z, -1.0)

    def test_direct_angle(self):

        assert are_close(Direct(90, 45).angle_with(
            Direct(90, 55)), 10.)
        assert are_close(Direct(90, 45).angle_with(
            Direct(270, 10)), 125.)
        assert are_close(Direct(90, 90).angle_with(
            Direct(135, 90)), 0.)
        assert are_close(Direct(0, 0).angle_with(
            Direct(135, 0)), 135.)
        assert are_close(Direct(0, 80).angle_with(
            Direct(180, 80)), 20.)

    def test_axis_angle(self):

        assert are_close(Axis(90, 0).angle_with(
            Axis(270, 0)), 0.)

    def test_plane_normal(self):

        assert are_close(
            Plane(90, 45).norm_direct_frwrd().angle_with(
                Direct(90, -45)), 0.)

    def test_plane2cplane(self):

        pl = CPlane3D.from_geol_plane(Plane(90, 45), Point(0, 0, 0))
        assert are_close(pl.angle_with(CPlane3D(1, 0, 1, 0)), 0.0)

    def test_plane_angle(self):

        assert are_close(
            Plane(90, 45).angle_with(
                Plane(90, 45)), 0.)
        assert are_close(
            Plane(90, 45).angle_with(
                Plane(90, 55)), 10.)
        assert are_close(
            Plane(90, 5).angle_with(
                Plane(270, 5)), 10.)
        assert are_close(
            Plane(90, 85).angle_with(
                Plane(270, 85)), 10.)
        assert are_close(
            Plane(0, 0).angle_with(
                Plane(0, 10)), 10.)
        assert are_close(
            Plane(0, 0).angle_with(
                Plane(180, 0)), 0.)

    def tearDown(self):

        pass


if __name__ == '__main__':

    unittest.main()
