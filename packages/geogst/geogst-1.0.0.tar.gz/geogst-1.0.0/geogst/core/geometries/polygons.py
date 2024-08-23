
from typing import Dict

from geogst.core.geometries.lines import *
from geogst.core.geometries.points import *
from geogst.core.geometries.shape import *


def isLeft(
        p0: np.ndarray,
        p1: np.ndarray,
        p2: np.ndarray
) -> numbers.Real:
    """

    Source:

    https://web.archive.org/web/20130109225203/http://geomalgorithms.com/index.html

    // Copyright 2000 softSurfer, 2012 Dan Sunday
    // This code may be freely used and modified for any purpose
    // providing that this copyright notice is included with it.
    // SoftSurfer makes no warranty for this code, and cannot be held
    // liable for any real or imagined damage resulting from its use.
    // Users of this code must verify correctness for their application.

    // isLeft(): tests if a point is Left|On|Right of an infinite line.
    //    Input:  three points P0, P1, and P2
    //    Return: >0 for P2 left of the line through P0 and P1
    //            =0 for P2  on the line
    //            <0 for P2  right of the line
    inline int
    isLeft( Point P0, Point P1, Point P2 )
    {
        return ( (P1.x - P0.x) * (P2.y - P0.y)
                - (P2.x -  P0.x) * (P1.y - P0.y) );
    }
    """

    return (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p2[0] - p0[0]) * (p1[1] - p0[1])


def calculate_wn(
        pt_coords: np.ndarray,
        poly_coords: np.ndarray
) -> numbers.Integral:
    """
    Calculate the winding number of a simple polygon.

    From:
    .....
    """

    wn = 0

    for ndx in range(len(poly_coords) - 1):

        v = poly_coords[ndx]
        vp1 = poly_coords[ndx + 1]

        if v[1] <= pt_coords[1]:

            if vp1[1] > pt_coords[1]:
                if isLeft(v, vp1, pt_coords) > 0.0:
                    wn += 1

        else:

            if vp1[1] <= pt_coords[1]:
                if isLeft(v, vp1, pt_coords) < 0.0:
                    wn -= 1

    return wn


