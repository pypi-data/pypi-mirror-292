
import itertools
from functools import singledispatch

from enum import Enum

from math import fabs

from geogst.core.geometries.points import *
from geogst.core.geometries.checks import *


class Segment(Shape):

    proper_space = 1

    def __init__(self,
                 start_pt: Point,
                 end_pt: Point
                 ):
        """
        Creates a segment instance.

        :param start_pt: the start point.
        :param end_pt: the end point.
        :return: the new segment instance.
        """

        super(Segment, self).__init__()

        self._coords = np.vstack((start_pt.coords, end_pt.coords))

    @property
    def coords(self) -> np.ndarray:

        return self._coords

    @property
    def start_pt(self):
        """Return start point"""

        return Point(*tuple(self._coords[0]))

    @property
    def end_pt(self):
        """Return end point"""

        return Point(*tuple(self._coords[1]))

    def __repr__(self) -> str:
        """
        Represents a Segment instance.

        :return: the Segment representation.
        """

        return f"Segment(start_pt={self.start_pt}, end_pt={self.end_pt})"

    def __iter__(self):
        """
        Return the elements of a Segment, i.e., start and end point.
        """

        return (Point(*tuple(self.coords[i])) for i in range(2))

    def clone(self) -> 'Segment':

        return Segment(self.start_pt, self.end_pt)

    def as_2d(self) -> 'Segment':
        """
        Creates a 2D copy of the original segment.

        Examples:
         >>> s3 = Segment(Point(1,2,3), Point(4, 5, 6))
         >>> s3.as_2d()
         Segment(start_pt=Point([1. 2.]), end_pt=Point([4. 5.]))
        """

        return Segment(self.start_pt.as_point2d(), self.end_pt.as_point2d())

    @property
    def length(self) -> numbers.Real:
        """Returns the length of the segment.

        Examples:
         >>> Segment(Point(0, 0, 0), Point(3, 4, 5)).length
         7.0710678118654755
        """

        return np.linalg.norm((self.end_pt - self.start_pt).coords)

    def length_2d(self) -> numbers.Real:
        """
        Returns the horizontal (2D) length of the segment.

        :return: the horizontal length of the segment.
        """

        return np.linalg.norm((self.end_pt - self.start_pt).coords[:2])

    def length_3d(self) -> numbers.Real:
        """
        Returns the 3D length of the segment.

        :return: the 3D length of the segment.
        """

        return np.linalg.norm((self.end_pt - self.start_pt).coords[:3])

    def area(self):
        """Calculate shape area"""

        return 0.0

    def delta_x(self) -> numbers.Real:
        """
        X delta between segment end point and start point.

        :return: the horizontal, x-parallel distance between segment end point and start point.
        """

        return self.end_pt.x - self.start_pt.x

    def delta_y(self) -> numbers.Real:
        """
        Y delta between segment end point and start point.

        :return: the horizontal, y-parallel distance between segment end point and start point.
        """

        return self.end_pt.y - self.start_pt.y

    def delta_z(self) -> Union[type(None), numbers.Real]:
        """
        Z delta between segment end point and start point.

        :return: the vertical distance between segment end point and start point.
        """

        try:
            return self.end_pt.z - self.start_pt.z
        except:
            return None

    def x_range(self) -> Tuple[numbers.Real, numbers.Real]:

        if self.start_pt.x < self.end_pt.x:
            return self.start_pt.x, self.end_pt.x
        else:
            return self.end_pt.x, self.start_pt.x

    def y_range(self) -> Tuple[numbers.Real, numbers.Real]:

        if self.start_pt.y < self.end_pt.y:
            return self.start_pt.y, self.end_pt.y
        else:
            return self.end_pt.y, self.start_pt.y

    def z_range(self) -> Tuple[numbers.Real, numbers.Real]:

        if self.start_pt.z < self.end_pt.z:
            return self.start_pt.z, self.end_pt.z
        else:
            return self.end_pt.z, self.start_pt.z

    def left_norm_vers2d(self) -> Vect2D:
        """
        Returns the left horizontal normal versor.

        :return: the left horizontal normal versor.
        """

        return Vect2D(
            x=-self.as_versor2d().y,
            y=self.as_versor2d().x
        )

    def right_norm_vers2d(self) -> Vect2D:
        """
        Returns the right horizontal normal versor.

        :return: the right horizontal normal versor.
        """

        return Vect2D(
            x=self.as_versor2d().y,
            y=-self.as_versor2d().x
        )

    def as_vector2d(self) -> Vect2D:
        """
        Convert a segment to a vector.
        """

        return Vect2D(
            x=self.delta_x(),
            y=self.delta_y()
        )

    def as_versor2d(self) -> Optional[Vect2D]:
        """
        Convert a segment to an optional versor.
        """

        return self.as_vector2d().versor()

    def as_vector3d(self) -> Vect3D:
        """
        Convert a segment to a vector.
        """

        return Vect3D(
            x=self.delta_x(),
            y=self.delta_y(),
            z=self.delta_z()
        )

    def as_versor3d(self) -> Vect3D:
        """
        Convert a segment to a versor.
        """

        vers, _ = self.as_vector3d().to_versor()

        return vers

    def conn_to_other(self,
                      another: 'Segment',
                      tol: numbers.Real = 1e-12
                      ) -> bool:
        """
        Check whether the first segment is sequentially connected to the second one.

        :param another: a segment to check for.
        :param tol: tolerance for distance between points.
        :return: whether the first segment is sequentially connected to the second one.

        Examples:
          >>> s1 = Segment(Point(0,0), Point(1,0))
          >>> s2 = Segment(Point(1,0), Point(2,0))
          >>> s1.conn_to_other(s2)
          True
          >>> s1 = Segment(Point(0,0,0), Point(1,0,0))
          >>> s2 = Segment(Point(1,0,0), Point(2,0,0))
          >>> s1.conn_to_other(s2)
          True
        """

        return self.end_pt.is_coincident(
            other=another.start_pt,
            tolerance=tol)

    def point_at_factor(self,
                        scale_factor: numbers.Real
                        ) -> Point:
        """
        Returns a point aligned with the segment
        and lying at given scale factor, where 1 is segment length
        and 0 is segment start.

        :param scale_factor: the scale factor, where 1 is the segment length.
        :return: Point at scale factor

        Examples:
          >>> s = Segment(Point(0,0), Point(1,0))
          >>> s.point_at_factor(0)
          Point([0. 0.])
          >>> s.point_at_factor(0.5)
          Point([0.5 0. ])
          >>> s.point_at_factor(1)
          Point([1. 0.])
          >>> s.point_at_factor(-1)
          Point([-1. 0.])
          >>> s.point_at_factor(-2)
          Point([-2.  0.])
          >>> s.point_at_factor(2)
          Point([2. 0.])
          >>> s = Segment(Point(0,0), Point(1,1))
          >>> s.point_at_factor(0.5)
          Point([0.5 0.5])
          >>> s = Segment(Point(0,0), Point(4,0))
          >>> s.point_at_factor(7.5)
          Point([30.  0.])
          >>> s = Segment(Point(0,0,0), Point(1,0,0))
          >>> s.point_at_factor(0)
          Point([0. 0. 0.])
          >>> s.point_at_factor(0.5)
          Point([0.5 0.  0. ])
          >>> s.point_at_factor(1)
          Point([1. 0. 0.])
          >>> s.point_at_factor(-1)
          Point([-1.  0.  0.])
          >>> s.point_at_factor(-2)
          Point([-2.  0.  0.])
          >>> s.point_at_factor(2)
          Point([2. 0. 0.])
          >>> s = Segment(Point(0,0,0), Point(0,0,1))
          >>> s.point_at_factor(0)
          Point([0. 0. 0.])
          >>> s.point_at_factor(0.5)
          Point([0.  0.  0.5])
          >>> s.point_at_factor(1)
          Point([0. 0. 1.])
          >>> s.point_at_factor(-1)
          Point([ 0.  0. -1.])
          >>> s.point_at_factor(-2)
          Point([ 0.  0. -2.])
          >>> s.point_at_factor(2)
          Point([0. 0. 2.])
          >>> s = Segment(Point(0,0,0), Point(1,1,1))
          >>> s.point_at_factor(0.5)
          Point([0.5 0.5 0.5])
          >>> s = Segment(Point(0,0,0), Point(4,0,0))
          >>> s.point_at_factor(7.5)
          Point([30.  0.  0.])
        """

        dx = self.delta_x() * scale_factor
        dy = self.delta_y() * scale_factor
        dz = None if self.delta_z() is None else self.delta_z() * scale_factor

        if dz is None:
            return Point(
                self.start_pt.x + dx,
                self.start_pt.y + dy
            )
        else:
            return Point(
                self.start_pt.x + dx,
                self.start_pt.y + dy,
                self.start_pt.z + dz
            )

    def midpoint(self) -> Point:
        """
        Returns the mid-point of the segment.

        Examples:
         >>> Segment(Point(1, 1), Point(3, 3)).midpoint()
         Point([2. 2.])
         >>> Segment(Point(0, 0), Point(0, 9)).midpoint()
         Point([0. 4.5])
         >>> Segment(Point(0, 0), Point(0, 0)).midpoint()
         Point([0. 0.])
         >>> Segment(Point(0, 0), Point(0, 20)).midpoint()
         Point([ 0. 10.])
        """

        return self.point_at_factor(0.5)

    def contains_pt(self,
                    pt: Point
                    ) -> bool:
        """
        Checks whether a point is contained in a segment.

        :param pt: the point for which to check containement.
        :return: whether a point is contained in a segment.

        Examples:
          >>> segment = Segment(Point(0, 0), Point(1, 0))
          >>> segment.contains_pt(Point(0, 0))
          True
          >>> segment.contains_pt(Point(1, 0))
          True
          >>> segment.contains_pt(Point(0.5, 0))
          True
          >>> segment.contains_pt(Point(0.5, 0.00001))
          False
          >>> segment.contains_pt(Point(1.00001, 0))
          False
          >>> segment.contains_pt(Point(0.000001, 0))
          True
          >>> segment.contains_pt(Point(-0.000001, 0))
          False
          >>> segment.contains_pt(Point(0.5, 1000))
          False
          >>> segment = Segment(Point(0, 0), Point(0, 1))
          >>> segment.contains_pt(Point(0, 0))
          True
          >>> segment.contains_pt(Point(0, 0.5))
          True
          >>> segment.contains_pt(Point(0, 1))
          True
          >>> segment.contains_pt(Point(0, 1.5))
          False
          >>> segment = Segment(Point(0, 0), Point(1, 1))
          >>> segment.contains_pt(Point(0.5, 0.5))
          True
          >>> segment.contains_pt(Point(1, 1))
          True
          >>> segment = Segment(Point(1, 2), Point(9, 8))
          >>> segment.contains_pt(segment.point_at_factor(0.745))
          True
          >>> segment.contains_pt(segment.point_at_factor(1.745))
          False
          >>> segment.contains_pt(segment.point_at_factor(-0.745))
          False
          >>> segment.contains_pt(segment.point_at_factor(0))
          True
          >>> segment = Segment(Point(0, 0, 0), Point(1, 0, 0))
          >>> segment.contains_pt(Point(0, 0, 0))
          True
          >>> segment.contains_pt(Point(1, 0, 0))
          True
          >>> segment.contains_pt(Point(0.5, 0, 0))
          True
          >>> segment.contains_pt(Point(0.5, 0.00001, 0))
          False
          >>> segment.contains_pt(Point(0.5, 0, 0.00001))
          False
          >>> segment.contains_pt(Point(1.00001, 0, 0))
          False
          >>> segment.contains_pt(Point(0.000001, 0, 0))
          True
          >>> segment.contains_pt(Point(-0.000001, 0, 0))
          False
          >>> segment.contains_pt(Point(0.5, 1000, 1000))
          False
          >>> segment = Segment(Point(0, 0, 0), Point(0, 1, 0))
          >>> segment.contains_pt(Point(0, 0, 0))
          True
          >>> segment.contains_pt(Point(0, 0.5, 0))
          True
          >>> segment.contains_pt(Point(0, 1, 0))
          True
          >>> segment.contains_pt(Point(0, 1.5, 0))
          False
          >>> segment = Segment(Point(0, 0, 0), Point(1, 1, 1))
          >>> segment.contains_pt(Point(0.5, 0.5, 0.5))
          True
          >>> segment.contains_pt(Point(1, 1, 1))
          True
          >>> segment = Segment(Point(1,2,3), Point(9,8,2))
          >>> segment.contains_pt(segment.point_at_factor(0.745))
          True
          >>> segment.contains_pt(segment.point_at_factor(1.745))
          False
          >>> segment.contains_pt(segment.point_at_factor(-0.745))
          False
          >>> segment.contains_pt(segment.point_at_factor(0))
          True
        """

        segment_length = self.length
        length_startpt_pt = self.start_pt.distance(pt)
        length_endpt_pt = self.end_pt.distance(pt)

        return are_close(
            a=segment_length,
            b=length_startpt_pt + length_endpt_pt
        )

    def point2d_at_hor_dist(self,
                            distance: numbers.Real
                            ) -> Point:
        """
        Returns a point aligned with the segment
        and lying at given distance from the segment start.

        :param distance: the distance from segment start
        :return: point at provided distance from segment start

        Examples:
          >>> s = Segment(Point(0,0), Point(1,0))
          >>> s.point2d_at_hor_dist(0)
          Point([0. 0.])
          >>> s.point2d_at_hor_dist(0.5)
          Point([0.5 0. ])
          >>> s.point2d_at_hor_dist(1)
          Point([1. 0.])
          >>> s.point2d_at_hor_dist(2)
          Point([2. 0.])
          >>> s = Segment(Point(0,0), Point(3, 4))
          >>> s.point2d_at_hor_dist(0)
          Point([0. 0.])
          >>> s.point2d_at_hor_dist(2.5)
          Point([1.5 2. ])
          >>> s.point2d_at_hor_dist(5)
          Point([3. 4.])
          >>> s.point2d_at_hor_dist(10)
          Point([6. 8.])
        """

        scale_factor_2d = distance / self.length_2d()

        dx = self.delta_x() * scale_factor_2d
        dy = self.delta_y() * scale_factor_2d

        return Point(
            self.start_pt.x + dx,
            self.start_pt.y + dy
        )

    def densify_as_line2d(self,
                          densify_distance: numbers.Real
                          ) -> 'Ln':
        """
        Densify a segment by adding additional points
        separated a distance equal to densify_distance.
        The result is no longer a Segment instance, instead it is a Ln instance.

        :param densify_distance: the densify distance
        :return: a line
        """

        return Ln.from_points(*self.densify_as_points2d(densify_distance=densify_distance))

    def densify_as_pts2d(self,
        densify_distance: numbers.Real,
        start_offset: numbers.Real = 0.0
    ) -> Tuple[Union[type(None), List[Point]], Error]:
        """
        Densify a segment as a list of points, by using the provided densify distance.

        :param densify_distance: the densify distance
        :param start_offset: the offset from the start point from which to densify.
        :return: an optional list of points and the error status.
        """

        try:

            length2d = self.length_2d()

            vers_2d = self.as_versor2d()

            step_vector = vers_2d.scale(densify_distance)

            if start_offset == 0.0:
                start_point = self.start_pt.as_point2d()
            else:
                start_point = self.point2d_at_hor_dist(start_offset)

            pts = [start_point]

            n = 0
            while True:
                n += 1
                shift_vector = step_vector.scale(n)
                new_pt = start_point.shift(shift_vector.x, shift_vector.y)
                distance = self.start_pt.distance(new_pt)
                if distance >= length2d:
                    break
                pts.append(new_pt)

            pts.append(self.end_pt)

            return pts, Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc()
            )

    def densify_as_points2d(self,
                            densify_distance: numbers.Real,
                            start_offset: numbers.Real = 0.0
                            ) -> List[Point]:
        """
        DEPRECATED: use 'densify_as_pts2d'.

        Densify a segment as a list of points, by using the provided densify distance.

        :param densify_distance: the densify distance
        :param start_offset: the offset from the start point from which to densify.
        :return: a list of points
        """

        length2d = self.length_2d()

        vers_2d = self.as_versor2d()

        step_vector = vers_2d.scale(densify_distance)

        if start_offset == 0.0:
            start_point = self.start_pt.as_point2d()
        else:
            start_point = self.point2d_at_hor_dist(start_offset)

        pts = [start_point]

        n = 0
        while True:
            n += 1
            shift_vector = step_vector.scale(n)
            new_pt = start_point.shift(shift_vector.x, shift_vector.y)
            distance = self.start_pt.distance(new_pt)
            if distance >= length2d:
                break
            pts.append(new_pt)

        pts.append(self.end_pt)

        return pts

    def point_projection(self,
        point: Point
    ) -> Union[type(None), Point]:
        """
        Return the point projection on the segment.

        Examples:
          >>> s = Segment(start_pt=Point(0,0,0), end_pt=Point(1,0,0))
          >>> p = Point(0.5, 1, 4)
          >>> s.point_projection(p)
          Point([0.5 0.  0. ])
          >>> s = Segment(start_pt=Point(0,0,0), end_pt=Point(4,0,0))
          >>> p = Point(7.5, 19.2, -14.72)
          >>> s.point_projection(p)
          Point([7.5 0.  0. ])
        """

        other_segment = Segment(
            self.start_pt,
            point
        )

        scale_factor = self.as_vector3d().scalar_projection(other_segment.as_vector3d()) / self.length

        return self.point_at_factor(scale_factor)

    def distance_to_point(self,
                          point: Point
                          ) -> Union[type(None), numbers.Real]:
        """
        Returns the point distance to the segment.

        :param point: the point to calculate the distance with
        :return: the distance of the point to the segment

        Examples:
          >>> s = Segment(Point(0,0,0), Point(0,0,4))
          >>> s.distance_to_point(Point(-17.2, 0.0, -49))
          17.2
          >>> s.distance_to_point(Point(-17.2, 1.22, -49))
          17.24321315764553
        """

        pt_proj = self.point_projection(point)

        return point.distance(pt_proj)

    def segment_2d_m(self) -> Optional[numbers.Real]:

        denom = self.end_pt.x - self.start_pt.x

        if denom == 0.0:
            return None

        return (self.end_pt.y - self.start_pt.y) / denom

    def segment_2d_p(self) -> Optional[numbers.Real]:

        s2d_m = self.segment_2d_m()

        if s2d_m is None:
            return None

        return self.start_pt.y - s2d_m * self.start_pt.x

    def intersect_segments2d(
            self,
            other: 'Segment',
            tol: numbers.Real = PRACTICAL_MIN_DIST
    ) -> Union[type(None), Point, 'Segment']:
        """
        Determines the optional point or segment intersection between the segment pair.

        :param other: the second segment
        :param tol: the distance tolerance for collapsing a intersection segment into a point
        :return: the optional point or segment intersection between the segment pair.

        Examples:
          >>> s2 = Segment(Point(0,0), Point(1,0))
          >>> s1 = Segment(Point(0,0), Point(1,0))
          >>> s1.intersect_segments2d(s2)
          Segment(start_pt=Point([0. 0.]), end_pt=Point([1. 0.]))
          >>> s1 = Segment(Point(-2,0), Point(-1,0))
          >>> s1.intersect_segments2d(s2) is None
          True
          >>> s1 = Segment(Point(-2,0), Point(0,0))
          >>> s1.intersect_segments2d(s2)
          Point([0. 0.])
          >>> s1 = Segment(Point(-2,0), Point(0.5,0.0))
          >>> s1.intersect_segments2d(s2)
          Segment(start_pt=Point([0. 0.]), end_pt=Point([0.5 0. ]))
          >>> s1 = Segment(Point(-2,0), Point(1,0))
          >>> s1.intersect_segments2d(s2)
          Segment(start_pt=Point([0. 0.]), end_pt=Point([1. 0.]))
          >>> s1 = Segment(Point(-2,0), Point(2,0))
          >>> s1.intersect_segments2d(s2)
          Segment(start_pt=Point([0. 0.]), end_pt=Point([1. 0.]))
          >>> s1 = Segment(Point(0,0), Point(0.5,0))
          >>> s1.intersect_segments2d(s2)
          Segment(start_pt=Point([0. 0.]), end_pt=Point([0.5 0. ]))
          >>> s1 = Segment(Point(0.25,0), Point(0.75,0))
          >>> s1.intersect_segments2d(s2)
          Segment(start_pt=Point([0.25 0.  ]), end_pt=Point([0.75 0.  ]))
          >>> s1 = Segment(Point(0.25,0), Point(1,0))
          >>> s1.intersect_segments2d(s2)
          Segment(start_pt=Point([0.25 0.  ]), end_pt=Point([1. 0.]))
          >>> s1 = Segment(Point(0.25,0), Point(1.25,0))
          >>> s1.intersect_segments2d(s2)
          Segment(start_pt=Point([0.25 0.  ]), end_pt=Point([1. 0.]))
          >>> s1 = Segment(Point(0,0), Point(1.25,0))
          >>> s1.intersect_segments2d(s2)
          Segment(start_pt=Point([0. 0.]), end_pt=Point([1. 0.]))
          >>> s1 = Segment(Point(1,0), Point(1.25,0))
          >>> s1.intersect_segments2d(s2)
          Point([1. 0.])
          >>> s2 = Segment(Point(0,0), Point(1,1))
          >>> s1 = Segment(Point(0.25,0.25), Point(0.75,0.75))
          >>> s1.intersect_segments2d(s2)
          Segment(start_pt=Point([0.25 0.25]), end_pt=Point([0.75 0.75]))
          >>> s1 = Segment(Point(0.25,0.25), Point(1.75,1.75))
          >>> s1.intersect_segments2d(s2)
          Segment(start_pt=Point([0.25 0.25]), end_pt=Point([1. 1.]))
          >>> s1 = Segment(Point(0.25,0.25), Point(1.75,0))
          >>> s1.intersect_segments2d(s2)
          Point([0.25 0.25])
          >>> s1 = Segment(Point(0.25,1), Point(0.75,0.75))
          >>> s1.intersect_segments2d(s2)
          Point([0.75 0.75])
          >>> s2 = Segment(Point(-1,-1), Point(1,1))
          >>> s1 = Segment(Point(-1,1), Point(1,-1))
          >>> s1.intersect_segments2d(s2)
          Point([0. 0.])
        """


        try:

            segment1 = self.as_2d()
            other = other.as_2d()

            s1_startpt_inside = segment1.segment_start_in(other)
            s2_startpt_inside = other.segment_start_in(segment1)

            s1_endpt_inside = segment1.segment_end_in(other)
            s2_endpt_inside = other.segment_end_in(segment1)

            elements = [s1_startpt_inside, s2_startpt_inside, s1_endpt_inside, s2_endpt_inside]

            if all(elements):
                return segment1.clone()

            if s1_startpt_inside and s1_endpt_inside:
                return segment1.clone()

            if s2_startpt_inside and s2_endpt_inside:
                return other.clone()

            if s1_startpt_inside and s2_startpt_inside:
                return point_or_segment2d(
                    segment1.start_pt,
                    other.start_pt,
                    tol=tol
                )

            if s1_startpt_inside and s2_endpt_inside:
                return point_or_segment2d(
                    segment1.start_pt,
                    other.end_pt,
                    tol=tol
                )

            if s1_endpt_inside and s2_startpt_inside:
                return point_or_segment2d(
                    other.start_pt,
                    segment1.end_pt,
                    tol=tol
                )

            if s1_endpt_inside and s2_endpt_inside:
                return point_or_segment2d(
                    segment1.end_pt,
                    other.end_pt,
                    tol=tol
                )

            if s1_startpt_inside:
                return segment1.start_pt

            if s1_endpt_inside:
                return segment1.end_pt

            if s2_startpt_inside:
                return other.start_pt

            if s2_endpt_inside:
                return other.end_pt

            shortest_segm_or_pt = shortest_segment_or_point2d(
                segment1,
                other,
                tol=tol
            )

            if not shortest_segm_or_pt:
                return None

            if not isinstance(shortest_segm_or_pt, Point):
                return None

            inters_pt = shortest_segm_or_pt

            if not segment1.contains_pt(inters_pt):
                return None

            if not other.contains_pt(inters_pt):
                return None

            return inters_pt

        except Exception as e:

            print(e)
            return None

    def intersection_2d_pt(self,
                           another: 'Segment'
                           ) -> Optional[Point]:
        """

        :param another:
        :return:
        """

        s_len2d = self.length_2d()
        a_len2d = another.length_2d()

        if s_len2d == 0.0 or a_len2d == 0.0:
            return None

        if self.start_pt.x == self.end_pt.x:  # self segment parallel to y axis
            x0 = self.start_pt.x
            m1, p1 = another.segment_2d_m(), another.segment_2d_p()
            if m1 is None:
                return None
            y0 = m1 * x0 + p1
        elif another.start_pt.x == another.end_pt.x:  # another segment parallel to y axis
            x0 = another.start_pt.x
            m1, p1 = self.segment_2d_m(), self.segment_2d_p()
            if m1 is None:
                return None
            y0 = m1 * x0 + p1
        else:  # no segment parallel to y axis
            m0, p0 = self.segment_2d_m(), self.segment_2d_p()
            m1, p1 = another.segment_2d_m(), another.segment_2d_p()
            if m0 is None or m1 is None:
                return None
            x0 = (p1 - p0) / (m0 - m1)
            y0 = m0 * x0 + p0

        return Point(x0, y0)

    def point_distance_from_start(self,
                                  point: Point
                                  ) -> Union[type(None), numbers.Real]:
        """
        Calculates the optional distance of the point along the segment.
        A zero value is for a point coinciding with the start point.
        Returns None if the point is not contained in the segment.

        :param point: the point to calculate the optional distance in the segment.
        :return: the optional distance of the point along the segment.
        """

        if not self.contains_pt(point):
            return None

        dist = self.start_pt.distance(point)

        return dist

    def subelement_distance_from_start(self,
                                       subelement: 'UnionPtSegment2D'
                                       ) -> Union[type(None), numbers.Real, Tuple[Union[type(None), numbers.Real], Union[type(None), numbers.Real]]]:
        """
        Calculates subelement distance (s) from segment start.
        Subelement is assumed to be fully contained in the segment (extremes comprised).
        """

        if isinstance(subelement, Point):
            return self.point_distance_from_start(subelement)
        elif isinstance(subelement, Segment):
            distance_start_segment = self.point_distance_from_start(subelement.start_pt)
            distance_end_segment = self.point_distance_from_start(subelement.end_pt)
            return distance_start_segment, distance_end_segment
        else:
            return None

    @classmethod
    def random(cls,
        lower_boundary: float = -MAX_SCALAR_VALUE,
        upper_boundary: float = MAX_SCALAR_VALUE):
        """
        Creates a random segment.

        :return: random segment
        """

        return cls(
            start_pt=Point.random(lower_boundary, upper_boundary),
            end_pt=Point.random(lower_boundary, upper_boundary)
        )

    def same_start(self,
                   another: 'Segment',
                   tol: numbers.Real = 1e-12
                   ) -> Union[type(None), bool]:
        """
        Check whether the two segments have the same start point.

        :param another: a segment to check for.
        :param tol: tolerance for distance between points.
        :return: whether the two segments have the same start point.

        Examples:
          >>> s1 = Segment(Point(0,0,0), Point(1,0,0))
          >>> s2 = Segment(Point(0,0,0), Point(0,1,0))
          >>> s1.same_start(s2)
          True
          >>> s1 = Segment(Point(0,0), Point(1,0))
          >>> s2 = Segment(Point(0,0), Point(0,1))
          >>> s1.same_start(s2)
          True
        """

        return self.start_pt.is_coincident(
            other=another.start_pt,
            tolerance=tol
        )

    def same_end(self,
                 another: 'Segment',
                 tol: numbers.Real = 1e-12
                 ) -> Union[type(None), bool]:
        """
        Check whether the two segments have the same end point.

        :param another: a segment to check for.
        :param tol: tolerance for distance between points.
        :return: whether the two segments have the same end point.

        Examples:
          >>> s1 = Segment(Point(0,0,0), Point(1,0,0))
          >>> s2 = Segment(Point(2,0,0), Point(1,0,0))
          >>> s1.same_end(s2)
          True
          >>> s1 = Segment(Point(0,0), Point(1,0))
          >>> s2 = Segment(Point(2,0), Point(1,0))
          >>> s1.same_end(s2)
          True
        """

        return self.end_pt.is_coincident(
            other=another.end_pt,
            tolerance=tol)

    def scale(self,
        scale_factor
    ) -> Union[type(None), 'Segment']:
        """
        Scale a segment by the given scale_factor.
        Start point does not change.

        :param scale_factor: the scale factor, where 1 is the segment length. May be negative.
        :return: Point at scale factor
        """

        end_pt = self.point_at_factor(scale_factor)

        return Segment(
            self.start_pt,
            end_pt)
    def rotate(self,
        rotation_axis: 'RotationAxis',
        center_point: 'Point' = None
        ) -> Union[type(None), 'Segment']:
        """
        Rotates a segment.

        :param rotation_axis:
        :param center_point:
        :return: the rotated segment

        Examples:
        >>> seg = Segment(Point(0,0,0), Point(0,0,1))
        >>> rot_ax = RotationAxis(0, 0, 90)
        >>> seg.rotate(rot_ax)
        Segment(start_pt=Point([0. 0. 0.]), end_pt=Point([1.00000000e+00 0.00000000e+00 2.22044605e-16]))
        >>> rot_ax = RotationAxis(0, 0, 180)
        >>> centr_pt = Point(0,0,0.5)
        >>> seg.rotate(rotation_axis=rot_ax, center_point=centr_pt)
        Segment(start_pt=Point([-6.123234e-17  0.000000e+00  1.000000e+00]), end_pt=Point([6.123234e-17 0.000000e+00 0.000000e+00]))
        >>> seg = Segment(Point(0,0,0), Point(1,1,0))
        >>> centr_pt = Point(1,0,0)
        >>> rot_ax = RotationAxis(0, 90, 90)
        >>> seg.rotate(rotation_axis=rot_ax, center_point=centr_pt)
        Segment(start_pt=Point([1.000000e+00 1.000000e+00 6.123234e-17]), end_pt=Point([ 2.00000000e+00  2.22044605e-16 -6.12323400e-17]))
        >>> seg = Segment(Point(1,1,1), Point(0,0,0))
        >>> rot_ax = RotationAxis(135, 0, 180)
        >>> centr_pt = Point(0.5,0.5,0.5)
        >>> seg.rotate(rotation_axis=rot_ax, center_point=centr_pt)
        Segment(start_pt=Point([1.66533454e-16 0.00000000e+00 1.11022302e-16]), end_pt=Point([1. 1. 1.]))
        """

        start_pt, end_pt = self

        rotated_start_pt = start_pt.rotate(
            rotation_axis=rotation_axis,
            center_point=center_point
        )

        if rotated_start_pt is None:
            return None

        rotated_end_pt = end_pt.rotate(
            rotation_axis=rotation_axis,
            center_point=center_point
        )

        if rotated_end_pt is None:
            return None

        return Segment(
            start_pt=rotated_start_pt,
            end_pt=rotated_end_pt
        )

    def shift(self,
              dx: numbers.Real,
              dy: numbers.Real
    ) -> 'Segment':
        """
        Shift a segment by dx and dy
        """

        return Segment(
            self.start_pt.shift(dx, dy),
            self.end_pt.shift(dx, dy)
        )

    def segment_start_in(self,
                         another: 'Segment'
                         ) -> bool:
        """
        Check whether the second segment contains the first segment start point.

        :param another: a segment to check for.
        :type another: Segment.
        :return: whether the second segment contains the first segment start point.
        :rtype: bool.

        Examples:
          >>> s1 = Segment(Point(0,0), Point(1,0))
          >>> s2 = Segment(Point(-0.5,0), Point(0.5,0))
          >>> s1.segment_start_in(s2)
          True
          >>> s1 = Segment(Point(0,0), Point(1,1))
          >>> s1.segment_start_in(s2)
          True
          >>> s1 = Segment(Point(0,1), Point(1,1))
          >>> s1.segment_start_in(s2)
          False
          >>> s1 = Segment(Point(-1,-1), Point(1,1))
          >>> s1.segment_start_in(s2)
          False
          >>> s1 = Segment(Point(0,0,0), Point(1,0,0))
          >>> s2 = Segment(Point(-0.5,0,0), Point(0.5,0,0))
          >>> s1.segment_start_in(s2)
          True
          >>> s1 = Segment(Point(0,0,0), Point(1,1,1))
          >>> s1.segment_start_in(s2)
          True
          >>> s1 = Segment(Point(0,1,0), Point(1,1,1))
          >>> s1.segment_start_in(s2)
          False
          >>> s1 = Segment(Point(-1,-1,-1), Point(1,1,1))
          >>> s1.segment_start_in(s2)
          False
        """

        return another.contains_pt(self.start_pt)

    def segment_end_in(self,
                       another: 'Segment'
                       ) -> bool:
        """
        Check whether the second segment contains the first segment end point.

        :param another: a segment to check for.
        :type another: Segment.
        :return: whether the second segment contains the first segment end point.
        :rtype: bool.

        Examples:
          >>> s1 = Segment(Point(0,0), Point(1,0))
          >>> s2 = Segment(Point(-0.5,0), Point(0.5,0))
          >>> s1.segment_end_in(s2)
          False
          >>> s1 = Segment(Point(0,0), Point(1,1))
          >>> s1.segment_end_in(s2)
          False
          >>> s1 = Segment(Point(0,1), Point(1,1))
          >>> s2 = Segment(Point(1,1), Point(0.5,0))
          >>> s1.segment_end_in(s2)
          True
          >>> s1 = Segment(Point(-1,-1), Point(1,1))
          >>> s2 = Segment(Point(0,2), Point(2,0))
          >>> s1.segment_end_in(s2)
          True
          >>> s1 = Segment(Point(0,0,0), Point(1,0,0))
          >>> s2 = Segment(Point(-0.5,0,0), Point(0.5,0,0))
          >>> s1.segment_end_in(s2)
          False
          >>> s1 = Segment(Point(0,0,0), Point(1,1,1))
          >>> s1.segment_end_in(s2)
          False
          >>> s1 = Segment(Point(0,1,0), Point(1,1,1))
          >>> s2 = Segment(Point(1,1,1), Point(0.5,0,0))
          >>> s1.segment_end_in(s2)
          True
          >>> s1 = Segment(Point(-1,-1,3), Point(1,1,3))
          >>> s2 = Segment(Point(0,2,3), Point(2,0,3))
          >>> s1.segment_end_in(s2)
          True
        """

        return another.contains_pt(self.end_pt)

    def tan_slope_angle(self) -> Union[type(None), numbers.Real]:
        """
        Calculates the delta z - delta s ratio of a segment.

        :return: the ratio.
        """

        len2d = self.length_2d()

        if len2d == 0.0:
            return None

        return self.delta_z() / len2d

    def slope_rad(self) -> Union[type(None), numbers.Real]:
        """
        Calculates the slope in radians of the segment.
        Positive is downward point, negative upward pointing.

        :return: the slope as radians.
        """

        delta_zs = self.tan_slope_angle()

        if delta_zs is None:
            return None
        else:
            return - math.atan(delta_zs)


