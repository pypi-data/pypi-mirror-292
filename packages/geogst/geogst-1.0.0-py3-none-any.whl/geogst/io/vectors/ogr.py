
from osgeo import ogr
from osgeo import osr

from geogst.core.profiles.profilers import *

from geogst.core.inspections.errors import *
from geogst.core.inspections.functions import *


ogr_2d_line_types = [
    ogr.wkbLineString,
    ogr.wkbLineStringM,
    ogr.wkbMultiLineString,
    ogr.wkbMultiLineStringM
]

ogr_3d_line_types = [
    ogr.wkbLineString25D,
    ogr.wkbLineStringZM,
    ogr.wkbMultiLineString25D,
    ogr.wkbMultiLineStringZM
]

ogr_line_types = [
    ogr.wkbLineString,
    ogr.wkbLineString25D,
    ogr.wkbLineStringM,
    ogr.wkbLineStringZM
]

ogr_multiline_types = [
    ogr.wkbMultiLineString,
    ogr.wkbMultiLineString25D,
    ogr.wkbMultiLineStringM,
    ogr.wkbMultiLineStringZM
]

ogr_polygon_types = [
    ogr.wkbPolygon,
    ogr.wkbPolygon25D,
    ogr.wkbPolygonM,
    ogr.wkbPolygonZM
]

ogr_multipolygon_types = [
    ogr.wkbMultiPolygon,
    ogr.wkbMultiPolygon25D,
    ogr.wkbMultiPolygonM,
    ogr.wkbMultiPolygonZM
]


def try_open_shapefile(
        path: str
) -> Tuple[bool, Union[ogr.Layer, str]]:

    dataSource = ogr.Open(path)

    if dataSource is None:
        return False, "Unable to open shapefile in provided path"

    shapelayer = dataSource.GetLayer()

    return True, shapelayer


def extract_ogr_simple_line(
    simple_line_geom: ogr.Geometry,
    has_z: bool
) -> Ln:
    '''
    Read a simple line feature.
    '''

    coords = []

    for i in range(simple_line_geom.GetPointCount()):

        x, y = simple_line_geom.GetX(i), simple_line_geom.GetY(i)

        if has_z:
            z = simple_line_geom.GetZ(i)
            coords.append([x, y, z])
        else:
            coords.append([x, y])

    return Ln(coords)


def read_line_shapefile(
        shp_path: str,
    ) -> Tuple[Union[type(None), Tuple[List[Ln], numbers.Integral]], Error]:
    '''
    Read results geometries from a line shapefile using ogr.
    The result is a flat list of lines (i.e., multilines are
    returned as lines).

    :param shp_path: line shapefile path.
    :return: success status and (error message or results).
    '''

    try:

        # check input path

        if shp_path == '':
            return None, Error(
                True,
                caller_name(),
                Exception("Provided input shapefile path is empty"),
                traceback.format_exc()
            )

        if not os.path.exists(shp_path):
            return None, Error(
                True,
                caller_name(),
                Exception(f"Input shapefile {shp_path} does not exist")
            )

        # open input vector layer

        ds = ogr.Open(shp_path, 0)

        if ds is None:
            return None, Error(
                True,
                caller_name(),
                Exception(f"Input shapefile {shp_path} not read")
            )

        # get internal layer

        layer = ds.GetLayer()

        # get projection

        try:

            srs = layer.GetSpatialRef()
            srs.AutoIdentifyEPSG()
            authority = srs.GetAuthorityName(None)
            if authority.upper() == "EPSG":
                epsg_cd = int(srs.GetAuthorityCode(None))
            else:
                epsg_cd = -1

        except:

            epsg_cd = -1

        # initialize list storing results

        records = []

        # loop in layer features

        for record in layer:

            # get geometries

            curr_geom = record.GetGeometryRef()

            if curr_geom is None:
                del ds
                return None, Error(
                    True,
                    caller_name(),
                    Exception(f"Input shapefile {shp_path} not read")
                )

            geometry_type = curr_geom.GetGeometryType()

            if geometry_type in ogr_3d_line_types:
                is_3d = True
            else:
                is_3d = False

            if geometry_type in ogr_line_types:

                geom_type = "simpleline"

            elif geometry_type in ogr_multiline_types:

                geom_type = "multiline"

            else:

                del ds
                return None, Error(
                    True,
                    caller_name(),
                    Exception(f"Geometry type is {geometry_type}, line expected")
                )

            if geom_type == "simpleline":

                line = extract_ogr_simple_line(
                    simple_line_geom=curr_geom,
                    has_z=is_3d
                )

                records.append(line)

            else:  # multiline case

                for simple_line_geom in curr_geom:

                    line = extract_ogr_simple_line(
                        simple_line_geom=simple_line_geom,
                        has_z=is_3d
                    )

                    records.append(line)

        del ds

        return (records, epsg_cd), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def read_line_shapefile_with_attributes(
        shp_path: str,
        flds: Optional[List[str]] = None
    ) -> Tuple[Union[type(None), Tuple[List, numbers.Integral]], Error]:
    '''
    Read results geometries from a line shapefile using ogr.

    :param shp_path: line shapefile path.
    :param flds: the fields to extract values from.
    :return: success status and (error_qt message or results).
    '''

    try:

        # check input path

        if shp_path == '':
            return None, Error(
                True,
                caller_name(),
                Exception("Provided input shapefile path is empty"),
                traceback.format_exc()
            )

        if not os.path.exists(shp_path):
            return None, Error(
                True,
                caller_name(),
                Exception(f"Input shapefile {shp_path} does not exist")
            )

        # open input vector layer

        ds = ogr.Open(shp_path, 0)

        if ds is None:
            return None, Error(
                True,
                caller_name(),
                Exception(f"Input shapefile {shp_path} not read")
            )

        # get internal layer

        layer = ds.GetLayer()

        # get projection

        try:

            srs = layer.GetSpatialRef()
            srs.AutoIdentifyEPSG()
            authority = srs.GetAuthorityName(None)
            if authority.upper() == "EPSG":
                epsg_cd = int(srs.GetAuthorityCode(None))
            else:
                epsg_cd = -1

        except:

            epsg_cd = -1

        # initialize list storing results

        records = []

        # loop in layer features

        for record in layer:

            # get attributes

            if flds:

                record_attributes = tuple(map(lambda fld_nm: record.GetField(fld_nm), flds))

            else:

                record_attributes = ()

            # get geometries

            record_geometries = []

            curr_geom = record.GetGeometryRef()

            if curr_geom is None:
                del ds
                return None, Error(
                    True,
                    caller_name(),
                    Exception(f"Input shapefile {shp_path} not read")
                )

            geometry_type = curr_geom.GetGeometryType()

            if geometry_type in ogr_3d_line_types:
                is_3d = True
            else:
                is_3d = False

            if geometry_type in ogr_line_types:

                geom_type = "simpleline"

            elif geometry_type in ogr_multiline_types:

                geom_type = "multiline"

            else:

                del ds
                return None, Error(
                    True,
                    caller_name(),
                    Exception(f"Geometry type is {geometry_type}, line expected")
                )

            if geom_type == "simpleline":

                line = extract_ogr_simple_line(
                    simple_line_geom=curr_geom,
                    has_z=is_3d
                )

                record_geometries.append(line)

            else:  # multiline case

                for simple_line_geom in curr_geom:

                    line = extract_ogr_simple_line(
                        simple_line_geom=simple_line_geom,
                        has_z=is_3d
                    )

                    record_geometries.append(line)

            records.append((record_geometries, record_attributes))

        del ds

        return (records, epsg_cd), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def extract_field_value_from_feature(
        feature, fld_nm):

    return feature.GetField(fld_nm)


