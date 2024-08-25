"""
These rotation operators are intended to operate with orientations,
without any locational information (differently from other location-aware operators)
"""

import functools
import random

from geogst.core.mathematics.quaternions import *
from geogst.core.geology.faults import *


def rotation_matrix_by_versor(
        rotation_versor: Vect3D,
        rot_angle_degr: numbers.Real
) -> np.ndarray:
    """
    Create rotation matrix from rotation versor and rot_angle (as degrees)
    """

    phi = radians(rot_angle_degr)

    l = rotation_versor.x
    m = rotation_versor.y
    n = rotation_versor.z

    cos_phi = cos(phi)
    sin_phi = sin(phi)

    a11 = cos_phi + ((l * l) * (1 - cos_phi))
    a12 = ((l * m) * (1 - cos_phi)) - (n * sin_phi)
    a13 = ((l * n) * (1 - cos_phi)) + (m * sin_phi)

    a21 = ((l * m) * (1 - cos_phi)) + (n * sin_phi)
    a22 = cos_phi + ((m * m) * (1 - cos_phi))
    a23 = ((m * n) * (1 - cos_phi)) - (l * sin_phi)

    a31 = ((l * n) * (1 - cos_phi)) - (m * sin_phi)
    a32 = ((m * n) * (1 - cos_phi)) + (l * sin_phi)
    a33 = cos_phi + ((n * n) * (1 - cos_phi))

    return np.array([(a11, a12, a13),
                     (a21, a22, a23),
                     (a31, a32, a33)])


