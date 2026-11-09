# Comparação: dados × painel × testes.md

Execução: 09/11/2026 19:11

| Caso | Campo | Calculado (dados) | Painel | testes.md | Situação |
|:--|:--|--:|--:|--:|:--|
| CT-01 | valor_liquido | 234.999.311,61 | — | 234999312 | 🔸 Confere com testes.md (painel não coletado) |
| CT-02 | — | erro no cálculo: Nenhuma meta com nivel='filial'. Valores existentes: ['Produto', 'Profissional', 'Serviço', 'Vendedor']. Ajuste NIVEL_META. | — | — | ❌ Corrigir cálculo |
| CT-03 | cidade | Brasília | — | Brasilia | 🔸 Confere com testes.md (painel não coletado) |
| CT-03 | qtd_vendas | 2629 | — | 2629 | 🔸 Confere com testes.md (painel não coletado) |
| CT-03 | valor_liquido | 13.298.929,19 | — | — | 🔸 Sem valor informado: preencher |
| CT-04 | vendedor | Juan Sampaio | — | Ana Laura da Rocha | ⚠️ testes.md diverge dos dados: conferir no painel |
| CT-04 | meta | 285.752,73 | — | — | 🔸 Sem valor informado: preencher |
| CT-04 | realizado | 167.821,01 | — | — | 🔸 Sem valor informado: preencher |
| CT-04 | atingimento_pct | 58,73 | — | — | 🔸 Sem valor informado: preencher |
| CT-05 | grupo | Protocolo | — | Protocolo | 🔸 Confere com testes.md (painel não coletado) |
| CT-05 | valor_bruto | 71.304.400,00 | — | — | 🔸 Sem valor informado: preencher |
| CT-05 | participacao_pct | 27,82 | — | 27,81 | 🔸 Confere com testes.md (painel não coletado) |