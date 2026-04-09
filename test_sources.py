import yfinance as yf

print("=== Buscando tickers brasileiros com Search ===")

# Testar diferentes termos de busca
test_queries = ["", "ação", "ON", "PN", "IBOV", "B3"]

for query in test_queries:
    print(f"\n--- Busca '{query}' ---")
    try:
        if query == "":
            # Tentando buscar os tickers mais ativos
            # Não funciona bem com string vazia
            continue
        search = yf.Search(query + " SA")
        print(f"Resultados: {len(search.quotes)}")
        count = 0
        for q in search.quotes:
            if q.get("symbol", "").endswith(".SA") or q.get("symbol", "").endswith(
                ".SP"
            ):
                print(f"  {q.get('symbol')}")
                count += 1
                if count >= 20:
                    break
    except Exception as e:
        print(f"Erro: {e}")

print("\n=== Tentando buscar via IBOV ===")
try:
    search = yf.Search("IBOV")
    print(f"Resultados: {len(search.quotes)}")
    for q in search.quotes[:10]:
        print(f"  {q.get('symbol')}")
except Exception as e:
    print(f"Erro: {e}")
