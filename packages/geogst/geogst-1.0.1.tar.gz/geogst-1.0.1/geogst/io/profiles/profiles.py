
from geogst.io.vectors.ogr import *


def try_export_to_shapefile(
        profiler: Profilers,
        shapefile_path: str,
        epsg_code: numbers.Integral
) -> Tuple[bool, str]:
    """
    Exports the parallel profilers in a line shapefile.

    :param profiler: the source profilers.
    :param shapefile_path: the path of the shapefile to create.
    :param epsg_code: the dataset EPSG code.
    :return: a success flag and a descriptive message.
    """

    try:

        records_values = []
        for ndx, profiler in enumerate(profiler):
            points_coords = profiler.line.coords()
            attributes = [ndx]
            records_values.append((points_coords, attributes))

        return try_create_write_line_shapefile(
            shapefile_path=shapefile_path,
            fields_dict_list=[{"name": "cod", "ogr_type": 'ogr.OFTInteger'}],
            records_values=records_values,
            epsg_code=epsg_code
        )

    except Exception as e:

        return False, f"{e!r}"
