# ROADMAP - Lottery Optimization Engine

Legenda: `[x]` feito  `[~]` em andamento  `[ ]` pendente

Atualizar a cada unidade de trabalho concluida. Commit local em cada checkpoint.

---

## Objetivo

Engine generica para loterias combinatorias. Loteria como configuracao (`LotterySpec`/preset),
nunca hardcode. Otimiza COBERTURA combinatoria e qualidade de carteira (diversidade,
sobreposicao, balanco, distancia, orcamento). NAO preve sorteio, NAO altera probabilidade
individual. Ver `CLAUDE.md` (regra fundamental) e `docs/MATH_MODEL.md`.

Loterias-alvo: Quina, Quina de Sao Joao, Mega-Sena, Mega-Sena da Virada, Lotofacil,
Lotomania, Timemania, Dupla Sena, + configuraveis futuras.

## Stack (ver ADRs em docs/DECISIONS.md)

Python 3.12, layout `src/`, build `pyproject.toml`, testes `pytest` (+ hypothesis), lint `ruff`.
Nucleo importavel (lib) + CLI fino. Deps minimas: stdlib no nucleo, `numpy` p/ metricas,
`openpyxl` p/ Excel. Sem rede.

## Arquitetura (modulos) - detalhe em docs/ARCHITECTURE.md

```
src/lottery_engine/
  disclaimer.py     combinatorics.py   spec.py        registry.py
  rng.py            generate.py        wheels.py      metrics.py
  portfolio.py      export.py          cli.py         __init__.py
tests/  (um test_<modulo> por modulo)
```

## Fases incrementais (Blocos)

- [x] **Bloco 0 - Fundacao**: repo, remote, `.gitignore`, commit inicial.
- [x] **Bloco 0.1 - Base documental**: `CLAUDE.md` (memoria operacional, 13 regras + comandos),
      `README.md`, `docs/SPEC.md`, `docs/ARCHITECTURE.md`, `docs/MATH_MODEL.md`, `docs/ROADMAP.md`,
      `docs/DECISIONS.md` (ADR-001..012), `docs/TESTING.md`. Sem codigo de engine.
- [x] **Bloco 1 - Scaffold + Spec + Registry**: `pyproject.toml`, `src/` layout, `disclaimer.py`,
      `combinatorics.py`, `LotterySpec`+validacao, presets das 8 loterias (precos None), testes verdes.
- [ ] **Bloco 2 - Geracao justa + orcamento**: `rng.py` (seed reproducivel), `generate.py`
      (jogos uniformes sem vies; respeita marks e orcamento), testes (uniformidade + repro).
- [ ] **Bloco 3 - Metricas de carteira**: `metrics.py` (cobertura pares/trincas, sobreposicao,
      balanco de frequencia, distancia media, redundancia), testes.
- [ ] **Bloco 4 - Wheeling / covering designs**: `wheels.py` (garantia K-de-M verificavel,
      jogos abreviados via greedy), teste de forca bruta que PROVA a garantia em casos pequenos.
- [ ] **Bloco 5 - Otimizacao de carteira**: `portfolio.py` (greedy + busca local, funcao-objetivo
      de metrics sob orcamento), testes comparando vs baseline aleatoria.
- [ ] **Bloco 6 - Export + disclaimer**: `export.py` (CSV, Excel, relatorio), disclaimer em toda
      saida; testes de presenca do aviso e integridade.
- [ ] **Bloco 7 - CLI + ponta-a-ponta**: `cli.py` (loteria, orcamento, modo, seed, export),
      demo reproducivel, testes de CLI.
- [ ] **Bloco 8 - Auditoria + performance + docs**: stress em loterias grandes (Lotofacil/Lotomania),
      edge cases, README de uso, auditoria critica anti-previsao.

## Proximo passo seguro

Bloco 2 (geracao justa + orcamento): rng.py + generate.py. Aguardando instrucao do usuario.