class RotationAxis(object):
    """
    Rotation axis, expressed by an orientation and a rotation rot_angle.
    """

    def __init__(self,
                 trend: numbers.Real,
                 plunge: numbers.Real,
                 rot_ang: numbers.Real
    ):
        """
        Constructor.

        :param trend: Float/Integer
        :param plunge: Float/Integer
        :param rot_ang: Float/Integer

        Examples:
        >>> RotationAxis(0, 90, 120)
        RotationAxis(0.0000, 90.0000, 120.0000)
        """

        self.dr = Direct(trend, plunge)
        self.a = float(rot_ang)

    @classmethod
    def from_quaternion(cls,
                        quat: Quaternion
                        ):
        """
        Calculates the Rotation Axis expressed by a quaternion.
        The resulting rotation as_vector2d is set to point downward.
        Examples are taken from Kuipers, 2002, chp. 5.

        :return: RotationAxis instance.

        Examples:
          >>> RotationAxis.from_quaternion(Quaternion(0.5, 0.5, 0.5, 0.5))
          RotationAxis(45.0000, -35.2644, 120.0000)
          >>> RotationAxis.from_quaternion(Quaternion(sqrt(2)/2, 0.0, 0.0, sqrt(2)/2))
          RotationAxis(0.0000, -90.0000, 90.0000)
          >>> RotationAxis.from_quaternion(Quaternion(sqrt(2)/2, sqrt(2)/2, 0.0, 0.0))
          RotationAxis(90.0000, -0.0000, 90.0000)
        """

        if abs(quat) < QUAT_MAGN_THRESH:

            rot_ang = 0.0
            rot_direct, err = Direct(0.0, 0.0)
            if err:
                raise Exception(err)

        elif are_close(quat.scalar, 1):

            rot_ang = 0.0
            rot_direct, err = Direct(0.0, 0.0)
            if err:
                raise Exception(err)

        else:

            unit_quat = quat.normalize()
            rot_ang = unit_quat.rot_angle()
            rot_direct, err = Direct.from_vector(unit_quat.vector())
            if err:
                raise Exception(err)

        return RotationAxis(*rot_direct.d, rot_ang)

    @classmethod
    def from_direction(cls,
                       direct: Direct,
                       angle: numbers.Real
                       ):
        """
        Class constructor from a Direct instance and an rot_angle value.

        :param direct: a Direct instance
        :param angle: numbers.Real.
        :return: RotationAxis instance

        Example:
          >>> RotationAxis.from_direction(Direct(320, 12), 30)
          RotationAxis(320.0000, 12.0000, 30.0000)
          >>> RotationAxis.from_direction(Direct(315.0, -0.0), 10)
          RotationAxis(315.0000, -0.0000, 10.0000)
        """

        return RotationAxis(*direct.d, angle)

    @classmethod
    def from_vector(cls,
                    vector: Vect3D,
                    rot_angle: numbers.Real
                    ):
        """
        Class constructor from a Vect instance and an rot_angle value.

        :param vector: a Vect instance
        :param rot_angle: float value
        :return: RotationAxis instance

        Example:
          >>> RotationAxis.from_vector(Vect3D(0, 1, 0), 30)
          RotationAxis(0.0000, -0.0000, 30.0000)
          >>> RotationAxis.from_vector(Vect3D(1, 0, 0), 30)
          RotationAxis(90.0000, -0.0000, 30.0000)
          >>> RotationAxis.from_vector(Vect3D(0, 0, -1), 30)
          RotationAxis(0.0000, 90.0000, 30.0000)
        """

        direct, err = Direct.from_vector(vector)
        if err:
            raise Exception(err)

        return RotationAxis.from_direction(direct, rot_angle)

    def __repr__(self):

        return "RotationAxis({:.4f}, {:.4f}, {:.4f})".format(*self.dr.d, self.a)

    @property
    def rot_angle(self) -> float:
        """
        Returns the rotation rot_angle of the rotation axis.

        :return: rotation rot_angle (Float)

        Example:
          >>> RotationAxis(10, 15, 230).rot_angle
          230.0
        """

        return self.a

    @property
    def rot_direct(self) -> Direct:
        """
        Returns the rotation axis, expressed as a Direct.

        :return: Direct instance

        Example:
          >>> RotationAxis(320, 40, 15).rot_direct
          Direct(az: 320.00°, pl: 40.00°)
          >>> RotationAxis(135, 0, -10).rot_direct
          Direct(az: 135.00°, pl: 0.00°)
          >>> RotationAxis(45, 10, 10).rot_direct
          Direct(az: 45.00°, pl: 10.00°)
        """

        return self.dr

    @property
    def versor(self) -> Vect3D:
        """
        Return the versor equivalent to the Rotation geological as_vector2d.

        :return: Vect
        """

        return self.dr.as_versor()

    def specular(self):
        """
        Derives the rotation axis with opposite as_vector2d direction
        and rotation rot_angle that is the complement to 360°.
        The resultant rotation is equivalent to the original one.

        :return: RotationAxis instance.

        Example
          >>> RotationAxis(90, 45, 320).specular()
          RotationAxis(270.0000, -45.0000, 40.0000)
          >>> RotationAxis(135, 0, -10).specular()
          RotationAxis(315.0000, -0.0000, 10.0000)
          >>> RotationAxis(45, 10, 10).specular()
          RotationAxis(225.0000, -10.0000, 350.0000)
        """

        gvect_opp = self.rot_direct.opposite()
        opposite_angle = (360.0 - self.rot_angle) % 360.0

        return RotationAxis.from_direction(gvect_opp, opposite_angle)

    def compl180(self):
        """
        Creates a new rotation axis that is the complement to 180 of the original one.

        :return: RotationAxis instance.

        Example:
          >>> RotationAxis(90, 45, 120).compl180()
          RotationAxis(90.0000, 45.0000, 300.0000)
          >>> RotationAxis(117, 34, 18).compl180()
          RotationAxis(117.0000, 34.0000, 198.0000)
          >>> RotationAxis(117, 34, -18).compl180()
          RotationAxis(117.0000, 34.0000, 162.0000)
        """

        rot_ang = - (180.0 - self.rot_angle) % 360.0
        return RotationAxis.from_direction(self.dr, rot_ang)

    def strictly_equival(self,
                         another,
                         ang_tol_degr: numbers.Real=VECTOR_ANGLE_THRESHOLD
                         ) -> bool:
        """
        Checks if two RotationAxis are almost equal, based on a strict checking
        of the Direct component and of the rotation rot_angle.

        :param another: another RotationAxis instance, to be compared with
        :type another: core.orientations.rotations.RotationAxis
        :parameter ang_tol_degr: the tolerance as the rot_angle (in degrees)
        :type ang_tol_degr: numbers.Real.
        :return: the equivalence (true/false) between the two compared RotationAxis
        :rtype: bool

        Examples:
          >>> ra_1 = RotationAxis(180, 10, 10)
          >>> ra_2 = RotationAxis(180, 10, 10.5)
          >>> ra_1.strictly_equival(ra_2)
          True
          >>> ra_3 = RotationAxis(180.2, 10, 10.4)
          >>> ra_1.strictly_equival(ra_3)
          True
          >>> ra_4 = RotationAxis(184.9, 10, 10.4)
          >>> ra_1.strictly_equival(ra_4)
          False
        """

        if not self.dr.is_sub_parallel(another.dr, ang_tol_degr):
            return False

        if not are_close(self.a, another.a, atol=1.0):
            return False

        return True

    def to_rot_quater(self) -> Quaternion:
        """
        Converts the rotation axis to the equivalent rotation quaternion.

        :return: the rotation quaternion.
        :rtype: Quaternion
        """

        rotation_angle_rad = radians(self.a)
        rotation_vector = self.dr.as_versor()

        w = cos(rotation_angle_rad / 2.0)
        x, y, z = rotation_vector.scale(sin(rotation_angle_rad / 2.0)).to_xyz()

        return Quaternion(w, x, y, z).normalize()

    def to_rot_matrix(self):
        """
        Derives the rotation matrix from the RotationAxis instance.

        :return: 3x3 numpy array
        """

        rotation_versor = self.versor
        rot_angle = self.a

        return rotation_matrix_by_versor(
            rotation_versor,
            rot_angle
        )


    def to_min_rot_axis(self):
        """
        Calculates the minimum rotation axis from the given quaternion.

        :return: RotationAxis instance.
        """

        return self if abs(self.rot_angle) <= 180.0 else self.specular()

    @classmethod
    def randomNaive(cls):
        """
        Naive method for creating a random RotationAxis instance.
        :return: random rotation axis (not uniformly distributed in the space)
        :rtype: core.orientations.rotations.RotationAxis
        """

        random_trend = random.uniform(0, 360)
        random_dip = random.uniform(-90, 90)
        random_rotation = random.uniform(0, 360)

        return cls(
            trend=random_trend,
            plunge=random_dip,
            rot_ang=random_rotation
        )


