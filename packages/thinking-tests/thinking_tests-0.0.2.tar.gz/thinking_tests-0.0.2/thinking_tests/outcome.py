from dataclasses import dataclass
from typing import TypeVar

def parenthesis_if_not_empty(s: str):
    if s:
        return f"(${s})"
    return s

class Outcome:
    def __str__(self):
        return type(self).__name__[:-1*len("Outcome")] + parenthesis_if_not_empty(self.__describe__())

    def __describe__(self) -> str:
        return ""

class SuccessOutcome(Outcome): pass

Outcome.Success = SuccessOutcome

ResultType = TypeVar("ResultType")

@dataclass
class ResultOutcome(SuccessOutcome):
    result: ResultType

    def __describe__(self):
        return "result="+repr(self.result)

Outcome.Result = ResultOutcome

@dataclass
class FailureOutcome(Outcome):
    reason: BaseException

    def reraise(self):
        raise self.reason

    def __describe__(self):
        return "reason="+repr(self.reason)

Outcome.Failure = FailureOutcome

#todo at some point, extract to commons