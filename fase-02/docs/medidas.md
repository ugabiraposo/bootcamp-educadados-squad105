# Medidas

Esta documentação apresenta as medidas DAX da Fase 02 e seus comportamentos. Cada medida é apresentada da mesma forma que na Fase 01:

- o que ela busca obter
- código em DAX
- seu comportamento

<!-- inserir print: ![medidas DAX](./capturas/medidas_DAX.png) -->

> **status:** as medidas novas abaixo são a **proposta da squad** para os desafios de DAX da Fase 02. Conforme forem criadas no Power BI, marque o status em cada uma e atualize o código caso algo mude durante a implementação.

## Organização

As medidas da Fase 01 continuam no projeto, sem alteração de código, nas mesmas quatro tabelas: **Medidas base**, **Medidas metas**, **Medidas percentuais** e **Medidas especiais**. A documentação delas continua em [`fase-01/docs/medidas.md`](../../fase-01/docs/medidas.md).

A Fase 02 acrescenta duas tabelas de medidas:

**Medidas atingimento:** atingimento numérico, faixa de atingimento, cor da faixa, contagem de filiais por faixa e alerta "sem meta".

**Medidas orçamentos:** orçamentos gerados, aprovados, perdidos e pendentes, taxa de conversão (da filial e da rede), desconto médio, valor perdido e valores do funil.

E duas medidas novas na tabela **Medidas percentuais**, para a matriz grupo › serviço.

---

## Medidas atingimento

### ating valor filial

Calcula o percentual de atingimento da meta de valor da filial, como **número**.

```DAX
ating valor filial = DIVIDE([valor líquido], [val filial])
```

### ating qtde filial

Calcula o percentual de atingimento da meta de quantidade da filial, como **número**.

```DAX
ating qtde filial = DIVIDE([número de vendas], [qtde filial])
```

**Por que medidas novas, se já existem `val filial %` e `qtde filial %`?** As medidas da Fase 01 devolvem o **texto** "sem meta" quando não há meta (`DIVIDE(..., ..., "sem meta")`). Uma medida que pode devolver número ou texto não pode ser comparada com `>= 0.9` nem somada, e isso quebra as faixas e as contagens. As versões novas devolvem **em branco** quando não há meta, e o texto "sem meta" passa a ser tratado só na faixa. As medidas da Fase 01 continuam no modelo para não quebrar os visuais herdados.

> **atenção (pendente de validação):** na Fase 01, `val filial` usa as metas de nível `Produto`, mas `qtde filial` usa as de nível `Vendedor`. As metas de nível `Vendedor` só existem para **2026**, então em 2024 e 2025 a meta de quantidade da filial fica em branco. Ver a decisão D-06 em [decisões](decisoes_reaproveitamento.md).

### atingimento

Escolhe o atingimento de valor ou de quantidade conforme o tipo de meta que está no contexto. É a base para reaproveitar a mesma faixa nos dois casos.

```DAX
atingimento =
SWITCH(
    SELECTEDVALUE(dTipoMeta[tipo]),
    "Valor", [ating valor filial],
    "Quantidade", [ating qtde filial]
)
```

### faixa de atingimento

**Desafio de DAX 1.** Classifica o atingimento em faixas usando `SWITCH(TRUE())`. A mesma medida serve para valor e para quantidade.

```DAX
faixa de atingimento =
VAR p = [atingimento]
RETURN
    SWITCH(
        TRUE(),
        ISBLANK(p), "sem meta",
        p >= 1,     "100% ou mais",
        p >= 0.9,   "90% a 99%",
        "abaixo de 90%"
    )
```

**Comportamento:** a ordem das condições importa, porque o `SWITCH(TRUE())` para na primeira condição verdadeira. Por isso o teste de 100% vem antes do de 90%. Um atingimento de 99,6% cai em "90% a 99%", porque ainda não bateu a meta.

### faixa valor / faixa qtde