class Polygon(Shape):

    proper_space = 2

    def __init__(self,
                 outer: Optional[Ln] = None,
                 inner: Optional[List[Ln]] = None):

        self._outer = outer.close() if outer is not None else None
        self._inner = [inn.close() for inn in inner] if inner is not None else []

    def num_inner_holes(self) -> numbers.Integral:
        """
        Returns the number of inner holes.

        Examples:
         >>> p = Polygon(outer=Ln([(0, 0), (1, 0), (0, 1)]))
         >>> p.num_inner_holes()
         0
         >>> p = Polygon(outer=Ln([(0, 0), (1, 0), (1, 1), (0, 1)]), inner=[Ln([(0.25, 0.25), (0.75, 0.25), (0.75, 0.75)])])
         >>> p.num_inner_holes()
         1
        """

        return len(self._inner)

    def num_outer_points(self) -> numbers.Integral:
        """
        Returns the number of outer points.
        """

        if self._outer is None:
            return 0

        return self._outer.num_points()

    def outer_segments(self) -> Union[type(None), List[Segment]]:
        """
        Returns a list of the outer segments.

        Examples:
         >>> Polygon().outer_segments() is None
         True
         >>> Polygon(outer=Ln([(0, 0)])).outer_segments() is None
         True
         >>> p = Polygon(outer=Ln([(0, 0), (1, 0)]))
         >>> p.outer_segments()
         [Segment(start_pt=Point([0. 0.]), end_pt=Point([1. 0.])), Segment(start_pt=Point([1. 0.]), end_pt=Point([0. 0.]))]
         >>> p = Polygon(outer=Ln([(0, 0), (1, 0), (0, 1)]))
         >>> p.outer_segments()
         [Segment(start_pt=Point([0. 0.]), end_pt=Point([1. 0.])), Segment(start_pt=Point([1. 0.]), end_pt=Point([0. 1.])), Segment(start_pt=Point([0. 1.]), end_pt=Point([0. 0.]))]
        """

        return self._outer.segments() if self._outer is not None else None

    def inner_segments(self,
                       ndx: numbers.Integral) -> Union[type(None), List[Segment]]:
        """
        Returns a list of the inner segments of the given inner polygon.

        Examples:
         >>> Polygon().inner_segments(0) is None
         True
         >>> p = Polygon(outer=Ln([(0, 0), (1, 0), (1, 1), (0, 1)]), inner=[Ln([(0.25, 0.25), (0.75, 0.25), (0.75, 0.75)])])
         >>> p.inner_segments(0)
         [Segment(start_pt=Point([0.25 0.25]), end_pt=Point([0.75 0.25])), Segment(start_pt=Point([0.75 0.25]), end_pt=Point([0.75 0.75])), Segment(start_pt=Point([0.75 0.75]), end_pt=Point([0.25 0.25]))]
         >>> p.inner_segments(1) is None
         True
         >>> p.inner_segments(-1)
        [Segment(start_pt=Point([0.25 0.25]), end_pt=Point([0.75 0.25])), Segment(start_pt=Point([0.75 0.25]), end_pt=Point([0.75 0.75])), Segment(start_pt=Point([0.75 0.75]), end_pt=Point([0.25 0.25]))]        """

        num_inter_hls = self.num_inner_holes()

        if num_inter_hls == 0:
            return None

        if not(-num_inter_hls <= ndx < num_inter_hls):
            return None

        return self._inner[ndx].segments()

    def __repr__(self) -> str:
        """
        Represents a Polygon instance as a shortened text.

        :return: a textual shortened representation of a Ln instance.
        :rtype: str.
        """

        n_pts = self.num_outer_points()

        if n_pts == 0:
            txt = "Empty Polygon"
        elif n_pts <= 4:
            txt = f"Polygon with {n_pts} point(s): " + ", ".join([f"{pt}" for pt in self._outer.pts()])
        else:
            txt = f"Polygon with {n_pts} points: {self._outer.pt(0)}, {self._outer.pt(1)}, .., {self._outer.pt(-2)}, {self._outer.pt(-1)}"

        return txt

    def point_in_polygon(self,
                         pt: Point
                         ) -> bool:
        """
        Checks whether a point is contained in the polygon.

        Source:

        https://web.archive.org/web/20130109225203/http://geomalgorithms.com/index.html

        // Copyright 2000 softSurfer, 2012 Dan Sunday
        // This code may be freely used and modified for any purpose
        // providing that this copyright notice is included with it.
        // SoftSurfer makes no warranty for this code, and cannot be held
        // liable for any real or imagined damage resulting from its use.
        // Users of this code must verify correctness for their application.

        // wn_PnPoly(): winding number test for a point in a polygon
        //      Input:   P = a point,
        //               V[] = vertex points of a polygon V[n+1] with V[n]=V[0]
        //      Return:  wn = the winding number (=0 only when P is outside)
        int
        wn_PnPoly( Point P, Point* V, int n )
        {
            int    wn = 0;    // the  winding number counter

            // loop through all edges of the polygon
            for (int i=0; i<n; i++) {   // edge from V[i] to  V[i+1]
                if (V[i].y <= P.y) {          // start y <= P.y
                    if (V[i+1].y  > P.y)      // an upward crossing
                         if (isLeft( V[i], V[i+1], P) > 0)  // P left of  edge
                             ++wn;            // have  a valid up intersect
                }
                else {                        // start y > P.y (no test needed)
                    if (V[i+1].y  <= P.y)     // a downward crossing
                         if (isLeft( V[i], V[i+1], P) < 0)  // P right of  edge
                             --wn;            // have  a valid down intersect
                }
            }
            return wn;
        }
        """

        for inner_ln in self._inner:

            wn = calculate_wn(
                pt.coords,
                inner_ln.coords
            )

            if wn != 0:

                return False

        wn = calculate_wn(
            pt.coords,
            self._outer.coords
        )

        if wn != 0:

            return True


    def intersect_segment_base(self,
                               segment: Segment) -> Tuple[Dict[numbers.Integral, Union[type(None), Point, Segment]], Dict[numbers.Integral, Union[type(None), Point, Segment]]]:
        """
        Intersects the polygon with a segment.
        """

        intersections_outer = dict()

        for ndx_outer_segment, outer_segment in enumerate(self.outer_segments()):
            intersections_outer[ndx_outer_segment] = segment.intersect_segments2d(outer_segment)

        intersections_inner = dict()

        for ndx_inner_hole in range(self.num_inner_holes()):

            for ndx_inner_segment, inner_segment in enumerate(self.inner_segments(ndx_inner_hole)):
                intersections_inner[(ndx_inner_hole, ndx_inner_segment)] = segment.intersect_segments2d(inner_segment)

        return intersections_outer, intersections_inner

    def area(self):

        return NotImplemented

    def length(self):

        return NotImplemented

    def clone(self):

        return NotImplemented


class Circle2D(Shape):

    embedding_space = 2

    def __init__(self,
                 x: numbers.Real,
                 y: numbers.Real,
                 r: numbers.Real
                 ):

        self._x = float(x)
        self._y = float(y)
        self._r = float(r)

    @property
    def x(self) -> numbers.Real:
        """
        Return the x coordinate of the current circle.

        :return: x coordinate.

        Examples:
          >>> Circle2D(4, 3, 2).x
          4.0
          >>> Circle2D(-0.39, 3, 7).x
          -0.39
        """

        return self._x

    @property
    def y(self) -> numbers.Real:
        """
        Return the y coordinate of the current circle.

        :return: y coordinate.

        Examples:
          >>> Point(4, 3).y
          3.0
          >>> Point(-0.39, 17.42).y
          17.42
        """

        return self._y

    @property
    def radius(self):
        return self._r

    def area(self):
        return math.pi * self._r * self._r

    def length(self):
        return 2.0 * math.pi * self._r

    def clone(self):
        return Circle2D(self._x, self._y, self._r)



if __name__ == "__main__":

    import doctest
    doctest.testmod()

