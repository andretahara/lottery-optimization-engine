import pytest
from pydantic import ValidationError

from lottery_optimizer.core.game import GameSpec
from lottery_optimizer.games import registry

EXPECTED = {"mega-sena", "quina", "lotofacil", "lotomania", "timemania", "dupla-sena"}


def make(**over):
    base = dict(game_id="t", name="Test", universe_min=1, universe_max=60, draw_size=6,
                allowed_ticket_sizes=(6, 7, 15))
    base.update(over)
    return GameSpec(**base)


def test_valid_spec_derived():
    s = make()
    assert s.pool == 60
    assert s.total_outcomes() == 50_063_860
    assert s.min_ticket_size == 6 and s.max_ticket_size == 15
    assert list(s.number_universe())[:2] == [1, 2]
    assert s.simple_combinations(15) == 5005
    assert s.contains(60) and not s.contains(61)


def test_universe_zero_based():
    s = make(universe_min=0, universe_max=99, draw_size=20, allowed_ticket_sizes=(50,),
             prize_tiers=(0, 15, 20))
    assert s.pool == 100
    assert s.contains(0) and s.contains(99) and not s.contains(100)


@pytest.mark.parametrize("over", [
    dict(universe_min=10, universe_max=5),       # min > max
    dict(draw_size=0),
    dict(draw_size=61),                          # > pool
    dict(allowed_ticket_sizes=()),               # vazio
    dict(allowed_ticket_sizes=(5,)),             # < draw_size
    dict(allowed_ticket_sizes=(61,)),            # > pool
    dict(prize_tiers=(0, 7)),                    # tier > draw_size
    dict(name=""),
])
def test_invalid_specs_raise(over):
    with pytest.raises(ValidationError):
        make(**over)


def test_registry_six_games_and_params():
    assert set(registry.available()) == EXPECTED
    expect = {
        "mega-sena": (60, 6, 6, 15),
        "quina": (80, 5, 5, 15),
        "lotofacil": (25, 15, 15, 18),
        "lotomania": (100, 20, 50, 50),
        "timemania": (80, 7, 10, 10),
        "dupla-sena": (50, 6, 6, 15),
    }
    for gid, (pool, draw, mn, mx) in expect.items():
        s = registry.get(gid)
        assert (s.pool, s.draw_size, s.min_ticket_size, s.max_ticket_size) == (pool, draw, mn, mx)
    assert registry.get("lotomania").universe_min == 0
    for gid in registry.available():
        # quina tem precos oficiais preenchidos (ADR-034); demais permanecem None
        if gid == "quina":
            assert registry.get(gid).price_table is not None
        else:
            assert registry.get(gid).price_table is None


def test_unknown_game():
    with pytest.raises(KeyError):
        registry.get("super-sete")
