import logging
import os

from src.models.constants import LOGGING_VERBOSITY
from src.models.page import Page

logger = logging.getLogger(__name__)
logger.setLevel(LOGGING_VERBOSITY)


class Comic:
    """
    Represents a comic object
    """

    def __init__(self, filename: str, directory: str) -> None:
        self._filename: str = filename
        self._directory: str = directory

        # list of Page: list to store the comic pages objects
        self._pages: list[Page] = []

    def setFilename(self, filename: str) -> None:
        self._filename = filename

    def getFilename(self) -> str:
        return self._filename

    def setDirectory(self, directory: str) -> None:
        self._directory = directory

    def getDirectory(self) -> str:
        return self._directory

    def setPages(self, pages: list[Page]) -> None:
        self._pages = pages

    def getPages(self) -> list[Page]:
        return self._pages

    def getComicPath(self) -> str:
        return os.path.join(self._directory, self._filename)

    def getPageCount(self) -> int:
        return len(self._pages)
