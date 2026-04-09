import sys

sys.path.insert(0, "C:/Leonardo/OpenCode/PainelInvest/app")

from pathlib import Path

_here = Path(__file__).resolve().parent

import flet as ft
from core.data_manager import DBManager
from ui.theme import PRIMARY, WHITE, BG, RED

db_path = _here / "assets" / "painel_invest.db"
dm = DBManager(str(db_path))
dm.initialize()

import ui.screens.acoes as acoes

page = ft.Page()


def set_content(controls):
    print("set_content called with", len(controls), "controls")


print("Testing acoes.build...")
try:
    acoes.build(page, dm, set_content, {})
    print("SUCCESS: acoes.build() completed without error")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback

    traceback.print_exc()
