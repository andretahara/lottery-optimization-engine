"""Guarda de precos: bloqueia execucao real com preco nulo/exemplo (ADR-020).

O usuario e responsavel pelos precos oficiais. A engine nao busca preco na internet;
ela apenas IMPEDE que precos nao verificados sejam usados numa aposta real sem consentimento
explicito (flag --allow-example-prices).
"""

from __future__ import annotations

from .game import GameSpec


class PriceError(RuntimeError):
    """Precos nao utilizaveis para execucao real."""


def prices_are_official(spec: GameSpec) -> bool:
    return spec.price_status == "official" and bool(spec.price_table)


def assert_prices_usable(spec: GameSpec, *, allow_example: bool = False) -> None:
    """Levanta PriceError se os precos nao puderem ser usados numa execucao real.

    - 'official' -> sempre ok.
    - 'example'  -> ok somente com allow_example=True.
    - 'unset'/null -> nunca ok (nao ha numeros para custear).
    """
    if prices_are_official(spec):
        return
    if spec.price_status == "example" and spec.price_table:
        if allow_example:
            return
        raise PriceError(
            f"'{spec.game_id}' usa precos de EXEMPLO (nao oficiais). Verifique o preco "
            "vigente e marque price_status='official', ou passe --allow-example-prices "
            "para prosseguir ciente de que sao ilustrativos."
        )
    raise PriceError(
        f"'{spec.game_id}' nao tem precos oficiais configurados (price_status="
        f"'{spec.price_status}'). Configure price_table com o preco vigente da Caixa "
        "(ADR-006) antes de uma aposta real."
    )


def price_config_summary(spec: GameSpec) -> str:
    """Linha auditavel de qual configuracao de preco foi usada (vai no relatorio)."""
    checked = spec.official_price_last_checked or "n/d"
    note = spec.price_source_note or "sem nota"
    return f"price_status={spec.price_status}; verificado={checked}; fonte={note}"