def line_from_ogr_linestring_geometry(
    linestring: ogr.Geometry,
    dimension: numbers.Integral
) -> Tuple[Union[type(None), Ln], Error]:
    '''
    Creates an optional Ln instance from a OgrLineString object.

    :param linestring: the input Ogr linestring geometry.
    :param dimension: the dimension of the embedding space.
    :return: the optional line.
    '''

    try:
        if linestring is None:
            return None, Error(
                True,
                caller_name(),
                Exception("Linestring is None")
            )

        coords = []

        for i in range(linestring.GetPointCount()):
            vals = [linestring.GetX(i), linestring.GetY(i)]
            if dimension > 2:
                vals.append(linestring.GetZ(i))

            coords.append(vals)

        return Ln(coords), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def multiline_from_ogr_multilinestring_geometry(
        geom: ogr.Geometry,
        dimension: numbers.Integral
) -> Union[type(None), MultiLine]:
    '''
    Creates an optional MultiLine instance from a OgrMultiLineString object.

    :param geom: the input Ogr multilinestring geometry.
    :param dimension: the dimension of the embedding space.
    :return: the optional multiline.
    '''

    lines = []

    for i in range(0, geom.GetGeometryCount()):

        g = geom.GetGeometryRef(i)
        if g is None:
            continue
        line, err = line_from_ogr_linestring_geometry(g, dimension)
        if err:
            print(f"{err!r} ")
            return None
        lines.append(line)

    if not lines:
        return None

    return MultiLine(lines)


def lines_from_ogr_multilinestring_geometry(
        geom: ogr.Geometry,
        dimension: numbers.Integral = 2
) -> Tuple[Union[type(None), List[Ln]], Error]:
    '''
    Creates a list of lines from a OgrMultiLineString object.

    :param geom: the input Ogr multilinestring geometry.
    :param dimension: the dimension of the embedding space.
    :return: the optional multiline.
    '''

    try:

        lines = []

        for i in range(0, geom.GetGeometryCount()):

            g = geom.GetGeometryRef(i)
            if g is None:
                continue
            line, err = line_from_ogr_linestring_geometry(g, dimension)
            if err:
                return None, err
            lines.append(line)

        return lines, Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def extract_mline_from_feature(
        feature: 'ogr.Feature'
) -> Union[type(None), MLine]:
    '''
    Extract the (multi)linear geometry from a feature.

    :param feature: the (multi)linear OGR feature.
    :return: the optional mline instance.
    '''

    geom = feature.GetGeometryRef()

    if geom is None:
        return None

    geom_type = geom.GetGeometryType()

    if geom_type not in ogr_line_types + ogr_multiline_types:
        return None

    if geom_type in ogr_3d_line_types:
        dimension = 3
    elif geom_type in ogr_2d_line_types:
        dimension = 2
    else:
        return None

    if geom_type in ogr_multiline_types:
        return multiline_from_ogr_multilinestring_geometry(geom, dimension=dimension)
    else:
        line, err = line_from_ogr_linestring_geometry(geom, dimension=dimension)
        if err:
            print(f"{err!r} ")
        return line


