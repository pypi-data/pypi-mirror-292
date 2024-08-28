#todo import stuff from aspects.current
from contextlib import contextmanager
from typing import NamedTuple

from thinking_tests.protocol import CaseCoordinates, TestStage


class CurrentTesting(NamedTuple):
    coordinates: CaseCoordinates
    stage: TestStage


CURRENT: CurrentTesting = None


@contextmanager
def test_stage(coordinates: CaseCoordinates, stage: TestStage):
    global CURRENT
    previous = CURRENT
    try:
        CURRENT = CurrentTesting(coordinates, stage)
        yield
    finally:
        CURRENT = previous


def current_metadata() -> CurrentTesting:
    return CURRENT


def current_case() -> CaseCoordinates:
    return current_metadata().coordinates

current_coordinates = current_case


def current_case_id() -> str:
    return current_case().id


def current_case_name() -> str:
    return current_case().name


def current_stage() -> TestStage:
    return current_metadata().stage
