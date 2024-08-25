
import unittest

from src_datasets import *


class TestFocalMechamismRotations(unittest.TestCase):

    def test_rotate_focal_mechanism(self):
        """
        Test whether a focal mechanism is correctly rotated.

        :return:
        """

        src_fm = k91_fs_PTBaxes
        rot_axes = map(sols2rotaxis, k91_rot_sols)
        rot_fm = k91_ss_PTBaxes

        for rot_axis in rot_axes:
            calc_rot_fm = focmech_rotate(src_fm, rot_axis)
            assert calc_rot_fm.almost_equal(rot_fm)

    def test_inversion_kagan_examples_1(self):
        """
        Test of focal mechanims rotations examples
        as described in Kagan Y.Y. 3-D rotation of double-couple earthquake sources

        :return:
        """

        rots, err = focmechs_invert_rotations(k91_fs_PTBaxes, k91_ss_PTBaxes)

        assert not err

        print("\nTest inverse focal mechanism rotation")
        for ndx, rot in enumerate(rots):
            print(f"calculated solution: {rot}")
            k91_sol = sols2rotaxis(k91_rot_sols[ndx])
            print(f"Kagan 1991 solution: {k91_sol}")
            assert rot.strictly_equival(k91_sol)


if __name__ == '__main__':

    unittest.main()

