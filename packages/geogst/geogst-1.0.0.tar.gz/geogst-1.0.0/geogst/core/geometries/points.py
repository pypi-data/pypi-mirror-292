
#from geogst.core.geometries.shape import *
from geogst.core.geometries.shape import *
from geogst.core.mathematics.vectors2d import *
from geogst.core.mathematics.vectors3d import *
from geogst.core.mathematics.arrays import *


class Point(Shape):

    proper_space = 0

    def __init__(self,
        *coords: Union[numbers.Real, np.ndarray]
    ):

        self._coords = np.float64(coords)

    @property
    def coords(self) -> np.ndarray:

        return self._coords

    def __repr__(self) -> str:

        return f"Point({self._coords})"

    def __add__(self,
                another: 'Point'
                ) -> 'Point':
        """Return point sum

        Example:
          >>> Point(1., 1., 3.) + Point(1., 1., 1.)
          Point([2. 2. 4.])
        """

        return Point(*tuple(self._coords + another._coords))

    def __sub__(self,
                another: 'Point'
                ) -> 'Point':
        """Return point difference

        Example:
          >>> Point(1., 1., 1.) - Point(1., 1., 1.)
          Point([0. 0. 0.])
        """

        return Point(*tuple(self._coords - another._coords))

    def __iter__(self):
        """
        Iterate the point coordinates.
        """

        return (float(a) for a in np.nditer(self._coords))

    def clone(self) -> 'Point':
        """
        Clone a point."""

        return Point(*tuple(self._coords))

    @property
    def x(self):
        """
        x coordinate.

        Examples:
         >>> Point(1, 2, 4).x
         1.0
        """

        return self._coords[0]

    @property
    def y(self):
        """
        y coordinate.

        Examples:
         >>> Point(1, 2, 4).y
         2.0
        """

        return self._coords[1]

    @property
    def z(self):
        """
        z coordinate.

        Examples:
         >>> Point(1, 2, 4).z
         4.0
        """

        return self._coords[2]

    def xy(self) -> Tuple[numbers.Real, numbers.Real]:
        """
        Returns the spatial components as a tuple of two values.

        :return: the spatial components (x, y).
        :rtype: a tuple of two floats.

        Examples:
          >>> Point(1, 0).xy()
          (1.0, 0.0)
        """

        return self._coords[0], self._coords[1]

    def xyz(self) -> Tuple[numbers.Real, numbers.Real, numbers.Real]:
        """
        Returns the spatial components as a tuple of three values.

        :return: the spatial components (x, y).

        Examples:
          >>> Point(1, 0, 3).xyz()
          (1.0, 0.0, 3.0)
        """

        return self._coords[0], self._coords[1], self._coords[2]

    def is_2d(self):
        """
        Checks whether the point is 2D.

        Examples:
         >>> Point(1, 2, 4).is_2d()
         False
         >>> Point(1, 2).is_2d()
         True
        """

        return self.coords.shape[0] == 2

    def as_point2d(self):
        """Converts a point to a point 2D"""

        return Point(*tuple(self._coords[:2]))

    def as_point3d(self):
        """Converts a point to a point 3D"""

        return Point(*tuple(self._coords[:3]))

    def area(self):
        """Calculate shape area"""

        return 0.0

    def length(self):
        """Calculate shape length"""

        return 0.0

    def distance(self, other: 'Point') -> numbers.Real:
        """Calculate distance between two points

        Examples:
         >>> Point(0, 0, 0).distance(Point(0, 0, 1))
         1.0
         >>> Point(1., 1., 1.).distance(Point(4., 5., 1))
          5.0
         >>> Point(1, 1, 1).distance(Point(4, 5, 1))
          5.0
         >>> Point(1, 1, 1).distance(Point(4, 5, 1))
          5.0
        """

        return np.linalg.norm(self._coords - other._coords)

    def distance_2d(self, other: 'Point') -> numbers.Real:
        """Calculate 2D distance between two points

        Examples:
         >>> Point(0, 0, 0).distance_2d(Point(0, 0, 1))
         0.0
        """

        return np.linalg.norm(self._coords[:2] - other._coords[:2])

    def distance_3d(self, other: 'Point') -> numbers.Real:
        """Calculate 3D distance between two points

        Examples:
         >>> Point(0, 0, 0).distance_3d(Point(0, 0, 1))
         1.0
         >>> Point(1, 0, 0).distance_3d(Point(0, 0, 1))
         1.4142135623730951
         >>> Point(1., 1., 1.).distance_3d(Point(4., 5., 1))
          5.0
         >>> Point(1, 1, 1).distance_3d(Point(4, 5, 1))
          5.0
         >>> Point(1, 1, 1).distance_3d(Point(4, 5, 1))
          5.0
        """

        return np.linalg.norm(self._coords[:3] - other._coords[:3])

    def is_coincident(self,
                      other: 'Point',
                      tolerance: numbers.Real = MIN_SEPARATION_THRESHOLD
                      ) -> bool:
        """
        Check whether two points are coincident.

        Example:
          >>> Point(1., 0., -1.).is_coincident(Point(1., 1.5, -1.))
          False
          >>> Point(1., 0., 0.).is_coincident(Point(1., 0., 0.))
          True
          >>> Point(1., 0., 0.).is_coincident(Point(1., 0., 1e-7), tolerance=1e-9)
          False
          >>> Point(1., 0., 0.).is_coincident(Point(1., 0., 1e-9), tolerance=1e-7)
          True
          """

        return self.distance(other) < tolerance

    def is_coincident_2d(self,
                      other: 'Point',
                      tolerance: numbers.Real = MIN_SEPARATION_THRESHOLD
                      ) -> bool:
        """
        Check whether two points are coincident in 2D.

        Example:
          >>> Point(1., 0., -1.).is_coincident_2d(Point(1., 1., -1.))
          False
          >>> Point(1., 0., 0.).is_coincident_2d(Point(1., 0., -1.))
          True
          >>> Point(1., 0.).is_coincident_2d(Point(1., 1e-7), tolerance=1e-9)
          False
          >>> Point(1., 0.).is_coincident_2d(Point(1., 1e-9), tolerance=1e-7)
          True
          """

        return self.distance_2d(other) < tolerance

    def is_coincident_3d(self,
                      other: 'Point',
                      tolerance: numbers.Real = MIN_SEPARATION_THRESHOLD
                      ) -> bool:
        """
        Check whether two points are coincident in 3D.

        Example:
          >>> Point(1., 0., -1.).is_coincident_3d(Point(1., 1., -1.))
          False
          >>> Point(1., 0., 0.).is_coincident_3d(Point(1., 0., 0.))
          True
          >>> Point(1., 0., 4.2).is_coincident_3d(Point(1., 1e-7, 4.2), tolerance=1e-9)
          False
          >>> Point(1., 0., 4.2).is_coincident_3d(Point(1., 1e-9, 4.2), tolerance=1e-7)
          True
          """

        return self.distance_3d(other) < tolerance

    def shift(self,
        *s
    ) -> 'Point':
        """
        Create a new object shifted by given amount from the self instance.

        Example:
          >>> Point(1, 1).shift(0.5, 1.)
          Point([1.5 2. ])
          >>> Point(1, 2).shift(0.5, 1.)
          Point([1.5 3. ])
          >>> Point(1, 1, 1).shift(0.5, 1., 1.5)
          Point([1.5 2.  2.5])
          >>> Point(1, 2, -1).shift(0.5, 1., 1.5)
          Point([1.5 3.  0.5])
       """

        return Point(*tuple(self._coords + s))

    def shift2d_by_vect(self,
                      v: Union[Vect2D, Vect3D]
                      ) -> 'Point':
        """
        Create a new point shifted from the self instance by given vector.

        :param v: the shift vector.
        :return: the shifted point.
       """

        x, y = self.x, self.y

        sx, sy = v.to_xy()

        x = x + sx
        y = y + sy

        return Point(x, y)

    def shift_by_vect(self,
                      v: Vect3D
                      ) -> 'Point':
        """
        Create a new point shifted from the self instance by given vector.

        :param v: the shift vector.
        :return: the shifted point.

        Example:
          >>> Point(1, 1, 1).shift_by_vect(Vect3D(0.5, 1., 1.5))
          Point([1.5 2.  2.5])
          >>> Point(1, 2, -1).shift_by_vect(Vect3D(0.5, 1., 1.5))
          Point([1.5 3.  0.5])
       """

        x, y, z = self.xyz()

        sx, sy, sz = v.to_xyz()

        x = x + sx
        y = y + sy
        z = z + sz

        return Point(x, y, z)

    def has_valued_z(self) -> bool:
        """
        Checks whether a point has z defined.

        Examples:
         >>> Point(0, 0).has_valued_z()
         False
         >>> Point(0, 0, 0).has_valued_z()
         True
        """

        try:
            return np.isfinite(self.z)
        except Exception as e:
            return False

    def to2d(self) -> 'Point':
        """
        Projection on the x-y plane as a 2D point.

        Examples:
          >>> Point(2, 3, 4).to2d()
          Point([2. 3.])
        """

        return Point(*tuple(self._coords[:2]))

    @classmethod
    def pt2d_to_3d(cls,
                   pt: 'Point',
                   z: Optional[numbers.Real] = 0.0
                   ) -> 'Point':
        """
        Create a 3D point from a 2D point and an optional z value.

        :param pt: the 2D point to convert to a 3D point.
        :param z: the optional elevation value.
        :return: a 3D point.
        """

        return Point(pt._coords[0], pt._coords[1], z)

    def as_vector(self) -> Union[type(None), Vect3D]:
        """
        Create a vector based on the point coordinates

        Example:
          >>> Point(1, 1, 0).as_vector()
          Vect3D(1.0000, 1.0000, 0.0000)
          >>> Point(0.2, 1, 6).as_vector()
          Vect3D(0.2000, 1.0000, 6.0000)
        """

        if not self.has_valued_z():
            return None
        else:
            return Vect3D(*self.xyz())

    def rotate(self,
        rotation_axis: RotationAxis,
        center_point: 'Point' = None
        ) -> Union[type(None), 'Point']:
        """
        Rotates the point around a rotation axis passing through a point..

        :param rotation_axis: the rotation axis.
        :param center_point: the point contained in the rotation axis.
        :return: the rotated point.

        Examples:
          >>> pt = Point(0,0,1)
          >>> rot_axis = RotationAxis(0,0,90)
          >>> center_pt = Point(0,0,0.5)
          >>> pt.rotate(rotation_axis=rot_axis, center_point=center_pt)
          Point([0.5 0.  0.5])
          >>> center_pt = Point(0,0,1)
          >>> pt.rotate(rotation_axis=rot_axis, center_point=center_pt)
          Point([0. 0. 1.])
          >>> center_pt = Point(0, 0, 2)
          >>> pt.rotate(rotation_axis=rot_axis, center_point=center_pt)
          Point([-1.  0.  2.])
          >>> rot_axis = RotationAxis(0,0,180)
          >>> pt.rotate(rotation_axis=rot_axis, center_point=center_pt)
          Point([-1.2246468e-16  0.0000000e+00  3.0000000e+00])
          >>> pt.rotate(rotation_axis=rot_axis)
          Point([ 1.2246468e-16  0.0000000e+00 -1.0000000e+00])
          >>> pt = Point(1,1,1)
          >>> rot_axis = RotationAxis(0,90,90)
          >>> pt.rotate(rotation_axis=rot_axis)
          Point([ 1. -1.  1.])
          >>> rot_axis = RotationAxis(0,90,180)
          >>> pt.rotate(rotation_axis=rot_axis)
          Point([-1. -1.  1.])
          >>> center_pt = Point(1,1,1)
          >>> pt.rotate(rotation_axis=rot_axis, center_point=center_pt)
          Point([1. 1. 1.])
          >>> center_pt = Point(2,2,10)
          >>> pt.rotate(rotation_axis=rot_axis, center_point=center_pt)
          Point([3. 3. 1.])
          >>> pt = Point(1, 1, 2)
          >>> rot_axis = RotationAxis(135, 0, 180)
          >>> center_pt = Point(0,0,1)
          >>> pt.rotate(rotation_axis=rot_axis, center_point=center_pt)
          Point([-1.00000000e+00 -1.00000000e+00  2.22044605e-16])
        """

        if not center_point:

            center_point = Point(0.0, 0.0, 0.0)

        p_diff = self - center_point

        p_vect = p_diff.as_vector()

        rot_vect = rotate_vector_via_axis(
            v=p_vect,
            rot_axis=rotation_axis
        )

        x, y, z = rot_vect

        rot_pt = Point(x, y, z)

        transl_pt = center_point + rot_pt

        return transl_pt

    @classmethod
    def random(cls,
        lower_boundary: float = -MAX_SCALAR_VALUE,
        upper_boundary: float =  MAX_SCALAR_VALUE,
        dim: Optional[numbers.Integral] = 3
    ):
        """
        Creates a random point.

        :return: random point
        """

        vals = [random.uniform(lower_boundary, upper_boundary) for _ in range(dim)]
        return cls(*vals)