UnionPtSegment2D = Union[Point, Segment]


class Ln(Shape):

    proper_space = 1

    def __init__(self,
        coords: Optional[Union[type(None), np.ndarray, List[Tuple[numbers.Real]]]] = None
    ):

        if coords is not None:
            coords = np.copy(np.asarray(coords))

        self._coords = coords

    def num_points(self) -> numbers.Integral:
        """
        Return the number of points.

        Examples:
         >>> Ln().num_points()
         0
        """

        return self._coords.shape[0] if self._coords is not None else 0

    def __repr__(self) -> str:
        """
        Represents a Ln instance as a shortened text.

        :return: a textual shortened representation of a Ln instance.
        :rtype: str.
        """

        n_pts = self.num_points()

        if n_pts == 0:
            txt = "Empty Ln"
        elif n_pts <= 4:
            txt = f"Ln with {n_pts} point(s): " + ", ".join([f"{pt}" for pt in self.pts()])
        else:
            txt = f"Ln with {n_pts} points: {self.pt(0)}, {self.pt(1)}, .., {self.pt(-2)}, {self.pt(-1)}"

        return txt

    @classmethod
    def from_points(cls,
        *points: Point):
        """
        Create a line given a list of points.

        Examples:
         >>> Ln.from_points(Point(0,0,0), Point(1,1,1), Point(2,2,2))
         Ln with 3 point(s): Point([0. 0. 0.]), Point([1. 1. 1.]), Point([2. 2. 2.])
        """

        pt_coords_arrays = [pt.coords for pt in points]

        arr = np.vstack(pt_coords_arrays)

        return cls(arr)

    @classmethod
    def fromCoordinates(cls,
                        *coordinates: List[numbers.Real]
                        ) -> 'Ln':
        """
        Create a Ln instance from a list of coordinates.

        Example:
          >>> Ln.fromCoordinates([0, 0], [1, 0], [0, 1])
          Ln with 3 point(s): Point([0. 0.]), Point([1. 0.]), Point([0. 1.])
        """

        return cls(np.vstack(coordinates))

    @property
    def coords(self) -> Union[type(None), np.ndarray]:
        """
        Returns the coordinates array.
        """

        return self._coords

    @property
    def closed(self) -> Union[type(None), bool]:
        """
        Whether the line is closed.

        Examples:
         >>> Ln().closed is None
         True
         >>> Ln([(1, 1), (2, 2)]).closed
         False
         >>> Ln([(1, 1), (2, 2), (3, 3), (1, 1)]).closed
         True
        """

        num_pts = self.num_points()

        if num_pts == 0:
            return None
        elif num_pts < 3:
            return False
        else:
            return np.all(self.coords[0, :] == self.coords[-1, :])

    def close(self) -> Union[type(None), 'Ln']:
        """
        Returns a closed copy of the source line.

        Examples:
         >>> Ln().close() is None
         True
         >>> Ln([(1, 1)]).close() is None
         True
         >>> Ln([(1, 1), (2, 2)]).close()
         Ln with 3 point(s): Point([1. 1.]), Point([2. 2.]), Point([1. 1.])
         >>> Ln([(1, 1), (2, 2), (3, 3), (1, 1)]).close()
         Ln with 4 point(s): Point([1. 1.]), Point([2. 2.]), Point([3. 3.]), Point([1. 1.])
        """

        num_pts = self.num_points()

        if num_pts < 2:
            return None

        if self.closed:
            return self.clone()

        return Ln(np.vstack([self.coords, self.coords[0, :]]))

    def area(self):
        """Calculate shape area"""

        return 0.0

    def clone(self) -> 'Ln':
        """
        Clone a line.

        :return: the cloned line
        """

        return Ln(self.coords)

    def reversed(self) -> 'Ln':
        """
        Reverse the line points.

        :return: the reversed line.

        Examples:
         >>> l = Ln([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
         >>> l.reversed()
         Ln with 3 point(s): Point([7. 8. 9.]), Point([4. 5. 6.]), Point([1. 2. 3.])
        """

        return Ln(np.flipud(self.coords))

    def as_2d(self) -> 'Ln':
        """
        Converts to a 2D line.
        """

        return Ln(self.coords[:, 0:2])

    def pt(self,
           ndx: numbers.Integral
    ) -> Union[type(None), Point]:
        """
        Returns the point at given index.

        Examples:
         >>> l = Ln.from_points(Point(1,2,3), Point(4,5,6), Point(7,8,9))
         >>> l.pt(2)
         Point([7. 8. 9.])
         >>> l.pt(0)
         Point([1. 2. 3.])
         >>> l.pt(4)
         None
         >>> l.pt(-1)
         Point([7. 8. 9.])
         >>> l.pt(-4)
         None
        """

        num_pts = self.num_points()

        if num_pts == 0:
            return None

        if -num_pts <= ndx < num_pts:
            return Point(*tuple(self.coords[ndx, :]))

        return None

    def pts(self) -> List[Point]:
        """
        Returns the list of points making up the line.

        Examples:
         >>> l = Ln.from_points(Point(1,2,3), Point(4,5,6), Point(7,8,9))
         >>> l.pts()
         [Point([1. 2. 3.]), Point([4. 5. 6.]), Point([7. 8. 9.])]
        """

        return [self.pt(ndx) for ndx in range(self.num_points())]

    def start_pt(self) -> Point:
        """
        Returns the initial point of the line.

        Examples:
         >>> l = Ln.from_points(Point(1,2,3), Point(4,5,6), Point(7,8,9))
         >>> l.start_pt()
         Point([1. 2. 3.])
        """

        return self.pt(0)

    def end_pt(self) -> Point:
        """
        Returns the initial point of the line.

        Examples:
         >>> l = Ln.from_points(Point(1,2,3), Point(4,5,6), Point(7,8,9))
         >>> l.end_pt()
         Point([7. 8. 9.])
        """

        return self.pt(-1)

    def as_segment(self) -> Union[type(None), Segment]:
        """Return the segment defined by line start and end points.

        Examples:
         >>> l = Ln.from_points(Point(1,2,3), Point(4,5,6), Point(7,8,9))
         >>> l.as_segment()
         Segment(start_pt=Point([1. 2. 3.]), end_pt=Point([7. 8. 9.]))
        """

        if self.start_pt() and self.end_pt():
            return Segment(self.start_pt(), self.end_pt())
        else:
            return None

    def segment(self,
        ndx: numbers.Integral
    ) -> Union[type(None), Segment]:
        """
        Returns the optional segment at index ndx.

        :param ndx: the segment index.
        :return: the segment or None.

        Examples:
         >>> l = Ln.from_points(Point(1,2,3), Point(4,5,6), Point(7,8,9))
         >>> l.segment(0)
         Segment(start_pt=Point([1. 2. 3.]), end_pt=Point([4. 5. 6.]))
         >>> l.segment(1)
         Segment(start_pt=Point([4. 5. 6.]), end_pt=Point([7. 8. 9.]))
         >>> l.segment(2)
         None
        """

        start_pt = self.pt(ndx)
        end_pt = self.pt(ndx + 1)

        if start_pt is None or end_pt is None:
            return None

        return Segment(
            start_pt=self.pt(ndx),
            end_pt=self.pt(ndx + 1)
        )

    def segments(self) -> Union[type(None), List[Segment]]:
        """
        Convert to a list of segments.

        :return: list of Segment objects.

        Examples:
         >>> Ln().segments() is None
         True
         >>> Ln([(1, 1)]).segments() is None
         True
         >>> Ln([(1, 1), (2, 2)]).segments()
         [Segment(start_pt=Point([1. 1.]), end_pt=Point([2. 2.]))]
         >>> l = Ln.from_points(Point(1,2,3), Point(4,5,6), Point(7,8,9))
         >>> l.segments()
         [Segment(start_pt=Point([1. 2. 3.]), end_pt=Point([4. 5. 6.])), Segment(start_pt=Point([4. 5. 6.]), end_pt=Point([7. 8. 9.]))]
        """

        if self.num_points() < 2:
            return None

        line_pts = self.pts()
        pts_pairs = zip(line_pts[:-1], line_pts[1:])
        segments = [Segment(pt_a, pt_b) for (pt_a, pt_b) in pts_pairs]

        return segments

    def to_list_ptsegm2d(self) -> List[UnionPtSegment2D]:
        """Converts the line to a list of points/segments."""

        n_pts = self.num_points()
        if n_pts == 0:
            return []
        elif n_pts == 1:
            return [self.start_pt()]
        else:
            return list(self.remove_coincident_points().segments())

    def xy_zipped(self) -> List[Tuple[numbers.Real, numbers.Real]]:

        return [(x, y) for x, y in zip(self.x_list(), self.y_list())]

    def __iter__(self):
        """
        Returns on iterator on the line segments.
        """

        return (segment for segment in self.segments())

    def __getitem__(self, ndx: numbers.Integral):
        """
        Returns segment at given index.
        """

        return list(self.segments())[ndx]

    def add_pt(self,
               pt: Point):
        """
        In-place transformation of the original Ln instance
        by adding a new point at the end.

        :param pt: the point to add.


        Examples:
         >>> l = Ln.from_points(Point(0,0,0), Point(1,1,1), Point(2,2,2))
         >>> l.add_pt(Point(3,3,3))
         >>> l
         Ln with 4 point(s): Point([0. 0. 0.]), Point([1. 1. 1.]), Point([2. 2. 2.]), Point([3. 3. 3.])
         >>> l = Ln()
         >>> l.add_pt(Point(0,0,0))
         >>> l
         Ln with 1 point(s): Point([0. 0. 0.])
        """

        if self.coords is None:
            self._coords = np.reshape(pt.coords, (1, pt.coords.shape[0]))
        else:
            self._coords = np.vstack([self._coords, pt.coords])

    def remove_coincident_points(self,
                                 tolerance: numbers.Real = MIN_SEPARATION_THRESHOLD
                                 ) -> Union[type(None), 'Ln']:
        """
        Remove coincident successive points.

        Examples:
         >>> l = Ln([[1121952.61908204, 4446743.74579965], [1122187.64747837, 4446882.23326361]])
         >>> l
         Ln with 2 point(s): Point([1121952.61908204 4446743.74579965]), Point([1122187.64747837 4446882.23326361])
         >>> l.remove_coincident_points()
         Ln with 2 point(s): Point([1121952.61908204 4446743.74579965]), Point([1122187.64747837 4446882.23326361])
        """

        try:

            line = Ln()

            if self.num_points() == 0:
                return line

            line.add_pt(self.pt(0))

            for ndx in range(1, self.num_points()):
                if not self.pt(ndx).is_coincident(
                        line.pt(-1),
                        tolerance=tolerance):
                    line.add_pt(self.pt(ndx))

            return line

        except Exception as e:

            print(Error(True, caller_name(), e))
            return None

    def remove_coincident_points_2d(self,
                                    tolerance: numbers.Real = MIN_SEPARATION_THRESHOLD
                                    ) -> Union[type(None), 'Ln']:
        """
        Remove 2D-coincident successive points.
        """

        try:

            line = Ln()

            if self.num_points() == 0:
                return line

            line.add_pt(self.pt(0))

            for ndx in range(1, self.num_points()):
                if not self.pt(ndx).is_coincident_2d(
                        line.pt(-1),
                        tolerance=tolerance):
                    line.add_pt(self.pt(ndx))

            return line

        except Exception as e:

            print(Error(True, caller_name(), e))
            return None

    def length(self):
        """ Calculate line length"""

        length = 0
        for ndx in range(1, self.num_points()):
            segment_length = self.pt(ndx).distance(self.pt(ndx - 1))
            length += segment_length

        return length

    def length_2d(self):
        """ Calculate 2D line length"""

        length = 0
        for ndx in range(1, self.num_points()):
            segment_length = self.pt(ndx).distance_2d(self.pt(ndx - 1))
            length += segment_length

        return length

    def length_3d(self):
        """ Calculate 3D line length"""

        length = 0
        for ndx in range(1, self.num_points()):
            segment_length = self.pt(ndx).distance_3d(self.pt(ndx - 1))
            length += segment_length

        return length

    def step_lengths_2d(self) -> List[numbers.Real]:
        """
        Returns the point-to-point 2D distances.
        It is the distance between a point and the previous one.
        The list has the same length as the source point list.

        :return: the individual 2D segment lengths.

        Examples:
        """

        segments_2d_lengths = [0.0]
        for ndx in range(1, self.num_points()):
            segment_2d_length = self.pt(ndx).distance_2d(self.pt(ndx - 1))
            segments_2d_lengths.append(segment_2d_length)

        return segments_2d_lengths

    def step_lengths_3d(self) -> List[numbers.Real]:
        """
        Returns the point-to-point 3d distances.
        It is the distance between a point and the previous one.
        The list has the same length as the source point list.

        :return: the individual 3d segment lengths.

        Examples:
        """

        segments_3d_lengths = [0.0]
        for ndx in range(1, self.num_points()):
            segment_3d_length = self.pt(ndx).distance_3d(self.pt(ndx - 1))
            segments_3d_lengths.append(segment_3d_length)

        return segments_3d_lengths

    def accumulated_length_2d(self) -> List[numbers.Real]:
        """
        Returns the accumulated 2D segment lengths.

        :return: accumulated 2D segment lengths.
        """

        return list(itertools.accumulate(self.step_lengths_2d()))

    def densify_as_line2d(self,
                          sample_distance: numbers.Real
                          ) -> Union[type(None), 'Ln']:
        """
        Densify a line into a new line instance,
        using the provided sample distance.
        Returned Ln instance has coincident successive points removed.

        :param sample_distance: numbers.Real
        :return: Ln instance
        """

        if sample_distance <= 0.0:
            print(f"Sample distance must be positive. {sample_distance} received")
            return None

        segments = self.segments()

        densified_lines = [segment.densify_as_line2d(sample_distance) for segment in segments]

        concatenated = concatenate(*densified_lines)

        densified_line_wo_coinc_pts = concatenated.remove_coincident_points()

        return densified_line_wo_coinc_pts

    def densify_as_equally_spaced_points2d(self,
       sample_distance: numbers.Real
       ) -> List[Point]:
        """
        Densify a line into a set of Point instances, each equally spaced along the line
        (so that at corners 2D distance between points is less than 'sample_distance').

        """

        points = []
        segment_start_offset = 0.0
        for segment in self.segments():
            segment_points = segment.densify_as_points2d(
                densify_distance=sample_distance,
                start_offset=segment_start_offset
            )
            points.extend(segment_points[:-1])
            segment_start_offset = sample_distance - segment_points[-2].distance(segment_points[-1])

        return points

    def slopes_degr(self) -> List[Union[type(None), numbers.Real]]:
        """
        Calculates the slopes (in degrees) of each Ln segment.
        The first value is the slope of the first segment.
        The last value, always None, is the slope of the segment starting at the last point.
        The number of elements is equal to the number of points in the Ln.

        :return: list of slopes (degrees).
        """

        slopes = []

        segments = self.segments()
        for segment in segments:
            vector = segment.as_vector3d()
            slopes.append(-vector.dip_angle())  # minus because vector convention is positive downward

        slopes.append(None)  # None refers to the slope of the Segment starting with the last point

        return slopes

    def shift_horiz(self,
                    dx: numbers.Real,
                    dy: numbers.Real
                    ) -> 'Ln':
        """
        Creates a new line shifted horizontally.

        Examples:
         >>> l = Ln.from_points(Point(1,2,3), Point(4,5,6), Point(7,8,9))
         >>> s = l.shift_horiz(10, 20)
         >>> s.coords[:, 0]
         array([11., 14., 17.])
         >>> s.coords[:, 1]
         array([22., 25., 28.])
         >>> s.coords[:, 2]
         array([3., 6., 9.])
        """

        crds = np.copy(self.coords)
        crds[:, 0 ] = crds[:, 0 ] + dx
        crds[:, 1] = crds[:, 1] + dy
        return Ln(crds)

    def absolute_slopes(self) -> np.ndarray:

        return np.asarray(list(map(abs, self.dir_slopes())))

    def dir_slopes(self) -> np.ndarray:

        slopes = []
        for ndx in range(self.num_points() - 1):
            segment_start_pt = self.pt(ndx)
            segment_end_pt = self.pt(ndx + 1)
            if np.isnan(segment_start_pt.z) or np.isnan(segment_end_pt.z):
                slopes.append(np.nan)
            else:
                vector = Segment(self.pt(ndx), self.pt(ndx + 1)).as_vector3d()
                slopes.append(-vector.dip_angle())  # minus because vector convention is positive downward
        slopes.append(np.nan)  # slope value for last point is unknown

        return np.asarray(slopes)

    def x_array(self) -> np.ndarray:

        return np.copy(self._coords[:, 0])

    def x_list(self) -> List[numbers.Real]:

        return list(self.x_array())

    def x_min(self) -> numbers.Real:
        return np.nanmin(self.x_array())

    def x_max(self) -> numbers.Real:
        return np.nanmax(self.x_array())

    def x_minmax(self) -> Tuple[numbers.Real, numbers.Real]:

        return self.x_min(), self.x_max()

    def x_mean(self) -> numbers.Real:
        return np.nanmean(self.x_array())

    def x_var(self) -> numbers.Real:

        return np.nanvar(self.x_array())

    def x_std(self) -> numbers.Real:

        return np.nanstd(self.x_array())

    def y_array(self):

        return np.copy(self._coords[:, 1])

    def y_list(self) -> List[numbers.Real]:

        return list(self.y_array())

    def y_min(self):
        return np.nanmin(self.y_array())

    def y_max(self):
        return np.nanmax(self.y_array())

    def y_minmax(self):

        return self.y_min(), self.y_max()

    def y_mean(self):

        return np.nanmean(self.y_array())

    def y_var(self):

        return np.nanvar(self.y_array())

    def y_std(self):

        return np.nanstd(self.y_array())

    def z_array(self):

        return np.copy(self._coords[:, 2])

    def z_list(self) -> List[numbers.Real]:

        return list(self.z_array())

    def z_min(self):
        return np.nanmin(self.z_array())

    def z_max(self):
        return np.nanmax(self.z_array())

    def z_mean(self):

        return np.nanmean(self.z_array())

    def z_var(self):

        return np.nanvar(self.z_array())

    def z_std(self):

        return np.nanstd(self.z_array())


