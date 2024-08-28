import time
import pytest

from kepler import Timer
from kepler.reporting import Reporter


@pytest.fixture
def timer():
    with Timer().context() as timer:
        yield timer


def events_from(timer: Timer):
    _, *events = Reporter().events(timer, [])
    return events


@pytest.mark.usefixtures("instant_sleep")
def test_split(timer: Timer):
    split = timer.stopwatch("watch")
    split("1")
    time.sleep(1)
    split("2")
    time.sleep(1)
    events = events_from(timer)
    assert len(events) == 3
    assert all("watch" in event.call_stack[0] for event in events)
    raise Exception(events)