def collapsable_points(
    points: List[Point],
    atol: numbers.Real = 1e-3
) -> Union[type(None), Point]:
    """
    Return the single point, the collapsed point or nothing,
    based on a distance tolerance between points.

    :param points: the point list.
    :param atol: the optional absolute tolerance distance between the points
    :return: nothing or the unique/collapsed point.

    Examples:
     >>> collapsable_points([]) is None
     True
     >>> collapsable_points([Point(1,2,3)])
     Point([1. 2. 3.])
     >>> collapsable_points([Point(1,2,3), Point(4, 5, 6)]) is None
     True
     >>> collapsable_points([Point(1,2,3), Point(1,2,3)])
     Point([1. 2. 3.])
     >>> collapsable_points([Point(1,2,3.001), Point(1,2,3), Point(1.0001,2,3)], atol=1e-2)
     Point([1.    2.    3.001])
     >>> collapsable_points([Point(1,2,3.001), Point(1,2,3)], atol=1e-6) is None
     True
    """

    if not points:
        return None
    elif len(points) == 1:
        return points[0]
    else:
        start_pt = points[0]
        for pt in points[1:]:
            if pt.distance(start_pt) > atol:
                return None
        return start_pt


def remove_coincident_points(
    pts: List[Point],
    atol: numbers.Real = MIN_POINT_POS_DIFF
) -> List[Point]:
    """
    Filters out successive coincident points,
    based on the input atol maximum disxtance.

    Examples:
    >>> remove_coincident_points([], atol=1.e-3)
    []
    >>> remove_coincident_points([Point(1,2,3)], atol=1.e-3)
    [Point([1. 2. 3.])]
    >>> remove_coincident_points([Point(1,2,3), Point(4,5,6)], atol=1.e-3)
    [Point([1. 2. 3.]), Point([4. 5. 6.])]
    >>> remove_coincident_points([Point(1,2,3), Point(1,2,3.000001)], atol=1.e-2)
    [Point([1. 2. 3.])]
    """

    if len(pts) <= 1:
        return pts

    filtered_pts = [pts[0].clone()]

    for pt in pts[1:]:
        if pt.distance(filtered_pts[-1]) > atol:
            filtered_pts.append(pt.clone())

    return filtered_pts


