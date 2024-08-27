#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import unittest
from pathlib import Path

import xmlrunner

REPORT_NAME = "unittest_report.xml"

# run the tests storing results in memory
if __name__ == "__main__":
    current_file = Path(__file__)
    test_dir = current_file.parent.parent

    print(f"Loading tests from: {test_dir}")
    assert test_dir.exists()

    with open(REPORT_NAME, "wb") as out:
        test_loader = unittest.TestLoader().discover(test_dir)
        test_runner = xmlrunner.XMLTestRunner(output=out)
        result: unittest.TestResult = test_runner.run(test_loader)

        exit(len(result.errors) + len(result.failures))
