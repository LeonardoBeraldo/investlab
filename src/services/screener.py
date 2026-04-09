"""
B3 Asset Screener — sem hardcode de tickers
Usa Yahoo Finance (yfinance) para descoberta dinâmica de ativos.
"""

from __future__ import annotations

import logging
import urllib.request
import json
import random
import concurrent.futures
from dataclasses import dataclass, field, asdict
from typing import Literal, Optional

import yfinance as yf
from yfinance import EquityQuery, FundQuery, screen

logger = logging.getLogger(__name__)

AssetType = Literal["stock", "etf", "fii"]

# Código da B3 (Bolsa de Valores de São Paulo) no Yahoo Finance screener
B3_EXCHANGE_CODE = "SAO"

SORT_FIELDS = {
    "market_cap": "intradaymarketcap",
    "volume":     "intradayvol",
    "price":      "intradayprice",
    "change":     "intradaypricechange",
    "pe_ratio":   "peratio.lasttwelvemonths",
}

# Sort fields disponíveis para FundQuery (subconjunto)
FUND_SORT_FIELDS = {
    "market_cap": "intradaymarketcap",
    "volume":     "intradayvol",
    "price":      "intradayprice",
    "change":     "intradaypricechange",
    # pe_ratio não existe em FundQuery
}

@dataclass
class Asset:
    symbol:              str
    name:                str
    asset_type:          AssetType
    price:               Optional[float]
    change_pct:          Optional[float]
    volume:              Optional[int]
    market_cap:          Optional[float]
    currency:            str = "BRL"
    sector:              Optional[str] = None
    pe_ratio:            Optional[float] = None
    dividend_yield:      Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low:  Optional[float] = None
    exchange:            Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def change_signal(self) -> str:
        if self.change_pct is None: return "–"
        return "▲" if self.change_pct >= 0 else "▼"

    def __repr__(self) -> str:
        chg   = f"{self.change_pct:+.2f}%" if self.change_pct is not None else "N/A"
        price = f"R${self.price:.2f}" if self.price else "N/A"
        return f"<Asset {self.symbol} | {price} {self.change_signal}{chg} | {self.asset_type.upper()}>"


def analyze_asset(a: Asset) -> tuple[int, int, str]:
    """
    Retorna (score_fund, score_tec, sinal) consistentes 
    baseando-se nos parametros da APi do Yahoo Finance.
    """
    if not a.price:
        return 0, 0, "AGUARDAR"
        
    s_fund = 50
    s_tech = 50
    
    if a.asset_type == "stock":
        # Analise fundamentalista basica
        if a.pe_ratio:
            if 0 < a.pe_ratio < 10: s_fund += 20
            elif a.pe_ratio > 25: s_fund -= 20
            elif a.pe_ratio < 0: s_fund -= 40
            
        if a.dividend_yield:
            if a.dividend_yield > 0.05: s_fund += 20
            elif a.dividend_yield > 0.10: s_fund += 30
            
    elif a.asset_type == "fii":
        if a.dividend_yield:
            # FIIs yield usually 8-12+
            if a.dividend_yield > 0.10: s_fund += 30
            elif a.dividend_yield > 0.08: s_fund += 15
            elif a.dividend_yield < 0.05: s_fund -= 20

    # Analise "tecnica" basica pela variacao diaria
    if a.change_pct:
        if a.change_pct > 2: s_tech += 20
        elif a.change_pct < -2: s_tech -= 30
        
    s_fund = max(0, min(100, s_fund))
    s_tech = max(0, min(100, s_tech))
    
    # Decide sinal principal
    sinal = "MANTER"
    if s_fund >= 70 and s_tech >= 40:
        sinal = "COMPRAR"
    elif s_fund <= 40 or s_tech <= 30:
        sinal = "VENDER"
        
    return s_fund, s_tech, sinal



def _parse_quote(raw: dict, asset_type: AssetType) -> Asset:
    return Asset(
        symbol=raw.get("symbol", "").replace(".SA", ""),
        name=raw.get("longName") or raw.get("shortName") or raw.get("symbol", ""),
        asset_type=asset_type,
        price=raw.get("regularMarketPrice"),
        change_pct=raw.get("regularMarketChangePercent"),
        volume=raw.get("regularMarketVolume"),
        market_cap=raw.get("marketCap"),
        currency=raw.get("currency", "BRL"),
        sector=raw.get("sector"),
        pe_ratio=raw.get("trailingPE"),
        dividend_yield=raw.get("dividendYield"),
        fifty_two_week_high=raw.get("fiftyTwoWeekHigh"),
        fifty_two_week_low=raw.get("fiftyTwoWeekLow"),
        exchange=raw.get("exchange") or raw.get("fullExchangeName"),
    )