Atalhos que fixam o tipo de meta. Assim a matriz pode mostrar as duas faixas lado a lado sem precisar colocar `dTipoMeta` no visual.

```DAX
faixa valor =
CALCULATE([faixa de atingimento], TREATAS({"Valor"}, dTipoMeta[tipo]))

faixa qtde =
CALCULATE([faixa de atingimento], TREATAS({"Quantidade"}, dTipoMeta[tipo]))
```

### cor faixa valor / cor faixa qtde

Devolvem a cor da faixa, para usar em **formatação condicional → valor do campo** (fundo ou fonte) na matriz de atingimento.

```DAX
cor faixa valor =
SWITCH(
    [faixa valor],
    "100% ou mais",  "#1E4D2B",
    "90% a 99%",     "#B7791F",
    "abaixo de 90%", "#5C1D24"
)
```

> `cor faixa qtde` é igual, trocando `[faixa valor]` por `[faixa qtde]`. As cores verde e vinho são as mesmas dos status da Fase 01; o amarelo é novo, para a faixa intermediária.

### filiais na faixa

**Desafio de DAX 2.** Conta quantas filiais estão em cada faixa, respeitando as segmentações de ano, mês e filial.

```DAX
filiais na faixa =
VAR faixaSelecionada = SELECTEDVALUE(dFaixas[faixa])
RETURN
    COUNTROWS(
        FILTER(
            VALUES(dFiliais[codigo_filial]),
            [faixa de atingimento] = faixaSelecionada
        )
    ) + 0
```

**Comportamento:** `VALUES(dFiliais[codigo_filial])` só traz as filiais que sobraram depois das segmentações. Para cada uma, a medida de faixa é recalculada (transição de contexto) com o ano e o mês selecionados. O `+ 0` faz o cartão mostrar 0 em vez de "(Em branco)".

Medidas para os cartões:

```DAX
filiais 100% valor =
CALCULATE([filiais na faixa],
    TREATAS({"100% ou mais"}, dFaixas[faixa]),
    TREATAS({"Valor"}, dTipoMeta[tipo]))

filiais 90 a 99% valor =
CALCULATE([filiais na faixa],
    TREATAS({"90% a 99%"}, dFaixas[faixa]),
    TREATAS({"Valor"}, dTipoMeta[tipo]))

filiais abaixo 90% valor =
CALCULATE([filiais na faixa],
    TREATAS({"abaixo de 90%"}, dFaixas[faixa]),
    TREATAS({"Valor"}, dTipoMeta[tipo]))
```

> as três versões de quantidade seguem o mesmo padrão, trocando `"Valor"` por `"Quantidade"`.

### filiais bateram valor e não quantidade

Deixa explícito o caso pedido no enunciado (pergunta de aprovação 1).

```DAX
filiais bateram valor e não quantidade =
COUNTROWS(
    FILTER(
        VALUES(dFiliais[codigo_filial]),
        [ating valor filial] >= 1
            && NOT ISBLANK([ating qtde filial])
            && [ating qtde filial] < 1
    )
) + 0
```

**Importante:** no DAX, um valor em branco é tratado como 0 em comparações, então `BLANK() < 1` é verdadeiro. Sem o `NOT ISBLANK`, uma filial sem meta de quantidade seria contada como "não bateu".

### meta cadastrada 2026

**Desafio de DAX 5.** Identifica quem não tem meta cadastrada para 2026 e devolve "sem meta". Funciona para filial, vendedor e profissional, porque as tabelas de metas se relacionam com as três dimensões.

```DAX
meta cadastrada 2026 =
VAR metasValor =
    CALCULATE(COUNTROWS(fMetas_valor),
        REMOVEFILTERS(dCalendario), dCalendario[ano] = 2026)
VAR metasQtde =
    CALCULATE(COUNTROWS(fMetas_quantidade),
        REMOVEFILTERS(dCalendario), dCalendario[ano] = 2026)
RETURN
    IF(metasValor + metasQtde = 0, "sem meta", "com meta")
```

