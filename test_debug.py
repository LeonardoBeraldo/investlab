import sys
import os

# Set up path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
os.chdir(os.path.join(os.path.dirname(__file__), "app"))

# Import after path setup
from core.data_manager import DBManager

db_path = "assets/painel_invest.db"
dm = DBManager(db_path)

# Test get_sinal function directly
from ui.screens import acoes

# Get a test perfil from database
conn = dm._connect()
perfis = conn.execute("SELECT * FROM perfis_analise WHERE nome = 'Moderado'").fetchall()
conn.close()

print(f"Loaded {len(perfis)} perfis")
if perfis:
    perfil = dict(perfis[0])
    print(f"Perfil: {perfil}")
    print(f"limiar_comprar type: {type(perfil.get('limiar_comprar'))}")
    print(f"limiar_comprar value: {perfil.get('limiar_comprar')}")

    # Test get_sinal
    result = acoes.get_sinal(80, perfil)
    print(f"get_sinal(80, perfil) = {result}")
