# Modelagem

Esta documentação apresenta os relacionamentos entre as tabelas na Fase 02, com suas particularidades, e os ajustes feitos em relação ao modelo da Fase 01.

<!-- inserir print: ![Modelagem](./capturas/modelagem.png) -->

A Fase 02 **mantém os 22 relacionamentos da Fase 01** (esquema estrela) e acrescenta os relacionamentos da nova tabela `fOrcamentos`. O detalhamento original continua em [`fase-01/docs/modelagem.md`](../../fase-01/docs/modelagem.md).

As relações são apresentadas da seguinte forma:

| Tabela (Estrangeira) | Coluna (Estrangeira) | Cardinalidade | Tabela (Primária) | Coluna (Primária) | Status |
| --- | --- | --- | --- | --- | --- |
| Tabela A | Coluna 1 | N --- 1 | Tabela B | Coluna 2 | Ativo |

---

### Relacionamentos novos (fOrcamentos)

| Tabela (Estrangeira) | Coluna (Estrangeira) | Cardinalidade | Tabela (Primária) | Coluna (Primária) | Status | Situação no projeto |
| --- | --- | --- | --- | --- | --- | --- |
| fOrcamentos | data | N --- 1 | dCalendario | data | Ativo | ⚠️ **a criar** |
| fOrcamentos | codigo_filial | N --- 1 | dFiliais | codigo_filial | Ativo | ✅ criado (detecção automática) |
| fOrcamentos | codigo_profissional | N --- 1 | dProfissionais | codigo_profissional | Ativo | ✅ criado (detecção automática) |
| fOrcamentos | codigo_venda | N --- 1 | fVendas | codigo_venda | Inativo | ✅ criado (detecção automática) |

> **atenção: `fOrcamentos[data]` ainda não está ligada à `dCalendario`.**
>
> Hoje a coluna `data` está ligada a uma tabela oculta `LocalDateTable_d93c9f9e...`, criada pela opção *Data/hora automática* do Power BI. Sem a ligação com a `dCalendario`, **as segmentações de ano e mês não filtram o funil de orçamentos**, e as perguntas de aprovação 2, 3 e 4 sairiam erradas.
>
> **Como corrigir:**
> 1. *Arquivo → Opções e configurações → Opções → Arquivo atual → Carregamento de dados* → desmarcar **Data/hora automática**. Isso remove as 4 tabelas `LocalDateTable`/`DateTableTemplate` do modelo.
> 2. No modo **Modelo**, arrastar `fOrcamentos[data]` até `dCalendario[data]` (muitos para um, filtro em direção única, ativo).

> **por que `fOrcamentos → fVendas` fica inativo:** a ligação entre as duas fatos não é necessária para nenhum visual da fase, porque o funil usa apenas `fOrcamentos`. Se ela ficasse ativa, abriria um segundo caminho de filtro entre `dFiliais`/`dCalendario` e `fVendas` (direto e via `fOrcamentos`), gerando ambiguidade. Quando for preciso cruzar orçamento e venda, use `USERELATIONSHIP()`.

> **sem ambiguidade com profissionais:** `fOrcamentos` liga direto em `dFiliais` e em `dProfissionais`. Como a relação `dProfissionais → dFiliais` continua inativa (decisão da Fase 01), não existe caminho duplo.

---

### Relacionamentos mantidos da Fase 01