def get_top_stocks(
    size: int = 50, # Buscar mais para compensar o filtro
    sort_by: str = "market_cap",
    ascending: bool = False,
    region: str = "br",
    b3_only: bool = False,
) -> list[Asset]:
    """Retorna as maiores ações via screener."""
    sort_field = SORT_FIELDS.get(sort_by, SORT_FIELDS["market_cap"])

    if b3_only:
        query = EquityQuery("and", [
            EquityQuery("eq", ["region", region]),
            EquityQuery("eq", ["exchange", B3_EXCHANGE_CODE]),
        ])
    else:
        query = EquityQuery("eq", ["region", region])

    result = screen(query, sortField=sort_field, sortAsc=ascending, size=size)
    quotes  = result.get("quotes", [])
    assets  = []
    for q in quotes:
        sym = q.get("symbol", "")
        # Ignorar BDRs (34, 35, 39...) e ETFs comuns que poluem a lista
        if sym.endswith(("34.SA", "35.SA", "39.SA", "11.SA")):
            continue
        assets.append(_parse_quote(q, "stock"))
    return assets[:20]

def get_top_etfs(
    size: int = 20,
    sort_by: str = "market_cap",
    ascending: bool = False,
    region: str = "br",
    b3_only: bool = False,
) -> list[Asset]:
    """Retorna os maiores ETFs via FundQuery."""
    sort_field = FUND_SORT_FIELDS.get(sort_by, FUND_SORT_FIELDS["market_cap"])

    if b3_only:
        query = FundQuery("eq", ["exchange", B3_EXCHANGE_CODE])
    else:
        query = FundQuery("gt", ["intradayprice", 0])

    result = screen(query, sortField=sort_field, sortAsc=ascending, size=size)
    quotes  = result.get("quotes", [])
    assets  = [_parse_quote(q, "etf") for q in quotes]
    return assets

def get_top_fiis(
    size: int = 50,
    sort_by: str = "market_cap",
    ascending: bool = False,
    region: str = "br",
    b3_only: bool = False,
) -> list[Asset]:
    """Retorna os maiores FIIs via EquityQuery adaptada + Filtro '11'."""
    sort_field = SORT_FIELDS.get(sort_by, SORT_FIELDS["market_cap"])

    # Usando EquityQuery pois FundQuery falha frequentemente para a B3
    if b3_only:
        query = EquityQuery("and", [
            EquityQuery("eq", ["region", region]),
            EquityQuery("eq", ["exchange", B3_EXCHANGE_CODE]),
        ])
    else:
        query = EquityQuery("eq", ["region", region])

    result = screen(query, sortField=sort_field, sortAsc=ascending, size=size*2)
    quotes  = result.get("quotes", [])
    assets  = []
    
    # Filtro customizado para tentar identificar FIIs se baseando em terminar com 11
    # Note: Algumas Units (Ex: TAEE11) vêm junto, mas e melhor do que lista vazia
    for q in quotes:
        sym = q.get("symbol", "")
        # Alguns FIIs vem como MUTUALFUND, outros EQUITY no Yahoo Finance
        if sym.endswith("11.SA"):
            # Exclui algumas famosas que sao Units e nao FIIs
            if sym.startswith(("TAEE", "SANB", "KLBN", "BPAC", "ENGI", "ALUP", "TIET")):
                continue
            assets.append(_parse_quote(q, "fii"))
            
    return assets[:20]

def search_assets(query: str, asset_type: Optional[AssetType] = None) -> list[Asset]:
    """Busca dinâmica de ativos pelo nome ou ticker via yf.Search."""
    search = yf.Search(query, max_results=20, news_count=0)
    quotes = search.quotes or []
    type_map = {"EQUITY": "stock", "ETF": "etf", "MUTUALFUND": "fii"}
    assets = []
    for q in quotes:
        qt       = q.get("quoteType", "")
        detected = type_map.get(qt, "stock")
        symbol   = q.get("symbol", "")
        if symbol.endswith("11") and qt in ("ETF", "MUTUALFUND"):
            detected = "fii"
        if asset_type and detected != asset_type:
            continue
        assets.append(Asset(
            symbol=symbol.replace(".SA", ""),
            name=q.get("longname") or q.get("shortname") or symbol,
            asset_type=detected,
            price=None, change_pct=None, volume=None, market_cap=None,
            exchange=q.get("exchDisp"),
        ))
    return assets

