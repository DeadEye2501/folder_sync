from typing import Union
from dataclasses import dataclass
import json
from sync import Sync, SyncItem
from gui import App
import flet as ft
import os

@dataclass
class SyncItem:
    name: str
    source: Union[str, list[str]]
    destination: str

@dataclass
class SyncGroup:
    name: str
    items: list[SyncItem]

def load_config(config_path: str) -> list[SyncGroup]:
    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    groups = []
    for group_name, items_data in data.items():
        items = []
        for item_name, paths in items_data.items():
            source = paths[0]
            destination = paths[1]
            items.append(SyncItem(name=item_name, source=source, destination=destination))
        groups.append(SyncGroup(name=group_name, items=items))
    
    return groups

def select_items(groups: list[SyncGroup]) -> list[SyncItem]:
    selected_items = []
    
    for group in groups:
        print(f"\nГруппа: {group.name}")
        response = input("Синхронизировать группу? (y/n/all): ").lower()
        
        if response == 'n':
            continue
        elif response == 'all':
            selected_items.extend(group.items)
        elif response == 'y':
            for item in group.items:
                print(f"\n  Элемент: {item.name}")
                if isinstance(item.source, list):
                    print(f"  {len(item.source)} файлов -> {item.destination}")
                else:
                    print(f"  {item.source} -> {item.destination}")
                item_response = input("  Синхронизировать элемент? (y/n): ").lower()
                if item_response == 'y':
                    selected_items.append(item)
        else:
            print("Пожалуйста, введите 'y', 'n' или 'all'")
    
    return selected_items

if __name__ == '__main__':
    if not os.path.exists('config.json'):
        with open('config.json', 'w', encoding='utf-8') as f:
            f.write('{}')
    groups = load_config('config.json')
    app = App(groups)
    ft.app(target=app.main, assets_dir=".")
