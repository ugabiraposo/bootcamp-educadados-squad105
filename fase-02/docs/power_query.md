# Power Query

Esta documentação apresenta as colunas e o tipo de dado atribuído a cada uma delas na Fase 02, com o intuito de facilitar a criação de medidas e indicadores.

<!-- inserir print: ![Tratamento](./capturas/power_query.png) -->

A Fase 02 **reaproveita todas as consultas da Fase 01** e acrescenta uma nova tabela fato: `fOrcamentos`. As tabelas já documentadas na Fase 01 estão resumidas no fim deste documento, e o detalhamento completo continua em [`fase-01/docs/power_query.md`](../../fase-01/docs/power_query.md).

As tabelas são apresentadas no mesmo formato da Fase 01: a linha de cima mostra os nomes das colunas e a linha de baixo mostra os tipos de dados.

### Nome da tabela

| Coluna 1 | Coluna 2 | Coluna 3 |
| --- | --- | --- |
| Tipo de dado 1 | Tipo de dado 2 | Tipo de dado 3 |

> **informações:**
>
> conterá informações importantes sobre a tabela, como chave primária, chaves estrangeiras e pontos de atenção.

> **glossário:** antes do nome de cada tabela há uma letra `d` ou `f`:
>- `f`: sinaliza que aquela é uma tabela fato.
>- `d`: sinaliza que aquela é uma tabela dimensão.

> **observação:** a tipagem e os nomes das colunas seguem o dicionário de dados (`00_dicionario_de_dados.xlsx`) repassado pela Educadados, filtrando a coluna "A partir da" por **Fase 2**.

---

## O que mudou em relação à Fase 01

| Item | Fase 01 | Fase 02 | Motivo |
| --- | --- | --- | --- |
| Pasta de origem dos arquivos | `C:\squad105\dados\` | `C:\bootcamp-educadados-squad105\dados\` | O projeto passou a ler os arquivos da pasta `dados` do próprio repositório clonado |
| Quantidade de bases | 11 planilhas | 12 planilhas | Inclusão de `orcamentos.xlsx` |
| Nova consulta | — | `fOrcamentos` | Necessária para o funil de orçamentos |

---

## Nova tabela

### fOrcamentos

| codigo_orcamento | data | codigo_filial | codigo_cliente | codigo_profissional | codigo_usuario | codigo_midia | valor_bruto | valor_desconto | valor_liquido | status | codigo_venda |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| inteiro | data | inteiro | inteiro | inteiro | inteiro | inteiro | decimal fixo (moeda) | decimal fixo (moeda) | decimal fixo (moeda) | texto | inteiro |

> **informações:**
>
> chave primária: codigo_orcamento (110.000 linhas, todas únicas)
>
> chaves estrangeiras:
> - data [dCalendario]
> - codigo_filial [dFiliais]
> - codigo_profissional [dProfissionais]
> - codigo_venda [fVendas]
>
> **valores da coluna `status`:**
>
> | status | linhas |
> | --- | ---: |
> | Perdido | 47.817 |
> | Aprovado | 44.172 |
> | Pendente | 18.011 |
>
> **atenção:**
> - a coluna `codigo_venda` tem **65.828 valores nulos**. Isso é esperado: só os orçamentos com status `Aprovado` viram venda. Todos os 44.172 aprovados têm `codigo_venda` preenchido, e todos esses códigos existem em `fVendas`.
> - o período vai de **02/01/2024 a 30/09/2026**, o mesmo intervalo de `fVendas`, e está coberto pela `dCalendario` (01/01/2024 a 31/12/2026).
> - `codigo_cliente`, `codigo_usuario` e `codigo_midia` não têm tabela dimensão no projeto. Ficam no modelo apenas como atributos da fato.
> - todas as 76 filiais aparecem na base de orçamentos.

#### Passos aplicados

```M
let
    Source = Excel.Workbook(File.Contents("C:\bootcamp-educadados-squad105\dados\orcamentos.xlsx"), null, true),
    orcamentos_Sheet = Source{[Item="orcamentos",Kind="Sheet"]}[Data],
    #"Promoted Headers" = Table.PromoteHeaders(orcamentos_Sheet, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"codigo_orcamento", Int64.Type}, {"data", type date}, {"codigo_filial", Int64.Type},
        {"codigo_cliente", Int64.Type}, {"codigo_profissional", Int64.Type}, {"codigo_usuario", Int64.Type},
        {"codigo_midia", Int64.Type}, {"valor_bruto", Currency.Type}, {"valor_desconto", Currency.Type},
        {"valor_liquido", Currency.Type}, {"status", type text}, {"codigo_venda", Int64.Type}})
in
    #"Changed Type"
```

> **pontos a padronizar** (ver [decisões](decisoes_reaproveitamento.md)):
> - os nomes das etapas estão em inglês (`Source`, `Promoted Headers`, `Changed Type`), enquanto as demais consultas usam português (`Fonte`, `Cabeçalhos Promovidos`, `Tipo Alterado`). Para manter o padrão, basta renomear as etapas.
> - os valores estão como `Currency.Type` (decimal fixo), enquanto `fVendas` usa `type number` (decimal). Os dois funcionam, mas é melhor usar um tipo só para valores em reais em todo o modelo.

---

## Tabelas reaproveitadas da Fase 01

Nenhuma coluna ou tipo foi alterado. Apenas o caminho do arquivo de origem mudou.

| Tabela | Arquivo | Chave primária |
| --- | --- | --- |
| dCalendario | calendario.xlsx | data |
| dCidades | cidades.xlsx | codigo_cidade |
| dFiliais | filiais.xlsx | codigo_filial |
| dGrupos_servico | grupos_servico.xlsx | codigo_grupo_servico |
| dProfissionais | profissionais.xlsx | codigo_profissional |
| dServicos | servicos.xlsx | codigo_servico |
| dVendedores | vendedores.xlsx | codigo_vendedor |
| fItens_venda | itens_venda.xlsx | codigo_item_venda |
| fMetas_quantidade | metas_quantidade.xlsx | codigo_meta_quantidade |
| fMetas_valor | metas_valor.xlsx | codigo_meta_valor |
| fVendas | vendas.xlsx | codigo_venda |

> **correção em relação à documentação da Fase 01:** na `dCalendario`, a coluna `dia_util` estava sem tipo na tabela do documento. O tipo correto é **verdadeiro/falso**.

> **lembrete do enunciado:** na `dCalendario`, `mes_ano` deve ser classificada por `ano_mes` e `mes_nome` por `mes_numero`. As duas classificações já estão configuradas no modelo.
