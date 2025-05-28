import flet as ft
import sys
import os
from sync import Sync, SyncItem

class App:
    def __init__(self, groups):
        self.page = None
        self.groups = groups
        self.expanded_groups = set()
        self.list_view = None
        self.selected_items = set()
        self.selected_groups = set()
        self.sync_button = None
        self.edit_button = None
        self.back_button = None
        self.sync = Sync()
        self.progress_bar = None
        self.log_view = None
        self.logs = []

    def build_group_items(self):
        items = []
        for group in self.groups:
            group_id = id(group)
            items.append(
                ft.Container(
                    ft.Row([
                        ft.Row([
                            ft.Checkbox(
                                value=group_id in self.selected_groups,
                                on_change=lambda e, g=group_id: self.on_group_checkbox_change(g, e.control.value)
                            ),
                            ft.Text(group.name, size=16, color=ft.Colors.WHITE),
                        ], spacing=10),
                        ft.Icon(
                            ft.Icons.EXPAND_MORE if group_id in self.expanded_groups else ft.Icons.CHEVRON_RIGHT,
                            color=ft.Colors.WHITE,
                            size=20
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10,
                    border_radius=8,
                    bgcolor={"hovered": ft.Colors.BLACK87},
                    ink=True,
                    on_click=lambda e, g=group_id: self.on_group_click(g),
                )
            )
            if group_id in self.expanded_groups:
                items.append(
                    ft.Container(
                        ft.Column([
                            ft.Column([
                                ft.Row([
                                    ft.Checkbox(
                                        value=id(item) in self.selected_items,
                                        on_change=lambda e, i=id(item): self.on_item_checkbox_change(i, e.control.value)
                                    ),
                                    ft.Column([
                                        ft.Text(item.name, size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        ft.Text(self.format_source(item.source), size=12, color=ft.Colors.WHITE70),
                                        ft.Text(f"To: {item.destination}", size=12, color=ft.Colors.WHITE70),
                                    ], spacing=2)
                                ], spacing=10)
                            ], spacing=8)
                            for item in group.items
                        ], spacing=8),
                        padding=ft.padding.only(left=20, top=5, bottom=5),
                        bgcolor=ft.Colors.BLACK45
                    )
                )
        return items

    def update_sync_button_visibility(self):
        if self.sync_button and self.edit_button:
            if len(self.selected_items) > 0:
                self.sync_button.visible = True
                self.edit_button.visible = False
            else:
                self.sync_button.visible = False
                self.edit_button.visible = True
            self.page.update()

    def on_group_checkbox_change(self, group_id, value):
        if value:
            self.selected_groups.add(group_id)
            for group in self.groups:
                if id(group) == group_id:
                    for item in group.items:
                        self.selected_items.add(id(item))
        else:
            self.selected_groups.remove(group_id)
            for group in self.groups:
                if id(group) == group_id:
                    for item in group.items:
                        self.selected_items.discard(id(item))
        self.list_view.controls = self.build_group_items()
        self.update_sync_button_visibility()
        self.list_view.update()

    def on_item_checkbox_change(self, item_id, value):
        if value:
            self.selected_items.add(item_id)
        else:
            self.selected_items.discard(item_id)
        self.list_view.controls = self.build_group_items()
        self.update_sync_button_visibility()
        self.list_view.update()

    def format_source(self, source):
        if isinstance(source, list):
            max_files = 3
            files = [str(f) for f in source]
            if len(files) > max_files:
                files = files[:max_files]
                return f"From: {', '.join(files)} ..."
            else:
                return f"From: {', '.join(files)}"
        else:
            return f"From: {source}"

    def on_group_click(self, group_id):
        if group_id in self.expanded_groups:
            self.expanded_groups.remove(group_id)
        else:
            self.expanded_groups.add(group_id)
        self.list_view.controls = self.build_group_items()
        self.list_view.update()

    def on_progress(self, current: str, total: str):
        if self.progress_bar and current and total:
            try:
                current_num = float(current)
                total_num = float(total)
                if total_num > 0:
                    self.progress_bar.value = current_num / total_num
                    self.page.update()
            except (ValueError, TypeError):
                pass

    def on_log(self, log: str, new_line: bool):
        if new_line:
            self.logs.append(log)
        else:
            if self.logs:
                self.logs[-1] = log
            else:
                self.logs.append(log)
        if self.log_view:
            self.log_view.value = "\n".join(self.logs)
            self.log_view.cursor_position = len(self.log_view.value)
            self.page.update()

    def on_sync_click(self, e):
        selected_items = []
        for group in self.groups:
            for item in group.items:
                if id(item) in self.selected_items:
                    selected_items.append(item)
        
        if selected_items:
            self.sync_button.visible = False
            self.progress_bar.visible = True
            self.list_view.visible = False
            self.log_view.visible = True
            self.logs = []
            self.back_button.visible = False
            self.page.update()
            
            self.sync.sync_items(selected_items, self.on_progress, self.on_log)
            
            self.progress_bar.visible = False
            self.back_button.visible = True
            self.page.update()

    def show_groups(self, e=None):
        self.list_view.visible = True
        self.log_view.visible = False
        self.back_button.visible = False
        self.update_sync_button_visibility()
        self.page.update()

    def on_edit_click(self, e):
        config_path = os.path.abspath("config.json")
        if sys.platform.startswith("win"):
            os.startfile(config_path)
        elif sys.platform.startswith("darwin"):
            os.system(f"open '{config_path}'")
        else:
            os.system(f"xdg-open '{config_path}'")

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
        self.list_view = ft.ListView(self.build_group_items(), expand=1)
        
        self.log_view = ft.TextField(
            value="",
            multiline=True,
            read_only=True,
            expand=True,
            visible=False,
            text_style=ft.TextStyle(
                color=ft.Colors.WHITE,
                size=12,
                font_family="Consolas"
            )
        )

        self.back_button = ft.IconButton(
            icon=ft.Icons.CHECK,
            icon_color=ft.Colors.WHITE,
            icon_size=20,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.ORANGE,
                shape=ft.CircleBorder(),
            ),
            on_click=self.show_groups,
            visible=False
        )

        self.sync_button = ft.IconButton(
            icon=ft.Icons.SYNC,
            icon_color=ft.Colors.WHITE,
            icon_size=20,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.ORANGE,
                shape=ft.CircleBorder(),
            ),
            on_click=self.on_sync_click,
            visible=False
        )

        self.edit_button = ft.IconButton(
            icon=ft.Icons.EDIT,
            icon_color=ft.Colors.WHITE,
            icon_size=20,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.ORANGE,
                shape=ft.CircleBorder(),
            ),
            on_click=self.on_edit_click,
            visible=False
        )

        self.progress_bar = ft.ProgressBar(
            expand=True,
            color=ft.Colors.ORANGE,
            bgcolor=ft.Colors.BLACK45,
            visible=False
        )

        footer = ft.Container(
            ft.Column([
                ft.Row([
                    self.sync_button,
                    self.edit_button,
                    self.back_button
                ], alignment=ft.MainAxisAlignment.END),
                self.progress_bar
            ], spacing=0),
            padding=10,
        )

        self.page.add(ft.Column([self.list_view, self.log_view, footer], expand=True))
        self.update_sync_button_visibility()
        self.page.update()

    def window_event(self, e):
        if e.data == "close":
            self.page.window_destroy()
            sys.exit(0)
