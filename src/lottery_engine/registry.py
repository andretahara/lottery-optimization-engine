"""Presets das loterias-alvo (ADR-003). Precos = None ate o usuario configurar (ADR-006).

Parametros estruturais (pool/draw/marks/tiers) conferidos nas regras oficiais da CAIXA
em jun/2026 (loterias.caixa.gov.br). Sao publicos e estaveis, mas se a CAIXA alterar uma
regra, ajustar AQUI - logica de negocio nunca ramifica por nome de loteria.
"""

from __future__ import annotations

from typing import Callable

from .spec import LotterySpec

# Registry interno: slug -> factory de LotterySpec.
_FACTORIES: dict[str, Callable[[], LotterySpec]] = {}


def _register(slug: str) -> Callable[[Callable[[], LotterySpec]], Callable[[], LotterySpec]]:
    def deco(factory: Callable[[], LotterySpec]) -> Callable[[], LotterySpec]:
        _FACTORIES[slug] = factory
        return factory

    return deco


@_register("mega-sena")
def _mega_sena() -> LotterySpec:
    return LotterySpec(
        name="Mega-Sena",
        pool=60,
        draw_size=6,
        min_marks=6,
        max_marks=15,
        prize_tiers=(4, 5, 6),
    )


@_register("mega-sena-virada")
def _mega_virada() -> LotterySpec:
    return LotterySpec(
        name="Mega-Sena da Virada",
        pool=60,
        draw_size=6,
        min_marks=6,
        max_marks=15,
        prize_tiers=(4, 5, 6),
        extra_rules={"special_draw": True, "no_accumulation": True},
    )


@_register("quina")
def _quina() -> LotterySpec:
    return LotterySpec(
        name="Quina",
        pool=80,
        draw_size=5,
        min_marks=5,
        max_marks=7,
        prize_tiers=(2, 3, 4, 5),
    )


@_register("quina-sao-joao")
def _quina_sao_joao() -> LotterySpec:
    return LotterySpec(
        name="Quina de São João",
        pool=80,
        draw_size=5,
        min_marks=5,
        max_marks=7,
        prize_tiers=(2, 3, 4, 5),
        extra_rules={"special_draw": True, "no_accumulation": True},
    )


@_register("lotofacil")
def _lotofacil() -> LotterySpec:
    return LotterySpec(
        name="Lotofácil",
        pool=25,
        draw_size=15,
        min_marks=15,
        max_marks=18,
        prize_tiers=(11, 12, 13, 14, 15),
    )


@_register("lotomania")
def _lotomania() -> LotterySpec:
    # Marca exatamente 50 de 100 dezenas (0-99); premia 15..20 acertos OU 0 acertos.
    return LotterySpec(
        name="Lotomania",
        pool=100,
        draw_size=20,
        min_marks=50,
        max_marks=50,
        prize_tiers=(0, 15, 16, 17, 18, 19, 20),
        number_start=0,
    )


@_register("timemania")
def _timemania() -> LotterySpec:
    # Marca exatamente 10 de 80; sorteia 7; premia 3..7 acertos + Time do Coracao (a parte).
    return LotterySpec(
        name="Timemania",
        pool=80,
        draw_size=7,
        min_marks=10,
        max_marks=10,
        prize_tiers=(3, 4, 5, 6, 7),
        extra_rules={"team_of_heart": True},
    )


@_register("dupla-sena")
def _dupla_sena() -> LotterySpec:
    # Dois sorteios por concurso; ganha em qualquer um deles.
    return LotterySpec(
        name="Dupla Sena",
        pool=50,
        draw_size=6,
        min_marks=6,
        max_marks=15,
        prize_tiers=(3, 4, 5, 6),
        extra_rules={"two_draws": True},
    )


def available() -> tuple[str, ...]:
    """Slugs das loterias registradas, ordenados."""
    return tuple(sorted(_FACTORIES))


def get(slug: str) -> LotterySpec:
    """Retorna a LotterySpec do slug. Levanta KeyError se desconhecido."""
    try:
        factory = _FACTORIES[slug]
    except KeyError:
        raise KeyError(
            f"loteria '{slug}' desconhecida; disponiveis: {', '.join(available())}"
        ) from None
    return factory()
