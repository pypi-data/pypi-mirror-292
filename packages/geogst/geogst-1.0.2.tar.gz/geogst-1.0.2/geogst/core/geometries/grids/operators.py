
from typing import List

import numbers
from math import sin, cos, floor

import numpy as np

from geogst.core.inspections.errors import *


def grad_i(
        array: np.ndarray,
        cell_size_i: numbers.Real,
        edge_order: numbers.Integral = 2
) -> np.ndarray:
    """
    Calculates the array gradient along the i axis.

    :param array: array.
    :param cell_size_i: the cell spacing in the y direction.
    :param edge_order: the type of edge order used in the Numpy gradient method.
    :return: gradient field.
    """

    return np.gradient(
        array,
        edge_order=edge_order,
        axis=0
    ) / cell_size_i


def grad_iminus(
        fld: np.ndarray,
        cell_size_i: numbers.Real,
        edge_order: numbers.Integral = 2
) -> np.ndarray:
    """
    Calculates the array gradient along the -i axis.

    :param fld: array.
    :type fld: np.ndarray.
    :param cell_size_i: the cell spacing in the y direction.
    :type cell_size_i: numbers.Real.
    :param edge_order: the type of edge order used in the Numpy gradient method.
    :type edge_order: numbers.Integral.
    :return: gradient field.
    :rtype: np.ndarray.

    Examples:
    """

    return - np.gradient(fld, edge_order=edge_order, axis=0) / cell_size_i


def grad_j(
    array: np.ndarray,
    cell_size_j: numbers.Real,
    edge_order: numbers.Integral = 2
) -> np.ndarray:
    """
    Calculates the array gradient along the j axis.

    :param array: array.
    :param cell_size_j: the cell spacing in the x direction.
    :param edge_order: the type of edge order used in the Numpy gradient method.
    :return: gradient field.
    """

    return np.gradient(
        array,
        edge_order=edge_order,
        axis=1
    ) / cell_size_j


def dir_deriv(
        fld: np.ndarray,
        cell_size_x: numbers.Real,
        cell_size_y: numbers.Real,
        direct_rad: numbers.Real,
        dx_edge_order: numbers.Integral = 2,
        dy_edge_order: numbers.Integral = 2
) -> np.ndarray:
    """
    Calculates the directional derivative in the provided direction.

    :param fld: the field.
    :param cell_size_x: the cell size along the x axis.
    :param cell_size_y: the cell size along the y
    :param direct_rad: the direction, expressed as radians.
    :param dx_edge_order: the edge order of the gradient along x.
    :param dy_edge_order: the edge order of the gradient along y.
    :return: the directional derivative array.
    """

    df_dx = grad_j(
        array=fld,
        cell_size_j=cell_size_x,
        edge_order=dx_edge_order)

    df_dy = - grad_i(
        array=fld,
        cell_size_i=cell_size_y,
        edge_order=dy_edge_order)

    return df_dx * sin(direct_rad) + df_dy * cos(direct_rad)


def magnitude(
        fld_x: np.ndarray,
        fld_y: np.ndarray
) -> np.ndarray:
    """
    Calculates the magnitude given two 2D arrays:
    the first represents the vector field x component, the second the vector field y component.

    :param fld_x: vector field x component.
    :param fld_y: vector field y component.
    :return: magnitude field.
    """

    return np.sqrt(fld_x ** 2 + fld_y ** 2)


def orients_r(
        fld_x: np.ndarray,
        fld_y: np.ndarray
) -> np.ndarray:
    """
    Calculates the orientations (as radians) given two 2D arrays:
    the first represents the vector field x component, the second the vector field y component.

    :param fld_x: vector field x component.
    :param fld_y: vector field y component.
    :return: orientation field, in radians.
    """

    azimuth_rad = np.arctan2(fld_x, fld_y)
    azimuth_rad = np.where(azimuth_rad < 0.0, azimuth_rad + 2*np.pi, azimuth_rad)

    return azimuth_rad


def orients_d(
        fld_x: np.ndarray,
        fld_y: np.ndarray
) -> np.ndarray:
    """
    Calculates the orientations (as decimal degrees) given two 2D arrays:
    the first represents the vector field x component, the second the vector field y component.

    :param fld_x: vector field x component.
    :param fld_y: vector field y component.
    :return: orientation field, in decimal degrees.
    """

    return np.degrees(orients_r(fld_x, fld_y))


def divergence(
        fld_x: np.ndarray,
        fld_y: np.ndarray,
        cell_size_x: numbers.Real,
        cell_size_y: numbers.Real
) -> np.ndarray:
    """
    Calculates the divergence from two 2D arrays:
    the first represents the vector field x component, the second the vector field y component.

    :param fld_x: vector field x component.
    :param fld_y: vector field y component.
    :param cell_size_x: the cell spacing in the x direction.
    :param cell_size_y: the cell spacing in the y direction.
    :return: divergence field.
    """

    dfx_dx = grad_j(fld_x, cell_size_x)
    dfy_dy = grad_iminus(fld_y, cell_size_y)

    return dfx_dx + dfy_dy


def curl_module(
        fld_x: np.ndarray,
        fld_y: np.ndarray,
        cell_size_x: numbers.Real,
        cell_size_y: numbers.Real
) -> np.ndarray:
    """
    Calculates the curl module from two 2D arrays:
    the first represents the vector field x component, the second the vector field y component.

    :param fld_x: vector field x component.
    :param fld_y: vector field y component.
    :param cell_size_x: the cell spacing in the x direction.
    :param cell_size_y: the cell spacing in the y direction.
    :return: curl field.
    """

    dfx_dy = grad_iminus(fld_x, cell_size_y, edge_order=2)
    dfy_dx = grad_j(fld_y, cell_size_x, edge_order=1)

    return dfy_dx - dfx_dy


