"""
views/renda_fixa.py
Aba Renda Fixa — CDB, LCI/LCA, Tesouro Direto ranqueados por taxa líquida.
"""

import flet as ft
from theme import (
    BG_PRIMARY, BG_SECONDARY, BORDER_COLOR, BORDER_WIDTH,
    GREEN_PRIMARY, RED_PRIMARY, YELLOW_PRIMARY, BLUE_PRIMARY,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY,
    FONT_SIZE_XS, FONT_SIZE_SM, FONT_SIZE_MD, FONT_SIZE_XL,
    PAD_MD, PAD_SM, PAD_XS,
)

_CDI_HOJE = "13,65% a.a."
_IPCA_HOJE = "5,10%"
_SELIC_HOJE = "13,75%"

_CDBS = [
    {"nome": "CDB Banco Inter",    "det": "Liquidez diária · FGC até R$250k · Mín R$100", "taxa": "112% CDI",  "bruto": "≈ 15,3% a.a."},
    {"nome": "CDB Sofisa Direto",  "det": "Venc. 2 anos · FGC · Mín R$1",                 "taxa": "118% CDI",  "bruto": "≈ 16,1% a.a."},
    {"nome": "CDB Prefixado BTG",  "det": "Venc. 1 ano · FGC · Mín R$1.000",              "taxa": "14,8% a.a.", "bruto": "Prefixado"},
]
_LCIS = [
    {"nome": "LCI Bradesco",       "det": "90 dias carência · FGC · Isenção IR",           "taxa": "IPCA + 6,2%",  "bruto": "≈ 11,3% líquido"},
    {"nome": "LCA Rabobank",       "det": "Venc. 2 anos · FGC · Agronegócio",              "taxa": "95% CDI",       "bruto": "≈ 12,97% líquido"},
    {"nome": "LCI XP Investimentos","det": "180 dias · FGC · Isenção IR",                  "taxa": "13,0% a.a.",   "bruto": "Prefixado isento"},
]
_TESOURO = [
    {"nome": "Tesouro Selic 2027",     "det": "Liquidez D+1 · Baixo risco",           "taxa": "SELIC +0,04%", "bruto": "≈ 13,79% a.a."},
    {"nome": "Tesouro IPCA+ 2035",     "det": "Longo prazo · Proteção inflação",      "taxa": "IPCA + 6,8%",  "bruto": "≈ 11,9% real a.a."},
    {"nome": "Tesouro Prefixado 2029", "det": "Trava taxa atual · Médio prazo",       "taxa": "14,2% a.a.",   "bruto": "Prefixado"},
]


def _ref_pill(label: str, valor: str, cor: str) -> ft.Row:
    return ft.Row(
        [
            ft.Text(label + " ", size=FONT_SIZE_SM, color=TEXT_SECONDARY),
            ft.Text(valor, size=FONT_SIZE_SM, weight=ft.FontWeight.W_600, color=cor),
        ],
        spacing=0,
    )


def _fi_card(item: dict) -> ft.Container:
    return ft.Container(
        content=ft.Row(
            [
                ft.Column(
                    [
                        ft.Text(item["nome"], size=FONT_SIZE_MD,
                                weight=ft.FontWeight.W_500, color=TEXT_PRIMARY),
                        ft.Text(item["det"], size=FONT_SIZE_XS, color=TEXT_SECONDARY),
                    ],
                    spacing=2, expand=True,
                ),
                ft.Column(
                    [
                        ft.Text(item["taxa"], size=FONT_SIZE_XL,
                                weight=ft.FontWeight.W_500, color=GREEN_PRIMARY),
                        ft.Text(item["bruto"], size=FONT_SIZE_XS, color=TEXT_TERTIARY),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    spacing=2,
                ),
            ],
            spacing=8,
        ),
        bgcolor=BG_SECONDARY,
        border_radius=ft.BorderRadius.all(8),
        padding=PAD_MD,
        margin=ft.Margin.only(bottom=8),
    )


def _group_card(title: str, items: list) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [ft.Text(title.upper(), size=FONT_SIZE_XS,
                     color=TEXT_TERTIARY, style=ft.TextStyle(letter_spacing=1.5))]
            + [_fi_card(i) for i in items],
            spacing=0,
        ),
        bgcolor=BG_PRIMARY,
        border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
        border_radius=ft.BorderRadius.all(10),
        padding=PAD_MD,
        expand=True,
    )


