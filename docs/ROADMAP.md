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
- [ ] **Bloco 3b - Geracao justa**: `random_balanced` (amostragem uniforme sem vies, respeita
      allowed_ticket_sizes e orcamento), testes de uniformidade + reprodutibilidade.
- [ ] **Bloco 4 - Wheeling / covering designs**: garantia K-de-M verificavel; teste de forca bruta.
- [ ] **Bloco 5 - Otimizacao de carteira**: local_search/simulated_annealing/genetic/grasp sobre
      a funcao-objetivo de metrics; comparar vs baseline aleatoria.
- [ ] **Bloco 6 - Export completo**: Excel (openpyxl) + charts (matplotlib); disclaimer em tudo.
- [ ] **Bloco 7 - CLI ponta-a-ponta**: `generate` ligado aos otimizadores; demo reproducivel.
- [ ] **Bloco 8 - Auditoria + performance**: stress Lotofacil/Lotomania, edge cases, auditoria anti-previsao.

## Proximo passo seguro

Bloco 3b (geracao justa em random_balanced). Aguardando instrucao do usuario.
