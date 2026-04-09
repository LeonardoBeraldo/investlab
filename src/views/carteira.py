"""
views/carteira.py
Aba Minha Carteira — posições reais, performance e rebalanceamento.
"""

from __future__ import annotations
import flet as ft
from typing import Callable

from models.ativo import Ativo, TipoAtivo, Sinal
from utils.formatters import (
    fmt_brl, fmt_pct, pl_color, sinal_color, tipo_color,
)
from components.badge import badge_sinal, badge_tipo

import threading
from services.screener import get_quotes
from theme import (
    BG_PRIMARY, BG_SECONDARY, BORDER_COLOR, BORDER_WIDTH,
    GREEN_PRIMARY, RED_PRIMARY, YELLOW_PRIMARY, BLUE_PRIMARY,
    GREEN_BG, GREEN_DARK, RED_BG, RED_DARK, NEUTRAL_BG, NEUTRAL_DARK,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY,
    FONT_SIZE_XS, FONT_SIZE_SM, FONT_SIZE_MD, FONT_SIZE_XL,
    PAD_MD, PAD_SM, PAD_XS,
)


def _alloc_bar(label: str, pct: float, cor: str) -> ft.Column:
    return ft.Column(
        [
            ft.Row(
                [
                    ft.Text(label, size=FONT_SIZE_SM, color=TEXT_SECONDARY, expand=True),
                    ft.Text(f"{pct:.0f}%", size=FONT_SIZE_SM,
                            weight=ft.FontWeight.W_500),
                ],
            ),
            ft.Container(
                content=ft.Container(
                    width=pct * 2.5,
                    height=8,
                    bgcolor=cor,
                    border_radius=ft.BorderRadius.all(4),
                ),
                height=8,
                bgcolor=BG_SECONDARY,
                border_radius=ft.BorderRadius.all(4),
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            ),
        ],
        spacing=4,
    )


def _bench_row(label: str, valor: str, positivo: bool = True) -> ft.Row:
    cor = GREEN_PRIMARY if positivo else RED_PRIMARY
    return ft.Container(
        content=ft.Row(
            [
                ft.Text(label, size=FONT_SIZE_SM, color=TEXT_SECONDARY, expand=True),
                ft.Text(valor, size=FONT_SIZE_SM, weight=ft.FontWeight.W_500, color=cor),
            ],
        ),
        padding=ft.Padding.symmetric(vertical=7),
        border=ft.Border.only(bottom=ft.BorderSide(0.5, BORDER_COLOR)),
    )


def _rebal_box(label: str, bg: str, border: str, texto_cor: str,
               itens: list[str]) -> ft.Container:
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(label, size=FONT_SIZE_XS,
                        weight=ft.FontWeight.W_500,
                        color=texto_cor, style=ft.TextStyle(letter_spacing=1)),
                ft.Text(", ".join(itens),
                        size=FONT_SIZE_SM, color=texto_cor,
                        no_wrap=False),
            ],
            spacing=6,
        ),
        bgcolor=bg,
        border=ft.Border.all(0.5, border),
        border_radius=ft.BorderRadius.all(8),
        padding=PAD_MD,
        expand=True,
    )


