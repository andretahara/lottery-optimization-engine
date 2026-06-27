"""Custo de apostas. Precos nunca sao inventados: vem da price_table da spec (ADR-006)."""

from __future__ import annotations

from decimal import Decimal

from .game import GameSpec
from .validation import SpecError


def ticket_price(spec: GameSpec, marks: int) -> Decimal:
    """Preco de uma aposta de `marks` dezenas. Erro claro se preco nao configurado."""
    if spec.price_table is None:
        raise SpecError(
            f"price_table de '{spec.slug}' nao configurada; defina os precos oficiais "
            "vigentes antes de calcular custo monetario (ADR-006)"
        )
    if marks not in spec.price_table:
        raise SpecError(f"sem preco para {marks} marcas em '{spec.slug}'")
    return spec.price_table[marks]


def portfolio_cost(spec: GameSpec, marks_per_ticket: list[int]) -> Decimal:
    """Custo total de uma carteira, somando o preco de cada aposta."""
    return sum((ticket_price(spec, m) for m in marks_per_ticket), Decimal("0"))


def max_tickets_for_budget(spec: GameSpec, marks: int, budget: Decimal) -> int:
    """Quantos jogos de `marks` dezenas cabem no orcamento monetario."""
    price = ticket_price(spec, marks)
    if price <= 0:
        raise SpecError(f"preco invalido {price} para {marks} marcas")
    return int(budget // price)
