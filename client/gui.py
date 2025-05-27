import flet as ft
import sys
from client.sync_tab import SyncTab
from client.config_tab import ConfigTab

class App:
    def __init__(self, groups):
        self.page = None
        self.sync_tab = SyncTab()
        self.config_tab = ConfigTab(groups)
        self.tabs = None

    def main(self, page: ft.Page):
        self.page = page
        self.page.title = "Sync"
        self.page.window_width = 800
        self.page.window_height = 600
        self.page.window_resizable = True
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.Colors.ORANGE,
                primary_container=ft.Colors.ORANGE_100,
                secondary=ft.Colors.ORANGE_700,
                secondary_container=ft.Colors.ORANGE_200,
            )
        )

        self.page.window_event = self.window_event
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    icon=ft.Icon(ft.Icons.SYNC, size=20),
                    content=self.sync_tab.build()
                ),
                ft.Tab(
                    icon=ft.Icon(ft.Icons.NOTE_ALT, size=20),
                    content=self.config_tab.build()
                ),
            ],
            expand=1,
            height=30
        )
        self.page.add(self.tabs)
        self.page.update()

    def window_event(self, e):
        if e.data == "close":
            self.page.window_destroy()
            sys.exit(0)
