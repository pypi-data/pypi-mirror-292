
from array import array

from geogst.core.geology.faults import *
from geogst.core.inspections.errors import *
from geogst.core.utils.types import *


class PointTrace:
    """
    Represents a point projected onto a vertical section.
    """

    def __init__(
        self,
        s: numbers.Real,
        z: numbers.Real,
        dist: numbers.Real,
    ):
        """
        :param s: the signed horizontal plane location along the profile.
        :param z: the height of the plane point location in the profile.
        :param dist: the distance between the source point and the point projection on the profile.
        """

        self.s = s
        self.z = z
        self.dist = dist

    def __repr__(self) -> str:
        """
        Creates the representation of a PointTrace instance.

        :return: the representation of a PointTrace instance.
        """

        return f"PointTrace(s={self.s:.2f}, z={self.z:.2f}, dist={self.dist:.2f})"

    def shift_by_s(
        self,
        shift_value: numbers.Real) -> 'PointTrace':
        """
        Shifts a point trace by the given value along the profile direction.

        :param shift_value: the shift value to apply.
        :returns: the shifted point trace.
        """

        return PointTrace(
            self.s + shift_value,
            self.z,
            self.dist,
        )


class PlaneTrace:
    """
    Represents a plane projected onto/intersected by a vertical section,
    expressed by a selected location of the plane onto the section,
    as well as its intersecting and original attitude.
    """

    def __init__(
        self,
        s: numbers.Real,
        z: numbers.Real,
        slope_degr: numbers.Real,
        down_sense: str,
        dist: numbers.Real,
        src_dip_dir: numbers.Real,
        src_dip_ang: numbers.Real
    ):
        """
        :param s: the signed horizontal plane location along the profile.
        :param z: the height of the plane point location in the profile.
        :param slope_degr: the slope of the plane attitude in the profile. Unit is degrees.
        :param down_sense: downward sense, to the right or to the profile left.
        :param dist: the distance between the plane attitude point and the point projection on the profile.
        :param src_dip_dir: plane source dip direction.
        :param src_dip_ang: plane source dip angle.
        """

        self.s = s
        self.z = z
        self.slope_degr = slope_degr
        self.down_sense = down_sense
        self.dist = dist
        self.src_dip_dir = src_dip_dir
        self.src_dip_ang = src_dip_ang

    def __repr__(self) -> str:
        """
        Creates the representation of a PlaneTrace instance.

        :return: the representation of a PlaneTrace instance.
        """

        return f"PlaneTrace(s={self.s:.2f}, z={self.z:.2f}, " \
               f"dip_angle={self.slope_degr:.2f}, down_sense={self.down_sense}, " \
               f"dist={self.dist:.2f}, src_dip_dir={self.src_dip_dir:.2f}, src_dip_ang={self.src_dip_ang:.2f})"

    def shift_by_s(
        self,
        shift_value: numbers.Real) -> 'PlaneTrace':
        """
        Shifts a plane attitude by the given value along the profile direction.

        :param shift_value: the shift value to apply.
        :returns: the shifted plane attitude.
        """

        return PlaneTrace(
            self.s + shift_value,
            self.z,
            self.slope_degr,
            self.down_sense,
            self.dist,
            self.src_dip_dir,
            self.src_dip_ang,
        )

    def create_segment_for_plot(
            self,
            profile_length: numbers.Real,
            vertical_exaggeration: numbers.Real = 1,
            segment_scale_factor: numbers.Real = 50.0):
        """

        :param profile_length:
        :param vertical_exaggeration:
        :param segment_scale_factor: the (inversely proportional) scale factor controlling the plane_attitude segment length in the plot.
        :return:
        """

        ve = float(vertical_exaggeration)

        z0 = self.z

        h_dist = self.s
        slope_rad = radians(self.slope_degr)
        intersection_downward_sense = self.down_sense
        length = profile_length / segment_scale_factor

        s_slope = sin(float(slope_rad))
        c_slope = cos(float(slope_rad))

        if c_slope == 0.0:
            height_corr = length / ve
            structural_segment_s = [h_dist, h_dist]
            structural_segment_z = [z0 + height_corr, z0 - height_corr]
        else:
            t_slope = s_slope / c_slope
            width = length * c_slope

            length_exag = width * sqrt(1 + ve*ve * t_slope*t_slope)

            corr_width = width * length / length_exag
            corr_height = corr_width * t_slope

            structural_segment_s = [h_dist - corr_width, h_dist + corr_width]
            structural_segment_z = [z0 + corr_height, z0 - corr_height]

            if intersection_downward_sense == "left":
                structural_segment_z = [z0 - corr_height, z0 + corr_height]

        return structural_segment_s, structural_segment_z


