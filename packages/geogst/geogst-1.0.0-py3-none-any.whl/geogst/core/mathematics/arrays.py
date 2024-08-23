
import warnings

from typing import Sequence, List
import decimal

import numpy as np
from numpy.linalg import LinAlgError

from geogst.core.mathematics.utils import *


def determinant3x3(
        a: np.array,
        precision: numbers.Integral = 40
) -> decimal.Decimal:
    """
    Calculates determinant of array.
    Implemented to bypass apparent bug in Numpy-linalg.det method in 3.22 QGIS version Linux

    :param a:
    :param precision:
    :return:

    Examples:
	  >>> determinant3x3(np.array([[4.75798344e+06, 0., 1.], [4.77184089e+06, 0., 1.], [4.77184089e+06, 1.e+03, 1.]]))
	  Decimal('13857449.999999254941940307617187500000')
    """

    decimal.getcontext().prec = precision

    a00 = decimal.Decimal(a[0, 0])
    a01 = decimal.Decimal(a[0, 1])
    a02 = decimal.Decimal(a[0, 2])

    a10 = decimal.Decimal(a[1, 0])
    a11 = decimal.Decimal(a[1, 1])
    a12 = decimal.Decimal(a[1, 2])

    a20 = decimal.Decimal(a[2, 0])
    a21 = decimal.Decimal(a[2, 1])
    a22 = decimal.Decimal(a[2, 2])

    result = a00*a11*a22 + a01*a12*a20 + a10*a21*a02 - (a02*a11*a20 + a01*a10*a22 + a00*a12*a21)

    return result

def array_to_tuple(
        arr1D: np.ndarray
) -> Tuple[numbers.Real, ...]:
    """
    Converts a 1D arrays into a tuple of floats.
    It assumes a 1D np.ndarray as input.
    Modified from: https://stackoverflow.com/questions/10016352/convert-numpy-array-to-tuple

    :param arr1D: the 1D-arrays whose components have to be extracted.
    :return: a tuple derived from the array values extraction.

    Examples:
      >>> levels = np.array([1,2,3,4,5])
      >>> array_to_tuple(levels)
      (1.0, 2.0, 3.0, 4.0, 5.0)
    """

    return tuple(map(float, arr1D))


def to_floats(
        iterable_obj: Sequence[numbers.Real]
) -> List[numbers.Real]:
    """
    Converts an iterable object storing float-compatible values to a list of floats.

    :param iterable_obj: iterable object storing float-compatible values
    :return: the float list.

    Examples:
      >>> to_floats([1, 2, 3])
      [1.0, 2.0, 3.0]
    """

    return [float(item) for item in iterable_obj]


def arrays_are_close(
        a_array: np.ndarray,
        b_array: np.ndarray,
        rtol: numbers.Real = 1e-12,
        atol: numbers.Real = 1e-12,
        equal_nan: bool = False,
        equal_inf: bool = False
) -> bool:
    """
    Check for equivalence between two numpy arrays.

    :param a_array: first array to be compared.
    :param b_array: second array to be compared with the first one.
    :param rtol: relative tolerance.
    :param atol: absolute tolerance.
    :param equal_nan: consider nan values equivalent or not.
    :param equal_inf: consider inf values equivalent or not.
    :return: whether the two arrays are close as component values.

    Examples:
      >>> arrays_are_close(np.array([1,2,3]), np.array([1,2,3]))
      True
      >>> arrays_are_close(np.array([[1,2,3], [4, 5, 6]]), np.array([1,2,3]))
      False
      >>> arrays_are_close(np.array([[1,2,3], [4,5,6]]), np.array([[1,2,3], [4,5,6]]))
      True
      >>> arrays_are_close(np.array([[1,2,np.nan], [4,5,6]]), np.array([[1,2,np.nan], [4,5,6]]))
      False
      >>> arrays_are_close(np.array([[1,2,np.nan], [4,5,6]]), np.array([[1,2,np.nan], [4,5,6]]), equal_nan=True)
      True
    """
    if a_array.shape != b_array.shape:
        return False

    are_close_values = []
    for a, b in np.nditer([a_array, b_array]):
        are_close_values.append(are_close(a.item(0), b.item(0), rtol=rtol, atol=atol, equal_nan=equal_nan, equal_inf=equal_inf))

    return all(are_close_values)


