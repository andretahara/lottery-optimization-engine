# MATH_MODEL - Fundamentacao matematica

Define a base probabilistica e combinatoria da engine. Tudo aqui reforca a regra
fundamental: a otimizacao mexe em COBERTURA, nunca em PROBABILIDADE individual.

## 1. Parametros

- **N**: tamanho do universo (maior dezena). Ex.: Mega-Sena N=60.
- **K**: tamanho do sorteio (dezenas sorteadas). Ex.: Mega-Sena K=6.
- **T**: tamanho da aposta (dezenas marcadas), com `K <= T <= N`.
- **custo(T)**: preco da aposta de T marcas (configuravel; nunca inventado - ADR-006).

## 2. Espaco amostral

O sorteio escolhe K dezenas distintas de N. O numero total de resultados possiveis e:

```
Total = C(N, K) = N! / (K! (N-K)!)
```

Cada um desses `C(N,K)` resultados e EQUIPROVAVEL. Exemplos:
- Mega-Sena: C(60,6)  = 50.063.860
- Quina:     C(80,5)  = 24.040.016
- Lotofacil: C(25,15) = 3.268.760

## 3. Aposta simples (T = K)

Uma aposta simples e UMA combinacao de K dezenas. Probabilidade de premio principal:

```
P_principal(simples) = 1 / C(N, K)
```

## 4. Aposta multipla (T > K) e cobertura equivalente

Marcar T > K dezenas equivale a jogar TODAS as combinacoes de tamanho K contidas nas T marcas.
O numero dessas combinacoes (cobertura simples equivalente) e:

```
C(T, K)
```

Logo uma aposta multipla de T marcas == `C(T, K)` apostas simples. Probabilidade de premio
principal de uma multipla (acertar as K sorteadas estando todas dentro das T marcas):

```
P_principal(multipla T) = C(T, K) / C(N, K)
```

Custo justo de uma multipla = `C(T,K) * custo(simples)` (a Caixa cobra exatamente isso). Ex.:
Mega com T=7 -> C(7,6)=7 jogos; T=8 -> C(8,6)=28; T=15 -> C(15,6)=5.005 jogos.

## 5. Por que multipla ~ varias simples (sem vantagem)

Razao premio/probabilidade por dinheiro:

```
P_principal(multipla) / custo(multipla) = [C(T,K)/C(N,K)] / [C(T,K)*custo_s]
                                        = 1 / (C(N,K) * custo_s)
                                        = P_principal(simples) / custo(simples)
```

A razao e CONSTANTE. Pagar por uma multipla de T marcas da exatamente a mesma probabilidade
por real que comprar `C(T,K)` simples distintas. A multipla e conveniencia/garantia de
cobertura interna (todos os subconjuntos das T marcas), nao vantagem probabilistica. O valor
esperado por real e o mesmo (e negativo, como toda loteria).

## 6. Carteira de M jogos simples distintos

Com M jogos simples DISTINTOS (sem sobreposicao de combinacao), a chance de premio principal:

```
P_principal(>=1 em M) = M / C(N, K)
```

Linear em M, e M e limitado pelo orcamento. Jogos DUPLICADOS nao somam: dois jogos iguais
cobrem 1 combinacao, nao 2. Dai a regra: **maximizar combinacoes distintas cobertas por real**.

## 7. Premios secundarios e cobertura de subconjuntos

Faixas menores (ex.: Quina/quadra na Mega) dependem de acertar J < K dezenas. Aqui a estrutura
da carteira importa: cobrir bem PARES, TRINCAS e QUADRAS aumenta a chance de faixas secundarias.
Wheeling (covering design) garante, de forma verificavel, "se K' das minhas M dezenas sairem,
ao menos um jogo tem J acertos". Isso e combinatoria pura, nao previsao.

## 8. Por que balanceamento NAO preve resultado

Equiprobabilidade: cada uma das `C(N,K)` combinacoes tem identica chance `1/C(N,K)`,
independente de quao "balanceada" parece (soma, paridade, distribuicao por colunas/linhas do
volante). Balancear a CARTEIRA muda apenas QUAIS combinacoes voce cobre e como elas se
espalham - reduz redundancia entre seus jogos. Nao move a probabilidade de nenhuma delas.
O balanceamento e propriedade da carteira, nao do sorteio.

## 9. Por que cobertura unica > padroes visuais

Padroes visuais no volante (diagonais, simetrias, "molduras") nao tem efeito probabilistico:
o sorteio nao enxerga geometria. O que importa para uma carteira sob orcamento fixo:
1. **Combinacoes distintas cobertas** (premio principal cresce linearmente com jogos distintos).
2. **Cobertura de subconjuntos** (pares/trincas/quadras) para faixas secundarias.
3. **Baixa sobreposicao/redundancia** entre jogos (jogo redundante = real desperdicado).

Maximizar cobertura unica e minimizar redundancia e a UNICA alavanca legitima. Qualquer
heuristica baseada em historico ou estetica e ruido.

## 10. Honestidade de EV

Loteria tem valor esperado negativo. A engine NAO promete lucro nem aumento de chance de
ganhar o principal alem do trivial `M/C(N,K)`. Otimiza estrutura de cobertura e, quando o
usuario joga multiplas pessoas/bolao, reduz redundancia do dinheiro gasto. Disclaimer
obrigatorio em toda saida.

## 11. Cobertura unica vs bruta (premio principal da carteira)

A engine define a probabilidade do premio principal de uma carteira como:

```
P_principal(carteira) = (# K-subsets UNICOS cobertos) / C(N, K)
```

- **Cobertura bruta** = soma de `C(T_i, K)` sobre os jogos (conta repeticoes).
- **Cobertura unica** = numero de K-subsets DISTINTOS cobertos (deduplicado). So a unica
  conta para a probabilidade: cobrir a mesma combinacao duas vezes nao aumenta a chance.

Implementado em `CombinationCoverage` com tres modos:
- **exact**: constroi o conjunto de subconjuntos unicos. Tem trava de memoria
  (`DEFAULT_EXACT_CAP`); acima dela, recusa e sugere modo amostral.
- **streaming**: gera subconjuntos preguicosamente (sem materializar tudo).
- **sampled**: estimativa Monte Carlo da fracao do espaco coberta - necessario para
  K-subsets gigantes (ex.: Lotomania, C(50,20) ~ 4.7e13, inviavel exato).

Faixas inferiores (acertar `h < K`) usam a hipergeometrica por aposta
`C(T,h)*C(N-T,K-h)/C(N,K)`; a agregacao por carteira e aproximada (cota de Boole),
nunca apresentada como exata.
