
from typing import Dict

import scipy

try:
    from osgeo import gdal
except ImportError:
    import gdal

try:
    from osgeo import osr
except ImportError:
    import osr

from geogst.core.geometries.grids.rasters import *
from geogst.core.inspections.errors import *
from geogst.core.inspections.functions import *


def extract_raster_params(
    file_ref: Any
) -> Tuple[
    Union[type(None), Tuple[gdal.Dataset, Union[type(None), GeoTransform], numbers.Integral, numbers.Integral, 'gdal.Projection']], Error]:
    """
    Read raster parameters.

    :param file_ref: the reference to the raster
    :return: the dataset, the parsed geotransform, the number of bands, the parsed projection,
              the original geotransform, the original projection as a tuple, plus the error status.
    """

    try:

        # open raster file and check operation success

        dataset = gdal.Open(file_ref, gdal.GA_ReadOnly)

        if not dataset:
            return None, Error(
                True,
                caller_name(),
                Exception("No input data open"),
                traceback.format_exc()
            )

        # get raster descriptive infos

        gdal_geotransform = dataset.GetGeoTransform()

        if gdal_geotransform:
            geotransform = GeoTransform.from_gdal_geotransform(gdal_geotransform)
        else:
            geotransform = None

        num_bands = dataset.RasterCount

        # https://gis.stackexchange.com/questions/267321/extracting-epsg-from-a-raster-using-gdal-bindings-in-python
        # does not work -> epsg = int(gdal.Info(input, format='json')['coordinateSystem']['wkt'].rsplit('"EPSG","', 1)[-1].split('"')[0])

        gdal_projection = osr.SpatialReference(wkt=dataset.GetProjection())
        gdal_projection.AutoIdentifyEPSG()

        try:
            epsg = int(gdal_projection.GetAttrValue('AUTHORITY', 1))
        except:
            epsg = -1

        return (dataset, geotransform, num_bands, epsg, gdal_projection), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def decompose_raster(
        file_ref: Any
) -> Tuple[
        Union[
            type(None),
            Tuple[
                gdal.Dataset, Union[type(None), GeoTransform], numbers.Integral, numbers.Integral]],
        Error
]:
    """
    Read a raster layer.

    :param file_ref: the reference to the raster
    :return: the dataset, its geotransform, the number of bands, the projection as a tuple, plus the error status.
    """

    try:

        # open raster file and check operation success

        dataset = gdal.Open(file_ref, gdal.GA_ReadOnly)

        if not dataset:
            return None, Error(
                True,
                caller_name(),
                Exception("No input data open"),
                traceback.format_exc()
            )

        # get raster descriptive infos

        gt = dataset.GetGeoTransform()

        if gt:
            geotransform = GeoTransform.from_gdal_geotransform(gt)
        else:
            geotransform = None

        num_bands = dataset.RasterCount

        # https://gis.stackexchange.com/questions/267321/extracting-epsg-from-a-raster-using-gdal-bindings-in-python
        # does not work -> epsg = int(gdal.Info(input, format='json')['coordinateSystem']['wkt'].rsplit('"EPSG","', 1)[-1].split('"')[0])

        proj = osr.SpatialReference(wkt=dataset.GetProjection())
        proj.AutoIdentifyEPSG()

        try:
            epsg = int(proj.GetAttrValue('AUTHORITY', 1))
        except:
            epsg = -1

        return (dataset, geotransform, num_bands, epsg), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def raster_band(
        dataset: gdal.Dataset,
        bnd_ndx: int = 1
) -> Tuple[
        Union[
            type(None),
            Tuple[dict, 'np.array']
            ],
        Error
]:
    """
    Read data and metadata of a rasters band based on GDAL.

    :param dataset: the source raster dataset
    :param bnd_ndx: the index of the band (starts from 1)
    :return: the band parameters and the data values
    """

    try:

        band = dataset.GetRasterBand(bnd_ndx)
        data_type = gdal.GetDataTypeName(band.DataType)

        unit_type = band.GetUnitType()

        stats = band.GetStatistics(False, False)

        if stats is None:
            dStats = dict(
                min=None,
                max=None,
                mean=None,
                std_dev=None)
        else:
            dStats = dict(
                min=stats[0],
                max=stats[1],
                mean=stats[2],
                std_dev=stats[3])

        noDataVal = band.GetNoDataValue()

        nOverviews = band.GetOverviewCount()

        colorTable = band.GetRasterColorTable()

        if colorTable:
            nColTableEntries = colorTable.GetCount()
        else:
            nColTableEntries = 0

        # read data from band

        grid_values = band.ReadAsArray()
        if grid_values is None:
            raise Exception("Unable to read data from rasters")

        # transform data into numpy array

        data = np.asarray(grid_values)

        # if nodatavalue exists, set null values to NaN in numpy array
        if noDataVal is not None and np.isfinite(noDataVal):
            data = np.where(abs(data - noDataVal) > 1e-10, data, np.NaN)

        band_params = dict(
            dataType=data_type,
            unitType=unit_type,
            stats=dStats,
            noData=noDataVal,
            numOverviews=nOverviews,
            numColorTableEntries=nColTableEntries)

        return (band_params, data), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def read_raster_band(
    raster_source: str,
    bnd_ndx: int = 1
) -> Tuple[Union[type(None), Tuple[GeoTransform, numbers.Integral, Dict, 'np.array']], Error]:
    """
    Read the band of a raster.
    Implicit band index is 1 (the first band).

    :param raster_source: the raster path.
    :param bnd_ndx: the band index. Implicit value is 1 (first band).
    :return: a tuple of results, plus the error status.
    """

    try:

        result, err = decompose_raster(raster_source)
        if err:
            return None, err

        dataset, geotransform, num_bands, epsg = result

        result, err = raster_band(dataset, bnd_ndx)
        if err:
            return None, err

        band_params, data = result

        return (geotransform, epsg, band_params, data), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def read_raster_band_with_projection(
    raster_source: str,
    bnd_ndx: int = 1
) -> Tuple[Union[type(None), Tuple[GeoTransform, numbers.Integral, Dict, np.ndarray, 'gdal.Projection']], Error]:
    """
    Read the band of a raster.
    Implicit band index is 1 (the first band).

    :param raster_source: the raster path.
    :param bnd_ndx: the band index. Implicit value is 1 (first band).
    :return: a tuple of results, plus the error status.
    """

    try:

        result, err = extract_raster_params(raster_source)
        if err:
            return None, err

        dataset, geotransform, num_bands, epsg, gdal_projection = result

        result, err = raster_band(dataset, bnd_ndx)
        if err:
            return None, err

        band_params, data = result

        return (geotransform, epsg, band_params, data, gdal_projection), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def write_geotiff(
    file_path: str,
    arr_out: np.ndarray,
    geotransform: 'gdal.GeoTransform',
    projection: 'gdal.Projection',
) -> Error:
    """

    Modified from:
    https://gis.stackexchange.com/questions/164853/reading-modifying-and-writing-a-geotiff-with-gdal-in-python
    Answer by Andrea Massetti
    Consulted on 2022-10-16.

    :return: Error
    """

    try:

        driver = gdal.GetDriverByName("GTiff")

        [rows, cols] = arr_out.shape

        outdata = driver.Create(
            file_path,
            cols,
            rows,
            1,
            gdal.GDT_Float64
        )

        outdata.SetGeoTransform(geotransform)
        outdata.SetProjection(projection.ExportToWkt())
        outdata.GetRasterBand(1).WriteArray(arr_out)
        outdata.FlushCache()

        return Error()

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def equivalent_geotransform(
        gt1: List,
        gt2: List
) -> bool:
    for val1, val2 in zip(gt1, gt2):
        if abs(val1 - val2) > 1e-7:
            print(val1, val2, abs(val1 - val2))
            return False
    return True


