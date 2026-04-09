"""
views/acoes.py
Aba Ações — tabela dinâmica via screener (yfinance).
"""

import flet as ft
import threading
from theme import (
    BG_PRIMARY, BG_SECONDARY, BORDER_COLOR, BORDER_WIDTH,
    GREEN_PRIMARY, RED_PRIMARY, YELLOW_PRIMARY, NEUTRAL_TEXT,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY,
    FONT_SIZE_XS, FONT_SIZE_SM, FONT_SIZE_MD, PAD_MD,
)
from components.badge import badge_sinal
from services.screener import get_quotes, get_top_dynamic, analyze_asset

def _vc(ok) -> str:
    if ok is True:  return GREEN_PRIMARY
    if ok is False: return RED_PRIMARY
    return NEUTRAL_TEXT

def _score_bar(score: int) -> ft.Row:
    color = GREEN_PRIMARY if score >= 70 else (YELLOW_PRIMARY if score >= 45 else RED_PRIMARY)
    return ft.Row([
        ft.Stack([
            ft.Container(width=60, height=6, bgcolor=BG_SECONDARY,
                         border_radius=ft.BorderRadius.all(3)),
            ft.Container(width=max(2, score * 0.6), height=6, bgcolor=color,
                         border_radius=ft.BorderRadius.all(3)),
        ]),
        ft.Text(str(score), size=FONT_SIZE_XS, color=color,
                weight=ft.FontWeight.W_500),
    ], spacing=6)

def build_acoes() -> ft.Column:
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
                    # Se o usuario digitou, bota ele na lista
                    symbol = q.upper() if q.upper().endswith(".SA") else f"{q.upper()}.SA"
                    assets = get_quotes([symbol])
                else:
                    # Traz de forma dinamicamente descoberta e ao vivo!
                    assets = get_top_dynamic('stock', limit=20)
                    
                rows = []
                for a in assets:
                    if not a.price:
                        continue # Ignora se não encontrou o ticker

                    # Mocking fundamentalist scores and signals since yfinance doesn't provide them all
                    pe_ratio = f"{a.pe_ratio:.1f}x" if a.pe_ratio else "—"
                    dy = f"{a.dividend_yield*100:.1f}%" if a.dividend_yield else "—"
                    
                    s_fund, s_tech, sinal = analyze_asset(a)
                    
                    rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(a.symbol.replace(".SA",""), size=FONT_SIZE_MD, weight=ft.FontWeight.W_500)),
                            ft.DataCell(ft.Text(f"R$ {a.price:.2f}" if a.price else "—", size=FONT_SIZE_SM)),
                            ft.DataCell(ft.Text(pe_ratio, size=FONT_SIZE_SM, color=_vc(a.pe_ratio and 0 < a.pe_ratio < 15))),
                            ft.DataCell(ft.Text("—", size=FONT_SIZE_SM, color=NEUTRAL_TEXT)), # PVP not in yfinance easily
                            ft.DataCell(ft.Text(dy, size=FONT_SIZE_SM, color=GREEN_PRIMARY)),
                            ft.DataCell(ft.Text("—", size=FONT_SIZE_SM)), # ROE 
                            ft.DataCell(ft.Text("—", size=FONT_SIZE_SM, color=NEUTRAL_TEXT)), # Div
                            ft.DataCell(_score_bar(s_fund)), 
                            ft.DataCell(_score_bar(s_tech)), 
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
        hint_text="Buscar ticker (ex: PETR4, VALE3...)",
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
            ft.DataColumn(ft.Text("Ticker",     size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("Preço",      size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("P/L",        size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("P/VP",       size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("DY 12m",     size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("ROE",        size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("Dív/PL",     size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("Score Fund.",size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("Score Téc.", size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
            ft.DataColumn(ft.Text("Sinal",      size=FONT_SIZE_XS, color=TEXT_TERTIARY)),
        ],
        rows=[],
        border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
        border_radius=ft.BorderRadius.all(10),
        horizontal_lines=ft.BorderSide(BORDER_WIDTH, BORDER_COLOR),
        heading_row_color=BG_SECONDARY,
        column_spacing=16,
    )

    col = ft.Column(
        [
            ft.Row([
                search,
                ft.FilledButton(
                    "Analisar ↗",
                    style=ft.ButtonStyle(bgcolor=GREEN_PRIMARY, color="white"),
                    on_click=on_analisar
                ),
            ], spacing=8),
            ft.Container(
                content=ft.Column([
                    ft.Text("Ações — Análise via Yahoo Finance",
                            size=FONT_SIZE_MD, weight=ft.FontWeight.W_500),
                    ft.Text("P/VP, ROE e Dív/PL não suportados via YFinance nesta versão.",
                            size=FONT_SIZE_XS, color=TEXT_TERTIARY),
                    ft.ProgressRing(ref=loading_ref, width=16, height=16, stroke_width=2, color=GREEN_PRIMARY, visible=False),
                    ft.Container(content=tabela,
                                 clip_behavior=ft.ClipBehavior.HARD_EDGE),
                ], spacing=10),
                bgcolor=BG_PRIMARY,
                border=ft.Border.all(BORDER_WIDTH, BORDER_COLOR),
                border_radius=ft.BorderRadius.all(10),
                padding=PAD_MD,
            ),
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
    )
    
    # Auto load the first time
    threading.Timer(0.1, on_analisar).start()
    return col
