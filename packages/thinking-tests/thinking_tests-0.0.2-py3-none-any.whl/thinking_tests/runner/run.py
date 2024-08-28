from thinking_tests.protocol import ThinkingCase
from thinking_tests.runner.singleton import get_global_runner

def execute(cases: list[ThinkingCase]):
    return get_global_runner().execute(cases)
def run(case: ThinkingCase):
    return get_global_runner().run(case)