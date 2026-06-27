"""Stub do otimizador 'genetic'. Implementacao real em bloco futuro do ROADMAP."""

from __future__ import annotations

from ..core.game import GameSpec
from ..core.portfolio import Portfolio
from ..utils.random import SeededRng
from .base import Optimizer


class GeneticOptimizer(Optimizer):
    name = "genetic"

    def optimize(
        self, spec: GameSpec, num_tickets: int, marks: int, rng: SeededRng
    ) -> Portfolio:
        raise NotImplementedError(f"otimizador '{self.name}' ainda nao implementado")
