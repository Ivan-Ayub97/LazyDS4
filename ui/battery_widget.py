from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QLinearGradient
import logging

class BatteryWidget(QWidget):
    """Interactive battery widget with visual indicator and alerts"""
    
    battery_low_warning = pyqtSignal(int)  # Emits battery percentage when low
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.battery_level = 0  # 0-100
        self.is_charging = False
        self.is_connected = False
        self.warning_shown = False
        
        # Battery thresholds
        self.low_battery_threshold = 20
        self.critical_battery_threshold = 10
        
        # Animation for charging indicator
        self.charging_animation_step = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_charging)
        self.animation_timer.start(500)  # 500ms animation cycle
        
        self.setFixedSize(120, 80)  # Increased height to accommodate text
        self.setStyleSheet("background-color: transparent;")
        
    def update_battery_status(self, level, is_charging=False, is_connected=True):
        """Update battery status and trigger repaint"""
        old_level = self.battery_level
        self.battery_level = max(0, min(100, level))
        self.is_charging = is_charging
        self.is_connected = is_connected
        
        # Check for low battery warning
        if (is_connected and not is_charging and 
            self.battery_level <= self.low_battery_threshold and 
            old_level > self.low_battery_threshold):
            self.battery_low_warning.emit(self.battery_level)
            self.warning_shown = True
            logging.warning(f"Low battery warning: {self.battery_level}%")
        
        # Reset warning flag when battery is good again
        if self.battery_level > self.low_battery_threshold:
            self.warning_shown = False
            
        self.update()  # Trigger repaint
        
    def _animate_charging(self):
        """Animate charging indicator"""
        if self.is_charging:
            self.charging_animation_step = (self.charging_animation_step + 1) % 4
            self.update()
            
    def _get_battery_color(self):
        """Get battery color based on level and charging status"""
        if not self.is_connected:
            return QColor(100, 100, 100)  # Gray when disconnected
            
        if self.is_charging:
            return QColor(50, 200, 50)  # Green when charging
            
        if self.battery_level <= self.critical_battery_threshold:
            return QColor(220, 50, 50)  # Red for critical
        elif self.battery_level <= self.low_battery_threshold:
            return QColor(255, 165, 0)  # Orange for low
        else:
            return QColor(50, 200, 50)  # Green for good
            
    def paintEvent(self, event):
        """Custom paint event for battery visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Get widget dimensions
        rect = self.rect()
        center_x = rect.width() // 2
        center_y = rect.height() // 2
        
        # Battery outline dimensions
        battery_width = 80
        battery_height = 35
        battery_x = center_x - battery_width // 2
        battery_y = center_y - battery_height // 2
        
        # Battery tip (positive terminal)
        tip_width = 4
        tip_height = 15
        tip_x = battery_x + battery_width
        tip_y = center_y - tip_height // 2
        
        # Draw battery outline
        outline_color = QColor(80, 80, 80) if self.is_connected else QColor(120, 120, 120)
        painter.setPen(QPen(outline_color, 2))
        painter.setBrush(QBrush(QColor(240, 240, 240)))
        painter.drawRoundedRect(battery_x, battery_y, battery_width, battery_height, 3, 3)
        
        # Draw battery tip
        painter.drawRoundedRect(tip_x, tip_y, tip_width, tip_height, 2, 2)
        
        # Draw battery fill based on level
        if self.is_connected and self.battery_level > 0:
            fill_width = int((battery_width - 6) * (self.battery_level / 100.0))
            fill_x = battery_x + 3
            fill_y = battery_y + 3
            fill_height = battery_height - 6
            
            # Create gradient for battery fill
            battery_color = self._get_battery_color()
            gradient = QLinearGradient(fill_x, fill_y, fill_x, fill_y + fill_height)
            
            if self.is_charging:
                # Pulsing effect for charging
                alpha = 180 + int(75 * abs(2 - self.charging_animation_step) / 2)
                bright_color = QColor(battery_color)
                bright_color.setAlpha(alpha)
                gradient.setColorAt(0, bright_color)
                gradient.setColorAt(1, battery_color)
            else:
                gradient.setColorAt(0, battery_color.lighter(120))
                gradient.setColorAt(1, battery_color)
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(fill_x, fill_y, fill_width, fill_height, 2, 2)
        
        # Draw charging indicator
        if self.is_charging and self.is_connected:
            # Lightning bolt symbol
            painter.setPen(QPen(QColor(255, 255, 255), 2))
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            
            # Create lightning bolt points
            bolt_points = [
                (center_x - 3, center_y - 8),
                (center_x + 2, center_y - 8),
                (center_x - 2, center_y - 2),
                (center_x + 3, center_y - 2),
                (center_x + 3, center_y + 8),
                (center_x - 2, center_y + 8),
                (center_x + 2, center_y + 2),
                (center_x - 3, center_y + 2)
            ]
            
            from PyQt5.QtGui import QPolygon
            from PyQt5.QtCore import QPoint
            
            bolt_polygon = QPolygon([QPoint(x, y) for x, y in bolt_points])
            painter.drawPolygon(bolt_polygon)
        
        # Draw battery percentage text
        if self.is_connected:
            painter.setPen(QPen(QColor(50, 50, 50), 1))
            font = QFont("Arial", 9, QFont.Bold)
            painter.setFont(font)
            
            text = f"{self.battery_level}%"
            if self.is_charging:
                text += " ⚡"
                
            text_rect = painter.fontMetrics().boundingRect(text)
            text_x = center_x - text_rect.width() // 2
            text_y = battery_y + battery_height + 15
            
            painter.drawText(text_x, text_y, text)
        else:
            # Show "Not Connected" when controller is disconnected
            painter.setPen(QPen(QColor(120, 120, 120), 1))
            font = QFont("Arial", 8)
            painter.setFont(font)
            
            text = "No Controller"
            text_rect = painter.fontMetrics().boundingRect(text)
            text_x = center_x - text_rect.width() // 2
            text_y = battery_y + battery_height + 15
            
            painter.drawText(text_x, text_y, text)
