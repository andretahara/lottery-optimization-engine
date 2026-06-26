import pytest

from lottery_engine.spec import LotterySpec


def make(**over):
    base = dict(
        name="Test", pool=60, draw_size=6, min_marks=6, max_marks=15, prize_tiers=(4, 5, 6)
    )
    base.update(over)
    return LotterySpec(**base)


def test_valid_spec_and_derived():
    s = make()
    assert s.pool == 60
    assert s.number_end == 60
    assert list(s.number_universe()) == list(range(1, 61))
    assert s.total_outcomes() == 50_063_860
    assert s.simple_combinations(7) == 7   # C(7,6)
    assert s.simple_combinations(15) == 5005  # C(15,6)


def test_number_start_zero_universe():
    s = make(pool=100, draw_size=20, min_marks=50, max_marks=50,
             prize_tiers=(0, 15, 20), number_start=0)
    assert s.number_end == 99
    assert list(s.number_universe())[:3] == [0, 1, 2]


def test_extra_rules_is_readonly():
    s = make(extra_rules={"two_draws": True})
    assert s.extra_rules["two_draws"] is True
    with pytest.raises(TypeError):
        s.extra_rules["x"] = 1  # MappingProxyType bloqueia


@pytest.mark.parametrize("over", [
    dict(pool=0),
    dict(draw_size=0),
    dict(draw_size=61),               # > pool
    dict(min_marks=5),               # < draw_size
    dict(max_marks=61),              # > pool
    dict(min_marks=10, max_marks=8),  # min > max
    dict(prize_tiers=()),            # vazio
    dict(prize_tiers=(6, 5, 4)),     # nao crescente
    dict(prize_tiers=(4, 5, 7)),     # tier > draw_size
    dict(name=""),
])
def test_invalid_specs_raise(over):
    with pytest.raises(ValueError):
        make(**over)


def test_price_table_out_of_range_raises():
    from decimal import Decimal
    with pytest.raises(ValueError):
        make(price_table={5: Decimal("6.00")})  # 5 < min_marks 6


def test_simple_combinations_rejects_out_of_range_marks():
    s = make()
    with pytest.raises(ValueError):
        s.simple_combinations(16)  # > max_marks
