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
    def __init__(self, progress_callback: Optional[Callable[[str, str], None]] = None, log_callback: Optional[Callable[[str], None]] = None):
        self.stats = SyncStats()
        self.current_group = ""
        self.current_item = ""
        self.total_files = 0
        self.processed_files = 0
        self.start_time = 0
        self.dots = ""
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.last_stats_update = 0

    def start_group(self, group_name: str):
        self.current_group = group_name
        self.stats = SyncStats()
        if self.progress_callback:
            self.progress_callback("0", "0")
        if self.log_callback:
            self.log_callback(f"Синхронизация: {group_name}", True)

    def start_item(self, item_name: str, total_files: int):
        self.current_item = item_name
        self.total_files = total_files
        self.processed_files = 0
        self.start_time = time.time()
        self.last_stats_update = 0
        self.stats = SyncStats()
        if self.log_callback:
            self.log_callback(f"{self.current_item} ... ()", True)
        self._update_progress(force=True)

    def update_progress(self, file_count: int = 1):
        self.processed_files += file_count
        self._update_progress()

    def _update_progress(self, force=False):
        now = time.time()
        if force or now - self.last_stats_update >= 1:
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
            stats_str = ", ".join(stats)
            if self.log_callback:
                self.log_callback(f"{self.current_item} ... ({stats_str})", False)
            self.last_stats_update = now
        if self.progress_callback:
            self.progress_callback(str(self.processed_files), str(self.total_files))

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
        self._update_progress(force=True)
        if not self.progress_callback and not self.log_callback:
            print() 