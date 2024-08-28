from unittest import TestCase
from unittest.mock import Mock, call

from thinking_tests.current import current_stage, current_case
from thinking_tests.decorators import case
from thinking_tests.protocol import ThinkingCase, CaseCoordinates, TestStage


#todo add variant with args, where we use result of setup and outcome of body
class NoArgsE2e(TestCase):
    def setUp(self):
        self.name = "NAME"
        self.coordinates = CaseCoordinates(__name__, self.name)
        # self.coordinates = CaseCoordinates(__name__, self.name, 29) #keep 30 up to date with line number of decorator on def body()
        self.mock = Mock()
        self.raise_in_stages = {}
        self.exceptions = []
        def impl():
            self.mock(current_case(), current_stage())
            if current_stage() in self.raise_in_stages:
                e = self.exceptions[0]
                self.exceptions = self.exceptions[1:]
                raise e
        def su():
            impl()

        def td():
            impl()

        @case(self.name, setup=su, teardown=td)
        def body():
            impl()

        self.thinking_case = body

    def test_basics(self):
        self.assertIsInstance(self.thinking_case, ThinkingCase)
        self.assertEqual(self.coordinates, self.thinking_case.coordinates)

    def test_happy(self):
        result = self.thinking_case.run()
        self.assertEqual(
            [
                call(self.coordinates, TestStage.SETUP),
                call(self.coordinates, TestStage.RUN),
                call(self.coordinates, TestStage.TEARDOWN)
            ],
            self.mock.mock_calls
        )
        self.assertEqual(1, result.testsRun)
        self.assertEqual([], result.errors)
        self.assertEqual([], result.failures)
        self.assertEqual([], result.skipped)

    def test_failed_setup(self):
        self.raise_in_stages = { TestStage.SETUP }
        self.exceptions = [ Exception() ]
        result = self.thinking_case.run()
        self.assertEqual(
            [
                call(self.coordinates, TestStage.SETUP)
            ],
            self.mock.mock_calls
        )
        self.assertEqual(1, result.testsRun)
        self.assertEqual(1, len(result.errors))
        self.assertEqual([], result.failures)
        self.assertEqual([], result.skipped)

    def test_assert_failed_setup(self):
        self.raise_in_stages = { TestStage.SETUP }
        self.exceptions = [ AssertionError() ]
        result = self.thinking_case.run()
        self.assertEqual(
            [
                call(self.coordinates, TestStage.SETUP)
            ],
            self.mock.mock_calls
        )
        self.assertEqual(1, result.testsRun)
        self.assertEqual([], result.errors)
        self.assertEqual(1, len(result.failures))
        self.assertEqual([], result.skipped)

    def test_failed_test(self):
        self.raise_in_stages = { TestStage.RUN }
        self.exceptions = [ Exception() ]
        result = self.thinking_case.run()
        self.assertEqual(
            [
                call(self.coordinates, TestStage.SETUP),
                call(self.coordinates, TestStage.RUN),
                call(self.coordinates, TestStage.TEARDOWN)
            ],
            self.mock.mock_calls
        )
        self.assertEqual(1, result.testsRun)
        self.assertEqual(1, len(result.errors))
        self.assertEqual([], result.failures)
        self.assertEqual([], result.skipped)

    def test_assert_failed_test(self):
        self.raise_in_stages = { TestStage.RUN }
        self.exceptions = [ AssertionError() ]
        result = self.thinking_case.run()
        self.assertEqual(
            [
                call(self.coordinates, TestStage.SETUP),
                call(self.coordinates, TestStage.RUN),
                call(self.coordinates, TestStage.TEARDOWN)
            ],
            self.mock.mock_calls
        )
        self.assertEqual(1, result.testsRun)
        self.assertEqual([], result.errors)
        self.assertEqual(1, len(result.failures))
        self.assertEqual([], result.skipped)

    def test_failed_teardown_after_test_success(self):
        self.raise_in_stages = { TestStage.TEARDOWN }
        self.exceptions = [ Exception() ]
        result = self.thinking_case.run()
        self.assertEqual(
            [
                call(self.coordinates, TestStage.SETUP),
                call(self.coordinates, TestStage.RUN),
                call(self.coordinates, TestStage.TEARDOWN)
            ],
            self.mock.mock_calls
        )
        self.assertEqual(1, result.testsRun)
        self.assertEqual(1, len(result.errors))
        self.assertEqual([], result.failures)
        self.assertEqual([], result.skipped)

    def test_assert_failed_teardown_after_test_success(self):
        self.raise_in_stages = { TestStage.TEARDOWN }
        self.exceptions = [ AssertionError() ]
        result = self.thinking_case.run()
        self.assertEqual(
            [
                call(self.coordinates, TestStage.SETUP),
                call(self.coordinates, TestStage.RUN),
                call(self.coordinates, TestStage.TEARDOWN)
            ],
            self.mock.mock_calls
        )
        self.assertEqual(1, result.testsRun)
        self.assertEqual([], result.errors)
        self.assertEqual(1, len(result.failures))
        self.assertEqual([], result.skipped)


    def test_failed_teardown_after_test_failure(self):
        self.raise_in_stages = { TestStage.TEARDOWN }
        self.exceptions = [ Exception(), Exception() ]
        result = self.thinking_case.run()
        self.assertEqual(
            [
                call(self.coordinates, TestStage.SETUP),
                call(self.coordinates, TestStage.RUN),
                call(self.coordinates, TestStage.TEARDOWN)
            ],
            self.mock.mock_calls
        )
        self.assertEqual(1, result.testsRun)
        self.assertEqual(1, len(result.errors))
        self.assertEqual([], result.failures)
        self.assertEqual([], result.skipped)

    def test_assert_failed_teardown_after_test_failure(self):
        self.raise_in_stages = { TestStage.TEARDOWN }
        self.exceptions = [ Exception(), AssertionError() ]
        result = self.thinking_case.run()
        self.assertEqual(
            [
                call(self.coordinates, TestStage.SETUP),
                call(self.coordinates, TestStage.RUN),
                call(self.coordinates, TestStage.TEARDOWN)
            ],
            self.mock.mock_calls
        )
        self.assertEqual(1, result.testsRun)
        self.assertEqual(1, len(result.errors))
        self.assertEqual([], result.failures)
        self.assertEqual([], result.skipped)


    def test_failed_teardown_after_test_assert_failure(self):
        self.raise_in_stages = { TestStage.TEARDOWN }
        self.exceptions = [ AssertionError(), Exception() ]
        result = self.thinking_case.run()
        self.assertEqual(
            [
                call(self.coordinates, TestStage.SETUP),
                call(self.coordinates, TestStage.RUN),
                call(self.coordinates, TestStage.TEARDOWN)
            ],
            self.mock.mock_calls
        )
        self.assertEqual(1, result.testsRun)
        self.assertEqual([], result.errors)
        self.assertEqual(1, len(result.failures))
        self.assertEqual([], result.skipped)

    def test_assert_failed_teardown_after_test_assert_failure(self):
        self.raise_in_stages = { TestStage.TEARDOWN }
        self.exceptions = [ AssertionError(), AssertionError() ]
        result = self.thinking_case.run()
        self.assertEqual(
            [
                call(self.coordinates, TestStage.SETUP),
                call(self.coordinates, TestStage.RUN),
                call(self.coordinates, TestStage.TEARDOWN)
            ],
            self.mock.mock_calls
        )
        self.assertEqual(1, result.testsRun)
        self.assertEqual([], result.errors)
        self.assertEqual(1, len(result.failures))
        self.assertEqual([], result.skipped)