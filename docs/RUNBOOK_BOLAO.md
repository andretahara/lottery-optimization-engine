# RUNBOOK - Uso real no bolao

> Esta otimizacao nao preve numeros sorteados. Ela apenas maximiza cobertura e reduz
> redundancia. Todas as combinacoes possiveis continuam tendo a mesma probabilidade individual.

Passo a passo para gerar, conferir e registrar apostas com a engine. A engine NAO inventa
preco oficial: voce e responsavel por atualizar o preco vigente.

## 1. Atualizar precos oficiais
Verifique o preco vigente da aposta simples em https://loterias.caixa.gov.br. Edite o YAML de
override (ex.: `lottery_optimizer/games/configs/user_overrides.example.yaml` copiado para um
arquivo seu) preenchendo `price_table`, `price_status: official` e `official_price_last_checked`.

## 2. Escolher o jogo
`python -m lottery_optimizer.cli.main list-games` e `inspect-game <game_id>`.

## 3. Configurar orcamento
Defina o numero de apostas (`--budget`) ou, nos scripts de exemplo, o orcamento monetario no YAML.

## 4. Escolher seed
Escolha uma seed inteira fixa (ex.: 20260627). A MESMA seed reproduz a MESMA carteira.

## 5. Rodar Quina de Sao Joao
Atualize o preco em `configs/quina_sao_joao_budget_19140.yaml` e rode
`python scripts/run_quina_sao_joao.py` (ou com `--allow-example-prices` so para ensaio).

## 6. Rodar Mega-Sena da Virada
Atualize o preco em `configs/mega_sena_virada_example.yaml` e rode
`python scripts/run_mega_sena_virada.py`.

## 7. Verificar CSV
Abra `jogos.csv` (UTF-8). Colunas: jogo_id, aposta_id, tamanho, dezena_01... Dezenas ordenadas.

## 8. Verificar Excel
Abra `jogos.xlsx`. Abas: Resumo, Jogos, Frequencias, Metricas, Cobertura, ScoreHistory,
Configuracao, AvisoMatematico.

## 9. Conferir custo total
No relatorio/Excel (Resumo). Se aparecer "(ESTIMATIVA)" ou "n/d", o preco NAO e oficial - volte ao passo 1.

## 10. Conferir saldo
Saldo = orcamento - custo total. Deve ser >= 0.

## 11. Conferir quantidade de apostas
Confira "Apostas" no relatorio vs o esperado (orcamento / preco simples).

## 12. Interpretar probabilidade teorica
"Probabilidade teorica do premio principal" = combinacoes unicas cobertas / C(N,K). Se marcada
"[ESTIMADA]", a cobertura foi amostral (jogo grande). Lembre: NAO ha previsao.

## 13. Interpretar cobertura
Cobertura unica de pares/trincas/quadras indica diversidade e chance de faixas secundarias.
Redundancia alta = jogos parecidos (dinheiro desperdicado).

## 14. Imprimir jogos
Imprima `jogos.csv`/`relatorio.txt` para registrar na loterica.

## 15. Arquivar seed e configuracao
Guarde `config.log` (ou o YAML usado) + a seed. Sao a prova de auditoria.

## 16. Reproduzir a mesma carteira no futuro
Rode de novo com a MESMA seed, jogo, orcamento e config de preco -> carteira identica.

---
> Esta otimizacao nao preve numeros sorteados. Ela apenas maximiza cobertura e reduz
> redundancia. Todas as combinacoes possiveis continuam tendo a mesma probabilidade individual.
