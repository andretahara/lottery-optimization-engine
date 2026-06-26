"""Primitivas combinatorias puras, reusadas por spec/generate/wheels/metrics (ADR-011)."""

from __future__ import annotations

import math
from itertools import combinations
from typing import Iterable, Iterator, Sequence, TypeVar

T = TypeVar("T")


def n_choose_k(n: int, k: int) -> int:
    """C(n, k) exato. Retorna 0 se k < 0 ou k > n. n deve ser >= 0."""
    if n < 0:
        raise ValueError(f"n deve ser >= 0, recebido {n}")
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def iter_combinations(items: Sequence[T], k: int) -> Iterator[tuple[T, ...]]:
    """Itera todas as combinacoes de tamanho k dos itens (ordem estavel)."""
    if k < 0:
        raise ValueError(f"k deve ser >= 0, recebido {k}")
    return combinations(items, k)


def k_subsets(ticket: Iterable[int], k: int) -> Iterator[tuple[int, ...]]:
    """k-subconjuntos de um jogo, com dezenas ordenadas. Base de cobertura de pares/trincas."""
    ordered = tuple(sorted(ticket))
    return combinations(ordered, k)
