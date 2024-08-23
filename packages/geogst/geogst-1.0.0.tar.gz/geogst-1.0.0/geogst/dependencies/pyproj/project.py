
from typing import Tuple
import numbers

import numpy as np

from pyproj.transformer import Transformer, TransformerGroup, AreaOfInterest

from geogst.core.inspections.errors import *


min_epsg_crs_code = 2000  # checked 2019-06-14 in EPSG database
EpsgCode = numbers.Integral


def project_xy(
    x: numbers.Real,
    y: numbers.Real,
    source_epsg_code: EpsgCode,
    dest_epsg_code: EpsgCode = 4326,
) -> Optional[Tuple[numbers.Real, numbers.Real]]:

    if source_epsg_code == -1:
        return None

    if dest_epsg_code == -1:
        return None

    transformer = Transformer.from_crs(
        f"epsg:{source_epsg_code}",
        f"epsg:{dest_epsg_code}"
    )

    x_prj, y_prj = transformer.transform(x, y)

    return x_prj, y_prj


def project_extent(
    x_min: numbers.Real,
    x_max: numbers.Real,
    y_min: numbers.Real,
    y_max: numbers.Real,
    source_epsg_code: EpsgCode
) -> Optional[Tuple[numbers.Real, numbers.Real, numbers.Real, numbers.Real]]:

    result = project_xy(
        x=x_min,
        y=y_min,
        source_epsg_code=source_epsg_code
    )

    if result is None:
        return None

    lon_min, lat_min = result

    result = project_xy(
        x=x_max,
        y=y_max,
        source_epsg_code=source_epsg_code
    )

    if result is None:
        return None

    lon_max, lat_max = result

    return lon_min, lat_min, lon_max, lat_max


def try_project_xy_arrays(
    x_array: np.ndarray,
    y_array: np.ndarray,
    source_epsg_code: EpsgCode,
    dest_epsg_code: EpsgCode,
    area_of_interest: Tuple[numbers.Real, numbers.Real, numbers.Real, numbers.Real]
) -> Tuple[bool, Union[str, Tuple[np.ndarray, np.ndarray]]]:
    """
    WARNING: currently this method is experimental.
    To understand why axis swap is need to obtain a correct result (4325 -> 32633)
    """

    try:

        transformer_group = TransformerGroup(
            crs_from=f"epsg:{source_epsg_code}",
            crs_to=f"epsg:{dest_epsg_code}",
            area_of_interest=AreaOfInterest(*area_of_interest),
        )

        if not transformer_group.best_available:
            return False, "Best transformation is not available"

        #TODO: understand why you have to swap axis to obtain a correct result....
        proj_x_coords, proj_y_coords = transformer_group.transformers[0].transform(
            y_array,
            x_array
        )

        return True, (proj_x_coords, proj_y_coords)

    except Exception as e:

        return False, f"{e!r}"


if __name__ == "__main__":

    import doctest

    doctest.testmod()
