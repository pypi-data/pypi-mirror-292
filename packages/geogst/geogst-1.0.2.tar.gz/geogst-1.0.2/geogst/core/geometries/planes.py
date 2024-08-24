
from typing import Type

from geogst.core.utils.lists import *
from geogst.core.geometries.lines import *
from geogst.core.mathematics.arrays import *

def geolplane_to_cartplane_comps(
    geol_plane: Plane,
    pt: Point
) -> Tuple[numbers.Real, numbers.Real, numbers.Real, numbers.Real]:
    """
    Calculate the Cartesian plane components
    provided a geological plane and a point lying in the plane.

    :param geol_plane: the source geological plane.
    :param pt: the point lying in the plane.
    :return: the tuple of the Cartesian plane components (a, b, c and d).
    """

    normal_versor = geol_plane.norm_direct_frwrd().as_versor()
    a, b, c = normal_versor.x, normal_versor.y, normal_versor.z
    d = - (a * pt.x + b * pt.y + c * pt.z)

    return a, b, c, d


class CPlane3D:
    """
    Cartesian plane.
    Expressed by equation:
    ax + by + cz + d = 0

    Note: CPlane3D is locational - its position in space is defined.
    This contrast with Plane, defined just by its plane attitude, but with undefined position

    """

    def __init__(self,
                 a: numbers.Real,
                 b: numbers.Real,
                 c: numbers.Real,
                 d: numbers.Real
                 ):

        if not isinstance(a, numbers.Real):
            raise Exception("Input value a must be float or int but is {}".format(type(a)))
        if not isinstance(b, numbers.Real):
            raise Exception("Input value b must be float or int but is {}".format(type(b)))
        if not isinstance(c, numbers.Real):
            raise Exception("Input value c must be float or int but is {}".format(type(c)))
        if not isinstance(d, numbers.Real):
            raise Exception("Input value d must be float or int but is {}".format(type(d)))

        norm = sqrt(a * a + b * b + c * c)
        self._a = float(a) / norm
        self._b = float(b) / norm
        self._c = float(c) / norm
        self._d = float(d) / norm

    def a(self) -> numbers.Real:
        """
        Return a coefficient of a CPlane3D instance.

        Example:
          >>> CPlane3D(1, 0, 0, 2).a()
          1.0
        """

        return self._a

    def b(self) -> numbers.Real:
        """
        Return b coefficient of a CPlane3D instance.

        Example:
          >>> CPlane3D(1, 4, 0, 2).b()
          0.9701425001453319
        """

        return self._b

    def c(self) -> numbers.Real:
        """
        Return a coefficient of a CPlane3D instance.

        Example:
          >>> CPlane3D(1, 0, 5.4, 2).c()
          0.9832820049844602
        """

        return self._c

    def d(self) -> numbers.Real:
        """
        Return a coefficient of a CPlane3D instance.

        Example:
          >>> CPlane3D(1, 0, 0, 2).d()
          2.0
        """

        return self._d

    def v(self) -> Tuple[numbers.Real, numbers.Real, numbers.Real, numbers.Real]:
        """
        Return coefficients of a CPlane3D instance.

        Examples:
          >>> CPlane3D(1, 1, 7, -4).v()
          (0.14002800840280097, 0.14002800840280097, 0.9801960588196068, -0.5601120336112039)
        """

        return self.a(), self.b(), self.c(), self.d()

    def clone(self) -> 'CPlane3D':
        """
        Clones a Cartesian plane.
        """

        return CPlane3D(*self.v())

    @classmethod
    def from_points(cls, pt1, pt2, pt3) -> 'CPlane3D':
        """
        Create a CPlane3D from three given Point instances.

        Example:
          >>> CPlane3D.from_points(Point(0, 0, 0), Point(1, 0, 0), Point(0, 1, 0))
          CPlane3D(0.00000000, 0.00000000, 1.00000000, 0.00000000)
          >>> CPlane3D.from_points(Point(0, 0, 0), Point(1, 0, 0), Point(0, 1, 0))
          CPlane3D(0.00000000, 0.00000000, 1.00000000, 0.00000000)
          >>> CPlane3D.from_points(Point(0, 0, 0), Point(0, 1, 0), Point(0, 0, 1))
          CPlane3D(1.00000000, 0.00000000, 0.00000000, 0.00000000)
          >>> CPlane3D.from_points(Point(1,2,3), Point(2,3,4), Point(-1,7,-2))
          CPlane3D(-0.79555728, 0.23866719, 0.55689010, -1.35244738)
        """

        if not (isinstance(pt1, Point)):
            raise Exception(f"First input point should be Point but is {type(pt1)}")

        if not (isinstance(pt2, Point)):
            raise Exception(f"Second input point should be Point but is {type(pt2)}")

        if not (isinstance(pt3, Point)):
            raise Exception(f"Third input point should be Point but is {type(pt3)}")

        matr_a = np.array(
            [[pt1.y, pt1.z, 1],
             [pt2.y, pt2.z, 1],
             [pt3.y, pt3.z, 1]])

        matr_b = - np.array(
            [[pt1.x, pt1.z, 1],
             [pt2.x, pt2.z, 1],
             [pt3.x, pt3.z, 1]])

        matr_c = np.array(
            [[pt1.x, pt1.y, 1],
             [pt2.x, pt2.y, 1],
             [pt3.x, pt3.y, 1]])

        matr_d = - np.array(
            [[pt1.x, pt1.y, pt1.z],
             [pt2.x, pt2.y, pt2.z],
             [pt3.x, pt3.y, pt3.z]])

        return cls(
            float(determinant3x3(matr_a)),
            float(determinant3x3(matr_b)),
            float(determinant3x3(matr_c)),
            float(determinant3x3(matr_d))
        )

    @classmethod
    def from_geol_plane(cls,
                        geol_plane: Plane,
                        pt: Point
                        ):
        """
          Given a Plane instance and a provided Point instance,
          calculate the corresponding Plane instance.

          Example:
            >>> CPlane3D.from_geol_plane(Plane(0, 0), Point(0, 0, 0))
            CPlane3D(0.00000000, 0.00000000, 1.00000000, -0.00000000)
            >>> CPlane3D.from_geol_plane(Plane(90, 45), Point(0, 0, 0))
            CPlane3D(0.70710678, 0.00000000, 0.70710678, -0.00000000)
            >>> CPlane3D.from_geol_plane(Plane(0, 90), Point(0, 0, 0))
            CPlane3D(0.00000000, 1.00000000, -0.00000000, -0.00000000)
          """

        check_type(geol_plane, "Geological plane", Plane)
        check_type(pt, "point", Point)

        components = geolplane_to_cartplane_comps(
            geol_plane=geol_plane,
            pt=pt
        )

        return CPlane3D(*components)

    def __repr__(self):

        return "CPlane3D({:.8f}, {:.8f}, {:.8f}, {:.8f})".format(*self.v())

    def normal_versor(self) -> Tuple[Vect3D, Error]:
        """
        Return the versor normal to the cartesian plane.

        Examples:
          >>> vers, _ = CPlane3D(0, 0, 5, -2).normal_versor()
          >>> vers
          Vect3D(0.0000, 0.0000, 1.0000)
          >>> vers, _ = CPlane3D(0, 7, 0, 5).normal_versor()
          >>> vers
          Vect3D(0.0000, 1.0000, 0.0000)
        """

        try:

            return Vect3D(self.a(), self.b(), self.c()).to_versor()

        except Exception as e:

            return Vect3D(), Error(True, caller_name(), e, traceback.format_exc())

    def normal_axis(self) -> Tuple[Union[Axis, type(None)], Error]:
        """
        Return the normal axis to the plane.
        """
        try:

            normal_vers, err = self.normal_versor()
            if err:
                return None, err

            direct, err = Direct.from_vector(normal_vers)
            if err:
                return None, err

            return Axis.from_direction(direct), Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc()
            )

    def as_lying_point(self) -> Point:
        """
        Returns a point lying in the plane (non-unique solution).

        Examples:
          >>> CPlane3D(0, 0, 1, -1).as_lying_point()
          Point([0. 0. 1.])
        """

        point = Point(
            *point_solution(
                np.array([[self.a(), self.b(), self.c()]]),
                np.array([-self.d()]))
        )

        return point

    def intersects_other(self,
        another: 'CPlane3D',
        ang_tol_degr: numbers.Real = MIN_DISORIENTATION_TOLERANCE,
        d_tol: numbers.Real = MIN_DISTANCE_TOLERANCE
    ) -> Tuple[Union[type(None), Vect3D, 'CPlane3D'], Error]:
        """
        Return intersection versor for two intersecting planes.

        :param another: the other Cartesian plane to intersect with.
        :param ang_tol_degr: the angular tolerance for plane parallelism.
        :param d_tol: the tolerance for the parameter d of the Cartesian plane equation.
        :return: the intersection line as a vector and the error status.

        Examples:
          >>> a = CPlane3D(1, 0, 0, 0)
          >>> result, _ = a.intersects_other(a)
          >>> result
          CPlane3D(1.00000000, 0.00000000, 0.00000000, 0.00000000)
          >>> b = CPlane3D(0, 0, 1, 0)
          >>> result, _ = a.intersects_other(b)
          >>> result
          Vect3D(0.0000, -1.0000, 0.0000)
          >>> b = CPlane3D(1, 0, 0, 1)  # parallel plane, no intersection
          >>> result, _ = a.intersects_other(b)
          >>> result is None
          True
        """

        try:

            are_coincident, err = self.is_coincident_with_plane(
                another,
                ang_tol_degr=ang_tol_degr,
                d_tol=d_tol
            )
            if err:
                return None, err

            if are_coincident:
                return self.clone(), Error()

            are_parallel, err = self.is_parallel_to_plane(
                another,
                ang_tol_degr=ang_tol_degr
            )
            if err:
                return None, err

            if are_parallel:
                return None, Error()

            self_normal, err = self.normal_versor()
            if err:
                return None, err

            another_normal, err = another.normal_versor()
            if err:
                return None, err

            cross_vect, err = self_normal.cross_vector(another_normal)
            if err:
                return None, err

            return cross_vect.to_versor()

        except Exception as e:

            return Vect3D(), Error(True, caller_name(), e, traceback.format_exc())

    def intersects_other_as_pt(self,
       another: 'CPlane3D',
       ang_tol_degr: numbers.Real = MIN_DISORIENTATION_TOLERANCE,
       d_tol: numbers.Real = MIN_DISTANCE_TOLERANCE
    ) -> Tuple[Union[type(None), Point], Error]:
        """
        Return point on intersection line (non-unique solution)
        for two planes.

        :param another: the second cartesian plane
        :param ang_tol_degr: the angular tolerance angle,
        :param d_tol: the minimum accepted distance,
        :return: the optional instersection point

        Examples:
          >>> p_a = CPlane3D(1, 0, 0, 0)
          >>> p_b = CPlane3D(0, 0, 1, 0)
          >>> pt, error = p_a.intersects_other_as_pt(p_b)
          >>> pt
          Point([0. 0. 0.])
          >>> p_b = CPlane3D(-1, 0, 0, 0)
          >>> pt, error = p_a.intersects_other_as_pt(p_b)
          >>> pt
          Point([0. 0. 0.])
          >>> p_a = CPlane3D(1, 7, 2, 4.5)
          >>> pt, error = p_a.intersects_other_as_pt(p_a)  # planes are coincident
          >>> pt
          Point([-0.08333333 -0.58333333 -0.16666667])
          >>> p_b = CPlane3D(1, 7, 2, 9.0)  # second plane is parallel to first plane but not coincident
          >>> pt, error = p_a.intersects_other_as_pt(p_b)
          >>> pt is None
          True
        """

        try:

            check_type(another, "Second plane", CPlane3D)

            are_parallel, error = self.is_parallel_to_plane(another, ang_tol_degr=ang_tol_degr)
            if error:
                return None, error

            are_coincident, error = self.is_coincident_with_plane(another, ang_tol_degr=ang_tol_degr, d_tol=d_tol)
            if error:
                return None, error

            if are_parallel and not are_coincident:
                return None, Error()

            # find a point lying on the intersection line (this is a non-unique solution)

            a = np.array([[self.a(), self.b(), self.c()], [another.a(), another.b(), another.c()]])
            b = np.array([-self.d(), -another.d()])
            x, y, z = point_solution(a, b)

            if x is not None and y is not None and z is not None:
                return Point(x, y, z), Error()
            else:
                return None, Error(True, caller_name(), Exception(f"Got x = {x}, y= {y}, z = {z}"), traceback.format_exc())

        except Exception as e:

            return None, Error(True, caller_name(), e, traceback.format_exc())

    def shift(
        self,
        dx: numbers.Real,
        dy: numbers.Real,
        dz: numbers.Real
    ) -> Tuple[Union[type(None), 'CPlane3D'], Error]:
        """
        Shift a Cartesian plane by the provided values.

        :param dx: the shift along the x direction.
        :param dy: the shift along the y direction.
        :param dz: the shift along the z direction.
        :return: the potential shifted plane and the error status.
        """

        point_in_plane = self.as_lying_point()
        shifted_point = point_in_plane.shift(dx, dy, dz)

        normal_vers, err = self.normal_versor()
        if err:
            return None, err

        shifted_plane, err = create_plane_from_vector(
            vector=normal_vers,
            point=shifted_point)

        if err:
            return None, err

        return shifted_plane, Error()

    def vector_offset(self,
                      vect: Vect3D
                      ) -> Tuple[Union[type(None), 'CPlane3D'], Error]:
        """
        Returns a new plane instance, offset by the
        provided vector components.
        """

        return self.shift(*vect.a)

    def absolute_distance_to_point(self,
                                   pt: Point
                                   ) -> numbers.Real:
        """
        Calculate the absolute distance between a 3D point and the cartesian plane.
        Distance expression:
        distance = a * x1 + b * y1 + c * z1 + d
        where a, b, c and d are plane parameters of the plane equation:
         a * x + b * y + c * z + d = 0
        and x1, y1, and z1 are the point coordinates.

        :param pt: the point to calculate distance with.
        :return: the distance value.
        :raise: Exception.

        Examples:
          >>> cpl = CPlane3D(0, 0, 1, 0)
          >>> pt = Point(0, 0, 1)
          >>> cpl.absolute_distance_to_point(pt)
          1.0
          >>> pt = Point(0, 0, 0.5)
          >>> cpl.absolute_distance_to_point(pt)
          0.5
          >>> pt = Point(0, 0, -0.5)
          >>> cpl.absolute_distance_to_point(pt)
          0.5
          >>> pt = Point(10, 20, 0.0)
          >>> cpl.absolute_distance_to_point(pt)
          0.0
          >>> # example from Zwirner, 'Istituzioni di matematiche', 1983, vol. II, p. 195
          >>> cpl = CPlane3D(math.sqrt(3), -3, 2, 4)
          >>> pt = Point(math.sqrt(3), 1, -1)
          >>> are_close(cpl.absolute_distance_to_point(pt), 0.5)
          True
          >>> # example from qgSurf - Profilers, check bug
          >>> cpl = CPlane3D(0.57381239, -0.81898678, 0.00000000, 3714794.62412554)
          >>> pt = Point(331950.34370242, 4768418.68185045, 0.0)
          >>> cpl.absolute_distance_to_point(pt)
          0.017733797430992126
          >>> cpl = CPlane3D(-0.57381239, 0.81898678, 0.00000000, 3714794.62412554)
          >>> cpl.absolute_distance_to_point(pt)
          7429589.248405428
        """

        #check_type(pt, "Input point", Point)

        return abs(self.a() * pt.x + self.b() * pt.y + self.c() * pt.z + self.d())

    def signed_distance_to_point(self,
                          pt: Point
                          ) -> numbers.Real:
        """
        Calculate the signed distance between a 3D point and the cartesian plane.
        Distance expression:
        distance = a * x1 + b * y1 + c * z1 + d
        where a, b, c and d are plane parameters of the plane equation:
         a * x + b * y + c * z + d = 0
        and x1, y1, and z1 are the point coordinates.

        :param pt: the point to calculate distance with.
        :return: the distance value.
        """

        check_type(pt, "Input point", Point)

        return self.a() * pt.x + self.b() * pt.y + self.c() * pt.z + self.d()

    def deltas_with_point(self,
                          pt: Point,
                          axis: Tuple[Axis, type(None)] = None,
                          distance_atol: numbers.Real = MIN_DISTANCE_TOLERANCE,
                          angular_atol: numbers.Real = MIN_DISORIENTATION_TOLERANCE
                          ) -> Tuple[Union[None, Tuple[numbers.Real, numbers.Real, numbers.Real]], Error]:
        """
        Calculates the deltas along the three axis, x, y and z, between a point and its
        projection, normal or along an axis, onto the plane.
        """

        try:

            projected_point, err = self.project_point(
                pt=pt,
                axis=axis,
                distance_atol=distance_atol,
                angular_atol=angular_atol
            )

            if err:
                return None, err

            x, y, z = pt
            xp, yp, zp = projected_point

            return (x-xp, y-yp, z-zp), Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())

    def is_parallel_to_plane(self,
                             plane: 'CPlane3D',
                             ang_tol_degr: numbers.Real = 1e-1
                             ) -> Tuple[Union[type(None), bool], Error]:
        """
        Checks whether the second plane is parallel.

        :param plane: the Cartesian plane for which to check parallelism.
        :param ang_tol_degr: the angular tolerance for plane disorientation.
        :return: the parallelism check and the error status.

        Examples:
        >>> p = CPlane3D(1, 1, 2, 4.5)
        >>> parallel, error = p.is_parallel_to_plane(p)
        >>> parallel
        True
        >>> p_a = CPlane3D(1, 7, 2, 4.5)
        >>> p_b = CPlane3D(1, 7, 2, 9.0)
        >>> parallel, error = p_a.is_parallel_to_plane(p_b)
        >>> parallel
        True
        >>> p_b = CPlane3D(3, 7, 2, 9.0)
        >>> parallel, error = p_a.is_parallel_to_plane(p_b)
        >>> parallel
        False
        >>> p_a = CPlane3D(1, 0, 0, 0)
        >>> p_b = CPlane3D(0, 0, 1, 0)
        >>> parallel, error = p_a.is_parallel_to_plane(p_b)
        >>> parallel
        False
        """

        try:

            internal_angle = self.angle_with(plane)
            if internal_angle is None:
                return None, Error(
                    True,
                    caller_name(),
                    Exception("Angle between planes is None"),
                    traceback.format_exc())
            if internal_angle <= ang_tol_degr:
                return True, Error()
            else:
                return False, Error()

        except Exception as e:

            return None, Error(True, caller_name(), e, traceback.format_exc())

    def is_coincident_with_plane(self,
                                 plane: 'CPlane3D',
                                 ang_tol_degr: numbers.Real = MIN_DISORIENTATION_TOLERANCE,
                                 d_tol: numbers.Real = MIN_DISTANCE_TOLERANCE
                                 ) -> Tuple[Union[type(None), bool], Error]:
        """
        Checks whether the second plane is almost coincident with the first.

        :param plane: the Cartesian plane for which to check parallelism.
        :param ang_tol_degr: the angular tolerance for plane disorientation.
        :param d_tol: the tolerance about the parameter d of the Cartesian plane equation.
        :return: the coincidence check and the error status.

        Examples:
        >>> p = CPlane3D(1, 1, 2, 4.5)
        >>> coincident, error = p.is_coincident_with_plane(p)
        >>> coincident
        True
        >>> p_a = CPlane3D(1, 7, 2, 4.5)
        >>> p_b = CPlane3D(1, 7, 2, 9.0)
        >>> coincident, error = p_a.is_coincident_with_plane(p_b)
        >>> coincident
        False
        >>> p_b = CPlane3D(2, 7, 2, 9.0)
        >>> coincident, error = p_a.is_coincident_with_plane(p_b)
        >>> coincident
        False
        >>> p_b = CPlane3D(1, 7, 2, 4.499999999)
        >>> coincident, error = p_a.is_coincident_with_plane(p_b)
        >>> coincident
        True
        >>> coincident, error = p_a.is_coincident_with_plane(p_b, d_tol=1e-10)
        >>> coincident
        False
        >>> p_a = CPlane3D(1, 0, 0, 0)
        >>> p_b = CPlane3D(0, 0, 1, 0)
        >>> parallel, error = p_a.is_parallel_to_plane(p_b, ang_tol_degr=1e-1)
        >>> parallel
        False
        >>> coincident, _ = p_a.is_coincident_with_plane(p_b)
        >>> coincident
        False
        """

        try:

            are_parallel, err = self.is_parallel_to_plane(plane, ang_tol_degr=ang_tol_degr)
            if err:
                return None, err
            if not are_parallel:
                return False, Error()

            if are_close(self.d(), plane.d(), atol=d_tol):
                return True, Error()
            else:
                return False, Error()

        except Exception as e:

            return None, Error(True, caller_name(), e, traceback.format_exc())

    def contains_point(self,
                       pt: Point,
                       atol: numbers.Real = 1e-2
                       ) -> bool:
        """
        Check whether a point lies in the current 3D plane.

        :param pt: the point to check.
        :param atol: distance tolerance for point-plane separation.
        :return: whether the point lies in the current plane.
        :raise: Exception.

        Examples:
          >>> pl = CPlane3D(0, 0, 1, 0)
          >>> pt = Point(0, 1, 0)
          >>> pl.contains_point(pt)
          True
          >>> pl = CPlane3D(0, 0, 1, 0)
          >>> pt = Point(0, 1, 0)
          >>> pl.contains_point(pt)
          True
          >>> pl = CPlane3D(1, 7, 2, 4.5)
          >>> pt = Point(-0.0833, -0.5833, -0.1667)
          >>> pl.contains_point(pt)
          True
          >>> # Following three examples from Zwirner, 1983, vol. II, p. 167
          >>> pl = CPlane3D(3, 2, 1, -6)
          >>> pl.contains_point(Point(1, 1, 1))
          True
          >>> pl.contains_point(Point(1, 2, -1))
          True
          >>> pl.contains_point(Point(2, 1, -2))
          True
          >>> # Following two examples from Zwirner, 1983, vol. II, p. 170
          >>> pl = CPlane3D(3, -2, 5, 23)
          >>> pl.contains_point(Point(2, -3, -7))
          True
          >>> pl.contains_point(Point(-1, 2, 5))
          False
        """

        check_type(pt, "Input point", Point)

        distance = self.absolute_distance_to_point(pt)

        return distance < atol

    def is_parallel_to_line(self,
                            line: ParamLine3D,
                            ang_tol: numbers.Real = 1e-1
                            ) -> Tuple[Union[Type[None], bool], Error]:
        """
        Checks whether the line is parallel to the plane.

        :param line: the parametric line to check for plane parallelism.
        :param ang_tol: the angular tolerance for disorientation between plane and line.
        :return: whether parallel and error status.

        Examples:
        >>> pl = CPlane3D(0, 0, 1, 5)
        >>> ln = ParamLine3D(srcPt=Point(2, 2, 6), l=7.3, m=9.2, n=0.0)
        >>> parallel, _ = pl.is_parallel_to_line(ln)
        >>> parallel
        True
        """

        try:

            ln_vers = line.as_versor()
            pl_vers, error = self.normal_versor()
            if error:
                return None, error

            plnormal_line_angle = pl_vers.angle_with(ln_vers)
            if plnormal_line_angle is None:
                return None, Error(True, caller_name(), Exception("Angle calculation returns None"), traceback.format_exc())
            disorientation = abs(90.0 - plnormal_line_angle)

            return are_close(disorientation, 0.0, ang_tol), Error()

        except Exception as e:

            return None, Error(True, caller_name(), e, traceback.format_exc())

    def contains_line(self,
                      line: ParamLine3D,
                      ang_tol: numbers.Real = 1e-1,
                      atol: numbers.Real = 1e-5
                      ) -> Tuple[Union[type(None), bool], Error]:
        """
        Checks whether a line is contained in the plane.

        :param line: the parametric line to check for laying in plane.
        :param ang_tol: the angular tolerance for disorientation between plane and line.
        :param atol: the spatial tolerance for line in-plane.
        :return: whether parallel and error status.

        Examples:
        >>> pl = CPlane3D(0, 0, 1, -5)
        >>> ln = ParamLine3D(srcPt=Point(2, 17, 5), l=7.3, m=9.2, n=0.0)
        >>> inplane, error = pl.contains_line(ln)
        >>> inplane
        True
        """

        try:

            is_line_parallel, error = self.is_parallel_to_line(line, ang_tol=ang_tol)
            if error:
                return None, error

            if not is_line_parallel:
                return False, Error()

            within_plane_check = self.a()*line.srcPt.x + self.b()*line.srcPt.y + self.c()*line.srcPt.z
            return are_close(abs(within_plane_check + self.d()), 0.0, atol=atol), Error()

        except Exception as e:

            return None, Error(True, caller_name(), e, traceback.format_exc())

    def angle_with(self,
                      another: 'CPlane3D'
                      ) -> Optional[numbers.Real]:
        """
        Calculate rot_angle (in degrees) between two planes.

        :param another: the CPlane3D instance to calculate rot_angle with.
        :return: the rot_angle (in degrees) between the two planes.
        :raise: Exception.

        Examples:
          >>> CPlane3D(1,0,0,0).angle_with(CPlane3D(0,1,0,0))
          90.0
          >>> CPlane3D(1,0,0,0).angle_with(CPlane3D(0,1,0,0))
          90.0
          >>> CPlane3D(1,0,0,0).angle_with(CPlane3D(1,0,1,0))
          45.0
          >>> CPlane3D(1,0,0,0).angle_with(CPlane3D(1,0,0,0))
          0.0
        """

        check_type(another, "Second Cartesian plane", CPlane3D)

        this_as_versor, error = self.normal_versor()
        if error:
            return None

        other_as_versor, error = another.normal_versor()
        if error:
            return None

        angle_degr = this_as_versor.angle_with(other_as_versor)

        if angle_degr is None:
            return None

        if angle_degr > 90.0:
            angle_degr = 180.0 - angle_degr

        return angle_degr

    def project_point(self,
                      pt: Point,
                      axis: Tuple[Axis, type(None)] = None,
                      distance_atol: numbers.Real = MIN_DISTANCE_TOLERANCE,
                      angular_atol: numbers.Real = MIN_DISORIENTATION_TOLERANCE
                      ) -> Tuple[Union[type(None), Point], Error]:
        """
        Projects a point onto the plane,
        using an optional axis or along the plane normal.
        It returns the projected point and the error status.

        :param pt: the point to project onto the plane.
        :param axis: the optional projection axis.
        :param distance_atol: the optional distance absolute tolerance of point from plane.
        :param angular_atol: the optional angular tolerance between axis and plane.
        :return: the projected point and the error status.
        """

        if axis is None:
            intersection, err = project_point_perpendicular_to_plane(
                plane=self,
                point=pt,
                distance_atol=distance_atol
            )
        else:
            intersection, err = intersect_plane_with_axis(
                plane=self,
                axis=axis,
                src_pt=pt,
                distance_atol=distance_atol,
                angular_atol=angular_atol
            )

        if err:
            return None, err

        if intersection is not None and not isinstance(intersection, Point):
            return None, Error(
                True,
                caller_name(),
                Exception(f"Debug: the result should be a Point but {type(intersection)}"),
                traceback.format_exc()
            )

        return intersection, Error()

    def project_line(self,
                     line: Ln,
                     axis: Tuple[Axis, type(None)] = None,
                     distance_atol: numbers.Real = MIN_DISTANCE_TOLERANCE,
                     angular_atol: numbers.Real = MIN_DISORIENTATION_TOLERANCE,
                     remove_coincident_points: bool = True
                     ) -> Tuple[Union[List[Union[Ln, Point]], type(None)], Error]:
        """
        Projects a line onto the plane,
        using an optional axis or along the plane normal.

        :param line: the line to project onto the plane.
        :param axis: the optional projection axis.
        :param distance_atol: the optional distance absolute tolerance of point from plane.
        :param angular_atol: the optional angular tolerance between axis and plane.
        :param remove_coincident_points: whether to remove coincident points in result.
        :return: the result geometry list or nothing, plus the error.
        """

        projected_points = []

        for pt in line.pts():
            geom, error = self.project_point(
                pt=pt,
                axis=axis,
                distance_atol=distance_atol,
                angular_atol=angular_atol)

            if error:
                return None, error

            if geom is None:
                continue

            if isinstance(geom, ParamLine3D):
                projected_points.append(pt)
            else:
                projected_points.append(geom)

        if not projected_points:
            return None, Error()

        sublines_points = split_list(
            lst=projected_points,
            splitter=None
        )

        if not sublines_points:
            return None, Error()

        projected_geometries = []
        for points in sublines_points:
            if not points:
                continue
            unique_point = collapsable_points(points)
            if unique_point is None:
                projected_geometries.append(
                    Ln.from_points(
                        *points)
                )
            else:  # collapsed points or unique point
                projected_geometries.append(unique_point)

        return projected_geometries, Error()

    def to_geol_plane(self) -> Tuple[Union[Plane, type(None)], Error]:
        """
        Converts the Cartesian plane to a geological plane.
        """

        try:

            normal, error = self.normal_versor()
            if error:
                return None, error

            direct, error = Direct.from_vector(normal)
            if error:
                return None, error

            return direct.normal_plane(), Error()

        except Exception as e:

            return None, Error(True, caller_name(), e, traceback.format_exc())


