"""
views/visao_geral.py
Aba Visão Geral — cockpit do investidor.
"""

import flet as ft
import threading
from theme import (
    BG_PRIMARY, BG_SECONDARY, BORDER_COLOR, BORDER_WIDTH,
    GREEN_PRIMARY, GREEN_DARK, RED_PRIMARY, RED_DARK,
    YELLOW_PRIMARY, BLUE_PRIMARY, NEUTRAL_DARK,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY,
    FONT_SIZE_XS, FONT_SIZE_SM, FONT_SIZE_MD,
    PAD_MD, PAD_SM,
)
from components.metric_card import metric_card
from services.screener import get_top_dynamic, analyze_asset


def _card(title: str, content: ft.Control) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    title.upper(),
                    size=FONT_SIZE_XS,
                    color=TEXT_TERTIARY,
                    weight=ft.FontWeight.W_500,
                    style=ft.TextStyle(letter_spacing=1.5),
                ),
                content,
            ],
            spacing=10,
        ),
        bgcolor=BG_PRIMARY,
        border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
        border_radius=ft.BorderRadius.all(10),
        padding=PAD_MD,
    )


def _decision_box(label: str, cor: str, cor_texto: str,
                  tickers: list) -> ft.Container:
    chips = [
        ft.Container(
            content=ft.Text(t, size=FONT_SIZE_SM,
                            weight=ft.FontWeight.W_500, color=cor_texto),
            bgcolor=cor + "44",
            border_radius=ft.BorderRadius.all(4),
            padding=ft.Padding.symmetric(horizontal=PAD_SM, vertical=3),
        )
        for t in tickers
    ]
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(label, size=FONT_SIZE_XS,
                        weight=ft.FontWeight.W_500, color=cor_texto,
                        style=ft.TextStyle(letter_spacing=1)),
                ft.Row(chips, wrap=True, spacing=6),
            ],
            spacing=6,
        ),
        bgcolor=cor + "22",
        border=ft.Border.all(0.5, cor),
        border_radius=ft.BorderRadius.all(8),
        padding=PAD_MD,
        margin=ft.Margin.only(bottom=8),
    )


def _alert_row(cor: str, texto: str, tempo: str) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    width=6, height=6,
                    border_radius=ft.BorderRadius.all(3),
                    bgcolor=cor,
                ),
                ft.Column(
                    [
                        ft.Text(texto, size=FONT_SIZE_SM, color=TEXT_PRIMARY),
                        ft.Text(tempo, size=FONT_SIZE_XS, color=TEXT_TERTIARY),
                    ],
                    spacing=1,
                    expand=True,
                ),
            ],
            spacing=8,
        ),
        bgcolor=BG_SECONDARY,
        border_radius=ft.BorderRadius.all(6),
        padding=ft.Padding.symmetric(horizontal=10, vertical=8),
        margin=ft.Margin.only(bottom=6),
    )


def build_visao_geral() -> ft.Column:
    metricas = ft.Row(
        [
            metric_card("IBOVESPA", "131.240", "▲ +0,82%", True,  expand=True),
            metric_card("SELIC",    "13,75%",  "a.a.",     None,  expand=True),
            metric_card("IPCA 12m", "5,1%",    "▲ acima meta", False, expand=True),
            metric_card("USD/BRL",  "5,82",    "▲ +0,45%", False, expand=True),
        ],
        spacing=10,
    )

    decisoes_box_ref = ft.Ref[ft.Column]()

    decisoes = _card(
        "Resumo de Decisões — Hoje (YFinance)",
        ft.Column(
            ref=decisoes_box_ref,
            controls=[
                _decision_box("▲ COMPRAR",       GREEN_PRIMARY, GREEN_DARK, ["Carregando..."]),
                _decision_box("◆ MANTER",        "#888780",     "#444441",  ["Carregando..."]),
                _decision_box("▼ VENDER / EVITAR", RED_PRIMARY, RED_DARK,   ["Carregando..."]),
            ],
            spacing=0,
        ),
    )

    def load_decisoes():
        try:
            # Buscar ações quentes da B3 dinamicamente
            assets = get_top_dynamic('stock', limit=15)
            if not assets:
                return

            buy_list = []
            hold_list = []
            sell_list = []

            for a in assets:
                if not a.price: continue
                _, _, sinal = analyze_asset(a)
                sym = a.symbol.replace(".SA", "")
                
                if sinal == "COMPRAR":
                    buy_list.append(sym)
                elif sinal == "VENDER":
                    sell_list.append(sym)
                else:
                    hold_list.append(sym)

            # Limitar tamanho das listas
            buy_list = buy_list[:5] or ["Nenhum hoje"]
            hold_list = hold_list[:5] or ["Nenhum hoje"]
            sell_list = sell_list[:5] or ["Nenhum hoje"]

            decisoes_box_ref.current.controls = [
                _decision_box("▲ COMPRAR (Bons Múltiplos)",  GREEN_PRIMARY, GREEN_DARK, buy_list),
                _decision_box("◆ MANTER (Dentro da média)",  "#888780",     "#444441",  hold_list),
                _decision_box("▼ VENDER / EVITAR (Esticados)", RED_PRIMARY, RED_DARK,   sell_list),
            ]
            decisoes_box_ref.current.update()
            if decisoes_box_ref.current.page:
                decisoes_box_ref.current.page.update()
        except:
            pass

    threading.Timer(0.2, load_decisoes).start()

    alertas = _card(
        "Alertas & Eventos",
        ft.Column(
            [
                _alert_row(RED_PRIMARY,    "Dados macro carregados com base no layout atual", "Info — Geral"),
                _alert_row(YELLOW_PRIMARY, "Decisão de juros pode impactar seu Renda Fixa", "Lembrete"),
                _alert_row(GREEN_PRIMARY,  "Mercado operando — cotações agora são via yfinance em runtime", "Hoje · Yfinance"),
            ],
            spacing=0,
        ),
    )

    return ft.Column(
        [
            metricas,
            ft.Row(
                [
                    ft.Container(content=decisoes, expand=2),
                    ft.Container(content=alertas, expand=1),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
    )