def remove_coincident_points_2d(
    pts: List[Point],
    atol: numbers.Real = MIN_POINT_POS_DIFF
) -> List[Point]:
    """
    Filters out successive coincident points,
    based on the input atol maximum disxtance.

    Examples:
    >>> remove_coincident_points([], atol=1.e-3)
    []
    >>> remove_coincident_points([Point(1,2,3)], atol=1.e-3)
    [Point([1. 2. 3.])]
    >>> remove_coincident_points([Point(1,2,3), Point(4,5,6)], atol=1.e-3)
    [Point([1. 2. 3.]), Point([4. 5. 6.])]
    >>> remove_coincident_points([Point(1,2,3), Point(1,2,3.000001)], atol=1.e-2)
    [Point([1. 2. 3.])]
    """

    if len(pts) <= 1:
        return pts

    filtered_pts = [pts[0].clone()]

    for pt in pts[1:]:
        if pt.distance_2d(filtered_pts[-1]) > atol:
            filtered_pts.append(pt.clone())

    return filtered_pts


def calculate_best_fit_plane_from_coordinates(
    coordinates: List[Tuple[numbers.Real, numbers.Real, numbers.Real]],
) -> Tuple[Union[None, Tuple[Plane, Point, np.ndarray]], Error]:

    try:

        xyz_array = np.array(
            coordinates,
            dtype=np.float64
        )

        xyz_mean = np.mean(
            xyz_array,
            axis=0
        )

        (_, sorted_eigenvalues, sorted_eigenvectors), err = singular_value_decomposition(
            xyz_array=xyz_array - xyz_mean
        )

        if err:
            return None, err

        lowest_eigenvector = sorted_eigenvectors[-1, : ]  # Solution is last row
        normal = lowest_eigenvector[: 3 ] / np.linalg.norm(lowest_eigenvector[: 3 ])
        normal_vector = Vect3D(normal[0], normal[1], normal[2])
        direction_normal_to_best_fit_plane, err = Direct.from_vector(normal_vector)

        if err:
            return None, err

        best_fit_geological_plane = direction_normal_to_best_fit_plane.normal_plane()
        central_point = Point(xyz_mean[0], xyz_mean[1], xyz_mean[2])

        return (best_fit_geological_plane, central_point, sorted_eigenvalues), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


if __name__ == "__main__":

    import doctest
    doctest.testmod()