def create_plane_from_vector(
    vector: Vect3D,
    point: Point
    ) -> Tuple[Union[type(None), CPlane3D], Error]:
        """
        Create a Cartesian plane instance given a vector (normal to the plane)
        and a point (through which the plane passes).

        :param vector: the vector normal to the plane.
        :param point: the point through which the plane passes.
        :return: the potential plane and the error status.
        """

        try:

            normal_versor, err = vector.to_versor()

            if err:
                return None, err

            a, b, c = normal_versor.x, normal_versor.y, normal_versor.z
            d = - (a * point.x + b * point.y + c * point.z)

            return CPlane3D(a, b, c, d), Error()

        except Exception as e:

            return None, Error(True, caller_name(), e, traceback.format_exc())


def shift_plane(
        plane: CPlane3D,
        dx: numbers.Real,
        dy: numbers.Real,
        dz: numbers.Real
) -> Tuple[Union[type(None), CPlane3D], Error]:
    """
    Shift a Cartesian plane by the provided values.

    :param plane: the Cartesian plane to shift.
    :param dx: the shift along the x direction.
    :param dy: the shift along the y direction.
    :param dz: the shift along the z direction.
    :return: the potential shifted plane and the error status.
    """

    point_in_plane = plane.as_lying_point()
    shifted_point = point_in_plane.shift(dx, dy, dz)

    normal_vers, err = plane.normal_versor()
    if err:
        return None, err

    shifted_plane, err = create_plane_from_vector(
        vector=normal_vers,
        point=shifted_point)

    if err:
        return None, err

    return shifted_plane, Error()


