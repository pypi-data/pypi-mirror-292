
from geogst.core.geometries.grids.rasters import *
from geogst.core.mathematics.utils import are_close


GRID_NULL_VALUE = -99999  # should already be imported but it isn't


class GDALParameters(object):
    """
    Manage GDAL parameters from rasters.

    """

    # class constructor
    def __init__(self):
        """
        Class constructor.

        @return:  generic-case GDAL parameters.
        """
        self._nodatavalue = None
        self._topleftX = None
        self._topleftY = None
        self._pixsizeEW = None
        self._pixsizeNS = None
        self._rows = None
        self._cols = None
        self._rotation_GT_2 = 0.0
        self._rotation_GT_4 = 0.0

    def s_noDataValue(self, nodataval):
        """
        Set raster no data value.

        @param  nodataval:  the raster no-data value.
        @type  nodataval:  None, otherwise number or string convertible to float.

        @return:  self.
        """

        try:
            self._nodatavalue = float(nodataval)
        except:
            self._nodatavalue = None

    def g_noDataValue(self):
        """
        Get raster no-data value.

        @return:  no-data value - float.
        """
        return self._nodatavalue

    # set property for no-data value
    noDataValue = property(g_noDataValue, s_noDataValue)

    def s_topLeftX(self, topleftX):
        """
        Set top-left corner x value of the raster.

        @param  topleftX:  the top-left corner x value, according to GDAL convention.
        @type  topleftX:  number or string convertible to float.

        @return:  self.
        """
        self._topleftX = float(topleftX)

    def g_topLeftX(self):
        """
        Get top-left corner x value of the raster.

        @return:  the top-left corner x value, according to GDAL convention - float.
        """
        return self._topleftX

    # set property for topleftX
    topLeftX = property(g_topLeftX, s_topLeftX)

    def s_topLeftY(self, topleftY):
        """
        Set top-left corner y value of the raster.

        @param  topleftY:  the top-left corner y value, according to GDAL convention.
        @type  topleftY:  number or string convertible to float.

        @return:  self.
        """
        self._topleftY = float(topleftY)

    def g_topLeftY(self):
        """
        Get top-left corner y value of the raster.

        @return:  the top-left corner y value, according to GDAL convention - float.
        """
        return self._topleftY

    # set property for topleftY
    topLeftY = property(g_topLeftY, s_topLeftY)

    def s_pixSizeEW(self, pixsizeEW):
        """
        Set East-West size of the raster cell.

        @param  pixsizeEW:  the top-left y value, according to GDAL convention.
        @type  pixsizeEW:  number or string convertible to float.

        @return:  self.
        """
        self._pixsizeEW = float(pixsizeEW)

    def g_pixSizeEW(self):
        """
        Get East-West size of the raster cell.

        @return:  the East-West size of the raster cell - float.
        """
        return self._pixsizeEW

    # set property for topleftY
    pixSizeEW = property(g_pixSizeEW, s_pixSizeEW)

    # pixsizeNS

    def s_pixSizeNS(self, pixsizeNS):
        """
        Set North-South size of the raster cell.

        @param  pixsizeNS:  the North-South size of the raster cell.
        @type  pixsizeNS:  number or string convertible to float.

        @return:  self.
        """
        self._pixsizeNS = float(pixsizeNS)

    def g_pixSizeNS(self):
        """
        Get North-South size of the raster cell.

        @return:  the North-South size of the raster cell - float.
        """
        return self._pixsizeNS

    # set property for topleftY
    pixSizeNS = property(g_pixSizeNS, s_pixSizeNS)

    def s_rows(self, rows):
        """
        Set row number.

        @param  rows:  the raster row number.
        @type  rows:  number or string convertible to int.

        @return:  self.
        """
        self._rows = int(rows)

    def g_rows(self):
        """
        Get row number.

        @return:  the raster row number - int.
        """
        return self._rows

    # set property for rows
    rows = property(g_rows, s_rows)

    def s_cols(self, cols):
        """
        Set column number.

        @param  cols:  the raster column number.
        @type  cols:  number or string convertible to int.

        @return:  self.
        """
        self._cols = int(cols)

    def g_cols(self):
        """
        Get column number.

        @return:  the raster column number - int.
        """
        return self._cols

    # set property for cols
    cols = property(g_cols, s_cols)

    def s_rotation_GT_2(self, rotation_GT_2):
        """
        Set rotation GT(2) (see GDAL documentation).

        @param  rotation_GT_2:  the raster rotation value GT(2).
        @type  rotation_GT_2:  number or string convertible to float.

        @return:  self.
        """
        self._rotation_GT_2 = float(rotation_GT_2)

    def g_rotation_GT_2(self):
        """
        Get rotation GT(2) (see GDAL documentation).

        @return:  the raster rotation value GT(2). - float.
        """
        return self._rotation_GT_2

    # set property for rotation_GT_2
    rotGT2 = property(g_rotation_GT_2, s_rotation_GT_2)

    def s_rotation_GT_4(self, rotation_GT_4):
        """
        Set rotation GT(4) (see GDAL documentation)

        @param  rotation_GT_4:  the raster rotation value GT(4).
        @type  rotation_GT_4:  number or string convertible to float.

        @return:  self.
        """
        self._rotation_GT_4 = float(rotation_GT_4)

    def g_rotation_GT_4(self):
        """
        Get rotation GT(4) (see GDAL documentation).

        @return:  the raster rotation value GT(4) - float.
        """
        return self._rotation_GT_4

    # set property for rotation_GT_4
    rotGT4 = property(g_rotation_GT_4, s_rotation_GT_4)

    def check_params(self, tolerance=1e-06):
        """
        Check absence of axis rotations or pixel size differences in the raster band.

        @param  tolerance:  the maximum threshold for both pixel N-S and E-W difference, or axis rotations.
        @type  tolerance:  float.

        @return:  None when successful, RasterParametersException when pixel differences or axis rotations.

        @raise: RasterParametersException - raster geometry incompatible with this module (i.e. different cell sizes or axis rotations).
        """
        # check if pixel size can be considered the same in the two axis directions
        if abs(abs(self._pixsizeEW) - abs(self._pixsizeNS)) / abs(self._pixsizeNS) > tolerance:
            raise Exception('Pixel sizes in x and y directions are different in raster')

            # check for the absence of axis rotations
        if abs(self._rotation_GT_2) > tolerance or abs(self._rotation_GT_4) > tolerance:
            raise Exception('There should be no axis rotation in raster')

        return

    def llcorner(self):
        """
        Creates a point at the lower-left corner of the raster.

        @return:  new Point instance.
        """
        return Point(
            self.topLeftX,
            self.topLeftY - abs(self.pixSizeNS) * self.rows
        )

    def trcorner(self):
        """
        Create a point at the top-right corner of the raster.

        @return:  new Point instance.
        """
        return Point(
            self.topLeftX + abs(self.pixSizeEW) * self.cols,
            self.topLeftY
        )

    def geo_equiv(self, other, tolerance=1.0e-6):
        """
        Checks if two rasters are geographically equivalent.

        @param  other:  a grid to be compared with self.
        @type  other:  Grid instance.
        @param  tolerance:  the maximum threshold for pixel sizes, topLeftX or topLeftY differences.
        @type  tolerance:  float.

        @return:  Boolean.
        """
        if 2 * (self.topLeftX - other.topLeftX) / (self.topLeftX + other.topLeftX) > tolerance or \
                                        2 * (self.topLeftY - other.topLeftY) / (
                                    self.topLeftY + other.topLeftY) > tolerance or \
                                        2 * (abs(self.pixSizeEW) - abs(other.pixSizeEW)) / (
                                    abs(self.pixSizeEW) + abs(other.pixSizeEW)) > tolerance or \
                                        2 * (abs(self.pixSizeNS) - abs(other.pixSizeNS)) / (
                                    abs(self.pixSizeNS) + abs(other.pixSizeNS)) > tolerance or \
                        self.rows != other.rows or self.cols != other.cols:
            return False
        else:
            return True


