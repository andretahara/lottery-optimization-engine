import pytest
from pydantic import ValidationError

from lottery_optimizer.core.game import GameSpec
from lottery_optimizer.games import registry

EXPECTED = {"mega-sena", "quina", "lotofacil", "lotomania", "timemania", "dupla-sena"}


def make(**over):
    base = dict(slug="t", name="Test", pool=60, draw_size=6, min_marks=6, max_marks=15,
                prize_tiers=(4, 5, 6))
    base.update(over)
    return GameSpec(**base)


def test_valid_spec_derived():
    s = make()
    assert s.total_outcomes() == 50_063_860
    assert s.number_end == 60
    assert list(s.number_universe())[:2] == [1, 2]
    assert s.simple_combinations(15) == 5005


@pytest.mark.parametrize("over", [
    dict(pool=0), dict(draw_size=0), dict(draw_size=61), dict(min_marks=5),
    dict(max_marks=61), dict(min_marks=10, max_marks=8), dict(prize_tiers=()),
    dict(prize_tiers=(6, 5, 4)), dict(prize_tiers=(4, 5, 7)), dict(name=""),
])
def test_invalid_specs_raise(over):
    with pytest.raises(ValidationError):
        make(**over)


def test_registry_has_six_games():
    assert set(registry.available()) == EXPECTED


@pytest.mark.parametrize("slug,pool,draw,mn,mx,tiers", [
    ("mega-sena", 60, 6, 6, 15, (4, 5, 6)),
    ("quina", 80, 5, 5, 7, (2, 3, 4, 5)),
    ("lotofacil", 25, 15, 15, 18, (11, 12, 13, 14, 15)),
    ("lotomania", 100, 20, 50, 50, (0, 15, 16, 17, 18, 19, 20)),
    ("timemania", 80, 7, 10, 10, (3, 4, 5, 6, 7)),
    ("dupla-sena", 50, 6, 6, 15, (3, 4, 5, 6)),
])
def test_structural_params(slug, pool, draw, mn, mx, tiers):
    s = registry.get(slug)
    assert (s.pool, s.draw_size, s.min_marks, s.max_marks, s.prize_tiers) == (pool, draw, mn, mx, tiers)


def test_prices_none_and_specials():
    for slug in registry.available():
        assert registry.get(slug).price_table is None
    assert registry.get("lotomania").number_start == 0
    assert registry.get("dupla-sena").extra_rules.get("two_draws") is True


def test_unknown_slug():
    with pytest.raises(KeyError):
        registry.get("super-sete")
