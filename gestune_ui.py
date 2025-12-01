"""
Gestune Modern UI - PyQt6
Professional and modern UI for Gestune application
Features: Clean design, responsive layout, real-time visualization
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QGroupBox, QGridLayout, QFrame, 
    QProgressBar, QSpacerItem, QSizePolicy, QStatusBar, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QImage, QPixmap, QFont, QIcon, QPainter, QColor
import cv2
import numpy as np
from typing import Optional, Dict, List, Tuple
from enum import Enum

from patterns import DRUM_PATTERNS


class HandSide(Enum):
    """Enum for hand sides."""
    LEFT = "left"
    RIGHT = "right"


class AnimatedProgressBar(QProgressBar):
    """Custom progress bar with smooth animation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._animation = QPropertyAnimation(self, b"value")
        self._animation.setDuration(150)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def animateToValue(self, value: int):
        """Animate to a target value."""
        self._animation.stop()
        self._animation.setStartValue(self.value())
        self._animation.setEndValue(value)
        self._animation.start()


class GestuneUI(QMainWindow):
    """
    Main UI Window for Gestune Application
    
    Features:
    - Live camera feed with hand tracking visualization
    - Real-time metrics and controls
    - Interactive BPM and pattern controls
    - Professional dark theme design
    - Smooth animations
    """
    
    # Signals
    bpm_changed = pyqtSignal(int)
    pattern_changed = pyqtSignal(int)
    reset_requested = pyqtSignal()
    
    # Constants
    MIN_BPM = 40
    MAX_BPM = 300
    DEFAULT_BPM = 120
    BPM_STEP = 10
    
    DRUM_DISPLAY_NAMES = {
        'kick': '🥁 KICK',
        'snare': '🎺 SNARE',
        'hihat': '🎩 HI-HAT',
        'hightom': '🥁 TOM',
        'crashcymbal': '💥 CRASH'
    }
    
    DRUM_COLORS = {
        'kick': '#FF5252',
        'snare': '#FFD740',
        'hihat': '#69F0AE',
        'hightom': '#FF80AB',
        'crashcymbal': '#40C4FF'
    }
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎵 Gestune - Musik dari Gerakan Tangan")
        self.setMinimumSize(1400, 850)
        self.resize(1600, 900)
        
        # Fade-out timers for drum indicators
        self.drum_fade_timers: Dict[str, QTimer] = {}
        
        # Performance tracking
        self.frame_count = 0
        self.fps_update_timer = QTimer()
        self.fps_update_timer.timeout.connect(self._update_fps_display)
        
        # Initialize UI
        self.setup_ui()
        
        # Status bar with rich information
        self.statusBar().showMessage("🎵 Ready - Gestune v2.0 | Modern Hand Gesture Music Controller")
        
    def setup_ui(self):
        """Setup the complete user interface"""
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create panels
        camera_panel = self.create_camera_panel()
        control_panel = self.create_control_panel()
        
        # Add panels with proper sizing (65% camera, 35% controls)
        main_layout.addWidget(camera_panel, 65)
        main_layout.addWidget(control_panel, 35)
        
        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Apply modern stylesheet
        self.apply_stylesheet()
    
    def apply_stylesheet(self):
        """Apply modern dark theme stylesheet with improved visuals"""
        self.setStyleSheet("""
            /* Main Window */
            QMainWindow {
                background-color: #0d1117;
            }
            
            /* Camera Panel */
            QFrame#cameraPanel {
                background-color: #161b22;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #21262d;
            }
            
            /* Camera Feed */
            QLabel#cameraFeed {
                background-color: #000000;
                border: 3px solid #1f6feb;
                border-radius: 10px;
                color: #8b949e;
                font-size: 16px;
                padding: 20px;
            }
            
            /* Control Panel */
            QFrame#controlPanel {
                background-color: #161b22;
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #21262d;
            }
            
            /* Panel Titles */
            QLabel#panelTitle {
                color: #58a6ff;
                padding: 10px 15px;
                background-color: #0d1117;
                border-radius: 8px;
                border-left: 4px solid #1f6feb;
                font-weight: bold;
            }
            
            /* Group Boxes */
            QGroupBox#controlGroup {
                background-color: #0d1117;
                border: 2px solid #30363d;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 20px;
                font-size: 13px;
                font-weight: bold;
                color: #c9d1d9;
            }
            
            QGroupBox#controlGroup::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background-color: #161b22;
                border-radius: 4px;
                color: #58a6ff;
                left: 10px;
            }
            
            /* Status Indicators */
            QLabel#statusInactive {
                color: #6e7681;
                padding: 8px 15px;
                background-color: #0d1117;
                border: 2px solid #30363d;
                border-radius: 6px;
                font-weight: bold;
            }
            
            QLabel#statusActive {
                color: #3fb950;
                padding: 8px 15px;
                background-color: #0d1117;
                border: 2px solid #238636;
                border-radius: 6px;
                font-weight: bold;
            }
            
            /* BPM Display */
            QLabel#bpmDisplay {
                color: #58a6ff;
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1f2937,
                    stop:1 #0d1117
                );
                border: 3px solid #1f6feb;
                border-radius: 10px;
                padding: 15px 25px;
                font-weight: bold;
            }
            
            /* Slider */
            QSlider#bpmSlider {
                height: 35px;
            }
            
            QSlider#bpmSlider::groove:horizontal {
                background: #30363d;
                height: 8px;
                border-radius: 4px;
            }
            
            QSlider#bpmSlider::handle:horizontal {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #79c0ff,
                    stop:1 #58a6ff
                );
                border: 2px solid #1f6feb;
                width: 20px;
                height: 20px;
                margin: -8px 0;
                border-radius: 10px;
            }
            
            QSlider#bpmSlider::handle:horizontal:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a5d6ff,
                    stop:1 #79c0ff
                );
                border: 2px solid #58a6ff;
                width: 22px;
                height: 22px;
                margin: -9px 0;
            }
            
            QSlider#bpmSlider::sub-page:horizontal {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1f6feb,
                    stop:1 #58a6ff
                );
                border-radius: 4px;
            }
            
            /* Buttons */
            QPushButton#controlButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2d333b,
                    stop:1 #21262d
                );
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 10px 18px;
                font-size: 12px;
                font-weight: bold;
                min-height: 35px;
            }
            
            QPushButton#controlButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d444d,
                    stop:1 #30363d
                );
                border-color: #58a6ff;
                color: #ffffff;
            }
            
            QPushButton#controlButton:pressed {
                background: #1f6feb;
                color: #ffffff;
                border-color: #1f6feb;
            }
            
            QPushButton#resetButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6e1818,
                    stop:1 #4d1212
                );
                color: #ff7b72;
                border: 1px solid #da3633;
                border-radius: 6px;
                padding: 10px 18px;
                font-weight: bold;
            }
            
            QPushButton#resetButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8e2424,
                    stop:1 #6e1818
                );
                border-color: #ff7b72;
                color: #ffffff;
            }
            
            /* Guide Frames */
            QFrame#guideFrame {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 12px;
            }
            
            QLabel#guideTitle {
                color: #58a6ff;
                font-weight: bold;
            }
            
            QLabel#guideText {
                color: #8b949e;
                line-height: 1.8;
            }
            
            /* Metric Values */
            QLabel#metricValue {
                color: #3fb950;
                font-family: 'Consolas', 'Courier New', monospace;
                font-weight: bold;
            }
            
            QLabel#metricLabel {
                color: #8b949e;
                font-weight: bold;
            }
            
            /* Progress Bars (Drum Indicators) */
            QProgressBar#drumIndicator {
                border: 2px solid #30363d;
                border-radius: 6px;
                background-color: #0d1117;
                text-align: center;
                min-height: 30px;
            }
            
            QProgressBar#drumIndicator::chunk {
                border-radius: 4px;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #161b22;
                color: #8b949e;
                border-top: 1px solid #30363d;
                padding: 5px 10px;
                font-size: 11px;
            }
            
            /* Scroll Area */
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            /* Tooltips */
            QToolTip {
                background-color: #161b22;
                color: #c9d1d9;
                border: 1px solid #30363d;
                padding: 5px;
                border-radius: 4px;
            }
        """)
    
    def create_camera_panel(self) -> QFrame:
        """Create camera feed panel with enhanced layout"""
        panel = QFrame()
        panel.setObjectName("cameraPanel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        
        # Header with title and status indicators
        header_layout = QHBoxLayout()
        
        title = QLabel("📹 LIVE CAMERA FEED")
        title.setObjectName("panelTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Status indicators
        self.left_hand_status = self.create_status_indicator("TANGAN KIRI")
        self.right_hand_status = self.create_status_indicator("TANGAN KANAN")
        
        header_layout.addWidget(self.left_hand_status)
        header_layout.addWidget(self.right_hand_status)
        
        # Camera display
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(800, 600)
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setObjectName("cameraFeed")
        self.camera_label.setText("⏳ Menunggu kamera...\n\nPastikan webcam terhubung dan diizinkan")
        self.camera_label.setFont(QFont("Segoe UI", 14))
        
        layout.addLayout(header_layout)
        layout.addWidget(self.camera_label, 1)
        
        return panel
    
    def create_status_indicator(self, text: str) -> QLabel:
        """Create a status indicator label with tooltip"""
        label = QLabel(f"◯ {text}")
        label.setObjectName("statusInactive")
        label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        label.setToolTip(f"Status deteksi {text.lower()}")
        return label
    
    def create_control_panel(self) -> QFrame:
        """Create control and visualization panel"""
        panel = QFrame()
        panel.setObjectName("controlPanel")
        
        # Use scroll area for better responsiveness
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🎛️ KONTROL & VISUALISASI")
        title.setObjectName("panelTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Components
        bpm_control = self.create_bpm_control_group()
        pattern_control = self.create_pattern_control_group()
        visualization = self.create_visualization_group()
        hand_guide = self.create_hand_guide_group()
        metrics = self.create_metrics_group()
        
        layout.addWidget(title)
        layout.addWidget(bpm_control)
        layout.addWidget(pattern_control)
        layout.addWidget(visualization)
        layout.addWidget(hand_guide)
        layout.addWidget(metrics)
        layout.addStretch()
        
        scroll.setWidget(content_widget)
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll)
        
        return panel
    
    def create_bpm_control_group(self) -> QGroupBox:
        """Create BPM control group with enhanced controls"""
        group = QGroupBox("⏱️ TEMPO CONTROL")
        group.setObjectName("controlGroup")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # BPM display
        bpm_display = QHBoxLayout()
        bpm_label = QLabel("BPM:")
        bpm_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        
        self.bpm_value = QLabel(str(self.DEFAULT_BPM))
        self.bpm_value.setObjectName("bpmDisplay")
        self.bpm_value.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.bpm_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        bpm_display.addWidget(bpm_label)
        bpm_display.addStretch()
        bpm_display.addWidget(self.bpm_value)
        bpm_display.addStretch()
        
        # BPM slider with labels
        slider_container = QHBoxLayout()
        min_label = QLabel(str(self.MIN_BPM))
        min_label.setFont(QFont("Segoe UI", 10))
        min_label.setStyleSheet("color: #6e7681;")
        
        max_label = QLabel(str(self.MAX_BPM))
        max_label.setFont(QFont("Segoe UI", 10))
        max_label.setStyleSheet("color: #6e7681;")
        
        self.bpm_slider = QSlider(Qt.Orientation.Horizontal)
        self.bpm_slider.setObjectName("bpmSlider")
        self.bpm_slider.setMinimum(self.MIN_BPM)
        self.bpm_slider.setMaximum(self.MAX_BPM)
        self.bpm_slider.setValue(self.DEFAULT_BPM)
        self.bpm_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.bpm_slider.setTickInterval(20)
        self.bpm_slider.valueChanged.connect(self.on_bpm_slider_changed)
        self.bpm_slider.setToolTip("Geser untuk mengubah tempo (BPM)")
        
        slider_container.addWidget(min_label)
        slider_container.addWidget(self.bpm_slider, 1)
        slider_container.addWidget(max_label)
        
        # BPM adjustment buttons
        btn_container = QHBoxLayout()
        btn_slower = QPushButton(f"🐢 LAMBAT (-{self.BPM_STEP})")
        btn_faster = QPushButton(f"🐇 CEPAT (+{self.BPM_STEP})")
        btn_reset = QPushButton("🔄 RESET")
        
        btn_slower.setObjectName("controlButton")
        btn_faster.setObjectName("controlButton")
        btn_reset.setObjectName("controlButton")
        
        btn_slower.clicked.connect(self.decrease_bpm)
        btn_faster.clicked.connect(self.increase_bpm)
        btn_reset.clicked.connect(self.reset_bpm)
        
        btn_slower.setToolTip(f"Kurangi BPM sebesar {self.BPM_STEP}")
        btn_faster.setToolTip(f"Tambah BPM sebesar {self.BPM_STEP}")
        btn_reset.setToolTip(f"Reset BPM ke {self.DEFAULT_BPM}")
        
        btn_container.addWidget(btn_slower)
        btn_container.addWidget(btn_faster)
        btn_container.addWidget(btn_reset)
        
        layout.addLayout(bpm_display)
        layout.addLayout(slider_container)
        layout.addLayout(btn_container)
        
        group.setLayout(layout)
        return group
    
    def create_pattern_control_group(self) -> QGroupBox:
        """Create pattern control group"""
        group = QGroupBox("🎼 PATTERN CONTROL")
        group.setObjectName("controlGroup")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Current pattern display
        pattern_display = QHBoxLayout()
        pattern_label = QLabel("Current Pattern:")
        pattern_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        
        self.pattern_value = QLabel("Pattern 1")
        self.pattern_value.setObjectName("metricValue")
        self.pattern_value.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.pattern_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        pattern_display.addWidget(pattern_label)
        pattern_display.addStretch()
        pattern_display.addWidget(self.pattern_value)
        
        # Pattern buttons
        btn_container = QGridLayout()
        btn_container.setSpacing(8)
        
        self.pattern_buttons = []
        for i in range(len(DRUM_PATTERNS)):
            btn = QPushButton(f"Pattern {i + 1}")
            btn.setObjectName("controlButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self.on_pattern_button_clicked(idx))
            btn.setToolTip(f"Ganti ke Pattern {i + 1}")
            self.pattern_buttons.append(btn)
            btn_container.addWidget(btn, i // 3, i % 3)
        
        # Set first button as checked
        if self.pattern_buttons:
            self.pattern_buttons[0].setChecked(True)
        
        layout.addLayout(pattern_display)
        layout.addLayout(btn_container)
        
        group.setLayout(layout)
        return group
    
    def create_hand_guide_group(self) -> QGroupBox:
        """Create enhanced hand control guide"""
        group = QGroupBox("👋 PANDUAN KONTROL")
        group.setObjectName("controlGroup")
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Left hand guide
        left_hand_frame = QFrame()
        left_hand_frame.setObjectName("guideFrame")
        left_layout = QVBoxLayout(left_hand_frame)
        
        left_title = QLabel("👈 TANGAN KIRI - ARPEGGIATOR")
        left_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        left_title.setObjectName("guideTitle")
        
        left_info = QLabel(
            "• 🎹 Pitch Control: Tinggi tangan\n"
            "• 🎚️ Volume: Jarak jari (pinch)\n"
            "• 🎵 Range: 3 oktaf penuh\n"
            "• ⚡ Real-time response"
        )
        left_info.setObjectName("guideText")
        left_info.setFont(QFont("Segoe UI", 10))
        left_info.setWordWrap(True)
        
        left_layout.addWidget(left_title)
        left_layout.addWidget(left_info)
        
        # Right hand guide
        right_hand_frame = QFrame()
        right_hand_frame.setObjectName("guideFrame")
        right_layout = QVBoxLayout(right_hand_frame)
        
        right_title = QLabel("👉 TANGAN KANAN - DRUM MACHINE")
        right_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        right_title.setObjectName("guideTitle")
        
        right_info = QLabel(
            "• 👍 Jempol: KICK\n"
            "• ☝️ Telunjuk: SNARE\n"
            "• 🖕 Jari tengah: HI-HAT\n"
            "• 💍 Jari manis: TOM\n"
            "• 🤙 Kelingking: CRASH\n"
            "• ✊ Tinju: Ganti pattern"
        )
        right_info.setObjectName("guideText")
        right_info.setFont(QFont("Segoe UI", 10))
        right_info.setWordWrap(True)
        
        right_layout.addWidget(right_title)
        right_layout.addWidget(right_info)
        
        layout.addWidget(left_hand_frame)
        layout.addWidget(right_hand_frame)
        
        group.setLayout(layout)
        return group
    
    def create_visualization_group(self) -> QGroupBox:
        """Create enhanced visualization group for drum hits"""
        group = QGroupBox("🥁 VISUALISASI DRUM")
        group.setObjectName("controlGroup")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Create drum indicators with animation
        self.drum_indicators: Dict[str, AnimatedProgressBar] = {}
        
        for drum_id, drum_label in self.DRUM_DISPLAY_NAMES.items():
            drum_layout = QHBoxLayout()
            
            # Label
            label = QLabel(drum_label)
            label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            label.setFixedWidth(120)
            
            # Animated indicator bar
            indicator = AnimatedProgressBar()
            indicator.setObjectName("drumIndicator")
            indicator.setMaximum(100)
            indicator.setValue(0)
            indicator.setTextVisible(False)
            indicator.setFixedHeight(32)
            
            color = self.DRUM_COLORS.get(drum_id, '#888888')
            indicator.setStyleSheet(f"""
                QProgressBar {{
                    border: 2px solid #30363d;
                    border-radius: 6px;
                    background-color: #0d1117;
                }}
                QProgressBar::chunk {{
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 {color},
                        stop:1 {self._lighten_color(color)}
                    );
                    border-radius: 4px;
                }}
            """)
            
            self.drum_indicators[drum_id] = indicator
            
            drum_layout.addWidget(label)
            drum_layout.addWidget(indicator, 1)
            
            layout.addLayout(drum_layout)
            
            # Initialize fade timer for this drum
            self.drum_fade_timers[drum_id] = QTimer()
            self.drum_fade_timers[drum_id].timeout.connect(
                lambda d=drum_id: self._fade_drum_indicator(d)
            )
        
        group.setLayout(layout)
        return group
    
    def _lighten_color(self, hex_color: str, factor: float = 1.3) -> str:
        """Lighten a hex color for gradient effect."""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def create_metrics_group(self) -> QGroupBox:
        """Create enhanced performance metrics display"""
        group = QGroupBox("📊 METRIK PERFORMA")
        group.setObjectName("controlGroup")
        layout = QGridLayout()
        layout.setSpacing(12)
        layout.setColumnStretch(1, 1)
        
        # FPS Counter
        fps_label = QLabel("FPS:")
        fps_label.setObjectName("metricLabel")
        fps_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.fps_value = QLabel("0.0")
        self.fps_value.setObjectName("metricValue")
        self.fps_value.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        self.fps_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # Detection Counter
        detection_label = QLabel("Deteksi Tangan:")
        detection_label.setObjectName("metricLabel")
        detection_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.detection_value = QLabel("0")
        self.detection_value.setObjectName("metricValue")
        self.detection_value.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        self.detection_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # Note Display
        note_label = QLabel("Current Note:")
        note_label.setObjectName("metricLabel")
        note_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.note_value = QLabel("--")
        self.note_value.setObjectName("metricValue")
        self.note_value.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        self.note_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # Volume Display
        volume_label = QLabel("Volume:")
        volume_label.setObjectName("metricLabel")
        volume_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.volume_value = QLabel("0%")
        self.volume_value.setObjectName("metricValue")
        self.volume_value.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        self.volume_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # Add widgets to grid
        layout.addWidget(fps_label, 0, 0)
        layout.addWidget(self.fps_value, 0, 1)
        layout.addWidget(detection_label, 1, 0)
        layout.addWidget(self.detection_value, 1, 1)
        layout.addWidget(note_label, 2, 0)
        layout.addWidget(self.note_value, 2, 1)
        layout.addWidget(volume_label, 3, 0)
        layout.addWidget(self.volume_value, 3, 1)
        
        group.setLayout(layout)
        return group
    
    # Event Handlers
    def decrease_bpm(self):
        """Decrease BPM by step amount"""
        current = self.bpm_slider.value()
        new_value = max(self.MIN_BPM, current - self.BPM_STEP)
        self.bpm_slider.setValue(new_value)
    
    def increase_bpm(self):
        """Increase BPM by step amount"""
        current = self.bpm_slider.value()
        new_value = min(self.MAX_BPM, current + self.BPM_STEP)
        self.bpm_slider.setValue(new_value)
    
    def reset_bpm(self):
        """Reset BPM to default value"""
        self.bpm_slider.setValue(self.DEFAULT_BPM)
    
    def on_bpm_slider_changed(self, value: int):
        """Handle BPM slider change with validation"""
        clamped_value = max(self.MIN_BPM, min(self.MAX_BPM, value))
        self.bpm_value.setText(str(clamped_value))
        self.bpm_changed.emit(clamped_value)
        self.statusBar().showMessage(f"🎵 BPM changed to {clamped_value}", 2000)
    
    def on_pattern_button_clicked(self, pattern_index: int):
        """Handle pattern button click"""
        # Uncheck all buttons
        for btn in self.pattern_buttons:
            btn.setChecked(False)
        
        # Check clicked button
        if pattern_index < len(self.pattern_buttons):
            self.pattern_buttons[pattern_index].setChecked(True)
        
        # Update display
        self.pattern_value.setText(f"Pattern {pattern_index + 1}")
        
        # Emit signal
        self.pattern_changed.emit(pattern_index)
        self.statusBar().showMessage(f"🎼 Switched to Pattern {pattern_index + 1}", 2000)
    
    # Public Update Methods
    def update_camera_feed(self, frame: np.ndarray):
        """Update camera display with processed frame"""
        if frame is None or frame.size == 0:
            return
        
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(
                rgb_frame.data, 
                w, h, 
                bytes_per_line, 
                QImage.Format.Format_RGB888
            )
            
            scaled = QPixmap.fromImage(qt_image).scaled(
                self.camera_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.camera_label.setPixmap(scaled)
            
            self.frame_count += 1
            
        except Exception as e:
            print(f"Error updating camera feed: {e}")
    
    def update_hand_status(self, hand_side: str, detected: bool):
        """Update hand detection status with animation"""
        if hand_side.lower() == HandSide.LEFT.value:
            label = self.left_hand_status
            text_base = "TANGAN KIRI"
        elif hand_side.lower() == HandSide.RIGHT.value:
            label = self.right_hand_status
            text_base = "TANGAN KANAN"
        else:
            return
        
        if detected:
            label.setText(f"🟢 {text_base}")
            label.setObjectName("statusActive")
        else:
            label.setText(f"◯ {text_base}")
            label.setObjectName("statusInactive")
        
        # Refresh style
        label.style().unpolish(label)
        label.style().polish(label)
        label.update()
    
    def update_arpeggiator_display(self, note: Optional[int], volume: Optional[float]):
        """Update arpeggiator visualization"""
        if note is not None:
            # Convert MIDI note to name
            notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            octave = (note // 12) - 1
            note_name = notes[note % 12]
            self.note_value.setText(f"{note_name}{octave}")
        else:
            self.note_value.setText("--")
        
        if volume is not None:
            volume_percent = int(volume * 100)
            self.volume_value.setText(f"{volume_percent}%")
        else:
            self.volume_value.setText("0%")
    
    def trigger_drum_indicator(self, drum_name: str, velocity: float = 1.0):
        """Trigger drum indicator animation with velocity"""
        if drum_name not in self.drum_indicators:
            return
        
        indicator = self.drum_indicators[drum_name]
        
        # Stop existing fade timer
        if drum_name in self.drum_fade_timers:
            self.drum_fade_timers[drum_name].stop()
        
        # Set value based on velocity
        value = int(velocity * 100)
        indicator.animateToValue(value)
        
        # Start fade timer
        self.drum_fade_timers[drum_name].start(150)
    
    def _fade_drum_indicator(self, drum_name: str):
        """Fade out drum indicator"""
        if drum_name in self.drum_indicators:
            self.drum_indicators[drum_name].animateToValue(0)
        if drum_name in self.drum_fade_timers:
            self.drum_fade_timers[drum_name].stop()
    
    def update_fps(self, fps: float):
        """Update FPS display"""
        self.fps_value.setText(f"{fps:.1f}")
    
    def update_detection_count(self, count: int):
        """Update hand detection count"""
        self.detection_value.setText(str(count))
    
    def update_pattern_display(self, pattern_index: int):
        """Update pattern display programmatically"""
        self.pattern_value.setText(f"Pattern {pattern_index + 1}")
        
        # Update button states
        for i, btn in enumerate(self.pattern_buttons):
            btn.setChecked(i == pattern_index)
    
    def _update_fps_display(self):
        """Internal method to update FPS from frame count"""
        # This can be called periodically if needed
        pass
    
    def get_bpm(self) -> int:
        """Get current BPM value"""
        return self.bpm_slider.value()
    
    def set_bpm(self, bpm: int):
        """Set BPM value programmatically"""
        clamped = max(self.MIN_BPM, min(self.MAX_BPM, bpm))
        self.bpm_slider.setValue(clamped)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop all timers
        for timer in self.drum_fade_timers.values():
            if timer.isActive():
                timer.stop()
        
        if self.fps_update_timer.isActive():
            self.fps_update_timer.stop()
        
        event.accept()


# Example usage
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = GestuneUI()
    window.show()
    
    # Simulate some updates
    def test_updates():
        import random
        
        # Test drum triggers
        drums = list(window.DRUM_DISPLAY_NAMES.keys())
        drum = random.choice(drums)
        window.trigger_drum_indicator(drum, random.uniform(0.5, 1.0))
        
        # Test hand status
        window.update_hand_status("left", random.choice([True, False]))
        window.update_hand_status("right", random.choice([True, False]))
        
        # Test FPS
        window.update_fps(random.uniform(25, 60))
    
    # Set up test timer
    test_timer = QTimer()
    test_timer.timeout.connect(test_updates)
    test_timer.start(500)
    
    sys.exit(app.exec())