from decimal import Decimal

import pytest

from lottery_optimizer.core.cost import CostModel
from lottery_optimizer.core.game import GameSpec
from lottery_optimizer.core.portfolio import Portfolio
from lottery_optimizer.core.ticket import Ticket
from lottery_optimizer.core.validation import SpecError


def spec(price_table=None):
    return GameSpec(game_id="t", name="T", universe_min=1, universe_max=60, draw_size=6,
                    allowed_ticket_sizes=(6, 7), price_table=price_table)


def test_official_price_not_estimate():
    cm = CostModel(spec({6: Decimal("6.00"), 7: Decimal("42.00")}))
    r = cm.ticket_cost(6)
    assert r.amount == Decimal("6.00") and r.is_estimate is False


def test_estimate_from_base_marked():
    cm = CostModel(spec(), base_cost=Decimal("5.00"))
    r6 = cm.ticket_cost(6)   # C(6,6)=1
    r7 = cm.ticket_cost(7)   # C(7,6)=7
    assert r6.amount == Decimal("5.00") and r6.is_estimate is True
    assert r7.amount == Decimal("35.00") and r7.is_estimate is True


def test_estimate_uses_official_simple_as_base():
    cm = CostModel(spec({6: Decimal("6.00")}))  # base = preco do simples (size==draw_size)
    r7 = cm.ticket_cost(7)
    assert r7.amount == Decimal("42.00") and r7.is_estimate is True  # 6 * C(7,6)=6*7


def test_no_price_no_base_raises():
    with pytest.raises(SpecError):
        CostModel(spec()).ticket_cost(6)


def test_portfolio_cost_and_balance():
    cm = CostModel(spec({6: Decimal("6.00"), 7: Decimal("42.00")}))
    p = Portfolio(spec({6: Decimal("6.00"), 7: Decimal("42.00")}),
                  [Ticket(numbers=tuple(range(1, 7))), Ticket(numbers=tuple(range(1, 8)))])
    total = cm.portfolio_cost(p)
    assert total.amount == Decimal("48.00") and total.is_estimate is False
    assert cm.balance(p, Decimal("50.00")).amount == Decimal("2.00")


def test_cost_per_simple_combination():
    cm = CostModel(spec({7: Decimal("42.00")}))
    r = cm.cost_per_simple_combination(7)  # 42 / C(7,6)=7
    assert r.amount == Decimal("6")
    assert cm.equivalent_simple_combinations(7) == 7