def closure_plane_from_geo(
        plane: Plane,
        src_pt: Point
) -> Callable:
    """
    Closure that embodies the analytical formula for a given, non-vertical plane.
    This closure is used to calculate the z value from given horizontal coordinates (x, y).

    :param plane: the geological plane
    :param src_pt: the 3D point expressing a location point contained by the plane.


    :return: lambda (closure) expressing an analytical formula for deriving z given x and y values.
    """

    x0 = src_pt.x
    y0 = src_pt.y
    z0 = src_pt.z

    # slope of the line parallel to the x axis and contained by the plane
    a = plane.m_coeff_in_x_dir()

    # slope of the line parallel to the y axis and contained by the plane
    b = plane.m_coeff_in_y_dir()

    return lambda x, y: a * (x - x0) + b * (y - y0) + z0


def try_derive_bestfitplane(
        points: List[Point]
) -> Tuple[bool, Union[str, Plane]]:
    """Deprecated. Use 'calculate_best_fit_plane_from_coordinates'
    """

    npaXyz = np.vstack(points)

    xyz_mean = np.mean(npaXyz, axis=0)

    svd_result = svd(npaXyz - xyz_mean)

    if svd_result is None:
        return False, "Unable to calculate result"

    _, _, eigenvectors = svd_result

    lowest_eigenvector = eigenvectors[-1, :]  # Solution is last row

    normal = lowest_eigenvector[: 3] / np.linalg.norm(lowest_eigenvector[: 3])
    normal_vector = Vect3D(normal[0], normal[1], normal[2])
    normal_direct, err = Direct.from_vector(normal_vector)

    if err:
        return False, str(err)

    return True, normal_direct.normal_plane()


