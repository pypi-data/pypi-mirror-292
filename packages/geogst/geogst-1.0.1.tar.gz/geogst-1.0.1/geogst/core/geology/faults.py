
from geogst.core.orientations.orientations import *
from geogst.core.geology.utils.faults import *


class Slickenline(object):
    """
    Slickeline.
    It can be represented by a Direct instance, when it has a movement sense,
    or by an Axis instance, when the movement sense is unknown or not sure.
    When the movement sense is known, the instance indicates the displacement of the block that is:
    - for a horizontal or a dipping, non-vertical fault: the upper block
    - for a vertical fault: the block individuated by the (formal) dip direction.
    """

    def __init__(
        self,
        trend: Union[numbers.Real, type(None)] = None,
        plunge: Union[numbers.Real, type(None)] = None,
        rake: Union[numbers.Real, type(None)] = None,
        known: bool = True,
        time: numbers.Real = 0.0
    ):
        """"
        Class constructors from trend, plunge and optional known movement sense flag.

        :param trend: the trend of the slickenline
        :param plunge: the slickenline plunge
        :param known: the known movement sense flag
        :param time: the absolute or relative timing of the slickeline.
        :return: the Slickenline instance
        :raise: Exception

        Example:
          >>> Slickenline(90, 10)
          Slickenline(az: 90.00°, pl: 10.00°, known_dir: True, time: 0.0)
          >>> Slickenline(90, 10, known=False)
          Slickenline(az: 90.00°, pl: 10.00°, known_dir: False, time: 0.0)
          >>> Slickenline(0, -10, known=False)
          Slickenline(az: 0.00°, pl: -10.00°, known_dir: False, time: 0.0)
        """

        if not isinstance(trend, numbers.Real):
            raise Exception("Trend must be a number")
        if not isinstance(plunge, numbers.Real):
            raise Exception("Plunge must be a number")
        if not isinstance(known, bool):
            raise Exception("Known movement sense must be a boolean")
        if not isinstance(time, (numbers.Real, str)):
            raise Exception("Time must be a number or a string")

        self.trend = trend
        self.plunge = plunge
        self.rake = rake
        self.known = known
        self.time = time

    def __repr__(self):

        return f"Slickenline(az: {self.trend:.2f}°, pl: {self.plunge:.2f}°, known_dir: {self.known}, time: {self.time})"

    @property
    def geom(self) -> Union[Direct, Axis]:
        """
        Returns the geometric object (Direct or Axis) defining the slickenline.

        :return: Direct or Axis instance

        Examples:
          >>> Slickenline(90, 45).geom
          Direct(az: 90.00°, pl: 45.00°)
          >>> Slickenline(90, 45, known=False).geom
          Axis(az: 90.00°, pl: 45.00°)
        """

        if self.known:
            return Direct(self.trend, self.plunge)
        else:
            return Axis(self.trend, self.plunge)

    def has_known_sense(self) -> bool:
        """
        Check whether the slickenline has known movement sense.

        Example:
          >>> Slickenline(90, 45).has_known_sense()
          True
          >>> Slickenline(90, 45, known=False).has_known_sense()
          False
        """

        return self.known

    def has_unknown_sense(self) -> bool:
        """
        Check whether the slickenline has unknown/uncertain movement sense.

        Example:
          >>> Slickenline(90, 45, known=False).has_unknown_sense()
          True
          >>> Slickenline(90, 45).has_unknown_sense()
          False
        """

        return not self.has_known_sense()

    def set_known_sense(self):
        """
        Set the slickenline movement sense to known.

        Example:
          >>> sl = Slickenline(180, 30, known=False)
          >>> sl.set_known_sense()
          >>> sl
          Slickenline(az: 180.00°, pl: 30.00°, known_dir: True, time: 0.0)
        """

        self.known = True

    def set_unknown_sense(self):
        """
        Set to unknown/uncertain the movement sense for the current Slickline instance.

        Example:
          >>> sl = Slickenline(180, -30)
          >>> sl.set_unknown_sense()
          >>> sl
          Slickenline(az: 180.00°, pl: -30.00°, known_dir: False, time: 0.0)
        """

        self.known = False

    def invert(self) -> Optional['Slickenline']:
        """
        Invert the slickenline orientation.

        Example:
         >>> Slickenline(30, 45, known=False).invert()
         Slickenline(az: 210.00°, pl: -45.00°, known_dir: False, time: 0.0)
         >>> Slickenline(30, 45).invert()
         Slickenline(az: 210.00°, pl: -45.00°, known_dir: True, time: 0.0)
        """

        return Slickenline(
            (self.trend + 180.0) % 360.0 if self.trend is not None else None,
            -self.plunge if self.plunge is not None else None,
            opposite_rake(self.rake) if self.rake is not None else None,
            self.known,
            self.time
        )