def lines_from_ogr_mlinestring_feature(
        feature: 'ogr.Feature',
        dimension: numbers.Integral = 2
) -> Tuple[Union[type(None), List[Ln]], Error]:
    '''
    Extract the (multi)linear geometry from a feature.

    :param feature: the (multi)linear OGR feature.
    :param dimension: the embedding space dimension of the geometry.
    :return: the optional lines list.
    '''

    try:

        geom = feature.GetGeometryRef()

        if geom is None:
            return None, Error(
                True,
                caller_name(),
                Exception("Geometry is None")
            )

        geom_type = geom.GetGeometryType()

        if geom_type not in ogr_line_types + ogr_multiline_types:
            return None, Error(
                True,
                caller_name(),
                Exception(f"Geometry type is {geom_type} instead of a mline one")
            )

        if geom_type in ogr_multiline_types:
            return lines_from_ogr_multilinestring_geometry(geom, dimension=dimension)
        else:
            line, err = line_from_ogr_linestring_geometry(geom, dimension=dimension)
            if err:
                return None, err
            return [line], Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def polygon_from_ogr_polygon_geometry(
    geom: ogr.Geometry,
    dimension: numbers.Integral = 2
) -> Tuple[Union[type(None), Polygon], Error]:
    """
    Info from: https://gis.stackexchange.com/questions/95280/get-the-outer-ring-inner-ring-for-a-given-polygon-using-ogr-python-binding/95284#95284
    Creates an optional Polygon instance from a OGR geometry object.

    :param geom: the input Ogr linestring geometry.
    :param dimension: the dimension of the embedding space.
    :return: the optional polygon and the error status.
    """

    try:
        if geom is None:
            return None, Error(
                True,
                caller_name(),
                Exception("Geometry is None")
            )
        outer_linestring = geom.GetGeometryRef(0)

        outer_ring, err = line_from_ogr_linestring_geometry(
            linestring=outer_linestring,
            dimension=dimension
        )

        if err:
            return None, err

        nbrRings = geom.GetGeometryCount()

        if nbrRings == 1:

            return Polygon(
                outer=outer_ring
            ), Error()

        inner_rings = []

        for r in range(1, nbrRings):

            inner_linestring = geom.GetGeometryRef(r)

            inner_ring, err = line_from_ogr_linestring_geometry(
                linestring=inner_linestring,
                dimension=dimension
            )

            if err:
                return None, err

            inner_rings.append(inner_ring)

        return Polygon(
            outer=outer_ring,
            inner=inner_rings
        ), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def polygons_from_ogr_mpolygon_geometry(
        geom: ogr.Geometry,
        dimension: numbers.Integral = 2
) -> Tuple[Union[type(None), List[Polygon]], Error]:
    '''
    Creates a list of polygons from an Ogr MultiPolygon object.

    :param geom: the input Ogr multilinestring geometry.
    :param dimension: the dimension of the embedding space.
    :return: the optional list of polygons.
    '''

    try:

        polygons = []

        for i in range(0, geom.GetGeometryCount()):

            g = geom.GetGeometryRef(i)
            if g is None:
                continue
            polygon, err = polygon_from_ogr_polygon_geometry(g, dimension)
            if err:
                return None, err
            if polygon is None:
                continue

            polygons.append(polygon)

        return polygons, Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def polygons_from_ogr_mpolygon_feature(
        feature: 'ogr.Feature',
        dimension: numbers.Integral = 2
) -> Tuple[Union[type(None), List[Polygon]], Error]:
    """
    Using infos from: https://gis.stackexchange.com/questions/95280/get-the-outer-ring-inner-ring-for-a-given-polygon-using-ogr-python-binding/95284#95284

    :param feature:
    :param dimension:
    :return:
    """

    try:

        geom = feature.GetGeometryRef()
        if geom is None:
            return None, Error(
                True,
                caller_name(),
                Exception("Geometry is None")
            )
        geom_type = geom.GetGeometryType()

        if geom_type not in ogr_polygon_types + ogr_multipolygon_types:
            return None, Error(
                True,
                caller_name(),
                Exception(f"Geometry type is {geom_type}, not (multi)polygon")
            )

        if geom_type in ogr_multipolygon_types:

            polygons, err = polygons_from_ogr_mpolygon_geometry(geom, dimension=dimension)
            if err:
                return None, err

        else:

            polygon, err = polygon_from_ogr_polygon_geometry(geom, dimension=dimension)
            if err:
                return None, err
            polygons = [polygon]

        return polygons, Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def read_line_shapefile_via_ids(
    shp_path: str,
    id_field_name: str = '',
) -> Tuple[Union[type(None), Tuple[EpsgCode, Dict[str, numbers.Real], Dict[Category, List[Ln]]]], Error]:
    '''
    Read linestring geometries from a shapefile using ogr.

    :param shp_path:  parameter to check.
    :param id_field_name: the name of the field storing the record id value.
    :return: the result of data reading
    '''

    try:

        # check input path

        if shp_path is None or shp_path == '':
            return None, Error(
                True,
                caller_name(),
                Exception('No input path')
            )

        # open input vector layer

        shape_driver = ogr.GetDriverByName("ESRI Shapefile")

        datasource = shape_driver.Open(str(shp_path), 0)

        # layer not read
        if datasource is None:
            return None, Error(
                True,
                caller_name(),
                Exception(f'Unable to open input shapefile {shp_path}')
            )

        # get internal layer
        layer = datasource.GetLayer(0)

        # get vector layer extent
        layer_extent = layer.GetExtent()
        lines_extent = {
            'xmin': layer_extent[0],
            'xmax': layer_extent[1],
            'ymin': layer_extent[2],
            'ymax': layer_extent[3]
        }

        # get projection

        try:

            srs = layer.GetSpatialRef()
            srs.AutoIdentifyEPSG()
            authority = srs.GetAuthorityName(None)
            if authority == "EPSG":
                epsg_cd = int(srs.GetAuthorityCode(None))
            else:
                epsg_cd = -1

        except:

            epsg_cd = -1

        # initialize result dictionary

        lines_dict = defaultdict(list)

        # start reading layer features

        ndx = 0
        feature = layer.GetNextFeature()

        # loop in layer features

        while feature:

            ndx += 1

            lines, err = lines_from_ogr_mlinestring_feature(feature)

            if err:
                return None, err

            if id_field_name:
                rec_id = extract_field_value_from_feature(feature, id_field_name)
            else:
                rec_id = ndx + 1

            lines_dict[rec_id].extend(lines)

            feature.Destroy()

            feature = layer.GetNextFeature()

        datasource.Destroy()

        return (epsg_cd, lines_extent, lines_dict), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def read_polygon_shapefile_via_ids(
    shp_path: str,
    id_field_name: str = '',
) -> Tuple[Union[type(None), Tuple[EpsgCode, Dict[str, numbers.Real], Dict[Category, List[Polygon]]]], Error]:
    '''
    Read polygon geometries from a shapefile using ogr.

    :param shp_path:  parameter to check.
    :param id_field_name: the name of the field storing the record id value.
    :return: the result of data reading and the error status.
    '''

    try:

        # check input path

        if shp_path is None or shp_path == '':
            return None, Error(
                True,
                caller_name(),
                Exception('No input path')
            )

        # open input vector layer

        shape_driver = ogr.GetDriverByName("ESRI Shapefile")

        datasource = shape_driver.Open(str(shp_path), 0)

        # layer not read
        if datasource is None:
            return None, Error(
                True,
                caller_name(),
                Exception(f'Unable to open input shapefile {shp_path}')
            )

        # get internal layer
        layer = datasource.GetLayer(0)

        # get vector layer extent
        layer_extent = layer.GetExtent()
        layer_extent_dict = {
            'xmin': layer_extent[0],
            'xmax': layer_extent[1],
            'ymin': layer_extent[2],
            'ymax': layer_extent[3]
        }

        # get projection

        try:

            srs = layer.GetSpatialRef()
            srs.AutoIdentifyEPSG()
            authority = srs.GetAuthorityName(None)
            if authority == "EPSG":
                epsg_cd = int(srs.GetAuthorityCode(None))
            else:
                epsg_cd = -1

        except:

            epsg_cd = -1

        # initialize result dictionary

        geometries_dict = defaultdict(list)

        # start reading layer features

        ndx = 0
        feature = layer.GetNextFeature()

        # loop in layer features

        while feature:

            ndx += 1

            if id_field_name:
                rec_id = extract_field_value_from_feature(feature, id_field_name)
            else:
                rec_id = ndx + 1

            polygons, err = polygons_from_ogr_mpolygon_feature(feature)

            if err:
                print(f"Feature with index {ndx} in {shp_path} has errors")
            else:
                geometries_dict[rec_id].extend(polygons)

            feature.Destroy()

            feature = layer.GetNextFeature()

        datasource.Destroy()

        return (epsg_cd, layer_extent_dict, geometries_dict), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def parse_ogr_type(ogr_type_str: str) -> 'ogr.OGRFieldType':
    """
    Parse the provided textual field type to return an actual OGRFieldType.

    :param ogr_type_str: the string referring to the ogr field type.
    :return: the actural ogr type.
    :raise: Exception.
    """

    if ogr_type_str.endswith("OFTInteger"):
        return ogr.OFTInteger
    elif ogr_type_str.endswith("OFTIntegerList"):
        return ogr.OFTIntegerList
    elif ogr_type_str.endswith("OFTReal"):
        return ogr.OFTReal
    elif ogr_type_str.endswith("OFTRealList"):
        return ogr.OFTRealList
    elif ogr_type_str.endswith("OFTString"):
        return ogr.OFTString
    elif ogr_type_str.endswith("OFTStringList"):
        return ogr.OFTStringList
    elif ogr_type_str.endswith("OFTBinary"):
        return ogr.OFTBinary
    elif ogr_type_str.endswith("OFTDate"):
        return ogr.OFTDate
    elif ogr_type_str.endswith("OFTTime"):
        return ogr.OFTTime
    elif ogr_type_str.endswith("OFTDateTime"):
        return ogr.OFTDateTime
    elif ogr_type_str.endswith("OFTInteger64"):
        return ogr.OFTInteger64
    elif ogr_type_str.endswith("OFTInteger64List"):
        return ogr.OFTInteger64List
    else:
        raise Exception(f"Unrecognized OGR type: {ogr_type_str}")


