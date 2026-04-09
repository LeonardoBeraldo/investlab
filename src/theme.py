"""
theme.py
Paleta de cores, tipografia e constantes visuais do InvestLab.
"""

import flet as ft

# ── Cores ─────────────────────────────────────────────────────────────
GREEN_PRIMARY   = "#1d9e75"
GREEN_DARK      = "#0F6E56"
GREEN_DARKER    = "#085041"
GREEN_BG        = "#E1F5EE"
GREEN_LIGHT     = "#9FE1CB"

RED_PRIMARY     = "#E24B4A"
RED_BG          = "#FCEBEB"
RED_DARK        = "#A32D2D"
RED_LIGHT       = "#F09595"
RED_TEXT        = "#791F1F"

YELLOW_PRIMARY  = "#EF9F27"
YELLOW_BG       = "#FAEEDA"
YELLOW_DARK     = "#854F0B"
YELLOW_BORDER   = "#E8C488"

BLUE_PRIMARY    = "#185FA5"
BLUE_BG         = "#E8EFF8"
BLUE_BORDER     = "#A8C4E8"

NEUTRAL_TEXT    = "#888780"
NEUTRAL_BG      = "#F1EFE8"
NEUTRAL_BORDER  = "#B4B2A9"
NEUTRAL_DARK    = "#5F5E5A"

BG_PRIMARY      = "#FFFFFF"
BG_SECONDARY    = "#F0EFEC"
BG_TERTIARY     = "#F5F4F0"
BG_DARK_HEADER  = "#1a3c34"

BORDER_COLOR    = "#E0DFDB"
TEXT_PRIMARY    = "#1a1a18"
TEXT_SECONDARY  = "#666662"
TEXT_TERTIARY   = "#999997"

# ── Tipografia ────────────────────────────────────────────────────────
FONT_MONO      = "monospace"
FONT_SIZE_XS   = 10
FONT_SIZE_SM   = 11
FONT_SIZE_MD   = 13
FONT_SIZE_LG   = 15
FONT_SIZE_XL   = 18
FONT_SIZE_2XL  = 20
FONT_SIZE_3XL  = 24
FONT_SIZE_4XL  = 32

# ── Espaçamentos ──────────────────────────────────────────────────────
PAD_XS  = 4
PAD_SM  = 8
PAD_MD  = 12
PAD_LG  = 16
PAD_XL  = 20
PAD_2XL = 24

# ── Bordas ────────────────────────────────────────────────────────────
RADIUS_SM    = 6
RADIUS_MD    = 8
RADIUS_LG    = 10
BORDER_WIDTH = 0.5

# ── Helpers ───────────────────────────────────────────────────────────
def card_border():
    return ft.Border.all(BORDER_WIDTH, BORDER_COLOR)

def make_theme() -> ft.Theme:
    """Retorna o tema Flet com as cores InvestLab."""
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=GREEN_PRIMARY,
            secondary=GREEN_DARK,
            surface=BG_PRIMARY,
            error=RED_PRIMARY,
            on_primary="white",
            on_secondary="white",
        ),
        font_family=FONT_MONO,
    )
