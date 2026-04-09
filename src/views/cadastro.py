"""
views/cadastro.py
Formulário de Cadastro de Ativo — 5 seções.
Compatível com Flet 0.80+.
"""

from __future__ import annotations
import uuid
from datetime import date, datetime
from typing import Callable, Optional

import flet as ft

from models.ativo import (
    Ativo, TipoAtivo, TipoRentabilidade, Objetivo,
    HorizonteInvestimento, Liquidez, Corretora, Sinal,
)
from theme import (
    BG_PRIMARY, BG_SECONDARY, BORDER_COLOR, BORDER_WIDTH,
    GREEN_PRIMARY, GREEN_DARK, GREEN_BG, GREEN_LIGHT,
    RED_PRIMARY, YELLOW_BG, YELLOW_DARK, YELLOW_BORDER,
    BLUE_BG, BLUE_BORDER, BLUE_PRIMARY,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_TERTIARY,
    FONT_SIZE_XS, FONT_SIZE_SM, FONT_SIZE_MD, FONT_SIZE_LG,
    PAD_MD, PAD_SM, PAD_XS,
)

_RF_TIPOS  = {TipoAtivo.CDB, TipoAtivo.LCI_LCA, TipoAtivo.TESOURO, TipoAtivo.DEBENT}
_VAR_TIPOS = {TipoAtivo.ACAO, TipoAtivo.FII, TipoAtivo.ETF}


# ── Helpers de UI ─────────────────────────────────────────────────────

def _section_header(num: str, titulo: str) -> ft.Row:
    return ft.Row([
        ft.Container(
            content=ft.Text(num, size=FONT_SIZE_XS, color="white",
                            weight=ft.FontWeight.W_600),
            width=20, height=20,
            bgcolor=GREEN_DARK,
            border_radius=ft.BorderRadius.all(10),
            alignment=ft.alignment.Alignment(0, 0),
        ),
        ft.Text(titulo.upper(), size=FONT_SIZE_XS,
                weight=ft.FontWeight.W_600, color=TEXT_PRIMARY,
                style=ft.TextStyle(letter_spacing=1)),
    ], spacing=8)


def _divider() -> ft.Divider:
    return ft.Divider(height=1, color=BORDER_COLOR, thickness=0.5)


