"""
views/fiis.py
Aba FIIs — tabela dinâmica via screener (yfinance).
"""

import flet as ft
import threading
from theme import (
    BG_PRIMARY, BG_SECONDARY, BORDER_COLOR, BORDER_WIDTH,
    GREEN_PRIMARY, RED_PRIMARY, YELLOW_PRIMARY, NEUTRAL_TEXT,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY,
    FONT_SIZE_XS, FONT_SIZE_SM, FONT_SIZE_MD,
    PAD_MD, PAD_SM,
)
from components.badge import badge_sinal
from services.screener import get_quotes, get_top_dynamic, analyze_asset

def _val_color(ok) -> str:
    if ok is True:  return GREEN_PRIMARY
    if ok is False: return RED_PRIMARY
    return NEUTRAL_TEXT


def _score_bar(score: int) -> ft.Row:
    if score >= 70:   color = GREEN_PRIMARY
    elif score >= 45: color = YELLOW_PRIMARY
    else:             color = RED_PRIMARY
    return ft.Row(
        [
            ft.Container(
                content=ft.Container(
                    width=score * 0.5, height=6, bgcolor=color,
                    border_radius=ft.BorderRadius.all(3),
                ),
                width=50, height=6, bgcolor=BG_SECONDARY,
                border_radius=ft.BorderRadius.all(3),
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            ),
            ft.Text(str(score), size=FONT_SIZE_XS,
                    color=color, weight=ft.FontWeight.W_500),
        ],
        spacing=6,
    )


