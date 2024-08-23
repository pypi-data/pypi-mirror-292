

import unittest

from geogst.core.deformations.space3d.rotations import *


class TestRotations(unittest.TestCase):

    def setUp(self):

        pass

    def test_rotate_vector_3d(self):

        struct = Vect3D(1, 0, 1)

        rotation_dir, rotation_angle = Direct(0, -90), 90
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.is_similar_to(Vect3D(0.0, 1.0, 1.0))

        rotation_dir, rotation_angle = Direct(0, 90), 90
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.is_similar_to(Vect3D(0.0, -1.0, 1.0))

        rotation_dir, rotation_angle = Direct(0, -90), 180
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.is_similar_to(Vect3D(-1.0, 0.0, 1.0))

        rotation_dir, rotation_angle = Direct(0, -90), 270
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.is_similar_to(Vect3D(-0.0, -1.0, 1.0))

        rotation_dir, rotation_angle = Direct(90, 0), 90
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.is_similar_to(Vect3D(1.0, -1.0, 0.0))

        rotation_dir, rotation_angle = Direct(90, 0), 180
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.is_similar_to(Vect3D(1.0, 0.0, -1.0))

        rotation_dir, rotation_angle = Direct(90, 0), 270
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.is_similar_to(Vect3D(1.0, 1.0, -0.0))

        rotation_dir, rotation_angle = Direct(90, 0), 360
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.is_similar_to(Vect3D(1.0, 0.0, 1.0))

        struct = Vect3D(0, 0, 3)

        rotation_dir, rotation_angle = Direct(0, -90), 90
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.is_similar_to(Vect3D(0.0, 0.0, 3.0))

        rotation_dir, rotation_angle = Direct(90, -45), 180
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.is_similar_to(Vect3D(3.0, 0.0, 0.0))

    def test_rotate_direction(self):

        struct = Direct(90, 0)

        rotation_dir, rotation_angle = Direct(0, 0), -45
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.angle_with(Direct(90, -45)) < 1e-12

        rotation_dir, rotation_angle = Direct(0, 0), -90
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.angle_with(Direct(0, -90)) < 1e-12

        rotation_dir, rotation_angle = Direct(0, 0), -180
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.angle_with(Direct(270, 0)) < 1e-12

        rotation_dir, rotation_angle = Direct(90, -45), 180
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.angle_with(Direct(0, -90)) < 1e-12

        rotation_dir, rotation_angle = Direct(90, -45), 360
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.angle_with(Direct(90, 0)) < 1e-12

    def test_rotate_axis(self):

        struct = Axis(90, -46)

        rotation_dir, rotation_angle = Direct(0, 0), -44
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.angle_with(Axis(0, -90)) < 1e-12

        rotation_dir, rotation_angle = Direct(0, 90), 180
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.angle_with(Axis(270, -46)) < 1e-12

    def test_rotate_slickenline(self):

        struct = Slickenline(45, 0)

        rotation_dir, rotation_angle = Direct(0, 90), 135
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.geom.angle_with(Direct(180, 0)) < 1e-12

        rotation_dir, rotation_angle = Direct(45, 0), 33.2
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.geom.angle_with(Direct(45, 0)) < 1e-12

        rotation_dir, rotation_angle = Direct(45, 0), 2227.29
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.geom.angle_with(Direct(45, 0)) < 1e-12

        rotation_dir, rotation_angle = Direct(225, 0), 54624
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.geom.angle_with(Direct(45, 0)) < 1e-12

        rotation_dir, rotation_angle = Direct(225, 90), 360*12
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)
        assert not err
        assert rot_struct.geom.angle_with(Direct(45, 0)) < 1e-12

    def test_rotate_fault(self):

        struct = Fault(
            azim=90,
            dip_ang=45,
            slickenlines=[0, 45, 90])

        rotation_dir, rotation_angle = Direct(0, 0), 45
        rot_struct, err = rotate(struct, rotation_dir, rotation_angle)

        assert not err

        rotated_plane = rot_struct.plane
        rotated_slickenlines = rot_struct.slickenlines()

        assert rotated_plane.angle_with(Plane(90, 90)) < 1e-12

        assert rotated_slickenlines[0].geom.angle_with(Direct(0, 0)) < 1e-12
        assert rotated_slickenlines[1].geom.angle_with(Direct(0, -45)) < 1e-12
        assert rotated_slickenlines[2].geom.angle_with(Direct(0, -90)) < 1e-12