def compose_raster_image(
        dst_file_path: str,
        array_red: np.ndarray,
        array_green: np.ndarray,
        array_blue: np.ndarray,
        geotransform: GeoTransform,
        projection: numbers.Integral, # EPSG code
        format="GTiff"
) -> Error:
    """
    Infos from:
        http://drr.ikcest.org/tutorial/k8024 (cons. 2020/12/26)

    """

    try:

        rows, cols = array_red.shape

        driver = gdal.GetDriverByName(format)
        dst_ds = driver.Create(
            utf8_path=dst_file_path,
            xsize=cols,
            ysize=rows,
            bands=3,
            eType=gdal.GDT_Byte
        )

        dst_ds.SetGeoTransform(geotransform)

        srs = osr.SpatialReference()
        srs.ImportFromEPSG(projection)
        dst_ds.SetProjection(srs.ExportToWkt())
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.GetRasterBand(1).WriteArray(array_red)
        dst_ds.GetRasterBand(2).SetNoDataValue(0)
        dst_ds.GetRasterBand(2).WriteArray(array_green)
        dst_ds.GetRasterBand(3).SetNoDataValue(0)
        dst_ds.GetRasterBand(3).WriteArray(array_blue)

        return Error()

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def create_raster_grid(
        dst_file_path: str,
        array: np.ndarray,
        geotransform: GeoTransform,
        projection: numbers.Integral,
        format="GTiff"
) -> Error:
    """
    Infos from:
        http://drr.ikcest.org/tutorial/k8024 (cons. 2020/12/26)

    :param dst_file_path:
    :param array:
    :param geotransform:
    :param projection:
    :param format:
    :return:
    """

    try:

        rows, cols = array.shape

        driver = gdal.GetDriverByName(format)
        dst_ds = driver.Create(
            utf8_path=dst_file_path,
            xsize=cols,
            ysize=rows,
            bands=1,
            eType=gdal.GDT_Float32
        )

        dst_ds.SetGeoTransform(geotransform)

        srs = osr.SpatialReference()
        srs.ImportFromEPSG(projection)
        dst_ds.SetProjection(srs.ExportToWkt())
        dst_ds.GetRasterBand(1).SetNoDataValue(0)
        dst_ds.GetRasterBand(1).WriteArray(array)

        return Error()

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def calculate_band_ratio(
        num_band_pth: str,
        denom_band_pth: str,
        num_zoom: int = 1,
        denom_zoom: int = 1,
) -> Tuple[Union[type(None), Tuple[np.ndarray, GeoTransform, numbers.Integral]], Error]:
    """
    Calculate band division of two bands with equal CRS and geotransform.

    :param num_band_pth:
    :param denom_band_pth:
    :param num_zoom:
    :param denom_zoom:
    :return:
    """

    try:

        result, err = read_raster_band(
            raster_source=num_band_pth)

        if err:
            return None, err

        num_geotransform, num_projection, _, num_array = result

        result, err = read_raster_band(
            raster_source=denom_band_pth)

        if err:
            return None, err

        denom_geotransform, denom_projection, _, denom_array = result

        if denom_projection != num_projection:
            return None, Error(
                True,
                caller_name(),
                Exception(f"Numerator band proj is {num_projection} while denominator band proj is {denom_projection}"),
                traceback.format_exc()
        )

        # from: https://stackoverflow.com/questions/13242382/resampling-a-numpy-array-representing-an-image
        # Joe Kington
        if num_zoom != 1:
            num_array = scipy.ndimage.zoom(num_array, num_zoom, order=0)
            final_geotransform = denom_geotransform
        elif denom_zoom != 1:
            denom_array = scipy.ndimage.zoom(denom_array, denom_zoom, order=0)
            final_geotransform = num_geotransform
        else:
            final_geotransform = num_geotransform

        if denom_array.shape != num_array.shape:
            return None, Error(
                True,
                caller_name(),
                Exception(f"Numerator band shape is {num_array.shape} while denominator band shape is {denom_array.shape}"),
                traceback.format_exc()
        )

        num_array = np.where(num_array == 0, np.nan, num_array)
        denom_array = np.where(denom_array == 0, np.nan, denom_array)

        index_array = np.divide(num_array, denom_array)

        return (index_array, final_geotransform, num_projection), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def save_band_ratio(
        num_band_pth: str,
        denom_band_pth: str,
        dest_gtif_flpth: str,
        num_zoom: int = 1,
        denom_zoom: int = 1,
) -> Error:
    """
    Save band division of two bands with equal CRS and geotransform.

    :param num_band_pth:
    :param denom_band_pth:
    :param dest_gtif_flpth:
    :param num_zoom:
    :param denom_zoom:
    :return:
    """

    try:

        result, err = calculate_band_ratio(
            num_band_pth=num_band_pth,
            denom_band_pth=denom_band_pth,
            num_zoom=num_zoom,
            denom_zoom=denom_zoom)

        if err:
            return err

        index_array, final_geotransform, num_projection = result

        return create_raster_grid(
            dst_file_path=dest_gtif_flpth,
            array=index_array,
            geotransform=final_geotransform,
            projection=num_projection
        )

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def save_band_ratio_ternary(
        num1_band_pth: str,
        num2_band_pth: str,
        denom_band_pth: str,
        dest_gtif_flpth: str,
        formula: str,
        num1_zoom: int = 1,
        num2_zoom: int = 1,
        denom_zoom: int = 1
) -> Error:
    """
    Return band division of two bands with equal CRS and geotransform.

    :param num1_band_pth:
    :param num2_band_pth:
    :param denom_band_pth:
    :param dest_gtif_flpth:
    :param formula:
    :param num1_zoom:
    :param num2_zoom:
    :param denom_zoom:
    :return:
    """

    try:

        # band num 1

        result, err = read_raster_band(
            raster_source=num1_band_pth)

        if err:
            return err

        num1_geotransform, num1_projection, _, num1_array = result

        # band num 2

        result, err = read_raster_band(
            raster_source=num2_band_pth)

        if err:
            return err

        num2_geotransform, num2_projection, _, num2_array = result

        if num2_projection != num1_projection:
            return Error(
                True,
                caller_name(),
                Exception(f"Numerator 2 band proj is {num2_projection} while Numerator 1 band proj is {num1_projection}"),
                traceback.format_exc()
            )

        # band denom

        result, err = read_raster_band(
            raster_source=denom_band_pth)

        if err:
            return err

        denom_geotransform, denom_projection, _, denom_array = result

        if denom_projection != num1_projection:
            return Error(
                True,
                caller_name(),
                Exception(f"Denominator band proj is {denom_projection} while Numerator 1 band proj is {num1_projection}"),
                traceback.format_exc()
            )

        # final geotransform definition
        # from: https://stackoverflow.com/questions/13242382/resampling-a-numpy-array-representing-an-image, Joe Kington answer

        if num1_zoom == 1:
            final_geotransform = num1_geotransform
        elif num2_zoom == 1:
            final_geotransform = num2_geotransform
        else:
            final_geotransform = denom_geotransform

        # resampling of bands when needed

        if num1_zoom != 1:
            num1_array = scipy.ndimage.zoom(num1_array, num1_zoom, order=0)
        if num2_zoom != 1:
            num2_array = scipy.ndimage.zoom(num2_array, num2_zoom, order=0)
        if denom_zoom != 1:
            denom_array = scipy.ndimage.zoom(denom_array, denom_zoom, order=0)

        if denom_array.shape != num1_array.shape:
            return Error(
                True,
                caller_name(),
                Exception(f"Numerator 1 band shape is {num1_array.shape} while denominator band shape is {denom_array.shape}"),
                traceback.format_exc()
            )

        if denom_array.shape != num2_array.shape:
            return Error(
                True,
                caller_name(),
                Exception(f"Numerator 2 band shape is {num2_array.shape} while denominator band shape is {denom_array.shape}"),
                traceback.format_exc()
            )

        # fixing of zero values in denominator to avoid infinity/nan results

        denom_array = np.where(denom_array == 0, np.nan, denom_array)

        # result array calculation

        if formula == 'plus':
            index_array = np.divide(num1_array + num2_array, denom_array * 2)
        elif formula == 'mult':
            index_array = np.divide(np.multiply(num1_array, num2_array), np.square(denom_array))
        else:
            return Error(
                True,
                caller_name(),
                Exception(
                    f"Debug: got calculation formula {formula}"),
                traceback.format_exc()
        )

        # save results as geotiff

        return create_raster_grid(
            dst_file_path=dest_gtif_flpth,
            array=index_array,
            geotransform=final_geotransform,
            projection=num1_projection
        )

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


if __name__ == "__main__":

    import doctest
    doctest.testmod()

