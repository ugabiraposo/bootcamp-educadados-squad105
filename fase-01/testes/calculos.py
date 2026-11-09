"""Cálculos de referência dos casos de teste, feitos a partir das planilhas."""
from functools import lru_cache
from pathlib import Path
import json
import unicodedata

import numpy as np
import pandas as pd

FASE = Path(__file__).resolve().parent.parent
DADOS = FASE / "dados"
VALORES_JSON = FASE / "testes" / "valores.json"

PLANILHAS = [
    "vendas", "itens_venda", "filiais", "cidades", "vendedores",
    "profissionais", "servicos", "grupos_servico", "calendario",
    "metas_valor", "metas_quantidade",
]

DIMENSAO_CT02 = "cidade"   # ou "filial": o que o CT-02 chama de "categoria"

# Valores da coluna "nivel" em metas_valor.
# Se o nome for outro, a mensagem de erro mostra os valores existentes: ajuste aqui.
NIVEL_META = {"filial": "filial", "vendedor": "vendedor"}

TOLERANCIA = {
    "valor_liquido": 1.0, "valor_lider": 1.0, "meta": 1.0, "realizado": 1.0, "valor_bruto": 1.0,
    "atingimento_lider_pct": 0.01, "atingimento_pct": 0.01, "participacao_pct": 0.01,
}


def norm(texto):
    """Compara nomes ignorando acentos, espaços e maiúsculas (Brasilia == Brasília)."""
    s = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return s.strip().lower()


def carregar_valores():
    return json.loads(VALORES_JSON.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def carregar():
    b = {n: pd.read_excel(DADOS / f"{n}.xlsx") for n in PLANILHAS}

    # Evita conflito entre as várias colunas "nome"
    b["filiais"] = b["filiais"].rename(columns={"nome": "nome_filial"})
    b["vendedores"] = b["vendedores"].rename(columns={"nome": "nome_vendedor"})
    b["profissionais"] = b["profissionais"].rename(columns={"nome": "nome_profissional"})

    # Códigos lidos como decimal (por causa de vazios) viram inteiro, para os merges baterem
    for df in b.values():
        for col in df.columns:
            if col.startswith("codigo_") and pd.api.types.is_float_dtype(df[col]):
                df[col] = df[col].astype("Int64")

    # >>> Repita aqui as limpezas do Power Query (ver docs/power_query.md) <<<
    return b


# ---------- Tabelas auxiliares ----------
def _vendas(b):
    v = b["vendas"].merge(b["filiais"][["codigo_filial", "nome_filial", "codigo_cidade"]],
                          on="codigo_filial", how="left")
    v = v.merge(b["cidades"][["codigo_cidade", "cidade"]], on="codigo_cidade", how="left")
    return v.merge(b["vendedores"][["codigo_vendedor", "nome_vendedor"]],
                   on="codigo_vendedor", how="left")


def _metas(b, nivel):
    m = b["metas_valor"]
    sel = m[m["nivel"].map(norm) == norm(NIVEL_META[nivel])]
    if sel.empty:
        existentes = sorted(m["nivel"].dropna().astype(str).unique())
        raise ValueError(f"Nenhuma meta com nivel='{NIVEL_META[nivel]}'. "
                         f"Valores existentes: {existentes}. Ajuste NIVEL_META.")
    return sel


# ---------- Um cálculo por caso de teste ----------
def ct01(b):
    return {"valor_liquido": float(b["vendas"]["valor_liquido"].sum())}


def ct02(b):
    chave, nome = (("codigo_cidade", "cidade") if DIMENSAO_CT02 == "cidade"
                   else ("codigo_filial", "nome_filial"))
    v = _vendas(b)
    m = _metas(b, "filial").merge(b["filiais"][["codigo_filial", "codigo_cidade"]],
                                  on="codigo_filial", how="left")
    realizado = v.groupby(chave)["valor_liquido"].sum()
    meta = m.groupby(chave)["meta_valor"].sum()
    ating = realizado / meta * 100
    ating = ating[np.isfinite(ating)]
    nomes = v.drop_duplicates(chave).set_index(chave)[nome]

    lv, la = realizado.idxmax(), ating.idxmax()
    return {
        "lider_valor": str(nomes[lv]),
        "valor_lider": float(realizado[lv]),
        "atingimento_lider_pct": float(ating.get(lv, np.nan)),
        "lider_atingimento": str(nomes[la]),
        "coincide": bool(lv == la),
    }


def ct03(b):
    g = _vendas(b).groupby("codigo_cidade").agg(
        cidade=("cidade", "first"),
        qtd=("codigo_venda", "nunique"),
        valor=("valor_liquido", "sum"),
    )
    lider = g["qtd"].idxmax()
    return {"cidade": str(g.loc[lider, "cidade"]),
            "qtd_vendas": int(g.loc[lider, "qtd"]),
            "valor_liquido": float(g.loc[lider, "valor"])}


def ct04(b):
    realizado = b["vendas"].groupby("codigo_vendedor")["valor_liquido"].sum()
    meta = _metas(b, "vendedor").groupby("codigo_vendedor")["meta_valor"].sum()
    t = pd.DataFrame({"realizado": realizado, "meta": meta}).fillna(0)
    t = t[t["meta"] > 0].copy()                      # regra do CT-04: só Meta > 0
    t["ating"] = t["realizado"] / t["meta"] * 100
    pior = t["ating"].idxmin()
    nomes = b["vendedores"].set_index("codigo_vendedor")["nome_vendedor"]
    return {"vendedor": str(nomes[pior]),
            "meta": float(t.loc[pior, "meta"]),
            "realizado": float(t.loc[pior, "realizado"]),
            "atingimento_pct": float(t.loc[pior, "ating"])}


def ct05(b):
    i = b["itens_venda"].merge(b["servicos"][["codigo_servico", "codigo_grupo_servico"]],
                               on="codigo_servico", how="left")
    i = i.merge(b["grupos_servico"], on="codigo_grupo_servico", how="left")
    g = i.groupby("grupo_servico")["valor_total"].sum()   # valor bruto por item
    lider = g.idxmax()
    return {"grupo": str(lider),
            "valor_bruto": float(g[lider]),
            "participacao_pct": float(g[lider] / g.sum() * 100)}


CALCULOS = {"CT-01": ct01, "CT-02": ct02, "CT-03": ct03, "CT-04": ct04, "CT-05": ct05}


def comparar(calculado, informado):
    """Lista os campos divergentes. Campos null no informado são ignorados."""
    erros = []
    for campo, esp in informado.items():
        if esp is None:
            continue
        obt = calculado[campo]
        if isinstance(esp, str):
            ok = norm(obt) == norm(esp)
        elif isinstance(esp, bool):
            ok = bool(obt) == esp
        else:
            ok = abs(obt - esp) <= TOLERANCIA.get(campo, 0)
        if not ok:
            erros.append(f"{campo}: calculado={obt!r} | informado={esp!r}")
    return erros