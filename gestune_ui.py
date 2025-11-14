"""
Gestune Modern UI - PyQt6
Professional and modern UI for Gestune application
Features: Clean design, responsive layout, real-time visualization
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QGroupBox, QGridLayout, QFrame, 
    QProgressBar, QSpacerItem, QSizePolicy, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QImage, QPixmap, QFont, QIcon
import cv2
import numpy as np


class GestuneUI(QMainWindow):
    """
    Main UI Window for Gestune Application
    
    Features:
    - Live camera feed with hand tracking visualization
    - Real-time metrics and controls
    - Interactive BPM and pattern controls
    - Professional dark theme design
    """
    
    # Signals
    bpm_changed = pyqtSignal(int)
    pattern_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎵 Gestune - Musik dari Gerakan Tangan")
        self.setMinimumSize(1400, 850)
        self.resize(1600, 900)
        
        # Initialize UI
        self.setup_ui()
        
        # Status bar
        self.statusBar().showMessage("Ready - Gestune v2.0")
        
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
        """Apply modern dark theme stylesheet"""
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
            }
            
            /* Panel Titles */
            QLabel#panelTitle {
                color: #58a6ff;
                padding: 10px;
                background-color: #0d1117;
                border-radius: 8px;
                border-left: 4px solid #1f6feb;
            }
            
            /* Group Boxes */
            QGroupBox#controlGroup {
                background-color: #0d1117;
                border: 2px solid #30363d;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
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
            }
            
            /* Status Indicators */
            QLabel#statusInactive {
                color: #6e7681;
                padding: 5px 12px;
                background-color: #0d1117;
                border: 2px solid #30363d;
                border-radius: 6px;
            }
            
            QLabel#statusActive {
                color: #238636;
                padding: 5px 12px;
                background-color: #0d1117;
                border: 2px solid #238636;
                border-radius: 6px;
            }
            
            /* BPM Display */
            QLabel#bpmDisplay {
                color: #58a6ff;
                background-color: #0d1117;
                border: 3px solid #1f6feb;
                border-radius: 8px;
                padding: 10px 20px;
            }
            
            /* Slider */
            QSlider#bpmSlider {
                height: 30px;
            }
            
            QSlider#bpmSlider::groove:horizontal {
                background: #30363d;
                height: 6px;
                border-radius: 3px;
            }
            
            QSlider#bpmSlider::handle:horizontal {
                background: #58a6ff;
                border: 2px solid #1f6feb;
                width: 18px;
                height: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }
            
            QSlider#bpmSlider::handle:horizontal:hover {
                background: #79c0ff;
                border: 2px solid #58a6ff;
            }
            
            QSlider#bpmSlider::sub-page:horizontal {
                background: #1f6feb;
                border-radius: 3px;
            }
            
            /* Buttons */
            QPushButton#controlButton {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            
            QPushButton#controlButton:hover {
                background-color: #30363d;
                border-color: #58a6ff;
            }
            
            QPushButton#controlButton:pressed {
                background-color: #1f6feb;
                color: #ffffff;
            }
            
            /* Guide Frames */
            QFrame#guideFrame {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 10px;
            }
            
            QLabel#guideTitle {
                color: #58a6ff;
            }
            
            QLabel#guideText {
                color: #8b949e;
                line-height: 1.6;
            }
            
            /* Metric Values */
            QLabel#metricValue {
                color: #3fb950;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            
            /* Progress Bars (Drum Indicators) */
            QProgressBar#drumIndicator {
                border: 2px solid #30363d;
                border-radius: 6px;
                background-color: #0d1117;
                text-align: center;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #161b22;
                color: #8b949e;
                border-top: 1px solid #30363d;
                padding: 5px;
            }
        """)
    
    def create_camera_panel(self):
        """Create camera feed panel"""
        panel = QFrame()
        panel.setObjectName("cameraPanel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(12)
        
        # Header with title
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
        self.camera_label.setText("⏳ Menunggu kamera...")
        
        layout.addLayout(header_layout)
        layout.addWidget(self.camera_label, 1)
        
        return panel
    
    def create_status_indicator(self, text):
        """Create a status indicator label"""
        label = QLabel(f"◯ {text}")
        label.setObjectName("statusInactive")
        label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        return label
    
    def create_control_panel(self):
        """Create control and visualization panel"""
        panel = QFrame()
        panel.setObjectName("controlPanel")
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🎛️ KONTROL & VISUALISASI")
        title.setObjectName("panelTitle")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Components
        bpm_control = self.create_bpm_control_group()
        visualization = self.create_visualization_group()
        hand_guide = self.create_hand_guide_group()
        metrics = self.create_metrics_group()
        
        layout.addWidget(title)
        layout.addWidget(bpm_control)
        layout.addWidget(visualization)
        layout.addWidget(hand_guide)
        layout.addWidget(metrics)
        layout.addStretch()
        
        return panel
    
    def create_bpm_control_group(self):
        """Create BPM control group"""
        group = QGroupBox("⏱️ TEMPO CONTROL")
        group.setObjectName("controlGroup")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # BPM display
        bpm_display = QHBoxLayout()
        bpm_label = QLabel("BPM:")
        bpm_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        
        self.bpm_value = QLabel("120")
        self.bpm_value.setObjectName("bpmDisplay")
        self.bpm_value.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.bpm_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        bpm_display.addWidget(bpm_label)
        bpm_display.addStretch()
        bpm_display.addWidget(self.bpm_value)
        bpm_display.addStretch()
        
        # BPM slider with labels
        slider_container = QHBoxLayout()
        min_label = QLabel("60")
        min_label.setFont(QFont("Segoe UI", 10))
        max_label = QLabel("180")
        max_label.setFont(QFont("Segoe UI", 10))
        
        self.bpm_slider = QSlider(Qt.Orientation.Horizontal)
        self.bpm_slider.setObjectName("bpmSlider")
        self.bpm_slider.setMinimum(60)
        self.bpm_slider.setMaximum(180)
        self.bpm_slider.setValue(120)
        self.bpm_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.bpm_slider.setTickInterval(20)
        self.bpm_slider.valueChanged.connect(self.on_bpm_slider_changed)
        
        slider_container.addWidget(min_label)
        slider_container.addWidget(self.bpm_slider, 1)
        slider_container.addWidget(max_label)
        
        # BPM adjustment buttons
        btn_container = QHBoxLayout()
        btn_slower = QPushButton("🐢 LAMBAT (-10)")
        btn_faster = QPushButton("🐇 CEPAT (+10)")
        
        btn_slower.setObjectName("controlButton")
        btn_faster.setObjectName("controlButton")
        
        btn_slower.clicked.connect(self.decrease_bpm)
        btn_faster.clicked.connect(self.increase_bpm)
        
        btn_container.addWidget(btn_slower)
        btn_container.addWidget(btn_faster)
        
        layout.addLayout(bpm_display)
        layout.addLayout(slider_container)
        layout.addLayout(btn_container)
        
        group.setLayout(layout)
        return group
    
    def create_hand_guide_group(self):
        """Create hand control guide"""
        group = QGroupBox("👋 PANDUAN KONTROL")
        group.setObjectName("controlGroup")
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Left hand guide
        left_hand_frame = QFrame()
        left_hand_frame.setObjectName("guideFrame")
        left_layout = QVBoxLayout(left_hand_frame)
        
        left_title = QLabel("👈 TANGAN KIRI - ARPEGGIATOR")
        left_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        left_title.setObjectName("guideTitle")
        
        left_info = QLabel(
            "• Geser ke atas/bawah: Ubah nada\n"
            "• Geser ke kiri/kanan: Ubah oktaf\n"
            "• Posisi tangan mengontrol pitch"
        )
        left_info.setObjectName("guideText")
        left_info.setFont(QFont("Segoe UI", 10))
        
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
            "• Jempol (👍): KICK\n"
            "• Telunjuk (☝️): SNARE\n"
            "• Jari tengah: HI-HAT\n"
            "• Jari manis: TOM\n"
            "• Kelingking: CRASH"
        )
        right_info.setObjectName("guideText")
        right_info.setFont(QFont("Segoe UI", 10))
        
        right_layout.addWidget(right_title)
        right_layout.addWidget(right_info)
        
        layout.addWidget(left_hand_frame)
        layout.addWidget(right_hand_frame)
        
        group.setLayout(layout)
        return group
    
    def create_visualization_group(self):
        """Create visualization group for drum hits"""
        group = QGroupBox("🥁 VISUALISASI DRUM")
        group.setObjectName("controlGroup")
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Create drum indicators
        self.drum_indicators = {}
        drum_info = [
            ("kick", "🥁 KICK", "#FF5252"),
            ("snare", "🎺 SNARE", "#FFD740"),
            ("hihat", "🎩 HI-HAT", "#69F0AE"),
            ("tom", "🥁 TOM", "#FF80AB"),
            ("crash", "💥 CRASH", "#40C4FF")
        ]
        
        for drum_id, drum_label, color in drum_info:
            drum_layout = QHBoxLayout()
            
            # Label
            label = QLabel(drum_label)
            label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            label.setFixedWidth(120)
            
            # Indicator bar
            indicator = QProgressBar()
            indicator.setObjectName("drumIndicator")
            indicator.setMaximum(100)
            indicator.setValue(0)
            indicator.setTextVisible(False)
            indicator.setFixedHeight(30)
            indicator.setStyleSheet(f"""
                QProgressBar {{
                    border: 2px solid #444;
                    border-radius: 5px;
                    background-color: #222;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 3px;
                }}
            """)
            
            self.drum_indicators[drum_id] = indicator
            
            drum_layout.addWidget(label)
            drum_layout.addWidget(indicator, 1)
            
            layout.addLayout(drum_layout)
        
        group.setLayout(layout)
        return group
    
    def create_metrics_group(self):
        """Create performance metrics display"""
        group = QGroupBox("� METRIK PERFORMA")
        group.setObjectName("controlGroup")
        layout = QGridLayout()
        layout.setSpacing(10)
        
        # FPS Counter
        fps_label = QLabel("FPS:")
        fps_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.fps_value = QLabel("0")
        self.fps_value.setObjectName("metricValue")
        self.fps_value.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.fps_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Detection Counter
        detection_label = QLabel("Deteksi Tangan:")
        detection_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.detection_value = QLabel("0")
        self.detection_value.setObjectName("metricValue")
        self.detection_value.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.detection_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Current Pattern
        pattern_label = QLabel("Pola Drum:")
        pattern_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.pattern_value = QLabel("basic")
        self.pattern_value.setObjectName("metricValue")
        self.pattern_value.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.pattern_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Add widgets to grid
        layout.addWidget(fps_label, 0, 0)
        layout.addWidget(self.fps_value, 0, 1)
        layout.addWidget(detection_label, 1, 0)
        layout.addWidget(self.detection_value, 1, 1)
        layout.addWidget(pattern_label, 2, 0)
        layout.addWidget(self.pattern_value, 2, 1)
        
        group.setLayout(layout)
        return group
    
    def apply_styles(self):
        """Terapkan stylesheet"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
            }
            QWidget {
                background-color: #0d1117;
                color: #c9d1d9;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QFrame {
                background-color: #161b22;
                border-radius: 10px;
                padding: 10px;
            }
            QGroupBox {
                background-color: #161b22;
                border: 2px solid #30363d;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                font-weight: bold;
                font-size: 13px;
                color: #58a6ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
            }
            QPushButton {
                background-color: #21262d;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #30363d;
                border-color: #58a6ff;
            }
            QPushButton:pressed {
                background-color: #1c2128;
            }
            QSlider::groove:horizontal {
                border: 1px solid #30363d;
                height: 8px;
                background: #21262d;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #58a6ff;
                border: 2px solid #1f6feb;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #79c0ff;
            }
            QSlider::sub-page:horizontal {
                background: #1f6feb;
                border: 1px solid #1f6feb;
                height: 8px;
                border-radius: 4px;
            }
            QProgressBar {
                border: 2px solid #30363d;
                border-radius: 5px;
                text-align: center;
                background-color: #21262d;
                color: #c9d1d9;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #2ea043;
                border-radius: 3px;
            }
            QLabel {
                color: #c9d1d9;
            }
        """)
    
    # Event handlers
    def on_bpm_changed(self, value):
        """Handler untuk perubahan BPM"""
        self.bpm_label.setText(str(value))
        self.bpm_changed.emit(value)
    
    def adjust_bpm(self, delta):
        """Adjust BPM dengan delta"""
        current = self.bpm_slider.value()
        new_value = max(60, min(200, current + delta))
        self.bpm_slider.setValue(new_value)
    
    def on_pattern_clicked(self):
        """Handler untuk ganti pattern"""
        self.pattern_changed.emit()
    
    # Public methods untuk update UI
    def update_camera(self, frame):
        """Update display kamera"""
        if frame is not None:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            scaled = QPixmap.fromImage(qt_image).scaled(
                self.camera_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.camera_label.setPixmap(scaled)
    
    def update_hand_status(self, hand_label, detected):
        """Update hand detection status"""
        if hand_label == "left":
            if detected:
                self.left_hand_status.setText("🟢 TANGAN KIRI")
                self.left_hand_status.setObjectName("statusActive")
            else:
                self.left_hand_status.setText("◯ TANGAN KIRI")
                self.left_hand_status.setObjectName("statusInactive")
        elif hand_label == "right":
            if detected:
                self.right_hand_status.setText("🟢 TANGAN KANAN")
                self.right_hand_status.setObjectName("statusActive")
            else:
                self.right_hand_status.setText("◯ TANGAN KANAN")
                self.right_hand_status.setObjectName("statusInactive")
        
        # Refresh style
        self.left_hand_status.style().unpolish(self.left_hand_status)
        self.left_hand_status.style().polish(self.left_hand_status)
        self.right_hand_status.style().unpolish(self.right_hand_status)
        self.right_hand_status.style().polish(self.right_hand_status)
    
    def update_arpeggiator(self, note, volume):
        """Update visualisasi arpeggiator"""
        if note:
            # Convert MIDI note to name
            notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            octave = (note // 12) - 1
            note_name = notes[note % 12]
            self.note_label.setText(f"Note: {note_name}{octave}")
        else:
            self.note_label.setText("Note: --")
        
        if volume is not None:
            self.volume_bar.setValue(int(volume * 100))
    
    def update_drums(self, active_drums):
        """Update indikator drum"""
        drums_map = {
            'kick': 'kick',
            'snare': 'snare',
            'hihat': 'hi-hat',
            'hightom': 'tom',
            'crashcymbal': 'cymbal'
        }
        
        for drum_key, display_name in drums_map.items():
            if display_name in self.drum_indicators:
                if drum_key in active_drums:
                    self.drum_indicators[display_name].setText(f"🔴 {display_name.capitalize()}")
                    self.drum_indicators[display_name].setStyleSheet("color: #f85149; font-weight: bold;")
                else:
                    self.drum_indicators[display_name].setText(f"⚫ {display_name.capitalize()}")
                    self.drum_indicators[display_name].setStyleSheet("color: #555;")
    
    def update_metrics(self, fps, bpm, pattern):
        """Update metrics"""
        self.fps_label.setText(f"FPS: {fps:.1f}")
        self.current_bpm_label.setText(f"BPM: {bpm}")
        self.pattern_label.setText(f"Pattern: {pattern + 1}")
    
    def get_bpm(self):
        """Dapatkan nilai BPM saat ini"""
        return self.bpm_slider.value()
    
    def decrease_bpm(self):
        """Decrease BPM by 10"""
        current = self.bpm_slider.value()
        new_value = max(60, current - 10)
        self.bpm_slider.setValue(new_value)
        self.bpm_value.setText(str(new_value))
        self.bpm_changed.emit(new_value)
    
    def increase_bpm(self):
        """Increase BPM by 10"""
        current = self.bpm_slider.value()
        new_value = min(180, current + 10)
        self.bpm_slider.setValue(new_value)
        self.bpm_value.setText(str(new_value))
        self.bpm_changed.emit(new_value)
    
    def on_bpm_slider_changed(self, value):
        """Handle BPM slider change"""
        self.bpm_value.setText(str(value))
        self.bpm_changed.emit(value)
    
    def update_camera_feed(self, frame):
        """Update camera display with processed frame"""
        self.update_camera(frame)
    
    def update_fps(self, fps):
        """Update FPS display"""
        self.fps_value.setText(f"{fps:.1f}")
    
    def trigger_drum_indicator(self, drum_name):
        """Trigger drum indicator animation"""
        if drum_name in self.drum_indicators:
            indicator = self.drum_indicators[drum_name]
            indicator.setValue(100)
            # Create timer to fade out
            QTimer.singleShot(100, lambda: indicator.setValue(0))
