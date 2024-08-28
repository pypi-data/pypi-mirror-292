from unittest import TestCase, FunctionTestCase

from thinking_tests.aspect.weaving import AspectWeaver
from thinking_tests.outcome import Outcome
from thinking_tests.protocol import ThinkingCase, Setup, TestStage

class ThinkingAdapter(TestCase):
    def __init__(self, case: ThinkingCase):
        self.case = case
        self.setup: Setup = None
        self.body_outcome: Outcome = None
        self.teardown_outcome: Outcome = None
        self.aspect = AspectWeaver()
        self.last_stage: TestStage = None
        TestCase.__init__(self)

    def id(self):
        return self.case.coordinates.id

    def setUp(self):
        self.last_stage = TestStage.SETUP
        with self.aspect.around(TestStage.SETUP, self.case):
            self.setup = self.case.set_up()

    def runTest(self):
        self.last_stage = TestStage.RUN
        with self.aspect.around(TestStage.RUN, self.case):
            self.body_outcome = self.case.run_body(self.setup)

    def tearDown(self):
        self.last_stage = TestStage.TEARDOWN
        with self.aspect.around(TestStage.TEARDOWN, self.case):
            self.teardown_outcome = self.case.tear_down(self.setup, self.body_outcome)
            if isinstance(self.teardown_outcome, Outcome.Failure):
                self.teardown_outcome.reraise()

    def __str__(self):
        return f"ThinkingAdapter(case={self.case}, last_stage={self.last_stage})"

    def __repr__(self):
        return f"ThinkingAdapter(case={self.case}, last_stage={self.last_stage}, setup={self.setup}, body_outcome={self.body_outcome}, teardown_outcome={self.teardown_outcome})"

def adapt(case: ThinkingCase) -> TestCase:
    return ThinkingAdapter(case)