class PlaneTrace2D:
    """
    Represents a plane intersected by a vertical section,
    expressed by a selected location of the plane onto the section,
    as well as its intersecting and original attitude.
    """

    def __init__(
        self,
        s: numbers.Real,
        slope_degr: numbers.Real,
        down_sense: str,
        src_dip_dir: numbers.Real,
        src_dip_ang: numbers.Real
    ):
        """
        :param s: the signed horizontal plane location along the profile.
        :param slope_degr: the slope of the plane attitude in the profile. Unit is degrees.
        :param down_sense: downward sense, to the right or to the profile left.
        :param src_dip_dir: plane source dip direction.
        :param src_dip_ang: plane source dip angle.
        """

        self.s = s
        self.slope_degr = slope_degr
        self.down_sense = down_sense
        self.src_dip_dir = src_dip_dir
        self.src_dip_ang = src_dip_ang

    def __repr__(self) -> str:
        """
        Creates the representation of a PlaneTrace2D instance.

        :return: the representation of a PlaneTrace2D instance.
        """

        return f"PlaneTrace2D(s={self.s:.2f}, " \
               f"dip_angle={self.slope_degr:.2f}, down_sense={self.down_sense}, " \
               f"src_dip_dir={self.src_dip_dir:.2f}, src_dip_ang={self.src_dip_ang:.2f})"

    def shift_by_s(
        self,
        shift_value: numbers.Real) -> 'PlaneTrace2D':
        """
        Shifts a plane attitude by the given value along the profile direction.

        :param shift_value: the shift value to apply.
        :returns: the shifted plane attitude.
        """

        return PlaneTrace2D(
            self.s + shift_value,
            self.slope_degr,
            self.down_sense,
            self.src_dip_dir,
            self.src_dip_ang,
        )

    def create_segment_for_plot(
            self,
            profile_length: numbers.Real,
            z0: numbers.Real,
            vertical_exaggeration: numbers.Real = 1,
            segment_scale_factor: numbers.Real = 50.0):
        """

        :param profile_length:
        :param z0: the elevation of the observation.
        :param vertical_exaggeration:
        :param segment_scale_factor: the (inversely proportional) scale factor controlling the plane_attitude segment length in the plot.
        :return:
        """

        ve = float(vertical_exaggeration)

        h_dist = self.s
        slope_rad = radians(self.slope_degr)
        intersection_downward_sense = self.down_sense
        length = profile_length / segment_scale_factor

        s_slope = sin(float(slope_rad))
        c_slope = cos(float(slope_rad))

        if c_slope == 0.0:
            height_corr = length / ve
            structural_segment_s = [h_dist, h_dist]
            structural_segment_z = [z0 + height_corr, z0 - height_corr]
        else:
            t_slope = s_slope / c_slope
            width = length * c_slope

            length_exag = width * sqrt(1 + ve*ve * t_slope*t_slope)

            corr_width = width * length / length_exag
            corr_height = corr_width * t_slope

            structural_segment_s = [h_dist - corr_width, h_dist + corr_width]
            structural_segment_z = [z0 + corr_height, z0 - corr_height]

            if intersection_downward_sense == "left":
                structural_segment_z = [z0 - corr_height, z0 + corr_height]

        return structural_segment_s, structural_segment_z


class FaultTrace:
    """
    Represents a fault projected onto a vertical section,
    expressed by a selected location of the plane onto the section,
    as well as the fault attitude.
    """

    def __init__(
        self,
        s: numbers.Real,
        z: numbers.Real,
        fault: Fault
    ):
        """
        :param s: the signed horizontal plane location along the profile.
        :param z: the height of the plane point location in the profile.
        :param fault: the projected fault.
        """

        self.s = s
        self.z = z
        self.fault = fault

    def __repr__(self) -> str:
        """
        Creates the representation of a FaultTrace instance.

        :return: the representation of a FaultTrace instance.
        :rtype: str.
        """

        return f"FaultTrace(s={self.s:.2f}, z={self.z:.2f}, fault={self.fault})"

    def shift_by_s(
        self,
        shift_value: numbers.Real) -> 'FaultTrace':
        """
        Shifts a fault projection by the given value along the profile direction.

        :param shift_value: the shift value to apply.
        :returns: the shifted fault projection.
        """

        return FaultTrace(
            self.s + shift_value,
            self.z,
            self.fault,
        )

