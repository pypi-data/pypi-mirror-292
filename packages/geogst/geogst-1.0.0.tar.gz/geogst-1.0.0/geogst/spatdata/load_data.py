import geopandas

from geogst.io.rasters.gdal import *
from geogst.io.vectors.ogr import *
from geogst.dependencies.geopandas.geopandas import *


current_folder = os.path.dirname(__file__)


dem_src_params = {
    "timpa_san_lorenzo": "tsl_tinitaly_w84u32.tif",
    "valnerina": "valnerina_utm33_red.tif",
    "colfiorito_2007": "srtm2.tif",
    "mt_alpi": "malpi_aster_w4u3.tif",
}

profile_src_params = {
    "timpa_san_lorenzo": "tsl_ortho_profile.shp",
    "valnerina": "profile.shp",
    "colfiorito_2007": "single_profile_swne.shp",
    "mt_alpi": "profile.shp",
}

fault_trace_src_params = {
    "timpa_san_lorenzo": "faults.shp",
    "valnerina": "faults.shp",
    "colfiorito_2007": "faults.shp",
    "mt_alpi": None,
}

seism_src_params = {
    "timpa_san_lorenzo": None,
    "valnerina": None,
    "colfiorito_2007": "ipocentri3d_shcm_wu3.shp",
    "mt_alpi": None,
}

attitude_src_params = {
    "timpa_san_lorenzo": None,
    "valnerina": "attitudes.shp",
    "colfiorito_2007": None,
    "mt_alpi": "attitudes.shp",
}

outcrop_src_params = {
    "timpa_san_lorenzo": "geological_outcrops_utm32N.shp",
    "valnerina": "geological_outcrops.shp",
    "colfiorito_2007": None,
    "mt_alpi": None,
}

line_with_attitude_src_params = {
    "timpa_san_lorenzo": "merged_intersections.shp",
    "valnerina": "main_plane_269_06_7.shp",
    "colfiorito_2007": None,
    "mt_alpi": None,
}