def intersect_segments3d(
    segment1: Segment,
    segment2: Segment,
    tol: numbers.Real = PRACTICAL_MIN_DIST
) -> Optional[Union[Point, Segment]]:
    """
    Determines the optional point or segment intersection between the segment pair.

    :param segment1: the first segment
    :param segment2: the second segment
    :param tol: the distance tolerance for collapsing a intersection segment into a point
    :return: the optional point or segment intersection between the segment pair.

    Examples:
      >>> s2 = Segment(Point(0,0,0), Point(1,0,0))
      >>> s1 = Segment(Point(0,0,0), Point(1,0,0))
      >>> intersect_segments3d(s1, s2)
      Segment(start_pt=Point([0. 0. 0.]), end_pt=Point([1. 0. 0.]))
      >>> s1 = Segment(Point(-2,0,0), Point(-1,0,0))
      >>> intersect_segments3d(s1, s2)
      None
      >>> s1 = Segment(Point(-2,0,0), Point(0,0,0))
      >>> intersect_segments3d(s1, s2)
      Point([0. 0. 0.])
      >>> s1 = Segment(Point(-2,0,0), Point(0.5,0,0))
      >>> intersect_segments3d(s1, s2)
      Segment(start_pt=Point([0. 0. 0.]), end_pt=Point([0.5 0.  0. ]))
      >>> s1 = Segment(Point(-2,0,0), Point(1,0,0))
      >>> intersect_segments3d(s1, s2)
      Segment(start_pt=Point([0. 0. 0.]), end_pt=Point([1. 0. 0.]))
      >>> s1 = Segment(Point(-2,0,0), Point(2,0,0))
      >>> intersect_segments3d(s1, s2)
      Segment(start_pt=Point([0. 0. 0.]), end_pt=Point([1. 0. 0.]))
      >>> s1 = Segment(Point(0,0,0), Point(0.5,0,0))
      >>> intersect_segments3d(s1, s2)
      Segment(start_pt=Point([0. 0. 0.]), end_pt=Point([0.5 0.  0. ]))
      >>> s1 = Segment(Point(0.25,0,0), Point(0.75,0,0))
      >>> intersect_segments3d(s1, s2)
      Segment(start_pt=Point([0.25 0.   0.  ]), end_pt=Point([0.75 0.   0.  ]))
      >>> s1 = Segment(Point(0.25,0,0), Point(1,0,0))
      >>> intersect_segments3d(s1, s2)
      Segment(start_pt=Point([0.25 0.   0.  ]), end_pt=Point([1. 0. 0.]))
      >>> s1 = Segment(Point(0.25,0,0), Point(1.25,0,0))
      >>> intersect_segments3d(s1, s2)
      Segment(start_pt=Point([0.25 0.   0.  ]), end_pt=Point([1. 0. 0.]))
      >>> s1 = Segment(Point(0,0,0), Point(1.25,0,0))
      >>> intersect_segments3d(s1, s2)
      Segment(start_pt=Point([0. 0. 0.]), end_pt=Point([1. 0. 0.]))
      >>> s1 = Segment(Point(1,0,0), Point(1.25,0,0))
      >>> intersect_segments3d(s1, s2)
      Point([1. 0. 0.])
      >>> s2 = Segment(Point(0,0,0), Point(1,1,1))
      >>> s1 = Segment(Point(0.25,0.25,0.25), Point(0.75,0.75,0.75))
      >>> intersect_segments3d(s1, s2)
      Segment(start_pt=Point([0.25 0.25 0.25]), end_pt=Point([0.75 0.75 0.75]))
      >>> s1 = Segment(Point(0.25,0.25,0.25), Point(1.75,1.75,1.75))
      >>> intersect_segments3d(s1, s2)
      Segment(start_pt=Point([0.25 0.25 0.25]), end_pt=Point([1. 1. 1.]))
      >>> s1 = Segment(Point(0.25,0.25,0.25), Point(1.75,0,1.75))
      >>> intersect_segments3d(s1, s2)
      Point([0.25 0.25 0.25])
      >>> s1 = Segment(Point(0.25,1,0.25), Point(0.75,0.75,0.75))
      >>> intersect_segments3d(s1, s2)
      Point([0.75 0.75 0.75])
      >>> s2 = Segment(Point(-1,-1,-1), Point(1,1,1))
      >>> s1 = Segment(Point(-1,1,1), Point(1,-1,-1))
      >>> intersect_segments3d(s1, s2)
      Point([0. 0. 0.])
    """

    s1_startpt_inside = segment1.segment_start_in(segment2)
    s2_startpt_inside = segment2.segment_start_in(segment1)

    s1_endpt_inside = segment1.segment_end_in(segment2)
    s2_endpt_inside = segment2.segment_end_in(segment1)

    elements = [s1_startpt_inside, s2_startpt_inside, s1_endpt_inside, s2_endpt_inside]

    if all(elements):
        return segment1.clone()

    if s1_startpt_inside and s1_endpt_inside:
        return segment1.clone()

    if s2_startpt_inside and s2_endpt_inside:
        return segment2.clone()

    if s1_startpt_inside and s2_startpt_inside:
        return point_or_segment3d(
            segment1.start_pt,
            segment2.start_pt,
            tol=tol
        )

    if s1_startpt_inside and s2_endpt_inside:
        return point_or_segment3d(
            segment1.start_pt,
            segment2.end_pt,
            tol=tol
        )

    if s1_endpt_inside and s2_startpt_inside:
        return point_or_segment3d(
            segment2.start_pt,
            segment1.end_pt,
            tol=tol
        )

    if s1_endpt_inside and s2_endpt_inside:
        return point_or_segment3d(
            segment1.end_pt,
            segment2.end_pt,
            tol=tol
        )

    if s1_startpt_inside:
        return segment1.start_pt.clone()

    if s1_endpt_inside:
        return segment1.end_pt.clone()

    if s2_startpt_inside:
        return segment2.start_pt.clone()

    if s2_endpt_inside:
        return segment2.end_pt.clone()

    shortest_segm_or_pt = shortest_segment_or_point3d(
        segment1,
        segment2,
        tol=tol
    )

    if not shortest_segm_or_pt:
        return None

    if not isinstance(shortest_segm_or_pt, Point):
        return None

    inters_pt = shortest_segm_or_pt

    if not segment1.contains_pt(inters_pt):
        return None

    if not segment2.contains_pt(inters_pt):
        return None

    return inters_pt