class ZTrace:
    """
    Represent an x-y array pair (i.e., a single y value for each x value).
    X values should be sorted and should start from zero.
    """

    def __init__(self,
                 x_array: Union[array, np.ndarray],
                 y_array: Union[array, np.ndarray],
                 breaks: Optional[Union[array, np.ndarray]] = None,
                 name: str = "undefined"
                 ):
        """
        Constructor.

        :param x_array: the x values array.
        :param y_array: the y values array.
        :param breaks: the internal x breaks.
        """

        check_type(x_array, "X array", (array, np.ndarray))

        if not np.all(np.isfinite(x_array)):
            raise Exception("X array values must all be finite")

        check_type(y_array, "Y array", (array, np.ndarray))
        if breaks is not None:
            check_type(breaks, "X breaks", (array, np.ndarray))

        if len(y_array) != len(x_array):
            raise Exception("Y array must have the same length as x array")

        if x_array[0] != 0.0:
            raise Exception("First value of X array should be zero")

        # from: https://stackoverflow.com/questions/47004506/check-if-a-numpy-array-is-sorted
        # answer by: luca
        is_sorted = lambda a: np.all(a[:-1] <= a[1:])

        if not is_sorted(x_array):
            raise Exception("X array must be already sorted")

        if breaks is not None:
            if breaks[0] != 0.0:
                raise Exception("First element of X breaks must always be zero")

        self._x = np.array(x_array, dtype=np.float64)
        self._y = np.array(y_array, dtype=np.float64)
        self._x_breaks = np.array(breaks, dtype=np.float64) if breaks is not None else np.array([x_array[0], x_array[-1]])
        self._name = name

    def clone(self) -> 'ZTrace':
        """
        Clone the ZTrace instance.
        """

        return ZTrace(
            x_array=np.copy(self._x),
            y_array=np.copy(self._y),
            breaks=None if self._x_breaks is None else np.copy(self._x_breaks)
        )

    def x_arr(self) -> np.ndarray:
        """
        Return the x array.

        :return: the x array.
        :rtype: array.
        """

        return self._x

    def y_arr(self) -> np.ndarray:
        """
        Return the y array.

        :return: the y array.
        """

        return self._y

    def x_breaks(self) -> Optional[np.ndarray]:

        return self._x_breaks

    def name(self) -> str:

        return self._name

    def __repr__(self) -> str:
        """
        Representation of a topographic profile instance.

        :return: the textual representation of the instance.
        :rtype: str.
        """

        return f"ZTrace with {len(self.x_arr())} nodes\nx = {self._x},\ny = {self._y}"

    def num_steps(self) -> numbers.Integral:
        """
        Return the number of steps in the array pair.

        :return: number of steps in the array pair.
        """

        return len(self._x)

    def x(self,
          ndx: numbers.Integral
          ) -> numbers.Real:
        """
        Returns the x value with the index ndx.

        :param ndx: the index in the x array
        :return: the s value corresponding to the ndx index
        """

        return self._x[ndx]

    def y(self,
          ndx: numbers.Integral
          ) -> numbers.Real:
        """
        Returns the y value with the index ndx.

        :param ndx: the index in the y array
        :return: the y value corresponding to the ndx index
        """

        return self._y[ndx]

    def x_min(self) -> numbers.Real:
        """
        Returns the minimum x value.

        :return: the minimum x value.
        """

        return np.nanmin(self._x)

    def x_max(self) -> numbers.Real:
        """
        Returns the maximum x value.

        :return: the maximum x value.
        """

        return np.nanmax(self._x)

    def y_min(self) -> numbers.Real:
        """
        Returns the minimum y value.

        :return: the minimum y value.
        """

        return np.nanmin(self._y)

    def y_max(self) -> numbers.Real:
        """
        Returns the maximum y value.

        :return: the maximum y value.
        :rtype: numbers.Real.
        """

        return np.nanmax(self._y)

    def x_length(self) -> numbers.Real:
        """
        Returns the geographic length of the profile.

        :return: length of profile.
        :rtype: numbers.Real.
        """

        return self._x[-1]

    def find_index_ge(self,
      x_val: numbers.Real):
        """

        Examples:
          >>> p = ZTrace(array('d', [ 0.0,  1.0,  2.0,  3.0, 3.14]), array('d', [10.0, 20.0, 0.0, 14.5, 17.9]))
          >>> p.find_index_ge(-1)
          0
          >>> p.find_index_ge(0.0)
          0
          >>> p.find_index_ge(0.5)
          1
          >>> p.find_index_ge(0.75)
          1
          >>> p.find_index_ge(1.0)
          1
          >>> p.find_index_ge(2.0)
          2
          >>> p.find_index_ge(2.5)
          3
          >>> p.find_index_ge(3.08)
          4
          >>> p.find_index_ge(3.14)
          4
          >>> p.find_index_ge(5) is None
          True
        """

        check_type(x_val, "X value", numbers.Real)
        if not np.isfinite(x_val):
            raise Exception(f"X value must be finite but {x_val} got")

        if x_val <= self.x_min():
            return 0
        elif x_val > self.x_max():
            return None
        else:
            return np.argmax(self._x >= x_val)

    def x_upper_ndx(self,
                    x_val: numbers.Real
                    ) -> Optional[numbers.Integral]:
        """
        To be possibly deprecated.
        Returns the optional index in the x array of the provided value.

        :param x_val: the value to search the index for in the x array
        :return: the optional index in the s array of the provided value

        Examples:
          >>> p = ZTrace(array('d', [ 0.0,  1.0,  2.0,  3.0, 3.14]), array('d', [10.0, 20.0, 0.0, 14.5, 17.9]))
          >>> p.x_upper_ndx(-1) is None
          True
          >>> p.x_upper_ndx(5) is None
          True
          >>> p.x_upper_ndx(0.5)
          1
          >>> p.x_upper_ndx(0.75)
          1
          >>> p.x_upper_ndx(1.0)
          1
          >>> p.x_upper_ndx(2.0)
          2
          >>> p.x_upper_ndx(2.5)
          3
          >>> p.x_upper_ndx(3.11)
          4
          >>> p.x_upper_ndx(3.14)
          4
          >>> p.x_upper_ndx(0.0)
          0
        """

        check_type(x_val, "Input value", numbers.Real)

        if x_val < self.x_min() or x_val > self.x_max():
            return None

        return np.searchsorted(self._x, x_val)

    def y_linear_interpol(self,
                          x_val: numbers.Real
                          ) -> Optional[numbers.Real]:
        """
        Returns the optional interpolated z value in the z array of the provided s value.

        :param x_val: the value to search the index for in the s array
        :return: the optional interpolated z value

        Examples:
          >>> p = ZTrace(array('d', [ 0.0,  1.0,  2.0,  3.0, 3.14]), array('d', [10.0, 20.0, 0.0, 14.5, 17.9]))
          >>> p.y_linear_interpol(-1) is None
          True
          >>> p.y_linear_interpol(5) is None
          True
          >>> p.y_linear_interpol(0.5)
          15.0
          >>> p.y_linear_interpol(0.75)
          17.5
          >>> p.y_linear_interpol(2.5)
          7.25
          >>> p.y_linear_interpol(3.14)
          17.9
          >>> p.y_linear_interpol(0.0)
          10.0
          >>> p.y_linear_interpol(1.0)
          20.0
        """

        check_type(x_val, "Input value", numbers.Real)

        ndx = self.x_upper_ndx(x_val)

        if ndx is not None:

            if ndx == 0:
                return self.y(0)

            val_y_i = self.y(ndx - 1)
            val_y_i_next = self.y(ndx)
            delta_val_y = val_y_i_next - val_y_i

            if delta_val_y == 0.0:
                return val_y_i

            val_x_i = self.x(ndx - 1)
            val_x_i_next = self.x(ndx)
            delta_val_x = val_x_i_next - val_x_i

            if delta_val_x == 0.0:
                return val_y_i

            d_x = x_val - val_x_i

            return val_y_i + d_x * delta_val_y / delta_val_x

        else:

            return None

    def x_subset(self,
                 x_start: numbers.Real,
                 x_end: Optional[numbers.Real] = None
                 ) -> Optional[np.ndarray]:
        """
        Return the x array values defined by the provided x range (extremes included).
        When the end value is not provided, a single-valued array is returned.

        :param x_start: the start x value (distance along the profile)
        :param x_end: the optional end x value (distance along the profile)
        :return: the s array subset, possibly with just a value

        Examples:
          >>> p = ZTrace(array('d', [ 0.0,  1.0,  2.0,  3.0, 3.14]), array('d', [10.0, 20.0, 0.0, 14.5, 17.9]))
          >>> p.x_subset(1.0)
          array([1.])
          >>> p.x_subset(0.0)
          array([0.])
          >>> p.x_subset(0.75)
          array([0.75])
          >>> p.x_subset(3.14)
          array([3.14])
          >>> p.x_subset(1.0, 2.0)
          array([1., 2.])
          >>> p.x_subset(0.75, 2.0)
          array([0.75, 1.  , 2.  ])
          >>> p.x_subset(0.75, 2.5)
          array([0.75, 1.  , 2.  , 2.5 ])
          >>> p.x_subset(0.75, 3.0)
          array([0.75, 1.  , 2.  , 3.  ])
          >>> p.x_subset(-1, 1)
          array([0., 1.])
          >>> p.x_subset(-1) is None
          True
          >>> p.x_subset(0.0, 10)
          array([0.  ,  1.  ,  2.  ,  3.  , 3.14])
          >>> p.x_subset(0.0, 3.14)
          array([0.  ,  1.  ,  2.  ,  3.  , 3.14])
        """

        # input data validity checks

        check_type(x_start, "Start x value", numbers.Real)
        if x_end is not None:
            check_type(x_end, "End x value", numbers.Real)

        if x_end is not None and x_end < x_start:
            raise Exception(f"Start is {x_start} while end is {x_end}")

        # result for single input value

        if x_end is None:
            if not self.x_min() <= x_start <= self.x_max():
                return None
            else:
                return np.array([x_start], dtype=np.float64)

        if x_start > self.x_max() or x_end < self.x_min():
            return None

        # fix ranges

        if x_start < self.x_min():
            x_start = self.x_min()
        if x_end > self.x_max():
            x_end = self.x_max()

        # particular case where start equal to end

        if x_end == x_start:
            return np.array([x_start], dtype=np.float64)

        # general case for x start < x end

        values = []

        s_start_upper_index_value = self.x_upper_ndx(x_start)

        if x_start < self.x(s_start_upper_index_value):
            values.append(x_start)

        s_end_upper_index_value = self.x_upper_ndx(x_end)

        for ndx in range(s_start_upper_index_value, s_end_upper_index_value):
            values.append(self.x(ndx))

        if x_end > self.x(s_end_upper_index_value - 1):
            values.append(x_end)

        return np.array(values, dtype=np.float64)

    def ys_from_x_range(self,
                        x_start: numbers.Real,
                        x_end: Optional[numbers.Real] = None
                        ) -> Optional[np.ndarray]:
        """
        Return the y array values defined by the provided x range (extremes included).
        When the end value is not provided, a single-valued array is returned.

        :param x_start: the start x value (distance along the profile)
        :param x_end: the optional end x value (distance along the profile)
        :return: the y array, possibly with just a value

        Examples:
          >>> p = ZTrace(array('d', [ 0.0,  1.0,  2.0,  3.0, 3.14]), array('d', [10.0, 20.0, 0.0, 14.5, 17.9]))
          >>> p.ys_from_x_range(1.0)
          array([20.])
          >>> p.ys_from_x_range(0.0)
          array([10.])
          >>> p.ys_from_x_range(0.75)
          array([17.5])
          >>> p.ys_from_x_range(3.14)
          array([17.9])
          >>> p.ys_from_x_range(1.0, 2.0)
          array([20., 0.])
          >>> p.ys_from_x_range(0.75, 2.0)
          array([17.5, 20. , 0. ])
          >>> p.ys_from_x_range(0.75, 2.5)
          array([17.5 , 20.  , 0.  , 7.25])
          >>> p.ys_from_x_range(0.75, 3.0)
          array([17.5, 20. , 0. , 14.5])
          >>> p.ys_from_x_range(-1, 1)
          array([10., 20.])
          >>> p.ys_from_x_range(-1) is None
          True
          >>> p.ys_from_x_range(0.0, 10)
          array([10. , 20. , 0. , 14.5, 17.9])
          >>> p.ys_from_x_range(0.0, 3.14)
          array([10. , 20. , 0. , 14.5, 17.9])
        """

        s_subset = self.x_subset(x_start, x_end)

        if s_subset is None:
            return None

        return np.array(list(map(self.y_linear_interpol, s_subset)), dtype=np.float64)

    def extend_in_place(self,
               another: 'ZTrace'
               ):
        """
        Extend an ZTrace instance in-place.
        Note that the last element of the first x-y array pair will be dropped
        and substituted by the first element of the second x-y array pair
        (no attempt to check values equality or to calculate a mean).
        Moverover, all the x values of the second x-y array pair will be incremented
        by the last x value of the first element.

        Examples:
          >>> f = ZTrace(np.array([ 0.0,  14.2,  20.0]), np.array([149.17, 132.4, 159.2]))
          >>> f.x_breaks()
          array([ 0., 20.])
          >>> f.x_max()
          20.0
          >>> s = ZTrace(np.array([ 0.0,  7.0,  11.0]), np.array([159.17, 180.1, 199.5]))
          >>> s.x_breaks()
          array([ 0., 11.])
          >>> s.x_breaks() + f.x_max()
          array([20., 31.])
          >>> f.extend_in_place(s)
          >>> f.x_arr()
          array([ 0. ,  14.2,  20. , 27. , 31. ])
          >>> f.y_arr()
          array([149.17, 132.4 , 159.17, 180.1 , 199.5 ])
          >>> f.x_breaks()
          array([ 0., 20., 31.])
        """

        check_type(another, "Second ZTrace instance", ZTrace)

        offset = self.x_max()
        self._x = np.append(self._x[:-1], another._x + offset)
        self._y = np.append(self._y[:-1], another._y)
        self._x_breaks = np.append(self._x_breaks[:-1], another._x_breaks + offset)

    def dir_slopes_deltas(self) -> Tuple[np.ndarray, np.ndarray]:

        delta_x = np.ediff1d(self._x, to_end=np.nan)
        delta_y = np.ediff1d(self._y, to_end=np.nan)

        return delta_x, delta_y

    def dir_slopes_ratios(self) -> np.ndarray:

        dx, dy = self.dir_slopes_deltas()

        return dy / dx

    def dir_slopes_percent(self) -> np.ndarray:

        return 100.0 * self.dir_slopes_ratios()

    def dir_slopes_radians(self) -> np.ndarray:

        dx, dy = self.dir_slopes_deltas()

        return np.arctan2(dy, dx)

    def dir_slopes_degrees(self) -> np.ndarray:

        return self.dir_slopes_radians() * 180.0 / np.pi

    def as_dir_slopes_degrees(self) -> 'ZTrace':

        return ZTrace(
            x_array=self._x,
            y_array=self.dir_slopes_degrees(),
            breaks=self._x_breaks
        )

    def as_abs_slopes_degrees(self) -> 'ZTrace':

        return ZTrace(
            x_array=self._x,
            y_array=np.fabs(self.dir_slopes_degrees()),
            breaks=self._x_breaks
        )


