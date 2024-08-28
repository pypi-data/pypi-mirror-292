from contextlib import contextmanager

from thinking_tests.protocol import ThinkingCase
from thinking_tests.runner.default_impl import default_runner
from thinking_tests.runner.protocol import ThinkingTestRunner

GLOBAL_RUNNER: ThinkingTestRunner = None

def get_global_runner() -> ThinkingTestRunner:
    global GLOBAL_RUNNER
    if GLOBAL_RUNNER is None:
        GLOBAL_RUNNER = default_runner()
    return GLOBAL_RUNNER

def set_global_runner(runner: ThinkingTestRunner):
    global GLOBAL_RUNNER
    GLOBAL_RUNNER = runner

@contextmanager
def as_global(runner: ThinkingTestRunner):
    global GLOBAL_RUNNER
    previous = get_global_runner()
    try:
        set_global_runner(runner)
        yield
    finally:
        GLOBAL_RUNNER = previous