def extract_geometry_types_from_shapefile(
    shapefile_pth: str
) -> Tuple[Union[type(None), set], Error]:

    try:

        # open input vector layer
        shape_driver = ogr.GetDriverByName("ESRI Shapefile")

        shapefile = shape_driver.Open(shapefile_pth, 0)

        # layer not read
        if shapefile is None:
            return None, Error(
                True,
                caller_name(),
                Exception('Unable to open input shapefile'),
                traceback.format_exc()
            )

        # get internal layer
        layer = shapefile.GetLayer(0)

        # initialize set storing geometry types

        geometry_types = set()

        # start reading layer features

        feature = layer.GetNextFeature()

        # loop in layer features
        while feature:

            geometry = feature.GetGeometryRef()

            if geometry is None:
                geometry_types.add(None)

            geometry_types.add(geometry.GetGeometryType())

            feature = layer.GetNextFeature()

        shapefile.Destroy()

        return geometry_types, Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def create_shapefile_def_field(
    field_params: Dict,
) -> Tuple[Union[type(None), 'ogr.FieldDefn'], Error]:
    '''
    Creates field definition.

    :param field_params: the field definition dictionary
    :return: the field definition instance
    '''

    try:

        field_name = field_params['name']
        ogr_type = parse_ogr_type(field_params['ogr_type'])

        fieldDef = ogr.FieldDefn(field_name, ogr_type)
        if ogr_type == ogr.OFTString:
            fieldDef.SetWidth(int(field_params['width']))

        return fieldDef, Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc())