def point_or_segment3d(
        point1: Point,
        point2: Point,
        tol: numbers.Real = PRACTICAL_MIN_DIST
) -> Union[Point, Segment]:
    """
    Creates a point or segment based on the points distance.

    :param point1: first input point.
    :type point1: Point.
    :param point2: second input point.
    :type point2: Point.
    :param tol: distance tolerance between the two points.
    :type tol: numbers.Real.
    :return: point or segment based on their distance.
    :rtype: PointOrSegment.
    :raise: Exception.
    """

    check_type(point1, "First point", Point)
    check_type(point2, "Second point", Point)

    if point1.distance(point2) <= tol:
        return Point(
            (point1.x + point2.x) / 2,
            (point1.y + point2.y) / 2,
            (point1.z + point2.z) / 2
        )
    else:
        return Segment(
            start_pt=point1,
            end_pt=point2
        )


def shortest_segment_or_point3d(
    first_segment: Segment,
    second_segment: Segment,
    tol: numbers.Real = PRACTICAL_MIN_DIST
) -> Optional[Union[Segment, Point]]:

    """
    Calculates the optional shortest segment - or the intersection point - between two lines represented by two segments.

    Adapted from:
        http://paulbourke.net/geometry/pointlineplane/

    C code from:
        http://paulbourke.net/geometry/pointlineplane/lineline.c
[
    typedef struct {
    double x,y,z;
    } XYZ;

    /*
    Calculate the line segment PaPb that is the shortest route between
    two lines P1P2 and P3P4. Calculate also the values of mua and mub where
      Pa = P1 + mua (P2 - P1)
      Pb = P3 + mub (P4 - P3)
    Return FALSE if no solution exists.
    */
    int LineLineIntersect(
    XYZ p1,XYZ p2,XYZ p3,XYZ p4,XYZ *pa,XYZ *pb,
    double *mua, double *mub)
    {
    XYZ p13,p43,p21;
    double d1343,d4321,d1321,d4343,d2121;
    double numer,denom;

    p13.x = p1.x - p3.x;
    p13.y = p1.y - p3.y;
    p13.z = p1.z - p3.z;
    p43.x = p4.x - p3.x;
    p43.y = p4.y - p3.y;
    p43.z = p4.z - p3.z;
    if (ABS(p43.x) < EPS && ABS(p43.y) < EPS && ABS(p43.z) < EPS)
      return(FALSE);
    p21.x = p2.x - p1.x;
    p21.y = p2.y - p1.y;
    p21.z = p2.z - p1.z;
    if (ABS(p21.x) < EPS && ABS(p21.y) < EPS && ABS(p21.z) < EPS)
      return(FALSE);

    d1343 = p13.x * p43.x + p13.y * p43.y + p13.z * p43.z;
    d4321 = p43.x * p21.x + p43.y * p21.y + p43.z * p21.z;
    d1321 = p13.x * p21.x + p13.y * p21.y + p13.z * p21.z;
    d4343 = p43.x * p43.x + p43.y * p43.y + p43.z * p43.z;
    d2121 = p21.x * p21.x + p21.y * p21.y + p21.z * p21.z;

    denom = d2121 * d4343 - d4321 * d4321;
    if (ABS(denom) < EPS)
      return(FALSE);
    numer = d1343 * d4321 - d1321 * d4343;

    *mua = numer / denom;
    *mub = (d1343 + d4321 * (*mua)) / d4343;

    pa->x = p1.x + *mua * p21.x;
    pa->y = p1.y + *mua * p21.y;
    pa->z = p1.z + *mua * p21.z;
    pb->x = p3.x + *mub * p43.x;
    pb->y = p3.y + *mub * p43.y;
    pb->z = p3.z + *mub * p43.z;

    return(TRUE);
    }

    :param first_segment: the first segment
    :param second_segment: the second segment
    :param tol: tolerance value for collapsing a segment into the midpoint.
    :return: the optional shortest segment or an intersection point.
    """

    check_type(second_segment, "Second Cartesian line", Segment)

    p1 = first_segment.start_pt
    p2 = first_segment.end_pt

    p3 = second_segment.start_pt
    p4 = second_segment.end_pt

    p13 = Point(
        p1.x - p3.x,
        p1.y - p3.y,
        p1.z - p3.z
    )

    p43 = Point(
        p4.x - p3.x,
        p4.y - p3.y,
        p4.z - p3.z
    )

    if p43.as_vector().is_close_to_zero():
        return None

    p21 = Point(
        p2.x - p1.x,
        p2.y - p1.y,
        p2.z - p1.z,
    )

    if p21.as_vector().is_close_to_zero():
        return None

    d1343 = p13.x * p43.x + p13.y * p43.y + p13.z * p43.z
    d4321 = p43.x * p21.x + p43.y * p21.y + p43.z * p21.z
    d1321 = p13.x * p21.x + p13.y * p21.y + p13.z * p21.z
    d4343 = p43.x * p43.x + p43.y * p43.y + p43.z * p43.z
    d2121 = p21.x * p21.x + p21.y * p21.y + p21.z * p21.z

    denom = d2121 * d4343 - d4321 * d4321

    if fabs(denom) < MIN_SCALAR_VALUE:
        return None

    numer = d1343 * d4321 - d1321 * d4343

    mua = numer / denom
    mub = (d1343 + d4321 * mua) / d4343

    pa = Point(
        p1.x + mua * p21.x,
        p1.y + mua * p21.y,
        p1.z + mua * p21.z
    )

    pb = Point(
        p3.x + mub * p43.x,
        p3.y + mub * p43.y,
        p3.z + mub * p43.z
    )

    intersection = point_or_segment3d(
        point1=pa,
        point2=pb,
        tol=tol
    )

    return intersection


