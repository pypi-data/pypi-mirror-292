from unittest import TestCase, skip

import test.fixture
from thinking_tests.current import current_case
from thinking_tests.decorators import case
from thinking_tests.protocol import CaseCoordinates
from thinking_tests.start import run_current_module, run_all


@case
def case1():
    test.fixture.accumulator.append(current_case())


@case
def case2():
    test.fixture.accumulator.append(current_case())

class TestDiscovery(TestCase):
    def test_running_current_module(self):
        test.fixture.accumulator = []
        result = run_current_module()
        self.assertEqual(2, result.testsRun)
        self.assertEqual(
            [
                CaseCoordinates(__name__, "case1"),
                CaseCoordinates(__name__, "case2")
                # CaseCoordinates(__name__, "case1", 10),
                # CaseCoordinates(__name__, "case2", 15)
            ],
            test.fixture.accumulator
        )


    @skip("This test cannot be written reliably; even though we control imports in this file, testing backend might "
          "be executing other cases in the same process, so some modules might have been already imported.")
    def test_running_all(self):
        test.fixture.accumulator = []
        result = run_all(root_package=None)
        self.assertEqual("???", result.testsRun)
        expected_order = "???"
        self.assertEqual(
            expected_order,
            test.fixture.accumulator
        )