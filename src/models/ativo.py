"""
models/ativo.py
Modelos de dados para os ativos da carteira.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from datetime import date, datetime
from typing import Optional


class TipoAtivo(str, Enum):
    ACAO      = "Ação (B3)"
    FII       = "FII"
    CDB       = "CDB / RDB"
    LCI_LCA   = "LCI / LCA"
    TESOURO   = "Tesouro Direto"
    DEBENT    = "Debenture / CRI / CRA"
    FUNDO     = "Fundo de Investimento"
    ETF       = "ETF"
    CRYPTO    = "Criptomoeda"
    OUTRO     = "Outro"


class TipoRentabilidade(str, Enum):
    CDI         = "Pós-fixado CDI (%)"
    IPCA_PLUS   = "IPCA + taxa fixa"
    PREFIXADO   = "Prefixado (% a.a.)"
    SELIC_PLUS  = "SELIC + spread"
    IGPM_PLUS   = "IGP-M + taxa fixa"


class Objetivo(str, Enum):
    RENDA       = "Renda / Dividendos"
    CRESCIMENTO = "Crescimento / Valorização"
    PROTECAO    = "Proteção / Hedge"
    EMERGENCIA  = "Reserva de emergência"
    OPORTUNIDADE = "Reserva de oportunidade"
    APOSENTADORIA = "Aposentadoria (longo prazo)"


class HorizonteInvestimento(str, Enum):
    CURTO    = "Curto prazo (< 1 ano)"
    MEDIO    = "Médio prazo (1–3 anos)"
    LONGO    = "Longo prazo (> 3 anos)"
    INDEFINIDO = "Indefinido"


class Liquidez(str, Enum):
    DIARIA     = "Liquidez diária (D+1)"
    C90        = "Carência 90 dias"
    C180       = "Carência 180 dias"
    C1ANO      = "Carência 1 ano"
    VENCIMENTO = "Apenas no vencimento"


class Sinal(str, Enum):
    COMPRAR  = "COMPRAR"
    MANTER   = "MANTER"
    AGUARDAR = "AGUARDAR"
    VENDER   = "VENDER"


class Corretora(str, Enum):
    XP       = "XP Investimentos"
    BTG      = "BTG Pactual"
    ITAU     = "Itaú Corretora"
    BRADESCO = "Bradesco Corretora"
    RICO     = "Rico"
    CLEAR    = "Clear"
    NUBANK   = "Nubank (NuInvest)"
    INTER    = "Banco Inter"
    MODAL    = "Modalmais"
    TORO     = "Toro Investimentos"
    WARREN   = "Warren"
    TESOURO  = "Tesouro Direto (site)"
    OUTRA    = "Outra"


@dataclass
class Ativo:
    """Representa uma posição na carteira do investidor."""

    # ── Identificação ────────────────────────────────────────
    id:          str            = ""
    tipo:        TipoAtivo      = TipoAtivo.ACAO
    ticker:      str            = ""          # PETR4, MXRF11...
    nome:        str            = ""          # nome completo
    setor:       str            = ""          # setor / segmento
    emissor:     str            = ""          # banco/emissor (renda fixa)
    cnpj_fundo:  str            = ""          # para fundos

    # ── Rentabilidade (renda fixa) ──────────────────────────
    tipo_rentabilidade: TipoRentabilidade = TipoRentabilidade.CDI
    taxa_contratada:    float   = 0.0         # ex: 112 para 112% CDI
    tributacao:         str     = "IR Regressivo"
    cobertura_fgc:      bool    = True

    # ── Dados da compra ──────────────────────────────────────
    data_compra:    date        = field(default_factory=date.today)
    quantidade:     float       = 0.0         # cotas
    preco_compra:   float       = 0.0         # R$/cota
    valor_total:    float       = 0.0         # total investido
    corretagem:     float       = 0.0         # taxas pagas
    corretora:      Corretora   = Corretora.XP
    tipo_operacao:  str         = "Compra normal"

    # ── Vencimento (renda fixa) ──────────────────────────────
    data_vencimento: Optional[date] = None
    liquidez:        Liquidez       = Liquidez.DIARIA

    # ── Preço atual (atualizado via mercado) ─────────────────
    preco_atual:    float       = 0.0
    rentabilidade_atual: str    = ""          # ex: "112% CDI"

    # ── Gestão de risco ──────────────────────────────────────
    objetivo:       Objetivo    = Objetivo.RENDA
    horizonte:      HorizonteInvestimento = HorizonteInvestimento.LONGO
    stop_loss:      Optional[float] = None
    alvo_preco:     Optional[float] = None
    max_carteira:   Optional[float] = None    # % máxima
    alerta_dividendo: str       = "Sim — alertar ao anúncio"
    no_rebalanceamento: bool    = True
    tags:           list        = field(default_factory=list)
    notas:          str         = ""

    # ── Rendimentos recebidos ────────────────────────────────
    dividendos_recebidos: float = 0.0
    ultimo_rendimento:    float = 0.0
    reinvestir:           str   = "Não — manter como caixa"

    # ── Sinal do painel ──────────────────────────────────────
    sinal:          Sinal       = Sinal.MANTER
    score_fund:     int         = 0
    score_tec:      int         = 0

    # ── Computed properties ──────────────────────────────────
    @property
    def custo_medio(self) -> float:
        """Custo médio real por cota incluindo corretagem."""
        if self.quantidade <= 0:
            return self.preco_compra
        return self.preco_compra + (self.corretagem / self.quantidade)

    @property
    def valor_atual(self) -> float:
        """Valor de mercado atual da posição."""
        if self.tipo in (TipoAtivo.CDB, TipoAtivo.LCI_LCA,
                         TipoAtivo.TESOURO, TipoAtivo.DEBENT,
                         TipoAtivo.FUNDO):
            return self.valor_total  # RF: usa valor total diretamente
        return self.quantidade * (self.preco_atual or self.preco_compra)

    @property
    def pl_reais(self) -> float:
        """P&L em reais (ganho/perda não realizado)."""
        return self.valor_atual - self.valor_total

    @property
    def pl_percentual(self) -> float:
        """P&L em percentual."""
        if self.valor_total <= 0:
            return 0.0
        return (self.pl_reais / self.valor_total) * 100

    @property
    def yield_on_cost(self) -> float:
        """Yield on cost acumulado (dividendos / custo)."""
        if self.valor_total <= 0:
            return 0.0
        return (self.dividendos_recebidos / self.valor_total) * 100

    @property
    def retorno_total(self) -> float:
        """P&L + dividendos recebidos."""
        return self.pl_reais + self.dividendos_recebidos

    def to_dict(self) -> dict:
        """Serializa para dicionário (JSON)."""
        return {
            "id": self.id,
            "tipo": self.tipo.value,
            "ticker": self.ticker,
            "nome": self.nome,
            "setor": self.setor,
            "emissor": self.emissor,
            "cnpj_fundo": self.cnpj_fundo,
            "tipo_rentabilidade": self.tipo_rentabilidade.value,
            "taxa_contratada": self.taxa_contratada,
            "tributacao": self.tributacao,
            "cobertura_fgc": self.cobertura_fgc,
            "data_compra": self.data_compra.isoformat(),
            "quantidade": self.quantidade,
            "preco_compra": self.preco_compra,
            "valor_total": self.valor_total,
            "corretagem": self.corretagem,
            "corretora": self.corretora.value,
            "tipo_operacao": self.tipo_operacao,
            "data_vencimento": self.data_vencimento.isoformat() if self.data_vencimento else None,
            "liquidez": self.liquidez.value,
            "preco_atual": self.preco_atual,
            "rentabilidade_atual": self.rentabilidade_atual,
            "objetivo": self.objetivo.value,
            "horizonte": self.horizonte.value,
            "stop_loss": self.stop_loss,
            "alvo_preco": self.alvo_preco,
            "max_carteira": self.max_carteira,
            "alerta_dividendo": self.alerta_dividendo,
            "no_rebalanceamento": self.no_rebalanceamento,
            "tags": self.tags,
            "notas": self.notas,
            "dividendos_recebidos": self.dividendos_recebidos,
            "ultimo_rendimento": self.ultimo_rendimento,
            "reinvestir": self.reinvestir,
            "sinal": self.sinal.value,
            "score_fund": self.score_fund,
            "score_tec": self.score_tec,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Ativo":
        """Desserializa de dicionário (JSON)."""
        a = cls()
        a.id           = d.get("id", "")
        a.tipo         = TipoAtivo(d.get("tipo", TipoAtivo.ACAO.value))
        a.ticker       = d.get("ticker", "")
        a.nome         = d.get("nome", "")
        a.setor        = d.get("setor", "")
        a.emissor      = d.get("emissor", "")
        a.cnpj_fundo   = d.get("cnpj_fundo", "")
        a.tipo_rentabilidade = TipoRentabilidade(
            d.get("tipo_rentabilidade", TipoRentabilidade.CDI.value))
        a.taxa_contratada = d.get("taxa_contratada", 0.0)
        a.tributacao   = d.get("tributacao", "IR Regressivo")
        a.cobertura_fgc = d.get("cobertura_fgc", True)
        a.data_compra  = date.fromisoformat(d["data_compra"]) if d.get("data_compra") else date.today()
        a.quantidade   = d.get("quantidade", 0.0)
        a.preco_compra = d.get("preco_compra", 0.0)
        a.valor_total  = d.get("valor_total", 0.0)
        a.corretagem   = d.get("corretagem", 0.0)
        a.corretora    = Corretora(d.get("corretora", Corretora.XP.value))
        a.tipo_operacao = d.get("tipo_operacao", "Compra normal")
        a.data_vencimento = date.fromisoformat(d["data_vencimento"]) if d.get("data_vencimento") else None
        a.liquidez     = Liquidez(d.get("liquidez", Liquidez.DIARIA.value))
        a.preco_atual  = d.get("preco_atual", 0.0)
        a.rentabilidade_atual = d.get("rentabilidade_atual", "")
        a.objetivo     = Objetivo(d.get("objetivo", Objetivo.RENDA.value))
        a.horizonte    = HorizonteInvestimento(d.get("horizonte", HorizonteInvestimento.LONGO.value))
        a.stop_loss    = d.get("stop_loss")
        a.alvo_preco   = d.get("alvo_preco")
        a.max_carteira = d.get("max_carteira")
        a.alerta_dividendo = d.get("alerta_dividendo", "Sim — alertar ao anúncio")
        a.no_rebalanceamento = d.get("no_rebalanceamento", True)
        a.tags         = d.get("tags", [])
        a.notas        = d.get("notas", "")
        a.dividendos_recebidos = d.get("dividendos_recebidos", 0.0)
        a.ultimo_rendimento    = d.get("ultimo_rendimento", 0.0)
        a.reinvestir   = d.get("reinvestir", "Não — manter como caixa")
        a.sinal        = Sinal(d.get("sinal", Sinal.MANTER.value))
        a.score_fund   = d.get("score_fund", 0)
        a.score_tec    = d.get("score_tec", 0)
        return a
