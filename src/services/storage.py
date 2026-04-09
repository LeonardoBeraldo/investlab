"""
services/storage.py
Persistência local em JSON.
Funciona em Windows, macOS, Linux e Android.

Flet fornece o caminho correto via variável de ambiente FLET_APP_STORAGE_DATA
em todas as plataformas (desktop + Android + iOS).
Fallback: ~/.investlab/ quando rodando fora do Flet (testes, REPL, etc.).
"""

from __future__ import annotations
import json
import os
import uuid
from pathlib import Path
from typing import Optional

from models.ativo import Ativo


def _resolve_data_dir() -> Path:
    """
    Retorna o diretório de dados persistentes do app.

    Prioridade:
      1. FLET_APP_STORAGE_DATA  — definido pelo runtime Flet (desktop, APK, AAB)
      2. ~/.investlab/           — fallback para desenvolvimento sem `flet run`
    """
    flet_dir = os.getenv("FLET_APP_STORAGE_DATA")
    if flet_dir:
        return Path(flet_dir)
    return Path.home() / ".investlab"


class StorageService:
    """Persiste a carteira e preferências do usuário em JSON local."""

    _CARTEIRA_FILE = "carteira.json"
    _PREFS_FILE    = "preferencias.json"

    def __init__(self) -> None:
        self._dir = _resolve_data_dir()
        self._dir.mkdir(parents=True, exist_ok=True)

    # ── Carteira ─────────────────────────────────────────────

    def carregar_carteira(self) -> list[Ativo]:
        """Carrega lista de ativos do arquivo JSON."""
        path = self._dir / self._CARTEIRA_FILE
        if not path.exists():
            return self._seed_demo()
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return [Ativo.from_dict(d) for d in data]
        except Exception:
            return self._seed_demo()

    def salvar_carteira(self, ativos: list[Ativo]) -> None:
        """Persiste lista de ativos."""
        path = self._dir / self._CARTEIRA_FILE
        with open(path, "w", encoding="utf-8") as f:
            json.dump([a.to_dict() for a in ativos], f,
                      ensure_ascii=False, indent=2)

    def salvar_ativo(self, ativo: Ativo,
                     ativos: list[Ativo]) -> list[Ativo]:
        """Insere ou atualiza um ativo e persiste."""
        if not ativo.id:
            ativo.id = str(uuid.uuid4())
        idx = next((i for i, a in enumerate(ativos) if a.id == ativo.id), None)
        if idx is not None:
            ativos[idx] = ativo
        else:
            ativos.append(ativo)
        self.salvar_carteira(ativos)
        return ativos

    def excluir_ativo(self, ativo_id: str,
                      ativos: list[Ativo]) -> list[Ativo]:
        """Remove ativo por ID e persiste."""
        ativos = [a for a in ativos if a.id != ativo_id]
        self.salvar_carteira(ativos)
        return ativos

    # ── Preferências ─────────────────────────────────────────

    def carregar_prefs(self) -> dict:
        path = self._dir / self._PREFS_FILE
        if not path.exists():
            return {}
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def salvar_prefs(self, prefs: dict) -> None:
        path = self._dir / self._PREFS_FILE
        with open(path, "w", encoding="utf-8") as f:
            json.dump(prefs, f, ensure_ascii=False, indent=2)

    # ── Dados de demonstração ─────────────────────────────────

    def _seed_demo(self) -> list[Ativo]:
        """Popula carteira com dados de demo na primeira execução."""
        from models.ativo import (
            TipoAtivo, TipoRentabilidade, Sinal,
            Objetivo, Corretora, HorizonteInvestimento, Liquidez,
        )
        from datetime import date

        demo = [
            Ativo(
                id="demo-1", tipo=TipoAtivo.ACAO,
                ticker="PETR4", nome="Petrobras PN",
                setor="Petróleo & Gás",
                data_compra=date(2025, 6, 10),
                quantidade=200, preco_compra=32.40,
                valor_total=6480.0, corretagem=5.0,
                corretora=Corretora.XP,
                preco_atual=38.20,
                objetivo=Objetivo.RENDA,
                horizonte=HorizonteInvestimento.LONGO,
                dividendos_recebidos=320.0,
                sinal=Sinal.COMPRAR, score_fund=82, score_tec=75,
            ),
            Ativo(
                id="demo-2", tipo=TipoAtivo.ACAO,
                ticker="BBAS3", nome="Banco do Brasil ON",
                setor="Bancário / Financeiro",
                data_compra=date(2025, 3, 15),
                quantidade=350, preco_compra=24.80,
                valor_total=8680.0, corretagem=5.0,
                corretora=Corretora.BTG,
                preco_atual=28.15,
                objetivo=Objetivo.RENDA,
                horizonte=HorizonteInvestimento.LONGO,
                dividendos_recebidos=580.0,
                sinal=Sinal.COMPRAR, score_fund=85, score_tec=72,
            ),
            Ativo(
                id="demo-3", tipo=TipoAtivo.ACAO,
                ticker="WEGE3", nome="WEG S.A. ON",
                setor="Indústria / Manufatura",
                data_compra=date(2024, 11, 20),
                quantidade=120, preco_compra=38.00,
                valor_total=4560.0, corretagem=5.0,
                corretora=Corretora.RICO,
                preco_atual=42.90,
                objetivo=Objetivo.CRESCIMENTO,
                horizonte=HorizonteInvestimento.LONGO,
                dividendos_recebidos=85.0,
                sinal=Sinal.AGUARDAR, score_fund=62, score_tec=58,
            ),
            Ativo(
                id="demo-4", tipo=TipoAtivo.FII,
                ticker="MXRF11", nome="Maxi Renda FII",
                setor="FII — Papel / CRI",
                data_compra=date(2025, 1, 8),
                quantidade=800, preco_compra=9.85,
                valor_total=7880.0, corretagem=0.0,
                corretora=Corretora.XP,
                preco_atual=10.42,
                rentabilidade_atual="12,5% DY",
                objetivo=Objetivo.RENDA,
                horizonte=HorizonteInvestimento.LONGO,
                dividendos_recebidos=720.0,
                sinal=Sinal.COMPRAR, score_fund=84, score_tec=0,
            ),
            Ativo(
                id="demo-5", tipo=TipoAtivo.FII,
                ticker="KNRI11", nome="Kinea Renda Imobiliária",
                setor="FII — Híbrido",
                data_compra=date(2024, 9, 3),
                quantidade=60, preco_compra=138.00,
                valor_total=8280.0, corretagem=0.0,
                corretora=Corretora.BTG,
                preco_atual=142.90,
                rentabilidade_atual="7,1% DY",
                objetivo=Objetivo.RENDA,
                horizonte=HorizonteInvestimento.LONGO,
                dividendos_recebidos=490.0,
                sinal=Sinal.MANTER, score_fund=61, score_tec=0,
            ),
            Ativo(
                id="demo-6", tipo=TipoAtivo.CDB,
                nome="CDB Banco Inter 112% CDI",
                emissor="Banco Inter",
                tipo_rentabilidade=TipoRentabilidade.CDI,
                taxa_contratada=112.0,
                tributacao="IR Regressivo",
                cobertura_fgc=True,
                data_compra=date(2025, 2, 1),
                valor_total=25000.0,
                corretora=Corretora.INTER,
                liquidez=Liquidez.DIARIA,
                rentabilidade_atual="112% CDI ≈ 15,3% a.a.",
                objetivo=Objetivo.EMERGENCIA,
                sinal=Sinal.MANTER,
            ),
            Ativo(
                id="demo-7", tipo=TipoAtivo.TESOURO,
                nome="Tesouro IPCA+ 2035",
                emissor="Tesouro Nacional",
                tipo_rentabilidade=TipoRentabilidade.IPCA_PLUS,
                taxa_contratada=6.8,
                tributacao="IR Regressivo",
                cobertura_fgc=False,
                data_compra=date(2024, 8, 20),
                valor_total=17000.0,
                corretora=Corretora.TESOURO,
                liquidez=Liquidez.VENCIMENTO,
                rentabilidade_atual="IPCA + 6,8% a.a.",
                objetivo=Objetivo.APOSENTADORIA,
                horizonte=HorizonteInvestimento.LONGO,
                sinal=Sinal.MANTER,
            ),
        ]
        self.salvar_carteira(demo)
        return demo
