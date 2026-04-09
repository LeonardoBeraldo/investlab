import yfinance as yf

print("=== Testando yf.Tickers() ===")
try:
    tickers = yf.Tickers("PETR4 VALE3 ITUB4")
    for t in tickers.tickers:
        print(f"  {t}: {t.info.get('regularMarketPrice')}")
except Exception as e:
    print(f"Erro: {e}")

print("\n=== Testando busca porIBOV componentes via Wikipedia ===")
try:
    import requests

    url = "https://en.wikipedia.org/wiki/Components_of_the_Bovespa_Index"
    resp = requests.get(url, timeout=10)
    print(f"Status: {resp.status_code}")
except Exception as e:
    print(f"Erro: {e}")
