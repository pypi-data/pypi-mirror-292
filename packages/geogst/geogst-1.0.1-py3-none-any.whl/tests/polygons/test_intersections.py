
import unittest

from geogst.core.geometries.polygons import *


class TestPolygonIntersections(unittest.TestCase):

    def setUp(self):

        # triangles

        self.t1 = Polygon(outer=Ln([(1, 1), (2, 1), (1.5, 2)]))
        self.t2 = Polygon(outer=Ln([(1, 1), (4, 1), (2.5, 2.5)]))

        # squares

        self.sq1 = Polygon(
            outer=Ln([(1, 1), (5, 1), (5, 5), (1, 5)]),
            inner=[Ln([(2, 2), (4, 4), (2, 4)])]
        )

        # butterflies (malformed polygons)

        self.bf1 = Polygon(
            outer=Ln([(1, 1), (7, 4), (7, 1), (1, 4)])
        )

    def test_intersection_triangle_segment_01(self):

        s = Segment(Point(1.5, -1), Point(1.5, 1.5))

        # intersection is Point(1.5, 1)

        outer_inters, _ = self.t1.intersect_segment_base(s)

        assert len(outer_inters) == 3

        ip = outer_inters[0]
        assert ip.is_coincident(Point(1.5, 1))
        ip = outer_inters[1]
        assert ip is None
        ip = outer_inters[2]
        assert ip is None

    def test_intersection_triangle_segment_02(self):

        s = Segment(Point(1.5, -1), Point(1.5, 2))

        outer_inters, _ = self.t1.intersect_segment_base(s)

        assert len(outer_inters) == 3
        ip = outer_inters[0]
        assert ip.is_coincident(Point(1.5, 1))
        ip = outer_inters[1]
        assert ip.is_coincident(Point(1.5, 2))
        ip = outer_inters[2]
        assert ip.is_coincident(Point(1.5, 2))

    def test_intersection_triangle_segment_03(self):

        s = Segment(Point(1.5, -1), Point(1.5, 2.5))

        outer_inters, _ = self.t1.intersect_segment_base(s)

        assert len(outer_inters) == 3
        ip = outer_inters[0]
        assert ip.is_coincident(Point(1.5, 1))
        ip = outer_inters[1]
        assert ip.is_coincident(Point(1.5, 2))
        ip = outer_inters[2]
        assert ip.is_coincident(Point(1.5, 2))

    def test_intersection_triangle_segment_04(self):

        s = Segment(Point(2, -1), Point(2, 2.5))

        outer_inters, _ = self.t1.intersect_segment_base(s)

        assert len(outer_inters) == 3
        ip = outer_inters[0]
        assert ip.is_coincident(Point(2, 1))
        ip = outer_inters[1]
        assert ip.is_coincident(Point(2, 1))
        ip = outer_inters[2]
        assert ip is None

    def test_intersection_triangle_segment_05(self):

        s = Segment(Point(3, -1), Point(3, 2.5))

        outer_inters, _ = self.t1.intersect_segment_base(s)

        assert len(outer_inters) == 3

        ip = outer_inters[0]
        assert ip is None
        ip = outer_inters[1]
        assert ip is None
        ip = outer_inters[2]
        assert ip is None

    def test_intersection_triangle_segment_06(self):

        s = Segment(Point(0, 0), Point(5, 5))

        outer_inters, _ = self.t2.intersect_segment_base(s)

        assert len(outer_inters) == 3

        ip = outer_inters[0]
        assert ip.is_coincident(Point(1, 1))
        ip = outer_inters[1]
        assert ip.is_coincident(Point(2.5, 2.5))
        ip = outer_inters[2]
        assert isinstance(ip, Segment)
        assert ip.start_pt.is_coincident(Point(2.5, 2.5))
        assert ip.end_pt.is_coincident(Point(1, 1))

    def test_intersections_square_with_hole_w_segment_01(self):

        s = Segment(Point(1, 0), Point(1, 5))

        outer_inters, inner_inters = self.sq1.intersect_segment_base(s)

        assert len(outer_inters) == 4

        ip = outer_inters[0]
        assert ip.is_coincident(Point(1, 1))

        ip = outer_inters[1]
        assert ip is None

        ip = outer_inters[2]
        assert ip.is_coincident(Point(1, 5))

        ip = outer_inters[3]
        assert isinstance(ip, Segment)
        assert ip.start_pt.is_coincident(Point(1, 5))
        assert ip.end_pt.is_coincident(Point(1, 1))

        assert len(inner_inters) == 3

        ip = inner_inters[(0, 0)]
        assert ip is None

        ip = inner_inters[(0, 1)]
        assert ip is None

        ip = inner_inters[(0, 2)]
        assert ip is None

    def test_intersections_square_with_hole_w_segment_02(self):

        s = Segment(Point(0, 0), Point(6, 6))

        outer_inters, inner_inters = self.sq1.intersect_segment_base(s)

        assert len(outer_inters) == 4

        ip = outer_inters[0]
        assert ip.is_coincident(Point(1, 1))

        ip = outer_inters[1]
        assert ip.is_coincident(Point(5, 5))

        ip = outer_inters[2]
        assert ip.is_coincident(Point(5, 5))

        ip = outer_inters[3]
        assert ip.is_coincident(Point(1, 1))

        assert len(inner_inters) == 3

        ip = inner_inters[(0, 0)]
        assert isinstance(ip, Segment)
        assert ip.end_pt.is_coincident(Point(4, 4))
        assert ip.start_pt.is_coincident(Point(2, 2))

        ip = inner_inters[(0, 1)]
        assert ip.is_coincident(Point(4, 4))

        ip = inner_inters[(0, 2)]
        assert ip.is_coincident(Point(2, 2))

    def test_intersections_butterfly_w_segment_01(self):

        s = Segment(Point(-3, 3), Point(12, 3))

        outer_inters, _ = self.bf1.intersect_segment_base(s)

        assert len(outer_inters) == 4

        ip = outer_inters[0]
        assert ip.is_coincident(Point(5, 3))

        ip = outer_inters[1]
        assert ip.is_coincident(Point(7, 3))

        ip = outer_inters[2]
        assert ip.is_coincident(Point(3, 3))

        ip = outer_inters[3]
        assert ip.is_coincident(Point(1, 3))