def vertical_plane_from_segment(
        segment: Segment
) -> Optional[CPlane3D]:
    """
    Returns the vertical Cartesian plane containing the segment.

    :param segment: the input segment.
    :return: the vertical Cartesian plane containing the segment.
    """

    if are_close(segment.length_2d(), 0.0):
        return None

    # arbitrary point on the same vertical as end point

    start_point = Point.pt2d_to_3d(segment.start_pt, z=0)
    end_point = Point.pt2d_to_3d(segment.end_pt, z=0)

    section_final_pt_up = end_point.shift(
        0.0,
        0.0,
        1000.0)

    return CPlane3D.from_points(
        pt1=start_point,
        pt2=end_point,
        pt3=section_final_pt_up)


def intersect_plane_with_axis(
        plane: CPlane3D,
        axis: Axis,
        src_pt: Point,
        distance_atol: numbers.Real = MIN_DISTANCE_TOLERANCE,
        angular_atol: numbers.Real = MIN_DISORIENTATION_TOLERANCE
) -> Tuple[Union[type(None), Point, ParamLine3D], Error]:
    """
    Intersects a Cartesian plane with an Axis passing through a provided point.
    The result may be a point (general case), a line (axis parallel to plane
    and source point lying on the plane) or nothing (axis parallel to plane and
    source point not lying on the plane).

    :param plane: the Cartesian plane to be intersected.
    :param axis: the axis that we use to intersect the Cartesian plane.
    :param src_pt: the point through which the axis is passing.
    :param distance_atol: the absolute tolerance for distance between point and plane.
    :param angular_atol: the absolute tolerance for disorientation (in degrees) between axis and plane.
    :return: one of point, parametric line or nothing, plus the error status.

    Examples:
    """

    try:

        axis_versor = axis.as_direction().as_versor()

        l, m, n = axis_versor.x, axis_versor.y, axis_versor.z

        axis_param_line = ParamLine3D(src_pt, l, m, n)

        intersection, err = intersect_plane_with_line(
            axis_param_line,
            plane,
            distance_atol=distance_atol,
            angular_atol=angular_atol)

        if err:
            return None, err

        return intersection, Error()

    except Exception as e:

        return None, Error(True, caller_name(), e, traceback.format_exc())


