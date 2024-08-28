from contextlib import contextmanager, ExitStack
from typing import Callable, NamedTuple, ContextManager

from thinking_tests.aspect.custom import CUSTOM_ASPECTS
from thinking_tests.aspect.defaults import DEFAULT_ASPECTS
from thinking_tests.aspect.protocol import TestAspect
from thinking_tests.protocol import TestStage, ThinkingCase


class AspectWeaver(TestAspect):
    @contextmanager
    def around(self, stage: TestStage, case: ThinkingCase) -> ContextManager:
        with ExitStack() as stack:
            for d in self.delegates:
                stack.enter_context(d.around(stage, case))
            yield

    @property
    def delegates(self) -> list[TestAspect]:
        all_aspects = DEFAULT_ASPECTS + CUSTOM_ASPECTS
        return all_aspects