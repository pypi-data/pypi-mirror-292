
from math import sin, cos, isfinite, pi, sqrt, tan, radians

from geogst.core.mathematics.vectors3d import *
from geogst.core.mathematics.utils import *
from geogst.core.orientations.defaults import *
from geogst.core.orientations.utils import *


class Azim(object):
    """
    Azim class
    """

    def __init__(self,
        val: numbers.Real,
        unit: str = 'd'
    ):
        """
        Creates an azimuth instance.

        :param val: azimuth value
        :param unit: azimuth measurement unit, 'd' (default, stands for decimal degrees) or 'r' (stands for radians)

        Examples:
          >>> Azim(10)
          Azim(10.00°)
          >>> Azim(370)
          Azim(10.00°)
          >>> Azim(pi/2, unit='r')
          Azim(90.00°)
        """

        # unit check
        if unit not in ("d", "r"):
            raise Exception(f"Unit input must be 'd' or 'r' but {unit} got")

        if not (isinstance(val, numbers.Real)):
            raise Exception(f"Input azimuth value must be int/float but type {type(val)} got")
        elif not isfinite(val):
            raise Exception(f"Input azimuth value must be finite but {val} got")

        if unit == 'd':
            val = radians(val)

        self.a = val % (2*pi)

    @property
    def d(self) -> numbers.Real:
        """
        Returns the azimuth in decimal degrees.

        :return: azimuth in decimal degrees

        Example:
          >>> Azim(10).d
          10.0
          >>> Azim(pi/2, unit='r').d
          90.0
        """

        return degrees(self.a)

    @property
    def r(self) -> numbers.Real:
        """
        Returns the azimuth in radians.

        :return: azimuth in radians.

        Example:
          >>> Azim(180).r
          3.141592653589793
        """

        return self.a

    @classmethod
    def fromXY(cls,
        x: numbers.Real,
        y: numbers.Real
    ) -> 'Azim':
        """
        Calculates azimuth given cartesian components.

        :param cls: class
        :param x: x component
        :param y: y component
        :return: Azim instance

        Examples:
          >>> Azim.fromXY(1, 1)
          Azim(45.00°)
          >>> Azim.fromXY(1, -1)
          Azim(135.00°)
          >>> Azim.fromXY(-1, -1)
          Azim(225.00°)
          >>> Azim.fromXY(-1, 1)
          Azim(315.00°)
          >>> Azim.fromXY(0, 0)
          Azim(0.00°)
          >>> Azim.fromXY(0, np.nan)
          Traceback (most recent call last):
          ...
          Exception: Input x and y values must be finite
        """

        # input vals checks
        vals = [x, y]
        if not all(map(lambda val: isinstance(val, numbers.Real), vals)):
            raise Exception("Input x and y values must be integer or float")
        elif not all(map(isfinite, vals)):
            raise Exception("Input x and y values must be finite")

        angle = atan2(x, y)
        return cls(angle, unit='r')

    def __repr__(self) -> str:

        return "Azim({:.2f}°)".format(self.d)

    def toXY(self
    ) -> Tuple[numbers.Real, numbers.Real]:
        """
        Converts an azimuth to x-y components.

        :return: a tuple storing x and y values:
        :type: tuple of two floats

        Examples:
          >>> apprFTuple(Azim(0).toXY())
          (0.0, 1.0)
          >>> apprFTuple(Azim(90).toXY())
          (1.0, 0.0)
          >>> apprFTuple(Azim(180).toXY())
          (0.0, -1.0)
          >>> apprFTuple(Azim(270).toXY())
          (-1.0, 0.0)
          >>> apprFTuple(Azim(360).toXY())
          (0.0, 1.0)
        """

        return sin(self.a), cos(self.a)


class Plunge(object):
    """
    Class representing a plunge
    """

    def __init__(self,
        val: numbers.Real,
        unit: str='d'
    ):
        """
        Creates a Plunge instance.

        :param val: plunge value
        :param unit: rot_angle measurement unit, decimal degrees ('d') or radians ('r')

        Examples:
          >>> Plunge(10)
          Plunge(10.00°)
          >>> Plunge(np.nan)
          Traceback (most recent call last):
          ...
          Exception: Input plunge value must be finite
          >>> Plunge(-100)
          Traceback (most recent call last):
          ...
          Exception: Input value in degrees must be between -90° and 90°
         """

        # unit check
        if unit not in ('d', 'r'):
            raise Exception("Unit input must be 'd' (for degrees) or 'r' (for radians)")

        # val check
        if not (isinstance(val, numbers.Real)):
            raise Exception("Input plunge value must be int/float")
        elif not isfinite(val):
            raise Exception("Input plunge value must be finite")
        if unit == 'd' and not (-90.0 <= val <= 90.0):
            raise Exception("Input value in degrees must be between -90° and 90°")
        elif unit == 'r' and not (-pi/2 <= val <= pi/2):
            raise Exception("Input value in radians must be between -pi/2 and pi/2")

        if unit == 'd':
            val = radians(val)

        self.p = val

    @property
    def d(self):
        """
        Returns the rot_angle in decimal degrees.

        :return: rot_angle in decimal degrees

        Example:
          >>> Plunge(10).d
          10.0
          >>> Plunge(-pi/2, unit='r').d
          -90.0
        """

        return degrees(self.p)

    @property
    def r(self):
        """
        Returns the rot_angle in radians.

        :return: rot_angle in radians

        Example:
          >>> Plunge(90).r
          1.5707963267948966
          >>> Plunge(45).r
          0.7853981633974483
        """

        return self.p

    @classmethod
    def fromHZ(cls,
               h: numbers.Real,
               z: numbers.Real
        ) -> 'Plunge':
        """
        Calculates plunge from h and z components.

        :param cls: class
        :param h: horizontal component (always positive)
        :param z: vertical component (positive upward)
        :return: Plunge instance

        Examples:
          >>> Plunge.fromHZ(1, 1)
          Plunge(-45.00°)
          >>> Plunge.fromHZ(1, -1)
          Plunge(45.00°)
          >>> Plunge.fromHZ(0, 1)
          Plunge(-90.00°)
          >>> Plunge.fromHZ(0, -1)
          Plunge(90.00°)
          >>> Plunge.fromHZ(-1, 0)
          Traceback (most recent call last):
          ...
          Exception: Horizontal component cannot be negative
          >>> Plunge.fromHZ(0, 0)
          Traceback (most recent call last):
          ...
          Exception: horizontal and vertical components cannot be both zero
        """

        # input vals check

        vals = [h, z]
        if not all(map(lambda val: isinstance(val, numbers.Real), vals)):
            raise Exception("Input h and z values must be integer or float")
        elif not all(map(isfinite, vals)):
            raise Exception("Input h and z values must be finite")

        if h == 0.0 and z == 0.0:
            raise Exception("horizontal and vertical components cannot be both zero")
        elif h < 0.0:
            raise Exception("Horizontal component cannot be negative")

        angle = atan2(-z, h)

        return cls(angle, unit='r')

    def __repr__(self) -> str:

        return "Plunge({:.2f}°)".format(self.d)

    def toHZ(self):

        """
        Converts an azimuth to h-z components.

        :return: a tuple storing h (horizontal) and z values:
        :type: tuple of two floats

        Examples:
          >>> apprFTuple(Plunge(0).toHZ())
          (1.0, 0.0)
          >>> apprFTuple(Plunge(90).toHZ())
          (0.0, -1.0)
          >>> apprFTuple(Plunge(-90).toHZ())
          (0.0, 1.0)
          >>> apprFTuple(Plunge(-45).toHZ(), ndec=6)
          (0.707107, 0.707107)
          >>> apprFTuple(Plunge(45).toHZ(), ndec=6)
          (0.707107, -0.707107)
        """

        return cos(self.p), -sin(self.p)

    @property
    def is_upward(self) -> bool:
        """
        Check whether the instance is pointing upward or horizontal.

        Examples:
          >>> Plunge(10).is_upward
          False
          >>> Plunge(0.0).is_upward
          False
          >>> Plunge(-45).is_upward
          True
        """

        return self.r < 0.0

    @property
    def is_downward(self) -> bool:
        """
        Check whether the instance is pointing downward or horizontal.

        Examples:
          >>> Plunge(15).is_downward
          True
          >>> Plunge(0.0).is_downward
          False
          >>> Plunge(-45).is_downward
          False
        """

        return self.r > 0.0