class ZTraces:
    """
    Class storing a set of z profiles.
    """

    def __init__(self,
                 s_array: np.ndarray,
                 z_array: np.ndarray,
                 s_breaks: np.ndarray):
        """
        Instantiates a topographic profile set.

        :param s_array: the 1D-array of s values.
        :param z_array: the 2D-array of z values. Can store multiple z-series.
        :param s_breaks: the 1D-array of s break values (i.e., where the profile changes direction).
        """

        check_type(s_array, "S array", np.ndarray)
        check_type(z_array, "Z array", np.ndarray)
        check_type(s_breaks, "S breaks array", np.ndarray)

        if s_array.ndim != 1:
            raise Exception(f"S array must be 1D but {s_array.ndim} got")
        if z_array.ndim != 2:
            raise Exception(f"Z array must be 2D but {z_array.ndim} got")
        if s_breaks.ndim != 1:
            raise Exception(f"S breaks array must be 1D but {s_breaks.ndim} got")

        if not np.all(s_array[1:] > s_array[:-1]):
            raise Exception(f"S array must be strictly increasing")

        num_steps = len(s_array)
        if num_steps <= 1:
            raise Exception(f"At least a two-values S array is required but {num_steps} got")

        (num_profiles, num_profs_steps) = z_array.shape
        if num_profs_steps != num_steps:
            raise Exception(f"S array has {num_steps} steps while Z array has {num_profs_steps} steps")

        self._s_array = s_array.astype(np.float64)
        self._z_array = z_array.astype(np.float64)
        self._s_breaks_array = s_breaks.astype(np.float64)

    @classmethod
    def fromProfiles(cls,
                     z_profiles: List[ZTrace]):
        """
        Instantiates a topographic profile set.

        :param z_profiles: the topographic profile set.
        """

        check_type(z_profiles, "Topographic profiles set", List)
        for el in z_profiles:
            check_type(el, "Topographic profile", ZTrace)

        return cls(
            z_profiles[0].x_arr(),
            np.array([zprof.y_arr() for zprof in z_profiles]),
            z_profiles[0].x_breaks()
        )

    def __getitem__(self,
        ndx: numbers.Integral) -> ZTrace:
        """
        Returns the profile with the given index.
        """

        return self.make_ztrace_from_arr(self._z_array[ndx])

    def num_profiles(self) -> int:
        """
        Returns the number of profiles.
        """

        return self._z_array.shape[0]

    def s_breaks(self) -> np.ndarray:
        """
        Returns a copy of the S breaks array.
        """

        return np.copy(self._s_breaks_array)

    def s_min(self) -> float:
        """
        Returns the minimum s value in the topographic profiles.

        :return: the minimum s value in the profiles.
        """

        return float(self._s_array[0])

    def s_max(self) -> float:
        """
        Returns the maximum s value in the topographic profiles.

        :return: the maximum s value in the profiles.
        :rtype: optional numbers.Real.
        """

        return float(self._s_array[-1])

    def z_min(self) -> Optional[numbers.Real]:
        """
        Returns the minimum elevation value in the topographic profiles.

        :return: the minimum elevation value in the profiles.
        :rtype: optional numbers.Real.
        """

        return np.nanmin(self._z_array)

    def z_max(self) -> Optional[numbers.Real]:
        """
        Returns the maximum elevation value in the topographic profiles.

        :return: the maximum elevation value in the profiles.
        :rtype: optional numbers.Real.
        """

        return np.nanmax(self._z_array)

    def natural_elev_range(self) -> Tuple[numbers.Real, numbers.Real]:
        """
        Returns the elevation range of the profiles.

        :return: minimum and maximum values of the considered topographic profiles.
        :rtype: tuple of two floats.
        """

        return self.z_min(), self.z_max()

    def topoprofiles_params(self):
        """

        :return:
        """

        return self.s_min(), self.s_max(), self.z_min(), self.z_max()

    def max_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles max values.
        """

        return np.nanmax(self._z_array, axis=0)

    def min_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles min values.
        """

        return np.nanmin(self._z_array, axis=0)

    def mean_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles mean values.
        """

        return np.nanmean(self._z_array, axis=0)

    def median_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles median values.
        """

        return np.nanmedian(self._z_array, axis=0)

    def var_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles var values.
        """

        return np.nanvar(self._z_array, axis=0)

    def std_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles std values.
        """

        return np.nanstd(self._z_array, axis=0)

    def range_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles range values.
        """

        return np.ptp(self._z_array, axis=0)

    def middle_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles range values.
        """

        return self.min_arr() + 0.5 * self.range_arr()

    def make_ztrace_from_arr(self,
                             arr: np.ndarray) -> ZTrace:
        """
        Creates an ZTrace instance given a 1D z array.

        :param arr: the array representing the z values.
        :return: a new ZTrace
        """

        return ZTrace(
            self._s_array,
            arr,
            self._s_breaks_array
        )

    def profile_max(self) -> ZTrace:
        """
        Creates a profile of the max values.
        """

        return self.make_ztrace_from_arr(self.max_arr())

    def profile_min(self) -> ZTrace:
        """
        Creates a profile of the min values.
        """

        return self.make_ztrace_from_arr(self.min_arr())

    def profile_mean(self) -> ZTrace:
        """
        Creates a profile of the mean values.
        """

        return self.make_ztrace_from_arr(self.mean_arr())

    def profile_median(self) -> ZTrace:
        """
        Creates a profile of the median values.
        """

        return self.make_ztrace_from_arr(self.median_arr())

    def profile_std(self) -> ZTrace:
        """
        Creates a profile of the std values.
        """

        return self.make_ztrace_from_arr(self.std_arr())

    def profile_var(self) -> ZTrace:
        """
        Creates a profile of the var values.
        """

        return self.make_ztrace_from_arr(self.var_arr())

    def profile_range(self) -> ZTrace:
        """
        Creates a profile of the range values.
        """

        return self.make_ztrace_from_arr(self.range_arr())

    def profile_middle(self) -> ZTrace:
        """
        Creates a profile of the middle values.
        """

        return self.make_ztrace_from_arr(self.middle_arr())


