"""RNG determinista. Toda aleatoriedade do nucleo passa por aqui (ADR-012)."""

from __future__ import annotations

import random
from typing import Sequence, TypeVar

T = TypeVar("T")


class SeededRng:
    """Wrapper fino sobre random.Random com seed fixa -> reprodutibilidade."""

    def __init__(self, seed: int):
        self.seed = seed
        self._rng = random.Random(seed)

    def sample(self, population: Sequence[T], k: int) -> list[T]:
        """k elementos distintos, sem reposicao."""
        return self._rng.sample(list(population), k)

    def shuffle(self, items: list[T]) -> list[T]:
        """Copia embaralhada (nao muta a entrada)."""
        out = list(items)
        self._rng.shuffle(out)
        return out

    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def random(self) -> float:
        """Float uniforme em [0, 1)."""
        return self._rng.random()

    def choice(self, seq):
        return self._rng.choice(list(seq))
