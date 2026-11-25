# Documentação da Feature, Regras e Padronização de Nomenclatura DAX

**Projeto:** Rede Aurora Odontologia — Fase 02 (*Atingimento*)

**Período da base de orçamentos:** `02/01/2024` a `30/09/2026` (`110.000` linhas em `orcamentos.xlsx`)

**Escopo:** Consolidação integral das análises, regras de negócio, modelagem/Power Query, mapeamento da Fase 1, padronização de nomenclatura e código DAX da Fase 02

## 1. O Que Foi Feito e Consolidado

Nesta etapa, foram consolidadas em um único documento todas as definições, alterações, diagnósticos e medidas da **Fase 02**, preservando os nomes já renomeados e salvos no projeto `.pbip` e incorporando os pontos de legado, modelagem, `fOrcamentos`, regras de negócio, visuais e alerta de 2026.

- **Atingimento de metas (valor e quantidade):** medidas dinâmicas (sem trava fixa em 2026 e sem dependência prévia de `dTipoMeta`) para percentuais (`ating valor-filial`, `ating qtde-filial`), faixas (`faixa ating-valor`, `faixa ating-qtde`), contagens de metas batidas (`filiais bateram valor`, `filiais bateram qtde`) e cruzamentos (`filiais bateram valor ñ quantidade`, `filiais bateram quantidade ñ valor`).

- **Funil de orçamentos, conversão, desconto e perdas:** medidas de volume (`orçamentos gerados`, `orçamentos aprovados`, `orçamentos perdidos` e `orçamentos pendentes`), tabela desconectada `dEtapasFunil` (`Gerados`, `Aprovados`, `Perdidos`) ordenada por `ordem` com a medida seletora `etapa do funil`, conversão ponderada (`taxa de conversão`, `taxa de conversão rede`), `desconto médio`, `valor perdido` e `valor perdido % vendido`.

- **Grupos e serviços:** medidas na tabela `Medidas venda/servico` (`receita grupo/serviço`, `qtde vendida grupo/serviço`, `total itens vendidos`, `valor bruto itens`, `porcent participação receita`, `porcent participação no grupo`, `ticket médio serviço`, `valor tabela total` e `desconto/diferença tabela %`), além das medidas alternativas de participação sobre valor bruto (`% do total da rede` e `% no grupo`).

- **Alerta de metas ausentes em 2026:** medidas na tabela `Medidas metas` travadas em `2026` (`REMOVEFILTERS(dCalendario), dCalendario[ano] = 2026`) e exigindo valores `> 0` (`valor metas-filial`, `qtde metas-filial`, `resultado-meta-filial`, `status meta-filial`, `sem meta-filial`, `filiais sem meta`, `filiais sem meta-valor` e `filiais sem meta-qtde`), além das referências de apoio (`meta cadastrada 2026` e `vendas em 2026`).

- **Padronização de nomenclatura:** manutenção integral dos nomes já definidos e salvos no modelo e na documentação, evitando renomeações que quebrem visuais ou retrabalho.

## 2. Convenção de Nomenclatura Adotada

- **Preservação do que já foi salvo:** manter os nomes exatos já renomeados no Power BI e registrados nos arquivos `.md` para evitar quebras ou retrabalho desnecessário.

- **Clareza de escopo e tipo:** diferenciar no nome o contexto ou a regra (ex.: `taxa de conversão` vs. `taxa de conversão rede`; `ating valor-filial` vs. `ating qtde-filial`; `filiais bateram valor ñ quantidade` vs. `filiais bateram quantidade ñ valor`).

- **Separação entre cálculo e rótulo:** medidas de percentual/indicador retornam valores numéricos ou em branco para permitir comparações e faixas (`>= 1`, `>= 0.9`, `> 0`), enquanto medidas de faixa/status retornam textos (`"sem meta"`, `"100% ou mais"`, `"90% a 99%"`, `"abaixo de 90%"`).

## 3. Mapeamento das Medidas da Fase 1 para a Fase 2

- **Reutilizar:**

- **Medidas base:** `valor líquido`, `número de vendas`, `valor bruto`, `quantidade de itens`, `meta de valor`, `meta de quantidade`.

