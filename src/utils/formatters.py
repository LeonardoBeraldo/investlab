"""
utils/formatters.py
Funções de formatação de valores monetários, percentuais e datas.
"""

from datetime import date
from typing import Optional


def fmt_brl(valor: float, prefixo: bool = True) -> str:
    """Formata valor em reais: R$ 1.234,56"""
    s = f"{abs(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    sinal = "-" if valor < 0 else ""
    return f"{sinal}R$ {s}" if prefixo else f"{sinal}{s}"


def fmt_pct(valor: float, decimais: int = 1) -> str:
    """Formata percentual: +18,4%"""
    sinal = "+" if valor > 0 else ""
    return f"{sinal}{valor:.{decimais}f}%".replace(".", ",")


def fmt_pct_raw(valor: float, decimais: int = 1) -> str:
    """Percentual sem sinal: 13,75%"""
    return f"{valor:.{decimais}f}%".replace(".", ",")


def fmt_data(d: Optional[date]) -> str:
    """Formata data: 31/03/2026"""
    if d is None:
        return "—"
    return d.strftime("%d/%m/%Y")


def fmt_qtd(qtd: float) -> str:
    """Formata quantidade de cotas."""
    if qtd == int(qtd):
        return f"{int(qtd):,}".replace(",", ".")
    return f"{qtd:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_numero(n: float, decimais: int = 1) -> str:
    """Formata número simples: 131.240"""
    return f"{n:,.{decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pl_color(valor: float) -> str:
    """Retorna cor baseada no sinal do valor."""
    from theme import GREEN_PRIMARY, RED_PRIMARY, NEUTRAL_TEXT
    if valor > 0:
        return GREEN_PRIMARY
    if valor < 0:
        return RED_PRIMARY
    return NEUTRAL_TEXT


def sinal_color(sinal: str) -> tuple[str, str]:
    """Retorna (bg_color, text_color) para o badge de sinal."""
    from theme import (
        GREEN_BG, GREEN_DARK, RED_BG, RED_DARK,
        NEUTRAL_BG, NEUTRAL_DARK, YELLOW_BG, YELLOW_DARK,
    )
    mapa = {
        "COMPRAR":  (GREEN_BG,   GREEN_DARK),
        "MANTER":   (NEUTRAL_BG, NEUTRAL_DARK),
        "AGUARDAR": (YELLOW_BG,  YELLOW_DARK),
        "VENDER":   (RED_BG,     RED_DARK),
    }
    return mapa.get(sinal, (NEUTRAL_BG, NEUTRAL_DARK))


def tipo_color(tipo: str) -> tuple[str, str]:
    """Retorna (bg_color, text_color) para o badge de tipo de ativo."""
    from theme import (
        BLUE_BG, BLUE_PRIMARY, GREEN_BG, GREEN_DARK,
        YELLOW_BG, YELLOW_DARK, NEUTRAL_BG, NEUTRAL_DARK,
    )
    if "Ação" in tipo or "ETF" in tipo:
        return (BLUE_BG, BLUE_PRIMARY)
    if "FII" in tipo:
        return (GREEN_BG, GREEN_DARK)
    if "Tesouro" in tipo:
        return (NEUTRAL_BG, NEUTRAL_DARK)
    # CDB, LCI, LCA, Debenture, Fundo, Crypto
    return (YELLOW_BG, YELLOW_DARK)
