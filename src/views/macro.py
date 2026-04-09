"""
views/macro.py
Aba Macro / Cenário — indicadores macroeconômicos do Brasil e EUA.
"""

import flet as ft
from theme import (
    BG_PRIMARY, BG_SECONDARY, BORDER_COLOR, BORDER_WIDTH,
    GREEN_PRIMARY, RED_PRIMARY, YELLOW_PRIMARY, BLUE_PRIMARY,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY,
    FONT_SIZE_XS, FONT_SIZE_SM, FONT_SIZE_MD,
    PAD_MD, PAD_SM,
)


def _macro_row(label: str, valor: str, cor: str = None) -> ft.Row:
    return ft.Container(
        content=ft.Row(
            [
                ft.Text(label, size=FONT_SIZE_SM, color=TEXT_SECONDARY, expand=True),
                ft.Text(valor, size=FONT_SIZE_SM,
                        weight=ft.FontWeight.W_500,
                        color=cor or TEXT_PRIMARY),
            ],
        ),
        padding=ft.Padding.symmetric(vertical=7),
        border=ft.Border.only(bottom=ft.BorderSide(0.5, BORDER_COLOR)),
    )


def _macro_card(title: str, rows: list) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [ft.Text(title.upper(), size=FONT_SIZE_XS,
                     color=TEXT_TERTIARY, style=ft.TextStyle(letter_spacing=1.5))]
            + rows,
            spacing=0,
        ),
        bgcolor=BG_PRIMARY,
        border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
        border_radius=ft.BorderRadius.all(10),
        padding=PAD_MD,
        expand=True,
    )


def _sinal_row(cor: str, texto: str) -> ft.Row:
    return ft.Container(
        content=ft.Row(
            [
                ft.Container(width=8, height=8, bgcolor=cor,
                             border_radius=ft.BorderRadius.all(4)),
                ft.Text(texto, size=FONT_SIZE_SM, color=TEXT_PRIMARY, expand=True),
            ],
            spacing=8,
        ),
        padding=ft.Padding.symmetric(vertical=6),
        border=ft.Border.only(bottom=ft.BorderSide(0.5, BORDER_COLOR)),
    )


def _alert_event(cor: str, texto: str, data: str) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            [
                ft.Container(width=6, height=6, bgcolor=cor,
                             border_radius=ft.BorderRadius.all(3),
                             margin=ft.Margin.only(top=3)),
                ft.Column(
                    [
                        ft.Text(texto, size=FONT_SIZE_SM, color=TEXT_PRIMARY),
                        ft.Text(data, size=FONT_SIZE_XS, color=TEXT_TERTIARY),
                    ],
                    spacing=1, expand=True,
                ),
            ],
            spacing=8,
        ),
        bgcolor=BG_SECONDARY,
        border_radius=ft.BorderRadius.all(6),
        padding=ft.Padding.symmetric(horizontal=10, vertical=8),
        margin=ft.Margin.only(bottom=6),
    )


def build_macro() -> ft.Column:
    brasil = _macro_card(
        "Brasil — Indicadores BACEN",
        [
            _macro_row("SELIC Meta",         "13,75% a.a."),
            _macro_row("IPCA acumulado 12m", "5,10%",          RED_PRIMARY),
            _macro_row("Meta IPCA 2026",     "3,0% ± 1,5%"),
            _macro_row("CDI",                "13,65% a.a."),
            _macro_row("PIB estimado 2026",  "+2,1%",           GREEN_PRIMARY),
            _macro_row("Desemprego",         "6,8%"),
            _macro_row("Dívida/PIB",         "89,2%",           RED_PRIMARY),
        ],
    )

    cambio = _macro_card(
        "Câmbio & Commodities",
        [
            _macro_row("USD/BRL",            "5,82",            RED_PRIMARY),
            _macro_row("EUR/BRL",            "6,38"),
            _macro_row("Minério de Ferro (t)","US$ 102",        YELLOW_PRIMARY),
            _macro_row("Petróleo Brent",     "US$ 78,40",       GREEN_PRIMARY),
            _macro_row("Soja (bushel)",      "US$ 10,22"),
            _macro_row("Ouro (oz)",          "US$ 2.980",       GREEN_PRIMARY),
        ],
    )

    eua = _macro_card(
        "EUA — Fed & Mercado Global",
        [
            _macro_row("Fed Funds Rate",     "4,25–4,50%"),
            _macro_row("CPI EUA 12m",        "2,8%",            YELLOW_PRIMARY),
            _macro_row("S&P 500",            "5.611 +0,4%",     GREEN_PRIMARY),
            _macro_row("Nasdaq",             "17.480 +0,6%",    GREEN_PRIMARY),
            _macro_row("VIX (medo)",         "22,4",            YELLOW_PRIMARY),
            _macro_row("Treasuries 10y",     "4,21%"),
        ],
    )

    termometro = ft.Container(
        content=ft.Column(
            [
                ft.Text("TERMÔMETRO DE RISCO — IMPACTO NAS DECISÕES",
                        size=FONT_SIZE_XS, color=TEXT_TERTIARY, style=ft.TextStyle(letter_spacing=1.5)),
                ft.Row(
                    [
                        ft.Column(
                            [
                                _sinal_row(RED_PRIMARY,  "Real desvalorizado → favorece exportadoras (VALE3, PETR4)"),
                                _sinal_row(RED_PRIMARY,  "IPCA acima da meta → SELIC pode subir"),
                                _sinal_row(RED_PRIMARY,  "Dívida/PIB alta → risco fiscal persiste"),
                            ],
                            spacing=0, expand=True,
                        ),
                        ft.Column(
                            [
                                _sinal_row(GREEN_PRIMARY,  "Petróleo em alta → PETR4 se beneficia"),
                                _sinal_row(GREEN_PRIMARY,  "PIB positivo → consumo e bancos ganham"),
                                _sinal_row(YELLOW_PRIMARY, "VIX elevado → cautela com bolsa no curto prazo"),
                            ],
                            spacing=0, expand=True,
                        ),
                    ],
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            spacing=10,
        ),
        bgcolor=BG_PRIMARY,
        border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
        border_radius=ft.BorderRadius.all(10),
        padding=PAD_MD,
        expand=True,
    )

    eventos = ft.Container(
        content=ft.Column(
            [
                ft.Text("PRÓXIMOS EVENTOS-CHAVE",
                        size=FONT_SIZE_XS, color=TEXT_TERTIARY, style=ft.TextStyle(letter_spacing=1.5)),
                _alert_event(RED_PRIMARY,    "Reunião COPOM — decisão SELIC",  "08/04/2026"),
                _alert_event(YELLOW_PRIMARY, "IPCA março (IBGE)",              "09/04/2026"),
                _alert_event(BLUE_PRIMARY,   "Fed Meeting — juros EUA",        "07/05/2026"),
            ],
            spacing=6,
        ),
        bgcolor=BG_PRIMARY,
        border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
        border_radius=ft.BorderRadius.all(10),
        padding=PAD_MD,
    )

    return ft.Column(
        [
            ft.Row(
                [brasil, cambio, eua],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Row(
                [
                    ft.Container(content=termometro, expand=2),
                    ft.Container(content=eventos, expand=1),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
    )
