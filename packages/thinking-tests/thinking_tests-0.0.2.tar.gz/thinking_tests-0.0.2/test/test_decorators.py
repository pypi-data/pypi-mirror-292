from unittest import TestCase

from thinking_tests.decorators import case, setup, teardown, KNOWN_CASES
from thinking_tests.protocol import ThinkingCase
from thinking_tests.simple import SimpleThinkingCase

ACCUMULATOR = []

def setupFoo1():
    return "setup1"


def setupFoo2():
    return "setup2"

def tearDownFoo1():
    return "teardown1"

def tearDownFoo2():
    return "teardown2"

@case
def case1():
    return "case1"

@case(name="custom name")
def case2():
    return "case2"

@case(setup=setupFoo1)
def case3():
    return "case3"

@case(teardown=tearDownFoo1)
def case4():
    return "case4"

with setup(setupFoo1):
    @case
    def case5():
        return "case5"

    with setup(setupFoo2):
        @case
        def case6():
            return "case6"

    with teardown(tearDownFoo1):
        @case
        def case7():
            return "case7"

        @case(setup=setupFoo2, teardown=tearDownFoo2)
        def case8():
            return "case8"

        @case("custom name")
        def case9():
            return "case9"

#todo with teardown()... - similar as with setup(...)

def unpack(c: ThinkingCase) -> tuple[str]:
    assert isinstance(c, SimpleThinkingCase)
    return c.coordinates.name, c.setup(), c.body(), c.teardown()

class DecoratorTests(TestCase):
    def setUp(self):
        self.cases = [x for x in KNOWN_CASES if x.coordinates.module_name == __name__]

    def test_number_of_discovered_is_correct(self):
        self.assertEqual(9, len(self.cases))

    def test_correct_methods_gathered(self):
        self.assertSetEqual(
            {
                ('case1', None, 'case1', None),
                ('custom name', None, 'case2', None),
                ('case3', 'setup1', 'case3', None),
                ('case4', None, 'case4', 'teardown1'),
                ('case5', 'setup1', 'case5', None),
                ('case6', 'setup2', 'case6', None),
                ('case7', 'setup1', 'case7', 'teardown1'),
                ('case8', 'setup2', 'case8', 'teardown2'),
                ('custom name', 'setup1', 'case9', 'teardown1')
            },
            set(map(unpack, self.cases))
        )