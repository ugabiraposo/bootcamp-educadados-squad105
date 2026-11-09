from datetime import datetime

import pytest

from calculos import CALCULOS, FASE, carregar, carregar_valores, comparar


@pytest.fixture(scope="session")
def bases():
    return carregar()


def _fmt(v):
    if v is None:
        return "—"
    if isinstance(v, bool):
        return "Sim" if v else "Não"
    if isinstance(v, float):
        return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return str(v)


def _situacao(campo, calc, painel, doc):
    ok_p = None if painel is None else not comparar({campo: calc}, {campo: painel})
    ok_d = None if doc is None else not comparar({campo: calc}, {campo: doc})
    if ok_p is False:
        return "❌ Painel diverge dos dados: investigar"
    if ok_p and ok_d is False:
        return "⚠️ Erro de preenchimento no testes.md"
    if ok_p:
        return "✅ OK"
    if ok_d is False:
        return "⚠️ testes.md diverge dos dados: conferir no painel"
    if ok_d:
        return "🔸 Confere com testes.md (painel não coletado)"
    return "🔸 Sem valor informado: preencher"


def pytest_sessionfinish(session, exitstatus):
    try:
        b, valores = carregar(), carregar_valores()
    except Exception as e:
        print(f"\nNão foi possível gerar resultados_comparacao.md: {e}")
        return

    linhas = [
        "# Comparação: dados × painel × testes.md",
        "",
        f"Execução: {datetime.now():%d/%m/%Y %H:%M}",
        "",
        "| Caso | Campo | Calculado (dados) | Painel | testes.md | Situação |",
        "|:--|:--|--:|--:|--:|:--|",
    ]
    for ct, func in CALCULOS.items():
        try:
            calc = func(b)
        except Exception as e:
            linhas.append(f"| {ct} | — | erro no cálculo: {e} | — | — | ❌ Corrigir cálculo |")
            continue
        painel = valores.get(ct, {}).get("painel") or {}
        doc = valores.get(ct, {}).get("documentado") or {}
        for campo, valor in calc.items():
            p, d = painel.get(campo), doc.get(campo)
            linhas.append(f"| {ct} | {campo} | {_fmt(valor)} | {_fmt(p)} | {_fmt(d)} | "
                          f"{_situacao(campo, valor, p, d)} |")

    (FASE / "docs" / "resultados_comparacao.md").write_text("\n".join(linhas), encoding="utf-8")