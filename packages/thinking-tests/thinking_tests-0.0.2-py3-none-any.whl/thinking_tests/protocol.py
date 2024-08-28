from abc import abstractmethod
from enum import Enum, auto
from typing import Protocol, TypeVar, NamedTuple, runtime_checkable

from thinking_tests.outcome import Outcome

Setup = TypeVar("Setup")
Result = TypeVar("Result")


class TestStage(Enum):
    SETUP = auto()
    RUN = auto()
    TEARDOWN = auto()

class CaseCoordinates(NamedTuple):
    module_name: str
    name: str
    # lineno: int

    @property
    def id(self) -> str:
        # return f"{self.module_name} ({self.lineno}) :: ${self.name}"
        return f"{self.module_name} :: {self.name}"


@runtime_checkable
class ThinkingCase(Protocol):
    coordinates: CaseCoordinates

    @abstractmethod
    def set_up(self) -> Setup: pass

    @abstractmethod
    def run_body(self, setup: Setup) -> Outcome: pass

    @abstractmethod
    def tear_down(self, setup: Setup, outcome: Outcome) -> Outcome: pass

    def run(self):
        from thinking_tests.runner.run import run
        return run(self)

    def __call__(self):
        return self.run()

