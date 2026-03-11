from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QSlider, QLabel, QFileDialog, QFrame
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QPalette

class UIOverlay(QWidget):
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    rate_changed = pyqtSignal(float)
    save_clicked = pyqtSignal()
    close_clicked = pyqtSignal()
    seek_requested = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setup_ui()
        self.old_pos = None
        self.current_rate = 0.8

    def setup_ui(self):
        # Main Container
        self.container = QFrame(self)
        self.container.setObjectName("MainContainer")
        self.container.setStyleSheet("""
            #MainContainer {
                background-color: rgba(30, 30, 35, 230);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 30);
            }
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 20);
                border-radius: 5px;
            }
            QLabel {
                color: #e0e0e0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #333;
                height: 4px;
                background: #555;
                margin: 2px 0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #0078d4;
                width: 14px;
                height: 14px;
                margin: -6px 0;
                border-radius: 7px;
            }
        """)

        layout = QVBoxLayout(self.container)
        
        # Top bar (Drag handle substitute & Close)
        top_layout = QHBoxLayout()
        self.title_label = QLabel("Leitor de Voz")
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(25, 25)
        self.close_btn.clicked.connect(self.close_clicked.emit)
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()
        top_layout.addWidget(self.close_btn)
        layout.addLayout(top_layout)

        # Progress Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.seek_requested.emit)
        layout.addWidget(self.slider)

        # Controls
        controls_layout = QHBoxLayout()
        
        self.rate_down_btn = QPushButton("-")
        self.rate_down_btn.setFixedSize(30, 30)
        self.rate_down_btn.clicked.connect(self.decrease_rate)
        
        self.play_pause_btn = QPushButton("▶")
        self.play_pause_btn.setFixedSize(40, 40)
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        
        self.rate_up_btn = QPushButton("+")
        self.rate_up_btn.setFixedSize(30, 30)
        self.rate_up_btn.clicked.connect(self.increase_rate)
        
        self.rate_label = QLabel("0.8x")
        self.rate_label.setFixedWidth(40)
        self.rate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.time_left_label = QLabel("-00:00")
        self.time_left_label.setFixedWidth(60)
        self.time_left_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.time_left_label.setStyleSheet("font-weight: bold; color: #aaa;")

        self.save_btn = QPushButton("⤴️") # Using a cleaner 'export' style icon
        self.save_btn.setFixedSize(35, 35)
        self.save_btn.setToolTip("Salvar Áudio")

        controls_layout.addWidget(self.rate_down_btn)
        controls_layout.addWidget(self.rate_label)
        controls_layout.addWidget(self.rate_up_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(self.play_pause_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(self.time_left_label)
        controls_layout.addWidget(self.save_btn)
        
        layout.addLayout(controls_layout)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.container)
        self.setLayout(main_layout)
        self.setFixedSize(350, 130)

    def toggle_play_pause(self):
        if self.play_pause_btn.text() == "▶":
            self.play_clicked.emit()
            self.play_pause_btn.setText("⏸")
        else:
            self.pause_clicked.emit()
            self.play_pause_btn.setText("▶")

    def set_playing(self, playing):
        self.play_pause_btn.setText("⏸" if playing else "▶")

    def increase_rate(self):
        self.current_rate = round(min(self.current_rate + 0.1, 2.0), 1)
        self.rate_label.setText(f"{self.current_rate}x")
        self.rate_changed.emit(self.current_rate)

    def decrease_rate(self):
        self.current_rate = round(max(self.current_rate - 0.1, 0.5), 1)
        self.rate_label.setText(f"{self.current_rate}x")
        self.rate_changed.emit(self.current_rate)

    def reset_progress(self):
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        self.time_left_label.setText("-00:00")

    def update_progress(self, position, duration):
        if duration > 0:
            self.slider.setRange(0, duration)
            self.slider.setValue(position)
            
            # Countdown logic
            remaining_ms = duration - position
            # Adjusted by playback rate
            if self.current_rate > 0:
                adjusted_remaining_sec = (remaining_ms / 1000.0) / self.current_rate
            else:
                adjusted_remaining_sec = (remaining_ms / 1000.0)
            
            minutes = int(adjusted_remaining_sec // 60)
            seconds = int(adjusted_remaining_sec % 60)
            self.time_left_label.setText(f"-{minutes:02}:{seconds:02}")

    # Dragging logic
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