class Direct:
    """
    Class describing a direction, expressed as a polar direction in degrees.
    """

    def __init__(self,
                 az: numbers.Real,
                 pl: numbers.Real
                 ):
        """
        Creates a polar direction instance.

        :param az: the azimuth value in decimal degrees
        :param pl: the plunge value in decimal degrees
        """

        self._az = Azim(az)
        self._pl = Plunge(pl)

    @property
    def d(self) -> Tuple[numbers.Real, numbers.Real]:
        """
        Returns azimuth and plunge in decimal degrees as a tuple.

        :return: tuple of azimuth and plunge in decimal degrees

        Example:
          >>> Direct(100, 20).d
          (100.0, 20.0)
        """

        return self.az.d, self.pl.d

    @property
    def r(self) -> Tuple[numbers.Real, numbers.Real]:
        """
        Returns azimuth and plunge in radians as a tuple.

        :return: tuple of azimuth and plunge in radians

        Example:
          >>> Direct(90, 45).r
          (1.5707963267948966, 0.7853981633974483)
        """

        return self.az.r, self.pl.r

    @property
    def az(self) -> Azim:
        """
        Returns the Azim instance.

        :return: Azim
        """

        return self._az

    @property
    def pl(self) -> Plunge:
        """
        Returns the plunge instance.

        :return: Plunge
        """

        return self._pl

    '''
    @classmethod
    def _from_xyz(cls,
                  x: numbers.Real,
                  y: numbers.Real,
                  z: numbers.Real
    ) -> 'Direct':
        """
        Private class constructor from three Cartesian values. Note: norm of components is unit.

        :param x: x component
        :param y: y component
        :param z: z component
        :return: Orientation instance
        """

        h = sqrt(x*x + y*y)

        az = Azim.fromXY(x, y)
        pl = Plunge.fromHZ(h, z)

        return cls(az.d, pl.d)
    '''

    @classmethod
    def from_xyz(cls,
                 x: numbers.Real,
                 y: numbers.Real,
                 z: numbers.Real
                 ) -> Tuple[Union[type(None), 'Direct'], Error]:
        """
        Class constructor from three generic Cartesian values.

        :param x: x component
        :param y: y component
        :param z: z component
        :return: direction instance

        Examples:
          >>> dir, err = Direct.from_xyz(1, 0, 0)
          >>> dir
          Direct(az: 90.00°, pl: 0.00°)
          >>> dir, err = Direct.from_xyz(0, 1, 0)
          >>> dir
          Direct(az: 0.00°, pl: 0.00°)
          >>> dir, err = Direct.from_xyz(0, 0, 1)
          >>> dir
          Direct(az: 0.00°, pl: -90.00°)
          >>> dir, err = Direct.from_xyz(0, 0, -1)
          >>> dir
          Direct(az: 0.00°, pl: 90.00°)
          >>> dir, err = Direct.from_xyz(1, 1, 0)
          >>> dir
          Direct(az: 45.00°, pl: 0.00°)
          >>> dir, err = Direct.from_xyz(0.5, -0.5, -0.7071067811865476)
          >>> dir
          Direct(az: 135.00°, pl: 45.00°)
          >>> dir, err = Direct.from_xyz(-0.5, 0.5, 0.7071067811865476)
          >>> dir
          Direct(az: 315.00°, pl: -45.00°)
          >>> dir, err = Direct.from_xyz(0, 0, 0)
          >>> bool(err)
          True
        """

        try:

            h = sqrt(x*x + y*y)

            az = Azim.fromXY(x, y)
            pl = Plunge.fromHZ(h, z)

            return cls(az.d, pl.d), Error()

        except Exception as e:

            return None, Error(True, caller_name(), e, traceback.format_exc())

    '''
    @classmethod
    def from_xyz(cls,
                 x: numbers.Real,
                 y: numbers.Real,
                 z: numbers.Real
                 ) -> 'Direct':
        """
        DEPRECATED: use 'from_xyz'.

        Class constructor from three generic Cartesian values.

        :param x: x component
        :param y: y component
        :param z: z component
        :return: Orientation instance

        Examples:
          >>> Direct.from_xyz(1, 0, 0)
          Direct(az: 90.00°, pl: -0.00°)
          >>> Direct.from_xyz(0, 1, 0)
          Direct(az: 0.00°, pl: -0.00°)
          >>> Direct.from_xyz(0, 0, 1)
          Direct(az: 0.00°, pl: -90.00°)
          >>> Direct.from_xyz(0, 0, -1)
          Direct(az: 0.00°, pl: 90.00°)
          >>> Direct.from_xyz(1, 1, 0)
          Direct(az: 45.00°, pl: -0.00°)
          >>> Direct.from_xyz(0.5, -0.5, -0.7071067811865476)
          Direct(az: 135.00°, pl: 45.00°)
          >>> Direct.from_xyz(-0.5, 0.5, 0.7071067811865476)
          Direct(az: 315.00°, pl: -45.00°)
          >>> Direct.from_xyz(0, 0, 0)
          Traceback (most recent call last):
          ...
          Exception: Input components have near-zero values
        """

        warnings.warn(
            "from_xyz is deprecated, use from_xyz instead",
            DeprecationWarning
        )

        result, error = norm_xyz(x, y, z)
        if error:
            raise Exception(error.exception)

        if result is None:
            raise Exception("Input components have near-zero values")

        _, norm = result

        return cls._from_xyz(*norm)
    '''

    @classmethod
    def from_vector(cls,
                  vect: Vect3D
                  ) -> Tuple[Union[type(None), 'Direct'], Error]:
        """
        Calculate the polar direction parallel to the Vect instance.
        Trend range: [0°, 360°[
        Plunge range: [-90°, 90°], with negative values for upward-pointing
        geological axes and positive values for downward-pointing axes.

        Examples:
          >>> dir, err = Direct.from_vector(Vect3D(1, 1, 1))
          >>> dir
          Direct(az: 45.00°, pl: -35.26°)
          >>> dir, err = Direct.from_vector(Vect3D(0, 1, 1))
          >>> dir
          Direct(az: 0.00°, pl: -45.00°)
          >>> dir, err = Direct.from_vector(Vect3D(1, 0, 1))
          >>> dir
          Direct(az: 90.00°, pl: -45.00°)
          >>> dir, err = Direct.from_vector(Vect3D(0, 0, 1))
          >>> dir
          Direct(az: 0.00°, pl: -90.00°)
          >>> dir, err = Direct.from_vector(Vect3D(0, 0, -1))
          >>> dir
          Direct(az: 0.00°, pl: 90.00°)
          >>> dir, err = Direct.from_vector(Vect3D(-1, 0, 0))
          >>> dir
          Direct(az: 270.00°, pl: -0.00°)
          >>> dir, err = Direct.from_vector(Vect3D(0, -1, 0))
          >>> dir
          Direct(az: 180.00°, pl: -0.00°)
          >>> dir, err = Direct.from_vector(Vect3D(-1, -1, 0))
          >>> dir
          Direct(az: 225.00°, pl: -0.00°)
          >>> dir, err = Direct.from_vector(Vect3D(0, 0, 0))
          >>> bool(err)
          True
        """

        try:

            if not vect.is_valid():
                return None, Error(True, caller_name(), Exception("vector is invalid"), traceback.format_exc())

            x, y, z = vect.to_xyz()
            return cls.from_xyz(x, y, z)

        except Exception as e:

            return None, Error(True, caller_name(), e, traceback.format_exc())

    '''
    @classmethod
    def from_vect(cls,
                  vect: Vect3D
                  ) -> Union[None, 'Direct', 'Axis']:
        """
        DEPRECATED: use 'from_vector'.

        Calculate the polar direction parallel to the Vect instance.
        Trend range: [0°, 360°[
        Plunge range: [-90°, 90°], with negative values for upward-pointing
        geological axes and positive values for downward-pointing axes.

        Examples:
          >>> Direct.from_vect(Vect3D(1, 1, 1))
          Direct(az: 45.00°, pl: -35.26°)
          >>> Direct.from_vect(Vect3D(0, 1, 1))
          Direct(az: 0.00°, pl: -45.00°)
          >>> Direct.from_vect(Vect3D(1, 0, 1))
          Direct(az: 90.00°, pl: -45.00°)
          >>> Direct.from_vect(Vect3D(0, 0, 1))
          Direct(az: 0.00°, pl: -90.00°)
          >>> Direct.from_vect(Vect3D(0, 0, -1))
          Direct(az: 0.00°, pl: 90.00°)
          >>> Direct.from_vect(Vect3D(-1, 0, 0))
          Direct(az: 270.00°, pl: -0.00°)
          >>> Direct.from_vect(Vect3D(0, -1, 0))
          Direct(az: 180.00°, pl: -0.00°)
          >>> Direct.from_vect(Vect3D(-1, -1, 0))
          Direct(az: 225.00°, pl: -0.00°)
          >>> Direct.from_vect(Vect3D(0, 0, 0))
          Traceback (most recent call last):
          ...
          Exception: Input components have near-zero values
        """

        warnings.warn(
            "from_vect is deprecated, use from_vector instead",
            DeprecationWarning
        )

        x, y, z = vect.to_xyz()

        return cls.from_xyz(x, y, z)
    '''

    def __repr__(self) -> str:

        return "Direct(az: {:.2f}°, pl: {:.2f}°)".format(*self.d)

    def to_xyz(self) -> Tuple[numbers.Real, numbers.Real, numbers.Real]:
        """
        Converts a direction to a tuple of x, y and z cartesian components (with unit norm).

        :return: tuple of x, y and z components.

        Examples:
          >>> apprFTuple(Direct(90, 0).to_xyz())
          (1.0, 0.0, 0.0)
          >>> apprFTuple(Direct(135, 45).to_xyz(), ndec=6)
          (0.5, -0.5, -0.707107)
          >>> apprFTuple(Direct(135, 0).to_xyz(), ndec=6)
          (0.707107, -0.707107, 0.0)
          >>> apprFTuple(Direct(180, 45).to_xyz(), ndec=6)
          (0.0, -0.707107, -0.707107)
          >>> apprFTuple(Direct(225, -45).to_xyz(), ndec=6)
          (-0.5, -0.5, 0.707107)
          >>> apprFTuple(Direct(270, 90).to_xyz(), ndec=6)
          (0.0, 0.0, -1.0)
        """

        x, y = self.az.toXY()
        h, z = self.pl.toHZ()

        return x*h, y*h, z

    def copy(self):
        """
        Return a copy of the instance.

        Example:
          >>> Direct(10, 20).copy()
          Direct(az: 10.00°, pl: 20.00°)
        """

        return self.__class__(self.az.d, self.pl.d)

    def opposite(self):
        """
        Return the opposite direction.

        Example:
          >>> Direct(0, 30).opposite()
          Direct(az: 180.00°, pl: -30.00°)
          >>> Direct(315, 10).opposite()
          Direct(az: 135.00°, pl: -10.00°)
          >>> Direct(135, 0).opposite()
          Direct(az: 315.00°, pl: -0.00°)
        """

        az, pl = self.r

        az = (az + pi) % (2*pi)
        pl = -pl

        return self.__class__(degrees(az), degrees(pl))

    def mirror_horizontal(self):
        """
        Return the mirror Orientation using a horizontal plane.

        Example:
          >>> Direct(0, 30).mirror_horizontal()
          Direct(az: 0.00°, pl: -30.00°)
          >>> Direct(315, 10).mirror_horizontal()
          Direct(az: 315.00°, pl: -10.00°)
          >>> Direct(135, 0).mirror_horizontal()
          Direct(az: 135.00°, pl: -0.00°)
        """

        az = self.az.r
        pl = -self.pl.r

        return self.__class__(degrees(az), degrees(pl))

    @property
    def colatitude_north(self) -> numbers.Real:
        """
        Calculates the colatitude from the North (top).

        :return: an rot_angle between 0 and 180 (in degrees).
        :rtype: numbers.Real.

        Examples:
          >>> Direct(320, 90).colatitude_north
          180.0
          >>> Direct(320, 45).colatitude_north
          135.0
          >>> Direct(320, 0).colatitude_north
          90.0
          >>> Direct(320, -45).colatitude_north
          45.0
          >>> Direct(320, -90).colatitude_north
          0.0
        """

        return plng2colatTop(self.pl.d)

    @property
    def colatitude_south(self) -> numbers.Real:
        """
        Calculates the colatitude from the South (bottom).

        :return: an rot_angle between 0 and 180 (in degrees).
        :rtype: numbers.Real.

        Examples:
          >>> Direct(320, 90).colatitude_south
          0.0
          >>> Direct(320, 45).colatitude_south
          45.0
          >>> Direct(320, 0).colatitude_south
          90.0
          >>> Direct(320, -45).colatitude_south
          135.0
          >>> Direct(320, -90).colatitude_south
          180.0
        """

        return plng2colatBottom(self.pl.d)

    def as_versor(self) -> Vect3D:
        """
        Return the unit vector corresponding to the Direct instance.

        Examples:
          >>> Direct(0, 90).as_versor()
          Vect3D(0.0000, 0.0000, -1.0000)
          >>> Direct(0, -90).as_versor()
          Vect3D(0.0000, 0.0000, 1.0000)
          >>> Direct(90, 90).as_versor()
          Vect3D(0.0000, 0.0000, -1.0000)
        """

        az, pl = self.r
        cos_az, cos_pl = cos(az), cos(pl)
        sin_az, sin_pl = sin(az), sin(pl)
        north_coord = cos_pl * cos_az
        east_coord = cos_pl * sin_az
        down_coord = sin_pl

        return Vect3D(
            east_coord,
            north_coord,
            -down_coord
        )

    @property
    def is_upward(self) -> bool:
        """
        Check whether the instance is pointing upward or horizontal.

        Examples:
          >>> Direct(10, 15).is_upward
          False
          >>> Direct(257.4, 0.0).is_upward
          False
          >>> Direct(90, -45).is_upward
          True
        """

        return self.pl.is_upward

    @property
    def is_downward(self) -> bool:
        """
        Check whether the instance is pointing downward or horizontal.

        Examples:
          >>> Direct(10, 15).is_downward
          True
          >>> Direct(257.4, 0.0).is_downward
          False
          >>> Direct(90, -45).is_downward
          False
        """

        return self.pl.is_downward

    def upward(self) -> 'Direct':
        """
        Return upward-point geological vector.

        Examples:
          >>> Direct(90, -45).upward().is_sub_parallel(Direct(90.0, -45.0))
          True
          >>> Direct(180, 45).upward().is_sub_parallel(Direct(0.0, -45.0))
          True
          >>> Direct(0, 0).upward().is_sub_parallel(Direct(0.0, 0.0))
          True
          >>> Direct(0, 90).upward().is_sub_parallel(Direct(180.0, -90.0))
          True
          >>> Direct(90, -45).upward().is_sub_parallel(Direct(90.0, -35.0))
          False
          >>> Direct(180, 45).upward().is_sub_parallel(Direct(10.0, -45.0))
          False
          >>> Direct(0, 0).upward().is_sub_parallel(Direct(170.0, 0.0))
          False
          >>> Direct(0, 90).upward().is_sub_parallel(Direct(180.0, -80.0))
          False
        """

        if not self.is_downward:
            return self.copy()
        else:
            return self.opposite()

    def downward(self) -> 'Direct':
        """
        Return downward-pointing geological vector.

        Examples:
          >>> Direct(90, -45).downward().is_sub_parallel(Direct(270.0, 45.0))
          True
          >>> Direct(180, 45).downward().is_sub_parallel(Direct(180.0, 45.0))
          True
          >>> Direct(0, 0).downward().is_sub_parallel(Direct(180.0, 0.0))
          False
          >>> Direct(0, 90).downward().is_sub_parallel(Direct(0.0, 90.0))
          True
          >>> Direct(90, -45).downward().is_sub_parallel(Direct(270.0, 35.0))
          False
          >>> Direct(180, 45).downward().is_sub_parallel(Direct(170.0, 45.0))
          False
          >>> Direct(0, 0).downward().is_sub_parallel(Direct(180.0, 10.0))
          False
          >>> Direct(0, 90).downward().is_sub_parallel(Direct(0.0, 80.0))
          False
        """

        if not self.is_upward:
            return self.copy()
        else:
            return self.opposite()

    def is_abs_dip_within(self,
                          min_val: numbers.Real,
                          max_val: numbers.Real,
                          min_val_incl: bool = False,
                          max_value_incl: bool = True
                          ) -> bool:
        """
        Check whether the absolute value of the dipang rot_angle of an Direct instance is intersect a given range
        (default: minimum value is not included, maximum value is included).

        :param min_val: the minimum dipang rot_angle, positive, domain: 0-90°.
        :param max_val: the maximum dipang rot_angle, positive, domain: 0-90°.
        :param min_val_incl: is minimum value included, boolean.
        :param max_value_incl: is maximum value included, boolean.
        :return: Boolean

        Examples:
          >>> Direct(90, -45).is_abs_dip_within(30, 60)
          True
          >>> Direct(120, 0).is_abs_dip_within(0, 60)
          False
          >>> Direct(120, 0).is_abs_dip_within(0, 60, min_val_incl=True)
          True
          >>> Direct(120, 60).is_abs_dip_within(0, 60)
          True
        """

        abs_dip = abs(self.pl.d)

        if abs_dip < min_val or abs_dip > max_val:
            return False
        elif abs_dip == min_val:
            if min_val_incl:
                return True
            else:
                return False
        elif abs_dip == max_val:
            if max_value_incl:
                return True
            else:
                return False
        else:
            return True

    def is_sub_horizontal(self,
                          max_dip_angle=DIP_ANGLE_THRESHOLD
                          ) -> bool:
        """
        Check whether the instance is almost horizontal.

        Examples:
          >>> Direct(10, 15).is_sub_horizontal()
          False
          >>> Direct(257, 2).is_sub_horizontal()
          True
          >>> Direct(90, -5).is_sub_horizontal()
          False
        """

        return abs(self.pl.d) < max_dip_angle

    def is_sub_vertical(self,
                        min_dip_angle=90.0 - DIP_ANGLE_THRESHOLD
                        ) -> bool:
        """
        Check whether the instance is almost vertical.

        Examples:
          >>> Direct(10, 15).is_sub_vertical()
          False
          >>> Direct(257, 89).is_sub_vertical()
          True
        """

        return abs(self.pl.d) > min_dip_angle

    def angle_with(self,
                   another: 'Direct'
                   ) -> numbers.Real:
        """
        Calculate rot_angle (in degrees) between the two Direct instances.
        Range is 0°-180°.

        Examples:
          >>> are_close(Direct(0, 90).angle_with(Direct(90, 0)), 90)
          True
          >>> are_close(Direct(0, 0).angle_with(Direct(270, 0)), 90)
          True
          >>> are_close(Direct(0, 0).angle_with(Direct(0, 0)), 0)
          True
          >>> are_close(Direct(0, 0).angle_with(Direct(180, 0)), 180)
          True
          >>> are_close(Direct(90, 0).angle_with(Direct(270, 0)), 180)
          True
        """

        angle_vers = self.as_versor().angle_with(another.as_versor())

        return angle_vers

    def is_sub_parallel(self,
                        another,
                        ang_tol_degr=VECTOR_ANGLE_THRESHOLD
        ):
        """
        Check that two Direct instances are sub-parallel,

        :param another: an Direct instance
        :param ang_tol_degr: the maximum allowed divergence rot_angle (in degrees)
        :return: Boolean

        Examples:
          >>> Direct(0, 90).is_sub_parallel(Direct(90, 0))
          False
          >>> Direct(0, 0).is_sub_parallel(Direct(0, 1e-6))
          True
          >>> Direct(0, 90).is_sub_parallel(Direct(180, 0))
          False
          >>> Direct(0, 90).is_sub_parallel(Direct(0, -90))
          False
        """

        fst_gvect = self

        snd_geoelem = another

        angle = fst_gvect.angle_with(snd_geoelem)

        if isinstance(another, Plane):
            return angle > (90.0 - ang_tol_degr)
        else:
            return angle <= ang_tol_degr

    def is_sub_antiparallel(self,
                            another,
                            ang_tol_degr=VECTOR_ANGLE_THRESHOLD
                            ) -> bool:
        """
        Check that two Vect instances are almost anti-parallel,

        :param another: a Vect instance
        :param ang_tol_degr: the maximum allowed divergence rot_angle (in degrees)
        :return: Boolean

        Examples:
          >>> Direct(0, 90).is_sub_antiparallel(Direct(90, -89.5))
          True
          >>> Direct(0, 0).is_sub_antiparallel(Direct(180, 1e-6))
          True
          >>> Direct(90, 45).is_sub_antiparallel(Direct(270, -45.5))
          True
          >>> Direct(45, 90).is_sub_antiparallel(Direct(0, -90))
          True
          >>> Direct(45, 72).is_sub_antiparallel(Direct(140, -38))
          False
        """

        return self.angle_with(another) > (180.0 - ang_tol_degr)

    def is_sub_orthogonal(self,
                          another: 'Direct',
                          ang_tol_degr: numbers.Real = VECTOR_ANGLE_THRESHOLD
                          ) -> bool:
        """
        Check that two Direct instance are sub-orthogonal

        :param another: a Direct instance
        :param ang_tol_degr: the maximum allowed divergence rot_angle (in degrees) from orthogonality
        :return: Boolean

         Examples:
          >>> Direct(0, 90).is_sub_orthogonal(Direct(90, 0))
          True
          >>> Direct(0, 0).is_sub_orthogonal(Direct(0, 1.e-6))
          False
          >>> Direct(0, 0).is_sub_orthogonal(Direct(180, 0))
          False
          >>> Direct(90, 0).is_sub_orthogonal(Direct(270, 89.5))
          True
          >>> Direct(0, 90).is_sub_orthogonal(Direct(0, 0.5))
          True
        """

        return 90.0 - ang_tol_degr <= self.angle_with(another) <= 90.0 + ang_tol_degr

    def normal_versor(self,
                      another: 'Direct'
                      ) -> Optional[Vect3D]:
        """
        Calculate the versor (Vect) defined by the vector product of two Direct instances.

        Examples:
          >>> Direct(0, 0).normal_versor(Direct(90, 0))
          Vect3D(0.0000, 0.0000, -1.0000)
          >>> Direct(45, 0).normal_versor(Direct(310, 0))
          Vect3D(0.0000, 0.0000, 1.0000)
          >>> Direct(0, 0).normal_versor(Direct(90, 90))
          Vect3D(-1.0000, 0.0000, -0.0000)
          >>> Direct(315, 45).normal_versor(Direct(315, 44.5)) is None
          True
        """

        if self.is_sub_parallel(another):
            return None
        else:
            return self.as_versor().cross_product(another.as_versor()).versor()

    def normal_plane(self) -> 'Plane':
        """
        Return the geological plane that is normal to the direction.

        Examples:
          >>> Direct(0, 45).normal_plane()
          Plane(180.00, +45.00)
          >>> Direct(0, -45).normal_plane()
          Plane(000.00, +45.00)
          >>> Direct(0, 90).normal_plane()
          Plane(180.00, +00.00)
        """

        down_orien = self.downward()
        dipdir = (down_orien.az.d + 180.0) % 360.0
        dipangle = 90.0 - down_orien.pl.d

        return Plane(dipdir, dipangle)

    def common_plane(self,
                     another
    ) -> Tuple[Union[type(None), 'Plane'], Error]:
        """
        Calculate Plane instance defined by the two directions.

        Examples:
          >>> plane, err = Direct(0, 0).common_plane(Direct(90, 0))
          >>> plane.is_sub_parallel(Plane(180.0, 0.0))
          True
          >>> plane, err = Direct(0, 0).common_plane(Direct(90, 90))
          >>> plane.is_sub_parallel(Plane(90.0, 90.0))
          True
          >>> plane, err = Direct(45, 0).common_plane(Direct(135, 45))
          >>> plane.is_sub_parallel(Plane(135.0, 45.0))
          True
          >>> plane, err = Direct(315, 45).common_plane(Direct(135, 45))
          >>> plane.is_sub_parallel(Plane(225.0, 90.0))
          True
          >>> plane, err = Direct(0, 0).common_plane(Direct(90, 0))
          >>> plane.is_sub_parallel(Plane(180.0, 10.0))
          False
          >>> plane, err = Direct(0, 0).common_plane(Direct(90, 90))
          >>> plane.is_sub_parallel(Plane(90.0, 80.0))
          False
          >>> plane, err = Direct(45, 0).common_plane(Direct(135, 45))
          >>> plane.is_sub_parallel(Plane(125.0, 45.0))
          False
          >>> plane, err = Direct(315, 45).common_plane(Direct(135, 45))
          >>> plane.is_sub_parallel(Plane(225.0, 80.0))
          False
          >>> plane, err = Direct(315, 45).common_plane(Direct(315, 44.5))
          >>> plane is None
          True
        """

        normal_versor = self.normal_versor(another)
        if normal_versor is None:
            return None, Error(True, caller_name(), Exception("Normal versor is None"), traceback.format_exc())
        else:
            direct, err = Direct.from_vector(normal_versor)
            if err:
                return None, err
            return direct.normal_plane(), Error()

    def normal_direction(self,
                         another: 'Direct'
    ) -> Union[type(None), 'Direct']:
        """
        Calculate the instance that is normal to the two provided sources.
        Angle between sources must be larger than MIN_ANGLE_DEGR_DISORIENTATION,

        Example:
          >>> Direct(0, 0).normal_direction(Direct(0.5, 0)) is None
          True
          >>> Direct(0, 0).normal_direction(Direct(179.5, 0)) is None
          True
          >>> Direct(0, 0).normal_direction(Direct(5.1, 0))
          Direct(az: 0.00°, pl: 90.00°)
          >>> Direct(90, 45).normal_direction(Direct(90, 0))
          Direct(az: 180.00°, pl: -0.00°)
        """

        if self.is_sub_antiparallel(another):
            return None
        elif self.is_sub_parallel(another):
            return None
        else:
            direct, err = self.__class__.from_vector(self.normal_versor(another))
            if err:
                return None
            return direct


