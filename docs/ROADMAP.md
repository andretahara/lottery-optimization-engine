# ROADMAP - Lottery Optimization Engine

Legenda: `[x]` feito  `[~]` em andamento  `[ ]` pendente

Atualizar a cada unidade de trabalho concluida. Commit local em cada checkpoint.

---

## Objetivo

Engine generica para loterias combinatorias. Trata cada loteria como configuracao
(`LotterySpec`/preset), nunca hardcode. Otimiza COBERTURA combinatoria e qualidade de
carteira (diversidade, sobreposicao, balanco, distancia, orcamento). NAO preve sorteio,
NAO altera probabilidade individual. Ver `CLAUDE.md` regra fundamental.

Loterias-alvo: Quina, Quina de Sao Joao, Mega-Sena, Mega-Sena da Virada, Lotofacil,
Lotomania, Timemania, Dupla Sena, + configuraveis futuras.

## Stack (ver ADRs em docs/DECISIONS.md)

- Python 3.12, layout `src/`, build via `pyproject.toml`, testes `pytest`.
- Nucleo importavel (lib) + CLI fino por cima.
- Deps minimas: stdlib (`itertools`, `random`) no nucleo; `numpy` p/ metricas;
  `openpyxl` p/ export Excel; `click` (ou `typer`) p/ CLI. Sem acesso a rede.

## Arquitetura inicial (modulos)

```
src/lottery_engine/
  __init__.py
  disclaimer.py     # constante unica do aviso obrigatorio
  spec.py           # LotterySpec (dataclass): pool, marks min/max, tiers, precos, regras; validacao
  registry.py       # presets das loterias (precos = None placeholder ate usuario setar)
  rng.py            # RNG uniforme/justo, seed reproducivel p/ testes
  generate.py       # geracao de jogos balanceados/aleatorios justos sob orcamento
  wheels.py         # wheeling / covering designs: garantia K-de-M, jogos abreviados
  portfolio.py      # otimizacao de carteira: diversidade, baixa sobreposicao, distancia, balanco
  metrics.py        # avaliacao de carteira: cobertura pares/trincas, overlap, balanco, redundancia
  export.py         # CSV, Excel (openpyxl), relatorio txt/md (com disclaimer obrigatorio)
  cli.py            # CLI fino (argparse/click)
tests/
  test_spec.py
  test_registry.py
  test_generate.py
  test_wheels.py
  test_portfolio.py
  test_metrics.py
  test_export.py
  test_cli.py
pyproject.toml
README.md
docs/ROADMAP.md
docs/DECISIONS.md
```

## Plano por fatias verticais (Blocos)

Cada bloco e uma fatia vertical entregavel com testes verdes. Usuario dirige a sequencia.

- [x] **Bloco 0 - Fundacao/planejamento**: repo, remote, CLAUDE.md, ROADMAP, DECISIONS, .gitignore. Commit inicial.
- [ ] **Bloco 1 - Scaffold + Spec + Registry**: `pyproject.toml`, `src/` layout, `disclaimer.py`,
      `LotterySpec` com validacao, presets das loterias (precos None), testes. Instalar dev, rodar pytest verde.
- [ ] **Bloco 2 - Geracao justa + orcamento**: `rng.py` (seed reproducivel), `generate.py`
      (jogos uniformes, sem vies; respeita marks min/max e orcamento via contagem de jogos), testes.
- [ ] **Bloco 3 - Metricas de carteira**: `metrics.py` (cobertura de pares/trincas, matriz de
      sobreposicao, balanco de frequencia das dezenas, distancia media par-a-par, indice de redundancia), testes.
- [ ] **Bloco 4 - Wheeling / covering designs**: `wheels.py` (garantia K-de-M verificavel,
      jogos abreviados minimos via greedy/cobertura), teste que PROVA a garantia por forca bruta em casos pequenos.
- [ ] **Bloco 5 - Otimizacao de carteira**: `portfolio.py` (greedy + busca local maximizando
      diversidade/distancia, minimizando sobreposicao/redundancia sob orcamento), testes que comparam vs baseline aleatoria.
- [ ] **Bloco 6 - Export + disclaimer**: `export.py` (CSV, Excel, relatorio txt/md), disclaimer
      presente em toda saida; testes de presenca do aviso e integridade dos arquivos.
- [ ] **Bloco 7 - CLI + fluxo ponta-a-ponta**: `cli.py` (escolher loteria, orcamento, modo
      wheel/portfolio, exportar), demo reproducivel, testes de CLI.
- [ ] **Bloco 8 - Auditoria + performance + docs**: stress em loterias grandes (Lotofacil/Lotomania),
      edge cases, README completo, exemplos. Auditoria critica anti-previsao.

## Proximo passo seguro

Bloco 1 (aguardando instrucao do usuario).