def build_fiis() -> ft.Column:
    search_ref = ft.Ref[ft.TextField]()
    tabela_ref = ft.Ref[ft.DataTable]()
    loading_ref = ft.Ref[ft.ProgressRing]()

    def on_analisar(_=None):
        q = search_ref.current.value.strip()
        loading_ref.current.visible = True
        tabela_ref.current.rows.clear()
        tabela_ref.current.update()
        loading_ref.current.update()
        
        def _fetch():
            try:
                if q:
                    symbol = q.upper() if q.upper().endswith("11.SA") else f"{q.upper()}11.SA"
                    assets = get_quotes([symbol])
                else:
                    assets = get_top_dynamic('fii', limit=20)
                    
                rows = []
                for a in assets:
                    if not a.price: continue
                    
                    dy = f"{a.dividend_yield*100:.1f}%" if a.dividend_yield else "—"
                    vol = f"R$ {a.volume/1e6:.1f}M" if a.volume and a.volume > 1e6 else (f"{a.volume}" if a.volume else "—")
                    
                    s_fund, s_tech, sinal = analyze_asset(a)

                    rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(a.symbol.replace(".SA",""), size=FONT_SIZE_MD, weight=ft.FontWeight.W_500)),
                            ft.DataCell(ft.Text("—", size=FONT_SIZE_SM, color=TEXT_SECONDARY)), # Segmento not guaranteed
                            ft.DataCell(ft.Text(f"R$ {a.price:.2f}" if a.price else "—", size=FONT_SIZE_SM)),
                            ft.DataCell(ft.Text("—", size=FONT_SIZE_SM, color=NEUTRAL_TEXT)), # PVP 
                            ft.DataCell(ft.Text(dy, size=FONT_SIZE_SM, color=GREEN_PRIMARY)),
                            ft.DataCell(ft.Text("—", size=FONT_SIZE_SM, color=NEUTRAL_TEXT)), # Vacancia missing
                            ft.DataCell(ft.Text("—", size=FONT_SIZE_SM)), # Ultimo rend missing
                            ft.DataCell(ft.Text(vol, size=FONT_SIZE_SM)), # Liquidez
                            ft.DataCell(_score_bar(s_fund)), 
                            ft.DataCell(badge_sinal(sinal)),
                        ])
                    )
                tabela_ref.current.rows = rows
            except Exception as e:
                print(f"Erro ao buscar ativos: {e}")
            finally:
                loading_ref.current.visible = False
                try:
                    tabela_ref.current.update()
                    loading_ref.current.update()
                    if tabela_ref.current.page:
                        tabela_ref.current.page.update()
                except:
                    pass
                
        threading.Thread(target=_fetch, daemon=True).start()

    search = ft.TextField(
        ref=search_ref,
        hint_text="Buscar FII (ex: MXRF11, HGLG11...)",
        prefix_icon=ft.Icons.SEARCH,
        bgcolor=BG_PRIMARY,
        border_color=BORDER_COLOR,
        border_radius=ft.BorderRadius.all(8),
        text_size=FONT_SIZE_SM,
        expand=True,
        height=44,
        on_submit=on_analisar
    )

    tabela = ft.DataTable(
        ref=tabela_ref,
        columns=[
            ft.DataColumn(ft.Text("Ticker",       size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("Segmento",     size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("Preço",        size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("P/VP",         size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("DY 12m",       size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("Vacância",     size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("Último Rend.", size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("Liquidez/dia", size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("Score",        size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("Sinal",        size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
        ],
        rows=[],
        border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
        border_radius=ft.BorderRadius.all(10),
        horizontal_lines=ft.BorderSide(BORDER_WIDTH, BORDER_COLOR),
        heading_row_color=BG_SECONDARY,
        column_spacing=12,
    )

    # Legenda P/VP
    def _leg(cor, label, val):
        return ft.Row(
            [
                ft.Container(width=8, height=8, bgcolor=cor,
                             border_radius=ft.BorderRadius.all(4)),
                ft.Text(label, size=FONT_SIZE_SM, color=TEXT_PRIMARY, expand=True),
                ft.Text(val, size=FONT_SIZE_SM,
                        color=GREEN_PRIMARY if "tim" in val.lower() or "bom" in val.lower()
                        else (RED_PRIMARY if "vitar" in val.lower() else YELLOW_PRIMARY)),
            ],
            spacing=8,
        )

    legenda_pvp = ft.Container(
        content=ft.Column(
            [
                ft.Text("Critério P/VP — FIIs", size=FONT_SIZE_XS,
                        color=TEXT_TERTIARY, style=ft.TextStyle(letter_spacing=1.5)),
                _leg(GREEN_PRIMARY, "P/VP < 0,95 — desconto", "Ótimo"),
                _leg(GREEN_PRIMARY, "P/VP 0,95–1,05", "Bom"),
                _leg(YELLOW_PRIMARY, "P/VP 1,05–1,20", "Neutro"),
                _leg(RED_PRIMARY, "P/VP > 1,20 — prêmio alto", "Evitar"),
            ],
            spacing=8,
        ),
        bgcolor=BG_PRIMARY,
        border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
        border_radius=ft.BorderRadius.all(10),
        padding=PAD_MD,
        expand=True,
    )

    col = ft.Column(
        [
            ft.Row([search,
                    ft.FilledButton("Analisar FII ↗",
                                      style=ft.ButtonStyle(bgcolor="#0F6E56", color="#9FE1CB", shape=ft.RoundedRectangleBorder(radius=8)),
                                      on_click=on_analisar)],
                   spacing=8),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("FIIs — Dados extraídos via YFinance",
                                size=FONT_SIZE_MD, weight=ft.FontWeight.W_500),
                        ft.Text("P/VP, Vacância e Segmento muitas vezes indisponíveis na versão atual da API.",
                                size=FONT_SIZE_XS, color=TEXT_TERTIARY),
                        ft.ProgressRing(ref=loading_ref, width=16, height=16, stroke_width=2, color=GREEN_PRIMARY, visible=False),
                        ft.Container(content=tabela,
                                     clip_behavior=ft.ClipBehavior.HARD_EDGE),
                    ],
                    spacing=10,
                ),
                bgcolor=BG_PRIMARY,
                border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
                border_radius=ft.BorderRadius.all(10),
                padding=PAD_MD,
            ),
            legenda_pvp,
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
    )

    threading.Timer(0.1, on_analisar).start()
    return col
