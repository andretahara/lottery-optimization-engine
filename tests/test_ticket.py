import pytest
from pydantic import ValidationError

from lottery_optimizer.core.ticket import Ticket


def test_normalized_sorted():
    assert Ticket(numbers=(5, 1, 3)).numbers == (1, 3, 5)


def test_duplicates_rejected():
    with pytest.raises(ValidationError):
        Ticket(numbers=(1, 1, 2))


def test_empty_rejected():
    with pytest.raises(ValidationError):
        Ticket(numbers=())


def test_matches_and_overlap():
    t = Ticket(numbers=(1, 2, 3, 4, 5, 6))
    assert t.matches((4, 5, 6, 7, 8, 9)) == 3
    assert t.overlap(Ticket(numbers=(1, 2, 10))) == 2
    assert len(t) == 6
