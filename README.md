# Lottery Optimization Engine

[![CI](https://github.com/andretahara/lottery-optimization-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/andretahara/lottery-optimization-engine/actions/workflows/ci.yml) ![coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

Engine generica para loterias combinatorias brasileiras. Otimiza **cobertura
combinatoria** e **qualidade de carteira** (diversidade, baixa sobreposicao, balanco,
distancia media, aderencia ao orcamento). Trata cada loteria como configuracao, nunca
hardcode.

> Esta otimizacao nao preve numeros sorteados. Ela apenas maximiza cobertura e reduz
> redundancia. Todas as combinacoes possiveis continuam tendo a mesma probabilidade
> individual.

## O que NAO e

Nao e preditor. Nao usa numeros quentes/frios/atrasados, datas, numerologia, ciclos ou
padroes historicos. Loteria justa = toda combinacao tem a mesma probabilidade. Ver a
regra fundamental em `CLAUDE.md` e os ADRs em `docs/DECISIONS.md`.

## Loterias-alvo

Quina, Quina de Sao Joao, Mega-Sena, Mega-Sena da Virada, Lotofacil, Lotomania,
Timemania, Dupla Sena, e outras configuraveis.

## Status

Repositorio publico. CI ao vivo via GitHub Actions
(`.github/workflows/ci.yml`: ruff + pytest a cada push) - o badge de CI acima reflete
o status do ultimo run na `main`. Suite atual: 158 testes, cobertura 95%.
Detalhe de progresso em `docs/ROADMAP.md`.

## Precos

Precos oficiais nao sao inclusos. Configure os precos vigentes na spec da loteria antes
de gerar apostas reais com orcamento monetario.
