import sqlite3
import threading
from datetime import datetime, timezone
from typing import Optional

from src.views.models import Chapter, LibraryItem

SCHEMA = """
CREATE TABLE IF NOT EXISTS library_folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS library_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('comic', 'series')),
    cover_path TEXT,
    page_count INTEGER DEFAULT 0,
    added_at TEXT NOT NULL,
    is_favorite INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS chapters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    library_item_id INTEGER NOT NULL REFERENCES library_items(id) ON DELETE CASCADE,
    path TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    page_count INTEGER DEFAULT 0,
    sort_index INTEGER DEFAULT 0
);
"""


class Database:
    def __init__(self, path: str):
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._conn.executescript(SCHEMA)
        self._conn.commit()
        self._lock = threading.Lock()

    def close(self) -> None:
        self._conn.close()

    def add_library_folder(self, path: str) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT OR IGNORE INTO library_folders (path) VALUES (?)", (path,)
            )
            self._conn.commit()

    def remove_library_folder(self, path: str) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM library_folders WHERE path = ?", (path,))
            self._conn.commit()

    def get_library_folders(self) -> list[str]:
        with self._lock:
            rows = self._conn.execute("SELECT path FROM library_folders").fetchall()
        return [row["path"] for row in rows]

    def upsert_library_item(
        self, path: str, title: str, kind: str, cover_path: Optional[str], page_count: int
    ) -> int:
        with self._lock:
            existing = self._conn.execute(
                "SELECT id, is_favorite FROM library_items WHERE path = ?", (path,)
            ).fetchone()
            if existing:
                self._conn.execute(
                    """UPDATE library_items
                       SET title = ?, kind = ?, cover_path = ?, page_count = ?
                       WHERE id = ?""",
                    (title, kind, cover_path, page_count, existing["id"]),
                )
                self._conn.commit()
                return existing["id"]

            cursor = self._conn.execute(
                """INSERT INTO library_items (path, title, kind, cover_path, page_count, added_at, is_favorite)
                   VALUES (?, ?, ?, ?, ?, ?, 0)""",
                (path, title, kind, cover_path, page_count, datetime.now(timezone.utc).isoformat()),
            )
            self._conn.commit()
            return cursor.lastrowid

    def replace_chapters(self, library_item_id: int, chapters: list[Chapter]) -> None:
        with self._lock:
            self._conn.execute(
                "DELETE FROM chapters WHERE library_item_id = ?", (library_item_id,)
            )
            self._conn.executemany(
                """INSERT INTO chapters (library_item_id, path, title, page_count, sort_index)
                   VALUES (?, ?, ?, ?, ?)""",
                [
                    (library_item_id, c.path, c.title, c.page_count, c.sort_index)
                    for c in chapters
                ],
            )
            self._conn.commit()

    def prune_missing(self, existing_paths: set[str]) -> None:
        with self._lock:
            rows = self._conn.execute("SELECT id, path FROM library_items").fetchall()
            stale_ids = [row["id"] for row in rows if row["path"] not in existing_paths]
            if stale_ids:
                self._conn.executemany(
                    "DELETE FROM library_items WHERE id = ?", [(i,) for i in stale_ids]
                )
                self._conn.commit()

    def set_favorite(self, item_id: int, is_favorite: bool) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE library_items SET is_favorite = ? WHERE id = ?",
                (int(is_favorite), item_id),
            )
            self._conn.commit()

    def get_all_items(self) -> list[LibraryItem]:
        with self._lock:
            rows = self._conn.execute(
                """SELECT li.*, COUNT(c.id) AS chapter_count
                   FROM library_items li
                   LEFT JOIN chapters c ON c.library_item_id = li.id
                   GROUP BY li.id
                   ORDER BY li.title COLLATE NOCASE"""
            ).fetchall()
        return [
            LibraryItem(
                id=row["id"],
                path=row["path"],
                title=row["title"],
                kind=row["kind"],
                cover_path=row["cover_path"],
                page_count=row["page_count"],
                added_at=row["added_at"],
                is_favorite=bool(row["is_favorite"]),
                chapter_count=row["chapter_count"] or 1,
            )
            for row in rows
        ]