def read_dem(
    area: str
) -> Union[Error, Grid]:

    try:

        dem_name = dem_src_params.get(area)

        if dem_name is None:
            return Error(
                True,
                caller_name(),
                Exception(f"Provided area is {area}, that is not an expected value"),
                traceback.format_exc()
            )

        src_dem_pth = f"{current_folder}/data_sources/{area}/{dem_name}"

        result, err = read_raster_band_with_projection(
            raster_source=src_dem_pth
        )

        if err:
            return err

        geotransform, epsg, band_params, data, gdal_projection = result

        return Grid(
            array=data,
            geotransform=geotransform,
            epsg_code=epsg,
            projection=gdal_projection
        )

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def read_profile(
    area: str
) -> Union[Error, Ln]:

    try:

        trace = profile_src_params.get(area)
        if trace is None:
            return Error(
                True,
                caller_name(),
                Exception(f"Provided area is {area}, that is not an expected value"),
                traceback.format_exc()
            )

        src_profile = f"{current_folder}/data_sources/{area}/{trace}"

        profiles, err = read_line_shapefile_with_attributes(
            shp_path=src_profile)

        if err:
            return err

        ([([profile_line, ], _)], epsg_code) = profiles

        if area == "timpa_san_lorenzo":
            profile_line = profile_line.reversed()

        return profile_line

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def read_faults(
    area: str,
) -> Union[Error, Dict]:

    try:

        faults_name = fault_trace_src_params.get(area)

        if faults_name is None:
            return Error(
                True,
                caller_name(),
                Exception(f"Provided area is {area}, that is not an expected value"),
                traceback.format_exc()
            )

        faults_shape = f"{current_folder}/data_sources/{area}/{faults_name}"

        if area == 'colfiorito_2007':

            cat_field_name = "type"

        else:

            cat_field_name = "id"

        result, err = read_line_shapefile_via_ids(
            shp_path=faults_shape,
            id_field_name=cat_field_name
        )

        if err:
            return err

        _, _, faults_dict = result

        return faults_dict

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def read_outcrops(
    area: str
) -> Union[Error, Dict[Category, List[Polygon]]]:

    try:

        dataset_name = outcrop_src_params.get(area)

        if dataset_name is None:
            return Error(
                True,
                caller_name(),
                Exception(f"Provided area is {area}, that has no associated outcrop dataset"),
                traceback.format_exc()
            )

        dataset_shpfl_path = f"{current_folder}/data_sources/{area}/{dataset_name}"

        result, err = read_polygon_shapefile_via_ids(
            shp_path=dataset_shpfl_path,
            id_field_name="code"
        )

        if err:
            return err

        epsg_cd, layer_extent, polygons = result

        return polygons

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def read_attitudes(
    area: str,
) -> Union[Error, Dict[Category, List[Polygon]]]:

    try:

        attitudes_name = attitude_src_params.get(area)

        if attitudes_name is None:
            return Error(
                True,
                caller_name(),
                Exception(f"No attitudes available for area {area}"),
                traceback.format_exc()
            )

        attitudes_shpfl_path = f"{current_folder}/data_sources/{area}/{attitudes_name}"

        attitudes_gdf = geopandas.read_file(attitudes_shpfl_path)

        attitudes_list, err = extract_attitudes(
            geodataframe=attitudes_gdf,
            azim_fldnm="dip_dir",
            dip_ang_fldnm="dip_ang"
        )

        if err:
            return err

        grid = load(area, "DEM")

        attitudes_3d = attitudes_3d_from_grid(
            structural_data=attitudes_list,
            height_source=grid,
        )

        if err:
            return err
        else:
            return attitudes_3d

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def read_lines_with_attitudes(
    area: str
) -> Union[Error, Dict]:

    try:

        dataset_name = line_with_attitude_src_params.get(area)

        if dataset_name is None:
            return Error(
                True,
                caller_name(),
                Exception(f"Provided area {area} has no associated dataset of 'lines_with_attitudes' type"),
                traceback.format_exc()
            )

        src_shapefile = f"{current_folder}/data_sources/{area}/{dataset_name}"

        if area == "timpa_san_lorenzo":

            results, err = read_line_shapefile_with_attributes(
                shp_path=src_shapefile,
                flds=["Source", "dip_dir", "dip_ang"]
            )

            if err:
                return None, err

            lines_data, _ = results

            line_orientations = defaultdict(list)
            for lines, (source, dip_dir, dip_ang) in lines_data:
                line_orientations[source].append([Plane(dip_dir, dip_ang), lines])

            return line_orientations

        elif area == "valnerina":

            results, err = read_line_shapefile(
                shp_path=src_shapefile,
            )

            if err:
                return err

            lines, epsg_code = results

            return {"main plane 269-06.7": (Plane(269, 6.7), lines)}

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def read_seisms(
    area: str,
) -> Union[Error, List[Tuple[Any, Point, Fault]]]:

    try:

        seism_src_name = seism_src_params.get(area)

        if seism_src_name is None:
            return Error(
                True,
                caller_name(),
                Exception(f"No seismic data available for area {area}"),
                traceback.format_exc()
            )

        seism_shpfl_path = f"{current_folder}/data_sources/{area}/{seism_src_name}"

        seism_gdf = geopandas.read_file(seism_shpfl_path)

        print(seism_gdf)

        seism_points, err = extract_seism_points(
            geodataframe=seism_gdf,
            azim_fldnm="STRIKE",
            dip_ang_fldnm="DIP",
            rake_fldnm="RAKE",
            is_rhrstrike=True,
            category_fldnm="MAGNITUDE",
        )

        if err:
            return err

        return seism_points

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


dataset_load_functions = {
    'DEM': read_dem,
    'profile': read_profile,
    'outcrops': read_outcrops,
    'lines_with_attitudes': read_lines_with_attitudes,
    'faults': read_faults,
    'seisms': read_seisms,
    'attitudes': read_attitudes,

}


def load(
    area: str = 'timpa_san_lorenzo',
    type: str = 'DEM'
) -> Union[Error, Grid, List[Ln], List[Polygon], Dict, ]:

    try:

        return dataset_load_functions[type](area=area)

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )





