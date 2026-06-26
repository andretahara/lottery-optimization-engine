# CLAUDE.md - Lottery Optimization Engine

Regras do repositorio. Ler ANTES de qualquer trabalho. Ao retomar apos interrupcao,
reler tambem `docs/ROADMAP.md` e `docs/DECISIONS.md`, inspecionar a arvore e o estado
dos testes, e continuar do ponto pendente (nunca recomecar do zero).

## Regra fundamental (inviolavel)

Todas as dezenas tem a MESMA probabilidade. A engine NAO preve sorteios e NAO altera
a probabilidade individual de nenhuma combinacao.

PROIBIDO usar como sinal de selecao: numeros quentes, frios, atrasados, ciclos, datas,
numerologia, padroes historicos, supersticao. Qualquer modulo que sugira previsao e bug.

O que a engine otimiza (e SO isso): cobertura combinatoria real, cobertura de
pares/trincas/quadras/subconjuntos, diversidade entre apostas, baixa sobreposicao,
frequencia equilibrada de dezenas DENTRO da carteira gerada, distancia media alta,
baixa redundancia, aderencia ao orcamento, exportacao clara.

## Aviso obrigatorio em toda saida probabilistica

Texto exato (constante unica no codigo, ver `disclaimer.py`):

> Esta otimizacao nao preve numeros sorteados. Ela apenas maximiza cobertura e reduz
> redundancia. Todas as combinacoes possiveis continuam tendo a mesma probabilidade
> individual.

## Loteria = configuracao, nunca hardcode

Cada loteria (Quina, Quina de Sao Joao, Mega-Sena, Mega da Virada, Lotofacil, Lotomania,
Timemania, Dupla Sena, futuras) e uma `LotterySpec` / preset no registry. Logica de
negocio le a spec; nunca ramifica por nome de loteria espalhado pelo codigo.

## Precos

NUNCA inventar preco oficial. Precos sao configuraveis (placeholder `None` ate o usuario
preencher). Toda geracao de aposta real exige o usuario setar os precos vigentes.

## Git

- `git push` SO com pedido explicito do usuario. Commits LOCAIS frequentes e descritivos = checkpoints.
- Nunca `git add -A` / `git add .`. Paths especificos. Conferir `git status --short` antes do commit.

## Qualidade

- Fatias verticais: spec -> implementacao -> testes -> rodar -> corrigir -> auditar -> documentar.
- "Pronto" exige prova: testes rodados e verdes. Nao confiar em auto-afirmacao.
- Ambiguidade tecnica: escolher opcao razoavel, registrar ADR em `docs/DECISIONS.md`, seguir.
- Nunca deixar o projeto quebrado. Parar so em ponto com testes verdes ou estado documentado.
