"""Funcao-objetivo da carteira. Pesos configuraveis por YAML/JSON.

CRITERIO PRINCIPAL: maximizar a cobertura de K-subsets UNICOS = unica alavanca real para o
premio principal (docs/MATH_MODEL.md). Balanceamento/diversidade melhoram a estrutura da
carteira (menos redundancia) mas NAO preveem sorteio. Pesos diferentes deslocam o foco entre
premio principal (main_coverage alto) e faixas secundarias (intermediate_coverage alto).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import yaml

from ..core.game import GameSpec
from ..core.portfolio import Portfolio
from .balance import balance_score
from .coverage import CoverageMetrics, coverage_ratio
from .distance import mean_pairwise_distance
from .frequency import FrequencyMetrics

# --- compat: API simples do Bloco 1 (mantida) ---


@dataclass(frozen=True)
class PortfolioMetrics:
    pair_coverage: float
    triple_coverage: float
    mean_distance: float
    balance: float


def evaluate(portfolio: Portfolio, spec: GameSpec) -> PortfolioMetrics:
    return PortfolioMetrics(
        pair_coverage=coverage_ratio(portfolio, spec, 2),
        triple_coverage=coverage_ratio(portfolio, spec, 3),
        mean_distance=mean_pairwise_distance(portfolio),
        balance=balance_score(portfolio, spec),
    )


DEFAULT_WEIGHTS = {"pair_coverage": 0.4, "triple_coverage": 0.3, "mean_distance": 0.2, "balance": 0.1}


def score(portfolio: Portfolio, spec: GameSpec, weights: dict[str, float] | None = None) -> float:
    w = weights or DEFAULT_WEIGHTS
    m = evaluate(portfolio, spec)
    return (
        w.get("pair_coverage", 0) * m.pair_coverage
        + w.get("triple_coverage", 0) * m.triple_coverage
        + w.get("mean_distance", 0) * m.mean_distance
        + w.get("balance", 0) * m.balance
    )


# --- PortfolioScore parametrizavel ---

DEFAULT_SCORE_WEIGHTS = {
    "main_coverage": 0.35,          # cobertura UNICA de K-subsets -> premio principal (PRINCIPAL)
    "intermediate_coverage": 0.20,  # pares/trincas -> faixas secundarias
    "diversity": 0.15,              # distancia media de Jaccard
    "balance": 0.10,                # equilibrio de frequencia
    "low_redundancy": 0.10,         # unica/bruta do principal
    "budget_adherence": 0.10,       # custo dentro do orcamento
}
DEFAULT_SCORE_PENALTIES = {
    "duplicates": 1.0,       # por aposta duplicada
    "concentration": 0.10,   # * coeficiente de variacao da frequencia
    "low_distance": 0.10,    # * (1 - diversidade)
}


def load_weights(path: str | Path) -> dict:
    """Carrega config de pesos de YAML ou JSON (chaves 'weights' e/ou 'penalties' opcionais)."""
    p = Path(path)
    raw = p.read_text(encoding="utf-8")
    data = json.loads(raw) if p.suffix.lower() == ".json" else yaml.safe_load(raw)
    return data or {}


class PortfolioScore:
    """Funcao-objetivo parametrizavel. Pesos via dict ou arquivo (YAML/JSON)."""

    def __init__(self, weights: dict | None = None, penalties: dict | None = None,
                 max_memory_mode: str = "normal"):
        self.weights = {**DEFAULT_SCORE_WEIGHTS, **(weights or {})}
        self.penalties = {**DEFAULT_SCORE_PENALTIES, **(penalties or {})}
        self.max_memory_mode = max_memory_mode

    @classmethod
    def from_file(cls, path: str | Path) -> "PortfolioScore":
        cfg = load_weights(path)
        return cls(weights=cfg.get("weights"), penalties=cfg.get("penalties"))

    def breakdown(
        self, portfolio: Portfolio, spec: GameSpec, *, budget=None, cost_model=None,
        coverage_mode: str = "exact",
    ) -> dict[str, float]:
        """Componentes individuais do score (transparencia/auditoria).

        coverage_mode='auto' tenta exact e cai para sampled se a cobertura exata estourar a
        trava de memoria (jogos grandes); 'exact'/'sampled' forcam o modo.
        """
        from ..core.coverage import CONSERVATIVE_EXACT_CAP
        from ..core.validation import SpecError
        from ..utils.logging import get_logger

        cap = CONSERVATIVE_EXACT_CAP if self.max_memory_mode == "conservative" else None
        cov = CoverageMetrics(spec, exact_cap=cap)
        if coverage_mode == "auto":
            try:
                main = cov.main(portfolio, mode="exact")
            except SpecError:
                get_logger("lottery_optimizer.scoring").warning(
                    "score: cobertura principal exata estourou; usando ESTIMATIVA amostral")
                main = cov.main(portfolio, mode="sampled")
        else:
            main = cov.main(portfolio, mode=coverage_mode)
        total = spec.total_outcomes()
        diversity = mean_pairwise_distance(portfolio)
        comp = {
            "main_coverage": (main.unique / total) if total else 0.0,
            "intermediate_coverage": (
                coverage_ratio(portfolio, spec, 2) + coverage_ratio(portfolio, spec, 3)
            ) / 2,
            "diversity": diversity,
            "balance": balance_score(portfolio, spec),
            "low_redundancy": main.unique_raw_ratio,
            "budget_adherence": self._budget_adherence(portfolio, budget, cost_model),
        }
        return comp

    def _budget_adherence(self, portfolio, budget, cost_model) -> float:
        if budget is None or cost_model is None:
            return 1.0
        cost = cost_model.portfolio_cost(portfolio).amount
        if cost <= budget:
            return 1.0
        return float(budget) / float(cost) if cost > 0 else 0.0

    def _penalty_amounts(self, portfolio, spec, diversity) -> dict[str, float]:
        n = len(portfolio)
        distinct = len({t.numbers for t in portfolio})
        return {
            "duplicates": float(n - distinct),
            "concentration": FrequencyMetrics(spec).coefficient_of_variation(portfolio),
            "low_distance": 1.0 - diversity,
        }

    def score(
        self, portfolio: Portfolio, spec: GameSpec, *, budget=None, cost_model=None,
        coverage_mode: str = "exact",
    ) -> float:
        """Soma ponderada dos componentes menos as penalizacoes. Maior = melhor.

        Nao e limitado a [0,1] (penalizacoes podem deixar negativo); e uma funcao-objetivo
        de comparacao, nao uma probabilidade.
        """
        comp = self.breakdown(
            portfolio, spec, budget=budget, cost_model=cost_model, coverage_mode=coverage_mode
        )
        pen = self._penalty_amounts(portfolio, spec, comp["diversity"])
        positive = sum(self.weights.get(k, 0.0) * v for k, v in comp.items())
        negative = sum(self.penalties.get(k, 0.0) * v for k, v in pen.items())
        return positive - negative
