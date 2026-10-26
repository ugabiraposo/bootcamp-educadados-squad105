## Notas de modelagem

### Vendas/itens sem meta cadastrada
- O **valor realizado é mantido e exibido normalmente** (não é excluído, não é zerado).
- O **percentual de atingimento retorna BLANK** via `DIVIDE([Total Vendas], [Total Meta])`.
  Motivo: `BLANK` sinaliza "não há meta para comparar"; `0%` sugeriria meta zero não batida.
- **Não substituir meta `BLANK` por `0`** no Power Query nem no DAX — distorce médias e quebra o atingimento.
- Onde precisar de rótulo explícito no visual, usar `Status da Meta` (retorna "Sem meta cadastrada").

### Relacionamentos inativos (`USERELATIONSHIP`)
- O modelo segue o dicionário de dados e **possui relacionamentos inativos intencionais**.
- O Power BI permite **apenas um relacionamento ativo por par de tabelas**; os demais ficam inativos por design.
- **Não ativar relacionamentos inativos no modelo** — isso quebra as medidas que já usam `USERELATIONSHIP`.
- Medidas que precisam filtrar por um relacionamento inativo usam `USERELATIONSHIP` dentro de `CALCULATE`.

Ex: `CALCULATE([___], USERELATIONSHIP(tabela[___], tabela[___]))`

### Critério de relacionamentos:
- **Ativo:** fato→dimensão direto, ou dimensão→dimensão que seja o ÚNICO caminho até aquela dimensão.
- **Inativo:** dimensão→dimensão que duplica um caminho já existente pelo fato (floco de neve).
- **Caso de julgamento:** metas→servicos e metas→grupos_servico não podem ser ambas ativas. Deixadas inativas para decidir por `USERELATIONSHIP` na fase de indicadores.s