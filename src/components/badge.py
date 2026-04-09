"""
components/badge.py
Badge colorido reutilizável (COMPRAR / MANTER / VENDER / tipos).
"""

import flet as ft
from theme import FONT_SIZE_XS, FONT_SIZE_SM, PAD_XS, PAD_SM
from utils.formatters import sinal_color, tipo_color


def badge_sinal(sinal: str, small: bool = False) -> ft.Container:
    """Badge de sinal de mercado (COMPRAR, MANTER, AGUARDAR, VENDER)."""
    bg, fg = sinal_color(sinal)
    size = FONT_SIZE_XS if small else FONT_SIZE_SM
    return ft.Container(
        content=ft.Text(
            sinal,
            size=size,
            weight=ft.FontWeight.W_600,
            color=fg,
            no_wrap=True,
        ),
        bgcolor=bg,
        border_radius=ft.BorderRadius.all(4),
        padding=ft.Padding.symmetric(horizontal=PAD_SM, vertical=PAD_XS),
    )


def badge_tipo(tipo: str, small: bool = False) -> ft.Container:
    """Badge do tipo de ativo (AÇÃO, FII, CDB, etc.)."""
    bg, fg = tipo_color(tipo)
    label = tipo.upper().replace("AÇÃO (B3)", "AÇÃO").replace(
        "TESOURO DIRETO", "TESOURO").replace(
        "DEBENTURE / CRI / CRA", "DEBÊNTURE").replace(
        "FUNDO DE INVESTIMENTO", "FUNDO")[:10]
    size = FONT_SIZE_XS if small else FONT_SIZE_XS
    return ft.Container(
        content=ft.Text(
            label,
            size=size,
            weight=ft.FontWeight.W_600,
            color=fg,
            no_wrap=True,
        ),
        bgcolor=bg,
        border_radius=ft.BorderRadius.all(4),
        padding=ft.Padding.symmetric(horizontal=PAD_SM, vertical=PAD_XS),
    )


def tag_chip(texto: str) -> ft.Container:
    """Mini chip/tag para labels personalizados."""
    from theme import BG_SECONDARY, TEXT_SECONDARY
    return ft.Container(
        content=ft.Text(texto, size=FONT_SIZE_XS, color=TEXT_SECONDARY),
        bgcolor=BG_SECONDARY,
        border_radius=ft.BorderRadius.all(4),
        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
    )
