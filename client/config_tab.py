import flet as ft

class ConfigTab:
    def __init__(self, groups):
        self.groups = groups

    def build(self):
        return ft.Column([
            ft.ListView(
                [
                    ft.Container(
                        ft.Row([
                            ft.Text(group.name, size=16, color=ft.Colors.WHITE),
                            ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.WHITE, size=20),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=10,
                        border_radius=8,
                        bgcolor={"hovered": ft.Colors.BLACK87},
                        ink=True,
                        on_click=lambda e: None,
                    )
                    for group in self.groups
                ],
                expand=1
            )
        ], expand=1, spacing=10)