# Lottery Optimization Engine

![tests](https://img.shields.io/badge/tests-158%20passing-brightgreen) ![coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

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

Testes passam localmente (158 verdes, cobertura 95%) e no CI interno
(`.github/workflows/ci.yml`: ruff + pytest a cada push). O repositorio e PRIVADO,
por isso nao ha badge dinamico publico do GitHub Actions - os badges acima sao
estaticos e refletem a suite atual. Detalhe de progresso em `docs/ROADMAP.md`.

## Precos

Precos oficiais nao sao inclusos. Configure os precos vigentes na spec da loteria antes
de gerar apostas reais com orcamento monetario.