def sort_rotations(
        rotation_axes: List[RotationAxis]
) -> List[RotationAxis]:
    """
    Sorts a list or rotation axes, based on the rotation rot_angle (absolute value),
    in an increasing order.

    :param rotation_axes: o list of RotationAxis objects.
    :return: the sorted list of RotationAxis

    Example:
      >>> rots = [RotationAxis(110, 14, -23), RotationAxis(42, 13, 17), RotationAxis(149, 87, 13)]
      >>> sort_rotations(rots)
      [RotationAxis(149.0000, 87.0000, 13.0000), RotationAxis(42.0000, 13.0000, 17.0000), RotationAxis(110.0000, 14.0000, -23.0000)]
    """

    return sorted(rotation_axes, key=lambda rot_ax: abs(rot_ax.rot_angle))


def rotation_matrix_from_trend_and_plunge(
        rot_axis_trend,
        rot_axis_plunge,
        rot_angle
):

    rotation_versor = Axis(rot_axis_trend, rot_axis_plunge).as_direction().as_versor()

    return rotation_matrix_by_versor(
        rotation_versor,
        rot_angle
    )


def rotate_vector_via_axis(
    v: Vect3D,
    rot_axis: RotationAxis
) -> Vect3D:
    """
    DEPRECATED: use 'rotate'.
    Rotates a vector.

    Implementation as in:
    https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
    Faster formula:
    t = 2 q x v
    v' = v + q0 t + q x t
    cited as:
    Janota, A; Šimák, V; Nemec, D; Hrbček, J (2015).
    "Improving the Precision and Speed of Euler Angles Computation from Low-Cost Rotation Sensor Data".
    Sensors. 15 (3): 7016–7039. doi:10.3390/s150307016. PMC 4435132. PMID 25806874.

    :param v: the vector to rotate
    :param rot_axis: the rotation axis
    :return: the rotated vector

    Examples:
      >>> v = Vect3D(1,0,1)
      >>> rotation = RotationAxis(0, -90, 90)
      >>> rotate_vector_via_axis(v, rotation)
      Vect3D(0.0000, 1.0000, 1.0000)
      >>> rotation = RotationAxis(0, 90, 90)
      >>> rotate_vector_via_axis(v, rotation)
      Vect3D(0.0000, -1.0000, 1.0000)
      >>> rotation = RotationAxis(0, -90, 180)
      >>> rotate_vector_via_axis(v, rotation)
      Vect3D(-1.0000, 0.0000, 1.0000)
      >>> rotation = RotationAxis(0, -90, 270)
      >>> rotate_vector_via_axis(v, rotation)
      Vect3D(-0.0000, -1.0000, 1.0000)
      >>> rotation = RotationAxis(90, 0, 90)
      >>> rotate_vector_via_axis(v, rotation)
      Vect3D(1.0000, -1.0000, 0.0000)
      >>> rotation = RotationAxis(90, 0, 180)
      >>> rotate_vector_via_axis(v, rotation)
      Vect3D(1.0000, 0.0000, -1.0000)
      >>> rotation = RotationAxis(90, 0, 270)
      >>> rotate_vector_via_axis(v, rotation)
      Vect3D(1.0000, 1.0000, -0.0000)
      >>> rotation = RotationAxis(90, 0, 360)
      >>> rotate_vector_via_axis(v, rotation)
      Vect3D(1.0000, 0.0000, 1.0000)
      >>> rotation = RotationAxis(0, -90, 90)
      >>> v = Vect3D(0,0,3)
      >>> rotate_vector_via_axis(v, rotation)
      Vect3D(0.0000, 0.0000, 3.0000)
      >>> rotation = RotationAxis(90, -45, 180)
      >>> rotate_vector_via_axis(v, rotation)
      Vect3D(3.0000, -0.0000, -0.0000)
      >>> v = Vect3D(0,0,3)
      >>> rotate_vector_via_axis(v, rotation)
      Vect3D(3.0000, -0.0000, -0.0000)
    """

    rot_quat = rot_axis.to_rot_quater()
    q = rot_quat.vector()

    t = q.scale(2).cross_product(v)
    rot_v = v + t.scale(rot_quat.scalar) + q.cross_product(t)

    return rot_v


