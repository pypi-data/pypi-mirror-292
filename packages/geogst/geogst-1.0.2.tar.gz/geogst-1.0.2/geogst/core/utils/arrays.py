
import warnings

from math import isfinite
import numbers
from array import array
from typing import List, Tuple

from numpy import linspace, fromfunction

from geogst.core.inspections.errors import *


class IdentifiedArrays:
    """
    An identified list of arrays.
    """

    def __init__(self,
                 rec_id: Union[str, numbers.Integral],
                 arrays: List[array]
                 ):

        self._id = rec_id
        self._arrays = arrays

    def __repr__(self):

        header = f"ArrayList(rec_id={self._id}"
        body = ""
        for part in self._arrays:
            body += f"\n{part}"

        return header + body + ")\n"

    def __iter__(self):

        return (part for part in self._arrays)

    @property
    def id(self) -> Union[str, numbers.Integral]:
        """
        Return the identified array id.

        :return: the id
        """

        return self._id

    @property
    def arrays(self) -> List[array]:
        """
        Returns the object arrays.

        :return: the instance arrays
        :rtype: List[array]
        """

        return self._arrays


def to_float(
        curr_iterable
) -> Tuple[float]:

    return tuple([float(item) for item in curr_iterable])


def almost_zero(val):
    """
    DEPRECATED: use mathematics.scalars.almost_zero
    """

    warnings.warn(
        "almost_zero is deprecated, use mathematics.utils.almost_zero instead",
        DeprecationWarning
    )

    tolerance = 1e-10
    if abs(val) > tolerance:
        return False
    else:
        return True


def formula_to_grid(array_range, array_size, formula):

    a_min, a_max, b_max, b_min = array_range  # note: b range reversed for conventional j order in arrays
    array_rows, array_cols = array_size

    a_array = linspace(a_min, a_max, num=array_cols)
    b_array = linspace(b_max, b_min, num=array_rows)  # note: reversed for conventional j order in arrays

    try:
        a_list, b_list = [a for a in a_array for _ in b_array], [b for _ in a_array for b in b_array]
    except:
        raise Exception("Error in a-b values")

    try:
        z_list = [eval(formula) for _ in a_array for _ in b_array]
    except:
        raise Exception("Error in applying formula to a and b array values")

    return a_list, b_list, z_list


def is_number(s):
    """
    Check if string can be converted to number.

    @param  s:  parameter to check.
    @type  s:  string

    @return:  boolean, whether string can be converted to a number (float).

    """

    try:
        float(s)
    except:
        return False
    else:
        return True


def ij_transfer_func(
        i,
        j,
        transfer_funcs
):
    """
    Return a p_z value as the result of a function (transfer_func_z) applied to a (p_x,p_y) point.
    This point is derived from a (i,j) point given two "transfer" functions (transfer_func_y, transfer_func_x).
    All three functions are stored into a tuple (transfer_funcs).

    @param  i:  array i (-p_y) coordinate of a single point.
    @type  i:  float.
    @param  j:  array j (p_x) coordinate of a single point.
    @type  j:  float.
    @param  transfer_funcs:  tuple storing three functions (transfer_func_x, transfer_func_y, transfer_func_z)
                            that derives p_y from i (transfer_func_y), p_x from j (transfer_func_x)
                            and p_z from (p_x,p_y) (transfer_func_z).
    @type  transfer_funcs:  Tuple of Functions.

    @return:  p_z value - float.

    """

    transfer_func_x, transfer_func_y, transfer_func_z = transfer_funcs

    return transfer_func_z(transfer_func_x(j), transfer_func_y(i))


def array_from_function(row_num, col_num, x_transfer_func, y_transfer_func, z_transfer_func):
    """
    Creates an array of p_z values based on functions that map (i,j) indices (to be created)
    into (p_x, p_y) values and then p_z values.

    @param  row_num:  row number of the array to be created.
    @type  row_num:  int.
    @param  col_num:  column number of the array to be created.
    @type  col_num:  int.
    @param  x_transfer_func:  function that derives p_x given a j array index.
    @type  x_transfer_func:  Function.
    @param  y_transfer_func:  function that derives p_y given an i array index.
    @type  y_transfer_func:  Function.
    @param  z_transfer_func:  function that derives p_z given a (p_x,p_y) point.
    @type  z_transfer_func:  Function.

    @return:  array of p_z value - array of float numbers.

    """

    transfer_funcs = (x_transfer_func, y_transfer_func, z_transfer_func)

    return fromfunction(ij_transfer_func, (row_num, col_num), transfer_funcs=transfer_funcs)


def densify_as_array1d_(
    segment_length: numbers.Real,
    densify_distance: numbers.Real
) -> Tuple[bool, Union[str, array]]:
    """
    Defines the array storing the incremental lengths according to the provided densify distance.

    :param segment_length: the length up to which densify.
    :param densify_distance: the densify distance.
    :return: optional array storing the incremental steps, with the last step being equal to the segment length.
    """

    try:

        if not isinstance(densify_distance, numbers.Real):
            return False, "Densify distance must be float or int"

        if not isfinite(densify_distance):
            return False, "Densify distance must be finite"

        if densify_distance <= 0.0:
            return False, "Densify distance must be positive"

        s_list = []
        n = 0
        length = n * densify_distance

        while length < segment_length:
            s_list.append(length)
            n += 1
            length = n * densify_distance

        s_list.append(segment_length)

        return True, array('d', s_list)

    except Exception as e:

        return False, str(e)

