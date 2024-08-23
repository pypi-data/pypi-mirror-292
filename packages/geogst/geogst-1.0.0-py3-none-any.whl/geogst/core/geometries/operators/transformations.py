
from affine import Affine

from geogst.core.mathematics.utils import *


def gdal_to_affine(
    geotransform: Tuple[numbers.Real, numbers.Real, numbers.Real, numbers.Real, numbers.Real, numbers.Real]
) -> Affine:
    """
    Create an affine transformation
    from a GDAL geotransform tuple.

    """

    return Affine.from_gdal(*geotransform)


def forward_transformation(
    trans: Affine,
    row: numbers.Real,
    col: numbers.Real
) -> Tuple[numbers.Real, numbers.Real]:
    """
    Calculate the x, y coordinates given an affine transformation
    and the row, col values.

    """

    return trans * (col, row)


if __name__ == "__main__":
    import doctest

    doctest.testmod()