def try_create_shapefile_def_field(
        field_def
) -> Tuple[bool, Union[str, 'ogr.FieldDefn']]:
    '''
    DEPRECATED: use 'create_shapefile_def_field'.

    Creates field definition.

    :param field_def: the field definition dictionary
    :return: the field definition instance
    '''

    try:

        name = field_def['name']
        ogr_type = parse_ogr_type(field_def['ogr_type'])

        fieldDef = ogr.FieldDefn(name, ogr_type)
        if ogr_type == ogr.OFTString:
            fieldDef.SetWidth(int(field_def['width']))

        return True, fieldDef

    except Exception as e:

        return False, str(e)


def create_new_shapefile(
    path: str,
    geom_type: int,
    fields_dict_list: List[dict],
    epsg_code: Optional[int] = None
) -> Error:
    '''
    Create a new shapefile.

    The geometric type is a OGRwkbGeometryType: ogr.wkbPoint, ....
    The list of fields is made up by elements with this structure:
        field dict: 'name',
                    'ogr_type': a string, e.g.:
                            'ogr.OFTString',
                            'ogr.wkbLineString',
                            'ogr.wkbLinearRing',
                            'ogr.wkbPolygon'
                    'width',

    :param path: the file path of the shapefile to create.
    :param geom_type: an int representing a OGRwkbGeometryType value.
    :param fields_dict_list: the list storing the dictionary of fields parameters.
    :param epsg_code: the optional EPSG code to attribute to the shapefile to be created.
    :return: the error status.
    '''

    try:

        driver = ogr.GetDriverByName("ESRI Shapefile")

        outShapefile = driver.CreateDataSource(str(path))
        if outShapefile is None:
            return Error(
                True,
                caller_name(),
                Exception(f'Unable to create shapefile in {str(path)}'),
                traceback.format_exc()
            )

        if epsg_code is not None:
            spatial_reference = osr.SpatialReference()
            spatial_reference.ImportFromEPSG(epsg_code)
            outShapelayer = outShapefile.CreateLayer(
                "layer",
                spatial_reference,
                geom_type
            )

        else:

            outShapelayer = outShapefile.CreateLayer(
                "layer",
                None,
                geom_type
            )

        if not outShapelayer:

            return Error(
                True,
                caller_name(),
                Exception(f'Unable to create output shape layer'),
                traceback.format_exc()
            )

        for field_def_params in fields_dict_list:

            field_def, err = create_shapefile_def_field(field_def_params)

            if err:
                return err

            outShapelayer.CreateField(field_def)

        return Error()

    except Exception as e:

        return Error(
                True,
                caller_name(),
                e,
                traceback.format_exc()
            )


def shapefile_create_def_field(field_def):
    """
    Check TO DEPRECATE

    :param field_def:
    :return:
    """

    name = field_def['name']
    ogr_type = parse_ogr_type(field_def['ogr_type'])

    fieldDef = ogr.FieldDefn(name, ogr_type)
    if ogr_type == ogr.OFTString:
        fieldDef.SetWidth(int(field_def['width']))

    return fieldDef


def create_and_open_shapefile(
    path,
    geom_type,
    fields_dict_list,
    crs=None,
) -> Tuple[Union[None, Tuple['gdal.datasource', 'gdal.layer']], Error]:
    """
    crs_prj4: projection in Proj4 text format
    geom_type = OGRwkbGeometryType: ogr.wkbPoint, ....
    list of:
        field dict: 'name',
                    'type': ogr.OFTString,
                            ogr.wkbLineString,
                            ogr.wkbLinearRing,
                            ogr.wkbPolygon,

                    'width',
    """

    try:

        driver = ogr.GetDriverByName("ESRI Shapefile")

        outShapefile = driver.CreateDataSource(str(path))

        if outShapefile is None:
            return None, Error(
                        True,
                        caller_name(),
                        Exception('Unable to save shapefile in provided path'),
                        traceback.format_exc(),
                    )

        if crs is not None:

            spatial_reference = osr.SpatialReference()

            if isinstance(crs, numbers.Integral):
                spatial_reference.ImportFromEPSG(crs)
            else:
                spatial_reference.ImportFromProj4(crs)

            outShapelayer = outShapefile.CreateLayer(
                "layer",
                spatial_reference,
                geom_type
            )

        else:

            outShapelayer = outShapefile.CreateLayer(
                "layer",
                None,
                geom_type
            )

        if not outShapelayer:
            return None, Error(
                        True,
                        caller_name(),
                        Exception('Unable to create layer in shapefile'),
                        traceback.format_exc(),
                    )

        for field_def_params in fields_dict_list:
            field_def = shapefile_create_def_field(field_def_params)
            outShapelayer.CreateField(field_def)

        return (outShapefile, outShapelayer), Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc(),
        )

def create_shapefile(
    path: str,
    geom_type: int,
    fields_dict_list: List[dict],
    epsg_code: Optional[int] = None
) -> Error:
    '''
    Create a new shapefile.

    The geometric type is a OGRwkbGeometryType: ogr.wkbPoint, ....
    The list of fields is made up by elements with this structure:
        field dict: 'name',
                    'ogr_type': a string, e.g.:
                            'ogr.OFTString',
                            'ogr.wkbLineString',
                            'ogr.wkbLinearRing',
                            'ogr.wkbPolygon'
                    'width',

    :param path: the file path of the shapefile to create.
    :param geom_type: an int representing a OGRwkbGeometryType value.
    :param fields_dict_list: the list storing the dictionary of fields parameters.
    :param epsg_code: the optional EPSG code to attribute to the shapefile to be created.
    :return: the error status.
    '''

    try:

        driver = ogr.GetDriverByName("ESRI Shapefile")

        outShapefile = driver.CreateDataSource(str(path))
        if outShapefile is None:
            return Error(
                True,
                caller_name(),
                Exception(f'Unable to create shapefile in {str(path)}'),
                traceback.format_exc()
            )

        if epsg_code is not None:
            spatial_reference = osr.SpatialReference()
            spatial_reference.ImportFromEPSG(epsg_code)
            outShapelayer = outShapefile.CreateLayer(
                "layer",
                spatial_reference,
                geom_type
            )

        else:

            outShapelayer = outShapefile.CreateLayer(
                "layer",
                None,
                geom_type
            )

        if not outShapelayer:

            return Error(
                True,
                caller_name(),
                Exception(f'Unable to create output shape layer'),
                traceback.format_exc()
            )

        """20230917: deactivated since better explicit
        if geom_type in (ogr.wkbPoint, ogr.wkbPoint25D):

            fields_dict_list.extend(
                [
                    dict(name="x", ogr_type="OFTReal"),
                    dict(name="y", ogr_type="OFTReal"),
                ]
            )
            if geom_type == ogr.wkbPoint25D:
                fields_dict_list.append(
                    dict(name="z", ogr_type="OFTReal")
                )
        """

        for field_def_params in fields_dict_list:

            field_def, err = create_shapefile_def_field(field_def_params)

            if err:
                return err

            outShapelayer.CreateField(field_def)

        return Error()

    except Exception as e:

        return Error(
                True,
                caller_name(),
                e,
                traceback.format_exc()
            )