def get_quotes(symbols: list[str]) -> list[Asset]:
    """Busca cotação em tempo real para uma lista de símbolos (PARALELIZADO para velocidade alta)."""
    if not symbols:
        return []
    normalized = [s if s.endswith(".SA") else f"{s}.SA" for s in symbols]
    tickers = yf.Tickers(" ".join(normalized))

    def _fetch_single(sym, norm):
        try:
            info      = tickers.tickers[norm].fast_info
            price     = float(info.last_price) if hasattr(info, "last_price") and info.last_price else None
            
            prev = None
            if hasattr(info, "previous_close") and info.previous_close:
                prev = float(info.previous_close)
                
            change_pct = ((price - prev) / prev * 100) if price and prev else None
            
            vol = None
            if hasattr(info, "three_month_average_volume") and info.three_month_average_volume:
                vol = int(info.three_month_average_volume)
            
            mkt_cap = None
            if hasattr(info, "market_cap") and info.market_cap:
                mkt_cap = float(info.market_cap)
            
            # yfinance .info faz requisicoes http para varios modulos, entao é lento se rodar de 1 em 1
            full_info = tickers.tickers[norm].info
            pe_ratio = full_info.get("trailingPE")
            div_yield = full_info.get("dividendYield")
            
            return Asset(
                symbol=sym,
                name=full_info.get("longName") or full_info.get("shortName") or sym,
                asset_type="stock",
                price=price,
                change_pct=change_pct,
                volume=vol,
                market_cap=mkt_cap,
                currency=getattr(info, "currency", "BRL"),
                pe_ratio=pe_ratio,
                dividend_yield=div_yield
            )
        except Exception as e:
            logger.warning(f"[Quotes] Erro ao buscar {sym}: {e}")
            return Asset(symbol=sym, name=sym, asset_type="stock", price=None, change_pct=None, volume=None, market_cap=None)

    # Executa todas as consultas de HTTP/info.get() simultaneamente para nao travar.
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(symbols)) as executor:
        assets = list(executor.map(lambda arg: _fetch_single(*arg), zip(symbols, normalized)))

    return assets

def _fetch_top_volume_tickers(asset_type: str, limit: int = 30) -> list[str]:
    """Busca a lista de ativos já ordenados por liquidez (volume) usando brapi."""
    try:
        t_param = "stock" if asset_type == "stock" else "fund"
        
        url = f"https://brapi.dev/api/quote/list?type={t_param}&sortBy=volume&sortOrder=desc&limit={limit}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            stocks = data.get('stocks', [])
            return [s['stock'] for s in stocks]
    except Exception as e:
        logger.warning(f"Erro ao buscar ativos por volume na brapi: {e}")
        return []

def get_top_dynamic(asset_type: str, limit: int = 20) -> list[Asset]:
    """Retorna os top ativos da B3 filtrados por maior liquidez e depois consulta os dados puros."""
    # Busca 50 para ter margem de descarte (FIIs e Acoes)
    tickers = _fetch_top_volume_tickers(asset_type, limit=50)
    
    if not tickers:
        # Fallback seguro caso a brapi saia do ar
        tickers = ["PETR4", "VALE3", "ITUB4", "WEGE3", "BBDC4", "BBAS3", "ELET3"] if asset_type == "stock" else ["MXRF11", "HGLG11", "KNRI11", "XPML11", "BTLG11", "IRDM11"]
        
    valid = []
    for t in tickers:
        t = t.upper()
        if asset_type == "stock":
            if not t.endswith(("11", "34", "35", "39")) and len(t) <= 6:
                valid.append(t)
        elif asset_type == "fii":
            if t.endswith("11") and not t.startswith(("TAEE", "SANB", "KLBN", "BPAC", "ENGI", "ALUP", "TIET", "BOVA", "IVVB", "SMAL", "BOVX")):
                valid.append(t)
                
    chosen = valid[:limit]
    
    # Agora puxamos os dados reais fundamentalistas do mercado usando yfinance
    return get_quotes(chosen)