class Fault(object):
    """
    Represent a fault plane, composed by a Plane instance, and zero, one or more slickenlines,
    stored by a list of Slickenline instances (None when no slickenlines).
    """

    def __init__(self,
        azim: numbers.Real,
        dip_ang: numbers.Real,
        slickenlines: Union[type(None), numbers.Real, Sequence[numbers.Real], Slickenline, Sequence[Slickenline]] = None,
        is_rhr_strike: bool = False,
    ):
        """
        Create an instance of a Fault.

        :param  azim:  azimuth of the plane (RHR strike or dipang direction).
        :param  dip_ang:  Dip rot_angle of the plane (0-90°).
        :param slickenlines: optional one or more slickenlines associated with the fault plane, as rakes or slikenlines.
        :param is_rhr_strike: if the source azimuth is RHR strike (default is False, i.e. it is dipang direction)
        :return: the instantiated fault instance.
        :raise: Exception.

        Example:
          >>> Fault(90, 45, slickenlines=[Slickenline(90, 45)])
          Fault(90.0, 45.0) with Slickenline(rake: -90.00)
          >>> Fault(90, 45, slickenlines=[Slickenline(90, 55)])
          Slickenline(az: 90.00°, pl: 55.00°, known_dir: True, time: 0.0) does not lie on the fault plane Plane(090.00, +45.00)
        """

        if not isinstance(azim, numbers.Real):
            raise Exception("Azim must be a number")
        if not isinstance(dip_ang, numbers.Real):
            raise Exception("Dip rot_angle must be a number")

        self._fltpln = Plane(azim, dip_ang, is_rhr_strike)

        slicks = []  # to be populated with Slickenline instances
        self._parse_slickenline_input(slickenlines, slicks)
        self._slicks = slicks

    def _parse_slickenline_input(self,
        input: Any,
        slicks: list
    ) -> None:
        """
        Parses recursively slickenline(s) populating an initially empty list with Slickenline instances.

        :param input: a potential rake or slickenline.
        :params slicks: the slickenline list that is referred.:
        :return: None
        """

        if isinstance(input, numbers.Real):
            slickenline, err = self.rake_to_slickenline(input)
            if not err and slickenline is not None:
                slicks.append(slickenline)
            else:
                print(err)
        elif isinstance(input, Slickenline):
            if not self.plane.contains(input.geom):
                print(f"{input} does not lie on the fault plane {self.plane}")
            else:
                slicks.append(input)
        elif isinstance(input, (list, tuple)):
            for slick in input:
                self._parse_slickenline_input(slick, slicks)
        else:
            print(f"Warning: {input} is of type {type(input)}")

    def __repr__(self):

        if self.num_slickenlines == 0:
            slick_txt = "no slickenlines"
        elif self.num_slickenlines == 1:
            slick_txt = f"Slickenline(rake: {self.rake(0):.2f})"
        else:
            slick_txt = f"{len(self.slickenlines())} slickelines"

        return f"Fault({self.plane.vals[0]}, {self.plane.vals[1]}) with {slick_txt}"

    @property
    def plane(self) -> Plane:
        """
        Return fault plane, as a Plane instance.

        Example:
          >>> Fault(90, 45, slickenlines=[Slickenline(90, 45)]).plane
          Plane(090.00, +45.00)
        """

        return self._fltpln

    @property
    def num_slickenlines(self) -> numbers.Integral:
        """
        Returns the number of slickenlines.

        :return: number of slickenlines, as integer

        Examples:
          >>> Fault(90, 45, slickenlines=[Slickenline(90, 45)]).num_slickenlines
          1
        """

        return len(self._slicks)

    def has_slickenlines(self) -> bool:
        """
        Returns whether there are slickenlines associated.

        :return: whether there are slickenlines associated.

        Examples:
          >>> Fault(90, 45, slickenlines=[Slickenline(90, 45)]).has_slickenlines()
          True
        """

        return self.num_slickenlines > 0

    def slickenlines(self) -> List[Slickenline]:
        """
        Return the slickenlines associated with the fault.
        """

        return self._slicks

    def slickenline(self,
        ndx: numbers.Integral = 0
    ) -> Slickenline:
        """
        Return the slickenline with the given index associated with the fault.

        :param ndx: the slickenline index.
        :return: the associated slickenline.
        :raise: Exception.

        Example:
          >>> Fault(90, 45, slickenlines=[Slickenline(90, 45)]).slickenline()
          Slickenline(az: 90.00°, pl: 45.00°, known_dir: True, time: 0.0)
        """

        if not isinstance(ndx, numbers.Integral):
            raise Exception("Slickenline index must be integer")

        if not self._slicks:
            raise Exception("No slickenline defined for current Fault instance")
        elif ndx > len(self._slicks) - 1:
            raise Exception("Slickenline index is greater than slickenlines number")
        else:
            return self._slicks[ndx]

    def slickenline_geometry(self,
                             ndx: numbers.Integral = 0
                             ) -> Optional[Direct]:
        """
        Return the geometric object (Direct or Axis) associated with slickenline.

        Example:
          >>> Fault(90, 45, slickenlines=[Slickenline(90, 45)]).slickenline_geometry()
          Direct(az: 90.00°, pl: 45.00°)
        """

        if not self._slicks:
            raise Exception("No slickenline defined for current Fault instance")
        elif ndx > len(self._slicks) - 1:
            raise Exception("Slickenline index is greater than slickenlines number")
        else:
            return self._slicks[ndx].geom

    def has_known_sense(self,
                        ndx: numbers.Integral = 0
                        ) -> Optional[bool]:
        """
        Check if the Slick instance in the Fault instance has a known movement sense.

        Example:
          >>> Fault(90, 45, slickenlines=[Slickenline(90, 45, known=False)]).has_known_sense()
          False
          >>> Fault(90, 45, slickenlines=[Slickenline(90, 45)]).has_known_sense()
          True
        """

        if not self._slicks:
            return None
        elif ndx > len(self._slicks) - 1:
            raise Exception("Slickenline index is greater than slickenlines number")
        else:
            return self._slicks[ndx].has_known_sense()

    def rake(self,
        ndx: numbers.Integral = 0
    ) -> numbers.Real:
        """
        Calculates the rake (sensu Aki & Richards, 1980) of the slickenline with the given index.
        The slickenlines must have known sense movement.

        :return: the rake value

        Examples:
          >>> Fault(180, 45, slickenlines=[Slickenline(90, 0)]).rake()
          0.0
          >>> Fault(180, 45, slickenlines=[Slickenline(0, -45)]).rake()
          90.0
          >>> Fault(180, 45, slickenlines=[Slickenline(270, 0)]).rake()
          180.0
          >>> Fault(180, 45, slickenlines=[Slickenline(180, 45)]).rake()
          -90.0
          >>> Fault(180, 45, slickenlines=[Slickenline(180, 45, known=False)]).rake()
          Traceback (most recent call last):
          ...
          Exception: Slickeline must have known movement sense
          >>> Fault(90, 90, slickenlines=[Slickenline(0, 0)]).rake()
          0.0
          >>> Fault(90, 90, slickenlines=[Slickenline(90, 90)]).rake()
          -90.0
          >>> Fault(90, 90, slickenlines=[Slickenline(90, -90)]).rake()
          90.0
          >>> Fault(90, 90, slickenlines=[Slickenline(180, 1)]).rake()
          -179.0000000000001
          >>> Fault(90, 90, slickenlines=[Slickenline(180, -1)]).rake()
          179.0000000000001
          >>> Fault(90, 90, slickenlines=[Slickenline(0, 0)]).rake()
          0.0
          >>> Fault(0, 90, slickenlines=[Slickenline(90, 30)]).rake()
          -150.0
          >>> Fault(45, 90, slickenlines=[Slickenline(135, 0)]).rake()
          180.0
          >>> Fault(90, 90, slickenlines=[Slickenline(0, 20)]).rake()
          -19.999999999999993
          >>> Fault(90, 90, slickenlines=[Slickenline(180, 40)]).rake()
          -140.00000000000003
        """

        if not self.has_known_sense(ndx):
            raise Exception("Slickeline must have known movement sense")

        sl_gv = self.slickenline_geometry(ndx)
        angle = sl_gv.angle_with(self.plane.rhr_strike_direction())

        if self.plane.dip_dir_orien().angle_with(sl_gv) < 90.0:
            return -angle
        else:
            return angle

    def rake_to_slickenline(self,
        rake: numbers.Real) -> Tuple[Union[type(None), Slickenline], Error]:
        """
        Given a rake value, calculates the corresponding slickenline.

        :param rake: the rake of the slickenline.
        :return: the potential slickenline and the error status.
        """

        try:

            direction, err = self.plane.rake_to_direct(rake)

            if err:
                return None, err

            return Slickenline(*direction.d, known=True), Error()

        except Exception as e:

            return None, Error(True, caller_name(), e, traceback.format_exc())

    def is_normal(self,
        ndx: numbers.Integral=0,
        rk_threshold: numbers.Real = RAKE_THRESHOLD,
        dip_angle_threshold: numbers.Real = DIP_ROTAT_ANGLE_THRESH
    ) -> bool:
        """
        Checks if a fault has normal (downward) movements.

        :param ndx: slickenline index
        :param rk_threshold: the threshold, in degrees, for the rake rot_angle
        :param dip_angle_threshold: the threshold, in degrees, for the dipang rot_angle of the geological plane
        :return: True if normal, False if not applicable

        Examples:
          >>> Fault(0, 45, slickenlines=[Slickenline(0, 45)]).is_normal()
          True
          >>> Fault(0, 45, slickenlines=[Slickenline(90, 0)]).is_normal()
          False
          >>> Fault(0, 15, slickenlines=[Slickenline(180, -15)]).is_normal()
          False
          >>> Fault(0, 90, slickenlines=[Slickenline(90, 45)]).is_normal()
          False
          >>> Fault(0, 90, slickenlines=[Slickenline(270, -45)]).is_normal()
          False
        """

        if self.plane.is_very_high_angle(dip_angle_threshold) or self.plane.is_very_low_angle(dip_angle_threshold):
            return False

        if - rk_threshold >= self.rake(ndx) >= -(180.0 - rk_threshold):
            return True
        else:
            return False

    def is_reverse(self,
       ndx: numbers.Integral = 0,
       rk_threshold: numbers.Real = RAKE_THRESHOLD,
       dip_angle_threshold: numbers.Real = DIP_ROTAT_ANGLE_THRESH
    ) -> bool:
        """
        Checks if a fault has reverse movements.

        :param ndx: slickenline index
        :param rk_threshold: the threshold, in degrees, for the rake rot_angle
        :param dip_angle_threshold: the threshold, in degrees, for the dipang rot_angle of the geological plane
        :return: True if reverse, False if not applicable

        Examples:
          >>> Fault(90, 90, slickenlines=[Slickenline(0, 0)]).is_reverse()
          False
          >>> Fault(90, 90, slickenlines=[Slickenline(90, 90)]).is_reverse()
          False
          >>> Fault(90, 45, slickenlines=[Slickenline(0, 0)]).is_reverse()
          False
          >>> Fault(90, 45, slickenlines=[Slickenline(270, -45)]).is_reverse()
          True
          >>> Fault(90, 45, slickenlines=[Slickenline(90, 45)]).is_reverse()
          False
        """

        if self.plane.is_very_high_angle(dip_angle_threshold) or self.plane.is_very_low_angle(dip_angle_threshold):
            return False

        if rk_threshold <= self.rake(ndx) <= (180.0 - rk_threshold):
            return True
        else:
            return False

    def is_right_lateral(self,
        ndx: numbers.Integral = 0,
        rk_threshold: numbers.Real = RAKE_THRESHOLD,
        dip_angle_threshold: numbers.Real = DIP_ROTAT_ANGLE_THRESH
    ) -> bool:
        """
        Checks if a fault has right-lateral movements.

        :param ndx: slickenline index
        :param rk_threshold: the threshold, in degrees, for the rake rot_angle
        :param dip_angle_threshold: the threshold, in degrees, for the dipang rot_angle of the geological plane
        :return: True if right-lateral, False if not applicable

        Examples:
          >>> Fault(90, 90, slickenlines=[Slickenline(0, 0)]).is_right_lateral()
          False
          >>> Fault(90, 90, slickenlines=[Slickenline(180, 0)]).is_right_lateral()
          True
          >>> Fault(90, 45, slickenlines=[Slickenline(0, 0)]).is_right_lateral()
          False
          >>> Fault(90, 45, slickenlines=[Slickenline(180, 0)]).is_right_lateral()
          True
          >>> Fault(90, 45, slickenlines=[Slickenline(270, -45)]).is_right_lateral()
          False
          >>> Fault(90, 2, slickenlines=[Slickenline(180, 0)]).is_right_lateral()
          False
        """

        if self.plane.is_very_low_angle(dip_angle_threshold):
            return False

        rake = self.rake(ndx)
        if rake >= (90.0 + rk_threshold) or rake <= (-90.0 - rk_threshold):
            return True
        else:
            return False

    def is_left_lateral(self,
        ndx: numbers.Integral = 0,
        rk_threshold: numbers.Real = RAKE_THRESHOLD,
        dip_angle_threshold: numbers.Real = DIP_ROTAT_ANGLE_THRESH
    ) -> bool:
        """
        Checks if a fault has left-lateral movements.

        :param ndx: slickenline index
        :param rk_threshold: the threshold, in degrees, for the rake rot_angle
        :param dip_angle_threshold: the threshold, in degrees, for the dipang rot_angle of the geological plane
        :return: True if left-lateral, False if not applicable

        Examples:
          >>> Fault(90, 90, slickenlines=[Slickenline(0, 0)]).is_left_lateral()
          True
          >>> Fault(90, 90, slickenlines=[Slickenline(180, 0)]).is_left_lateral()
          False
          >>> Fault(90, 45, slickenlines=[Slickenline(0, 0)]).is_left_lateral()
          True
          >>> Fault(90, 45, slickenlines=[Slickenline(180, 0)]).is_left_lateral()
          False
          >>> Fault(90, 45, slickenlines=[Slickenline(270, -45)]).is_left_lateral()
          False
          >>> Fault(90, 2, slickenlines=[Slickenline(0, 0)]).is_left_lateral()
          False
        """

        if self.plane.is_very_low_angle(dip_angle_threshold):
            return False

        if (-90.0 + rk_threshold) <= self.rake(ndx) <= (90.0 - rk_threshold):
            return True
        else:
            return False


if __name__ == "__main__":

    import doctest
    doctest.testmod()
