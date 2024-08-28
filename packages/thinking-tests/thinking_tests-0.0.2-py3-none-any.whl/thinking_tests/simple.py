import inspect
from dataclasses import dataclass
from typing import Callable, TypeVar, get_type_hints

from thinking_tests.outcome import Outcome, ResultType
from thinking_tests.protocol import ThinkingCase, Setup, CaseCoordinates

T = TypeVar("T")

def _describe_args(callable: Callable) -> list[str]:
    return inspect.getargs(callable.__code__).args

def _bind_args(args: list[str], bindings: dict[str, object]) -> tuple:
    return tuple([bindings.get(k) for k in args])

@dataclass
class SimpleThinkingCase(ThinkingCase):
    coordinates: CaseCoordinates

    setup: Callable[[], Setup]
    body: Callable[[...], ResultType]
    teardown: Callable[[...], Outcome | ResultType]

    def set_up(self) -> Setup:
        return self.setup()


    def run_body(self, setup: Setup) -> Outcome:
        args = _describe_args(self.body)

        bound = _bind_args(args, {"setup": setup})
        try:
            out = self.body(*bound)
            return Outcome.Result(out)
        except BaseException as e:
            return Outcome.Failure(e)

    def tear_down(self, setup: Setup, outcome: Outcome) -> Outcome:
        args = _describe_args(self.teardown)
        bound = _bind_args(args, {"setup": setup, "outcome": outcome})
        result = self.teardown(*bound)
        if result is None: return outcome
        if isinstance(result, Outcome): return result
        return outcome