class Axis(Direct):
    """
    Polar Axis. Inherits from Orientation
    """

    def __init__(self,
                 az: numbers.Real,
                 pl: numbers.Real
                 ):
        """
        Instantiate an Axis.

        Example:
          >>> Axis(0, 0)
          Axis(az: 0.00°, pl: 0.00°)
          >>> Axis(0, 90)
          Axis(az: 0.00°, pl: 90.00°)
          >>> Axis(360, 90)
          Axis(az: 0.00°, pl: 90.00°)
          >>> Axis(45, 170)
          Axis(az: 225.00°, pl: 10.00°)
          >>> Axis(45, 180)
          Axis(az: 225.00°, pl: 0.00°)
          >>> Axis(45, 190)
          Axis(az: 45.00°, pl: 10.00°)
          >>> Axis(45, 260)
          Axis(az: 45.00°, pl: 80.00°)
          >>> Axis(45, 270)
          Axis(az: 45.00°, pl: 90.00°)
          >>> Axis(45, 315)
          Axis(az: 225.00°, pl: 45.00°)
          >>> Axis(45, 305)
          Axis(az: 225.00°, pl: 55.00°)
          >>> Axis(45, 225)
          Axis(az: 45.00°, pl: 45.00°)
          >>> Axis(45, 135)
          Axis(az: 225.00°, pl: 45.00°)
        """

        check_type(az, "Azimuth", (numbers.Integral, numbers.Real))
        check_type(pl, "Plunge", (numbers.Integral, numbers.Real))

        if pl < 0.:
            pl = - pl
            az = az + 180.

        pl = pl % 360.

        if pl > 270.:
            az = az + 180.
            pl = 360. - pl
        elif pl > 180.:
            pl = pl - 180.
        elif pl > 90.:
            az = az + 180.
            pl = 180. - pl

        super().__init__(az % 360.0, pl)

    def __repr__(self):

        return "Axis(az: {:.2f}°, pl: {:.2f}°)".format(*self.d)

    @classmethod
    def from_xyz(cls,
                 x: numbers.Real,
                 y: numbers.Real,
                 z: numbers.Real
                 ) -> Tuple[Union[type(None), 'Axis'], Error]:
        """
        Class constructor from three generic Cartesian values.

        :param x: x component
        :param y: y component
        :param z: z component
        :return: axis instance

        Examples:
          >>> axis, err = Axis.from_xyz(1, 0, 0)
          >>> axis
          Axis(az: 90.00°, pl: 0.00°)
          >>> axis, err = Axis.from_xyz(0, 1, 0)
          >>> axis
          Axis(az: 0.00°, pl: 0.00°)
          >>> axis, err = Axis.from_xyz(0, 0, 1)
          >>> axis
          Axis(az: 180.00°, pl: 90.00°)
          >>> axis, err = Axis.from_xyz(0, 0, -1)
          >>> axis
          Axis(az: 0.00°, pl: 90.00°)
          >>> axis, err = Axis.from_xyz(1, 1, 0)
          >>> axis
          Axis(az: 45.00°, pl: 0.00°)
          >>> axis, err = Axis.from_xyz(0.5, -0.5, -0.7071067811865476)
          >>> axis
          Axis(az: 135.00°, pl: 45.00°)
          >>> axis, err = Axis.from_xyz(-0.5, 0.5, 0.7071067811865476)
          >>> axis
          Axis(az: 135.00°, pl: 45.00°)
          >>> axis, err = Axis.from_xyz(0, 0, 0)
          >>> bool(err)
          True
        """

        try:

            h = sqrt(x*x + y*y)

            az = Azim.fromXY(x, y)
            pl = Plunge.fromHZ(h, z)

            return cls(az.d, pl.d), Error()

        except Exception as e:

            return None, Error(True, caller_name(), e, traceback.format_exc())

    @classmethod
    def from_direction(cls,
        direction: Direct
    ) -> 'Axis':
        """
        Create Axis instance from a direction.

        Example:
          >>> Axis.from_direction(Direct(220, 32))
          Axis(az: 220.00°, pl: 32.00°)
        """

        check_type(direction, "Direction", Direct)

        return Axis(
            az=direction.az.d,
            pl=direction.pl.d
        )

    def as_direction(self) -> Direct:
        """
        Create Direct instance with the same plane_attitude as the self instance.

        Example:
          >>> Axis(220, 32).as_direction()
          Direct(az: 220.00°, pl: 32.00°)
          >>> Axis(220, -32).as_direction()
          Direct(az: 40.00°, pl: 32.00°)
        """

        return Direct(
            az=self.az.d,
            pl=self.pl.d
        )

    def normal_axis(self,
                    another: 'Axis'
    ) -> Optional['Axis']:
        """
        Calculate the Axis instance that is perpendicular to the two provided.
        The two source Axis must not be subparallel (threshold is MIN_ANGLE_DEGR_DISORIENTATION),
        otherwise a SubparallelLineationException will be raised.

        Example:
          >>> Axis(0, 0).normal_axis(Axis(0.5, 0)) is None
          True
          >>> Axis(0, 0).normal_axis(Axis(180, 0)) is None
          True
          >>> Axis(90, 0).normal_axis(Axis(180, 0))
          Axis(az: 0.00°, pl: 90.00°)
          >>> Axis(90, 45).normal_axis(Axis(180, 0))
          Axis(az: 270.00°, pl: 45.00°)
          >>> Axis(270, 45).normal_axis(Axis(180, 90)).is_sub_parallel(Axis(180, 0))
          True
        """

        norm_orien = self.normal_direction(another)
        if norm_orien is None:
            return None
        else:
            return Axis.from_direction(norm_orien)

    def angle_with(self,
                   another
                   ):
        """
        Calculate rot_angle (in degrees) between the two Axis instances.
        Range is 0°-90°.

        Examples:
          >>> are_close(Axis(0, 90).angle_with(Axis(90, 0)), 90)
          True
          >>> are_close(Axis(0, 0).angle_with(Axis(270, 0)), 90)
          True
          >>> are_close(Axis(0, 0).angle_with(Axis(0, 0)), 0)
          True
          >>> are_close(Axis(0, 0).angle_with(Axis(180, 0)), 0)
          True
          >>> are_close(Axis(0, 0).angle_with(Axis(179, 0)), 1)
          True
          >>> are_close(Axis(0, -90).angle_with(Axis(0, 90)), 0)
          True
          >>> are_close(Axis(90, 0).angle_with(Axis(315, 0)), 45)
          True
        """

        angle_vers = self.as_versor().angle_with(another.as_versor())

        return min(angle_vers, 180.0 - angle_vers)