class JoinTypes(Enum):
    """
    Enumeration for Ln and Segment type.
    """

    START_START = 1  # start point coincident with start point
    START_END   = 2  # start point coincident with end point
    END_START   = 3  # end point coincident with start point
    END_END     = 4  # end point coincident with end point


def analyze_joins(
        first: Union[Ln, Segment],
        second: Union[Ln, Segment]
) -> Optional[List[Optional[JoinTypes]]]:
    """
    Analyze join types between two lines/segments.

    :param first: a line or segment.
    :param second: a line or segment.
    :return: an optional list of join types.

    Examples:
      >>> first = Segment(Point(0,0), Point(1,0))
      >>> second = Segment(Point(1,0), Point(0,0))
      >>> analyze_joins(first, second)
      [<JoinTypes.START_END: 2>, <JoinTypes.END_START: 3>]
      >>> first = Segment(Point(0,0), Point(1,0))
      >>> second = Segment(Point(2,0), Point(3,0))
      >>> analyze_joins(first, second)
      []
    """

    join_types = []

    if first.start_pt.is_coincident(second.start_pt):
        join_types.append(JoinTypes.START_START)

    if first.start_pt.is_coincident(second.end_pt):
        join_types.append(JoinTypes.START_END)

    if first.end_pt.is_coincident(second.start_pt):
        join_types.append(JoinTypes.END_START)

    if first.end_pt.is_coincident(second.end_pt):
        join_types.append(JoinTypes.END_END)

    return join_types


