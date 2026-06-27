"""Primitivas combinatorias puras (ADR-011)."""

from __future__ import annotations

import math
from itertools import combinations
from typing import Iterator, Sequence, TypeVar

T = TypeVar("T")


def n_choose_k(n: int, k: int) -> int:
    """C(n, k) exato. Retorna 0 se k < 0 ou k > n. Exige n >= 0."""
    if n < 0:
        raise ValueError(f"n deve ser >= 0, recebido {n}")
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def iter_combinations(items: Sequence[T], k: int) -> Iterator[tuple[T, ...]]:
    """Itera combinacoes de tamanho k (ordem estavel)."""
    if k < 0:
        raise ValueError(f"k deve ser >= 0, recebido {k}")
    return combinations(items, k)


def k_subsets(numbers: Sequence[int], k: int) -> Iterator[tuple[int, ...]]:
    """k-subconjuntos ordenados de um jogo. Base de cobertura de pares/trincas."""
    return combinations(tuple(sorted(numbers)), k)