- **Medidas de meta:** `val vendedor`, `qtde vendedor`, `val profissional`, `qtde profissional`, `val grupos`, `qtde grupos`, `val serviços`, `qtde serviços`, `val cidade`, `qtde cidade`, `val rede`, `qtde rede`, `val filial` (conferindo o nível de filtro de `qtde filial` conforme as regras da Fase 2 antes de usá-lo nas novas faixas de quantidade).

- **Medidas especiais de destaque e rótulo:** `Destaque - Filial Líder`, `Destaque - Cidade Líder`, `Destaque - Vendedor Líder`, `Destaque - Serviço Líder`, `Destaque - Profissional Líder`, `rótulo especial` (cuidando da codificação de caracteres ao editar arquivos em texto).

- **Manter para legado (não usar diretamente nas novas faixas):**

- **Medidas percentuais:** `val vendedor %`, `qtde vendedor %`, `val profissional %`, `qtde profissional %`, `val grupos %`, `qtde grupos %`, `val serviços %`, `qtde serviços %`, `qtde cidade %`, `val cidade %`, `qtde filial %`, `val filial %`, `val rede %`, `qtde rede %` — retornam `"sem meta"` (texto) quando não há meta/denominador, o que impede comparações numéricas diretas com `90%` ou `100%`.

- **Adaptar / evoluir:**

- **Medidas de status:** `status val vendedor`, `status qtde vendedor`, `status val profissional`, `status qtde profissional` — na Fase 1 usam `SWITCH(TRUE())` com 2 cores (`#1E4D2B` e `#5C1D24`) e comparações `> 1` e `< 1` (sem faixa explícita para `100%` exato) sobre medidas que podem retornar `"sem meta"`. A estrutura `SWITCH(TRUE())` serve de base, mas a Fase 2 exige **3 faixas** (`abaixo de 90%`, `de 90% a 99%`, `100% ou mais`) e tratamento numérico separado.

## 4. Modelagem, Power Query, `fOrcamentos` e Regras de Negócio

### Diagnóstico de Modelagem e Power Query (Sem Dicionário de Dados)

- **Base e arquivos:** 12 planilhas na pasta `dados` (incluindo `orcamentos.xlsx` com `110.000` linhas de `02/01/2024` a `30/09/2026`), documentação em `fase-02/docs/` e projeto `.pbip` (`TMDL` / `PBIR` em `pt-BR`).

- **Relacionamentos e calendário:** desmarcar **Data/hora automática** (para remover tabelas ocultas `LocalDateTable`/`DateTableTemplate`), manter a ordenação correta de `mes_ano` por `ano_mes` e `mes_nome` por `mes_numero`, garantir relação ativa `fOrcamentos[data] → dCalendario[data]`, manter **inativa** `fOrcamentos → fVendas` (evitando ambiguidade) e manter **inativas** `dVendedores → dFiliais` e `dProfissionais → dFiliais` (usando `LOOKUPVALUE` quando necessário).

- **Níveis de meta:** conferir o comportamento das metas por nível (`Produto` vs. `Vendedor`, considerando que metas de nível `Vendedor` aparecem em 2026).

- **Validação manual no Power Query:** sem dicionário de dados formal, conferir diretamente no Power Query e na base os tipos de dados de `valor_bruto`, `valor_desconto`, `valor_liquido` e `codigo_venda`, bem como o comportamento do status `Pendente` em relação a `Gerados`, `Aprovados` e `Perdidos`.

### Regras de Negócio e Visuais por Bloco

- **Atingimento e faixas:** avaliar valor e quantidade separadamente (uma filial como Caxias pode atingir uma meta e não a outra), classificar em `abaixo de 90%`, `de 90% a 99%` e `100% ou mais`, e contar filiais por faixa/condição respeitando ano, mês e filial.

- **Funil, conversão, desconto e perdas:** exibir funil (`Gerados`, `Aprovados`, `Perdidos`) com taxa de conversão no rótulo, calcular `taxa de conversão` (filial), `taxa de conversão rede` (linha de referência removendo filtros de filial/cidade e mantendo ano/mês) e `desconto médio` de forma **ponderada** (nunca média simples de percentuais), apurar `valor perdido` em registros `Perdido` e cruzar com atingimento/conversão.

