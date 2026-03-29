from kigo.qt import QtGui

@lru_cache(maxsize=256)
def load_pixmap(path: str) -> QtGui.QPixmap:
    """
    Load an image once and keep it in RAM.
    """
    pix = QtGui.QPixmap(path)
    if pix.isNull():
        raise FileNotFoundError(path)
    return pix

