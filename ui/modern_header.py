from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor, QPen
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ModernHeaderWidget(QWidget):
    """Modern header widget with animated elements and professional design"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self.pulse_opacity = 1.0
        self.pulse_direction = -1
        self._setup_ui()
        self._setup_animations()
        
    def _setup_ui(self):
        """Setup the header UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)
        
        # Left section: Icon and branding
        left_section = QHBoxLayout()
        left_section.setSpacing(15)
        
        # App icon with glow effect
        self.icon_label = QLabel()
        icon_pixmap = QPixmap(resource_path("assets/icon.png"))
        if not icon_pixmap.isNull():
            # Scale icon to appropriate size
            scaled_icon = icon_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(scaled_icon)
        self.icon_label.setFixedSize(64, 64)
        left_section.addWidget(self.icon_label)
        
        # Title and subtitle
        title_section = QVBoxLayout()
        title_section.setSpacing(2)
        
        self.title_label = QLabel("LazyDS4")
        self.title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.title_label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-weight: bold;
                text-shadow: 0px 0px 15px rgba(0, 212, 255, 0.4);
            }
        """)
        title_section.addWidget(self.title_label)
        
        self.subtitle_label = QLabel("DualShock 4 to XInput Controller")
        self.subtitle_label.setFont(QFont("Segoe UI", 12))
        self.subtitle_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-weight: 300;
            }
        """)
        title_section.addWidget(self.subtitle_label)
        
        left_section.addLayout(title_section)
        left_section.addStretch()
        
        # Right section: Status indicator and activity icon
        right_section = QHBoxLayout()
        right_section.setSpacing(15)
        
        # Activity indicator
        self.activity_label = QLabel()
        activity_pixmap = QPixmap(resource_path("assets/activity.svg"))
        if not activity_pixmap.isNull():
            scaled_activity = activity_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.activity_label.setPixmap(scaled_activity)
        self.activity_label.setFixedSize(32, 32)
        right_section.addWidget(self.activity_label)
        
        # Status section
        status_section = QVBoxLayout()
        status_section.setSpacing(5)
        
        self.status_title = QLabel("Service Status")
        self.status_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.status_title.setStyleSheet("color: #ffffff;")
        status_section.addWidget(self.status_title)
        
        self.status_label = QLabel("Service Stopped")
        self.status_label.setFont(QFont("Segoe UI", 11, QFont.Medium))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(244, 67, 54, 0.15), stop:1 rgba(244, 67, 54, 0.05));
                border: 1px solid rgba(244, 67, 54, 0.3);
                border-radius: 6px;
                padding: 4px 12px;
            }
        """)
        status_section.addWidget(self.status_label)
        
        right_section.addLayout(status_section)
        
        main_layout.addLayout(left_section)
        main_layout.addLayout(right_section)
        
        # Apply header styling
        self.setStyleSheet("""
            ModernHeaderWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 45, 48, 0.9), stop:1 rgba(35, 35, 38, 0.9));
                border: 1px solid rgba(100, 100, 100, 0.2);
                border-radius: 15px;
                margin: 10px;
            }
        """)
        
    def _setup_animations(self):
        """Setup pulsing animation for activity indicator"""
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self._pulse_activity)
        self.pulse_timer.start(50)  # 50ms for smooth animation
        
    def _pulse_activity(self):
        """Create pulsing effect for activity indicator"""
        self.pulse_opacity += self.pulse_direction * 0.02
        if self.pulse_opacity <= 0.3:
            self.pulse_opacity = 0.3
            self.pulse_direction = 1
        elif self.pulse_opacity >= 1.0:
            self.pulse_opacity = 1.0
            self.pulse_direction = -1
            
        # Apply opacity to activity indicator
        self.activity_label.setStyleSheet(f"""
            QLabel {{
                background: rgba(0, 212, 255, {self.pulse_opacity * 0.2});
                border-radius: 16px;
                padding: 8px;
            }}
        """)
        
    def update_status(self, status_text, is_running=False):
        """Update the status display"""
        self.status_label.setText(status_text)
        
        if is_running:
            # Green theme for running status
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(76, 175, 80, 0.15), stop:1 rgba(76, 175, 80, 0.05));
                    border: 1px solid rgba(76, 175, 80, 0.3);
                    border-radius: 6px;
                    padding: 4px 12px;
                }
            """)
        else:
            # Red theme for stopped status
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 rgba(244, 67, 54, 0.15), stop:1 rgba(244, 67, 54, 0.05));
                    border: 1px solid rgba(244, 67, 54, 0.3);
                    border-radius: 6px;
                    padding: 4px 12px;
                }
            """)
