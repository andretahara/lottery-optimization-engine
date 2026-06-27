"""Frequencia das dezenas DENTRO da carteira gerada (nao historico)."""

from __future__ import annotations

from collections import Counter

from ..core.portfolio import Portfolio


def digit_frequency(portfolio: Portfolio) -> dict[int, int]:
    """Quantas vezes cada dezena aparece na carteira."""
    counter: Counter[int] = Counter()
    for ticket in portfolio:
        counter.update(ticket.numbers)
    return dict(counter)
