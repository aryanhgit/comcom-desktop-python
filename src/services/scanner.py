import os

from PySide6.QtCore import QObject, QThread, Signal

from src.views.database import Database
from src.views.models import Chapter, LibraryItem
from src.views.natural_sort import natural_key
from src.services.thumbnail import ThumbnailService

COMIC_EXTENSIONS = (".cbz", ".pdf")


class ScannerWorker(QObject):
    item_found = Signal(object)
    progress = Signal(int, int)
    finished = Signal()

    def __init__(self, db: Database, thumbnails: ThumbnailService, folders: list[str]):
        super().__init__()
        self._db = db
        self._thumbnails = thumbnails
        self._folders = folders

    def run(self) -> None:
        entries = []
        for folder in self._folders:
            if os.path.isdir(folder):
                entries.extend(self._top_level_entries(folder))

        existing_paths = {entry for entry in entries}
        total = len(entries)

        for index, entry_path in enumerate(entries, start=1):
            item = self._process_entry(entry_path)
            if item is not None:
                self.item_found.emit(item)
            self.progress.emit(index, total)

        self._db.prune_missing(existing_paths)
        self.finished.emit()

    def _top_level_entries(self, folder: str) -> list[str]:
        return [os.path.join(folder, name) for name in sorted(os.listdir(folder))]

    def _process_entry(self, entry_path: str) -> LibraryItem | None:
        if os.path.isdir(entry_path):
            return self._process_series(entry_path)
        if entry_path.lower().endswith(COMIC_EXTENSIONS):
            return self._process_single_comic(entry_path)
        return None

    def _process_single_comic(self, path: str) -> LibraryItem:
        title = os.path.splitext(os.path.basename(path))[0]
        cover = self._thumbnails.get_or_create(path)
        pages = self._thumbnails.page_count(path)

        item_id = self._db.upsert_library_item(path, title, "comic", cover, pages)
        chapter = Chapter(None, item_id, path, title, pages, 0)
        self._db.replace_chapters(item_id, [chapter])

        return LibraryItem(item_id, path, title, "comic", cover, pages, "", False)

    def _process_series(self, folder: str) -> LibraryItem | None:
        chapter_paths = sorted(
            (
                os.path.join(folder, name)
                for name in os.listdir(folder)
                if name.lower().endswith(COMIC_EXTENSIONS)
            ),
            key=lambda p: natural_key(os.path.basename(p)),
        )
        if not chapter_paths:
            return None

        title = os.path.basename(folder)
        cover = self._thumbnails.get_or_create(chapter_paths[0])
        total_pages = sum(self._thumbnails.page_count(p) for p in chapter_paths)

        item_id = self._db.upsert_library_item(folder, title, "series", cover, total_pages)
        chapters = [
            Chapter(
                None,
                item_id,
                path,
                os.path.splitext(os.path.basename(path))[0],
                self._thumbnails.page_count(path),
                index,
            )
            for index, path in enumerate(chapter_paths)
        ]
        self._db.replace_chapters(item_id, chapters)

        return LibraryItem(item_id, folder, title, "series", cover, total_pages, "", False, len(chapters))


class LibraryScanner(QObject):
    item_found = Signal(object)
    progress = Signal(int, int)
    finished = Signal()

    def __init__(self, db: Database, thumbnails: ThumbnailService):
        super().__init__()
        self._db = db
        self._thumbnails = thumbnails
        self._thread: QThread | None = None
        self._worker: ScannerWorker | None = None

    def scan(self, folders: list[str]) -> None:
        self._thread = QThread()
        self._worker = ScannerWorker(self._db, self._thumbnails, folders)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.item_found.connect(self.item_found)
        self._worker.progress.connect(self.progress)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self.finished)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()