@singledispatch
def concatenate(
    geom: Shape,
    *args
) -> Union[type(None), Shape]:

    return None


@concatenate.register(Ln)
def _(
    geom: Ln,
    *args
) -> Union[type(None), Ln]:
    """
    Concatenates a sequence of lines.

    Examples:
     >>> l1 = Ln.from_points(Point(1,2,3), Point(4,5,6))
     >>> l2 = Ln.from_points(Point(7,8,9), Point(10, 11, 12), Point(13, 14, 15))
     >>> l3 = Ln.from_points(Point(16, 17, 18), Point(19, 20, 21))
     >>> concatenate(l1, l2, l3)
     Ln with 7 points: Point([1. 2. 3.]), Point([4. 5. 6.]), .., Point([16. 17. 18.]), Point([19. 20. 21.])

    """

    return Ln(np.vstack([ln.coords for ln in [geom]+list(args)]))


def point_or_segment2d(
        point1: Point,
        point2: Point,
        tol: numbers.Real = PRACTICAL_MIN_DIST
) -> Union[Point, Segment]:
    """
    Creates a 2D point or segment based on the points distance.

    :param point1: first input point.
    :param point2: second input point.
    :param tol: distance tolerance between the two points.
    :return: point or segment based on their distance.
    :raise: Exception.
    """

    check_type(point1, "First point", Point)
    check_type(point2, "Second point", Point)

    point1 = point1.as_point2d()
    point2 = point2.as_point2d()

    if point1.distance(point2) <= tol:
        return Point(
            (point1.x + point2.x) / 2,
            (point1.y + point2.y) / 2
        )
    else:
        return Segment(
            start_pt=point1,
            end_pt=point2
        )


