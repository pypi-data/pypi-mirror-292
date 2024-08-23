
import unittest

from geogst.core.geometries.polygons import *
from geogst.core.profiles.profilers import *


class TestSegmentProfilerPolygonIntersections(unittest.TestCase):

    def setUp(self):

        # triangles

        self.t1 = Polygon(outer=Ln([(1, 1), (2, 1), (1.5, 2)]))
        self.t2 = Polygon(outer=Ln([(1, 1), (4, 1), (2.5, 2.5)]))

        # squares

        self.sq1 = Polygon(
            outer=Ln([(1, 1), (5, 1), (5, 5), (1, 5)]),
            inner=[Ln([(2, 2), (4, 2), (4, 4), (2, 4)])]
        )

        # butterflies (malformed polygons)

        self.bf1 = Polygon(
            outer=Ln([(1, 1), (7, 4), (7, 1), (1, 4)])
        )

        self.bf2 = Polygon(
            outer=Ln([(1, 1), (7, 4), (7, 1), (1, 4)]),
            inner=[Ln([(2, 2), (6, 3), (6, 2), (2, 3)])]
        )

    def test_intersection_square_1(self):

        segment_prof = Segment(start_pt=Point(-3, 3), end_pt=Point(12, 3))

        sp = SegmentProfiler(segment=segment_prof)

        result = sp.intersect_polygon(self.sq1)

        print(f"Result: {result}")

        assert len(result) == 2

        assert result[0].start_pt.is_coincident(Point(1., 3.))
        assert result[0].end_pt.is_coincident(Point(2., 3.))

        assert result[1].start_pt.is_coincident(Point(4., 3.))
        assert result[1].end_pt.is_coincident(Point(5., 3.))

        segment_prof = Segment(start_pt=Point(-3, 1.01), end_pt=Point(12, 1.01))

        sp = SegmentProfiler(segment=segment_prof)

        result = sp.intersect_polygon(self.sq1)

        print(f"Result: {result}")

        assert len(result) == 1

        assert result[0].start_pt.is_coincident(Point(1., 1.01))
        assert result[0].end_pt.is_coincident(Point(5., 1.01))

        segment_prof = Segment(start_pt=Point(-3, 5.01), end_pt=Point(12, 5.01))

        sp = SegmentProfiler(segment=segment_prof)

        result = sp.intersect_polygon(self.sq1)

        print(f"Result: {result}")

        assert len(result) == 0

    def test_intersection_butterfly_01(self):

        segment_prof = Segment(start_pt=Point(-3, 3), end_pt=Point(12, 3))

        sp = SegmentProfiler(segment=segment_prof)

        result = sp.intersect_polygon(self.bf1)

        print(f"Result: {result}")

        for segment in result:
            print(segment)

    def test_intersection_butterfly_02(self):

        segment_prof = Segment(start_pt=Point(-3, 2.5), end_pt=Point(12, 2.5))

        sp = SegmentProfiler(segment=segment_prof)

        result = sp.intersect_polygon(self.bf2)

        print(f"Result: {result}")

        for segment in result:
            print(segment)