def join_ztraces(
        *ztraces: ZTrace
) -> Tuple[Union[type(None), ZTrace], Error]:
    """
    Combines a tuple of ZTrace instances into an extended single ZTrace instance.

    Examples:
      >>> f = ZTrace(np.array([ 0.0,  14.2,  20.0]), np.array([149.17, 132.4, 159.2]))
      >>> s = ZTrace(np.array([ 0.0,  7.0,  11.0]), np.array([159.17, 180.1, 199.5]))
      >>> t = ZTrace(np.array([ 0.0,  22.0,  30.0]), np.array([199.5, 200.1, 179.1]))
      >>> combined, err = join_ztraces(f, s, t)
      >>> combined.x_arr()
      array([ 0. ,  14.2, 20. , 27. , 31. , 53. , 61. ])
      >>> combined.y_arr()
      array([149.17, 132.4 , 159.17, 180.1 , 199.5 , 200.1 , 179.1 ])
      >>> combined.x_breaks()
      array([ 0., 20., 31., 61.])
    """

    try:

        if len(ztraces) == 0:
            return None, Error(True, caller_name(), Exception("Length of ztraces is zero"), traceback.format_exc())

        combined_xy_arrays = ztraces[0].clone()

        for xy_array_pair in ztraces[1:]:
            combined_xy_arrays.extend_in_place(xy_array_pair)

        return combined_xy_arrays, Error()

    except Exception as e:

        return None, Error(True, caller_name(), e, traceback.format_exc())


