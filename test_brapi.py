import urllib.request
import json
import sys
import os

# Adiciona a pasta src no path do Python para poder importar o serviço do projeto
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from services.screener import get_quotes

def test_fetch_dynamic_stocks():
    print("=" * 70)
    print("1) Acessando a API da Brapi (ORDENADO POR MAIOR VOLUME / LIQUIDEZ)")
    print("=" * 70)
    
    # Busca focada nas ações mais negociadas da b3
    url = "https://brapi.dev/api/quote/list?type=stock&sortBy=volume&sortOrder=desc&limit=50"
    print(f"URL: {url}")
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            top_stocks_raw = data.get('stocks', [])
            
            print(f"\n-> Ativos Retornados pela Brapi: {len(top_stocks_raw)}")
            tickers_raw = [s['stock'] for s in top_stocks_raw]
            print(f"-> Top 15 Ativos de Maior Volume na B3 hoje: {tickers_raw[:15]}\n")
            
    except Exception as e:
        print(f"Erro ao acessar Brapi: {e}")
        return

    print("=" * 70)
    print("2) Filtrando Lixos (BDRs, FIIs, Units)...")
    print("=" * 70)
    
    valid_stocks = []
    for t in top_stocks_raw:
        ticker = t['stock'].upper()
        # Regra base para "AÇÕES": Não pode terminar em 11 (FIIs/Units/ETFs), 34/35/39 (BDRs)
        if not ticker.endswith(("11", "34", "35", "39")) and len(ticker) <= 6:
            valid_stocks.append(ticker)
            
    print(f"-> Sobraram Ações Puras após filtro: {len(valid_stocks)}")
    
    # Pega as 15 primeiras válidas (Já estão ordenadas pelas mais quentes do mercado)
    chosen_15 = valid_stocks[:15]
    print(f"-> Top 15 Ações Puras Válidas Separadas: {chosen_15}\n")

    print("=" * 70)
    print("3) Buscando Dados Fundamentalistas no Yahoo Finance (yfinance)...")
    print("=" * 70)
    
    quotes = get_quotes(chosen_15)
    
    print(f"{'TICKER'.ljust(8)} | {'NOME'.ljust(20)} | {'PREÇO'.ljust(12)} | {'P/L'.ljust(12)} | {'DIV.YIELD'.ljust(10)}")
    print("-" * 70)
    for asset in quotes:
        nome = (asset.name[:18] + '..') if len(asset.name) > 20 else asset.name
        preco = f"R$ {asset.price:.2f}" if asset.price else "Sem Preço"
        pl = f"{asset.pe_ratio:.1f}x" if asset.pe_ratio else "N/A"
        dy = f"{asset.dividend_yield*100:.1f}%" if asset.dividend_yield else "N/A"
        
        print(f"{asset.symbol.ljust(8)} | {nome.ljust(20)} | {preco.ljust(12)} | {pl.ljust(12)} | {dy.ljust(10)}")
        
    print("\nTeste da Estratégia Liquidez + Yahoo Fundamentalista Concluído com Sucesso!")

if __name__ == "__main__":
    test_fetch_dynamic_stocks()