def shortest_segment_or_point2d(
    first_segment: Segment,
    second_segment: Segment,
    tol: numbers.Real = PRACTICAL_MIN_DIST
) -> Optional[Union[Segment, Point]]:
    """
    TODO: check correct implementation for 2D case, since it derives from 3D implementation.

    Calculates the optional shortest segment - or intersection point - between two segments.

    Adapted from:
        http://paulbourke.net/geometry/pointlineplane/

    C code from:
        http://paulbourke.net/geometry/pointlineplane/lineline.c
[
    typedef struct {
    double x,y,z;
    } XYZ;

    /*
    Calculate the line segment PaPb that is the shortest route between
    two lines P1P2 and P3P4. Calculate also the values of mua and mub where
      Pa = P1 + mua (P2 - P1)
      Pb = P3 + mub (P4 - P3)
    Return FALSE if no solution exists.
    */
    int LineLineIntersect(
    XYZ p1,XYZ p2,XYZ p3,XYZ p4,XYZ *pa,XYZ *pb,
    double *mua, double *mub)
    {
    XYZ p13,p43,p21;
    double d1343,d4321,d1321,d4343,d2121;
    double numer,denom;

    p13.x = p1.x - p3.x;
    p13.y = p1.y - p3.y;
    p13.z = p1.z - p3.z;
    p43.x = p4.x - p3.x;
    p43.y = p4.y - p3.y;
    p43.z = p4.z - p3.z;
    if (ABS(p43.x) < EPS && ABS(p43.y) < EPS && ABS(p43.z) < EPS)
      return(FALSE);
    p21.x = p2.x - p1.x;
    p21.y = p2.y - p1.y;
    p21.z = p2.z - p1.z;
    if (ABS(p21.x) < EPS && ABS(p21.y) < EPS && ABS(p21.z) < EPS)
      return(FALSE);

    d1343 = p13.x * p43.x + p13.y * p43.y + p13.z * p43.z;
    d4321 = p43.x * p21.x + p43.y * p21.y + p43.z * p21.z;
    d1321 = p13.x * p21.x + p13.y * p21.y + p13.z * p21.z;
    d4343 = p43.x * p43.x + p43.y * p43.y + p43.z * p43.z;
    d2121 = p21.x * p21.x + p21.y * p21.y + p21.z * p21.z;

    denom = d2121 * d4343 - d4321 * d4321;
    if (ABS(denom) < EPS)
      return(FALSE);
    numer = d1343 * d4321 - d1321 * d4343;

    *mua = numer / denom;
    *mub = (d1343 + d4321 * (*mua)) / d4343;

    pa->x = p1.x + *mua * p21.x;
    pa->y = p1.y + *mua * p21.y;
    pa->z = p1.z + *mua * p21.z;
    pb->x = p3.x + *mub * p43.x;
    pb->y = p3.y + *mub * p43.y;
    pb->z = p3.z + *mub * p43.z;

    return(TRUE);
    }

    :param first_segment: the first segment
    :param second_segment: the second segment
    :param tol: tolerance value for collapsing a segment into the midpoint.
    :return: the optional shortest segment or an intersection point.
    """

    check_type(second_segment, "Second Cartesian line", Segment)

    p1 = first_segment.start_pt
    p2 = first_segment.end_pt

    p3 = second_segment.start_pt
    p4 = second_segment.end_pt

    p13 = Point(
        p1.x - p3.x,
        p1.y - p3.y
    )

    p43 = Point(
        p4.x - p3.x,
        p4.y - p3.y
    )

    if p43.is_coincident(Point(0, 0)):
        return None

    p21 = Point(
        p2.x - p1.x,
        p2.y - p1.y
    )

    if p21.is_coincident(Point(0, 0)):
        return None

    d1343 = p13.x * p43.x + p13.y * p43.y
    d4321 = p43.x * p21.x + p43.y * p21.y
    d1321 = p13.x * p21.x + p13.y * p21.y
    d4343 = p43.x * p43.x + p43.y * p43.y
    d2121 = p21.x * p21.x + p21.y * p21.y

    denom = d2121 * d4343 - d4321 * d4321

    if fabs(denom) < MIN_SCALAR_VALUE:
        return None

    numer = d1343 * d4321 - d1321 * d4343

    mua = numer / denom
    mub = (d1343 + d4321 * mua) / d4343

    pa = Point(
        p1.x + mua * p21.x,
        p1.y + mua * p21.y
    )

    pb = Point(
        p3.x + mub * p43.x,
        p3.y + mub * p43.y
    )

    intersection = point_or_segment2d(
        point1=pa,
        point2=pb,
        tol=tol
    )

    return intersection