def rotate_vector_via_quaternion(
        quat: Quaternion,
        vect: Vect3D
) -> Vect3D:
    """
    Calculates a rotated solution of a Vect3D instance given a normalized quaternion.
    Original formula in:

    Kagan, Y.Y., 1991. 3-D rotation of double-couple earthquake sources.
    Geophys. J. Int, 106, 709-716.

    Eq. 6: R(qv) = q qv q(-1)

    :param quat: a Quaternion instance
    :param vect: a Vect instance
    :return: a rotated Vect instance

    Example:
      >>> q = Quaternion.i()  # rotation of 180° around the x axis
      >>> rotate_vector_via_quaternion(q, Vect3D(0, 1, 0))
      Vect3D(0.0000, -1.0000, 0.0000)
      >>> rotate_vector_via_quaternion(q, Vect3D(0, 1, 1))
      Vect3D(0.0000, -1.0000, -1.0000)
      >>> q = Quaternion.k()  # rotation of 180° around the z axis
      >>> rotate_vector_via_quaternion(q, Vect3D(0, 1, 1))
      Vect3D(0.0000, -1.0000, 1.0000)
      >>> q = Quaternion.j()  # rotation of 180° around the y axis
      >>> rotate_vector_via_quaternion(q, Vect3D(1, 0, 1))
      Vect3D(-1.0000, 0.0000, -1.0000)
    """

    q = quat.normalize()
    qv = Quaternion.from_vector(vect)

    rotated_v = q * (qv * q.inverse)

    return rotated_v.vector()


@functools.singledispatch
def rotate(
    struct: Any,
    rotation_direction: Direct,
    rotation_angle: numbers.Real,
) -> Tuple[Union[type(None), Any], Error]:

    return None, Error(True, caller_name(), NotImplementedError, traceback.format_exc())


