from decimal import Decimal

import pytest
from pydantic import ValidationError

from lottery_optimizer.core.game import GameSpec
from lottery_optimizer.core.pricing import PriceError, assert_prices_usable
from lottery_optimizer.games.registry import GameRegistry

EXPECTED = {"mega-sena", "quina", "lotofacil", "lotomania", "timemania", "dupla-sena"}


def test_load_all_yaml():
    reg = GameRegistry()
    assert set(reg.available()) == EXPECTED
    for gid in reg.available():
        s = reg.get(gid)
        assert s.price_table is None
        assert s.price_status == "unset"


def test_ignores_override_example_file():
    # user_overrides.example.yaml nao deve virar jogo
    assert "mega-sena" in GameRegistry().available()
    assert len(GameRegistry().available()) == 6


def test_reject_invalid_yaml(tmp_path):
    (tmp_path / "bad.yaml").write_text(
        "game_id: bad\nname: Bad\nuniverse_min: 1\nuniverse_max: 10\n"
        "draw_size: 20\nallowed_ticket_sizes: [20]\n",  # draw_size > pool
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        GameRegistry(tmp_path)


def test_block_null_price_real_run():
    spec = GameRegistry().get("mega-sena")  # price_status unset
    with pytest.raises(PriceError):
        assert_prices_usable(spec)
    with pytest.raises(PriceError):  # flag nao salva preco nulo (nao ha numeros)
        assert_prices_usable(spec, allow_example=True)


def test_example_price_needs_flag():
    reg = GameRegistry()
    reg.apply_overrides({"mega-sena": {
        "price_status": "example",
        "price_source_note": "EXAMPLE_NOT_OFFICIAL",
        "price_table": {6: Decimal("5.00")},
    }})
    spec = reg.get("mega-sena")
    with pytest.raises(PriceError):
        assert_prices_usable(spec)               # sem flag -> bloqueia
    assert_prices_usable(spec, allow_example=True)  # com flag -> ok


def test_accept_official_override():
    reg = GameRegistry()
    reg.apply_overrides({"mega-sena": {
        "price_status": "official",
        "official_price_last_checked": "2026-06-26",
        "price_source_note": "loterias.caixa.gov.br",
        "price_table": {6: Decimal("6.00")},
    }})
    assert_prices_usable(reg.get("mega-sena"))   # official -> nao levanta


def test_load_overrides_file(tmp_path):
    f = tmp_path / "ov.yaml"
    f.write_text(
        "mega-sena:\n  price_status: official\n  official_price_last_checked: '2026-06-26'\n"
        "  price_source_note: caixa\n  price_table:\n    6: '6.00'\n",
        encoding="utf-8",
    )
    reg = GameRegistry()
    reg.load_overrides_file(f)
    assert_prices_usable(reg.get("mega-sena"))


def test_custom_small_game():
    reg = GameRegistry()
    reg.add_custom(GameSpec(game_id="mini9", name="Mini9", universe_min=1, universe_max=9,
                            draw_size=3, allowed_ticket_sizes=(3, 4)))
    assert reg.get("mini9").pool == 9
    with pytest.raises(ValueError):
        reg.add_custom(GameSpec(game_id="quina", name="dup", universe_min=1, universe_max=80,
                                draw_size=5, allowed_ticket_sizes=(5,)))
