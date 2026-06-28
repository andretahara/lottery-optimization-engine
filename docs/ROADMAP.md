# ROADMAP - Lottery Optimization Engine

Legenda: `[x]` feito  `[~]` em andamento  `[ ]` pendente

---

## Objetivo

Engine generica para loterias combinatorias. Loteria como configuracao (`GameSpec`/YAML),
nunca hardcode. Otimiza COBERTURA combinatoria e qualidade de carteira. NAO preve sorteio,
NAO altera probabilidade individual. Ver `CLAUDE.md` e `docs/MATH_MODEL.md`.

Loterias-alvo: Quina, Mega-Sena, Lotofacil, Lotomania, Timemania, Dupla Sena (+ variantes
especiais e novas via YAML).

## Stack

Python 3.11+, pacote flat `lottery_optimizer`, `pytest`(+hypothesis), `ruff`. Nucleo
importavel + CLI fino (typer). pydantic no dominio. Deps: numpy/pandas/pydantic/pyyaml/
openpyxl/matplotlib/typer/rich; accel opcional (scipy/ortools/numba).

## Fases incrementais (Blocos)

- [x] **Bloco 0 / 0.1 - Fundacao + base documental**: repo, CLAUDE.md (memoria operacional),
      SPEC/ARCHITECTURE/MATH_MODEL/TESTING/ROADMAP/DECISIONS.
- [x] **Bloco 1 - Esqueleto profissional**: pacote `lottery_optimizer` (core/metrics/algorithms/
      games/export/cli/utils), stubs limpos, 6 YAML, Makefile, scripts. Metricas intra-carteira reais.
- [x] **Bloco 2 - Nucleo matematico generico**: `GameSpec` (game_id/universe/allowed_ticket_sizes),
      `Ticket`/`Portfolio` spec-aware, `CostModel` (oficial vs estimativa marcada), `ProbabilityModel`
      (premio principal = K-subsets UNICOS / C(N,K); faixas inferiores hipergeometricas),
      `CombinationCoverage` (modos exact/streaming/sampled, trava anti-estouro). 49 testes verdes.
- [x] **Bloco 3 - Sistema de configuracao + guarda de precos**: GameRegistry (load/validate/list/override/custom), 6 YAML com campos de preco (price_status/official_price_last_checked/price_source_note), user_overrides.example.yaml, guarda assert_prices_usable (bloqueia null/example sem --allow-example-prices), relatorio registra config de preco. 57 testes.
- [x] **Bloco 3b - Geracao justa**: RandomBalancedOptimizer (modo uniforme justo + modo balanceado simetrico, sem favorecer dezena); guardas (marks permitido, num_tickets <= C(N,marks)); reprodutivel por seed. Teste de justica qui-quadrado. 64 testes.: `random_balanced` (amostragem uniforme sem vies, respeita
      allowed_ticket_sizes e orcamento), testes de uniformidade + reprodutibilidade.
- [x] **Bloco M - Metricas avancadas**: FrequencyMetrics, BalanceMetrics, CoverageMetrics, DistanceMetrics, PortfolioScore (pesos configuraveis YAML/JSON; main_coverage = criterio principal). 72 testes.
- [ ] **Bloco 4 - Wheeling / covering designs**: garantia K-de-M verificavel; teste de forca bruta.
- [x] **Bloco G - Geradores iniciais**: BaseGenerator (generate(spec,budget,constraints,seed)) + Random/BalancedRandom/GreedyCoverage/Diversity/HybridInitial; estrategias all_simple/fixed/mixed_ticket_sizes; reprodutivel, sem duplicatas, logs. 91 testes.
- [x] **Bloco O - Otimizadores**: BaseOptimizer + OptimizationResult + RuntimeConfig; LocalSearch/SimulatedAnnealing/Genetic/GRASP/Hybrid; movimentos (troca dezena/aposta/replace-worst); checkpoint; reprodutivel; coverage_mode auto. 102 testes.
- [ ] **Bloco 6 - Export completo**: Excel (openpyxl) + charts (matplotlib); disclaimer em tudo.
- [x] **Bloco CLI**: Typer+Rich, 9 comandos (list-games, inspect-game, validate-config, generate, optimize, report, export, compare, benchmark); aviso obrigatorio sempre, bloqueia preco exemplo, output/TS_GAME/, logs. 110 testes.
- [x] **Bloco Ex1 - Quina de Sao Joao**: scripts/run_quina_sao_joao.py + configs/quina_sao_joao_budget_19140.yaml; valida preco (PARA se null/exemplo), decide simples/multipla pelo custo por combinacao equivalente, gera+otimiza+exporta. Sem preco inventado.
- [ ] **Bloco 8 - Auditoria + performance**: stress Lotofacil/Lotomania, edge cases, auditoria anti-previsao.

## Status

TODOS os blocos cobertos (Fundacao -> Runbook). 158 testes verdes, ruff limpo. Engine generica,
matematicamente auditada, performance otimizada (suite ~19s), sem preco oficial inventado.

Pos-conclusao:
- [x] **Verificacao de prontidao (11 itens)** cristalizada em `tests/test_full_verification.py`
      (geracao -> CSV/Excel/TXT/PNG -> sem duplicatas -> orcamento -> p_main=K-subsets/C(N,K)
      -> reprodutibilidade por seed). Repo PUSHED (origin/main).
- [x] **CI GitHub Actions** (`.github/workflows/ci.yml`: ruff + pytest) + badge no README; CI verde.
- [x] **Quina com precos OFICIAIS** preenchidos (organizador + Caixa): 5..15 dezenas,
      simples R$ 3,00, multiplas C(T,5) x 3,00; guarda libera execucao real (ADR-034).
- [x] **Teste de medicao de cobertura Quina** R$ 19.140 (seed 30062026): A engine-livre
      (6380 simples) vs B enxuta fixa (10 apostas). Mesma cobertura do principal (p_main
      identica); A cobre 100% dos pares / B compacta operacionalmente. Artefatos em
      `output/quina_sao_joao/`. Detalhe e quadro em ADR-035.

Pendencia operacional: usuario preencher precos oficiais dos DEMAIS jogos antes de aposta real
(engine nunca inventa). Push da Frente 2 (Quina) pendente de pedido explicito do usuario.