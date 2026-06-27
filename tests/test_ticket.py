import pytest
from pydantic import ValidationError

from lottery_optimizer.core.ticket import Ticket
from lottery_optimizer.core.validation import TicketError


def test_canonical_sorted_unique():
    assert Ticket(numbers=(5, 1, 3)).numbers == (1, 3, 5)


@pytest.mark.parametrize("nums", [(1, 1, 2), ()])
def test_invalid_numbers(nums):
    with pytest.raises(ValidationError):
        Ticket(numbers=nums)


def test_matches_overlap_len():
    t = Ticket(numbers=(1, 2, 3, 4, 5, 6))
    assert t.matches((4, 5, 6, 7, 8, 9)) == 3
    assert t.overlap(Ticket(numbers=(1, 2, 10))) == 2
    assert len(t) == 6


def test_validate_against_spec(mini):
    Ticket.create(mini, (1, 2, 3))            # tamanho 3 permitido, dentro do universo
    with pytest.raises(TicketError):
        Ticket.create(mini, (1, 2))           # tamanho 2 nao permitido
    with pytest.raises(TicketError):
        Ticket.create(mini, (1, 2, 99))       # 99 fora do universo
