import hashlib
import os
import zipfile

import fitz
from PIL import Image

from src.views.natural_sort import natural_key

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
THUMBNAIL_WIDTH = 400


class ThumbnailService:
    def __init__(self, cache_dir: str):
        self._cache_dir = cache_dir

    def get_or_create(self, source_path: str) -> str | None:
        cache_path = self._cache_path_for(source_path)
        if os.path.exists(cache_path):
            return cache_path

        image = self._extract_cover(source_path)
        if image is None:
            return None

        image.thumbnail((THUMBNAIL_WIDTH, THUMBNAIL_WIDTH * 2))
        image.convert("RGB").save(cache_path, "JPEG", quality=85)
        return cache_path

    def _cache_path_for(self, source_path: str) -> str:
        stat = os.stat(source_path)
        key = f"{source_path}:{stat.st_mtime_ns}:{stat.st_size}"
        digest = hashlib.sha1(key.encode()).hexdigest()
        return os.path.join(self._cache_dir, f"{digest}.jpg")

    def _extract_cover(self, source_path: str) -> Image.Image | None:
        if source_path.lower().endswith(".cbz"):
            return self._extract_cbz_cover(source_path)
        if source_path.lower().endswith(".pdf"):
            return self._extract_pdf_cover(source_path)
        return None

    def _extract_cbz_cover(self, path: str) -> Image.Image | None:
        with zipfile.ZipFile(path) as archive:
            names = sorted(
                (n for n in archive.namelist() if n.lower().endswith(IMAGE_EXTENSIONS)),
                key=natural_key,
            )
            if not names:
                return None
            with archive.open(names[0]) as file:
                return Image.open(file).copy()

    def _extract_pdf_cover(self, path: str) -> Image.Image | None:
        document = fitz.open(path)
        if document.page_count == 0:
            return None
        page = document.load_page(0)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        mode = "RGBA" if pixmap.alpha else "RGB"
        return Image.frombytes(mode, (pixmap.width, pixmap.height), pixmap.samples)

    def page_count(self, source_path: str) -> int:
        if source_path.lower().endswith(".cbz"):
            with zipfile.ZipFile(source_path) as archive:
                return sum(
                    1 for n in archive.namelist() if n.lower().endswith(IMAGE_EXTENSIONS)
                )
        if source_path.lower().endswith(".pdf"):
            return fitz.open(source_path).page_count
        return 0
