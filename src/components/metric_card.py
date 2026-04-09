"""
components/metric_card.py
Card de métrica mini para o painel superior.
"""

import flet as ft
from theme import (
    BG_PRIMARY, BORDER_COLOR, BORDER_WIDTH, FONT_SIZE_XS,
    FONT_SIZE_2XL, PAD_MD, TEXT_PRIMARY, TEXT_SECONDARY,
    GREEN_PRIMARY, RED_PRIMARY, NEUTRAL_TEXT,
)


def metric_card(
    label: str,
    valor: str,
    delta: str = "",
    delta_up: bool | None = None,
    expand: bool = False,
) -> ft.Container:
    """
    Card com label, valor grande e delta opcional.
    delta_up: True=verde, False=vermelho, None=neutro
    """
    if delta_up is True:
        delta_color = GREEN_PRIMARY
    elif delta_up is False:
        delta_color = RED_PRIMARY
    else:
        delta_color = NEUTRAL_TEXT

    children: list[ft.Control] = [
        ft.Text(label, size=FONT_SIZE_XS, color=TEXT_SECONDARY,
                text_align=ft.TextAlign.CENTER),
        ft.Text(valor, size=FONT_SIZE_2XL, color=TEXT_PRIMARY,
                weight=ft.FontWeight.W_500,
                text_align=ft.TextAlign.CENTER),
    ]
    if delta:
        children.append(
            ft.Text(delta, size=FONT_SIZE_XS, color=delta_color,
                    text_align=ft.TextAlign.CENTER)
        )

    return ft.Container(
        content=ft.Column(
            children,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=2,
        ),
        bgcolor=BG_PRIMARY,
        border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
        border_radius=ft.BorderRadius.all(10),
        padding=PAD_MD,
        expand=expand,
    )
