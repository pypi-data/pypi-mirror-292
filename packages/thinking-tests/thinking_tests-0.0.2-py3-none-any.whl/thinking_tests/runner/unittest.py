from unittest import TextTestRunner, TestSuite, TestResult

from thinking_tests.adapter import adapt
from thinking_tests.protocol import ThinkingCase
from thinking_tests.runner.protocol import ThinkingTestRunner

class UnittestRunner(ThinkingTestRunner):
    def __init__(self, unittest_runner = None):
        self.backend = unittest_runner or TextTestRunner()

    def execute(self, cases: list[ThinkingCase]) -> TestResult:

        suite = TestSuite([adapt(case) for case in cases])
        return self.backend.run(suite)