def _sinal_row(cor: str, texto: str) -> ft.Row:
    return ft.Row(
        [
            ft.Container(width=8, height=8, bgcolor=cor,
                         border_radius=ft.BorderRadius.all(4)),
            ft.Text(texto, size=FONT_SIZE_SM, color=TEXT_PRIMARY, expand=True),
        ],
        spacing=8,
    )


def build_renda_fixa() -> ft.Column:
    ref_bar = ft.Container(
        content=ft.Row(
            [
                ft.Text("Referências do dia:", size=FONT_SIZE_SM, color=TEXT_SECONDARY),
                _ref_pill("CDI",   _CDI_HOJE,   BLUE_PRIMARY),
                _ref_pill("IPCA",  _IPCA_HOJE,  RED_PRIMARY),
                _ref_pill("SELIC", _SELIC_HOJE, GREEN_PRIMARY),
            ],
            spacing=16,
            wrap=True,
        ),
        bgcolor=BG_SECONDARY,
        border_radius=ft.BorderRadius.all(8),
        padding=ft.Padding.symmetric(horizontal=PAD_MD, vertical=10),
    )

    estrategia = ft.Container(
        content=ft.Column(
            [
                ft.Text("ESTRATÉGIA — QUAL ESCOLHER AGORA?",
                        size=FONT_SIZE_XS, color=TEXT_TERTIARY, style=ft.TextStyle(letter_spacing=1.5)),
                _sinal_row(GREEN_PRIMARY, "Juros em queda? Prefixado e IPCA+ ganham mais"),
                _sinal_row(GREEN_PRIMARY, "Curto prazo (< 1 ano): CDI/Selic é seguro"),
                _sinal_row(GREEN_PRIMARY, "LCI/LCA isento = equivale a CDI >100% líquido"),
                _sinal_row(YELLOW_PRIMARY, "IPCA+ para reserva de longo prazo (5+ anos)"),
                _sinal_row(RED_PRIMARY, "Evite prefixado longo se SELIC pode subir"),
            ],
            spacing=8,
        ),
        bgcolor=BG_PRIMARY,
        border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
        border_radius=ft.BorderRadius.all(10),
        padding=PAD_MD,
        expand=True,
    )

    # Tabela IR regressivo
    def _ir_row(prazo, aliq, fator):
        return ft.DataRow(cells=[
            ft.DataCell(ft.Text(prazo, size=FONT_SIZE_SM, color=TEXT_PRIMARY)),
            ft.DataCell(ft.Text(aliq,  size=FONT_SIZE_SM, color=RED_PRIMARY)),
            ft.DataCell(ft.Text(fator, size=FONT_SIZE_SM, color=GREEN_PRIMARY)),
        ])

    ir_table = ft.Container(
        content=ft.Column(
            [
                ft.Text("TABELA IR REGRESSIVO", size=FONT_SIZE_XS,
                        color=TEXT_TERTIARY, style=ft.TextStyle(letter_spacing=1.5)),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Prazo", size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
                        ft.DataColumn(ft.Text("Alíquota IR", size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
                        ft.DataColumn(ft.Text("Fator líquido", size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
                    ],
                    rows=[
                        _ir_row("Até 180 dias",      "22,5%", "× 0,775"),
                        _ir_row("181 a 360 dias",    "20,0%", "× 0,800"),
                        _ir_row("361 a 720 dias",    "17,5%", "× 0,825"),
                        _ir_row("Acima de 720 dias", "15,0%", "× 0,850"),
                    ],
                    border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
                    horizontal_lines=ft.BorderSide(BORDER_WIDTH, BORDER_COLOR),
                    heading_row_color=BG_SECONDARY,
                    column_spacing=20,
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

    return ft.Column(
        [
            ref_bar,
            ft.Row(
                [
                    _group_card("CDB / RDB — Recomendados", _CDBS),
                    _group_card("LCI / LCA — Isentos de IR", _LCIS),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            ft.Row(
                [
                    _group_card("Tesouro Direto", _TESOURO),
                    ft.Column(
                        [estrategia, ir_table],
                        spacing=10, expand=True,
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
    )