def intersect_plane_with_line(
        parametric_line: ParamLine3D,
        cartes_plane: CPlane3D,
        distance_atol: numbers.Real = MIN_DISTANCE_TOLERANCE,
        angular_atol: numbers.Real = MIN_DISORIENTATION_TOLERANCE,
) -> Tuple[Union[type(None), Point, ParamLine3D], Error]:
    """
    Return intersection point between parametric line and Cartesian plane.

    :param parametric_line: the line to intersect with the plane.
    :param cartes_plane: a Cartesian plane.
    :param distance_atol: the distance tolerance between the plane and the line.
    :param angular_atol: the angular tolerance (in degrees) between plane and line.
    :return: the intersection geometry instance between parametric line and Cartesian plane.

    Examples:
    >>> # From Zwirner, 1983, 'Istituzioni di matematiche', vol. II, p. 183
    >>> pline = ParamLine3D(Point(2, 1, 3), 3, 2, 5)
    >>> cplane = CPlane3D(2, 1, -3, 11)
    >>> inters_pt, err = intersect_plane_with_line(pline, cplane)
    >>> inters_pt
    Point([5. 3. 8.])
    >>> bool(err)
    False
    """

    try:

        # line parameters

        x1, y1, z1 = parametric_line.srcPt.x, parametric_line.srcPt.y, parametric_line.srcPt.z
        l, m, n = parametric_line.l, parametric_line.m, parametric_line.n

        # Cartesian plane parameters
        a, b, c, d = cartes_plane.a(), cartes_plane.b(), cartes_plane.c(), cartes_plane.d()

        plane_normal_vector = Vect3D(a, b, c)
        line_vector = Vect3D(l, m, n)

        if are_close(line_vector.angle_with(plane_normal_vector), 90.0, atol=angular_atol):
            if are_close(cartes_plane.absolute_distance_to_point(parametric_line.srcPt), 0.0, atol=distance_atol):
                return ParamLine3D(parametric_line.srcPt.clone(), l, m, n), Error()
            else:
                return None, Error()

        k = (a * x1 + b * y1 + c * z1 + d) / (a * l + b * m + c * n)

        return Point(
            x1 - l * k,
            y1 - m * k,
            z1 - n * k
        ), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc())


