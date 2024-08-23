
import unittest

from src_datasets import *


class TestFocalMechamismRotations(unittest.TestCase):

    def test_quaternion_transformation(self):
        """
        Test forward and backward transformation from focal mechanism to quaternion.

        :return:
        """

        k91_fs_backPTBaxes = PTBAxes.from_quaternion(k91_fs_quater)
        k91_ss_backPTBaxes = PTBAxes.from_quaternion(k91_ss_quater)

        assert k91_fs_backPTBaxes.almost_equal(k91_fs_PTBaxes)
        assert k91_ss_backPTBaxes.almost_equal(k91_ss_PTBaxes)


if __name__ == '__main__':

    unittest.main()