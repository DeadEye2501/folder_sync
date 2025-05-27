from dataclasses import dataclass, field
from typing import Dict, Optional, Callable
import time

@dataclass
class SyncStats:
    updated: int = 0
    added: int = 0
    deleted: int = 0
    ignored: int = 0
    errors: int = 0

class SyncLogger:
    def __init__(self, progress_callback: Optional[Callable[[str, str], None]] = None):
        self.stats = SyncStats()
        self.current_group = ""
        self.current_item = ""
        self.total_files = 0
        self.processed_files = 0
        self.start_time = 0
        self.dots = ""
        self.progress_callback = progress_callback

    def start_group(self, group_name: str):
        self.current_group = group_name
        self.stats = SyncStats()
        if self.progress_callback:
            self.progress_callback(f"Начата синхронизация группы: {group_name}", "")
        else:
            print(f"\nНачата синхронизация группы: {group_name}")

    def start_item(self, item_name: str, total_files: int):
        self.current_item = item_name
        self.total_files = total_files
        self.processed_files = 0
        self.start_time = time.time()
        self._update_progress()

    def update_progress(self, file_count: int = 1):
        self.processed_files += file_count
        self._update_progress()

    def _update_progress(self):
        if self.total_files == 0:
            percentage = 100
        else:
            percentage = min(100, int((self.processed_files / self.total_files) * 100))
        
        stats = []
        if self.stats.updated > 0:
            stats.append(f"updated: {self.stats.updated}")
        if self.stats.added > 0:
            stats.append(f"added: {self.stats.added}")
        if self.stats.deleted > 0:
            stats.append(f"deleted: {self.stats.deleted}")
        if self.stats.ignored > 0:
            stats.append(f"ignored: {self.stats.ignored}")
        if self.stats.errors > 0:
            stats.append(f"errors: {self.stats.errors}")
        
        progress = f"{self.current_item} {percentage}% ({', '.join(stats)})"
        if self.progress_callback:
            self.progress_callback(progress, "")
        else:
            print(f"\n{progress}", end="", flush=True)

    def file_updated(self):
        self.stats.updated += 1
        self.update_progress()

    def file_added(self):
        self.stats.added += 1
        self.update_progress()

    def file_deleted(self):
        self.stats.deleted += 1
        self.update_progress()

    def file_ignored(self):
        self.stats.ignored += 1
        self.update_progress()

    def file_error(self):
        self.stats.errors += 1
        self.update_progress()

    def finish_item(self):
        if not self.progress_callback:
            print() 