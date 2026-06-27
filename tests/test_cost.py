from decimal import Decimal

import pytest

from lottery_optimizer.core import cost
from lottery_optimizer.core.game import GameSpec
from lottery_optimizer.core.validation import SpecError


def spec_with_prices():
    return GameSpec(slug="t", name="T", pool=60, draw_size=6, min_marks=6, max_marks=15,
                    prize_tiers=(4, 5, 6),
                    price_table={6: Decimal("6.00"), 7: Decimal("42.00")})


def test_ticket_price():
    s = spec_with_prices()
    assert cost.ticket_price(s, 6) == Decimal("6.00")
    assert cost.ticket_price(s, 7) == Decimal("42.00")


def test_portfolio_cost():
    s = spec_with_prices()
    assert cost.portfolio_cost(s, [6, 6, 7]) == Decimal("54.00")


def test_max_tickets_for_budget():
    s = spec_with_prices()
    assert cost.max_tickets_for_budget(s, 6, Decimal("20.00")) == 3


def test_missing_price_table_raises():
    s = GameSpec(slug="t", name="T", pool=60, draw_size=6, min_marks=6, max_marks=15,
                 prize_tiers=(4, 5, 6))
    with pytest.raises(SpecError):
        cost.ticket_price(s, 6)


def test_unknown_marks_price_raises():
    with pytest.raises(SpecError):
        cost.ticket_price(spec_with_prices(), 10)