def arrays_same_shape(
        a_array: np.ndarray,
        b_array: np.ndarray
) -> bool:
    """
    Checks that two arrays have the same shape.

    :param a_array: first array
    :param b_array: second array
    :return: whether the two arrays have the same shape.

    Examples:
      >>> arrays_same_shape(np.ones((2,2)), np.ones(4))
      False
      >>> arrays_same_shape(np.ones((2,2,3)), np.zeros((2,2,3)))
      True
    """

    return a_array.shape == b_array.shape


def point_solution(
        a_array: np.ndarray,
        b_array: np.ndarray
) -> Tuple[Optional[numbers.Real], Optional[numbers.Real], Optional[numbers.Real]]:
    """
    Finds a non-unique solution for a set of linear equations.

    :param a_array: the first array.
    :param b_array: the second array.
    :return: an optional tuple of solutions.
    """

    try:

        return np.linalg.lstsq(a_array, b_array, rcond=None)[0]

    except Exception:

        return None, None, None


def svd(
    xyz_array: np.ndarray
        ) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    DEPRECATED: use singular_value_decomposition.
    Calculates the SVD solution given a Numpy array.

    # modified after:
    # http://stackoverflow.com/questions/15959411/best-fit-plane-algorithms-why-different-results-solved

    :param xyz_array: the source array.
    :return: the singular value decomposition solution.
    """
    warnings.warn(
        "DEPRECATED: use singular_value_decomposition",
        DeprecationWarning,
    )
    try:
        return np.linalg.svd(xyz_array)
    except Exception:
        return None


def singular_value_decomposition(
    xyz_array: np.ndarray,
    full_matrices: bool = True,
    compute_uv: bool = True,
) -> Tuple[Tuple[Union[None, np.ndarray], Union[None, np.ndarray], Union[None, np.ndarray]], Error]:
    """
    Calculates the SVD solution given a Numpy array.

    # modified after:
    # http://stackoverflow.com/questions/15959411/best-fit-plane-algorithms-why-different-results-solved

    :param xyz_array: the source array.
    :return: the singular value decomposition solution.
    """

    u, s, vh = None, None, None
    err = Error()

    try:

        if compute_uv:

            u, s, vh = np.linalg.svd(
                a=xyz_array,
                full_matrices=full_matrices,
                compute_uv=compute_uv,
            )

        else:

            s = np.linalg.svd(
                a=xyz_array,
                full_matrices=full_matrices,
                compute_uv=compute_uv,
            )

    except LinAlgError as _:

        err = Error(
            True,
            caller_name(),
            Exception("SVD computation does not converge."),
            traceback.format_exc()
        )

    except Exception as e:

        err = Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )

    finally:

        return (u, s, vh), err

def pixels_zoom(
    width: numbers.Integral,
    height: numbers.Integral,
    z: numbers.Real
) -> Tuple[numbers.Integral, numbers.Integral, numbers.Integral, numbers.Integral]:
    """
    Zoom into a grid center by a given factor.
    It returns the left, right, top and down pixel indices.
    The pixel indices start from 0, left-to-right (j) and top-to-down(i).

    :param width: the grid width in pixels.
    :param height: the grid height in pixels.
    :param z: the factor to zoom into the grid center.

    Examples:
      >>> pixels_zoom(4, 4, 1)
      (0, 4, 0, 4)
      >>> pixels_zoom(4, 4, 2)
      (1, 3, 1, 3)
      >>> pixels_zoom(3, 6, 3)
      (1, 2, 2, 4)
    """

    halved_shrinked = 1 / (2 * z)

    center_minus, center_plus = 0.5 - halved_shrinked, 0.5 + halved_shrinked

    left_pixel, right_pixel = round(center_minus * width), round(center_plus * width)
    top_pixel, bottom_pixel = round(center_minus * height), round(center_plus * height)

    return left_pixel, right_pixel, top_pixel, bottom_pixel


if __name__ == "__main__":

    import doctest

    doctest.testmod()
