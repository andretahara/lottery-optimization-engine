"""Probabilidade de loteria. Tudo aqui reforca: otimizacao mexe em COBERTURA, nunca em
probabilidade individual (docs/MATH_MODEL.md). Funcoes puras e documentadas.
"""

from __future__ import annotations

from fractions import Fraction

from .combinations import n_choose_k


def total_outcomes(pool: int, draw_size: int) -> int:
    """C(N, K): numero de resultados equiprovaveis do sorteio."""
    return n_choose_k(pool, draw_size)


def equivalent_simple_games(marks: int, draw_size: int) -> int:
    """C(T, K): jogos simples equivalentes a uma aposta multipla de `marks` dezenas."""
    return n_choose_k(marks, draw_size)


def p_main_simple(pool: int, draw_size: int) -> Fraction:
    """Probabilidade do premio principal numa aposta simples: 1 / C(N, K)."""
    return Fraction(1, total_outcomes(pool, draw_size))


def p_main_multiple(pool: int, draw_size: int, marks: int) -> Fraction:
    """Premio principal numa aposta multipla de `marks` dezenas: C(T, K) / C(N, K)."""
    return Fraction(equivalent_simple_games(marks, draw_size), total_outcomes(pool, draw_size))


def p_at_least_one_main(pool: int, draw_size: int, distinct_games: int) -> Fraction:
    """Premio principal em >= 1 de M jogos simples DISTINTOS: M / C(N, K).

    Linear em M (limitado pelo orcamento). Jogos duplicados nao somam (docs/MATH_MODEL §6).
    """
    total = total_outcomes(pool, draw_size)
    if not (0 <= distinct_games <= total):
        raise ValueError(f"distinct_games {distinct_games} fora de [0, {total}]")
    return Fraction(distinct_games, total)


def p_exact_hits(pool: int, draw_size: int, marks: int, hits: int) -> Fraction:
    """Probabilidade de acertar exatamente `hits` dezenas com uma aposta de `marks`.

    Distribuicao hipergeometrica:
        C(T, h) * C(N - T, K - h) / C(N, K)
    onde T=marks, K=draw_size, N=pool, h=hits.
    """
    if not (0 <= hits <= min(marks, draw_size)):
        return Fraction(0, 1)
    favoraveis = n_choose_k(marks, hits) * n_choose_k(pool - marks, draw_size - hits)
    return Fraction(favoraveis, total_outcomes(pool, draw_size))
