from abc import abstractmethod
from typing import Protocol, ContextManager

from thinking_tests.protocol import TestStage, ThinkingCase


class TestAspect(Protocol):
    @abstractmethod
    def around(self, stage: TestStage, case: ThinkingCase) -> ContextManager: pass