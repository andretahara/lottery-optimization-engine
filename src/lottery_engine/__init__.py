"""Lottery Optimization Engine.

Engine generica de otimizacao de COBERTURA combinatoria para loterias. Nao preve
sorteios e nao altera a probabilidade individual de nenhuma combinacao. Ver CLAUDE.md
(regra fundamental) e docs/MATH_MODEL.md.
"""

from .disclaimer import DISCLAIMER
from .spec import LotterySpec
from . import combinatorics, registry

__all__ = ["DISCLAIMER", "LotterySpec", "combinatorics", "registry"]
__version__ = "0.1.0"
