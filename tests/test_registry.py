import pytest

from lottery_engine import registry
from lottery_engine.spec import LotterySpec

EXPECTED = {
    "mega-sena", "mega-sena-virada", "quina", "quina-sao-joao",
    "lotofacil", "lotomania", "timemania", "dupla-sena",
}


def test_all_lotteries_available():
    assert set(registry.available()) == EXPECTED


def test_get_returns_valid_spec_for_each():
    for slug in registry.available():
        spec = registry.get(slug)
        assert isinstance(spec, LotterySpec)
        spec.validate()  # nao levanta


def test_prices_are_none_placeholder():
    for slug in registry.available():
        assert registry.get(slug).price_table is None


def test_unknown_slug_raises():
    with pytest.raises(KeyError):
        registry.get("super-sete")


@pytest.mark.parametrize("slug,pool,draw,mn,mx,tiers", [
    ("mega-sena", 60, 6, 6, 15, (4, 5, 6)),
    ("mega-sena-virada", 60, 6, 6, 15, (4, 5, 6)),
    ("quina", 80, 5, 5, 7, (2, 3, 4, 5)),
    ("quina-sao-joao", 80, 5, 5, 7, (2, 3, 4, 5)),
    ("lotofacil", 25, 15, 15, 18, (11, 12, 13, 14, 15)),
    ("lotomania", 100, 20, 50, 50, (0, 15, 16, 17, 18, 19, 20)),
    ("timemania", 80, 7, 10, 10, (3, 4, 5, 6, 7)),
    ("dupla-sena", 50, 6, 6, 15, (3, 4, 5, 6)),
])
def test_structural_params(slug, pool, draw, mn, mx, tiers):
    s = registry.get(slug)
    assert (s.pool, s.draw_size, s.min_marks, s.max_marks, s.prize_tiers) == (
        pool, draw, mn, mx, tiers
    )


def test_lotomania_universe_starts_at_zero():
    assert registry.get("lotomania").number_start == 0


def test_special_draw_extra_rules():
    assert registry.get("mega-sena-virada").extra_rules.get("no_accumulation") is True
    assert registry.get("dupla-sena").extra_rules.get("two_draws") is True
    assert registry.get("timemania").extra_rules.get("team_of_heart") is True
