from abc import abstractmethod
from typing import TypeVar

from thinking_tests.protocol import ThinkingCase


BackendResultType = TypeVar("BackendResultType")

class ThinkingTestRunner:
    @abstractmethod
    def execute(self, cases: list[ThinkingCase]) -> BackendResultType: pass

    def run(self, case: ThinkingCase) -> BackendResultType:
        return self.execute([case])