- **Grupos de serviço e serviços:** estruturar a matriz hierárquica `Grupo de Serviço > Serviço` a partir das tabelas de vendas e serviços (`vendas.xlsx`, `itens_venda.xlsx`, `servicos.xlsx`, `grupos_servico.xlsx`), exibindo valor (com barras de dados), `% do total da rede` e `% no grupo` fechando `100%` dentro de cada grupo.

- **Página de alerta (sem meta em 2026):** exibir em página dedicada de alerta (tipo tela de erro) as filiais sem meta cadastrada para 2026, com identificação da filial, situação retornando `"sem meta"` e vendas no ano.

## 5. Código DAX Consolidado por Bloco

### A. Atingimento de Metas (`Medidas metas`)

```dax
ating valor-filial =
DIVIDE([valor líquido], [val filial])
```

```dax
ating qtde-filial =
DIVIDE([número de vendas], [qtde filial])
```

```dax
faixa ating-valor =
VAR vPct = [ating valor-filial]
RETURN
    SWITCH(
        TRUE(),
        ISBLANK(vPct), "sem meta",
        vPct >= 1,     "100% ou mais",
        vPct >= 0.9,   "90% a 99%",
        "abaixo de 90%"
    )
```

```dax
faixa ating-qtde =
VAR vPct = [ating qtde-filial]
RETURN
    SWITCH(
        TRUE(),
        ISBLANK(vPct), "sem meta",
        vPct >= 1,     "100% ou mais",
        vPct >= 0.9,   "90% a 99%",
        "abaixo de 90%"
    )
```

```dax
filiais bateram valor =
COUNTROWS(
    FILTER(
        VALUES(dFiliais[codigo_filial]),
        [ating valor-filial] >= 1
    )
) + 0
```

```dax
filiais bateram qtde =
COUNTROWS(
    FILTER(
        VALUES(dFiliais[codigo_filial]),
        [ating qtde-filial] >= 1
    )
) + 0
```

```dax
filiais bateram valor ñ quantidade =
COUNTROWS(
    FILTER(
        VALUES(dFiliais[codigo_filial]),
        [ating valor-filial] >= 1
            && NOT ISBLANK([ating qtde-filial])
            && [ating qtde-filial] < 1
    )
) + 0
```

```dax
filiais bateram quantidade ñ valor =
COUNTROWS(
    FILTER(
        VALUES(dFiliais[codigo_filial]),
        [ating qtde-filial] >= 1
            && NOT ISBLANK([ating valor-filial])
            && [ating valor-filial] < 1
    )
) + 0
```

### B. Funil de Orçamentos, Conversão, Desconto e Perdas

```dax
orçamentos gerados =
COUNTROWS(fOrcamentos)
```

```dax
orçamentos aprovados =
CALCULATE(
    [orçamentos gerados],
    fOrcamentos[status] = "Aprovado"
)
```

```dax
orçamentos perdidos =
CALCULATE(
    [orçamentos gerados],
    fOrcamentos[status] = "Perdido"
)
```

```dax
orçamentos pendentes =
CALCULATE(
    [orçamentos gerados],
    fOrcamentos[status] = "Pendente"
)
```

```dax
etapa do funil =
SWITCH(
    SELECTEDVALUE(dEtapasFunil[etapa]),
    "Gerados",   [orçamentos gerados],
    "Aprovados", [orçamentos aprovados],
    "Perdidos",  [orçamentos perdidos]
)
```

```dax
taxa de conversão =
DIVIDE(
    [orçamentos aprovados],
    [orçamentos gerados]
)
```

```dax
taxa de conversão rede =
CALCULATE(
    [taxa de conversão],
    REMOVEFILTERS(dFiliais),
    REMOVEFILTERS(dCidades)
)
```

```dax
desconto médio =
DIVIDE(
    SUM(fOrcamentos[valor_desconto]),
    SUM(fOrcamentos[valor_bruto])
)
```

