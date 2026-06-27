import pytest

from lottery_optimizer.core.portfolio import Portfolio
from lottery_optimizer.core.ticket import Ticket
from lottery_optimizer.core.validation import TicketError


def test_add_and_len():
    p = Portfolio([Ticket(numbers=(1, 2, 3)), Ticket(numbers=(4, 5, 6))])
    assert len(p) == 2
    assert list(p)[0].numbers == (1, 2, 3)


def test_no_duplicates_default():
    p = Portfolio([Ticket(numbers=(1, 2, 3))])
    with pytest.raises(TicketError):
        p.add(Ticket(numbers=(1, 2, 3)))


def test_allow_duplicates():
    p = Portfolio(allow_duplicates=True)
    p.add(Ticket(numbers=(1, 2, 3)))
    p.add(Ticket(numbers=(1, 2, 3)))
    assert len(p) == 2
