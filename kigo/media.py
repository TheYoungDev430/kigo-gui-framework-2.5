# kigo/media.py
Kigo Media Player v1.7
from __future__ import annotations
from typing import Optional

from kigo.qt import QtCore, QtWidgets

Qt = QtCore.Qt

def _load_multimedia():
    try:
        # QtPy provides these if the selected binding has them
        from qtpy import QtMultimedia, QtMultimediaWidgets
        return QtMultimedia, QtMultimediaWidgets
    except Exception:
        return None, None


class AudioPlayerWidget(QtWidgets.QWidget):
    def __init__(self, path: str = ""):
        super().__init__()
        self.qt_widget = self

        QtMultimedia, _ = _load_multimedia()
        if QtMultimedia is None:
            raise ImportError("QtMultimedia not available. Install a Qt build that includes multimedia support.")

        self.player = QtMultimedia.QMediaPlayer(self)
        self.audio = QtMultimedia.QAudioOutput(self)
        self.player.setAudioOutput(self.audio)

        self.play_btn = QtWidgets.QPushButton("Play")
        self.seek = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.vol = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.vol.setRange(0, 100)
        self.vol.setValue(60)
        self.audio.setVolume(0.6)

        self.play_btn.clicked.connect(self.toggle)
        self.seek.sliderMoved.connect(lambda ms: self.player.setPosition(int(ms)))
        self.vol.valueChanged.connect(lambda v: self.audio.setVolume(v / 100.0))

        self.player.positionChanged.connect(self._on_pos)
        self.player.durationChanged.connect(lambda d: self.seek.setRange(0, int(d)))

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.play_btn)
        layout.addWidget(self.seek)
        layout.addWidget(QtWidgets.QLabel("Volume"))
        layout.addWidget(self.vol)

        if path:
            self.set_source(path)

    def set_source(self, path: str):
        self.player.setSource(QtCore.QUrl.fromLocalFile(path))

    def toggle(self):
        st = self.player.playbackState()
        if st == self.player.PlaybackState.PlayingState:
            self.player.pause()
            self.play_btn.setText("Play")
        else:
            self.player.play()
            self.play_btn.setText("Pause")

    def _on_pos(self, ms: int):
        if not self.seek.isSliderDown():
            self.seek.setValue(int(ms))


class VideoPlayerWidget(QtWidgets.QWidget):
    def __init__(self, path: str = ""):
        super().__init__()
        self.qt_widget = self

        QtMultimedia, QtMultimediaWidgets = _load_multimedia()
        if QtMultimedia is None or QtMultimediaWidgets is None:
            raise ImportError("QtMultimedia/QtMultimediaWidgets not available. Install multimedia support.")

        self.player = QtMultimedia.QMediaPlayer(self)
        self.audio = QtMultimedia.QAudioOutput(self)
        self.player.setAudioOutput(self.audio)

        self.video = QtMultimediaWidgets.QVideoWidget(self)
        self.player.setVideoOutput(self.video)

        self.play_btn = QtWidgets.QPushButton("Play")
        self.seek = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.vol = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.vol.setRange(0, 100)
        self.vol.setValue(60)
        self.audio.setVolume(0.6)

        self.play_btn.clicked.connect(self.toggle)
        self.seek.sliderMoved.connect(lambda ms: self.player.setPosition(int(ms)))
        self.vol.valueChanged.connect(lambda v: self.audio.setVolume(v / 100.0))

        self.player.positionChanged.connect(self._on_pos)
        self.player.durationChanged.connect(lambda d: self.seek.setRange(0, int(d)))

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.video)
        layout.addWidget(self.seek)
        layout.addWidget(self.play_btn)
        layout.addWidget(QtWidgets.QLabel("Volume"))
        layout.addWidget(self.vol)

        if path:
            self.set_source(path)

    def set_source(self, path: str):
        self.player.setSource(QtCore.QUrl.fromLocalFile(path))

    def toggle(self):
        st = self.player.playbackState()
        if st == self.player.PlaybackState.PlayingState:
            self.player.pause()
            self.play_btn.setText("Play")
        else:
            self.player.play()
            self.play_btn.setText("Pause")

    def _on_pos(self, ms: int):
        if not self.seek.isSliderDown():
            self.seek.setValue(int(ms))
