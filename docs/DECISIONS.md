# DECISIONS - Architecture Decision Records

Formato ADR: Contexto / Decisao / Consequencia. Append-only; novas decisoes que
revertem antigas referenciam o ADR superado.

---

## ADR-001 - Linguagem: Python 3.12
- **Contexto**: Engine de combinatoria pesada + estatistica de carteira + export.
- **Decisao**: Python 3.12. `itertools`/`random` no nucleo, `numpy` p/ metricas vetoriais.
- **Consequencia**: Iteracao rapida e libs cientificas fortes. Performance bruta inferior
  a Rust em loterias enormes; mitigar com algoritmos (cobertura greedy) e numpy. Cliente externo
  consome via API futura se necessario.

## ADR-002 - Interface: biblioteca + CLI fino
- **Contexto**: Precisa ser reutilizavel e testavel sem acoplar a web.
- **Decisao**: Nucleo de funcoes puras importavel; CLI fino por cima. Sem servico HTTP no MVP.
- **Consequencia**: Alta testabilidade, baixo acoplamento. Exposicao web fica para fase futura
  (e exige defesa de endpoint antes de qualquer disparo cobrado).

## ADR-003 - Loteria como Spec configuravel, nunca hardcode
- **Contexto**: 8+ loterias com regras distintas (pool, marks, tiers, regras especiais).
- **Decisao**: `LotterySpec` (dataclass) + `registry` de presets. Logica le a spec; sem `if nome ==`.
- **Consequencia**: Adicionar loteria = adicionar config, nao codigo. Spec precisa modelar
  regras especiais (Lotomania marca 50 de 100; Dupla Sena 2 sorteios; Timemania time do coracao).

## ADR-004 - Sem sinal preditivo/historico (regra fundamental)
- **Contexto**: Falacia do apostador. Loteria justa = toda combinacao equiprovavel.
- **Decisao**: PROIBIDO quente/frio/atrasado/ciclo/data/numerologia/padrao historico/supersticao
  como sinal de selecao. Engine otimiza SO cobertura combinatoria e qualidade de carteira.
- **Consequencia**: Modulo de "estatistica descritiva sobre historico de sorteios" NAO existe.
  Metricas sao sobre a CARTEIRA GERADA (intra-portfolio), nao sobre sorteios passados. Frame
  honesto, defensavel legal/marca. Disclaimer obrigatorio em toda saida (ver ADR-005).

## ADR-005 - Disclaimer obrigatorio, constante unica
- **Contexto**: Risco de usuario interpretar otimizacao como previsao.
- **Decisao**: Constante unica em `disclaimer.py`; toda saida probabilistica (relatorio/export/CLI)
  injeta o texto exato definido em CLAUDE.md.
- **Consequencia**: Mensagem consistente, testavel (teste verifica presenca). Mudanca de texto
  num lugar so.

## ADR-006 - Precos configuraveis, nunca inventados
- **Contexto**: Precos oficiais mudam; inventar = informacao falsa.
- **Decisao**: `LotterySpec.price_table` = `None` placeholder. Gerar aposta real exige usuario setar.
  Funcoes de orcamento falham explicito/avisam se preco ausente.
- **Consequencia**: Sem numero falso. Custo: usuario precisa configurar antes de usar orcamento monetario.
  Orcamento por CONTAGEM de jogos funciona sem preco.

## ADR-007 - Sem acesso a rede no nucleo
- **Contexto**: Testabilidade e determinismo.
- **Decisao**: Nucleo nao busca dados (sem fetcher Caixa). Entrada de dados, quando existir, e
  arquivo (CSV/JSON) fornecido pelo usuario. Saida e export local.
- **Consequencia**: Testes deterministas e offline. Eventual ingestao de historico fica em ferramenta
  separada e opcional (e nunca alimenta selecao - ver ADR-004).

## ADR-008 - Layout src/ + pyproject + pytest
- **Contexto**: Empacotamento limpo e import isolado.
- **Decisao**: `src/lottery_engine/`, `pyproject.toml` (PEP 621), testes em `tests/` com pytest.
- **Consequencia**: Evita import acidental do cwd; instalavel via `pip install -e .`.