'''20220809: deactivated since class method should be used. When sure, remove
def intersect_segments2d(
    segment1: Segment,
    segment2: Segment,
    tol: numbers.Real = PRACTICAL_MIN_DIST
) -> Union[type(None), Point, Segment]:
    """
    Determines the optional point or segment intersection between the segment pair.

    :param segment1: the first segment
    :param segment2: the second segment
    :param tol: the distance tolerance for collapsing a intersection segment into a point
    :return: the optional point or segment intersection between the segment pair.

    Examples:
      >>> s2 = Segment(Point(0,0), Point(1,0))
      >>> s1 = Segment(Point(0,0), Point(1,0))
      >>> intersect_segments2d(s1, s2)
      Segment(start_pt=Point([0. 0.]), end_pt=Point([1. 0.]))
      >>> s1 = Segment(Point(-2,0), Point(-1,0))
      >>> intersect_segments2d(s1, s2) is None
      True
      >>> s1 = Segment(Point(-2,0), Point(0,0))
      >>> intersect_segments2d(s1, s2)
      Point([0. 0.])
      >>> s1 = Segment(Point(-2,0), Point(0.5,0.0))
      >>> intersect_segments2d(s1, s2)
      Segment(start_pt=Point([0. 0.]), end_pt=Point([0.5 0. ]))
      >>> s1 = Segment(Point(-2,0), Point(1,0))
      >>> intersect_segments2d(s1, s2)
      Segment(start_pt=Point([0. 0.]), end_pt=Point([1. 0.]))
      >>> s1 = Segment(Point(-2,0), Point(2,0))
      >>> intersect_segments2d(s1, s2)
      Segment(start_pt=Point([0. 0.]), end_pt=Point([1. 0.]))
      >>> s1 = Segment(Point(0,0), Point(0.5,0))
      >>> intersect_segments2d(s1, s2)
      Segment(start_pt=Point([0. 0.]), end_pt=Point([0.5 0. ]))
      >>> s1 = Segment(Point(0.25,0), Point(0.75,0))
      >>> intersect_segments2d(s1, s2)
      Segment(start_pt=Point([0.25 0.  ]), end_pt=Point([0.75 0.  ]))
      >>> s1 = Segment(Point(0.25,0), Point(1,0))
      >>> intersect_segments2d(s1, s2)
      Segment(start_pt=Point([0.25 0.  ]), end_pt=Point([1. 0.]))
      >>> s1 = Segment(Point(0.25,0), Point(1.25,0))
      >>> intersect_segments2d(s1, s2)
      Segment(start_pt=Point([0.25 0.  ]), end_pt=Point([1. 0.]))
      >>> s1 = Segment(Point(0,0), Point(1.25,0))
      >>> intersect_segments2d(s1, s2)
      Segment(start_pt=Point([0. 0.]), end_pt=Point([1. 0.]))
      >>> s1 = Segment(Point(1,0), Point(1.25,0))
      >>> intersect_segments2d(s1, s2)
      Point([1. 0.])
      >>> s2 = Segment(Point(0,0), Point(1,1))
      >>> s1 = Segment(Point(0.25,0.25), Point(0.75,0.75))
      >>> intersect_segments2d(s1, s2)
      Segment(start_pt=Point([0.25 0.25]), end_pt=Point([0.75 0.75]))
      >>> s1 = Segment(Point(0.25,0.25), Point(1.75,1.75))
      >>> intersect_segments2d(s1, s2)
      Segment(start_pt=Point([0.25 0.25]), end_pt=Point([1. 1.]))
      >>> s1 = Segment(Point(0.25,0.25), Point(1.75,0))
      >>> intersect_segments2d(s1, s2)
      Point([0.25 0.25])
      >>> s1 = Segment(Point(0.25,1), Point(0.75,0.75))
      >>> intersect_segments2d(s1, s2)
      Point([0.75 0.75])
      >>> s2 = Segment(Point(-1,-1), Point(1,1))
      >>> s1 = Segment(Point(-1,1), Point(1,-1))
      >>> intersect_segments2d(s1, s2)
      Point([0. 0.])
    """

    check_type(segment1, "First segment", Segment)
    check_type(segment2, "Second segment", Segment)

    segment1 = segment1.as_2d()
    segment2 = segment2.as_2d()

    s1_startpt_inside = segment1.segment_start_in(segment2)
    s2_startpt_inside = segment2.segment_start_in(segment1)

    s1_endpt_inside = segment1.segment_end_in(segment2)
    s2_endpt_inside = segment2.segment_end_in(segment1)

    elements = [s1_startpt_inside, s2_startpt_inside, s1_endpt_inside, s2_endpt_inside]

    if all(elements):
        return segment1.clone()

    if s1_startpt_inside and s1_endpt_inside:
        return segment1.clone()

    if s2_startpt_inside and s2_endpt_inside:
        return segment2.clone()

    if s1_startpt_inside and s2_startpt_inside:
        return point_or_segment2d(
            segment1.start_pt,
            segment2.start_pt,
            tol=tol
        )

    if s1_startpt_inside and s2_endpt_inside:
        return point_or_segment2d(
            segment1.start_pt,
            segment2.end_pt,
            tol=tol
        )

    if s1_endpt_inside and s2_startpt_inside:
        return point_or_segment2d(
            segment2.start_pt,
            segment1.end_pt,
            tol=tol
        )

    if s1_endpt_inside and s2_endpt_inside:
        return point_or_segment2d(
            segment1.end_pt,
            segment2.end_pt,
            tol=tol
        )

    if s1_startpt_inside:
        return segment1.start_pt.clone()

    if s1_endpt_inside:
        return segment1.end_pt.clone()

    if s2_startpt_inside:
        return segment2.start_pt.clone()

    if s2_endpt_inside:
        return segment2.end_pt.clone()

    shortest_segm_or_pt = shortest_segment_or_point2d(
        segment1,
        segment2,
        tol=tol
    )

    if not shortest_segm_or_pt:
        return None

    if not isinstance(shortest_segm_or_pt, Point):
        return None

    inters_pt = shortest_segm_or_pt

    if not segment1.contains_pt(inters_pt):
        return None

    if not segment2.contains_pt(inters_pt):
        return None

    return inters_pt
'''

def lines_to_points_segments(
        lines: List[Ln]
) -> List[UnionPtSegment2D]:

    ptsegms2d = []

    for line in lines:
        ptsegms2d.extend(line.to_list_ptsegm2d())

    return ptsegms2d


class MultiLine(Shape):

    proper_space = 1

    def __init__(self, lines_list):

        super(MultiLine, self).__init__()

        self._lines = lines_list

    def lines(self) -> List[Ln]:

        return self._lines

    def line(self, ndx: numbers.Integral):

        return self._lines[ndx]

    def num_lines(self):

        return len(self.lines())

    def add(self, line: Ln):
        """Adds a line to the multiline."""

        self._lines.append(line)

    def clone(self):
        """Clones the multiline."""

        return MultiLine(self.lines())

    def num_points(self):

        num_points = 0
        for line in self.lines():
            num_points += line.num_points()

        return num_points

    def __repr__(self) -> str:
        """
        Represents a MultiLine instance as a shortened text.

        :return: a textual shortened representation of a MultiLine instance.
        """

        num_lines = self.num_lines()

        if num_lines == 0:
            return f"Empty MultiLine"

        num_points = self.num_points()

        return f"MultiLine made up by {num_lines} line(s) and {num_points} total point(s)"

    def is_continuous(self):

        for line_ndx in range(len(self._lines) - 1):
            if not self.lines()[line_ndx].pts()[-1].is_coincident(self.lines()[line_ndx + 1].pts()[0]) or \
               not self.lines()[line_ndx].pts()[-1].is_coincident(self.lines()[line_ndx + 1].pts()[-1]):
                return False

        return True

    def is_unidirectional(self):

        for line_ndx in range(len(self.lines()) - 1):
            if not self.lines()[line_ndx].pts()[-1].is_coincident(self.lines()[line_ndx + 1].pts()[0]):
                return False

        return True

    @property
    def x_min(self) -> Optional[float]:

        if self.num_points() == 0:
            return None
        else:
            return np.nanmin([line.x_min for line in self.lines()])[0]

    @property
    def x_max(self):

        if self.num_points() == 0:
            return None
        else:
            return np.nanmax([line.x_max for line in self.lines()])

    @property
    def y_min(self):

        if self.num_points() == 0:
            return None
        else:
            return np.nanmin([line.y_min for line in self.lines()])

    @property
    def y_max(self):

        if self.num_points() == 0:
            return None
        else:
            return np.nanmax([line.y_max for line in self.lines()])

    @property
    def z_min(self):

        if self.num_points() == 0:
            return None
        else:
            return np.nanmin([line.z_min for line in self.lines()])

    @property
    def z_max(self):

        if self.num_points() == 0:
            return None
        else:
            return np.nanmax([line.z_max for line in self.lines()])

    def __iter__(self):

        return (line for line in self.lines)

    def length(self) -> numbers.Real:
        """Returns length of the multiline."""

        return sum(line.length() for line in self)

    def area(self):
        """Calculate shape area"""

        return 0.0

    def to_line(self):

        return Ln.from_points(*[point for line in self.lines() for point in line.pts()])


def xytuple_list_to_line2d(
        xy_list: List[Tuple[numbers.Real, numbers.Real]]
) -> Ln:

    return Ln(xy_list)


def xytuple_l2_to_multiline2d(
        xytuple_list2
) -> MultiLine:

    # input is a list of list of (x,y) values

    lines_list = []
    for xy_list in xytuple_list2:
        lines_list.append(xytuple_list_to_line2d(xy_list))

    return MultiLine(lines_list)


def merge_line2d(
        line
) -> Ln:
    """
    line: a list of (x,y) tuples for line
    """

    line_type, line_geometry = line

    if line_type == 'multiline':
        path_line = xytuple_l2_to_multiline2d(line_geometry).to_line()
    elif line_type == 'line':
        path_line = xytuple_list_to_line2d(line_geometry)
    else:
        raise Exception("unknown line type")

    # transformed into a single Ln

    result = path_line.remove_coincident_points()

    return result


def merge_lines2d(
        lines: List[Ln],
        progress_ids
):
    """
    lines: a list of list of (x,y,z) tuples for multilines
    """

    sorted_line_list = [line for (_, line) in sorted(zip(progress_ids, lines))]

    line_list = []
    for line in sorted_line_list:

        line_type, line_geometry = line

        if line_type == 'multiline':
            path_line = xytuple_l2_to_multiline2d(line_geometry).to_line()
        elif line_type == 'line':
            path_line = xytuple_list_to_line2d(line_geometry)
        else:
            continue
        line_list.append(path_line)  # now a list of Lines

    # now the list of Lines is transformed into a single Ln with coincident points removed

    line = MultiLine(line_list).to_line().remove_coincident_points()

    return line


@singledispatch
def intersect(
    shape1: Shape,
    shape2: Shape
) -> Optional[Union[List[UnionPtSegment2D], type(NotImplemented)]]:

    return NotImplemented


@intersect.register(Segment)
def _(
    shape1: Segment,
    shape2: Shape
) -> Union[List[UnionPtSegment2D], type(NotImplemented)]:
    """
    Calculates the possible intersections between the provided segment and another shape.

    :param shape1: the first shape, a 2D segment
    :param shape2: the second generic Shape instance
    :return: the optional intersections, as a PointsSegments2D instance, or NotImplemented
    """

    if isinstance(shape2, Ln):

        intersections = [curr_segment.intersect_segments2d(shape1) for curr_segment in shape2.segments() if curr_segment is not None]

    elif isinstance(shape2, MultiLine):

        intersections = [curr_segment.intersect_segments2d(shape1) for line in shape2.lines() for curr_segment in
                         line.segments() if curr_segment is not None]

    else:
        print(f"Error: second shape is a {type(shape2)} instance")
        return NotImplemented

    return list(filter(lambda val: val is not None, intersections))


class ParamLine3D(object):
    """
    A parametric line is defined by a source point
    and three scalar line coefficients (l, m, n).
    """

    def __init__(self,
                 srcPt: Point,
                 l: numbers.Real,
                 m: numbers.Real,
                 n: numbers.Real
            ):

        check_type(srcPt, "Source point", Point)

        self.srcPt = srcPt.clone()
        norm = math.sqrt(l*l + m*m + n*n)
        self.l = l / norm
        self.m = m / norm
        self.n = n / norm

    def __repr__(self):

        return f"ParamLine3D({self.srcPt}, {self.l:.4f}, {self.m:.4f}, {self.n:.4f})"

    def is_point_on_line(self,
        pt: Point
    ) -> Tuple[Union[type(None), bool], Error]:
        """
        Determines if a point lies on the line.

        :param pt: the point to check for.
        :result: whether the point lies on the line and an error message.
        """

        try:

            if are_close(pt.distance(self.srcPt), 0):
                return True, Error()

            versor_pt, err = Segment(self.srcPt, pt).as_vector3d().to_versor()
            if err:
                return None, err

            versor_ln = Vect3D(self.l, self.m, self.n)

            cross_vect, err = versor_pt.cross_vector(versor_ln)

            if err:
                return None, err

            if cross_vect.is_close_to_zero():
                return True, Error()

            return False, Error()

        except Exception as e:

            return None, Error(True, caller_name(), e, traceback.format_exc())

    def as_versor(self) -> Vect3D:
        """
        Converts a parametric line to a versor.

        Examples:
        >>> par_ln = ParamLine3D(Point(4,2,8), 6, 9, 3)
        >>> par_ln.as_versor()
        Vect3D(0.5345, 0.8018, 0.2673)
        """

        return Vect3D(self.l, self.m, self.n)


MLine = Union[Ln, MultiLine]



if __name__ == "__main__":

    import doctest
    doctest.testmod()