def try_create_shapefile(
    path: str,
    geom_type: int,
    fields_dict_list: List[dict],
    epsg_code: Optional[int] = None
) -> Tuple[bool, str]:
    '''
    DEPRECATED.

    Try creating a new shapefile.
    The geometric type is a OGRwkbGeometryType: ogr.wkbPoint, ....
    The list of fields is made up by elements with this structure:
        field dict: 'name',
                    'ogr_type': a string, e.g.:
                            'ogr.OFTString',
                            'ogr.wkbLineString',
                            'ogr.wkbLinearRing',
                            'ogr.wkbPolygon'
                    'width',

    :param path: the file path of the shapefile to create.
    :param geom_type: an int representing a OGRwkbGeometryType value.
    :param fields_dict_list: the list storing the dictionary of fields parameters.
    :param epsg_code: the optional EPSG code to attribute to the shapefile to be created.
    :return: a success flag and a descriptive message.
    '''

    try:

        driver = ogr.GetDriverByName("ESRI Shapefile")

        outShapefile = driver.CreateDataSource(str(path))
        if outShapefile is None:
            return False, f'Unable to create shapefile in {str(path)}'

        if epsg_code is not None:
            spatial_reference = osr.SpatialReference()
            spatial_reference.ImportFromEPSG(epsg_code)
            outShapelayer = outShapefile.CreateLayer("layer", spatial_reference, geom_type)
        else:
            outShapelayer = outShapefile.CreateLayer("layer", None, geom_type)

        if not outShapelayer:
            return False, "Unable to create output shape layer"

        for field_def_params in fields_dict_list:
            success, result = try_create_shapefile_def_field(field_def_params)
            if not success:
                msg = result
                return False, msg
            field_def = result
            outShapelayer.CreateField(field_def)

        return True, "Shapefile created"

    except Exception as e:

        return False, str(e)


def try_write_pt_shapefile(
        point_layer,
        geoms: List[Tuple[numbers.Real, numbers.Real, numbers.Real]],
        field_names: List[str],
        attrs: List[Tuple]
) -> Tuple[bool, str]:
    '''
    Add point records in an existing shapefile, filling attribute values.

    :param point_layer: the existing shapefile layer in which to write.
    :param geoms: the geometric coordinates of the points, a list of x, y, and z coordinates.
    :param field_names: the field names of the attribute table.
    :param attrs: the values for each record.
    :return: success status and related messages.
    '''

    len_geoms = len(geoms)
    len_attrs = len(attrs)

    if len_geoms != len_attrs:
        return False, "Function error_qt: geometries are {} while attributes are {}".format(len_geoms, len_attrs)

    if len_geoms == 0:
        return True, "No values to be added in shapefile"

    try:

        outshape_featdef = point_layer.GetLayerDefn()

        for ndx_rec in range(len_geoms):

            # pre-processing for new feature in output layer

            curr_Pt_geom = ogr.Geometry(ogr.wkbPoint25D)
            curr_Pt_geom.AddPoint(*geoms[ndx_rec])

            # create a new feature

            curr_pt_shape = ogr.Feature(outshape_featdef)
            curr_pt_shape.SetGeometry(curr_Pt_geom)

            rec_attrs = attrs[ndx_rec]

            for ndx_fld, fld_nm in enumerate(field_names):

                curr_pt_shape.SetField(fld_nm, rec_attrs[ndx_fld])

            # add the feature to the output layer
            point_layer.CreateFeature(curr_pt_shape)

            # destroy no longer used objects
            #curr_Pt_geom.Destroy()
            curr_pt_shape.Destroy()

        del outshape_featdef

        return True, ""

    except Exception as e:

        return False, "Exception: {}".format(e)