@rotate.register(Vect3D)
def _(
    struct: Vect3D,
    rotation_direction: Direct,
    rotation_angle: numbers.Real
) -> Tuple[Union[type(None), Vect3D], Error]:
    """
    Rotate a 3D vector around a rotation axis.

    Implementation as in:
    https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
    Faster formula:
    t = 2 q x v
    v' = v + q0 t + q x t
    cited as:
    Janota, A; Šimák, V; Nemec, D; Hrbček, J (2015).
    "Improving the Precision and Speed of Euler Angles Computation from Low-Cost Rotation Sensor Data".
    Sensors. 15 (3): 7016–7039. doi:10.3390/s150307016. PMC 4435132. PMID 25806874.

    :param struct: the 3D vector to rotate.
    :param rotation_direction: the rotation direction.
    :param rotation_angle: the angle of the rotation.
    :return: a rotated 3D vector.

    Examples:
      >>> v = Vect3D(1,0,1)
      >>> rotation_dir, rotation_agle = Direct(0, -90), 90
      >>> rv, err = rotate(v, rotation_dir, rotation_agle)
      >>> rv
      Vect3D(0.0000, 1.0000, 1.0000)
      >>> rotation_dir, rotation_agle = Direct(0, 90), 90
      >>> rotate(v, rotation_dir, rotation_agle)
      Vect3D(0.0000, -1.0000, 1.0000)
      >>> rotation_dir, rotation_agle = Direct(0, -90), 180
      >>> rotate(v, rotation_dir, rotation_agle)
      Vect3D(-1.0000, 0.0000, 1.0000)
      >>> rotation_dir, rotation_agle = Direct(0, -90), 270
      >>> rotate(v, rotation_dir, rotation_agle)
      Vect3D(-0.0000, -1.0000, 1.0000)
      >>> rotation_dir, rotation_agle = Direct(90, 0), 90
      >>> rotate(v, rotation_dir, rotation_agle)
      Vect3D(1.0000, -1.0000, 0.0000)
      >>> rotation_dir, rotation_agle = Direct(90, 0), 180
      >>> rotate(v, rotation_dir, rotation_agle)
      Vect3D(1.0000, 0.0000, -1.0000)
      >>> rotation_dir, rotation_agle = Direct(90, 0), 270
      >>> rotate(v, rotation_dir, rotation_agle)
      Vect3D(1.0000, 1.0000, -0.0000)
      >>> rotation_dir, rotation_agle = Direct(90, 0), 360
      >>> rotate(v, rotation_dir, rotation_agle)
      Vect3D(1.0000, 0.0000, 1.0000)
      >>> rotation_dir, rotation_agle = Direct(0, -90), 90
      >>> v = Vect3D(0,0,3)
      >>> rotate(v, rotation_dir, rotation_agle)
      Vect3D(0.0000, 0.0000, 3.0000)
      >>> rotation_dir, rotation_agle = Direct(90, -45), 180
      >>> rotate(v, rotation_dir, rotation_agle)
      Vect3D(3.0000, -0.0000, -0.0000)
      >>> v = Vect3D(0,0,3)
      >>> rotate(v, rotation_dir, rotation_agle)
      Vect3D(3.0000, -0.0000, -0.0000)
    """

    try:

        rot_axis = RotationAxis(
            *rotation_direction.d,
            rotation_angle
        )

        rot_quat = rot_axis.to_rot_quater()
        q = rot_quat.vector()

        t = q.scale(2).cross_product(struct)
        rot_v = struct + t.scale(rot_quat.scalar) + q.cross_product(t)

        return rot_v, Error()

    except Exception as e:

        return None, Error(True, caller_name(), e, traceback.format_exc())


