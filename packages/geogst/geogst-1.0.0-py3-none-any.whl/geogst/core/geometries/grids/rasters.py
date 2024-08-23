
import os

from geogst.core.geometries.georeferencing.crs import *
from geogst.core.geometries.georeferencing.geotransform import *
from geogst.core.geometries.grids.operators import *
from geogst.core.geometries.planes import *
from geogst.core.geometries.points import *
from geogst.core.mathematics.arrays import *
from geogst.core.utils.arrays import *
from geogst.core.utils.types import *
from geogst.core.geometries.grids.intersections import *


class GeoArray:
    """
    GeoArray class.
    Stores and process georeferenced raster data.
    """

    def __init__(self,
        geotransform: GeoTransform,
        epsg_code: numbers.Integral = -1,
        arrays: Optional[List[np.ndarray]] = None,
        original_geotransform = None,
        original_projection = None
    ):
        """
        GeoArray class constructor.

        :param geotransform: the geotransform.
        :param epsg_code: the projection EPSG code.
        :param  arrays:  the list of nd-arrays storing the data.
        :param original_geotransform: the source raster original GDAL geotransform.
        :param original_projection: the source raster original GDAL projection.
        """

        self._gt = geotransform
        self._crs = Crs(epsg_code)
        if arrays is None:
            self._levels = []
        else:
            self._levels = arrays

        self.original_geotransform = original_geotransform
        self.original_projection = original_projection

    def geotransform(self):
        """
        Returns geotransform.

        :return: the geotransform.
        :rtype: GeoTransform.
        """

        return self._gt

    @classmethod
    def fromRasterio(cls,
        array: np.ndarray,
        affine_transform: affine.Affine,
        epsg_code: numbers.Integral,
    ):
        """
        Create a GeoArray instance from RasterIO-derived input data.

        :param array: the numpy array with the Geoarray values
        :param affine_transform: the affine transformation from image to geographic coordinates
        :param epsg_code: the EPSG code
        """

        gt = GeoTransform.from_affine(affine_transform)

        return GeoArray(
            geotransform=gt,
            epsg_code=epsg_code,
            arrays=[array]
        )

    @property
    def crs(self) -> Crs:
        """
        Return the geoarray crs.

        :return: the georeferenced.
        """

        return self._crs

    @property
    def epsg_code(self) -> numbers.Integral:
        """
        Return the geoarray georeferenced EPSG code.

        :return: the georeferenced EPSG  code.
        """

        return self.crs.epsg_code

    def define_epsg(self,
                    epsg_cd: numbers.Integral
    ):
        """
        Overwrite the geoarray EPSG code.

        :return:
        """

        if not isinstance(epsg_cd, numbers.Integral):
            raise Exception("Provided EPSG code must be integer")

        self._crs = Crs(epsg_cd)

    def __repr__(self) -> str:
        """
        Represents a GeoArray instance as a shortened text.

        :return: a textual shortened representation of a GeoArray instance.
        """

        num_bands = self.levels_num
        epsg_code = self.epsg_code
        bands_txt = ""
        for band_ndx in range(num_bands):
            band = self.level(level_ndx=band_ndx)
            rows, cols = band.shape
            bmin, bmax = band.min(), band.max()
            bands_txt += f"\nBand {band_ndx+1}: {rows} rows x {cols} cols; min: {bmin},  max: {bmax}"

        txt = f"GeoArray with {num_bands} band(s) - CRS: EPSG: {epsg_code}\n{bands_txt}"

        return txt

    @property
    def src_cellsize_j(self) -> numbers.Real:
        """
        Get the cell size of the geoarray in the x direction.

        :return: cell size in the x (j) direction.

        Examples:
        """

        return abs(self._gt.pixWidth)

    @property
    def src_cellsize_i(self) -> numbers.Real:
        """
        Get the cell size of the geoarray in the y direction.

        :return: cell size in the y (-i) direction.

        Examples:
        """

        return abs(self._gt.pixHeight)

    @property
    def mean_cellsize(self) -> numbers.Real:
        """
        Get the mean cell size of the geoarray.

        :return: mean cell size.

        Examples:
        """

        return (self.src_cellsize_i + self.src_cellsize_j) / 2.0

    @property
    def levels_num(self) -> numbers.Integral:
        """
        Returns the number of levels (dimensions) of the geoarray.

        :return: number of levels.

        Examples:
          >>> gt = GeoTransform(0, 0, 10, 10)
          >>> GeoArray(gt, -1, [np.array([[1, 2], [3, 4]])]).levels_num
          1
          >>> GeoArray(gt, -1, [np.array([[1, 2], [3, 4]]), np.ones((4, 3, 2))]).levels_num
          2
        """

        return len(self._levels)

    def level(self,
              level_ndx: numbers.Integral = 0
    ) -> Union[type(None), np.ndarray]:
        """
        Return the array corresponding to the requested level
        if existing else None.

        :param level_ndx: the index of the requested level.
        :return: the array or None.
        """

        if 0 <= level_ndx < self.levels_num:
            return self._levels[level_ndx]
        else:
            return None

    def level_shape(self,
                    level_ndx: numbers.Integral = 0
    ) -> Optional[Tuple[numbers.Integral, numbers.Integral]]:
        """
        Returns the shape (num. rows and num. columns) of the considered level geoarray.

        :param level_ndx: index of the level (geoarray) to consider.
        :return: number of rows and columns of the specific geoarray.

        Examples:
          >>> gt = GeoTransform(0, 0, 10, 10)
          >>> GeoArray(gt, -1, [np.array([[1, 2], [3, 4]])]).level_shape()
          (2, 2)
          >>> GeoArray(gt, -1, [np.array([[1, 2], [3, 4]]), np.ones((4, 3, 2))]).level_shape(1)
          (4, 3, 2)
        """

        if 0 <= level_ndx < self.levels_num:
            return self._levels[level_ndx].shape
        else:
            return None

    def level_llc(self,
        level_ndx: numbers.Integral = 0
    ) -> Optional[Tuple[numbers.Real, numbers.Real]]:
        """
        Deprecated. Use "band_corners_geogcoords" instead.

        Returns the geographic coordinates of the lower-left corner.

        :param level_ndx: index of the level (geoarray) to consider.
        :return: x and y values of the lower-left corner of the specific geoarray.

        Examples:
        """

        shape = self.level_shape(level_ndx)
        if not shape:
            return None

        llc_i_pix, llc_j_pix = shape[0], 0

        return self.ijPixToxy(llc_i_pix, llc_j_pix)

    def band_corners_pixcoords(self,
        level_ndx: numbers.Integral = 0
    ) -> Tuple[Tuple[numbers.Real, numbers.Real], Tuple[numbers.Real, numbers.Real], Tuple[numbers.Real, numbers.Real], Tuple[numbers.Real, numbers.Real]]:
        """
        Returns the pixel coordinates of the top-left, top-right, bottom-right and bottom-left band corners.

        :param level_ndx: index of the level (geoarray) to consider.
        :return: pixel coordinates of the top-left, top-right, bottom-right and bottom-left band corners.

        Examples:
          >>> gt = GeoTransform(0, 0, 10, 10)
          >>> ga = GeoArray(gt, -1, [np.array([[1, 2, 3], [4, 5, 6]])])
          >>> ga.band_corners_pixcoords()
          ((0.0, 0.0), (0.0, 3.0), (2.0, 3.0), (2.0, 0.0))
        """

        shape = self.level_shape(level_ndx)
        num_rows, num_cols = shape

        top_left_ijpix = (0.0, 0.0)
        top_right_ijpix = (0.0, float(num_cols))
        btm_right_ijpix = (float(num_rows), float(num_cols))
        btm_left_ijpix = (float(num_rows), 0.0)

        return top_left_ijpix, top_right_ijpix, btm_right_ijpix, btm_left_ijpix

    def band_corners_geogcoords(self,
                                level_ndx: numbers.Integral = 0
    ) -> Tuple[Tuple[numbers.Real, numbers.Real], Tuple[numbers.Real, numbers.Real], Tuple[numbers.Real, numbers.Real], Tuple[numbers.Real, numbers.Real]]:
        """
        Returns the geographic coordinates of the top-left, top-right, bottom-right and bottom-left band corners.

        :param level_ndx: index of the level (geoarray) to consider.
        :return: geographic coordinates of the top-left, top-right, bottom-right and bottom-left band corners.

        Examples:
          >>> gt = GeoTransform(1500, 3000, 10, 10)
          >>> ga = GeoArray(gt, -1, [np.array([[1, 2, 3], [4, 5, 6]])])
          >>> ga.band_corners_geogcoords()
          ((1500.0, 3000.0), (1530.0, 3000.0), (1530.0, 2980.0), (1500.0, 2980.0))
        """

        top_left_ijpix, top_right_ijpix, btm_right_ijpix, btm_left_ijpix = self.band_corners_pixcoords(level_ndx=level_ndx)

        top_left_geogcoord = self.ijPixToxy(*top_left_ijpix)
        top_right_geogcoord = self.ijPixToxy(*top_right_ijpix)
        btm_right_geogcoord = self.ijPixToxy(*btm_right_ijpix)
        btm_left_geogcoord = self.ijPixToxy(*btm_left_ijpix)

        return top_left_geogcoord, top_right_geogcoord, btm_right_geogcoord, btm_left_geogcoord

    def xyToijArr(self,
                  x: numbers.Real,
                  y: numbers.Real
    ) -> Tuple[numbers.Real, numbers.Real]:
        """
        Converts from geographic to array coordinates.

        :param x: x geographic component.
        :param y: y geographic component.
        :return: i and j values referred to array.

        Examples:
        """

        return ij_pixel_to_ij_array(*self._gt.xy_geogr_to_ij_pixel(x, y))

    def xyToijPix(self,
                  x: numbers.Real,
                  y: numbers.Real
    ) -> Tuple[numbers.Real, numbers.Real]:
        """
        Converts from geographic to pixel coordinates.

        :param x: x geographic component
        :param y: y geographic component
        :return: i and j values referred to geoarray.

        Examples:
        """

        return self._gt.xy_geogr_to_ij_pixel(x, y)

    def ijArrToxy(self,
                  i: numbers.Real,
                  j: numbers.Real
    ) -> Tuple[numbers.Real, numbers.Real]:
        """
        Converts from array indices to geographic coordinates.
        It automatically converts indices to cell center.
        :param i: i array component.
        :param j: j array component.
        :return: x and y geographic coordinates.
        """

        i_pix, j_pix = ij_array_to_ij_pixel(i, j)

        return self._gt.ij_pixels_to_xy_geogr(i_pix, j_pix)

    def ijPixToxy(self,
      i: numbers.Real,
      j: numbers.Real
    ) -> Tuple[numbers.Real, numbers.Real]:
        """
        Converts from geoarray indices to geographic coordinates.

        :param i: i pixel component.
        :param j: j pixel component.
        :return: x and y geographic coordinates.

        Examples:
        """

        return self._gt.ij_pixels_to_xy_geogr(i, j)

    @property
    def has_rotation(self) -> bool:
        """
        Determines if a geoarray has axis rotations defined.

        :return: true if there are rotations, false otherwise.

        Examples:
        """

        return self._gt.has_rotation

    def geotransf_cell_sizes(self) -> Tuple[numbers.Real, numbers.Real]:
        """
        Calculates the geotransformed cell sizes.

        :return: a pair of numbers.Real values, representing the cell sizes in the j and i directions.
        """

        factor = 100

        start_pt = Point(*self.ijArrToxy(0, 0))
        end_pt_j = Point(*self.ijArrToxy(0, factor))
        end_pt_i = Point(*self.ijArrToxy(factor, 0))

        return end_pt_j.distance(start_pt) / factor, end_pt_i.distance(start_pt) / factor

    def cell_centers_xy_arrays(self,
                               level_ndx: numbers.Integral = 0
    ) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Returns the two arrays storing respectively the x and the y coordinates
        of the geoarray cell centers for the chosen level (default is first level).

        :param level_ndx: the index of the
        :return: two arrays storing the geographical coordinates of the geoarray centers.

        Examples:
        """

        res = self.level_shape(level_ndx)

        if not res:

            return None

        else:

            num_rows, num_cols = res
            X = np.zeros((num_rows, num_cols), dtype=np.float64)
            Y = np.zeros((num_rows, num_cols), dtype=np.float64)
            for i in range(num_rows):
                for j in range(num_cols):
                    x, y = self._gt.ij_pixels_to_xy_geogr(i + 0.5, j + 0.5)
                    X[i, j] = x
                    Y[i, j] = y

            return X, Y

    def interpolate_bilinear(self,
         x: numbers.Real,
         y: numbers.Real,
         level_ndx=0
    ) -> Union[type(None), numbers.Real]:
        """
        Interpolate the z value at a point, given its geographic coordinates.
        Interpolation method: bilinear.

        :param x: x geographic coordinate.
        :param y: y geographic coordinate.
        :param level_ndx: the index of the used array.
        :return: the interpolated z value.
        """

        i, j = self.xyToijArr(x, y)

        return array_bilin_interp(self._levels[level_ndx], i, j)

    def interpolate_bilinear_point(self,
        pt: Point,
        level_ndx: numbers.Integral = 0
    ) -> Union[type(None), Point]:
        """
        Interpolate the z value at a point, returning a Point with elevation extracted from the DEM.
        Interpolation method: bilinear.

        :param pt: the positional point.
        :param level_ndx: the geoarray instance level to use for interpolation calculation.
        :return: a point with the same x-y position of the input point and with z equal to the interpolated z value.
        """

        try:

            check_type(pt, "Input point", Point)

            x, y = pt.x, pt.y

            z = self.interpolate_bilinear(
                x=x,
                y=y,
                level_ndx=level_ndx)

            if z is not None:
                return Point(x, y, z)
            else:
                return None

        except Exception as e:

            err = Error(
                True,
                caller_name(),
                e,
                traceback.format_exc()
            )
            print(f"{err!r}")
            return None

    def magnitude_field(self,
                        ndx_fx=0,
                        ndx_fy=1
    ) -> 'GeoArray':
        """
        Calculates magnitude field as a geoarray.

        :param ndx_fx: index of x field.
        :param ndx_fy: index of y field.
        :return: a geoarray storing the magnitude field.

        Examples:
        """

        magn = magnitude(
            fld_x=self._levels[ndx_fx],
            fld_y=self._levels[ndx_fy])

        return GeoArray(
            geotransform=self._gt,
            epsg_code=self.epsg_code,
            arrays=[magn]
        )

    def orientations(self,
                     ndx_fx=0,
                     ndx_fy=1
    ) -> 'GeoArray':
        """
        Calculates orientations field as a geoarray.

        :param ndx_fx: index of x field.
        :param ndx_fy: index of y field.
        :return: a geoarray storing the orientation field.

        Examples:
        """

        orient = orients_d(
            fld_x=self._levels[ndx_fx],
            fld_y=self._levels[ndx_fy])

        return GeoArray(
            geotransform=self._gt,
            epsg_code=self.epsg_code,
            arrays=[orient]
        )

    def divergence_2D(self,
                      ndx_fx=0,
                      ndx_fy=1
    ) -> 'GeoArray':
        """
        Calculates divergence of a 2D field as a geoarray.

        :param ndx_fx: index of x field.
        :param ndx_fy: index of y field.
        :return: a geoarray storing the divergence field.

        Examples:
        """

        div = divergence(
            fld_x=self._levels[ndx_fx],
            fld_y=self._levels[ndx_fy],
            cell_size_x=self.src_cellsize_j,
            cell_size_y=self.src_cellsize_i)

        return GeoArray(
            geotransform=self._gt,
            epsg_code=self.epsg_code,
            arrays=[div]
        )

    def curl_module(self,
                    ndx_fx=0,
                    ndx_fy=1
    ) -> 'GeoArray':
        """
        Calculates curl module of a 2D field as a geoarray.

        :param ndx_fx: index of x field.
        :param ndx_fy: index of y field.
        :return: a geoarray storing the curl module field.

        Examples:
        """

        curl_m = curl_module(
            fld_x=self._levels[ndx_fx],
            fld_y=self._levels[ndx_fy],
            cell_size_x=self.src_cellsize_j,
            cell_size_y=self.src_cellsize_i)

        return GeoArray(
            geotransform=self._gt,
            epsg_code=self.epsg_code,
            arrays=[curl_m])

    def magnitude_grads(self,
                        axis: str= '',
                        ndx_fx: numbers.Integral=0,
                        ndx_fy: numbers.Integral=1
    ) -> 'GeoArray':
        """
        Calculates the magnitude gradient along the x, y axis or both, of a 2D field as a geoarray.

        :param axis: axis along wich to calculate the gradient, 'x' or 'y', or '' (predefined) for both x and y.
        :param ndx_fx: index of x field.
        :param ndx_fy: index of y field.
        :return: a geoarray storing the magnitude gradient along the x, y axis (or both) field.
        :raises: Exception.

        Examples:
        """

        if axis == 'x':
            cell_sizes = [self.src_cellsize_j]
        elif axis == 'y':
            cell_sizes = [self.src_cellsize_i]
        elif axis == '':
            cell_sizes = [self.src_cellsize_j, self.src_cellsize_i]
        else:
            raise Exception("Axis must be 'x' or 'y. '{}' given".format(axis))

        magnitude_gradients = magn_grads(
            fld_x=self._levels[ndx_fx],
            fld_y=self._levels[ndx_fy],
            dir_cell_sizes=cell_sizes,
            axis=axis)

        return GeoArray(
            geotransform=self._gt,
            epsg_code=self.epsg_code,
            arrays=magnitude_gradients)

    def grad_flowlines(self,
                       ndx_fx: numbers.Integral=0,
                       ndx_fy: numbers.Integral=1
                       ) -> 'GeoArray':
        """
        Calculates gradient along flow lines.

        :param ndx_fx: index of x field.
        :param ndx_fy: index of y field.
        :return: a geoarray storing the flowline gradient field
        """

        flowln_grad = magn_grad_along_flowlines(
            fld_x=self._levels[ndx_fx],
            fld_y=self._levels[ndx_fy],
            cell_size_x=self.src_cellsize_j,
            cell_size_y=self.src_cellsize_i)

        return GeoArray(
            geotransform=self._gt,
            epsg_code=self.epsg_code,
            arrays=[flowln_grad])

    def zoom_in(
        self,
        level_ndx: numbers.Integral,
        zoom_factor: numbers.Real
    ) -> Tuple[Union[type(None), 'GeoArray'], Error]:
        """
        Created a new geoarray zoomed to the center by the given zoom factor.
        """

        try:

            arr = self.level(level_ndx=level_ndx)

            rows, cols = arr.shape

            left_pixel, right_pixel, top_pixel, bottom_pixel = pixels_zoom(cols, rows, zoom_factor)

            # upper-left corner of upper-left pixel x & y coordinates
            ulc_ulp_x, ulc_ulp_y = self.geotransform().ij_pixels_to_xy_geogr(
                i=left_pixel,
                j=top_pixel
            )

            resized_geotransform = self.geotransform().shifted(
                ulc_ulp_x,
                ulc_ulp_y
            )

            resized_array = arr[top_pixel:bottom_pixel, left_pixel:right_pixel]

            return GeoArray(
                geotransform=resized_geotransform,
                epsg_code=self.epsg_code,
                arrays=[np.copy(resized_array)]
            ), Error()

        except Exception as e:

            return None, Error(
                True,
                caller_name(),
                e,
                traceback.format_exc())


def line_on_grid(
        ga: GeoArray,
        profile_line: Ln
) -> Optional[Ln]:
    """
    Calculates a line draped on a grid.

    :param ga: grid
    :param profile_line: the profile line.
    :return: the profile.
    """

    coords = []

    for point in profile_line.pts():

        z = ga.interpolate_bilinear(point.x, point.y)
        if z:
            coords.append([point.x, point.y, z])

    return Ln(coords)


def ij_array_coords_to_xyz_coords(
        ijarr2xy_func: Callable,
        xy2z_func: Callable,
        i: numbers.Real,
        j: numbers.Real
) -> Tuple[numbers.Real, numbers.Real, numbers.Real]:
    """
    Return a tuple of (x, y, z) values, starting by array indices.

    :param ijarr2xy_func: a function converting from array to geographic coordinates.
    :param xy2z_func: a callable converting from x, y geographic coordinates to a z value.
    :param i: i index.
    :param j: j index.
    :return: Point
    """

    x, y = ijarr2xy_func(i, j)
    z = xy2z_func(x, y)
    return x, y, z


def array_ij_to_segment_slope(
    xy2z_func: Callable,
    arrij2xy_func: Callable,
    i_end: numbers.Real,
    j_end: numbers.Real,
    i_start=0.0,
    j_start=0.0
) -> Union[type(None), numbers.Real]:
    """
    Calculates the tangent of the segment slope along a gridded direction defined by its end point i, j array coordinates.
    Default start point is at array coordinates 0, 0.

    :param xy2z_func: a callable calculating a z value from geographic x-y coordinates..
    :param arrij2xy_func: a function to convert from array coordinates to geographic coordinates.
    :param i_end: i index of end point.
    :param j_end: j index of end point.
    :param i_start: i index of start point. Default is 0.0.
    :param j_start: j index of start point. Default is 0.0.
    :return: tangent of segment slope.
    """

    start_point = Point(*ij_array_coords_to_xyz_coords(
        ijarr2xy_func=arrij2xy_func,
        xy2z_func=xy2z_func,
        i=i_start,
        j=j_start))

    end_point = Point(*ij_array_coords_to_xyz_coords(
        ijarr2xy_func=arrij2xy_func,
        xy2z_func=xy2z_func,
        i=i_end,
        j=j_end))

    return Segment(start_point, end_point).tan_slope_angle()


def intersections_normalized_indices(
    m_arr1: np.ndarray,
    m_arr2: np.ndarray,
    q_arr1: np.ndarray,
    q_arr2: np.ndarray,
    cell_size: numbers.Real,
    m_delta_tol: Optional[numbers.Real] = 1e-9,
    q_delta_tol: Optional[numbers.Real] = 1e-9
) -> np.ndarray:
    """
    Creates array storing the residual index [0-1[ of the intersection
    between segments along the considered array axis (i or j)
    whose m (slope) and q (y-axis intersection) values
    along the considered array axis (i or j)
    are defined in the two pairs of input arrays.

    :param m_arr1: array storing values of grid 1 segment slopes.
    :param m_arr2: array storing values of grid 2 segment slopes.
    :param q_arr1: array storing values of grid 1 segment y-axis intersections.
    :param q_arr2: array storing values of grid 2 segment y-axis intersections.
    :param cell_size: cell size of the two io along the considered direction. Required the same in the two io.
    :param m_delta_tol: optional tolerance for delta between grid 1 and grid 2 segment slopes.
    :param q_delta_tol: optional tolerance for delta between grid 1 and grid 2 segment y-axis intersections.
    :return: array with values of intersection residual indices [0 - 1[
    """

    # if segments slope are not sub-equal,
    # we calculate the intersection residual slope
    # using the required formula

    # m and q are the angular coefficient and the intercept of each segment
    # the two segments intercept at m1*x + q1 = m2*x + q2

    intersections_normalized_indices_array = np.where(
        abs(m_arr1 - m_arr2) < m_delta_tol,
        np.NaN,
        (q_arr2 - q_arr1) / (cell_size * (m_arr1 - m_arr2))
    )

    # if the elevations at the left cell center are sub-equal,
    # the residual index is set to 0.0, i.e. there is an intersection at the left cell

    intersections_normalized_indices_array = np.where(
        abs(q_arr1 - q_arr2) < q_delta_tol,
        0.0,
        intersections_normalized_indices_array
    )

    # we filter out residual indices that do not intersect cell range, i.e., are not between 0.0 (included) and 1.0 (excluded)

    within_cell_intersections_normalized_indices = np.where(
        np.logical_and(
            intersections_normalized_indices_array >= 0.0,
            intersections_normalized_indices_array < 1.0
        ),
        intersections_normalized_indices_array,
        np.NaN
    )

    return within_cell_intersections_normalized_indices


def points3d_from_array_residual_indices(
        direction: str,
        arr: np.ndarray,
        ij2xy_func: Callable,
        xy2z_func: Callable
) -> List[Point]:
    """
    Converts an array of along-direction (i- or j-) intra-cell segments [0 -> 1[ into
    a list of 3D points.

    :param direction: considered intersection direction: 'i' (for i axis) or 'j' (for j axis).
    :param arr: array of along-direction (i- or j-) intra-cell segments [0 -> 1[.
    :param ij2xy_func: function to convert from array indices to x-y geographic coordinates.
    :param xy2z_func: function that calculates z value given x and y coordinates.
    :return: list of 3D points.
    :raise: Exception when direction is not 'i' or 'j'
    """

    pts = []
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            val = arr[i, j]
            if np.isfinite(val):
                if direction == 'i':
                    i_int, j_int = i + val, j
                elif direction == 'j':
                    i_int, j_int = i, j + val
                else:
                    raise Exception('Unexpected array direction value: {}'.format(direction))
                x, y = ij2xy_func(i_int, j_int)
                z = xy2z_func(x, y)
                pts.append(Point(x, y, z))

    return pts


def points3d_from_dem_and_array_res_indices(
        direction: str,
        arr: np.ndarray,
        ij2xy_func: Callable,
        geoarray: GeoArray
) -> Tuple[Union[type(None), List[Point]], Error]:
    """
    Converts an array of along-direction (i- or j-) intra-cell segments [0 -> 1[ into
    a list of 3D points.

    :param direction: considered intersection direction: 'i' (for i axis) or 'j' (for j axis).
    :param arr: array of along-direction (i- or j-) intra-cell segments [0 -> 1[.
    :param ij2xy_func: function to convert from array indices to x-y geographic coordinates.
    :param geoarray: the geoarray to use for the 3D point calculation.
    :return: list of 3D points.
    """

    try:

        pts = []
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                val = arr[i, j]
                if np.isfinite(val):
                    if direction == 'i':
                        i_int, j_int = i + val, j
                    elif direction == 'j':
                        i_int, j_int = i, j + val
                    else:
                        raise Exception(f'Unexpected array direction value: {direction}')
                    x, y = ij2xy_func(i_int, j_int)
                    pt = geoarray.interpolate_bilinear_point(Point(x, y))
                    if pt is not None:
                        pts.append(pt)

        return pts, Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def plane_dem_intersections_strategy_2(
        plane_attitude: Plane,
        source_point: Point,
        geoarray: GeoArray,
        level_ndx: numbers.Integral = 0
) -> Tuple[Union[type(None), List[Point]], Error]:
    """
    Calculates the intersections (as points) between the grid and a planar analytical surface.

    :param plane_attitude: orientation of the surface (currently only planes).
    :param source_point: point that the plane must contain.
    :param geoarray: the input GeoArray storing the used grid.
    :param level_ndx: the grid level to use from the provided grid. Default is first (index equal to zero).
    :return: list of unique intersecting points and error status.
    """

    try:

        # dem values as a Numpy array

        q_dem = geoarray.level(
            level_ndx=level_ndx)

        # row and column numbers of the dem

        row_num, col_num = q_dem.shape

        # plane closure that, given (x, y), derive z

        plane_z_closure = closure_plane_from_geo(
            plane_attitude,
            source_point
        )

        # plane elevations at grid cell centers

        q_plane = np.asarray(array_from_geotransform_function(
                row_num=row_num,
                col_num=col_num,
                geotransform=geoarray.geotransform(),
                z_transfer_func=plane_z_closure,
                i_shift=0.5,
                j_shift=0.5
            )
        )

        # calculate angular coefficients of the plane in the two orthogonal directions i and j

        index_multiplier = 100  # sufficiently large value to ensure a precise slope values

        # slopes of the plane along the -i direction
        # note: cell-center shift is irrelevant

        m_plane_i = - array_ij_to_segment_slope(
            xy2z_func=plane_z_closure,
            arrij2xy_func=geoarray.ijArrToxy,
            i_end=index_multiplier,
            j_end=0) * np.ones((row_num, col_num))

        # slopes of the plane along the j direction
        # note: cell-center shift is irrelevant

        m_plane_j = array_ij_to_segment_slope(
            xy2z_func=plane_z_closure,
            arrij2xy_func=geoarray.ijArrToxy,
            i_end=0,
            j_end=index_multiplier) * np.ones((row_num, col_num))

        # 2D array of DEM segment parameters

        cell_size_j, cell_size_i = geoarray.geotransf_cell_sizes()

        # gradient of the dem array along the -i direction
        # as computed, the values at to be intended to refer to the cell center

        m_dem_i = - np.diff(q_dem, axis=0) / cell_size_i

        # gradient of the dem array along the j direction
        # as computed, the values at to be intended to refer to the cell center

        m_dem_j = np.diff(q_dem, axis=1) / cell_size_j

        # intersection points

        intersection_pts_j = intersections_normalized_indices(
            m_arr1=m_dem_j,
            m_arr2=m_plane_j[:, :-1],
            q_arr1=q_dem[:, :-1],
            q_arr2=q_plane[:, :-1],
            cell_size=cell_size_j
        )

        intersection_pts_along_x, err = points3d_from_dem_and_array_res_indices(
            direction='j',
            arr=intersection_pts_j,
            ij2xy_func=geoarray.ijArrToxy,
            geoarray=geoarray
        )

        if err:
            return None, err

        intersection_pts_i = intersections_normalized_indices(
            m_arr1=m_dem_i,
            m_arr2=m_plane_i[:-1, :],
            q_arr1=q_dem[:-1, :],
            q_arr2=q_plane[:-1, :],
            cell_size=cell_size_i
        )

        intersection_pts_along_minus_y, err = points3d_from_dem_and_array_res_indices(
            direction='i',
            arr=intersection_pts_i,
            ij2xy_func=geoarray.ijArrToxy,
            geoarray=geoarray
        )

        if err:
            return None, err

        intersection_points = intersection_pts_along_x + intersection_pts_along_minus_y

        return intersection_points, Error()

    except Exception as e:

        return None, Error(
            True,
            caller_name(),
            e,
            traceback.format_exc()
        )


def point_velocity(
        geoarray: GeoArray,
        pt: Point
) -> Union[type(None), Tuple[numbers.Real, numbers.Real]]:
    """
    TODO: since it assumes a two level geoarray, it is better to provide explicitly two grids, decoupling from geoarray.
    Return the velocity components of a 2D-flow field at a point location, based on bilinear interpolation.

    :param geoarray: the flow field expressed as a GeoArray.
    :param pt: the point for which the velocity comnponents are extracted.
    :return: the x and y velocity components of the flow field at the point location.
    """

    x, y = pt.xy()

    vx = geoarray.interpolate_bilinear(
        x=x,
        y=y,
        level_ndx=0)

    if vx is None:
        return None

    vy = geoarray.interpolate_bilinear(
        x=x,
        y=y,
        level_ndx=1)

    if vy is None:
        return None

    return vx, vy


def interpolate_rkf(
        geoarray: GeoArray,
        delta_time: numbers.Real,
        start_pt: Point
    ) -> Union[type(None), Tuple[Point, numbers.Real]]:
    """
    TODO: since it assumes a two level geoarray, it is better to provide explicitly two grids, decoupling from geoarray.
    Interpolate point-like object position according to the Runge-Kutta-Fehlberg method.

    :param geoarray: the flow field expressed as a GeoArray.
    :param delta_time: the flow field expressed as a GeoArray.
    :param start_pt: the initial point.
    :return: the estimated point-like object position at the incremented time, with the estimation error.
    """

    result = point_velocity(geoarray, start_pt)
    if result is None:
        return None
    k1_vx, k1_vy = result

    k2_pt = Point(
        start_pt.x + 0.25 * delta_time * k1_vx,
        start_pt.y + 0.25 * delta_time * k1_vy
    )

    result = point_velocity(geoarray, k2_pt)
    if result is None:
        return None
    k2_vx, k2_vy = result

    k3_pt = Point(
        start_pt.x + (3.0 / 32.0) * delta_time * k1_vx + (9.0 / 32.0) * delta_time * k2_vx,
        start_pt.y + (3.0 / 32.0) * delta_time * k1_vy + (9.0 / 32.0) * delta_time * k2_vy
    )

    result = point_velocity(geoarray, k3_pt)
    if result is None:
        return None
    k3_vx, k3_vy = result

    k4_pt = Point(
        start_pt.x + (1932.0 / 2197.0) * delta_time * k1_vx - (7200.0 / 2197.0) * delta_time * k2_vx + (7296.0 / 2197.0) * delta_time * k3_vx,
        start_pt.y + (1932.0 / 2197.0) * delta_time * k1_vy - (7200.0 / 2197.0) * delta_time * k2_vy + (7296.0 / 2197.0) * delta_time * k3_vy
    )

    result = point_velocity(geoarray, k4_pt)
    if result is None:
        return None
    k4_vx, k4_vy = result

    k5_pt = Point(
        start_pt.x + (439.0 / 216.0) * delta_time * k1_vx - 8.0 * delta_time * k2_vx + (3680.0 / 513.0) * delta_time * k3_vx - (845.0 / 4104.0) * delta_time * k4_vx,
        start_pt.y + (439.0 / 216.0) * delta_time * k1_vy - 8.0 * delta_time * k2_vy + (3680.0 / 513.0) * delta_time * k3_vy - (845.0 / 4104.0) * delta_time * k4_vy
    )

    result = point_velocity(geoarray, k5_pt)
    if result is None:
        return None
    k5_vx, k5_vy = result

    k6_pt = Point(
        start_pt.x - (8.0 / 27.0) * delta_time * k1_vx + 2.0 * delta_time * k2_vx - (3544.0 / 2565.0) * delta_time * k3_vx + (1859.0 / 4104.0) * delta_time * k4_vx - (
                          11.0 / 40.0) * delta_time * k5_vx,
        start_pt.y - (8.0 / 27.0) * delta_time * k1_vy + 2.0 * delta_time * k2_vy - (3544.0 / 2565.0) * delta_time * k3_vy + (1859.0 / 4104.0) * delta_time * k4_vy - (
                          11.0 / 40.0) * delta_time * k5_vy
    )

    result = point_velocity(geoarray, k6_pt)
    if result is None:
        return None
    k6_vx, k6_vy = result

    rkf_4o_x = start_pt.x + delta_time * (
            (25.0 / 216.0) * k1_vx + (1408.0 / 2565.0) * k3_vx + (2197.0 / 4104.0) * k4_vx - (
            1.0 / 5.0) * k5_vx)
    rkf_4o_y = start_pt.y + delta_time * (
            (25.0 / 216.0) * k1_vy + (1408.0 / 2565.0) * k3_vy + (2197.0 / 4104.0) * k4_vy - (
            1.0 / 5.0) * k5_vy)
    temp_pt = Point(
        rkf_4o_x,
        rkf_4o_y
    )

    interp_x = start_pt.x + delta_time * (
            (16.0 / 135.0) * k1_vx + (6656.0 / 12825.0) * k3_vx + (28561.0 / 56430.0) * k4_vx - (
            9.0 / 50.0) * k5_vx + (2.0 / 55.0) * k6_vx)
    interp_y = start_pt.y + delta_time * (
            (16.0 / 135.0) * k1_vy + (6656.0 / 12825.0) * k3_vy + (28561.0 / 56430.0) * k4_vy - (
            9.0 / 50.0) * k5_vy + (2.0 / 55.0) * k6_vy)
    interp_pt = Point(
        interp_x,
        interp_y
    )

    interp_pt_error_estim = interp_pt.distance(temp_pt)

    return interp_pt, interp_pt_error_estim


class Grid:
    """
    Represent a grid.
    """

    def __init__(self,
        array: np.ndarray,
        geotransform: GeoTransform,
        epsg_code: numbers.Integral = -1,
        projection = None
    ):
        """
        Grid constructor.

        :param array: the nd-array storing the data.
        :param geotransform: the geotransform.
        """

        self._geotransform = geotransform
        self._array = array
        self._epsg_code = epsg_code
        self._projection = projection

    @property
    def array(self) -> np.ndarray:
        """
        Returns the array.

        :return: the array.
        """

        return self._array

    def row_num(self):
        """
        Get row number of the grid domain.

        @return: number of rows of data array - int.
        """
        return np.shape(self.array)[0]

    def col_num(self):
        """
        Get column number of the grid domain.

        @return: number of columns of data array - int.
        """
        return np.shape(self.array)[1]

    @property
    def geotransform(self) -> GeoTransform:
        """
        Returns geotransform.

        :return: the geotransform.
        """

        return self._geotransform

    @property
    def epsg_code(self) -> numbers.Integral:
        """
        Returns the grid EPSG code.
        """

        return self._epsg_code

    @property
    def projection(self) -> Union[type(None), 'gdal.Projection']:

        return self._projection

    def __repr__(self) -> str:
        """
        Represents a Grid instance as a shortened text.

        :return: a textual shortened representation of a Grid instance.
        """

        rows, cols = self.array.shape

        return f"Grid with {rows} rows and {cols} columns - EPSG code {self.epsg_code}"

    @property
    def cellsize_x(self) -> numbers.Real:
        """
        Get the cell size of the grid in the x direction.

        :return: cell size in the x (j) direction.
        """

        return abs(self._geotransform.pixWidth)

    @property
    def cellsize_y(self) -> numbers.Real:
        """
        Get the cell size of the grid in the y direction.

        :return: cell size in the y (-i) direction.
        """

        return abs(self._geotransform.pixHeight)

    @property
    def cellsize_mean(self) -> numbers.Real:
        """
        Get the mean cell size of the grid.

        :return: the mean cell size.
        """

        return (self.cellsize_x + self.cellsize_y) / 2.0

    def corners_pixel(self,
    ) -> Tuple[Tuple[numbers.Real, numbers.Real], Tuple[numbers.Real, numbers.Real], Tuple[numbers.Real, numbers.Real], Tuple[numbers.Real, numbers.Real]]:
        """
        Returns  the top-left, top-right, bottom-right
        and bottom-left grid cell corners as pixel coordinates.

        :return: pixel coordinates of the top-left, top-right, bottom-right and bottom-left band corners.

        Examples:
          >>> gt = GeoTransform(0, 0, 10, 10)
          >>> g = Grid(np.array([[1, 2, 3], [4, 5, 6]]), gt)
          >>> g.corners_pixel()
          ((0.0, 0.0), (0.0, 3.0), (2.0, 3.0), (2.0, 0.0))
        """

        num_rows, num_cols = self.array.shape

        top_left_ijpix = (0.0, 0.0)
        top_right_ijpix = (0.0, float(num_cols))
        btm_right_ijpix = (float(num_rows), float(num_cols))
        btm_left_ijpix = (float(num_rows), 0.0)

        return top_left_ijpix, top_right_ijpix, btm_right_ijpix, btm_left_ijpix

    def corners_geog(self,
    ) -> Tuple[Tuple[numbers.Real, numbers.Real], Tuple[numbers.Real, numbers.Real], Tuple[numbers.Real, numbers.Real], Tuple[numbers.Real, numbers.Real]]:
        """
        Returns the geographic coordinates of the top-left, top-right, bottom-right and bottom-left band corners.

        :return: geographic coordinates of the top-left, top-right, bottom-right and bottom-left band corners.

        Examples:
          >>> gt = GeoTransform(1500, 3000, 10, 10)
          >>> g = Grid(np.array([[1, 2, 3], [4, 5, 6]]), gt)
          >>> g.corners_geog()
          ((1500.0, 3000.0), (1530.0, 3000.0), (1530.0, 2980.0), (1500.0, 2980.0))
        """

        top_left_ijpix, top_right_ijpix, btm_right_ijpix, btm_left_ijpix = self.corners_pixel()

        top_left_geogcoord = self.ijPixToxy(*top_left_ijpix)
        top_right_geogcoord = self.ijPixToxy(*top_right_ijpix)
        btm_right_geogcoord = self.ijPixToxy(*btm_right_ijpix)
        btm_left_geogcoord = self.ijPixToxy(*btm_left_ijpix)

        return top_left_geogcoord, top_right_geogcoord, btm_right_geogcoord, btm_left_geogcoord

    def xyToijArr(self,
        x: numbers.Real,
        y: numbers.Real
    ) -> Tuple[numbers.Real, numbers.Real]:
        """
        Converts from geographic to array coordinates.

        :param x: x geographic component.
        :param y: y geographic component.
        :return: i and j values referred to array.
        """

        return ij_pixel_to_ij_array(*self.geotransform.xy_geogr_to_ij_pixel(x, y))

    def xyToijPix(self,
        x: numbers.Real,
        y: numbers.Real
    ) -> Tuple[numbers.Real, numbers.Real]:
        """
        Converts from geographic to pixel coordinates.

        :param x: x geographic component
        :param y: y geographic component
        :return: i and j values referred to grid.
        """

        return self._geotransform.xy_geogr_to_ij_pixel(x, y)

    def ijArrToxy(self,
        i: numbers.Real,
        j: numbers.Real
    ) -> Tuple[numbers.Real, numbers.Real]:
        """
        Converts from array indices to geographic coordinates.

        :param i: i array component.
        :param j: j array component.
        :return: x and y geographic coordinates.
        """

        i_pix, j_pix = ij_array_to_ij_pixel(i, j)

        return self._geotransform.ij_pixels_to_xy_geogr(i_pix, j_pix)

    def ijPixToxy(self,
      i: numbers.Real,
      j: numbers.Real
    ) -> Tuple[numbers.Real, numbers.Real]:
        """
        Converts from grid indices to geographic coordinates.

        :param i: i pixel component.
        :param j: j pixel component.
        :return: x and y geographic coordinates.
        """

        return self._geotransform.ij_pixels_to_xy_geogr(i, j)

    @property
    def has_rotation(self) -> bool:
        """
        Determines if a grid has axis rotations defined.

        :return: true if there are rotations, false otherwise.
        """

        return self.geotransform.has_rotation

    def geotransf_cell_sizes(self) -> Tuple[numbers.Real, numbers.Real]:
        """
        Calculates the geotransformed cell sizes.

        :return: a pair of numbers.Real values, representing the cell sizes in the j and i directions.
        """

        dummy_factor = 100

        start_pt = Point(*self.ijArrToxy(0, 0))
        end_pt_j = Point(*self.ijArrToxy(0, dummy_factor))
        end_pt_i = Point(*self.ijArrToxy(dummy_factor, 0))

        return end_pt_j.distance(start_pt) / dummy_factor, end_pt_i.distance(start_pt) / dummy_factor

    def cell_centers_xy_arrays(self,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Returns the two arrays storing respectively the x and the y coordinates
        of the grid cell centers for the grid.

        :return: two arrays storing the geographical coordinates of the grid centers.
        """

        num_rows, num_cols = self.array.shape

        X = np.zeros((num_rows, num_cols), dtype=np.float64)
        Y = np.zeros((num_rows, num_cols), dtype=np.float64)
        for i in range(num_rows):
            for j in range(num_cols):
                x, y = self._geotransform.ij_pixels_to_xy_geogr(i + 0.5, j + 0.5)
                X[i, j] = x
                Y[i, j] = y

        return X, Y

    def interpolate_bilinear(self,
         x: numbers.Real,
         y: numbers.Real
    ) -> Union[type(None), numbers.Real]:
        """
        Interpolate the z value at a point, given its geographic coordinates.
        Interpolation method: bilinear.

        :param x: x geographic coordinate.
        :param y: y geographic coordinate.
        :return: the interpolated z value.
        """

        i, j = self.xyToijArr(x, y)

        return array_bilin_interp(self.array, i, j)

    def interpolate_bilinear_point(self,
        pt: Point,
    ) -> Union[type(None), Point]:
        """
        Interpolate the z value at a point, returning a Point with elevation extracted from the DEM.
        Interpolation method: bilinear.

        :param pt: the positional point.
        :return: a point with the same x-y position of the input point and with z equal to the interpolated z value.
        """

        check_type(pt, "Input point", Point)

        x, y = pt.x, pt.y

        z = self.interpolate_bilinear(
            x=x,
            y=y)

        if z is not None:
            return Point(x, y, z)
        else:
            return None

    def interpolate_bilinear_point_with_nan(self,
        pt: Point,
    ) -> Union[type(None), Point]:
        """
        Interpolate the z value at a point, returning a Point with elevation extracted from the DEM.
        Interpolation method: bilinear.

        :param pt: the positional point.
        :return: a point with the same x-y position of the input point and with z equal to the interpolated z value.
        """

        check_type(pt, "Input point", Point)

        x, y = pt.x, pt.y

        z = self.interpolate_bilinear(
            x=x,
            y=y)

        return Point(x, y, z)

    def grad_forward_y(self):
        """
        Return an array representing the forward gradient in the y direction (top-wards), with values scaled by cell size.

        @return: numpy.array, same shape as current Grid instance
        """
        gf = np.zeros(np.shape(self.array)) * np.NaN
        gf[1:, :] = self.array[:-1, :] - self.array[1:, :]

        return gf / float(self.cellsize_y)

    def grad_forward_x(self):
        """
        Return an array representing the forward gradient in the x direction (right-wards), with values scaled by cell size.

        @return: numpy.array, same shape as current Grid instance
        """
        gf = np.zeros(np.shape(self.array), ) * np.NaN
        gf[:, :-1] = self.array[:, 1:] - self.array[:, :-1]

        return gf / float(self.cellsize_x)

    def zoom_in(
        self,
        zoom_factor: numbers.Real
    ) -> Tuple[Union[type(None), 'Grid'], Error]:
        """
        Created a new grid zoomed to the center by the given zoom factor.

        :param zoom_factor: the zoom foctor.
        :return: the potential grid and an error status.
        """

        try:

            rows, cols = self.array.shape

            left_pixel, right_pixel, top_pixel, bottom_pixel = pixels_zoom(cols, rows, zoom_factor)

            # upper-left corner of upper-left pixel x & y coordinates
            ulc_ulp_x, ulc_ulp_y = self.geotransform.ij_pixels_to_xy_geogr(
                i=top_pixel,
                j=left_pixel
            )

            resized_geotransform = self.geotransform.shifted(
                ulc_ulp_x,
                ulc_ulp_y
            )

            resized_array = self.array[top_pixel:bottom_pixel+1, left_pixel:right_pixel+1]

            return Grid(
                array=np.copy(resized_array),
                geotransform=resized_geotransform,
            ), Error()

        except Exception as e:

            return None, Error(True, caller_name(), e, traceback.format_exc())


'''
def intersect_grid_with_plane(
    grid: Grid,
    srcPt: Point,
    srcPlaneAttitude: Plane
) -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], Error]:
    """
    Calculates the intersections (as points) between DEM (the grid object) and a plane.

    :param srcPt: point, expressed in geographical coordinates, that the plane must contain.
    :param srcPlaneAttitude: orientation of the surface (currently only planes).
    :return: tuple of four arrays or error
    """

    try:

        _, trcorner, _, llcorner = grid.corners_geog()

        # closures to compute the geographic coordinates (in x- and y-) of a cell center
        # the grid coordinates of the cell center are expressed by i and j

        grid_coord_to_geogr_coord_x_closure = lambda j: llcorner[0] + grid.cellsize_x * (0.5 + j)
        grid_coord_to_geogr_coord_y_closure = lambda i: trcorner[1] - grid.cellsize_y * (0.5 + i)

        # arrays storing the geographical coordinates of the cell centers along the x- and y- axes

        cell_center_x_array, cell_center_y_array = grid.cell_centers_xy_arrays()
        ycoords_x, xcoords_y = np.broadcast_arrays(cell_center_x_array, cell_center_y_array)

        #### x-axis direction intersections

        # 2D array of DEM segment parameters
        x_dem_m = grid.grad_forward_x()
        x_dem_q = grid.array - cell_center_x_array * x_dem_m

        # closure for the planar surface that, given (x,y), will be used to derive z
        plane_z_closure = closure_plane_from_geo(
            srcPlaneAttitude,
            srcPt
        )

        # 2D array of plane segment parameters
        x_plane_m = srcPlaneAttitude.m_coeff_in_x_dir()
        x_plane_q = array_from_function(
            grid.row_num(),
            1,
            lambda j: 0, grid_coord_to_geogr_coord_y_closure,
            plane_z_closure
        )

        # 2D array that defines denominator for intersections between local segments
        x_inters_denomin = np.where(
            x_dem_m != x_plane_m,
            x_dem_m - x_plane_m,
            np.NaN
        )

        coincident_x = np.where(x_dem_q != x_plane_q, np.NaN, ycoords_x)

        xcoords_x = np.where(
            x_dem_m != x_plane_m,
            (x_plane_q - x_dem_q) / x_inters_denomin,
            coincident_x
        )

        xcoords_x = np.where(
            xcoords_x < ycoords_x,
            np.NaN,
            xcoords_x
        )

        xcoords_x = np.where(
            xcoords_x >= ycoords_x + grid.cellsize_x,
            np.NaN,
            xcoords_x
        )

        #### y-axis direction intersections

        # 2D array of DEM segment parameters
        y_dem_m = grid.grad_forward_y()
        y_dem_q = grid.array - cell_center_y_array * y_dem_m

        # 2D array of plane segment parameters
        y_plane_m = srcPlaneAttitude.m_coeff_in_y_dir()
        y_plane_q = array_from_function(
            1,
            grid.col_num(),
            grid_coord_to_geogr_coord_x_closure,
            lambda i: 0,
            plane_z_closure
        )

        # 2D array that defines denominator for intersections between local segments
        y_inters_denomin = np.where(
            y_dem_m != y_plane_m,
            y_dem_m - y_plane_m,
            np.NaN
        )

        coincident_y = np.where(
            y_dem_q != y_plane_q,
            np.NaN,
            xcoords_y
        )

        ycoords_y = np.where(
            y_dem_m != y_plane_m,
            (y_plane_q - y_dem_q) / y_inters_denomin,
            coincident_y
        )

        # filter out cases where intersection is outside cell range
        ycoords_y = np.where(
            ycoords_y < xcoords_y,
            np.NaN,
            ycoords_y
        )

        ycoords_y = np.where(
            ycoords_y >= xcoords_y + grid.cellsize_y,
            np.NaN,
            ycoords_y
        )

        for i in range(xcoords_x.shape[0]):
            for j in range(xcoords_x.shape[1]):
                if abs(xcoords_x[i, j] - ycoords_x[i, j]) < 1.0e-5 and abs(
                        ycoords_y[i, j] - xcoords_y[i, j]) < 1.0e-5:
                    ycoords_y[i, j] = np.NaN

        return xcoords_x, xcoords_y, ycoords_x, ycoords_y

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc())
'''

def plane_dem_intersections_strategy_1(
    plane_attitude: Plane,
    source_point: Point,
    grid: Grid
) -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], Error]:
    """
    Calculates the intersections (as points) between DEM (the grid object) and a plane.

    :param plane_attitude: orientation of the surface (currently only planes).
    :param source_point: point, expressed in geographical coordinates, that the plane must contain.
    :param grid: the source DEM.
    :return: tuple of two lists or error
    """

    try:

        _, trcorner, _, llcorner = grid.corners_geog()

        # closures to compute the geographic coordinates (in x- and y-) of a cell center
        # the grid coordinates of the cell center are expressed by i and j

        grid_coord_to_geogr_coord_x_closure = lambda j: llcorner[0] + grid.cellsize_x * (0.5 + j)
        grid_coord_to_geogr_coord_y_closure = lambda i: trcorner[1] - grid.cellsize_y * (0.5 + i)

        # arrays storing the geographical coordinates of the cell centers along the x- and y- axes

        cell_center_x_array, cell_center_y_array = grid.cell_centers_xy_arrays()
        ycoords_x, xcoords_y = np.broadcast_arrays(cell_center_x_array, cell_center_y_array)

        #### x-axis direction intersections

        # 2D array of DEM segment parameters
        x_dem_m = grid.grad_forward_x()
        x_dem_q = grid.array - cell_center_x_array * x_dem_m

        # closure for the planar surface that, given (x,y), will be used to derive z
        plane_z_closure = closure_plane_from_geo(
            plane_attitude,
            source_point
        )

        # 2D array of plane segment parameters
        x_plane_m = plane_attitude.m_coeff_in_x_dir()
        x_plane_q = array_from_function(
            grid.row_num(),
            1,
            lambda j: 0, grid_coord_to_geogr_coord_y_closure,
            plane_z_closure
        )

        # 2D array that defines denominator for intersections between local segments
        x_inters_denomin = np.where(
            x_dem_m != x_plane_m,
            x_dem_m - x_plane_m,
            np.NaN
        )

        coincident_x = np.where(x_dem_q != x_plane_q, np.NaN, ycoords_x)

        xcoords_x = np.where(
            x_dem_m != x_plane_m,
            (x_plane_q - x_dem_q) / x_inters_denomin,
            coincident_x
        )

        xcoords_x = np.where(
            xcoords_x < ycoords_x,
            np.NaN,
            xcoords_x
        )

        xcoords_x = np.where(
            xcoords_x >= ycoords_x + grid.cellsize_x,
            np.NaN,
            xcoords_x
        )

        #### y-axis direction intersections

        # 2D array of DEM segment parameters
        y_dem_m = grid.grad_forward_y()
        y_dem_q = grid.array - cell_center_y_array * y_dem_m

        # 2D array of plane segment parameters
        y_plane_m = plane_attitude.m_coeff_in_y_dir()
        y_plane_q = array_from_function(
            1,
            grid.col_num(),
            grid_coord_to_geogr_coord_x_closure,
            lambda i: 0,
            plane_z_closure
        )

        # 2D array that defines denominator for intersections between local segments
        y_inters_denomin = np.where(
            y_dem_m != y_plane_m,
            y_dem_m - y_plane_m,
            np.NaN
        )

        coincident_y = np.where(
            y_dem_q != y_plane_q,
            np.NaN,
            xcoords_y
        )

        ycoords_y = np.where(
            y_dem_m != y_plane_m,
            (y_plane_q - y_dem_q) / y_inters_denomin,
            coincident_y
        )

        # filter out cases where intersection is outside cell range
        ycoords_y = np.where(
            ycoords_y < xcoords_y,
            np.NaN,
            ycoords_y
        )

        ycoords_y = np.where(
            ycoords_y >= xcoords_y + grid.cellsize_y,
            np.NaN,
            ycoords_y
        )

        for i in range(xcoords_x.shape[0]):
            for j in range(xcoords_x.shape[1]):
                if abs(xcoords_x[i, j] - ycoords_x[i, j]) < 1.0e-5 and abs(
                        ycoords_y[i, j] - xcoords_y[i, j]) < 1.0e-5:
                    ycoords_y[i, j] = np.NaN

        return xcoords_x, xcoords_y, ycoords_x, ycoords_y

    except Exception as e:

        return Error(
            True,
            caller_name(),
            e,
            traceback.format_exc())


def try_write_esrigrid(
    grid: Grid,
    outgrid_flpth: str,
    esri_nullvalue: numbers.Integral = -9999,
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
        return False, f"Output grid '{outgrid_flpth}' already exists"

    try:
        outputgrid = open(outgrid_flpth, 'w')  # create the output ascii file
    except Exception:
        return False, f"Unable to create output grid '{outgrid_flpth}'"

    if outputgrid is None:
        return False, f"Unable to create output grid '{outgrid_flpth}'"

    if grid.has_rotation:
        return False, "Grid has axes rotations defined"

    cell_size_x = grid.cellsize_x
    cell_size_y = grid.cellsize_y
    print(f"cell_size_x: {cell_size_x}")
    print(f"cell_size_y: {cell_size_y}")
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

    return True, f"Data saved in {outgrid_flpth}"


def ij_array_to_ij_pixel(
        i_arr: numbers.Real,
        j_arr: numbers.Real
) -> Tuple[numbers.Real, numbers.Real]:
    """
    Converts from array indices to geotransform-related pixel indices.

    :param i_arr: the array i value.
    :param j_arr: the array j value.
    :return: the geotransform-equivalent i and j indices.

    Examples:
      >>> ij_array_to_ij_pixel(0, 0)
      (0.5, 0.5)
      >>> ij_array_to_ij_pixel(0.5, 0.5)
      (1.0, 1.0)
      >>> ij_array_to_ij_pixel(1.5, 0.5)
      (2.0, 1.0)
    """

    return i_arr + 0.5, j_arr + 0.5


def ij_pixel_to_ij_array(
        i_pix: numbers.Real,
        j_pix: numbers.Real
) -> Tuple[numbers.Real, numbers.Real]:
    """
    Converts from pixel (geotransform-derived) to array indices.

    :param i_pix: the geotransform i value.
    :param j_pix: the geotransform j value.
    :return: the array-equivalent i and j indices.

    Examples:
      >>> ij_pixel_to_ij_array(0, 0)
      (-0.5, -0.5)
      >>> ij_pixel_to_ij_array(0.5, 0.5)
      (0.0, 0.0)
      >>> ij_pixel_to_ij_array(0.5, 1.5)
      (0.0, 1.0)
    """

    return i_pix - 0.5, j_pix - 0.5


def ij_transfer_func_with_geotransform(
        i: numbers.Real,
        j: numbers.Real,
        geotransform: GeoTransform,
        z_transfer_func: Callable,
        i_shift: numbers.Real = 0.5,
        j_shift: numbers.Real = 0.5
) -> numbers.Real:
    """
    Return a z value as the result of a function (transfer_func_z) applied to a
    (i+i_shift,j+j_shift) point (i.e., with default values, the cell center, not the cell top-left corner)
    given a geotransform.

    :param  i:  array i (-y) coordinate of a single point.
    :param  j:  array j (x) coordinate of a single point.
    :param  geotransform:  geotransform
    :param  z_transfer_func:  function that calculates the z value given x and y input
    :param i_shift: cell unit shift in the i direction with respect to the cell top-left corner. Default is 0.5, i.e. half the cell size
    :param j_shift: cell unit shift in the j direction with respect to the cell top-left corner. Default is 0.5, i.e. half the cell size
    :return: z value
    """

    return z_transfer_func(*geotransform.ij_pixels_to_xy_geogr(i + i_shift, j + j_shift))


def array_from_geotransform_function(
        row_num: numbers.Integral,
        col_num: numbers.Integral,
        geotransform: GeoTransform,
        z_transfer_func: Callable,
        i_shift: numbers.Real = 0.5,
        j_shift: numbers.Real = 0.5
) -> np.ndarray:
    """
    Creates an array of z values based on functions that map (i,j) indices (to be created)
    into (x, y) values and then z values.

    :param  row_num:  row number of the array to be created.
    :param  col_num:  column number of the array to be created.
    :param  geotransform:  the used geotransform.
    :param  z_transfer_func:  function that derives z given a (x, y) point.
    :param i_shift: cell unit shift in the i direction with respect to the cell top-left corner. Default is 0.5, i.e. half the cell size
    :param j_shift: cell unit shift in the j direction with respect to the cell top-left corner. Default is 0.5, i.e. half the cell size
    :return:  array of z values
    """

    return np.array(np.fromfunction(
            function=ij_transfer_func_with_geotransform,
            shape=(row_num, col_num),
            dtype=np.float64,
            geotransform=geotransform,
            z_transfer_func=z_transfer_func,
            i_shift=i_shift,
            j_shift=j_shift
        )
    )


def array_from_function(row_num, col_num, x_transfer_func, y_transfer_func, z_transfer_func):
    """
    Creates an array of z values based on functions that map (i,j) indices (to be created)
    into (x, y) values and then z values.

    @param  row_num:  row number of the array to be created.
    @type  row_num:  int.
    @param  col_num:  column number of the array to be created.
    @type  col_num:  int.
    @param  x_transfer_func:  function that derives x given a j array index.
    @type  x_transfer_func:  Function.
    @param  y_transfer_func:  function that derives y given an i array index.
    @type  y_transfer_func:  Function.
    @param  z_transfer_func:  function that derives z given a (x,y) point.
    @type  z_transfer_func:  Function.

    @return:  array of z value - array of float numbers.

    """

    transfer_funcs = (x_transfer_func, y_transfer_func, z_transfer_func)

    return np.fromfunction(
        ij_transfer_func,
        (row_num, col_num),
        transfer_funcs=transfer_funcs
    )