def add_points_to_shapefile(
    path: str,
    field_names: List[str],
    values: List[Tuple],
    ndx_x_val: int
) -> Error:
    '''
    Add point records in an existing shapefile, filling attribute values.
    The point coordinates, i.e. x, y, z start at ndx_x_val index (index is zero-based) and are
    assumed to be sequential in order (i.e., 0, 1, 2 or 3, 4, 5).

    :param path: the path of the existing shapefile in which to write.
    :param field_names: the field names of the attribute table.
    :param values: the values for each record.
    :param ndx_x_val: the index of the x coordinate. Y and z should follow.
    :return: error status.
    '''

    try:

        dataSource = ogr.Open(path, 1)

        if dataSource is None:
            return Error(
                True,
                caller_name(),
                Exception("Unable to open shapefile in provided path"),
                traceback.format_exc()
            )

        point_layer = dataSource.GetLayer()

        outshape_featdef = point_layer.GetLayerDefn()

        for pt_vals in values:

            # pre-processing for new feature in output layer
            curr_Pt_geom = ogr.Geometry(ogr.wkbPoint25D)
            curr_Pt_geom.AddPoint(pt_vals[ndx_x_val], pt_vals[ndx_x_val+1], pt_vals[ndx_x_val+2])

            # create a new feature
            curr_pt_shape = ogr.Feature(outshape_featdef)
            curr_pt_shape.SetGeometry(curr_Pt_geom)

            for ndx, fld_nm in enumerate(field_names):

                curr_pt_shape.SetField(fld_nm, pt_vals[ndx])

            # add the feature to the output layer
            point_layer.CreateFeature(curr_pt_shape)

            # destroy no longer used objects
            curr_pt_shape.Destroy()

        del outshape_featdef
        del point_layer
        del dataSource

        return Error()

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def add_lines_to_shapefile(
        path: str,
        field_names: List[str],
        values: Dict
) -> Error:
    '''
    Add line records in an existing shapefile, filling attribute values.

    :param path: the path of the existing shapefile in which to write.
    :param field_names: the field names of the attribute table.
    :param values: the values for each record, a dictionary with values made up by two dictionaries.
    :return: success status and related messages.
    '''

    try:

        dataSource = ogr.Open(path, 1)

        if dataSource is None:
            return Error(
                True,
                caller_name(),
                Exception("Unable to open shapefile in provided path"),
                traceback.format_exc()
            )

        line_layer = dataSource.GetLayer()

        outshape_featdef = line_layer.GetLayerDefn()

        for curr_id in sorted(values.keys()):

            # pre-processing for new feature in output layer
            line_geom = ogr.Geometry(ogr.wkbLineString25D)

            for id_xyz in values[curr_id]["pts"]:
                x, y, z = id_xyz
                line_geom.AddPoint(x, y, z)

            # create a new feature
            line_shape = ogr.Feature(outshape_featdef)
            line_shape.SetGeometry(line_geom)

            for ndx, fld_nm in enumerate(field_names):

                line_shape.SetField(fld_nm, values[curr_id]["vals"][ndx])

            # add the feature to the output layer
            line_layer.CreateFeature(line_shape)

            # destroy no longer used objects
            line_shape.Destroy()

        del outshape_featdef
        del line_layer
        del dataSource

        return Error()

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def write_point_shapefile_from_points(
    path: str,
    id_field: str, # must store integer values
    points: List[List[Point]],
    points_are_3d: bool = False
) -> Error:
    '''
    Add lines in an existing shapefile, filling attribute values.

    :param path: the path of the existing shapefile in which to write.
    :param id_field: the field name of the attribute table.
    :param points: the values for each record.
    :param points_are_3d: whether the point geometry is 3D or 2D. Default is False
    :return: success status and related messages.
    '''

    try:

        if points_are_3d:
            geom_type = ogr.wkbPoint25D
        else:
            geom_type = ogr.wkbPoint

        dataSource = ogr.Open(path, 1)

        if dataSource is None:
            return Error(
                True,
                 caller_name(),
                Exception("Unable to open shapefile in provided path"),
                traceback.format_exc()
            )

        layer = dataSource.GetLayer()

        layer_defn = layer.GetLayerDefn()

        for ndx, line_points in enumerate(points):

            for point in line_points:

                geometry = ogr.Geometry(geom_type)
                geometry.AddPoint(*point.coords)

                # create a new feature

                feature = ogr.Feature(layer_defn)
                feature.SetGeometry(geometry)

                feature.SetField(0, ndx)
                feature.SetField(1, point.x)
                feature.SetField(2, point.y)
                if geom_type == ogr.wkbPoint25D:
                    feature.SetField(3, point.z)
                    
                # add the feature to the output layer
                layer.CreateFeature(feature)

        return Error()

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc())


def write_line_shapefile_from_points(
    path: str,
    id_field: str, # must store integer values
    lines: List[List[Point]],
    lines_are_3d: bool = False
) -> Error:
    '''
    Add lines in an existing shapefile, filling attribute values.

    :param path: the path of the existing shapefile in which to write.
    :param id_field: the field name of the attribute table.
    :param lines: the values for each record.
    :param lines_are_3d: whether the line geometry is 3D or 2D. Default is False
    :return: success status and related messages.
    '''

    try:

        if lines_are_3d:
            geom_type = ogr.wkbLineString25D
        else:
            geom_type = ogr.wkbLineString

        dataSource = ogr.Open(path, 1)

        if dataSource is None:
            return Error(
                True,
                caller_name(),
                Exception("Unable to open shapefile in provided path"),
                traceback.format_exc()
            )

        line_layer = dataSource.GetLayer()

        layer_defn = line_layer.GetLayerDefn()

        for ndx, line in enumerate(lines):

            # pre-processing for new feature in output layer
            line_geom = ogr.Geometry(geom_type)
            for point in line:
                line_geom.AddPoint(*point.coords)

            # create a new feature

            line_shape = ogr.Feature(layer_defn)
            line_shape.SetGeometry(line_geom)

            line_shape.SetField(id_field, ndx)

            # add the feature to the output layer
            line_layer.CreateFeature(line_shape)

        return Error()

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc())


