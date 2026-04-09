"""
components/top_bar.py
Barra superior com logo, status do mercado e indicadores em tempo real.
"""

import flet as ft
from datetime import datetime
from theme import (
    BG_PRIMARY, BORDER_COLOR, BORDER_WIDTH,
    GREEN_PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY,
    FONT_SIZE_XS, FONT_SIZE_LG, PAD_MD,
)


def top_bar() -> ft.Container:
    now = datetime.now()
    hora = now.strftime("%d/%m/%Y · %H:%M")

    # Dot sem animação — compatível com todas as versões do Flet
    live_dot = ft.Container(
        width=8, height=8,
        border_radius=ft.BorderRadius.all(4),
        bgcolor=GREEN_PRIMARY,
    )

    return ft.Container(
        content=ft.Row(
            [
                # Logo
                ft.Row(
                    [
                        ft.Text("INVEST", size=FONT_SIZE_LG,
                                weight=ft.FontWeight.W_500,
                                color=TEXT_PRIMARY),
                        ft.Text("LAB", size=FONT_SIZE_LG,
                                weight=ft.FontWeight.W_500,
                                color=GREEN_PRIMARY),
                        ft.Text(" — Painel de Decisão",
                                size=FONT_SIZE_XS,
                                color=TEXT_SECONDARY),
                    ],
                    spacing=0,
                ),
                # Status
                ft.Row(
                    [
                        ft.Row(
                            [
                                live_dot,
                                ft.Text("Mercado aberto", size=FONT_SIZE_XS,
                                        color=TEXT_SECONDARY),
                            ],
                            spacing=4,
                        ),
                        ft.Text(hora, size=FONT_SIZE_XS, color=TEXT_SECONDARY),
                        ft.Text("IBOV 131.240", size=FONT_SIZE_XS,
                                color=GREEN_PRIMARY),
                        ft.Text("SELIC 13,75%", size=FONT_SIZE_XS,
                                color=TEXT_SECONDARY),
                    ],
                    spacing=16,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=BG_PRIMARY,
        border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
        border_radius=ft.BorderRadius.all(10),
        padding=ft.Padding.symmetric(horizontal=PAD_MD, vertical=10),
        margin=ft.Margin.only(bottom=10),
    )