**Comportamento:** `REMOVEFILTERS(dCalendario)` faz a página de alerta ignorar as segmentações de ano e mês, já que a regra é sempre "meta para 2026". No visual, filtre a medida por "sem meta".

### vendas em 2026

Valor líquido vendido no ano, para a coluna "vendas no ano" da página de alerta.

```DAX
vendas em 2026 =
CALCULATE([valor líquido], REMOVEFILTERS(dCalendario), dCalendario[ano] = 2026)
```

### filial do cadastro

Mostra a filial de vendedores e profissionais na página de alerta. É preciso usar `LOOKUPVALUE` porque as relações `dVendedores → dFiliais` e `dProfissionais → dFiliais` são inativas (decisão da Fase 01).

```DAX
filial do vendedor =
LOOKUPVALUE(dFiliais[filial], dFiliais[codigo_filial], SELECTEDVALUE(dVendedores[codigo_filial]))

filial do profissional =
LOOKUPVALUE(dFiliais[filial], dFiliais[codigo_filial], SELECTEDVALUE(dProfissionais[codigo_filial]))
```

**Resultado esperado** (conferido direto nas planilhas):

| Quem | Sem meta em 2026 | Observação |
| --- | ---: | --- |
| Filiais | 3 | Brasília Asa Norte, Sobradinho Centro e Uberlândia Centro, todas encerradas em 2025 |
| Vendedores | 10 | Todos inativos, nenhum com venda em 2026 |
| Profissionais | 58 | Todos inativos, mas **39 têm vendas em 2026**. É exatamente o caso que o Dr. Henrique não quer ver "sumindo" do ranking |

---

## Medidas orçamentos

### orçamentos gerados

```DAX
orçamentos gerados = COUNTROWS(fOrcamentos)
```

### orçamentos aprovados / perdidos / pendentes

```DAX
orçamentos aprovados =
CALCULATE([orçamentos gerados], fOrcamentos[status] = "Aprovado")

orçamentos perdidos =
CALCULATE([orçamentos gerados], fOrcamentos[status] = "Perdido")

orçamentos pendentes =
CALCULATE([orçamentos gerados], fOrcamentos[status] = "Pendente")
```

### taxa de conversão

**Desafio de DAX 4.** Divide o **total** de aprovados pelo **total** de gerados. Não é a média das taxas de cada filial.

```DAX
taxa de conversão = DIVIDE([orçamentos aprovados], [orçamentos gerados])
```

**Comportamento:** a regra do enunciado é "aprovados ÷ orçamentos criados no mês, pela data do orçamento". Por isso a relação `fOrcamentos[data] → dCalendario[data]` precisa estar criada (ver [modelagem](modelagem.md)).

### taxa de conversão rede

Linha de referência do gráfico de conversão por filial: aprovados ÷ gerados de **todas as filiais juntas**, respeitando ano e mês.

```DAX
taxa de conversão rede =
CALCULATE(
    [taxa de conversão],
    REMOVEFILTERS(dFiliais),
    REMOVEFILTERS(dCidades)
)
```

**Importante:** `dCidades` também precisa sair do filtro, porque um filtro de cidade chega em `dFiliais` pelo relacionamento e continuaria restringindo as filiais.

### desconto médio

**Desafio de DAX 4.** Desconto médio **ponderado pelo valor**: soma dos descontos ÷ soma do valor bruto. Um orçamento de R$ 10.000 pesa mais que um de R$ 500.

```DAX
desconto médio =
DIVIDE(SUM(fOrcamentos[valor_desconto]), SUM(fOrcamentos[valor_bruto]))
```

> **decisão:** considera todos os orçamentos gerados, porque o desconto é concedido no momento do orçamento. Se a squad preferir medir só o desconto que virou venda, basta envolver a medida em `CALCULATE(..., fOrcamentos[status] = "Aprovado")`.