def magn_grads(
        fld_x: np.ndarray,
        fld_y: np.ndarray,
        dir_cell_sizes: List[numbers.Real],
        axis: str = ''
) -> List[np.ndarray]:
    """
    Calculates the magnitude gradient along the given direction, based on the field-defining two 2D arrays:
    the first representing the x component, the second the y component.

    :param fld_x: vector field x component.
    :param fld_y: vector field y component.
    :param dir_cell_sizes: list of cell spacing(s) in the considered direction(s).
    :param axis: declares the axis ('x' or 'y') or the axes('', i.e., empty string) for both x and y directions.
    :return: magnitude gradient field(s) along the considered direction.
    :raises: Exception.
    """

    magn = magnitude(fld_x, fld_y)
    if axis == 'x':
        return [grad_j(magn, dir_cell_sizes[0])]
    elif axis == 'y':
        return [grad_iminus(magn, dir_cell_sizes[0])]
    elif axis == '':
        return [grad_j(magn, dir_cell_sizes[0]), grad_iminus(magn, dir_cell_sizes[1])]
    else:
        raise Exception("Axis must be 'x' or 'y' or '' (for both x and y). '{}' given".format(axis))


def magn_grad_along_flowlines(
        fld_x: np.ndarray,
        fld_y: np.ndarray,
        cell_size_x: numbers.Real,
        cell_size_y: numbers.Real
) -> np.ndarray:
    """
    Calculates gradient along flow lines.

    :param fld_x: vector field x component.
    :param fld_y: vector field y component.
    :param cell_size_x: the cell spacing in the x direction.
    :param cell_size_y: the cell spacing in the y direction.
    :return: the flowline gradient field
    """

    orien_rad = orients_r(fld_x, fld_y)

    dm_dx, dm_dy = magn_grads(
        fld_x=fld_x,
        fld_y=fld_y,
        dir_cell_sizes=[cell_size_x, cell_size_y])

    velocity_gradient = dm_dx * np.sin(orien_rad) + dm_dy * np.cos(orien_rad)

    return velocity_gradient


if __name__ == "__main__":
    import doctest

    doctest.testmod()


def interp_linear(
        frac_s: numbers.Real,
        v0: numbers.Real,
        v1: numbers.Real
) -> numbers.Real:
    """
    Interpolate a number in a linear way.

    :param frac_s: the fractional distance between the start and end point. Range 0-1.
    :type frac_s: numbers.Real.
    :param v0: the value at the start point.
    :type v0: numbers.Real.
    :param v1: the value at the end point.
    ;:type v1: numbers.Real.
    :return: the interpolated value.

    Examples:
      >>> interp_linear(0, 10, 20)
      10
      >>> interp_linear(1, 10, 20)
      20
      >>> interp_linear(-1, 10, 20)
      0
      >>> interp_linear(2, 10, 20)
      30
      >>> interp_linear(0.3, 0, 10)
      3.0
      >>> interp_linear(0.75, 0, 10)
      7.5
    """

    delta_z = v1 - v0
    return v0 + frac_s * delta_z


def scalars_bilin_interp(
        i: numbers.Real,
        j: numbers.Real,
        v00: numbers.Real,
        v01: numbers.Real,
        v10: numbers.Real,
        v11: numbers.Real
) -> numbers.Real:
    """
    Return an interpolated number based on a bilinear interpolation.

    :param i: the delta i relative to the preceding cell center.
    :param j: the delta j relative to the preceding cell center.
    :param v00: the z value of the (i=0, j=0) cell center.
    :param v01: the z value of the (i=0, j=1) cell center.
    :param v10: the z value of the (i=1, j=0) cell center.
    :param v11: the z value of the (i=1, j=1) cell center.
    :return: the interpolated z value.
    """

    grid_val_y0 = v00 + (v10 - v00) * i
    grid_val_y1 = v01 + (v11 - v01) * i

    return grid_val_y0 + (grid_val_y1 - grid_val_y0) * j


def array_bilin_interp(
        arr: np.ndarray,
        i: Union[numbers.Real, np.float64],
        j: Union[numbers.Real, np.float64],
) -> Union[type(None), numbers.Real]:
    """
    Interpolate the z value at a given i,j values couple.
    Interpolation method: bilinear.

    0, 0   0, 1

    1, 0,  1, 1

    :param arr: array with values for which the interpolation will be made.
    :param i: i array index of the point (may be fractional).
    :param j: j array index of the point (may be fractional).
    :return: interpolated z value (may be math.nan).
    """

    i = float(i)
    j = float(j)

    i_max, j_max = arr.shape
    di = i - floor(i)
    dj = j - floor(j)

    if i < 0.0 or j < 0.0:
        return None
    elif i > i_max - 1 or j > j_max - 1:
        return None
    elif i == i_max - 1 and j == j_max - 1:
        return arr[int(round(i)), int(round(j))]
    elif i == i_max - 1:
        v0 = arr[int(round(i)), int(floor(j))]
        v1 = arr[int(round(i)), int(floor(j + 1))]
        return interp_linear(
            frac_s=dj,
            v0=v0,
            v1=v1)
    elif j == j_max - 1:
        v0 = arr[int(floor(i)), int(round(j))]
        v1 = arr[int(floor(i + 1)), int(round(j))]
        return interp_linear(
            frac_s=di,
            v0=v0,
            v1=v1)
    else:
        v00 = arr[int(floor(i)), int(floor(j))]
        v01 = arr[int(floor(i)), int(floor(j + 1))]
        v10 = arr[int(floor(i + 1)), int(floor(j))]
        v11 = arr[int(floor(i + 1)), int(floor(j + 1))]
        return scalars_bilin_interp(di, dj, v00, v01, v10, v11)