class CarteiraView:
    """
    View da carteira com estado reativo.
    Recebe lista de ativos e callbacks para editar/excluir/adicionar.
    """

    def __init__(
        self,
        ativos: list[Ativo],
        on_adicionar: Callable,
        on_editar: Callable[[Ativo], None],
        on_excluir: Callable[[str], None],
    ) -> None:
        self.ativos = ativos
        self.on_adicionar = on_adicionar
        self.on_editar = on_editar
        self.on_excluir = on_excluir

    # ── Cálculos ──────────────────────────────────────────────

    def _total_patrimonio(self) -> float:
        return sum(a.valor_atual for a in self.ativos)

    def _total_pl(self) -> float:
        return sum(a.pl_reais for a in self.ativos)

    def _total_dividendos(self) -> float:
        return sum(a.dividendos_recebidos for a in self.ativos)

    def _alocacao_pct(self, tipo_list: list[TipoAtivo]) -> float:
        total = self._total_patrimonio()
        if total <= 0:
            return 0.0
        sub = sum(a.valor_atual for a in self.ativos if a.tipo in tipo_list)
        return (sub / total) * 100

    # ── Linha da tabela ───────────────────────────────────────

    def _build_row(self, ativo: Ativo) -> ft.DataRow:
        total = self._total_patrimonio()
        pct_cart = (ativo.valor_atual / total * 100) if total > 0 else 0
        nome_display = ativo.ticker if ativo.ticker else ativo.nome[:18]

        return ft.DataRow(
            cells=[
                ft.DataCell(badge_tipo(ativo.tipo.value, small=True)),
                ft.DataCell(ft.Text(nome_display, size=FONT_SIZE_MD,
                                    weight=ft.FontWeight.W_500, color=TEXT_PRIMARY)),
                ft.DataCell(ft.Text(
                    f"{int(ativo.quantidade)} cotas" if ativo.quantidade > 0
                    else fmt_brl(ativo.valor_total),
                    size=FONT_SIZE_SM, color=TEXT_SECONDARY,
                )),
                ft.DataCell(ft.Text(
                    fmt_brl(ativo.preco_compra) if ativo.preco_compra > 0 else "—",
                    size=FONT_SIZE_SM,
                )),
                ft.DataCell(ft.Text(
                    fmt_brl(ativo.preco_atual) if ativo.preco_atual > 0
                    else ativo.rentabilidade_atual or "—",
                    size=FONT_SIZE_SM,
                )),
                ft.DataCell(ft.Text(
                    fmt_brl(ativo.valor_atual),
                    size=FONT_SIZE_SM, weight=ft.FontWeight.W_500,
                )),
                ft.DataCell(ft.Text(
                    fmt_brl(ativo.pl_reais, prefixo=True),
                    size=FONT_SIZE_SM,
                    color=pl_color(ativo.pl_reais),
                    weight=ft.FontWeight.W_500,
                )),
                ft.DataCell(ft.Text(
                    fmt_pct(ativo.pl_percentual),
                    size=FONT_SIZE_SM,
                    color=pl_color(ativo.pl_percentual),
                )),
                ft.DataCell(ft.Text(
                    f"{pct_cart:.1f}%", size=FONT_SIZE_SM,
                )),
                ft.DataCell(ft.Text(
                    ativo.corretora.value.split()[0],
                    size=FONT_SIZE_XS, color=TEXT_TERTIARY,
                )),
                ft.DataCell(badge_sinal(ativo.sinal.value, small=True)),
                ft.DataCell(
                    ft.Row(
                        [
                            ft.IconButton(
                                ft.Icons.EDIT_OUTLINED,
                                icon_size=16,
                                icon_color=BLUE_PRIMARY,
                                tooltip="Editar",
                                on_click=lambda e, a=ativo: self.on_editar(a),
                            ),
                            ft.IconButton(
                                ft.Icons.DELETE_OUTLINE,
                                icon_size=16,
                                icon_color=RED_PRIMARY,
                                tooltip="Excluir",
                                on_click=lambda e, a=ativo: self.on_excluir(a.id),
                            ),
                        ],
                        spacing=0,
                    )
                ),
            ]
        )

    # ── Build principal ───────────────────────────────────────

    def build(self) -> ft.Column:
        total = self._total_patrimonio()
        pl_total = self._total_pl()
        divid = self._total_dividendos()
        pl_pct = (pl_total / (total - pl_total) * 100) if (total - pl_total) > 0 else 0

        pct_rv   = self._alocacao_pct([TipoAtivo.ACAO, TipoAtivo.ETF])
        pct_fii  = self._alocacao_pct([TipoAtivo.FII])
        pct_rf   = self._alocacao_pct([TipoAtivo.CDB, TipoAtivo.LCI_LCA, TipoAtivo.DEBENT])
        pct_tes  = self._alocacao_pct([TipoAtivo.TESOURO])
        pct_oth  = 100 - pct_rv - pct_fii - pct_rf - pct_tes

        # ── Cards de resumo ──
        resumo = ft.Row(
            [
                self._mini_card("Patrimônio Total",  fmt_brl(total),
                                fmt_pct(pl_pct) + " (total)", pl_pct > 0),
                self._mini_card("P&L não realizado", fmt_brl(pl_total),
                                fmt_pct(pl_pct), pl_pct > 0),
                self._mini_card("Dividendos (total)", fmt_brl(divid),
                                "recebidos", True),
                self._mini_card("Ativos",            str(len(self.ativos)),
                                "na carteira", None),
            ],
            spacing=10,
        )

        # ── Alocação atual ──
        alocacao = ft.Container(
            content=ft.Column(
                [
                    ft.Text("ALOCAÇÃO ATUAL", size=FONT_SIZE_XS,
                            color=TEXT_TERTIARY, style=ft.TextStyle(letter_spacing=1.5)),
                    _alloc_bar("Renda Variável — Ações",  pct_rv,  "#185FA5"),
                    _alloc_bar("FIIs",                    pct_fii, GREEN_PRIMARY),
                    _alloc_bar("Renda Fixa (CDI/CDB)",   pct_rf,  YELLOW_PRIMARY),
                    _alloc_bar("Tesouro IPCA+",           pct_tes, "#D85A30"),
                    _alloc_bar("Outros / Caixa",          max(pct_oth, 0), "#888780"),
                ],
                spacing=10,
            ),
            bgcolor=BG_PRIMARY,
            border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
            border_radius=ft.BorderRadius.all(10),
            padding=PAD_MD,
            expand=True,
        )

        # ── Performance ──
        performance = ft.Container(
            content=ft.Column(
                [
                    ft.Text("PERFORMANCE ACUMULADA", size=FONT_SIZE_XS,
                            color=TEXT_TERTIARY, style=ft.TextStyle(letter_spacing=1.5)),
                    ft.Row(
                        [
                            self._perf_mini("+18,4%", "12 meses"),
                            self._perf_mini("+6,2%",  "6 meses"),
                            self._perf_mini("+3,1%",  "3 meses"),
                            self._perf_mini("+1,4%",  "Este mês"),
                        ],
                        spacing=10,
                    ),
                    _bench_row("vs CDI (benchmark)", "+4,7% acima"),
                    _bench_row("vs IBOV",            "+2,1% acima"),
                    _bench_row("vs IFIX",            "+1,8% acima"),
                    _bench_row("Dividendos 12m",     fmt_brl(divid)),
                ],
                spacing=8,
            ),
            bgcolor=BG_PRIMARY,
            border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
            border_radius=ft.BorderRadius.all(10),
            padding=PAD_MD,
            expand=True,
        )

        tabela_dt = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Tipo",    size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
                ft.DataColumn(ft.Text("Ativo",   size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
                ft.DataColumn(ft.Text("Qtd/Val", size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
                ft.DataColumn(ft.Text("Pm R$",   size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
                ft.DataColumn(ft.Text("Atual*",  size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
                ft.DataColumn(ft.Text("Total",   size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
                ft.DataColumn(ft.Text("P&L R$",  size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
                ft.DataColumn(ft.Text("P&L %",   size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
                ft.DataColumn(ft.Text("% Cart.", size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
                ft.DataColumn(ft.Text("Corret.", size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
                ft.DataColumn(ft.Text("Sinal*",  size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
                ft.DataColumn(ft.Text("Ações",   size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ],
            rows=[self._build_row(a) for a in self.ativos],
            border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
            border_radius=ft.BorderRadius.all(10),
            horizontal_lines=ft.BorderSide(BORDER_WIDTH, BORDER_COLOR),
            heading_row_color=BG_SECONDARY,
            column_spacing=12,
        )

        tabela_ativos = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Ativos Cadastrados",
                                    size=FONT_SIZE_MD,
                                    weight=ft.FontWeight.W_500,
                                    color=TEXT_PRIMARY,
                                    expand=True),
                            ft.FilledButton(
                                "+ Novo Ativo",
                                style=ft.ButtonStyle(bgcolor=GREEN_DARK, color="#9FE1CB", shape=ft.RoundedRectangleBorder(radius=8)),
                                on_click=lambda e: self.on_adicionar(),
                            ),
                        ],
                    ),
                    ft.Container(
                        content=tabela_dt,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    ),
                ],
                spacing=10,
            ),
            bgcolor=BG_PRIMARY,
            border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
            border_radius=ft.BorderRadius.all(10),
            padding=PAD_MD,
        )

        # ── Rebalanceamento IA ──
        rebal_row = ft.Row(
            [
                _rebal_box("▲ AUMENTAR POSIÇÃO", GREEN_BG, GREEN_PRIMARY, GREEN_DARK, ["Carregando..."]),
                _rebal_box("◆ MANTER COMO ESTÁ", NEUTRAL_BG, NEUTRAL_DARK, NEUTRAL_DARK, ["Carregando..."]),
                _rebal_box("▼ REDUZIR OU SAIR", RED_BG, RED_PRIMARY, RED_DARK, ["Carregando..."]),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        rebal = ft.Container(
            content=ft.Column(
                [
                    ft.Text("SUGESTÃO DE REBALANCEAMENTO — IA / YFINANCE",
                            size=FONT_SIZE_XS, color=TEXT_TERTIARY, style=ft.TextStyle(letter_spacing=1.5)),
                    rebal_row,
                ],
                spacing=10,
            ),
            bgcolor=BG_PRIMARY,
            border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
            border_radius=ft.BorderRadius.all(10),
            padding=PAD_MD,
        )

        # Atualizacao em background
        def update_quotes():
            # Extrair simbolos validos da b3
            valid_symbols = [a.ticker for a in self.ativos if a.tipo in (TipoAtivo.ACAO, TipoAtivo.FII, TipoAtivo.ETF) and a.ticker]
            if not valid_symbols:
                rebal_row.controls = [
                    _rebal_box("▲ AUMENTAR POSIÇÃO", GREEN_BG, GREEN_PRIMARY, GREEN_DARK, ["Renda fixa oportuna"]),
                    _rebal_box("◆ MANTER COMO ESTÁ", NEUTRAL_BG, NEUTRAL_DARK, NEUTRAL_DARK, ["Tudo sob controle"]),
                    _rebal_box("▼ REDUZIR OU SAIR", RED_BG, RED_PRIMARY, RED_DARK, ["Nenhuma variável"]),
                ]
                rebal_row.update()
                return

            quotes = get_quotes(valid_symbols)
            comprar = []
            manter = []
            vender = []

            for ativo in self.ativos:
                if ativo.ticker in valid_symbols:
                    q = next((x for x in quotes if x.symbol == ativo.ticker), None)
                    if q and q.price:
                        # Atualizar preco em runtime para display
                        ativo.preco_atual = q.price
                        # Atualizar calculo basico usando as properties calculadas
                        if ativo.quantidade > 0:
                            if q.pe_ratio and q.pe_ratio < 10:
                                ativo.sinal = Sinal.COMPRA
                                comprar.append(f"{ativo.ticker} (Abaixo Preço/Lucro)")
                            elif q.pe_ratio and q.pe_ratio > 25:
                                ativo.sinal = Sinal.VENDA
                                vender.append(f"{ativo.ticker} (Acima Preço/Lucro)")
                            elif ativo.pl_percentual > 30:
                                ativo.sinal = Sinal.VENDA
                                vender.append(f"{ativo.ticker} (Realizar lucro)")
                            elif ativo.pl_percentual < -20:
                                ativo.sinal = Sinal.COMPRA
                                comprar.append(f"{ativo.ticker} (Preço descontado)")
                            else:
                                ativo.sinal = Sinal.MANTER
                                manter.append(f"{ativo.ticker}")
                        else:
                            ativo.sinal = Sinal.MANTER
                            manter.append(f"{ativo.ticker}")
                            
            if not comprar: comprar.append("Nenhum")
            if not manter: manter.append("Nenhum")
            if not vender: vender.append("Nenhum")

            rebal_row.controls = [
                _rebal_box("▲ AUMENTAR POSIÇÃO", GREEN_BG, GREEN_PRIMARY, GREEN_DARK, comprar),
                _rebal_box("◆ MANTER COMO ESTÁ", NEUTRAL_BG, NEUTRAL_DARK, NEUTRAL_DARK, manter),
                _rebal_box("▼ REDUZIR OU SAIR", RED_BG, RED_PRIMARY, RED_DARK, vender),
            ]
            
            # Recriar os rows e atualizar via update do control
            tabela_dt.rows = [self._build_row(a) for a in self.ativos]
            
            try:
                tabela_dt.update()
                rebal_row.update()
            except Exception:
                pass # pode ocorrer se a pagina ja tiver sido destruida antes do thread terminar

        threading.Thread(target=update_quotes, daemon=True).start()

        return ft.Column(
            [
                resumo,
                ft.Row(
                    [alocacao, performance],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                tabela_ativos,
                rebal,
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )

    # ── Helpers ───────────────────────────────────────────────

    def _mini_card(self, label: str, valor: str,
                   sub: str, positivo) -> ft.Container:
        from theme import GREEN_PRIMARY, RED_PRIMARY, NEUTRAL_TEXT
        sub_cor = (GREEN_PRIMARY if positivo is True
                   else RED_PRIMARY if positivo is False
                   else NEUTRAL_TEXT)
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(label, size=FONT_SIZE_XS, color=TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text(valor, size=FONT_SIZE_XL,
                            weight=ft.FontWeight.W_500, color=TEXT_PRIMARY,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text(sub, size=FONT_SIZE_XS, color=sub_cor,
                            text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            bgcolor=BG_PRIMARY,
            border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
            border_radius=ft.BorderRadius.all(10),
            padding=PAD_MD,
            expand=True,
        )

    def _perf_mini(self, valor: str, label: str) -> ft.Container:
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(valor, size=FONT_SIZE_XL,
                            weight=ft.FontWeight.W_500,
                            color=GREEN_PRIMARY,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text(label, size=FONT_SIZE_XS,
                            color=TEXT_SECONDARY,
                            text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ),
            expand=True,
        )



