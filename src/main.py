"""
main.py  —  InvestLab ponto de entrada.

Modal de cadastro implementado como Stack overlay (não AlertDialog),
pois AlertDialog em Flet 0.80+ não propaga eventos de clique corretamente
para controles internos com scroll.
"""

from __future__ import annotations
import sys, os

sys.path.insert(0, os.path.dirname(__file__))

import flet as ft

from theme import (
    BG_TERTIARY, GREEN_DARK, GREEN_PRIMARY,
    TEXT_PRIMARY, TEXT_TERTIARY, FONT_SIZE_SM,
    BG_PRIMARY, BORDER_COLOR,
)
from models.ativo import Ativo
from services.storage import StorageService
from components.top_bar import top_bar
from components.nav_bar import nav_bar
from views.visao_geral import build_visao_geral
from views.acoes       import build_acoes
from views.fiis        import build_fiis
from views.renda_fixa  import build_renda_fixa
from views.macro       import build_macro
from views.carteira    import CarteiraView
from views.cadastro    import CadastroForm


class InvestLabApp:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self._storage = StorageService()
        self._ativos: list[Ativo] = []
        self._aba_atual: int = 0
        self._nav = None
        self._content_area = None
        # Overlay de cadastro (Stack, não AlertDialog)
        self._overlay_stack: ft.Stack | None = None

        self._setup_page()
        self._ativos = self._storage.carregar_carteira()
        self._build_ui()

    # ── Configuração ──────────────────────────────────────────

    def _setup_page(self) -> None:
        p = self.page
        p.title = "InvestLab — Painel de Decisão"
        p.theme_mode = ft.ThemeMode.LIGHT
        p.bgcolor = BG_TERTIARY
        p.padding = 0
        p.scroll = ft.ScrollMode.HIDDEN

        try:
            if p.platform in (
                ft.PagePlatform.WINDOWS,
                ft.PagePlatform.MACOS,
                ft.PagePlatform.LINUX,
            ):
                p.window.width      = 1100
                p.window.height     = 780
                p.window.min_width  = 900
                p.window.min_height = 600
        except Exception:
            pass

    # ── UI principal ──────────────────────────────────────────

    def _build_ui(self) -> None:
        self._nav = nav_bar(on_change=self._mudar_aba)
        self._content_area = ft.Column(
            [self._build_aba(0)],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        self.page.add(
            ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                top_bar(),
                                ft.Container(
                                    content=self._content_area,
                                    expand=True,
                                ),
                            ],
                            spacing=0,
                            expand=True,
                        ),
                        padding=ft.Padding.symmetric(horizontal=12, vertical=12),
                        expand=True,
                    ),
                    self._nav,
                ],
                spacing=0,
                expand=True,
            )
        )

    def _build_aba(self, index: int) -> ft.Control:
        builders = {
            0: build_visao_geral,
            1: build_acoes,
            2: build_fiis,
            3: build_renda_fixa,
            4: build_macro,
            5: self._build_carteira,
        }
        fn = builders.get(index)
        return fn() if fn else ft.Text("Aba não encontrada", color=TEXT_TERTIARY)

    def _build_carteira(self) -> ft.Control:
        return CarteiraView(
            ativos=self._ativos,
            on_adicionar=self._abrir_cadastro,
            on_editar=self._abrir_edicao,
            on_excluir=self._excluir_ativo,
        ).build()

    # ── Navegação ─────────────────────────────────────────────

    def _mudar_aba(self, index: int) -> None:
        self._aba_atual = index
        self._content_area.controls = [self._build_aba(index)]
        self._content_area.update()

    # ── Modal de cadastro via Stack overlay ───────────────────
    # AlertDialog não propaga eventos corretamente em Flet 0.80+
    # quando o conteúdo tem scroll. Usamos Stack direto no page.overlay.

    def _abrir_cadastro(self) -> None:
        self._abrir_form(None)

    def _abrir_edicao(self, ativo: Ativo) -> None:
        self._abrir_form(ativo)

    def _abrir_form(self, ativo_editar) -> None:
        form = CadastroForm(
            on_salvar=self._salvar_ativo,
            on_cancelar=self._fechar_form,
            ativo_editar=ativo_editar,
            page=self.page,
        )

        # Fundo escurecido clicável para fechar
        backdrop = ft.Container(
            expand=True,
            bgcolor="#00000066",          # preto 40% opacidade
            on_click=lambda e: self._fechar_form(),
        )

        # form.build() já retorna um ft.Stack com o card arrastável posicionado
        form_stack = form.build()

        # Stack geral: backdrop embaixo, form arrastável em cima
        self._overlay_stack = ft.Stack(
            [backdrop, form_stack],
            expand=True,
        )

        self.page.overlay.append(self._overlay_stack)
        self.page.update()

    def _fechar_form(self) -> None:
        if self._overlay_stack and self._overlay_stack in self.page.overlay:
            self.page.overlay.remove(self._overlay_stack)
            self._overlay_stack = None
            self.page.update()

    # ── Salvar / Excluir ──────────────────────────────────────

    def _salvar_ativo(self, ativo: Ativo) -> None:
        self._ativos = self._storage.salvar_ativo(ativo, self._ativos)
        self._fechar_form()
        if self._aba_atual == 5:
            self._mudar_aba(5)
        self._snack("Ativo salvo com sucesso! ✓", GREEN_PRIMARY)

    def _excluir_ativo(self, ativo_id: str) -> None:
        def _close():
            self.page.close(dlg)

        def _ok(e):
            _close()
            self._ativos = self._storage.excluir_ativo(ativo_id, self._ativos)
            if self._aba_atual == 5:
                self._mudar_aba(5)
            self._snack("Ativo removido.", TEXT_TERTIARY)

        def _no(e):
            _close()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar exclusão",
                          size=FONT_SIZE_SM, weight=ft.FontWeight.W_600),
            content=ft.Text(
                "Remover este ativo da carteira?\nEsta ação não pode ser desfeita.",
                size=FONT_SIZE_SM, color=TEXT_TERTIARY,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=_no),
                ft.FilledButton(
                    "Remover",
                    style=ft.ButtonStyle(bgcolor="#E24B4A", color="white"),
                    on_click=_ok,
                ),
            ],
        )
        self.page.open(dlg)

    # ── Helpers ───────────────────────────────────────────────

    def _snack(self, msg: str, cor: str) -> None:
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="white", size=FONT_SIZE_SM),
            bgcolor=cor,
            duration=2500,
        )
        self.page.snack_bar.open = True
        self.page.update()


# ─────────────────────────────────────────────────────────────────────
def main(page: ft.Page) -> None:
    InvestLabApp(page)


if __name__ == "__main__":
    ft.run(main)
