"""Erros e helpers de validacao compartilhados."""

from __future__ import annotations


class SpecError(ValueError):
    """Configuracao de loteria incoerente."""


class TicketError(ValueError):
    """Jogo invalido (dezenas repetidas, fora do universo, etc)."""


def ensure(condition: bool, message: str, exc: type[ValueError] = ValueError) -> None:
    """Levanta `exc(message)` se a condicao for falsa."""
    if not condition:
        raise exc(message)
