import logging
from typing import TYPE_CHECKING, Any, Optional, Union

from PySide6.QtCore import QObject, QThreadPool, QUrl, Signal, Slot
from PySide6.QtGui import QDesktopServices, QPixmap

from src.models.comic_loader_factory import ComicLoaderFactory
from src.models.constants import HELP_URL
from src.models.main_model import MainModel

if TYPE_CHECKING:
    from src.models.comic import Comic

logger = logging.getLogger(__name__)

class MainController(QObject):
    """
    This class serves as the intermediatory between the model and the view.
    It handles user interactions and updates the view accordingly.
    """

    # Signals 
    # updateCentralWidgetContentSignal = Signal(QPixmap, int)
    # updatePageBoxSignal = Signal(int, int)
    # updateWindowTitleSignal = Signal(str)
    # closeMainWindowSignal = Signal()
    # updatePageActionsSignal = Signal(bool, bool)
    # loadProgressSignal = Signal(int)
    # startProgressSignal = Signal(int)
    # doneProgressSignal = Signal()
    # errorLoadSignal = Signal(str)
    # finishProgressSignal = Signal()

    def __init__(self, model: MainModel) -> None:
        """
        Initializes the MainController.
        
        Args: 
            model (MainModel): The model instance to be controlled.
        """
        super().__init__()
        self._mainModel: MainModel = model
        self._loader: Union[None, Comic] = None
        self.threadpool: Union[None, QThreadPool] = None