def try_write_esrigrid(
    grid: Grid,
    outgrid_flpth: str,
    esri_nullvalue: numbers.Integral = GRID_NULL_VALUE,
) -> Tuple[bool, str]:
    """
    Writes ESRI ascii grid.

    :param grid:
    :param outgrid_flpth:
    :param esri_nullvalue:
    :return: success and descriptive message
    """

    outgrid_flpth = str(outgrid_flpth)

    # checking existence of output slope grid

    if os.path.exists(outgrid_flpth):
        return False, "Output grid '{}' already exists".format(outgrid_flpth)

    try:
        outputgrid = open(outgrid_flpth, 'w')  # create the output ascii file
    except Exception:
        return False, "Unable to create output grid '{}'".format(outgrid_flpth)

    if outputgrid is None:
        return False, "Unable to create output grid '{}'".format(outgrid_flpth)

    if grid.has_rotation:
        return False, "Grid has axes rotations defined"

    cell_size_x = grid.cellsize_x
    cell_size_y = grid.cellsize_y

    if not are_close(cell_size_x, cell_size_y, rtol=1e-6):
        return False, "Cell sizes in the x- and y- directions are not similar"

    arr = grid.array

    num_rows, num_cols = arr.shape
    _ , _, _, (llc_x, llc_y) = grid.corners_geog()

    # writes header of grid ascii file

    outputgrid.write("NCOLS %d\n" % num_cols)
    outputgrid.write("NROWS %d\n" % num_rows)
    outputgrid.write("XLLCORNER %.8f\n" % llc_x)
    outputgrid.write("YLLCORNER %.8f\n" % llc_y)
    outputgrid.write("CELLSIZE %.8f\n" % cell_size_x)
    outputgrid.write("NODATA_VALUE %f\n" % esri_nullvalue)

    esrigrid_outvalues = np.where(np.isnan(arr), esri_nullvalue, arr)

    # output of results

    for i in range(0, num_rows):
        for j in range(0, num_cols):
            outputgrid.write("%.8f " % (esrigrid_outvalues[i, j]))
        outputgrid.write("\n")

    outputgrid.close()

    return True, "Data saved in {}".format(outgrid_flpth)