def versor_from_plane_attitude_inters(
    cartes_plane: CPlane3D,
    attitude: Plane,
    point: Point
) -> Tuple[Union[type(None), Vect3D, CPlane3D], Error]:
    """
    Determine the intersection of an attitude with a plane,
    represented by the intersection vector (but possibly a Cartesian plane, when parallel
    and coincident).

    :param cartes_plane: the Cartesian plane to intersect with the planar attitude.
    :param attitude: the planar attitude to intersect with the Cartesian plane.
    :param point: the point contained in the attitude plane.
    :return: the result, either None or a geometry, and the error status.
    """

    try:

        if point.is_2d():
            print(f"Warning: input point is 2D. Will be converted to 3D with z = 0")
            point_3d = Point.pt2d_to_3d(point)
        else:
            point_3d = point

        attitude_plane = CPlane3D.from_geol_plane(attitude, point_3d)
        intersection, err = cartes_plane.intersects_other(
            attitude_plane)

        if err:
            return None, err

        if intersection is None:
            return None, Error()

        if isinstance(intersection, CPlane3D):
            return CPlane3D, Error()
        elif not intersection.is_valid():
            return None, Error(
                True,
                caller_name(),
                Exception(f"DEBUG: <intersection> is not valid"),
                traceback.format_exc())
        else:
            return intersection, Error()

    except Exception as e:

        return None, Error(True, caller_name(), e, traceback.format_exc())


