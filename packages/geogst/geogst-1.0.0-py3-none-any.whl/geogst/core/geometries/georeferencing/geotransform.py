
import affine

from geogst.core.mathematics.arrays import *


class GeoTransform(np.ndarray):
    """
    Manage geotransform parameters for io.
    It is based on the GDAL GeoTransform concept.
    See: http://www.gdal.org/gdal_datamodel.html
    """

    def __new__(cls,
            inTopLeftX: numbers.Real,
            inTopLeftY: numbers.Real,
            inPixWidth: numbers.Real,
            inPixHeight: numbers.Real,
            inRotRow: numbers.Real=0.0,
            inRotColumn: numbers.Real=0.0
    ) -> 'GeoTransform':
        """
        Instance creator.
        Note: pixel height input is positive.

        :param inTopLeftX: top left corner of the top left pixel of the raster - x coord
        :param inTopLeftY:: top left corner of the top left pixel of the raster - y coord
        :param inPixWidth: pixel width
        :param inPixHeight: pixel height
        :param inRotRow: rotation
        :param inRotColumn: rotation

        Examples:
          >>> GeoTransform(1500, 3000, 10, 10)
          GeoTransform(topLeftX: 1500.00, topLeftY: 3000.00, pixWidth: 10.00, pixHeight: 10.00, rotRow: 0.00, rotColumn: 0.00)
          """

        return np.array([
            inTopLeftX,  # GT(0) - top left corner of the top left pixel of the raster
            inPixWidth,  # GT(1) - pixel width
            inRotRow,  # GT(2) - row rotation
            inTopLeftY,  # GT(3) - top left corner of the top left pixel of the raster
            inRotColumn,  # GT(4) - column rotation
            -inPixHeight  # GT(5) - pixel height
        ], dtype=float).view(cls)

    @classmethod
    def from_gdal_geotransform(cls,
                               gdal_gt: Tuple[numbers.Real, numbers.Real, numbers.Real, numbers.Real, numbers.Real, numbers.Real]
                               ) -> 'GeoTransform':
        """
        Creates a Geotransform from a GDAL-convention tuple.

        :param gdal_gt: tuple with GDAL geotransform parameters
        :return: None
        """

        return cls(
            gdal_gt[0],
            gdal_gt[3],
            gdal_gt[1],
            -gdal_gt[5],
            gdal_gt[2],
            gdal_gt[4])

    def to_gdal_geotransform(self
        ) -> Tuple[numbers.Real, numbers.Real, numbers.Real, numbers.Real, numbers.Real, numbers.Real]:

        return (self.topLeftX,
                self.pixWidth,
                self.rotRow,
                self.topLeftY,
                self.rotColumn,
                -self.pixHeight
                )

    @classmethod
    def from_affine(cls,
        affine_transformation: affine.Affine
    ) -> 'GeoTransform':
        """
        Creates a Geotransform from an affine transformation.

        :param affine_transformation: the affine transformation
        :type affine_transformation: affine.Affine
        """

        gdal_transformation = affine_transformation.to_gdal()
        return GeoTransform.from_gdal_geotransform(gdal_transformation)

    def __repr__(self) -> str:

        return "GeoTransform(topLeftX: {:.2f}, topLeftY: {:.2f}, pixWidth: {:.2f}, pixHeight: {:.2f}, rotRow: {:.2f}, rotColumn: {:.2f})".format(
            self.topLeftX,
            self.topLeftY,
            self.pixWidth,
            self.pixHeight,
            self.rotRow,
            self.rotColumn)

    @property
    def components(self):
        """
        Returns the Geotransform components as a tuple.

        :return:
        """

        return self[0], self[1], self[2], self[3], self[4], self[5]

    @property
    def topLeftX(self) -> numbers.Real:
        """
        Get top-left corner x value of the io.

        :return: the top-left corner x value, according to GDAL convention
        :rtype: numbers.Real.

        Examples:
          >>> GeoTransform(1500, 3000, 10, 10, 0, 0).topLeftX
          1500.0
        """

        return self[0]

    @property
    def topLeftY(self) -> numbers.Real:
        """
        Get top-left corner y value of the io.

        :return:  the top-left corner y value, according to GDAL convention.
        :rtype: numbers.Real.

        Examples:
          >>> GeoTransform(1500, 3000, 10, 10, 0, 0).topLeftY
          3000.0
          """

        return self[3]

    @property
    def pixWidth(self) -> numbers.Real:
        """
        Get East-West size of the io cell.

        :return:  the East-West size of the io cell
        :rtype: numbers.Real.

        Examples:
          >>> GeoTransform(1500, 3000, 10, 10, 0, 0).pixWidth
          10.0
        """

        return self[1]

    @property
    def pixHeight(self) -> numbers.Real:
        """
        Get North-South size of the io cell.

        :return:  the North-South size of the io cell.
        :rtype: numbers.Real.

        Examples:
          >>> GeoTransform(1500, 3000, 10, 10, 0, 0).pixHeight
          10.0
        """

        return -self[5]

    @property
    def rotRow(self) -> numbers.Real:
        """
        Get row rotation GT(2) (see GDAL documentation).

        :return:  the io rotation value GT(2).
        :rtype: numbers.Real.

        Examples:
          >>> GeoTransform(1500, 3000, 10, 10, 0, 0).rotRow
          0.0
        """

        return self[2]

    @property
    def rotColumn(self) -> numbers.Real:
        """
        Get column rotation GT(4) (see GDAL documentation).

        :return:  the io rotation value GT(4).
        :rtype: numbers.Real.

        Examples:
          >>> GeoTransform(1500, 3000, 10, 10, 0, 0).rotColumn
          0.0
        """

        return self[4]

    @property
    def has_rotation(self) -> bool:
        """
        Determines if the geotransform has axis rotations defined.

        :return: true if there are rotations, false otherwise.
        :rtype: bool.

        Examples:
        """

        return self.rotRow != 0.0 or self.rotColumn != 0.0

    def to_xy_cell_centers_arrays(
            self,
            num_rows: numbers.Integral,
            num_cols: numbers.Integral
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create two arrays that represent the X and Y geographic coordinates of
        the cells CENTERS (not corners) given the geotransform.

        :param num_rows: the number of rows.
        :type num_rows: numbers.Integral.
        :param num_cols: the number of the columns.
        :type num_cols: numbers.Integral.
        :return: the two Numpy arrays representing the geographic X and Y coordinates.
        :rtype: Numpy array of float64.

        Examples:
        """

        X = np.zeros((num_rows, num_cols), dtype=np.float64)
        Y = np.zeros((num_rows, num_cols), dtype=np.float64)
        for i in range(num_rows):
            for j in range(num_cols):
                x, y = self.ij_pixels_to_xy_geogr(i + 0.5, j + 0.5)
                X[i, j] = x
                Y[i, j] = y

        return X, Y

    def ij_pixels_to_xy_geogr(
            self,
            i: numbers.Real,
            j: numbers.Real
    ) -> Tuple[numbers.Real, numbers.Real]:
        """
        Transforms from pixel to geographic coordinates.

        See: http://www.gdal.org/gdal_datamodel.html
        "Note that the pixel/line coordinates in the above are from (0.0,0.0)
        at the top left corner of the top left pixel to (width_in_pixels,
        height_in_pixels) at the bottom right corner of the bottom right pixel.
        The pixel/line location of the center of the top left pixel would
        therefore be (0.5,0.5)."

        :param i: the pixel i coordinate.
        :param j: the pixel i coordinate.
        :return: tuple storing geographic x-y pair

        Examples:
          >>> gt1 = GeoTransform(1500, 3000, 10, 10)
          >>> gt1.ij_pixels_to_xy_geogr(0, 0)
          (1500.0, 3000.0)
          >>> gt1.ij_pixels_to_xy_geogr(10, 10)
          (1600.0, 2900.0)
          >>> gt1.ij_pixels_to_xy_geogr(2, 1)
          (1510.0, 2980.0)
        """

        Xgeo = self[0] + j * self[1] + i * self[2]
        Ygeo = self[3] + j * self[4] + i * self[5]

        return Xgeo, Ygeo

    def xy_geogr_to_ij_pixel(
            self,
            x: numbers.Real,
            y: numbers.Real
    ) -> Tuple[numbers.Real, numbers.Real]:
        """
        Transforms from geographic to pixel coordinates.

        See: http://www.gdal.org/gdal_datamodel.html
        "Note that the pixel/line coordinates in the above are from (0.0,0.0)
        at the top left corner of the top left pixel to (width_in_pixels,
        height_in_pixels) at the bottom right corner of the bottom right pixel.
        The pixel/line location of the center of the top left pixel would
        therefore be (0.5,0.5)."

        Formula derivation
        ------------------

        x = g0 + col * g1 + row * g2
        y = g3 + col * g4 + row * g5

        x - g0 - row* g2 = col * g1
        col = (x - g0 - row*g2) / g1
        col = (y - g3 - row*g5) / g4

        g1 * y - g1 * g3 - row * g5 * g1 = g4 * x - g0 * g4 - row * g2 * g4
        row * (g2g4 + g1g5) = -g1y + g1g3 + g4x - g0g4
        row = (g1g3 - g0g4 + g4x - g1y) / (g2g4 - g1g5)

        (x - g0 - g1p) / g2 =  (g1g3 - g0g4 + g4x - g1y) / (g2g4 - g1g5)

        g2 * (g1g3 - g0g4 + g4x - g1y) / (g2g4 - g1g5) = x - g0 - g1p

        :param x: the  geographic x coordinate.
        :param y: the geographic y coordinate.
        :return: tuple storing pixel x-y pair

        Examples:
          >>> gt1 = GeoTransform(1500, 3000, 10, 10)
          >>> gt1.xy_geogr_to_ij_pixel(1600, 2900)
          (10.0, 10.0)
          >>> gt1.xy_geogr_to_ij_pixel(1600, 2800)
          (20.0, 10.0)
          >>> gt1.xy_geogr_to_ij_pixel(1800, 2600)
          (40.0, 30.0)
        """

        g0, g1, g2, g3, g4, g5 = self.components

        row = (g1*g3 - g0*g4 + g4*x - g1*y) / (g2*g4 - g1*g5)
        col = (x - g0 - row*g2) / g1

        return row, col

    def close_to(
            self,
            another: 'GeoTransform'
    ) -> bool:
        """
        Check equivalence between two GeoTransform instances.

        :param another: the second geotransform.
        :type another: GeoTransform.
        :return: whether the two geotransform are quivalent.
        :rtype: bool.

        Examples:
          >>> gt1 = GeoTransform(1500, 3000, 10, 10)
          >>> gt2 = GeoTransform(1500, 3000, 10, 10)
          >>> gt1.close_to(gt2)
          True
          >>> gt3 = GeoTransform(1600, 3000, 10, 10)
          >>> gt1.close_to(gt3)
          False
        """

        return arrays_are_close(
            self,
            another)

    def shifted(self,
        x: numbers.Real,
        y: numbers.Real):
        """
        Create a new GeoTransform with new coordinates
        of the upper-left corner of the upper-left pixel.
        """

        return GeoTransform(
            x,
            y,
            self.pixWidth,
            self.pixHeight,
            self.rotRow,
            self.rotColumn
        )


if __name__ == "__main__":

    import doctest
    doctest.testmod()