| Tabela (Estrangeira) | Coluna (Estrangeira) | Cardinalidade | Tabela (Primária) | Coluna (Primária) | Status |
| --- | --- | --- | --- | --- | --- |
| dFiliais | codigo_cidade | N --- 1 | dCidades | codigo_cidade | Ativo |
| dProfissionais | codigo_filial | N --- 1 | dFiliais | codigo_filial | Inativo |
| dServicos | codigo_grupo_servico | N --- 1 | dGrupos_servico | codigo_grupo_servico | Ativo |
| dVendedores | codigo_filial | N --- 1 | dFiliais | codigo_filial | Inativo |
| fItens_venda | codigo_servico | N --- 1 | dServicos | codigo_servico | Ativo |
| fItens_venda | codigo_venda | N --- 1 | fVendas | codigo_venda | Ativo |
| fMetas_quantidade | codigo_filial | N --- 1 | dFiliais | codigo_filial | Ativo |
| fMetas_quantidade | codigo_grupo_servico | N --- 1 | dGrupos_servico | codigo_grupo_servico | Inativo |
| fMetas_quantidade | codigo_profissional | N --- 1 | dProfissionais | codigo_profissional | Ativo |
| fMetas_quantidade | codigo_servico | N --- 1 | dServicos | codigo_servico | Inativo |
| fMetas_quantidade | codigo_vendedor | N --- 1 | dVendedores | codigo_vendedor | Ativo |
| fMetas_quantidade | mes | N --- 1 | dCalendario | data | Ativo |
| fMetas_valor | codigo_filial | N --- 1 | dFiliais | codigo_filial | Ativo |
| fMetas_valor | codigo_grupo_servico | N --- 1 | dGrupos_servico | codigo_grupo_servico | Inativo |
| fMetas_valor | codigo_profissional | N --- 1 | dProfissionais | codigo_profissional | Ativo |
| fMetas_valor | codigo_servico | N --- 1 | dServicos | codigo_servico | Inativo |
| fMetas_valor | codigo_vendedor | N --- 1 | dVendedores | codigo_vendedor | Ativo |
| fMetas_valor | mes | N --- 1 | dCalendario | data | Ativo |
| fVendas | codigo_filial | N --- 1 | dFiliais | codigo_filial | Ativo |
| fVendas | codigo_profissional | N --- 1 | dProfissionais | codigo_profissional | Ativo |
| fVendas | codigo_vendedor | N --- 1 | dVendedores | codigo_vendedor | Ativo |
| fVendas | data | N --- 1 | dCalendario | data | Ativo |

> **correção em relação à documentação da Fase 01:** o documento da Fase 01 escreve `codigo_grupos_servico` (com "s"). O nome real da coluna é `codigo_grupo_servico`, e assim está corrigido acima.

---

### Tabelas auxiliares (sem relacionamento)

Para atender aos desafios de DAX, o modelo recebe tabelas desconectadas, que não se relacionam com nenhuma outra. Elas servem apenas para alimentar visuais e medidas.

| Tabela | Conteúdo | Uso |
| --- | --- | --- |
| `dTipoMeta` | `Valor`, `Quantidade` | Permite que **uma única medida de faixa** sirva para valor e para quantidade (ver [medidas](medidas.md#faixa-de-atingimento)) |
| `dFaixas` | `100% ou mais`, `90% a 99%`, `abaixo de 90%`, com uma coluna de ordem | Eixo e legenda dos visuais por faixa, sempre na mesma ordem |
| `dEtapasFunil` | `Gerados`, `Aprovados`, `Perdidos`, com uma coluna de ordem | Categoria do gráfico de funil (ver [medidas](medidas.md#etapa-do-funil)) |
| `Medidas orçamentos` | — | Tabela de medidas para o funil, no mesmo padrão das tabelas de medidas da Fase 01 |
| `Medidas atingimento` | — | Tabela de medidas para faixas, contagens e alerta "sem meta" |

As duas tabelas de apoio podem ser criadas em *Página Inicial → Inserir dados*:

```
dTipoMeta                    dFaixas
| tipo       |               | faixa          | ordem |
|------------|               |----------------|-------|
| Valor      |               | 100% ou mais   | 1     |
| Quantidade |               | 90% a 99%      | 2     |
                             | abaixo de 90%  | 3     |
```

> classificar `dFaixas[faixa]` e `dEtapasFunil[etapa]` pelas respectivas colunas `ordem`.

---

#### Relações inativas

A lógica da Fase 01 continua valendo: relações inativas priorizam caminhos diretos e evitam caminhos alternativos concorrentes. Na Fase 02 entra mais uma relação inativa (`fOrcamentos → fVendas`), pelo mesmo motivo.

```DAX
CALCULATE(
    [Medida],
    USERELATIONSHIP(Tabela1[Coluna], Tabela2[Coluna])
)
```

---

### Testes e validações

<!-- inserir print: ![Validações](./capturas/testes_modelagem.png) -->

| Teste | Como verificar | Resultado esperado |
| --- | --- | --- |
| Chave primária de `fOrcamentos` é única | Contar linhas e `codigo_orcamento` distintos | 110.000 = 110.000 |
| Todo `codigo_filial` de orçamentos existe em `dFiliais` | Tabela com `dFiliais[filial]` e contagem de orçamentos; não pode haver linha em branco | 76 filiais, sem linha em branco |
| Segmentação de ano/mês filtra o funil | Escolher set/2026 na segmentação e conferir se a contagem de orçamentos muda | Muda (depois de criar a relação com `dCalendario`) |
| Tabelas de data automática removidas | Conferir no modo Modelo | Nenhuma `LocalDateTable` |