def along_attitude_nearest_projection(
    cartes_plane: CPlane3D,
    attitude: Plane,
    point: Point,
    intersection: Vect3D
) -> Tuple[Union[type(None), Point], Error]:
    """
    Determine the along-attitude nearest-point projection on the Cartesian plane.

    :param cartes_plane: the Cartesian plane to intersect with the planar attitude.
    :param attitude: the planar attitude along which to intersect with the Cartesian plane.
    :param point: the point contained in the attitude plane.
    :param intersection: the intersection vector on the Cartesian plane.
    :return: the result, either None or a geometry, and the error status.
    """

    try:

        attitude_plane = CPlane3D.from_geol_plane(attitude, point)

        dummy_inters_pt, err = cartes_plane.intersects_other_as_pt(attitude_plane)

        if err:
            return None, err

        if dummy_inters_pt is None:
            return None, Error(
                True,
                caller_name(),
                Exception(f"DEBUG: <dummy_inters_pt> is None"),
                traceback.format_exc())

        dummy_structural_vect = Segment(dummy_inters_pt, point).as_vector3d()

        dummy_distance = dummy_structural_vect.dot_product(intersection)
        offset_vector = intersection.scale(dummy_distance)

        if offset_vector is None:
            return None, Error(
                True,
                caller_name(),
                Exception(f"DEBUG: <offset_vector> is None"),
                traceback.format_exc())

        projected_pt = Point(
            dummy_inters_pt.x + offset_vector.x,
            dummy_inters_pt.y + offset_vector.y,
            dummy_inters_pt.z + offset_vector.z
        )

        return projected_pt, Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc())


