"""Otimizadores de carteira. Refinam uma carteira inicial maximizando o PortfolioScore."""

from .base import BaseOptimizer, OptimizationResult, RuntimeConfig
from .genetic import GeneticOptimizer
from .grasp import GRASPOptimizer
from .hybrid import HybridOptimizer
from .local_search import LocalSearchOptimizer
from .simulated_annealing import SimulatedAnnealingOptimizer

OPTIMIZERS = {
    "local_search": LocalSearchOptimizer,
    "simulated_annealing": SimulatedAnnealingOptimizer,
    "genetic": GeneticOptimizer,
    "grasp": GRASPOptimizer,
    "hybrid": HybridOptimizer,
}

__all__ = [
    "BaseOptimizer", "OptimizationResult", "RuntimeConfig", "OPTIMIZERS",
    "LocalSearchOptimizer", "SimulatedAnnealingOptimizer", "GeneticOptimizer",
    "GRASPOptimizer", "HybridOptimizer",
]