class Plane:
    """
    Geological plane.
    Defined by dipang direction and dipang rot_angle (both in degrees):
     - dipang direction: [0.0, 360.0[ clockwise, from 0 (North);
     - dipang rot_angle: [0, 90.0]: downward-pointing.
    """

    def __init__(self,
                 azim: numbers.Real,
                 dip_ang: numbers.Real,
                 is_rhr_strike: bool = False
    ):
        """
        Geological plane constructor.

        :param  azim:  azimuth of the plane (RHR strike or dipang direction).
        :type  azim:  number or string convertible to float.
        :param  dip_ang:  Dip rot_angle of the plane (0-90°).
        :type  dip_ang:  number or string convertible to float.
        :param is_rhr_strike: if the source azimuth is RHR strike (default is False, i.e. it is dipang direction)
        :return: the instantiated geological plane.
        :rtype: Plane.

        Example:
          >>> Plane(0, 90)
          Plane(000.00, +90.00)
          >>> Plane(0, 90, is_rhr_strike=True)
          Plane(090.00, +90.00)
          >>> Plane(0, 90, True)
          Plane(090.00, +90.00)
          >>> Plane(0, 900)
          Traceback (most recent call last):
          ...
          Exception: Dip rot_angle must be between 0° and 90°
        """

        def rhrstrk2dd(rhr_strk):
            """Converts RHR strike value to dipang direction value.

            Example:
                >>> rhrstrk2dd(285.5)
                15.5
            """

            return (rhr_strk + 90.0) % 360.0

        if not isinstance(azim, numbers.Real):
            raise Exception("Source azimuth must be number")
        if not isinstance(dip_ang, numbers.Real):
            raise Exception("Source dipang rot_angle must be number")
        if not isinstance(is_rhr_strike, bool):
            raise Exception("Source azimuth type must be boolean")

        if not (0.0 <= dip_ang <= 90.0):
            raise Exception("Dip rot_angle must be between 0° and 90°")

        if is_rhr_strike:
            self._dipdir = rhrstrk2dd(azim)
        else:
            self._dipdir = azim % 360.0
        self._dipangle = float(dip_ang)

    @classmethod
    def from_normal(cls,
        normal: Vect3D):
        """
        Create a plane given its normal.
        """

        direct, _ = Direct.from_vector(normal)
        return direct.normal_plane()

    @property
    def dipazim(self):
        """
        Return the azimuth of the dip direction of the geological plane.

        Example:
          >>> Plane(34.2, 89.7).dipazim
          34.2
        """

        return self._dipdir

    @property
    def dipang(self):
        """
        Return the dip angle of the geological plane.

        Example:
          >>> Plane(183, 77).dipang
          77.0

        """

        return self._dipangle

    @property
    def vals(self):
        """
        Return a tuple storing the dipang direction and dipang rot_angle values of a geological plane.

        Example:
          >>> gp = Plane(89.4, 17.2)
          >>> gp.vals
          (89.4, 17.2)
        """

        return self.dipazim, self.dipang

    @property
    def rhr_strike(self) -> numbers.Real:
        """
        Return the strike according to the right-hand-rule.

        Examples:
          >>> Plane(90, 45).rhr_strike
          0.0
          >>> Plane(45, 89).rhr_strike
          315.0
          >>> Plane(275, 38).rhr_strike
          185.0
          >>> Plane(0, 38).rhr_strike
          270.0
        """

        return (self.dipazim - 90.0) % 360.0

    @property
    def strike_dipang(self):
        """
        Return a tuple storing the right-hand-rule strike and dipang rot_angle values of a geological plane.

        Example:
          >>> Plane(100, 17.2).strike_dipang
          (10.0, 17.2)
          >>> Plane(10, 87).strike_dipang
          (280.0, 87.0)
        """

        return self.rhr_strike, self.dipang

    @property
    def lhr_strike(self):
        """
        Return the strike according to the left-hand-rule.

        Examples:
          >>> Plane(90, 45).lhr_strike
          180.0
          >>> Plane(45, 89).lhr_strike
          135.0
          >>> Plane(275, 38).lhr_strike
          5.0
          >>> Plane(0, 38).lhr_strike
          90.0
        """

        return (self.dipazim + 90.0) % 360.0

    @property
    def lhr_strike_dipang(self):
        """
        Return a tuple storing the left-hand-rule strike and dipang rot_angle values of a geological plane.

        Example:
          >>> Plane(100, 17.2).lhr_strike_dipang
          (190.0, 17.2)
          >>> Plane(10, 87).lhr_strike_dipang
          (100.0, 87.0)
        """

        return self.lhr_strike, self.dipang

    def __repr__(self):

        return "Plane({:06.2f}, {:+06.2f})".format(*self.vals)

    def rhr_strike_direction(self) -> Direct:
        """
        Creates a direction instance that is parallel to the right-hand rule strike.

        Examples:
          >>> Plane(90, 45).rhr_strike_direction()
          Direct(az: 0.00°, pl: 0.00°)
          >>> Plane(45, 17).rhr_strike_direction()
          Direct(az: 315.00°, pl: 0.00°)
          >>> Plane(90, 0).rhr_strike_direction()
          Direct(az: 0.00°, pl: 0.00°)
        """

        return Direct(
            az=self.rhr_strike,
            pl=0.0)

    def lhr_strike_orien(self):
        """
        Creates an Orientation instance that is parallel to the left-hand rule strike.

        :return: OrienM instance.

        Examples:
          >>> Plane(90, 45).lhr_strike_orien()
          Direct(az: 180.00°, pl: 0.00°)
          >>> Plane(45, 17).lhr_strike_orien()
          Direct(az: 135.00°, pl: 0.00°)
        """

        return Direct(
            az=self.lhr_strike,
            pl=0.0)

    def dip_dir_orien(self):
        """
        Creates a OrienM instance that is parallel to the dipang direction.

        :return: OrienM instance.

        Examples:
          >>> Plane(90, 45).dip_dir_orien()
          Direct(az: 90.00°, pl: 45.00°)
          >>> Plane(45, 17).dip_dir_orien()
          Direct(az: 45.00°, pl: 17.00°)
        """

        return Direct(
            az=self.dipazim,
            pl=self.dipang)

    def dip_dir_opp_orien(self):
        """
        Creates a OrienM instance that is anti-parallel to the dipang direction.

        :return: OrienM instance.

        Examples:
          >>> Plane(90, 45).dip_dir_opp_orien()
          Direct(az: 270.00°, pl: -45.00°)
          >>> Plane(45, 17).dip_dir_opp_orien()
          Direct(az: 225.00°, pl: -17.00°)
        """

        return self.dip_dir_orien().opposite()

    def mirror_vert_p_plane(self):
        """
        Mirror a geological plane around a vertical plane
        creating a new one that has a dipang direction opposite
        to the original one but with downward plunge.

        :return: geological plane
        :rtype: Plane

        Examples:
          >>> Plane(0, 45).mirror_vert_p_plane()
          Plane(180.00, +45.00)
          >>> Plane(225, 80).mirror_vert_p_plane()
          Plane(045.00, +80.00)
          >>> Plane(90, 90).mirror_vert_p_plane()
          Plane(270.00, +90.00)
          >>> Plane(270, 0).mirror_vert_p_plane()
          Plane(090.00, +00.00)
        """

        return Plane(
            azim=opposite_trend(self.dipazim),
            dip_ang=self.dipang)

    def norm_direct_frwrd(self) -> Direct:
        """
        Return the direction normal to the geological plane,
        pointing in the same direction as the geological plane.

        Example:
            >>> Plane(90, 55).norm_direct_frwrd()
            Direct(az: 90.00°, pl: -35.00°)
            >>> Plane(90, 90).norm_direct_frwrd()
            Direct(az: 90.00°, pl: 0.00°)
            >>> Plane(90, 0).norm_direct_frwrd()
            Direct(az: 90.00°, pl: -90.00°)
        """

        tr = self.dipazim % 360.0
        pl = self.dipang - 90.0

        return Direct(
            az=tr,
            pl=pl)

    def nor_direct_bckwrd(self):
        """
        Return the direction normal to the geological plane,
        pointing in the opposite direction to the geological plane.

        Example:
            >>> Plane(90, 55).nor_direct_bckwrd()
            Direct(az: 270.00°, pl: 35.00°)
            >>> Plane(90, 90).nor_direct_bckwrd()
            Direct(az: 270.00°, pl: -0.00°)
            >>> Plane(90, 0).nor_direct_bckwrd()
            Direct(az: 270.00°, pl: 90.00°)
        """

        return self.norm_direct_frwrd().opposite()

    def norm_direct_down(self):
        """
        Return the direction normal to the geological plane and
        pointing downward.

        Example:
            >>> Plane(90, 55).norm_direct_down()
            Direct(az: 270.00°, pl: 35.00°)
            >>> Plane(90, 90).norm_direct_down()
            Direct(az: 90.00°, pl: 0.00°)
            >>> Plane(90, 0).norm_direct_down()
            Direct(az: 270.00°, pl: 90.00°)
        """

        return self.norm_direct_frwrd().downward()

    def norm_direct_up(self):
        """
        Return the direction normal to the polar plane,
        pointing upward.

        Example:
            >>> Plane(90, 55).norm_direct_up()
            Direct(az: 90.00°, pl: -35.00°)
            >>> Plane(90, 90).norm_direct_up()
            Direct(az: 90.00°, pl: 0.00°)
            >>> Plane(90, 0).norm_direct_up()
            Direct(az: 90.00°, pl: -90.00°)
        """

        return self.norm_direct_frwrd().upward()

    def normal_direction(self) -> 'Direct':
        """
        Wrapper to down_normal_gv.

        :return: downward-pointing Direct instance normal to the Plane self instance
        """

        return self.norm_direct_down()

    def normal_axis(self) -> Axis:
        """
        Normal Axis.

        :return: Axis normal to the Plane self instance
        """

        return Axis.from_direction(self.norm_direct_down())

    def angle_with(self, another: 'Plane'):
        """
        Calculate rot_angle (in degrees) between two geoplanes.
        Range is 0°-90°.

        Examples:
          >>> Plane(100.0, 50.0).angle_with(Plane(100.0, 50.0))
          0.0
          >>> Plane(300.0, 11.0).angle_with(Plane(300.0, 90.0))
          79.0
          >>> Plane(90.0, 90.0).angle_with(Plane(270.0, 90.0))
          0.0
          >>> are_close(Plane(90.0, 90.0).angle_with(Plane(130.0, 90.0)), 40)
          True
          >>> are_close(Plane(90, 70).angle_with(Plane(270, 70)), 40)
          True
          >>> are_close(Plane(90.0, 10.0).angle_with(Plane(270.0, 10.0)), 20.0)
          True
          >>> are_close(Plane(90.0, 10.0).angle_with(Plane(270.0, 30.0)), 40.0)
          True
        """

        if not isinstance(another, Plane):
            raise Exception("Second instance for rot_angle is of {} type".format(type(another)))

        gpl_axis = Axis.from_direction(self.norm_direct_frwrd())
        an_axis = Axis.from_direction(another.norm_direct_frwrd())

        return gpl_axis.angle_with(an_axis)

    def is_sub_parallel(self,
                        another,
                        ang_tol_degr: numbers.Real = PLANE_ANGLE_THRESHOLD
    ):
        """
        Check that two GPlanes are sub-parallel

        :param another: a Plane instance
        :param ang_tol_degr: the maximum allowed divergence rot_angle (in degrees)
        :return: Boolean

         Examples:
          >>> Plane(0, 90).is_sub_parallel(Plane(270, 90))
          False
          >>> Plane(0, 90).is_sub_parallel(Plane(180, 90))
          True
          >>> Plane(0, 90).is_sub_parallel(Plane(0, 0))
          False
          >>> Plane(0, 0).is_sub_parallel(Plane(0, 1e-6))
          True
          >>> Plane(0, 0).is_sub_parallel(Plane(0, 1.1))
          False
        """

        return self.angle_with(another) < ang_tol_degr

    def contains(self,
        direct: 'Direct',
        ang_tol_degr: numbers.Real = PLANE_ANGLE_THRESHOLD
    ) -> bool:
        """
        Check that a plane contains a direction instance.

        :param direct: a Direct instance
        :param ang_tol_degr: the tolerance rot_angle
        :return: True or False

        Examples:
          >>> Plane(90, 0).contains(Direct(60, 0))
          True
          >>> Plane(90, 0).contains(Axis(60, 0))
          True
          >>> Plane(90, 0).contains(Direct(60, 10))
          False
        """

        plane_norm = self.normal_axis()

        return direct.is_sub_orthogonal(plane_norm, ang_tol_degr)

    def is_sub_orthogonal(self,
                          another,
                          ang_tol_degr: numbers.Real = PLANE_ANGLE_THRESHOLD
    ):
        """
        Check that two GPlanes are sub-orthogonal.

        :param another: a Plane instance
        :param ang_tol_degr: the maximum allowed divergence rot_angle (in degrees)
        :return: Boolean

         Examples:
          >>> Plane(0, 90).is_sub_orthogonal(Plane(270, 90))
          True
          >>> Plane(0, 90).is_sub_orthogonal(Plane(180, 90))
          False
          >>> Plane(0, 90).is_sub_orthogonal(Plane(0, 0))
          True
          >>> Plane(0, 0).is_sub_orthogonal(Plane(0, 88))
          False
          >>> Plane(0, 0).is_sub_orthogonal(Plane(0, 45))
          False
        """

        fst_axis = Axis.from_direction(self.normal_direction())

        if isinstance(another, Plane):
            snd_gaxis = Axis.from_direction(another.normal_direction())
        else:
            raise Exception("Not accepted argument type for isSubOrthog method")

        angle = fst_axis.angle_with(snd_gaxis)

        if isinstance(another, Plane):
            return angle > 90.0 - ang_tol_degr
        else:
            return angle < ang_tol_degr

    def rake_to_direct(self,
        rake: numbers.Real
    ) -> Tuple[Union[type(None), 'Direct'], Error]:
        """
        Calculate the Direct instance given a Plane instance and a rake value.
        The rake is defined according to the Aki and Richards, 1980 conventions:
        rake = 0° -> left-lateral
        rake = 90° -> reverse
        rake = +/- 180° -> right-lateral
        rake = -90° -> normal

        Examples:
          >>> direct, err = Plane(180, 45).rake_to_direct(0.0)
          >>> direct
          Direct(az: 90.00°, pl: -0.00°)
          >>> direct, err = Plane(180, 45).rake_to_direct(90.0)
          >>> direct
          Direct(az: 0.00°, pl: -45.00°)
          >>> direct, err = Plane(180, 45).rake_to_direct(-90.0)
          >>> direct
          Direct(az: 180.00°, pl: 45.00°)
          >>> direct, err = Plane(180, 45).rake_to_direct(180.0)
          >>> direct.is_sub_parallel(Direct(270.00, 0.00))
          True
          >>> direct, err = Plane(180, 45).rake_to_direct(-180.0)
          >>> direct
          Direct(az: 270.00°, pl: 0.00°)
        """

        rk = radians(rake)
        strk = radians(self.rhr_strike)
        dip = radians(self.dipang)

        x = cos(rk) * sin(strk) - sin(rk) * cos(dip) * cos(strk)
        y = cos(rk) * cos(strk) + sin(rk) * cos(dip) * sin(strk)
        z = sin(rk) * sin(dip)

        return Direct.from_xyz(x, y, z)

    def is_very_low_angle(self,
                          dip_angle_threshold: numbers.Real = DIP_ROTAT_ANGLE_THRESH
                          ):
        """
        Checks if a geological plane is very low rot_angle.

        :param dip_angle_threshold: the limit for the plane rot_angle, in degrees
        :type dip_angle_threshold: numbers.Real.
        :return: bool flag indicating if it is very low rot_angle

        Examples:
          >>> Plane(38.9, 1.2).is_very_low_angle()
          True
          >>> Plane(38.9, 7.4).is_very_low_angle()
          False
        """

        return self.dipang < dip_angle_threshold

    def is_very_high_angle(self,
                           dip_angle_threshold: numbers.Real = DIP_ROTAT_ANGLE_THRESH
                           ):
        """
        Checks if a geological plane is very high rot_angle.

        :param dip_angle_threshold: the limit for the plane rot_angle, in degrees
        :type dip_angle_threshold: numbers.Real.
        :return: bool flag indicating if it is very high rot_angle

        Examples:
          >>> Plane(38.9, 11.2).is_very_high_angle()
          False
          >>> Plane(38.9, 88.4).is_very_high_angle()
          True
        """

        return self.dipang > (90.0 - dip_angle_threshold)

    def m_coeff_in_x_dir(self) -> numbers.Real:
        """
        Calculate the m coefficient of a given plane along the x direction.
        It is equivalent to delta z divided by distance.
        So it is equivalent to the m value of the line.
        The plane orientation  is expressed following the geological convention.

        :return: the slope along the x direction

        Examples:
          >>> Plane(90, 42).m_coeff_in_x_dir() == tan(radians(-42))
          True
          >>> Plane(270, 42).m_coeff_in_x_dir() == tan(radians(42))
          True
          >>> are_close(Plane(0, 42).m_coeff_in_x_dir(), 0)
          True
          >>> are_close(Plane(180, 42).m_coeff_in_x_dir(), 0)
          True
          >>> are_close(Plane(90, 0).m_coeff_in_x_dir(), 0)
          True

        Examples:
          >>> Plane(180, 42).m_coeff_in_y_dir() == tan(radians(42))
          True
          >>> Plane(0, 42).m_coeff_in_y_dir() == tan(radians(-42))
          True
          >>> are_close(Plane(90, 42).m_coeff_in_y_dir(), 0)
          True
          >>> are_close(Plane(270, 42).m_coeff_in_y_dir(), 0)
          True
          >>> are_close(Plane(90, 0).m_coeff_in_y_dir(), 0)
          True

        """
        return - sin(radians(self.dipazim)) * tan(radians(self.dipang))

    def m_coeff_in_y_dir(self) -> numbers.Real:
        """
        Calculate the m coefficient of a given plane along the y direction.
        The plane orientation  is expressed following the geological convention.

        :return: the slope along the y direction
        """
        return - cos(radians(self.dipazim)) * tan(radians(self.dipang))

    def plane_from_geo(self, or_Pt):
        """
        Closure that embodies the analytical formula for a given, non-vertical plane.
        This closure is used to calculate the z value from given horizontal coordinates (x, y).

        @param  or_Pt:  Point_3D instance expressing a location point contained by the plane.
        @type  or_Pt:  Point_3D.

        @return:  lambda (closure) expressing an analytical formula for deriving z given x and y values.
        """

        x0 = or_Pt.x
        y0 = or_Pt.y
        z0 = or_Pt.z

        # slope of the line parallel to the x axis and contained by the plane
        a = self.m_coeff_in_x_dir()

        # slope of the line parallel to the y axis and contained by the plane
        b = self.m_coeff_in_y_dir()

        return lambda x, y: a * (x - x0) + b * (y - y0) + z0


if __name__ == "__main__":

    import doctest
    doctest.testmod()
