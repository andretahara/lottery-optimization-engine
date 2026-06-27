"""Contrato comum dos otimizadores de carteira."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..core.game import GameSpec
from ..core.portfolio import Portfolio
from ..utils.random import SeededRng


class Optimizer(ABC):
    """Interface: dado spec + orcamento (numero de jogos) + RNG, produz uma carteira."""

    name: str = "optimizer"

    @abstractmethod
    def optimize(
        self, spec: GameSpec, num_tickets: int, marks: int, rng: SeededRng
    ) -> Portfolio:
        """Retorna uma carteira de `num_tickets` jogos de `marks` dezenas."""
        raise NotImplementedError
