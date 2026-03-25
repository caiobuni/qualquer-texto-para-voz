from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, QObject, pyqtSignal

class AudioPlayer(QObject):
    state_changed = pyqtSignal(QMediaPlayer.PlaybackState)
    position_changed = pyqtSignal(int)
    duration_changed = pyqtSignal(int)
    playback_rate_changed = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        
        # Connect signals
        self.player.playbackStateChanged.connect(self.state_changed.emit)
        self.player.positionChanged.connect(self.position_changed.emit)
        self.player.durationChanged.connect(self.duration_changed.emit)
        self.player.playbackRateChanged.connect(self.playback_rate_changed.emit)

        self.current_rate = 0.8

    def load(self, file_path):
        # Recriar QAudioOutput para usar o dispositivo padrão atual do sistema
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl())  # Clear previous source
        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.player.setPlaybackRate(self.current_rate)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def set_rate(self, rate):
        self.current_rate = rate
        self.player.setPlaybackRate(rate)

    def get_rate(self):
        return self.current_rate

    def set_position(self, position):
        self.player.setPosition(position)