```dax
valor perdido =
CALCULATE(
    SUM(fOrcamentos[valor_liquido]),
    fOrcamentos[status] = "Perdido"
)
```

```dax
valor perdido % vendido =
DIVIDE(
    [valor perdido],
    [valor líquido]
)
```

### C. Grupos e Serviços (`Medidas venda/servico` e Referências de Percentual)

```dax
receita grupo/serviço =
[valor líquido]
```

```dax
qtde vendida grupo/serviço =
[número de vendas]
```

```dax
total itens vendidos =
SUM(fItens_venda[quantidade])
```

```dax
valor bruto itens =
SUM(fItens_venda[valor_total])
```

```dax
porcent participação receita =
DIVIDE(
    [valor líquido],
    CALCULATE(
        [valor líquido],
        ALLSELECTED(dServicos),
        ALLSELECTED(dGrupos_servico)
    )
)
```

```dax
porcent participação no grupo =
DIVIDE(
    [valor líquido],
    CALCULATE(
        [valor líquido],
        ALLEXCEPT(dServicos, dGrupos_servico[grupo_servico])
    )
)
```

```dax
ticket médio serviço =
DIVIDE(
    [valor líquido],
    [número de vendas]
)
```

```dax
valor tabela total =
SUMX(
    fItens_venda,
    fItens_venda[quantidade] * RELATED(dServicos[valor tabela])
)
```

```dax
desconto/diferença tabela % =
DIVIDE(
    [valor tabela total] - [valor bruto itens],
    [valor tabela total]
)
```

```dax
% do total da rede =
DIVIDE(
    [valor bruto],
    CALCULATE([valor bruto], REMOVEFILTERS(dGrupos_servico), REMOVEFILTERS(dServicos))
)
```

```dax
% no grupo =
DIVIDE(
    [valor bruto],
    CALCULATE([valor bruto], REMOVEFILTERS(dServicos))
)
```

### D. Alerta de Metas Ausentes em 2026 (`Medidas metas` e Referências)

```dax
valor metas-filial =
CALCULATE(
    SUM(fMetas_valor[meta_valor]),
    REMOVEFILTERS(dCalendario),
    dCalendario[ano] = 2026
)
```

```dax
qtde metas-filial =
CALCULATE(
    SUM(fMetas_quantidade[meta_quantidade]),
    REMOVEFILTERS(dCalendario),
    dCalendario[ano] = 2026
)
```

```dax
resultado-meta-filial =
VAR vlr = COALESCE([valor metas-filial], 0)
VAR vQtd = COALESCE([qtde metas-filial], 0)
RETURN
    IF(vlr > 0 || vQtd > 0, 1, 0)
```

```dax
status meta-filial =
VAR temValor = COALESCE([valor metas-filial], 0) > 0
VAR temQtde = COALESCE([qtde metas-filial], 0) > 0
RETURN
    SWITCH(
        TRUE(),
        NOT temValor && NOT temQtde, "sem meta",
        NOT temValor && temQtde, "Sem meta de Valor",
        temValor && NOT temQtde, "Sem meta de Quantidade",
        "Com meta definida"
    )
```

```dax
sem meta-filial =
IF(
    [resultado-meta-filial] = 0,
    "sem meta",
    "Com meta"
)
```

```dax
filiais sem meta =
COUNTROWS(
    FILTER(
        VALUES(dFiliais[codigo_filial]),
        [resultado-meta-filial] = 0
    )
) + 0
```

```dax
filiais sem meta-valor =
COUNTROWS(
    FILTER(
        VALUES(dFiliais[codigo_filial]),
        COALESCE([valor metas-filial], 0) <= 0
    )
) + 0
```

```dax
filiais sem meta-qtde =
COUNTROWS(
    FILTER(
        VALUES(dFiliais[codigo_filial]),
        COALESCE([qtde metas-filial], 0) <= 0
    )
) + 0
```

```dax
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

```dax
vendas em 2026 =
CALCULATE([valor líquido], REMOVEFILTERS(dCalendario), dCalendario[ano] = 2026)
```