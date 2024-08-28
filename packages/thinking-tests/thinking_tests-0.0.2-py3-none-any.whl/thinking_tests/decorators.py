from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from logging import getLogger
from os.path import basename
from typing import Callable, NamedTuple

from thinking_tests.fluent_decorator import fluent_decorator
from thinking_tests.protocol import ThinkingCase, CaseCoordinates
from thinking_tests.runner.run import run
from thinking_tests.simple import SimpleThinkingCase

log = getLogger(__name__)

def noop(*args, **kwargs): pass

CURRENT_SETUP = noop
CURRENT_TEARDOWN = noop

KNOWN_CASES: list[ThinkingCase] = []


class WrappedMethod(NamedTuple):
    case: ThinkingCase

    def __call__(self):
        run(self.case)

@contextmanager
def setup(impl: Callable):
    global CURRENT_SETUP
    previous = CURRENT_SETUP
    try:
        CURRENT_SETUP = impl
        yield
    finally:
        CURRENT_SETUP = previous


@contextmanager
def teardown(impl: Callable):
    global CURRENT_TEARDOWN
    previous = CURRENT_TEARDOWN
    try:
        CURRENT_TEARDOWN = impl
        yield
    finally:
        CURRENT_TEARDOWN = previous

# def _lineno(foo):
#     try:
#         return foo.__code__.co_firstlineno
#     except:
#         return None

@fluent_decorator
def case(name=None, *, setup=None, teardown=None):
    def decorator(f):
        nonlocal name, setup, teardown
        name = name or f.__name__
        setup = setup or CURRENT_SETUP
        teardown = teardown or CURRENT_TEARDOWN
        case = SimpleThinkingCase(
            CaseCoordinates(f.__module__, name),
            setup,
            f,
            teardown
        )
        KNOWN_CASES.append(case)
        return case
    return decorator