def try_writing_line_shapefile(
    path: str,
    field_names: List[str],
    lines: List[Tuple],
    lines_are_3d: bool = False
) -> Tuple[bool, str]:
    '''
    Add lines in an existing shapefile, filling attribute values.

    :param path: the path of the existing shapefile in which to write.
    :param field_names: the field names of the attribute table.
    :param lines: the values for each record.
    :param lines_are_3d: whether the line geometry is 3D or 2D. Default is False
    :return: success status and related messages.
    '''

    try:

        if lines_are_3d:
            geom_type = ogr.wkbLineString25D
        else:
            geom_type = ogr.wkbLineString

        dataSource = ogr.Open(path, 1)

        if dataSource is None:
            return False, "Unable to open shapefile in provided path"

        line_layer = dataSource.GetLayer()

        layer_defn = line_layer.GetLayerDefn()

        for line, attributes in lines:

            # pre-processing for new feature in output layer
            line_geom = ogr.Geometry(geom_type)
            for point_coords in line:
                line_geom.AddPoint(*point_coords)

            # create a new feature

            line_shape = ogr.Feature(layer_defn)
            line_shape.SetGeometry(line_geom)

            for ndx, fld_nm in enumerate(field_names):
                line_shape.SetField(fld_nm, attributes[ndx])

            # add the feature to the output layer
            line_layer.CreateFeature(line_shape)

        return True, f"Shapefile populated"

    except Exception as e:

        return False, str(e)


def create_write_point_shapefile_from_points(
    shapefile_path: str,
    id_field: Dict,
    records_values: List[List[Point]],
    epsg_code: Union[type(None), numbers.Integral] = None,
    points_are_3d: bool = False
) -> Error:
    '''
    Try creating and populating a line shapefile.

    :param shapefile_path: the path of the shapefile to create and populate.
    :param id_field: the parameters of the lines id field.
    :param records_values: the values to write, as a list of x-y-z coords and attributes pairs.
    :param epsg_code: the EPSG code to attribute to the shapefile.
    :param points_are_3d: whether the point geometries are 3D or 2D. Default is False (2D)
    :return: the error status.
    '''

    try:

        if points_are_3d:
            geom_type = ogr.wkbPoint25D
        else:
            geom_type = ogr.wkbPoint

        err = create_shapefile(
            path=shapefile_path,
            geom_type=geom_type,
            fields_dict_list=[id_field],
            epsg_code=epsg_code
        )

        if err:
            return err

        return write_point_shapefile_from_points(
            path=shapefile_path,
            id_field=id_field["name"],
            points=records_values,
            points_are_3d=points_are_3d
        )

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc())


def create_write_line_shapefile_from_points(
    shapefile_path: str,
    id_field: Dict,
    records_values: List[List[Point]],
    epsg_code: Union[type(None), numbers.Integral] = None,
    lines_are_3d: bool = False
) -> Error:
    '''
    Try creating and populating a line shapefile.

    :param shapefile_path: the path of the shapefile to create and populate.
    :param id_field: the parameters of the lines id field.
    :param records_values: the values to write, as a list of x-y-z coords and attributes pairs.
    :param epsg_code: the EPSG code to attribute to the shapefile.
    :param lines_are_3d: whether the line geometries are 3D or 2D. Default is False (2D)
    :return: the error status.
    '''

    try:

        if lines_are_3d:
            geom_type = ogr.wkbLineString25D
        else:
            geom_type = ogr.wkbLineString

        err = create_shapefile(
            path=shapefile_path,
            geom_type=geom_type,
            fields_dict_list=[id_field],
            epsg_code=epsg_code
        )

        if err:
            return err

        return write_line_shapefile_from_points(
            path=shapefile_path,
            id_field=id_field["name"],
            lines=records_values,
            lines_are_3d=lines_are_3d
        )

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc())


def try_create_write_line_shapefile(
    shapefile_path: str,
    fields_dict_list: List[Dict],
    records_values: List[Tuple],
    epsg_code: Union[type(None), numbers.Integral] = None,
    lines_are_3d: bool = False
) -> Tuple[bool, str]:
    '''
    Try creating and populating a line shapefile.

    :param shapefile_path: the path of the shapefile to create and populate.
    :param fields_dict_list: the list of fields dictionaries.
    :param records_values: the values to write, as a list of x-y-z coords and attributes pairs.
    :param epsg_code: the EPSG code to attribute to the shapefile.
    :param lines_are_3d: whether the line geomtry is 3D or 2D. Default is False (2D)
    :return: a success flag and a descriptive message.
    '''

    try:

        if lines_are_3d:
            geom_type = ogr.wkbLineString25D
        else:
            geom_type = ogr.wkbLineString

        success, msg = try_create_shapefile(
            path=shapefile_path,
            geom_type=geom_type,
            fields_dict_list=fields_dict_list,
            epsg_code=epsg_code
        )

        if not success:
            return False, msg

        return try_writing_line_shapefile(
            path=shapefile_path,
            field_names=[field["name"] for field in fields_dict_list],
            lines=records_values,
            lines_are_3d=lines_are_3d
        )

    except Exception as e:

        return False, str(e)


def ogr_write_point_result(
        point_shapelayer,
        field_list,
        rec_values_list2,
        geom_type=ogr.wkbPoint25D
):
    outshape_featdef = point_shapelayer.GetLayerDefn()

    for rec_value_list in rec_values_list2:

        # pre-processing for new feature in output layer
        curr_Pt_geom = ogr.Geometry(geom_type)
        if geom_type == ogr.wkbPoint25D:
            curr_Pt_geom.AddPoint(rec_value_list[1], rec_value_list[2], rec_value_list[3])
        else:
            curr_Pt_geom.AddPoint(rec_value_list[1], rec_value_list[2])

        # create a new feature
        curr_Pt_shape = ogr.Feature(outshape_featdef)
        curr_Pt_shape.SetGeometry(curr_Pt_geom)

        for fld_name, fld_value in zip(field_list, rec_value_list):
            curr_Pt_shape.SetField(fld_name, fld_value)

        # add the feature to the output layer
        point_shapelayer.CreateFeature(curr_Pt_shape)

        # destroy no longer used objects
        curr_Pt_geom.Destroy()
        curr_Pt_shape.Destroy()

