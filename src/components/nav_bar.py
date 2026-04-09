"""
components/nav_bar.py
Barra de navegação inferior.
"""

import flet as ft
from theme import GREEN_PRIMARY, BG_PRIMARY, BORDER_COLOR


def nav_bar(on_change) -> ft.NavigationBar:
    return ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Visão Geral",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SHOW_CHART_OUTLINED,
                selected_icon=ft.Icons.SHOW_CHART,
                label="Ações",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.APARTMENT_OUTLINED,
                selected_icon=ft.Icons.APARTMENT,
                label="FIIs",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.ACCOUNT_BALANCE_OUTLINED,
                selected_icon=ft.Icons.ACCOUNT_BALANCE,
                label="Renda Fixa",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.PUBLIC_OUTLINED,
                selected_icon=ft.Icons.PUBLIC,
                label="Macro",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.WALLET_OUTLINED,
                selected_icon=ft.Icons.WALLET,
                label="Carteira",
            ),
        ],
        selected_index=0,
        bgcolor=BG_PRIMARY,
        on_change=lambda e: on_change(e.control.selected_index),
    )