def _info_box(texto: str, estilo: str = "blue") -> ft.Container:
    cores = {
        "blue":   (BLUE_BG,   BLUE_BORDER,   BLUE_PRIMARY),
        "yellow": (YELLOW_BG, YELLOW_BORDER, YELLOW_DARK),
        "green":  (GREEN_BG,  GREEN_PRIMARY,  GREEN_DARK),
    }
    bg, border, fg = cores.get(estilo, cores["blue"])
    return ft.Container(
        content=ft.Row([
            ft.Text("ℹ", size=14, color=fg),
            ft.Text(texto, size=FONT_SIZE_XS, color=fg, expand=True),
        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.START),
        bgcolor=bg,
        border=ft.Border.all(0.5, border),
        border_radius=ft.BorderRadius.all(8),
        padding=ft.Padding.symmetric(horizontal=PAD_MD, vertical=10),
        margin=ft.Margin.only(bottom=10),
    )


def _field(label: str, control: ft.Control,
           hint: str = "", required: bool = False) -> ft.Column:
    lbl = label + (" *" if required else "")
    children: list[ft.Control] = [
        ft.Text(lbl, size=FONT_SIZE_XS, color=TEXT_SECONDARY,
                weight=ft.FontWeight.W_500),
        control,
    ]
    if hint:
        children.append(ft.Text(hint, size=FONT_SIZE_XS, color=TEXT_TERTIARY))
    return ft.Column(children, spacing=4)


def _tf(hint: str = "", value: str = "",
        keyboard=ft.KeyboardType.TEXT,
        on_change=None, read_only: bool = False) -> ft.TextField:
    """TextField com estilo padrão InvestLab."""
    return ft.TextField(
        value=value,
        hint_text=hint,
        text_size=FONT_SIZE_SM,
        border_color=BORDER_COLOR,
        focused_border_color=GREEN_PRIMARY,
        border_radius=ft.BorderRadius.all(8),
        border_width=BORDER_WIDTH,
        height=42,
        content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
        keyboard_type=keyboard,
        on_change=on_change,
        read_only=read_only,
        bgcolor=BG_SECONDARY if read_only else BG_PRIMARY,
    )


def _dd(options: list[str], value: str = "") -> ft.Dropdown:
    """Dropdown minimal — compatível com Flet 0.80+."""
    return ft.Dropdown(
        options=[ft.dropdown.Option(o) for o in options],
        value=value or (options[0] if options else None),
        text_size=FONT_SIZE_SM,
        border_color=BORDER_COLOR,
        focused_border_color=GREEN_PRIMARY,
        border_width=BORDER_WIDTH,
    )


def _btn_tipo(label: str, selected: bool,
              on_click) -> ft.Container:
    """Botão de seleção de tipo de ativo."""
    bg     = GREEN_BG      if selected else BG_SECONDARY
    fg     = GREEN_DARK    if selected else TEXT_SECONDARY
    border = GREEN_PRIMARY if selected else BORDER_COLOR
    return ft.Container(
        content=ft.Text(label, size=FONT_SIZE_XS,
                        color=fg, weight=ft.FontWeight.W_500),
        bgcolor=bg,
        border=ft.Border.all(0.5, border),
        border_radius=ft.BorderRadius.all(6),
        padding=ft.Padding.symmetric(horizontal=PAD_SM, vertical=PAD_XS + 2),
        on_click=on_click,
    )


# ═══════════════════════════════════════════════════════════════════════
class CadastroForm:
    """Formulário completo de cadastro/edição de ativo."""

    def __init__(
        self,
        on_salvar: Callable[[Ativo], None],
        on_cancelar: Callable,
        ativo_editar: Optional[Ativo] = None,
        page=None,
    ) -> None:
        self.on_salvar   = on_salvar
        self.on_cancelar = on_cancelar
        self._page       = page          # referência à page para update()
        self._editando   = ativo_editar is not None
        self._ativo      = ativo_editar or Ativo()
        self._tipo       = self._ativo.tipo
        # Estado de posição para drag
        self._drag_x: float = 0.0
        self._drag_y: float = 0.0
        self._card_ref: Optional[ft.Container] = None

        a = self._ativo

        # ── Identificação ────────────────────────────────────
        self._ticker  = _tf("Ex: PETR4", a.ticker)
        self._nome    = _tf("Ex: Petrobras PN", a.nome)
        self._setor   = _dd(
            [""] + [
                "Petróleo & Gás", "Mineração", "Bancário / Financeiro",
                "Varejo", "Indústria / Manufatura", "Energia Elétrica",
                "Saneamento", "Tecnologia", "Saúde / Farmacêutico",
                "Agronegócio", "Construção Civil", "Transporte / Logística",
                "Telecomunicações",
                "FII — Papel / CRI", "FII — Logística / Galpões",
                "FII — Lajes Corporativas", "FII — Shopping",
                "FII — Híbrido", "FII — Residencial",
            ],
            a.setor,
        )
        self._emissor     = _tf("Ex: Banco Inter, BTG...", a.emissor)
        self._tipo_rent   = _dd([t.value for t in TipoRentabilidade],
                                a.tipo_rentabilidade.value)
        self._taxa        = _tf("Ex: 112", str(a.taxa_contratada or ""),
                                keyboard=ft.KeyboardType.NUMBER)
        self._tributacao  = _dd(
            ["IR Regressivo (CDB / Tesouro)",
             "Isento IR (LCI / LCA)",
             "IR 15% (Debenture incentivada)"],
            a.tributacao,
        )
        self._fgc = _dd(
            ["Sim — coberto até R$ 250.000", "Não — sem cobertura FGC"],
            "Sim — coberto até R$ 250.000" if a.cobertura_fgc else "Não — sem cobertura FGC",
        )
        self._cnpj    = _tf("00.000.000/0000-00", a.cnpj_fundo)

        # ── Compra ───────────────────────────────────────────
        self._data_compra  = _tf("AAAA-MM-DD",
                                 a.data_compra.isoformat() if a.data_compra else date.today().isoformat(),
                                 keyboard=ft.KeyboardType.DATETIME)
        self._quantidade   = _tf("Ex: 100",
                                 str(int(a.quantidade)) if a.quantidade else "",
                                 keyboard=ft.KeyboardType.NUMBER,
                                 on_change=self._recalc)
        self._preco_compra = _tf("0,00",
                                 f"{a.preco_compra:.2f}" if a.preco_compra else "",
                                 keyboard=ft.KeyboardType.NUMBER,
                                 on_change=self._recalc)
        self._valor_total  = _tf("Calculado automaticamente",
                                 f"{a.valor_total:.2f}" if a.valor_total else "",
                                 keyboard=ft.KeyboardType.NUMBER)
        self._corretagem   = _tf("0,00",
                                 f"{a.corretagem:.2f}" if a.corretagem else "",
                                 keyboard=ft.KeyboardType.NUMBER)
        self._corretora    = _dd([c.value for c in Corretora], a.corretora.value)
        self._tipo_op      = _dd(
            ["Compra normal", "Aporte adicional",
             "Transferência de custódia",
             "Bonificação / Desdobramento", "Subscrição"],
            a.tipo_operacao,
        )
        self._data_venc = _tf("AAAA-MM-DD",
                              a.data_vencimento.isoformat() if a.data_vencimento else "",
                              keyboard=ft.KeyboardType.DATETIME)
        self._liquidez  = _dd([l.value for l in Liquidez], a.liquidez.value)

        # ── Gestão ───────────────────────────────────────────
        self._objetivo  = _dd([o.value for o in Objetivo], a.objetivo.value)
        self._horizonte = _dd([h.value for h in HorizonteInvestimento],
                              a.horizonte.value)
        self._stop_loss  = _tf("Ex: 30,00",
                               f"{a.stop_loss:.2f}" if a.stop_loss else "",
                               keyboard=ft.KeyboardType.NUMBER)
        self._alvo_preco = _tf("Ex: 50,00",
                               f"{a.alvo_preco:.2f}" if a.alvo_preco else "",
                               keyboard=ft.KeyboardType.NUMBER)
        self._max_cart   = _tf("Ex: 10",
                               f"{a.max_carteira:.0f}" if a.max_carteira else "",
                               keyboard=ft.KeyboardType.NUMBER)
        self._tags  = _tf("dividendos, longo prazo...", ", ".join(a.tags))
        self._notas = ft.TextField(
            value=a.notas,
            hint_text="Tese de investimento, motivo da compra, gatilhos de saída...",
            text_size=FONT_SIZE_SM,
            border_color=BORDER_COLOR,
            focused_border_color=GREEN_PRIMARY,
            border_width=BORDER_WIDTH,
            multiline=True,
            min_lines=3, max_lines=5,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=8),
        )

        # ── Rendimentos ──────────────────────────────────────
        self._dividendos = _tf("0,00",
                               f"{a.dividendos_recebidos:.2f}" if a.dividendos_recebidos else "",
                               keyboard=ft.KeyboardType.NUMBER)
        self._ult_rend   = _tf("0,00",
                               f"{a.ultimo_rendimento:.2f}" if a.ultimo_rendimento else "",
                               keyboard=ft.KeyboardType.NUMBER)
        self._reinvestir = _dd(
            ["Não — manter como caixa",
             "Sim — reinvestir neste ativo",
             "Sim — reinvestir em outro ativo"],
            a.reinvestir,
        )

        # ── Painéis dinâmicos ─────────────────────────────────
        self._painel_rv   = ft.Column(visible=self._tipo in _VAR_TIPOS)
        self._painel_rf   = ft.Column(visible=self._tipo in _RF_TIPOS)
        self._painel_venc = ft.Column(visible=self._tipo in _RF_TIPOS)
        self._qtd_row     = ft.Column(visible=self._tipo in _VAR_TIPOS)

        self._tipo_btns: dict[TipoAtivo, ft.Container] = {}
        self._erros = ft.Text("", size=FONT_SIZE_SM, color=RED_PRIMARY)

    # ── Eventos ───────────────────────────────────────────────

    def _recalc(self, e=None):
        try:
            q = float(self._quantidade.value or 0)
            p = float(self._preco_compra.value or 0)
            if q > 0 and p > 0:
                self._valor_total.value = f"{q * p:.2f}"
                if self._page:
                    self._page.update()
        except (ValueError, TypeError):
            pass

    def _set_tipo(self, tipo: TipoAtivo, e=None):
        self._tipo = tipo
        # atualizar aparência dos botões
        for t, btn in self._tipo_btns.items():
            sel = (t == tipo)
            btn.bgcolor = GREEN_BG if sel else BG_SECONDARY
            btn.border  = ft.Border.all(0.5, GREEN_PRIMARY if sel else BORDER_COLOR)
            if btn.content:
                btn.content.color = GREEN_DARK if sel else TEXT_SECONDARY
        # mostrar/ocultar painéis
        self._painel_rv.visible   = tipo in _VAR_TIPOS
        self._painel_rf.visible   = tipo in _RF_TIPOS
        self._painel_venc.visible = tipo in _RF_TIPOS
        self._qtd_row.visible     = tipo in _VAR_TIPOS
        # Uma única chamada page.update() é mais confiável
        if self._page:
            self._page.update()

    def _validar(self) -> bool:
        erros = []
        if self._tipo in _VAR_TIPOS and not (self._ticker.value or "").strip():
            erros.append("Ticker obrigatório para ações, FIIs e ETFs.")
        if self._tipo in _RF_TIPOS and not (self._emissor.value or "").strip():
            erros.append("Instituição emissora obrigatória.")
        try:
            float(self._valor_total.value or 0)
        except ValueError:
            erros.append("Valor total deve ser numérico.")
        self._erros.value = "  ·  ".join(erros)
        if self._page:
            self._page.update()
        return len(erros) == 0

    # ── Helpers de conversão ──────────────────────────────────

    @staticmethod
    def _to_float(value, default: float = 0.0) -> float:
        """Converte string para float aceitando vírgula ou ponto como decimal."""
        try:
            return float(str(value).strip().replace(".", "").replace(",", ".")) if value else default
        except (ValueError, TypeError):
            return default

    def _coletar(self) -> Ativo:
        a = self._ativo
        a.id     = a.id or str(uuid.uuid4())
        a.tipo   = self._tipo
        a.ticker = (self._ticker.value or "").strip().upper()
        a.nome   = (self._nome.value or "").strip()
        a.setor  = self._setor.value or ""
        a.emissor = (self._emissor.value or "").strip()
        a.cnpj_fundo = (self._cnpj.value or "").strip()
        for tr in TipoRentabilidade:
            if tr.value == self._tipo_rent.value:
                a.tipo_rentabilidade = tr; break
        a.taxa_contratada = self._to_float(self._taxa.value)
        a.tributacao = self._tributacao.value or "IR Regressivo"
        a.cobertura_fgc = "Sim" in (self._fgc.value or "")
        try:
            a.data_compra = date.fromisoformat(self._data_compra.value)
        except Exception:
            a.data_compra = date.today()
        a.quantidade   = self._to_float(self._quantidade.value)
        a.preco_compra = self._to_float(self._preco_compra.value)
        a.valor_total  = self._to_float(self._valor_total.value)
        a.corretagem   = self._to_float(self._corretagem.value)
        a.tipo_operacao = self._tipo_op.value or "Compra normal"
        for c in Corretora:
            if c.value == self._corretora.value:
                a.corretora = c; break
        try:
            a.data_vencimento = date.fromisoformat(self._data_venc.value) if self._data_venc.value else None
        except Exception:
            a.data_vencimento = None
        for lq in Liquidez:
            if lq.value == self._liquidez.value:
                a.liquidez = lq; break
        for obj in Objetivo:
            if obj.value == self._objetivo.value:
                a.objetivo = obj; break
        for h in HorizonteInvestimento:
            if h.value == self._horizonte.value:
                a.horizonte = h; break
        a.stop_loss    = self._to_float(self._stop_loss.value)  if self._stop_loss.value  else None
        a.alvo_preco   = self._to_float(self._alvo_preco.value) if self._alvo_preco.value else None
        a.max_carteira = self._to_float(self._max_cart.value)   if self._max_cart.value   else None
        a.tags  = [t.strip() for t in (self._tags.value or "").split(",") if t.strip()]
        a.notas = self._notas.value or ""
        a.dividendos_recebidos = self._to_float(self._dividendos.value)
        a.ultimo_rendimento    = self._to_float(self._ult_rend.value)
        a.reinvestir = self._reinvestir.value or "Não — manter como caixa"
        if not self._editando:
            a.sinal = Sinal.MANTER
        return a

    def _on_salvar(self, e):
        if not self._validar():
            return
        self.on_salvar(self._coletar())

    # ── Build ──────────────────────────────────────────────────

    def build(self) -> ft.Container:

        # ── Botões de tipo ──
        tipo_info = [
            (TipoAtivo.ACAO,    "📈 Ação (B3)"),
            (TipoAtivo.FII,     "🏢 FII"),
            (TipoAtivo.CDB,     "🏦 CDB / RDB"),
            (TipoAtivo.LCI_LCA, "🌿 LCI / LCA"),
            (TipoAtivo.TESOURO, "🇧🇷 Tesouro Direto"),
            (TipoAtivo.DEBENT,  "📄 Debênture / CRI / CRA"),
            (TipoAtivo.FUNDO,   "📦 Fundo de Investimento"),
            (TipoAtivo.ETF,     "🔗 ETF"),
            (TipoAtivo.CRYPTO,  "₿ Criptomoeda"),
            (TipoAtivo.OUTRO,   "⚙ Outro"),
        ]
        tipo_btns_list = []
        for tipo, label in tipo_info:
            sel = (tipo == self._tipo)
            btn = ft.Container(
                content=ft.Text(label, size=FONT_SIZE_XS,
                                color=GREEN_DARK if sel else TEXT_SECONDARY,
                                weight=ft.FontWeight.W_500),
                bgcolor=GREEN_BG if sel else BG_SECONDARY,
                border=ft.Border.all(0.5, GREEN_PRIMARY if sel else BORDER_COLOR),
                border_radius=ft.BorderRadius.all(6),
                padding=ft.Padding.symmetric(horizontal=PAD_SM, vertical=PAD_XS + 2),
                on_click=lambda e, t=tipo: self._set_tipo(t),
            )
            self._tipo_btns[tipo] = btn
            tipo_btns_list.append(btn)

        # ── Seção 2: Identificação RV ──
        self._painel_rv = ft.Column([
            _info_box("Digite o ticker como aparece na B3 (ex: PETR4). "
                      "O painel buscará dados fundamentalistas via API.", "blue"),
            ft.Row([
                _field("Ticker B3", self._ticker, "Ex: PETR4", required=True),
                _field("Nome da empresa / fundo", self._nome, "Ex: Petrobras PN"),
                _field("Setor / Segmento", self._setor),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
        ], spacing=10, visible=self._tipo in _VAR_TIPOS)

        # ── Seção 2: Identificação RF ──
        self._painel_rf = ft.Column([
            ft.Row([
                _field("Instituição emissora", self._emissor, required=True),
                _field("Tipo de rentabilidade", self._tipo_rent, required=True),
                _field("Taxa contratada", self._taxa,
                       "Ex: 112 para 112% CDI · 6,8 para IPCA+6,8%", required=True),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Row([
                _field("Cobertura FGC?", self._fgc),
                _field("Tributação", self._tributacao),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
        ], spacing=10, visible=self._tipo in _RF_TIPOS)

        # ── Seção 3: Qtd/Preço (só RV) ──
        self._qtd_row = ft.Column([
            ft.Row([
                _field("Quantidade de cotas", self._quantidade,
                       "Nº de cotas nesta operação", required=True),
                _field("Preço pago por cota (R$)", self._preco_compra,
                       "", required=True),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
        ], visible=self._tipo in _VAR_TIPOS)

        # ── Seção 3: Vencimento (só RF) ──
        self._painel_venc = ft.Column([
            _divider(),
            _info_box("Para renda fixa, informe o vencimento e a liquidez. "
                      "Títulos com liquidez diária podem ser resgatados a qualquer momento.", "yellow"),
            ft.Row([
                _field("Data de vencimento", self._data_venc, "AAAA-MM-DD"),
                _field("Liquidez", self._liquidez),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
        ], spacing=10, visible=self._tipo in _RF_TIPOS)

        # ── Conteúdo completo ──
        content = ft.Column([
            # Cabeçalho
            ft.Row([
                ft.Text(
                    "Editar Ativo" if self._editando else "Cadastrar Novo Ativo",
                    size=FONT_SIZE_LG, weight=ft.FontWeight.W_500,
                    color=TEXT_PRIMARY, expand=True,
                ),
                ft.IconButton(
                    ft.Icons.CLOSE, icon_color=TEXT_TERTIARY,
                    on_click=lambda e: self.on_cancelar(),
                ),
            ]),
            ft.Text("Campos com * são obrigatórios.",
                    size=FONT_SIZE_XS, color=TEXT_TERTIARY),
            _divider(),

            # 1. Tipo
            _section_header("1", "Tipo do Ativo"),
            ft.Row(tipo_btns_list, wrap=True, spacing=8, run_spacing=8),
            _divider(),

            # 2. Identificação
            _section_header("2", "Identificação do Ativo"),
            self._painel_rv,
            self._painel_rf,
            _divider(),

            # 3. Compra
            _section_header("3", "Dados da Compra / Aporte"),
            ft.Row([
                _field("Data da compra", self._data_compra, "AAAA-MM-DD", required=True),
                _field("Corretora / Plataforma", self._corretora, required=True),
                _field("Tipo de operação", self._tipo_op),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
            self._qtd_row,
            ft.Row([
                _field("Valor total investido (R$)", self._valor_total,
                       "Para renda fixa: valor aplicado", required=True),
                _field("Corretagem + taxas (R$)", self._corretagem),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
            self._painel_venc,
            _divider(),

            # 4. Gestão
            _section_header("4", "Gestão de Risco e Configurações"),
            ft.Row([
                _field("Objetivo deste ativo", self._objetivo),
                _field("Horizonte de investimento", self._horizonte),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Row([
                _field("Stop loss (R$)", self._stop_loss,
                       "Alerta quando o preço cair abaixo"),
                _field("Alvo de preço / Take profit (R$)", self._alvo_preco,
                       "Alerta de realização"),
                _field("Concentração máxima (%)", self._max_cart),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
            _field("Tags personalizadas", self._tags,
                   "Separe com vírgulas: dividendos, longo prazo, exportadora"),
            _field("Notas / Tese de investimento", self._notas,
                   "Privado — não aparece nas listagens"),
            _divider(),

            # 5. Rendimentos
            _section_header("5", "Rendimentos Recebidos (opcional)"),
            _info_box("Registre dividendos, JCP, rendimentos de FII ou cupons "
                      "para calcular o retorno total real.", "green"),
            ft.Row([
                _field("Total de rendimentos recebidos (R$)", self._dividendos),
                _field("Último rendimento (R$)", self._ult_rend),
                _field("Reinvestir dividendos?", self._reinvestir),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START),
            _divider(),

            # Erros e ações
            self._erros,
            ft.Row([
                ft.OutlinedButton(
                    "Cancelar",
                    on_click=lambda e: self.on_cancelar(),
                ),
                ft.FilledButton(
                    "Salvar ativo na carteira ✓",
                    on_click=self._on_salvar,
                    style=ft.ButtonStyle(bgcolor=GREEN_DARK, color="white"),
                ),
            ], alignment=ft.MainAxisAlignment.END, spacing=12),

        ], spacing=14, scroll=ft.ScrollMode.AUTO)

        # Calcula altura disponível deixando margens verticais
        page_h = 780
        try:
            if self._page:
                page_h = self._page.window.height or 780
        except Exception:
            pass
        card_height = max(500, page_h - 80)   # margem de 40px em cima e embaixo

        # Cartão do formulário arrastável
        form_card = ft.Container(
            content=content,
            bgcolor=BG_PRIMARY,
            border_radius=ft.BorderRadius.all(12),
            padding=PAD_MD,
            width=900,
            height=card_height,
            shadow=ft.BoxShadow(
                blur_radius=20,
                color="#00000055",
                spread_radius=2,
            ),
        )
        self._card_ref = form_card

        # GestureDetector para arrastar o popup
        # Nesta versão do Flet o delta vem em e.local_delta (Offset com .x e .y)
        def _on_pan_update(e: ft.DragUpdateEvent):
            if e.local_delta is not None:
                self._drag_x += e.local_delta.x
                self._drag_y += e.local_delta.y
            elif e.global_delta is not None:
                self._drag_x += e.global_delta.x
                self._drag_y += e.global_delta.y
            draggable_wrapper.left = center_left + self._drag_x
            draggable_wrapper.top  = center_top  + self._drag_y
            if self._page:
                self._page.update()

        gesture = ft.GestureDetector(
            content=form_card,
            on_pan_update=_on_pan_update,
            drag_interval=10,
        )

        # Posição inicial centralizada (será ajustada em run-time)
        center_left = 0.0
        center_top  = 0.0
        try:
            if self._page:
                pw = self._page.window.width or 1100
                center_left = (pw - 900) / 2
                center_top  = 40.0
        except Exception:
            pass

        draggable_wrapper = ft.Container(
            content=gesture,
            left=center_left,
            top=center_top,
        )

        return ft.Stack(
            [draggable_wrapper],
            expand=True,
        )
