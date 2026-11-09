import pytest

from calculos import CALCULOS, carregar_valores, comparar

VALORES = carregar_valores()
CASOS = [(ct, fonte) for ct in CALCULOS for fonte in ("painel", "documentado")]


# ---------- CT-01 a CT-05: dados × painel e dados × testes.md ----------
@pytest.mark.parametrize("ct, fonte", CASOS, ids=[f"{ct}-{f}" for ct, f in CASOS])
def test_valores(bases, ct, fonte):
    informado = VALORES.get(ct, {}).get(fonte) or {}
    if all(v is None for v in informado.values()):
        pytest.skip(f"{ct}: valores do {fonte} ainda não preenchidos")
    calculado = CALCULOS[ct](bases)
    erros = comparar(calculado, informado)
    assert not erros, f"{ct} ({fonte}) divergente:\n" + "\n".join(erros)


# ---------- CT-06: inspeção de erros na carga ----------
@pytest.mark.parametrize("tabela, coluna", [
    ("vendas", "codigo_venda"), ("vendas", "codigo_filial"), ("vendas", "codigo_vendedor"),
    ("vendas", "codigo_profissional"), ("vendas", "data"), ("vendas", "valor_liquido"),
    ("itens_venda", "codigo_venda"), ("itens_venda", "codigo_servico"),
])
def test_CT06_sem_nulos(bases, tabela, coluna):
    nulos = bases[tabela][coluna].isna().sum()
    assert nulos == 0, f"{tabela}.{coluna} tem {nulos} nulos"


@pytest.mark.parametrize("fato, coluna, dimensao", [
    ("vendas", "codigo_filial", "filiais"),
    ("vendas", "codigo_vendedor", "vendedores"),
    ("vendas", "codigo_profissional", "profissionais"),
    ("itens_venda", "codigo_venda", "vendas"),
    ("itens_venda", "codigo_servico", "servicos"),
    ("filiais", "codigo_cidade", "cidades"),
    ("servicos", "codigo_grupo_servico", "grupos_servico"),
    ("metas_valor", "codigo_filial", "filiais"),
    ("metas_valor", "codigo_vendedor", "vendedores"),
])
def test_CT06_relacionamentos(bases, fato, coluna, dimensao):
    orfaos = set(bases[fato][coluna].dropna()) - set(bases[dimensao][coluna].dropna())
    assert not orfaos, f"{fato}.{coluna} sem correspondência em {dimensao}: {sorted(orfaos)[:10]}"


def test_CT06_datas_no_calendario(bases):
    import pandas as pd
    datas_vendas = set(pd.to_datetime(bases["vendas"]["data"]).dt.normalize())
    datas_cal = set(pd.to_datetime(bases["calendario"]["data"]).dt.normalize())
    fora = datas_vendas - datas_cal
    assert not fora, f"{len(fora)} datas de vendas fora do calendário, ex.: {sorted(fora)[:5]}"


@pytest.mark.parametrize("tabela, coluna", [
    ("vendas", "codigo_venda"), ("itens_venda", "codigo_item_venda"),
])
def test_CT06_codigos_unicos(bases, tabela, coluna):
    dup = bases[tabela][coluna].duplicated().sum()
    assert dup == 0, f"{dup} {coluna} duplicados em {tabela}"


@pytest.mark.parametrize("tabela, coluna", [
    ("vendas", "valor_bruto"), ("vendas", "valor_desconto"), ("vendas", "valor_liquido"),
    ("itens_venda", "quantidade"), ("itens_venda", "valor_total"), ("metas_valor", "meta_valor"),
])
def test_CT06_sem_negativos(bases, tabela, coluna):
    neg = (bases[tabela][coluna] < 0).sum()
    assert neg == 0, f"{tabela}.{coluna} tem {neg} valores negativos"


def test_CT06_liquido_igual_bruto_menos_desconto(bases):
    v = bases["vendas"]
    dif = (v["valor_bruto"] - v["valor_desconto"] - v["valor_liquido"]).abs() > 0.01
    assert dif.sum() == 0, f"{dif.sum()} vendas onde líquido ≠ bruto − desconto"


def test_CT06_itens_somam_valor_bruto(bases):
    soma_itens = bases["itens_venda"].groupby("codigo_venda")["valor_total"].sum()
    bruto = bases["vendas"].set_index("codigo_venda")["valor_bruto"]
    dif = (bruto - soma_itens.reindex(bruto.index).fillna(0)).abs() > 0.01
    assert dif.sum() == 0, f"{dif.sum()} vendas onde a soma dos itens ≠ valor_bruto"


# ---------- Manuais ----------
MANUAIS = {
    "CT-00": "Requisitos visuais (8 elementos)",
    "CT-07": "Requisição de homologação / log de bugs",
    "CT-08": "Exportação em PDF e envio por e-mail",
    "CT-09": "Navegação, botões, marcadores e fatiadores",
}


@pytest.mark.parametrize("caso", MANUAIS)
def test_manual(caso):
    pytest.skip(f"{caso} é manual: {MANUAIS[caso]}")