def intersect_plane_with_attitude(
    cartes_plane: CPlane3D,
    attitude: Plane,
    point: Point
) -> Tuple[Union[type(None), Tuple[Union[Vect3D, CPlane3D], Point]], Error]:
    """
    Determine the intersection of an attitude with a plane,
    represented by the intersection vector (but possibly a Cartesian plane, when parallel
    and coincident) and the nearest point.

    :param cartes_plane: the Cartesian plane to intersect with the planar attitude.
    :param attitude: the planar attitude to intersect with the Cartesian plane.
    :param point: the point contained in the attitude plane.
    :return: the result, either None or a tuple of Vect3D and Point, and the error status.
    """

    try:

        # calculate intersection geometry between attitude and plane

        intersection, err = versor_from_plane_attitude_inters(
            cartes_plane,
            attitude,
            point
        )

        if err:
            return None, err

        if isinstance(intersection, CPlane3D):
            return (intersection, point), Error()

        # get nearest along-attitude plane-intersecting point

        projected_pt, err = along_attitude_nearest_projection(
            cartes_plane,
            attitude,
            point,
            intersection
        )

        if err:
            return None, err

        return (intersection, projected_pt), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc())


def project_point_perpendicular_to_plane(
        plane: CPlane3D,
        point: Point,
        distance_atol: numbers.Real = MIN_DISTANCE_TOLERANCE
) -> Tuple[Union[type(None), Point], Error]:
    """
    Calculates the projection of a point on a plane,
    perpendicularly to the plane.

    :param plane: the Cartesian plane to intersect the point with.
    :param point: the point location, to be intersected with the plane.
    :param distance_atol: the minimum distance of the point from the plane, to consider the former not lying in the latter.
    :return: the intersection result and the error status.
    """

    if plane.absolute_distance_to_point(point) < distance_atol:
        return point, Error()

    normal_versor, error = plane.normal_versor()
    if error:
        return None, error

    l, m, n = normal_versor.to_xyz()

    axis_param_line = ParamLine3D(point, l, m, n)

    intersection, err = intersect_plane_with_line(
        axis_param_line,
        plane,
        distance_atol=distance_atol)

    if err:
        return None, err

    if isinstance(intersection, ParamLine3D):
        return None, Error(
            True,
            caller_name(),
            Exception("Intersection is not supposed to be a ParamLine3D instance"),
            traceback.format_exc())

    return intersection, Error()


'''
def project_point_to_plane_with_axis(
        plane: CPlane3D,
        point: Point,
        axis: Axis,
        distance_atol: numbers.Real = MIN_DISTANCE_TOLERANCE
):
    """
    Calculates the projection of a point on a plane,
    perpendicularly to the plane.

    :param plane: the Cartesian plane to intersect the point with.
    :param point: the point location, to be intersected with the plane.
    :param axis: the axis alogn which to project the point.
    :param distance_atol: the minimum distance of the point from the plane, to consider the former not lying in the latter.
    :return: the intersection result and the error status.
    """

    if plane.absolute_distance_to_point(point) < distance_atol:
        return point, Error()
'''


if __name__ == "__main__":
    import doctest

    doctest.testmod()