class ZArray:
    """
    Class storing a set of z profiles as arrays.
    Possible candidate substitute for ZTraces.
    """

    def __init__(self):

        self._s_array = None
        self._z_array = None
        self._s_breaks_array = None
        self._names = []

    def add_profile(self,
        z_trace: ZTrace,
        name: str = "undefined"):

        if self._s_array is None:
            self._s_array = z_trace.x_arr()

        if self._z_array is None:
            self._z_array = np.expand_dims(z_trace.y_arr(), axis=0)
        else:
            self._z_array = np.vstack((self._z_array, z_trace.y_arr()))

        if self._s_breaks_array is None:
            self._s_breaks_array = z_trace.x_breaks()

        self._names.append(name)

    def __getitem__(self,
        ndx: numbers.Integral) -> ZTrace:
        """
        Returns the profile with the given index.
        """

        return ZTrace(
            self._s_array,
            self._z_array[ndx, :],
            self._s_breaks_array,
            self._names[ndx]
        )

    def make_ztrace_from_arr(self,
        arr: np.ndarray,
        name: str = "undefined"
    ) -> ZTrace:
        """
        Creates an ZTrace instance given a 1D z array.

        :param arr: the array representing the z values.
        :return: a new ZTrace
        """

        return ZTrace(
            self._s_array,
            arr,
            self._s_breaks_array,
            name
        )

    def num_profiles(self) -> int:
        """
        Returns the number of profiles.
        """

        return self._z_array.shape[0]

    def s_breaks(self) -> np.ndarray:
        """
        Returns a copy of the S breaks array.
        """

        return np.copy(self._s_breaks_array)

    def s_min(self) -> float:
        """
        Returns the minimum s value in the topographic profiles.

        :return: the minimum s value in the profiles.
        """

        return float(self._s_array[0])

    def s_max(self) -> float:
        """
        Returns the maximum s value in the topographic profiles.

        :return: the maximum s value in the profiles.
        :rtype: optional numbers.Real.
        """

        return float(self._s_array[-1])

    def z_min(self) -> Optional[numbers.Real]:
        """
        Returns the minimum elevation value in the topographic profiles.

        :return: the minimum elevation value in the profiles.
        :rtype: optional numbers.Real.
        """

        return np.nanmin(self._z_array)

    def z_max(self) -> Optional[numbers.Real]:
        """
        Returns the maximum elevation value in the topographic profiles.

        :return: the maximum elevation value in the profiles.
        :rtype: optional numbers.Real.
        """

        return np.nanmax(self._z_array)

    def natural_elev_range(self) -> Tuple[numbers.Real, numbers.Real]:
        """
        Returns the elevation range of the profiles.

        :return: minimum and maximum values of the considered topographic profiles.
        :rtype: tuple of two floats.
        """

        return self.z_min(), self.z_max()

    def topoprofiles_params(self):
        """

        :return:
        """

        return self.s_min(), self.s_max(), self.z_min(), self.z_max()

    def max_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles max values.
        """

        return np.nanmax(self._z_array, axis=0)

    def min_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles min values.
        """

        return np.nanmin(self._z_array, axis=0)

    def mean_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles mean values.
        """

        return np.nanmean(self._z_array, axis=0)

    def median_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles median values.
        """

        return np.nanmedian(self._z_array, axis=0)

    def var_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles var values.
        """

        return np.nanvar(self._z_array, axis=0)

    def std_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles std values.
        """

        return np.nanstd(self._z_array, axis=0)

    def range_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles range values.
        """

        return np.ptp(self._z_array, axis=0)

    def middle_arr(self) -> np.ndarray:
        """
        Return the array of the along-profiles range values.
        """

        return self.min_arr() + 0.5 * self.range_arr()

    def profile_max(self) -> ZTrace:
        """
        Creates a profile of the max values.
        """

        return self.make_ztrace_from_arr(
            self.max_arr(),
            "maximum")

    def profile_min(self) -> ZTrace:
        """
        Creates a profile of the min values.
        """

        return self.make_ztrace_from_arr(
            self.min_arr(),
            "minimum")

    def profile_mean(self) -> ZTrace:
        """
        Creates a profile of the mean values.
        """

        return self.make_ztrace_from_arr(
            self.mean_arr(),
            "mean")

    def profile_median(self) -> ZTrace:
        """
        Creates a profile of the median values.
        """

        return self.make_ztrace_from_arr(
            self.median_arr(),
            "median")

    def profile_std(self) -> ZTrace:
        """
        Creates a profile of the std values.
        """

        return self.make_ztrace_from_arr(
            self.std_arr(),
            "standard deviation")

    def profile_var(self) -> ZTrace:
        """
        Creates a profile of the var values.
        """

        return self.make_ztrace_from_arr(
            self.var_arr(),
            "variance")

    def profile_range(self) -> ZTrace:
        """
        Creates a profile of the range values.
        """

        return self.make_ztrace_from_arr(
            self.range_arr(),
            "range")

    def profile_middle(self) -> ZTrace:
        """
        Creates a profile of the middle values.
        """

        return self.make_ztrace_from_arr(
            self.middle_arr(),
            "middle")


