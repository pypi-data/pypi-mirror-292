#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import unittest
from os import path

if __name__ == "__main__":
    test_path = path.abspath(__file__)
    test_path = path.dirname(test_path)

    suite = unittest.TestLoader().discover(test_path)
    unittest.TextTestRunner().run(suite)