### valor perdido

Valor líquido dos orçamentos com status "Perdido" (pergunta de aprovação 3).

```DAX
valor perdido =
CALCULATE(SUM(fOrcamentos[valor_liquido]), fOrcamentos[status] = "Perdido")
```

### valor perdido % vendido

Quanto o valor perdido representa do valor líquido vendido no mesmo período.

```DAX
valor perdido % vendido = DIVIDE([valor perdido], [valor líquido])
```

### etapa do funil

O visual de funil precisa de uma categoria com as etapas. Como "Gerados" não é um status (é a soma de todos), usa-se uma tabela desconectada `dEtapasFunil` (`Gerados`, `Aprovados`, `Perdidos`, com coluna de ordem).

```DAX
etapa do funil =
SWITCH(
    SELECTEDVALUE(dEtapasFunil[etapa]),
    "Gerados",   [orçamentos gerados],
    "Aprovados", [orçamentos aprovados],
    "Perdidos",  [orçamentos perdidos]
)
```

> no funil, ative o rótulo **"Percentual da primeira"**: na etapa "Aprovados", esse percentual é exatamente a taxa de conversão.

---

## Medidas percentuais (novas)

### % do total da rede

**Desafio de DAX 3.** Participação do grupo ou serviço no valor bruto total.

```DAX
% do total da rede =
DIVIDE(
    [valor bruto],
    CALCULATE([valor bruto], REMOVEFILTERS(dGrupos_servico), REMOVEFILTERS(dServicos))
)
```

### % no grupo

**Desafio de DAX 3.** Participação do serviço dentro do próprio grupo. Os serviços de cada grupo somam 100%.

```DAX
% no grupo =
DIVIDE(
    [valor bruto],
    CALCULATE([valor bruto], REMOVEFILTERS(dServicos))
)
```

**Comportamento:** `REMOVEFILTERS(dServicos)` tira só o filtro do serviço da linha. O filtro do grupo continua valendo, porque está em `dGrupos_servico` e chega em `fItens_venda` pelo relacionamento. Na linha do grupo, o resultado é 100%.

**Importante:**
- na matriz, o primeiro nível deve ser `dGrupos_servico[grupo_servico]` e o segundo `dServicos[servico]`. Se o grupo vier de `dServicos[codigo_grupo_servico]`, o `REMOVEFILTERS(dServicos)` também apagaria o grupo e a medida passaria a dar o mesmo resultado que `% do total da rede`.
- as duas medidas respeitam as segmentações de ano, mês e filial, porque só removem filtros de grupo e serviço. A pergunta de aprovação 5 pede o valor bruto dos itens (`valor_total`), que é o que `[valor bruto]` soma.

---

## Testes e Validações

Os testes da Fase 02 seguem o padrão do [`testes.md`](../../fase-01/docs/testes.md) da Fase 01, usando como casos as cinco perguntas de aprovação do enunciado (set/2026):

| ID | Pergunta | Medidas envolvidas |
| --- | --- | --- |
| CT-01 | Filiais que bateram 100% da meta de valor e quantas bateram valor e não quantidade | `filiais 100% valor`, `filiais bateram valor e não quantidade` |
| CT-02 | Filial com maior taxa de conversão e se bateu a meta de valor | `taxa de conversão`, `faixa valor` |
| CT-03 | Valor perdido da rede e % do valor vendido | `valor perdido`, `valor perdido % vendido` |
| CT-04 | Filiais que bateram a meta de valor com conversão abaixo da média da rede | `ating valor filial`, `taxa de conversão`, `taxa de conversão rede` |
| CT-05 | Participação do grupo Alinhador e serviço líder dentro dele | `% do total da rede`, `% no grupo` |
| CT-06 | Página de alerta lista 3 filiais, 10 vendedores e 58 profissionais | `meta cadastrada 2026` |