@rotate.register(Direct)
def _(
    struct: Direct,
    rotation_direction: Direct,
    rotation_angle: numbers.Real
) -> Tuple[Union[type(None), Direct], Error]:
    """
    Rotate a direction around a rotation axis.

    :param struct: the direction to rotate.
    :param rotation_direction: the rotation direction.
    :param rotation_angle: the angle of the rotation.
    :return: a rotated direction.
    """

    try:

        vect = struct.as_versor()
        rotated_vect, err = rotate(
            vect,
            rotation_direction,
            rotation_angle
        )

        if err:
            return None, err

        return Direct.from_vector(rotated_vect)

    except Exception as e:

        return None, Error(True, caller_name(), e, traceback.format_exc())


@rotate.register(Axis)
def _(
        struct: Axis,
        rotation_direction: Direct,
        rotation_angle: numbers.Real
) -> Tuple[Union[type(None), Direct], Error]:
    """
    Rotate an axis around a rotation axis.

    :param struct: the axis to rotate.
    :param rotation_direction: the rotation direction.
    :param rotation_angle: the angle of the rotation.
    :return: the rotated axis.
    """

    try:

        vect = struct.as_versor()
        rotated_vect, err = rotate(
            vect,
            rotation_direction,
            rotation_angle
        )

        if err:
            return None, err

        return Axis.from_xyz(*rotated_vect.to_xyz())

    except Exception as e:

        return None, Error(True, caller_name(), e, traceback.format_exc())


@rotate.register(Plane)
def _(
        struct: Plane,
        rotation_direction: Direct,
        rotation_angle: numbers.Real
) -> Tuple[Union[type(None), Plane], Error]:
    """
    Rotate a plane around a rotation axis.

    :param struct: the plane to rotate.
    :param rotation_direction: the rotation direction.
    :param rotation_angle: the angle of the rotation.
    :return: the rotated plane.
    """

    try:

        vect = struct.normal_direction().as_versor()

        rotated_vect, err = rotate(
            vect,
            rotation_direction,
            rotation_angle
        )

        if err:
            return None, err

        return Plane.from_normal(rotated_vect), Error()

    except Exception as e:

        return None, Error(True, caller_name(), e, traceback.format_exc())


@rotate.register(Slickenline)
def _(
    struct: Slickenline,
    rotation_direction: Direct,
    rotation_angle: numbers.Real
) -> Tuple[Union[type(None), Slickenline], Error]:
    """
    Rotate a slickenline around a rotation axis.

    :param struct: the slickenline to rotate.
    :param rotation_direction: the rotation direction.
    :param rotation_angle: the angle of the rotation.
    :return: a rotated slickenline.
    """

    try:

        vect = struct.geom.as_versor()
        vect, err = rotate(
            vect,
            rotation_direction,
            rotation_angle
        )

        if err:
            return None, err

        direct, err = Direct.from_vector(vect)
        if err:
            return None, err

        trend, plunge = direct.d

        return Slickenline(
            trend=trend,
            plunge=plunge,
            rake=None,
            known=struct.known,
            time=struct.time
        ), Error()

    except Exception as e:

        return None, Error(True, caller_name(), e, traceback.format_exc())


@rotate.register(Fault)
def _(
    struct: Fault,
    rotation_direction: Direct,
    rotation_angle: numbers.Real,
) -> Tuple[Union[type(None), Fault], Error]:
    """
    Rotate a fault around a rotation axis.
    Rotation angle follow the right-hand rule.

    :param struct: the fault to rotate.
    :param rotation_direction: the rotation axis (oriented).
    :param rotation_angle: the angle of the rotation.
    :return: a rotated fault.
    """

    try:

        fault_plane = struct.plane

        rotated_fault_plane, err = rotate(
            fault_plane,
            rotation_direction,
            rotation_angle
        )

        if err:
            return None, err

        rotated_slickenlines = []
        for slick in struct.slickenlines():

            rotated_slickenline, err = rotate(
                slick,
                rotation_direction,
                rotation_angle
            )
            if err:
                return None, err

            rotated_slickenlines.append(rotated_slickenline)

        return Fault(
            rotated_fault_plane.dipazim,
            rotated_fault_plane.dipang,
            slickenlines=rotated_slickenlines
        ), Error()

    except Exception as e:

        return None, Error(True, caller_name(), e, traceback.format_exc())


if __name__ == "__main__":

    import doctest
    doctest.testmod()


