
import traceback

import math
import numbers
from typing import Tuple

from geogst.core.inspections.errors import *
from geogst.core.inspections.functions import *

from geogst.core.mathematics.defaults import *


def norm_xyz(
        x: numbers.Real,
        y: numbers.Real,
        z: numbers.Real,
        min_magnitude: numbers.Real = MIN_VECTOR_MAGNITUDE
) -> Tuple[Union[type(None), Tuple[numbers.Real, Tuple[numbers.Real, numbers.Real, numbers.Real]]], Error]:
    """
    Normalize three numeric values, considering them as vector Cartesian components.

    :param x: x numeric value.
    :param y: y numeric value.
    :param z: z numeric value.
    :param min_magnitude: the minimum vector magnitude to be considered meaningful.
    :return: the optional magnitude and a tuple of three float values, plus the error status.

    Examples:
      >>> result, err = norm_xyz(0.0, 0.0, 0.0)
      >>> result
      None
      >>> err
      ''
      >>> result, err = norm_xyz(math.nan, 0.0, 0.0)
      >>> result
      None
      >>> bool(err)
      True
    """

    try:

        # input vals checks

        vals = [x, y, z, min_magnitude]

        if not all(map(lambda val: isinstance(val, numbers.Real), vals)):
            raise Exception("input values must be integer or float")
        elif not all(map(math.isfinite, vals)):
            raise Exception("input values must be finite")

        mag = math.sqrt(x*x + y*y + z*z)

        if mag <= min_magnitude:
            return None, Error()
        else:
            normalized_xyz = x/mag, y/mag, z/mag
            return (mag, normalized_xyz), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc())


def almost_zero(
    val: numbers.Real,
    tolerance: numbers.Real = SCALAR_ALMOST_ZERO_TOLERANCE
):

    if abs(val) > tolerance:
        return False
    else:
        return True


def are_close(
    a: numbers.Real,
    b: numbers.Real,
    rtol: numbers.Real = SCALAR_CLOSENESS_RTOL,
    atol: numbers.Real = SCALAR_CLOSENESS_ATOL,
    equal_nan: bool = False,
    equal_inf: bool = False
) -> bool:
    """
    Mimics math.isclose from Python 3.5 (see: https://docs.python.org/3.5/library/math.html)

    Example:
      >>> are_close(1.0, 1.0)
      True
      >>> are_close(1.0, 1.000000000000001)
      True
      >>> are_close(1.0, 1.0000000001)
      False
      >>> are_close(0.0, 0.0)
      True
      >>> are_close(0.0, 0.000000000000001)
      True
      >>> are_close(0.0, 0.0000000001)
      False
      >>> are_close(100000.0, 100000.0)
      True
      >>> are_close(100000.0, 100000.0000000001)
      True
      >>> are_close(float('nan'), float('nan'))
      False
      >>> are_close(float('nan'), 1000000)
      False
      >>> are_close(1.000000000001e300, 1.0e300)
      False
      >>> are_close(1.0000000000001e300, 1.0e300)
      True
      >>> are_close(float('nan'), float('nan'), equal_nan=True)
      True
      >>> are_close(float('inf'), float('inf'))
      False
      >>> are_close(float('inf'), 1.0e300)
      False
      >>> are_close(float('inf'), float('inf'), equal_inf=True)
      True
    """

    # nan cases
    if equal_nan and math.isnan(a) and math.isnan(b):
        return True
    elif math.isnan(a) or math.isnan(b):
        return False

    # inf cases
    if equal_inf and math.isinf(a) and a > 0.0 and math.isinf(b) and b > 0.0:
        return True
    elif equal_inf and math.isinf(a) and a < 0.0 and math.isinf(b) and b < 0.0:
        return True
    elif math.isinf(a) or math.isinf(b):
        return False

    # regular case
    return abs(a - b) <= max(rtol * max(abs(a), abs(b)), atol)


def apprFloat(
    val: numbers.Real,
    ndec: numbers.Integral = 1
) -> numbers.Real:
    """
    Rounds a numeric value to ndec.

    :param val: value to round
    :param ndec: number of decimals used
    :return: rounded float value

    Examples:
      >>> apprFloat(0.00001)
      0.0
      >>> apprFloat(1.425324e-7)
      0.0
    """

    rval = round(val, ndec)
    if rval == 0.0:
        rval = round(0.0, ndec)

    return rval


def apprFTuple(
    tup: Tuple[numbers.Real, ...],
    ndec=1
) -> Tuple[numbers.Real, ...]:
    """
    Rounds numeric values inside a tuple to ndec decimals

    :param tup: tuple of numbers.Real values
    :param ndec: number of decimals used
    :return: tuple with rounded numbers

    Examples:
      >>> apprFTuple((-2.4492935982947064e-16, 1.0))
      (0.0, 1.0)
      >>> apprFTuple((-1.0, -1.8369701987210297e-16))
      (-1.0, 0.0)
    """

    return tuple(map(lambda val: apprFloat(val, ndec), tup))


if __name__ == "__main__":

    import doctest
    doctest.testmod()
