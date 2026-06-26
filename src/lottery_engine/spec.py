"""LotterySpec: loteria como configuracao (ADR-003). Sem logica de geracao aqui."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class LotterySpec:
    """Especificacao imutavel de uma loteria combinatoria.

    Universo de dezenas: inteiros de ``number_start`` a ``number_start + pool - 1``.
    Aposta marca de ``min_marks`` a ``max_marks`` dezenas; o sorteio escolhe ``draw_size``.
    ``prize_tiers`` = quantidades de acerto que premiam. ``price_table`` = None ate o
    usuario configurar precos vigentes (ADR-006).
    """

    name: str
    pool: int  # N: quantidade de dezenas no universo
    draw_size: int  # K: dezenas sorteadas
    min_marks: int  # menor T permitido na aposta
    max_marks: int  # maior T permitido na aposta
    prize_tiers: tuple[int, ...]  # acertos que premiam, crescente
    number_start: int = 1  # menor dezena (Lotomania usa 0)
    price_table: Mapping[int, Decimal] | None = None  # marcas -> preco
    extra_rules: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # congela extra_rules como mapping read-only para manter imutabilidade real
        object.__setattr__(self, "extra_rules", MappingProxyType(dict(self.extra_rules)))
        self.validate()

    @property
    def number_end(self) -> int:
        """Maior dezena do universo."""
        return self.number_start + self.pool - 1

    def number_universe(self) -> range:
        """Range das dezenas validas."""
        return range(self.number_start, self.number_end + 1)

    def validate(self) -> None:
        """Levanta ValueError se a spec for incoerente."""
        if not self.name:
            raise ValueError("name vazio")
        if self.pool <= 0:
            raise ValueError(f"pool deve ser > 0, recebido {self.pool}")
        if not (1 <= self.draw_size <= self.pool):
            raise ValueError(
                f"draw_size deve estar em [1, pool={self.pool}], recebido {self.draw_size}"
            )
        if not (1 <= self.min_marks <= self.max_marks <= self.pool):
            raise ValueError(
                f"exige 1 <= min_marks <= max_marks <= pool; recebido "
                f"min_marks={self.min_marks}, max_marks={self.max_marks}, pool={self.pool}"
            )
        if self.min_marks < self.draw_size:
            raise ValueError(
                f"min_marks ({self.min_marks}) nao pode ser menor que draw_size "
                f"({self.draw_size}): aposta precisa marcar ao menos o tamanho do sorteio"
            )
        if not self.prize_tiers:
            raise ValueError("prize_tiers vazio")
        if list(self.prize_tiers) != sorted(set(self.prize_tiers)):
            raise ValueError(f"prize_tiers deve ser crescente e sem repetidos: {self.prize_tiers}")
        max_hits = min(self.draw_size, self.max_marks)
        for tier in self.prize_tiers:
            if not (0 <= tier <= max_hits):
                raise ValueError(
                    f"tier {tier} fora de [0, {max_hits}] (min(draw_size, max_marks))"
                )
        if self.price_table is not None:
            for marks in self.price_table:
                if not (self.min_marks <= marks <= self.max_marks):
                    raise ValueError(
                        f"price_table tem marcas {marks} fora de "
                        f"[{self.min_marks}, {self.max_marks}]"
                    )

    def simple_combinations(self, marks: int) -> int:
        """C(marks, draw_size): jogos simples equivalentes a uma aposta de `marks` dezenas."""
        from .combinatorics import n_choose_k

        if not (self.min_marks <= marks <= self.max_marks):
            raise ValueError(f"marks {marks} fora de [{self.min_marks}, {self.max_marks}]")
        return n_choose_k(marks, self.draw_size)

    def total_outcomes(self) -> int:
        """C(pool, draw_size): tamanho do espaco amostral do sorteio."""
        from .combinatorics import n_choose_k

        return n_choose_k(self.pool, self.draw_size)
