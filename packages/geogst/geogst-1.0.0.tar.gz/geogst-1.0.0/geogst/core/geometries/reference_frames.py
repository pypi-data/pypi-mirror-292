
from geogst.core.mathematics.vectors2d import *


class RefFrame2D(object):

    def __init__(self,
                 versor_x: Vect2D,
                 versor_y: Vect2D):
        """
        Reference frame constructor.

        :param versor_x: Vect instance representing the x axis orientation
        :param versor_y: Vect instance representing the y axis orientation

        Examples:
        """

        if not (versor_x.is_close_to_1 and versor_y.is_close_to_1):
            raise Exception("Input vectors must be near unit")

        if not are_close(versor_x.angle_with(versor_y), 90.0):
            raise Exception("Input vectors must be sub-orthogonal")

        self._x = versor_x
        self._y = versor_y

    @property
    def x(self) -> Vect2D:
        """
        Return the x axis as a vector.

        :return: x axis
        :rtype: Vect3D

        Examples:
          >>> RefFrame2D(Vect2D(1,0), Vect2D(0,1)).x
          Vect2D(1.0000, 0.0000)
        """

        return self._x

    @property
    def y(self) -> Vect2D:
        """
        Return the y as a vector.

        :return: y axis
        :rtype: Vect3D

        Examples:
          >>> RefFrame2D(Vect2D(1,0), Vect2D(0,1)).y
          Vect2D(0.0000, 1.0000)
        """

        return self._y


class RefFrame3D:

    def __init__(self,
                 versor_x,
                 versor_y,
                 versor_z
                 ):

        assert almost_zero(versor_x.scalar_product(versor_y))
        assert almost_zero(versor_x.scalar_product(versor_z))
        assert almost_zero(versor_y.scalar_product(versor_z))

        self.axes = [versor_x, versor_y, versor_z]

    def rotation_matrix(self, rotated_frame):

        for frame_axis in self.axes:
            assert almost_zero(frame_axis.lenght_3d() - 1.0)
        for frame_axis in rotated_frame.axes:
            assert almost_zero(frame_axis.lenght_3d() - 1.0)

        rot_matrix = np.zeros((3, 3)) * np.nan

        for i, rot_frame_versor in enumerate(rotated_frame.axes):
            for j, init_frame_versor in enumerate(self.axes):
                rot_matrix[i, j] = init_frame_versor.scalar_product(rot_frame_versor)

        return rot_matrix
