
import unittest

from geogst.core.geometries.lines import *


class TestCartesianPlanesIntersections(unittest.TestCase):

    def setUp(self):

        self.p1 = Point(2, 1, 3)
        self.p2 = Point(-1, 2, 1)
        self.p3 = Point(2, 1, 3.1)

    def test_points_on_line(self):

        segment = Segment(self.p1, self.p2)
        versor = segment.as_versor3d()
        l, m, n = versor.to_xyz()

        par_line = ParamLine3D(self.p1, l, m, n)

        line_p, err = par_line.is_point_on_line(self.p1)
        assert(line_p)
        assert (not err)

        line_p, err = par_line.is_point_on_line(self.p2)
        assert(line_p)
        assert (not err)

        line_p, err = par_line.is_point_on_line(self.p3)
        assert(not line_p)
        assert (not err)



