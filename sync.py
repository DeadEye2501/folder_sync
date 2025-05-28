from typing import Union
import os
import shutil
from dataclasses import dataclass
from logger import SyncLogger

IGNORE_FOLDERS = ['.git', '.stfolder']

@dataclass
class SyncItem:
    name: str
    source: Union[str, list[str]]
    destination: str

class Sync:
    def count_files(self, path: str) -> int:
        if isinstance(path, list):
            return len(path)
        
        if os.path.isfile(path):
            return 1
        
        total = 0
        for entry in os.scandir(path):
            name = os.path.basename(entry.path)
            if name in IGNORE_FOLDERS:
                continue
            if entry.is_file():
                total += 1
            elif entry.is_dir():
                total += self.count_files(entry.path)
        return total

    def sync_items(self, items: list[SyncItem], progress_callback=None, log_callback=None):
        logger = SyncLogger(progress_callback, log_callback)
        
        for item in items:
            if not os.path.exists(item.destination):
                continue

            if isinstance(item.source, list):
                self._sync_file_list(item, logger)
            else:
                self._sync_directory(item, logger)
            logger.finish_item()

    def _sync_file_list(self, item: SyncItem, logger: SyncLogger):
        logger.start_item(item.name, len(item.source))
        for source_file in item.source:
            if not os.path.exists(source_file):
                logger.file_error()
                continue
            
            dest_file = os.path.join(item.destination, os.path.basename(source_file))
            self._sync_file(source_file, dest_file, logger)

    def _sync_file(self, source_file: str, dest_file: str, logger: SyncLogger):
        if os.path.exists(dest_file):
            source_stat = os.stat(source_file)
            dest_stat = os.stat(dest_file)
            source_mtime = int(source_stat.st_mtime // 60)
            dest_mtime = int(dest_stat.st_mtime // 60)
            if source_stat.st_size == dest_stat.st_size and source_mtime == dest_mtime:
                logger.file_ignored()
                return
            try:
                shutil.copy2(source_file, dest_file)
                os.utime(dest_file, (source_stat.st_atime, source_stat.st_mtime))
                logger.file_updated()
            except Exception:
                logger.file_error()
        else:
            try:
                shutil.copy2(source_file, dest_file)
                source_stat = os.stat(source_file)
                os.utime(dest_file, (source_stat.st_atime, source_stat.st_mtime))
                logger.file_added()
            except Exception:
                logger.file_error()

    def _sync_directory(self, item: SyncItem, logger: SyncLogger):
        if self._is_directory_empty(item.source):
            return

        total_files = self.count_files(item.source)
        logger.start_item(item.name, total_files)

        self._sync_directory_recursive(item, logger)

    def _sync_directory_recursive(self, item: SyncItem, logger: SyncLogger):
        os.makedirs(item.destination, exist_ok=True)

        self._copy_source_files(item.source, item.destination, logger)
        self._remove_extra_files(item.source, item.destination, logger)

        for subdir in self._get_subdirectories(item.source):
            source_subdir = os.path.join(item.source, subdir)
            dest_subdir = os.path.join(item.destination, subdir)
            self._sync_directory_recursive(SyncItem(name=subdir, source=source_subdir, destination=dest_subdir), logger)

    def _is_directory_empty(self, path: str) -> bool:
        for entry in os.scandir(path):
            if os.path.basename(entry.path) in IGNORE_FOLDERS:
                continue
            return False
        return True

    def _copy_source_files(self, source: str, destination: str, logger: SyncLogger):
        for entry in os.scandir(source):
            if entry.is_file():
                source_file = entry.path
                dest_file = os.path.join(destination, entry.name)
                self._sync_file(source_file, dest_file, logger)

    def _remove_extra_files(self, source: str, destination: str, logger: SyncLogger):
        if not os.path.exists(destination):
            return

        for entry in os.scandir(destination):
            if entry.is_file():
                source_file = os.path.join(source, entry.name)
                if not os.path.exists(source_file):
                    try:
                        os.remove(entry.path)
                        logger.file_deleted()
                    except Exception:
                        logger.file_error()

    def _get_subdirectories(self, path: str) -> list[str]:
        subdirs = []
        for entry in os.scandir(path):
            if entry.is_dir() and os.path.basename(entry.path) not in IGNORE_FOLDERS:
                subdirs.append(entry.name)
        return subdirs
