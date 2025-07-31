from PyQt5.QtWidgets import QPushButton, QFrame, QLabel, QWidget, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QFont, QPalette

class ModernButton(QPushButton):
    """Modern styled button with hover animations"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 10, QFont.Medium))
        self._setup_animation()
        self._apply_style()
        
    def _setup_animation(self):
        """Setup hover animations"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def _apply_style(self):
        """Apply modern button styling"""
        self.setStyleSheet("""
            ModernButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0078D4, stop:1 #106EBE);
                border: none;
                border-radius: 6px;
                color: white;
                font-weight: 500;
                padding: 8px 16px;
            }
            ModernButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1084D8, stop:1 #1976C2);
            }
            ModernButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #005A9E, stop:1 #004578);
            }
            ModernButton:disabled {
                background: #3F3F3F;
                color: #888888;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

class StatusIndicator(QLabel):
    """Animated status indicator with color changes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.status = "disconnected"
        self._setup_animation()
        
    def _setup_animation(self):
        """Setup pulsing animation for connected state"""
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self._pulse)
        self.pulse_opacity = 1.0
        self.pulse_direction = -1
        
    def set_status(self, status):
        """Set the status and update appearance"""
        self.status = status
        if status == "connected":
            self.pulse_timer.start(50)
        else:
            self.pulse_timer.stop()
            self.pulse_opacity = 1.0
        self.update()
        
    def _pulse(self):
        """Create pulsing effect"""
        self.pulse_opacity += self.pulse_direction * 0.05
        if self.pulse_opacity <= 0.3:
            self.pulse_opacity = 0.3
            self.pulse_direction = 1
        elif self.pulse_opacity >= 1.0:
            self.pulse_opacity = 1.0
            self.pulse_direction = -1
        self.update()
        
    def paintEvent(self, event):
        """Custom paint event for the indicator"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.status == "connected":
            color = QColor(46, 204, 113, int(255 * self.pulse_opacity))
        elif self.status == "searching":
            color = QColor(241, 196, 15)
        else:
            color = QColor(231, 76, 60)
            
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 12, 12)

class AnimatedFrame(QFrame):
    """Frame with slide-in animation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self._setup_animation()
        self._apply_style()
        
    def _setup_animation(self):
        """Setup slide animation"""
        self.slide_animation = QPropertyAnimation(self, b"geometry")
        self.slide_animation.setDuration(300)
        self.slide_animation.setEasingCurve(QEasingCurve.OutQuart)
        
    def _apply_style(self):
        """Apply modern frame styling"""
        self.setStyleSheet("""
            AnimatedFrame {
                background-color: #3A3B3C;
                border: 1px solid #4A4B4C;
                border-radius: 8px;
                margin: 4px;
            }
        """)
        
        # Add subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setXOffset(0)
        shadow.setYOffset(1)
        shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(shadow)
        
    def slide_in_from_left(self):
        """Animate sliding in from left"""
        start_rect = self.geometry()
        start_rect.moveLeft(-start_rect.width())
        end_rect = self.geometry()
        
        self.slide_animation.setStartValue(start_rect)
        self.slide_animation.setEndValue(end_rect)
        self.slide_animation.start()

class ModernProgressBar(QWidget):
    """Custom progress bar with modern styling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(8)
        self.value = 0
        self.maximum = 255
        self._setup_animation()
        
    def _setup_animation(self):
        """Setup value change animation"""
        self.value_animation = QPropertyAnimation(self, b"value")
        self.value_animation.setDuration(200)
        self.value_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def setValue(self, value):
        """Set value with animation"""
        self.value_animation.setStartValue(self.value)
        self.value_animation.setEndValue(value)
        self.value_animation.start()
        
    def paintEvent(self, event):
        """Custom paint event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.setBrush(QColor(45, 45, 45))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 4, 4)
        
        # Progress
        if self.value > 0:
            progress_width = int((self.value / self.maximum) * self.width())
            progress_rect = QRect(0, 0, progress_width, self.height())
            
            gradient = QLinearGradient(0, 0, progress_width, 0)
            gradient.setColorAt(0, QColor(0, 120, 212))
            gradient.setColorAt(1, QColor(16, 110, 190))
            
            painter.setBrush(gradient)
            painter.drawRoundedRect(progress_rect, 4, 4)

class ModernLabel(QLabel):
    """Modern styled label with optional formatting"""
    
    def __init__(self, text="", font_size=10, bold=False, parent=None):
        super().__init__(text, parent)
        self._setup_font(font_size, bold)
        self._apply_style()
        
    def _setup_font(self, font_size, bold):
        """Setup font styling"""
        font = QFont("Segoe UI", font_size)
        if bold:
            font.setBold(True)
        self.setFont(font)
        
    def _apply_style(self):
        """Apply modern label styling"""
        self.setStyleSheet("""
            ModernLabel {
                color: #ffffff;
                background: transparent;
                padding: 2px;
            }
        """)

class GlowLabel(QLabel):
    """Label with glow effect"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._apply_glow_effect()
        
    def _apply_glow_effect(self):
        """Apply glow effect to the label"""
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(15)
        glow.setXOffset(0)
        glow.setYOffset(0)
        glow.setColor(QColor(0, 120, 212, 100))
        self.setGraphicsEffect(glow)
