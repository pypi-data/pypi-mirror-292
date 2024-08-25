
import unittest

from geogst.core.geometries.planes import *


class TestCartesianPlanesGeneric(unittest.TestCase):

    def setUp(self):

        self.plane_0 = CPlane3D(1342.25, 332, 342.3, 4224)
        self.shift = (234523, 34535, 856)

    def test_shift_plane(self):

        shifted_plane, err = shift_plane(
           self.plane_0, *self.shift)

        assert not err

        assert isinstance(shifted_plane, CPlane3D)

        assert shifted_plane.is_parallel_to_plane(self.plane_0)

        shift_vector = Vect3D(*self.shift)
        plane0_versor, err = self.plane_0.normal_versor()
        assert not err
        shift_distance = abs(shift_vector.dot_product(plane0_versor))

        point_in_shifted_plane = shifted_plane.as_lying_point()
        calculated_planes_distance = self.plane_0.absolute_distance_to_point(point_in_shifted_plane)

        assert are_close(shift_distance, calculated_planes_distance)

