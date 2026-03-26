from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QSlider, QLabel, QComboBox,
)
from PyQt6.QtCore import Qt, pyqtSignal


class ControlPanel(QWidget):
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    step_forward = pyqtSignal()
    step_backward = pyqtSignal()
    jump_start = pyqtSignal()
    jump_end = pyqtSignal()
    speed_changed = pyqtSignal(float)
    algorithm_changed = pyqtSignal(str)
    graph_changed = pyqtSignal(str)

    # Slider range maps 1..20 -> 0.1x..10.0x (step of 0.5x per tick)
    _SPEED_MIN = 1
    _SPEED_MAX = 20

    def __init__(self, parent=None):
        super().__init__(parent)

        self._playing = False

        outer = QVBoxLayout(self)
        outer.setContentsMargins(6, 4, 6, 4)
        outer.setSpacing(4)

        # ── Row 1: graph / algorithm selectors ──────────────────────────
        row1 = QHBoxLayout()
        row1.setSpacing(8)

        graph_label = QLabel("Graph:")
        self._graph_combo = QComboBox()
        self._graph_combo.addItems([
            "Demo 9V",
            "Random 20V",
            "Grid 5x5",
            "Obstacle Grid 5x5",
        ])

        algo_label = QLabel("Algorithm:")
        self._algo_combo = QComboBox()
        self._algo_combo.addItems([
            "Kruskal",
            "Prim",
            "Dijkstra",
            "Dijkstra Obstacle",
        ])

        row1.addWidget(graph_label)
        row1.addWidget(self._graph_combo)
        row1.addSpacing(16)
        row1.addWidget(algo_label)
        row1.addWidget(self._algo_combo)
        row1.addStretch()

        # ── Row 2: playback controls ─────────────────────────────────────
        row2 = QHBoxLayout()
        row2.setSpacing(4)

        self._btn_jump_start = QPushButton("|<")
        self._btn_jump_start.setFixedWidth(36)
        self._btn_jump_start.setToolTip("Jump to start")

        self._btn_step_back = QPushButton("<")
        self._btn_step_back.setFixedWidth(36)
        self._btn_step_back.setToolTip("Step backward")

        self._btn_play_pause = QPushButton("Play")
        self._btn_play_pause.setFixedWidth(64)
        self._btn_play_pause.setToolTip("Play / Pause")

        self._btn_step_fwd = QPushButton(">")
        self._btn_step_fwd.setFixedWidth(36)
        self._btn_step_fwd.setToolTip("Step forward")

        self._btn_jump_end = QPushButton(">|")
        self._btn_jump_end.setFixedWidth(36)
        self._btn_jump_end.setToolTip("Jump to end")

        speed_label = QLabel("Speed:")
        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setRange(self._SPEED_MIN, self._SPEED_MAX)
        self._speed_slider.setValue(2)          # default: 1.0x
        self._speed_slider.setFixedWidth(120)
        self._speed_slider.setToolTip("Playback speed")

        self._speed_value_label = QLabel("1.0x")
        self._speed_value_label.setFixedWidth(40)

        self._step_counter = QLabel("Step: 0 / 0")

        row2.addWidget(self._btn_jump_start)
        row2.addWidget(self._btn_step_back)
        row2.addWidget(self._btn_play_pause)
        row2.addWidget(self._btn_step_fwd)
        row2.addWidget(self._btn_jump_end)
        row2.addSpacing(12)
        row2.addWidget(speed_label)
        row2.addWidget(self._speed_slider)
        row2.addWidget(self._speed_value_label)
        row2.addSpacing(16)
        row2.addWidget(self._step_counter)
        row2.addStretch()

        outer.addLayout(row1)
        outer.addLayout(row2)

        # ── Wire internal signals ────────────────────────────────────────
        self._btn_jump_start.clicked.connect(self.jump_start)
        self._btn_step_back.clicked.connect(self.step_backward)
        self._btn_play_pause.clicked.connect(self._on_play_pause)
        self._btn_step_fwd.clicked.connect(self.step_forward)
        self._btn_jump_end.clicked.connect(self.jump_end)

        self._speed_slider.valueChanged.connect(self._on_speed_changed)
        self._graph_combo.currentTextChanged.connect(self.graph_changed)
        self._algo_combo.currentTextChanged.connect(self.algorithm_changed)

    # ── Public API ───────────────────────────────────────────────────────

    def set_step_count(self, current: int, total: int) -> None:
        self._step_counter.setText(f"Step: {current} / {total}")

    def set_playing(self, playing: bool) -> None:
        self._playing = playing
        self._btn_play_pause.setText("Pause" if playing else "Play")

    # ── Slots ────────────────────────────────────────────────────────────

    def _on_play_pause(self):
        if self._playing:
            self.pause_clicked.emit()
        else:
            self.play_clicked.emit()

    def _on_speed_changed(self, value: int):
        # Map slider 1..20 -> 0.1..10.0 (each step = 0.5x)
        speed = round(value * 0.5, 1)
        self._speed_value_label.setText(f"{speed}x")
        self.speed_changed.emit(speed)
