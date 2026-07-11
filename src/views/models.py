from dataclasses import dataclass
from typing import Optional


@dataclass
class Chapter:
    id: Optional[int]
    library_item_id: int
    path: str
    title: str
    page_count: int
    sort_index: int


@dataclass
class LibraryItem:
    id: Optional[int]
    path: str
    title: str
    kind: str
    cover_path: Optional[str]
    page_count: int
    added_at: str
    is_favorite: bool
    chapter_count: int = 1
