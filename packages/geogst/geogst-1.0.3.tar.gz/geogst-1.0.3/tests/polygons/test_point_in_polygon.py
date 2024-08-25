
import unittest

from geogst.core.geometries.polygons import *


class TestPointInPolygon(unittest.TestCase):

    def setUp(self):

        # squares

        self.sq1 = Polygon(
            outer=Ln([(1, 1), (3, 1), (3, 3), (1, 3)]),
        )

        self.sq2 = Polygon(
            outer=Ln([(1, 1), (5, 1), (5, 5), (1, 5)]),
            inner=[Ln([(2, 2), (4, 4), (2, 4)])]
        )

        # butterflies (malformed polygons)

        self.bf2 = Polygon(
            outer=Ln([(1, 1), (7, 4), (7, 1), (1, 4)]),
            inner=[Ln([(2, 2), (6, 3), (6, 2), (2, 3)])]
        )

    def test_point_in_simple_square_01(self):

        assert self.sq1.point_in_polygon(Point(1, 1))

        assert self.sq1.point_in_polygon(Point(2, 2))

        assert not self.sq1.point_in_polygon(Point(6, 2))

    def test_point_in_square_with_hole_01(self):

        assert not self.sq2.point_in_polygon(Point(0.999, 0.999))

        assert self.sq2.point_in_polygon(Point(1, 1))

        assert self.sq2.point_in_polygon(Point(2, 2))

        assert not self.sq2.point_in_polygon(Point(3, 3.5))

        assert self.sq2.point_in_polygon(Point(4, 4))

        assert self.sq2.point_in_polygon(Point(4.999999, 4.999999))

        assert not self.sq2.point_in_polygon(Point(5.00001, 5))

        assert not self.sq2.point_in_polygon(Point(5, 5.5))

        assert not self.sq2.point_in_polygon(Point(100, 5.5))

        assert not self.sq2.point_in_polygon(Point(100, 100))

    def test_butterly_01(self):

        assert not self.bf2.point_in_polygon(Point(0.999, 0.999))

        assert self.bf2.point_in_polygon(Point(1.000001, 1.000001))

        assert not self.bf2.point_in_polygon(Point(2.000001, 2.5))

        assert not self.bf2.point_in_polygon(Point(4, 3))

        assert self.bf2.point_in_polygon(Point(2, 1.9999))

        assert not self.bf2.point_in_polygon(Point(5.9999, 2.5))

        assert not self.bf2.point_in_polygon(Point(4, 1))

        assert not self.bf2.point_in_polygon(Point(0, 0))

        assert not self.bf2.point_in_polygon(Point(100000000, -100000000))

        assert not self.bf2.point_in_polygon(Point(100000000, 100000000))


