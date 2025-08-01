from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QTextEdit, QGroupBox,
                             QFrame, QGridLayout, QSlider, QSpinBox, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QRect, QPoint
from PyQt5.QtGui import QFont, QPalette, QPainter, QColor, QPen, QBrush, QPolygon
import math

# Fallback classes if modern_widgets is not available
try:
    from .modern_widgets import ModernButton, ModernLabel
except ImportError:
    # Fallback to standard widgets
    class ModernButton(QPushButton):
        def __init__(self, text="", parent=None):
            super().__init__(text, parent)
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:disabled {
                    background-color: #666;
                }
            """)
    
    class ModernLabel(QLabel):
        def __init__(self, text="", font_size=12, bold=False, parent=None):
            super().__init__(text, parent)
            font = self.font()
            font.setPointSize(font_size)
            font.setBold(bold)
            self.setFont(font)


class ControllerVisualizationWidget(QWidget):
    """Widget to display real-time controller visualization during calibration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: #1e1e1e; border: 2px solid #444;")
        
        # Current joystick positions (normalized -1.0 to 1.0)
        # Initialize joysticks in centered position
        self.left_stick_x = 0.0
        self.left_stick_y = 0.0
        self.right_stick_x = 0.0
        self.right_stick_y = 0.0
        
        # Raw values for display
        self.raw_values = {'lx': 128, 'ly': 128, 'rx': 128, 'ry': 128}
        
    def update_joystick_data(self, raw_values):
        """Update joystick data and refresh display"""
        self.raw_values = raw_values
        
        # Convert raw values (0-255) to normalized positions (-1.0 to 1.0)
        self.left_stick_x = (raw_values.get('lx', 128) - 128) / 127.0
        self.left_stick_y = -(raw_values.get('ly', 128) - 128) / 127.0  # Invert Y
        self.right_stick_x = (raw_values.get('rx', 128) - 128) / 127.0
        self.right_stick_y = -(raw_values.get('ry', 128) - 128) / 127.0  # Invert Y
        
        # Clamp values
        self.left_stick_x = max(-1.0, min(1.0, self.left_stick_x))
        self.left_stick_y = max(-1.0, min(1.0, self.left_stick_y))
        self.right_stick_x = max(-1.0, min(1.0, self.right_stick_x))
        self.right_stick_y = max(-1.0, min(1.0, self.right_stick_y))
        
        self.update()  # Trigger repaint
        
    def paintEvent(self, event):
        """Paint the controller visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Clear background
        painter.fillRect(self.rect(), QColor(30, 30, 30))
        
        # Draw controller outline
        self._draw_controller_outline(painter)
        
        # Draw joysticks
        self._draw_joystick(painter, self.left_stick_x, self.left_stick_y, "left")
        self._draw_joystick(painter, self.right_stick_x, self.right_stick_y, "right")
        
        # Draw raw values
        self._draw_values(painter)
        
    def _draw_controller_outline(self, painter):
        """Draw a simplified controller outline"""
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        
        # Main controller body
        width = self.width()
        height = self.height()
        
        # Controller body (rounded rectangle)
        body_rect = QRect(int(width * 0.1), int(height * 0.3), int(width * 0.8), int(height * 0.4))
        painter.drawRoundedRect(body_rect, 20, 20)
        
        # Left grip
        left_grip = QRect(int(width * 0.05), int(height * 0.5), int(width * 0.15), int(height * 0.35))
        painter.drawRoundedRect(left_grip, 15, 15)
        
        # Right grip
        right_grip = QRect(int(width * 0.8), int(height * 0.5), int(width * 0.15), int(height * 0.35))
        painter.drawRoundedRect(right_grip, 15, 15)
        
    def _draw_joystick(self, painter, norm_x, norm_y, side):
        """Draw a joystick at the specified normalized position"""
        width = self.width()
        height = self.height()
        
        # Joystick area dimensions
        stick_area_radius = min(width, height) * 0.08
        stick_radius = stick_area_radius * 0.3
        
        # Calculate joystick center position
        if side == "left":
            center_x = width * 0.25
            center_y = height * 0.65
        else:  # right
            center_x = width * 0.75
            center_y = height * 0.65
            
        # Draw joystick area (outer circle)
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        painter.setBrush(QBrush(QColor(40, 40, 40)))
        painter.drawEllipse(QPoint(int(center_x), int(center_y)), int(stick_area_radius), int(stick_area_radius))
        
        # Calculate stick position
        stick_x = center_x + (norm_x * stick_area_radius * 0.8)
        stick_y = center_y + (norm_y * stick_area_radius * 0.8)
        
        # Draw joystick (inner circle)
        stick_color = QColor(0, 150, 255) if abs(norm_x) > 0.1 or abs(norm_y) > 0.1 else QColor(120, 120, 120)
        painter.setPen(QPen(stick_color, 2))
        painter.setBrush(QBrush(stick_color))
        painter.drawEllipse(QPoint(int(stick_x), int(stick_y)), int(stick_radius), int(stick_radius))
        
        # Draw crosshair at center
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawLine(int(center_x - stick_area_radius), int(center_y), int(center_x + stick_area_radius), int(center_y))
        painter.drawLine(int(center_x), int(center_y - stick_area_radius), int(center_x), int(center_y + stick_area_radius))
        
        # Draw side label
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        label_y = center_y - stick_area_radius - 15
        painter.drawText(int(center_x - 15), int(label_y), side.upper())
        
    def _draw_values(self, painter):
        """Draw raw values on screen"""
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.setFont(QFont("Consolas", 9))
        
        # Draw values in top area
        y_offset = 20
        painter.drawText(10, y_offset, f"Left Stick:  X={self.raw_values.get('lx', 128):3d} Y={self.raw_values.get('ly', 128):3d}")
        painter.drawText(10, y_offset + 15, f"Right Stick: X={self.raw_values.get('rx', 128):3d} Y={self.raw_values.get('ry', 128):3d}")
        
        # Draw normalized values
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        painter.drawText(10, y_offset + 35, f"Normalized L: X={self.left_stick_x:+.2f} Y={self.left_stick_y:+.2f}")
        painter.drawText(10, y_offset + 50, f"Normalized R: X={self.right_stick_x:+.2f} Y={self.right_stick_y:+.2f}")


class CalibrationDialog(QDialog):
    """Dialog for controller stick calibration process"""
    
    calibration_requested = pyqtSignal()
    calibration_completed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Controller Calibration")
        self.setModal(True)
        self.resize(1000, 700)  # Adjusted size for better layout
        self.setStyleSheet(self._get_dark_style())
        
        self.calibration_timer = None
        self.calibration_time = 15  # Increased to 15 seconds for better calibration
        self.time_remaining = self.calibration_time
        
        # Create controller visualization widget with enhanced size
        self.controller_viz = ControllerVisualizationWidget()
        self.controller_viz.setMinimumSize(500, 350)
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the calibration dialog UI with better layout management"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Title
        title = ModernLabel("Controller Calibration", font_size=18, bold=True)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Create horizontal layout for better space distribution
        content_layout = QHBoxLayout()
        
        # Left column - Instructions and Status
        left_column = QVBoxLayout()
        left_column.setSpacing(10)
        
        # Instructions group (compact)
        instructions_group = QGroupBox("Instructions")
        instructions_group.setMaximumHeight(120)
        instructions_layout = QVBoxLayout(instructions_group)
        instructions_layout.setContentsMargins(8, 8, 8, 8)
        
        instructions_text = QTextEdit()
        instructions_text.setMaximumHeight(90)
        instructions_text.setReadOnly(True)
        instructions_text.setPlainText(
            "• Leave sticks centered for 2 seconds\n"
            "• Move each stick in complete circles\n"
            "• Push sticks to all extreme positions\n"
            "• Return to center when timer completes"
        )
        instructions_layout.addWidget(instructions_text)
        left_column.addWidget(instructions_group)
        
        # Status group (compact)
        status_group = QGroupBox("Status")
        status_group.setMaximumHeight(80)
        status_layout = QVBoxLayout(status_group)
        status_layout.setContentsMargins(8, 8, 8, 8)
        
        self.status_label = ModernLabel("Ready to calibrate", font_size=11)
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.calibration_time)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(20)
        status_layout.addWidget(self.progress_bar)
        
        left_column.addWidget(status_group)
        
        # Calibration data display (compact)
        data_group = QGroupBox("Calibration Data")
        data_group.setMaximumHeight(150)
        data_layout = QGridLayout(data_group)
        data_layout.setContentsMargins(8, 15, 8, 8)
        data_layout.setSpacing(8)
        
        # Headers
        data_layout.addWidget(ModernLabel("Axis", bold=True, font_size=10), 0, 0)
        data_layout.addWidget(ModernLabel("Min", bold=True, font_size=10), 0, 1)
        data_layout.addWidget(ModernLabel("Max", bold=True, font_size=10), 0, 2)
        data_layout.addWidget(ModernLabel("Center", bold=True, font_size=10), 0, 3)
        
        # Create labels for each axis
        self.data_labels = {}
        axes = [('L-X', 'lx'), ('L-Y', 'ly'), ('R-X', 'rx'), ('R-Y', 'ry')]
        
        for i, (name, key) in enumerate(axes, 1):
            data_layout.addWidget(ModernLabel(name, font_size=10), i, 0)
            self.data_labels[key] = {
                'min': ModernLabel("--", font_size=10),
                'max': ModernLabel("--", font_size=10),
                'center': ModernLabel("128", font_size=10)
            }
            data_layout.addWidget(self.data_labels[key]['min'], i, 1)
            data_layout.addWidget(self.data_labels[key]['max'], i, 2)
            data_layout.addWidget(self.data_labels[key]['center'], i, 3)
        
        left_column.addWidget(data_group)
        left_column.addStretch()  # Push everything up
        
        # Right column - Controller visualization
        right_column = QVBoxLayout()
        viz_group = QGroupBox("Controller Visualization")
        viz_layout = QVBoxLayout(viz_group)
        viz_layout.setContentsMargins(8, 8, 8, 8)
        
        # Set fixed size for visualization widget
        self.controller_viz.setFixedSize(450, 300)
        viz_layout.addWidget(self.controller_viz)
        right_column.addWidget(viz_group)
        
        # Add columns to content layout
        content_layout.addLayout(left_column, 1)  # 1 part of space
        content_layout.addLayout(right_column, 1)  # 1 part of space
        
        main_layout.addLayout(content_layout)
        
        # Buttons at bottom
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_button = ModernButton("Start Calibration")
        self.start_button.clicked.connect(self._start_calibration)
        button_layout.addWidget(self.start_button)
        
        self.apply_button = ModernButton("Apply & Close")
        self.apply_button.clicked.connect(self._apply_calibration)
        self.apply_button.setEnabled(False)
        button_layout.addWidget(self.apply_button)
        
        self.cancel_button = ModernButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(button_layout)
        
    def _start_calibration(self):
        """Start the calibration process"""
        self.start_button.setEnabled(False)
        self.apply_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        
        self.status_label.setText("Calibrating... Move sticks in all directions!")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.time_remaining = self.calibration_time
        
        # Start the calibration timer
        self.calibration_timer = QTimer()
        self.calibration_timer.timeout.connect(self._update_calibration)
        self.calibration_timer.start(1000)  # Update every second
        
        # Signal to start calibration in the input translator
        self.calibration_requested.emit()
        
    def _update_calibration(self):
        """Update calibration progress"""
        self.time_remaining -= 1
        self.progress_bar.setValue(self.calibration_time - self.time_remaining)
        
        if self.time_remaining > 0:
            self.status_label.setText(f"Calibrating... {self.time_remaining} seconds remaining")
        else:
            self._finish_calibration()
            
    def _finish_calibration(self):
        """Finish the calibration process"""
        if self.calibration_timer:
            self.calibration_timer.stop()
            self.calibration_timer = None
            
        self.progress_bar.setVisible(False)
        self.status_label.setText("Calibration completed! Check the data below.")
        
        self.start_button.setEnabled(True)
        self.apply_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        
        # Signal that calibration is done
        self.calibration_completed.emit()
        
    def update_calibration_data(self, data):
        """Update the displayed calibration data"""
        for axis, values in data.items():
            if axis in self.data_labels:
                self.data_labels[axis]['min'].setText(f"{values['min']:.0f}")
                self.data_labels[axis]['max'].setText(f"{values['max']:.0f}")
                # Center is always 128 for DS4 controllers
                self.data_labels[axis]['center'].setText("128")
                
    def _apply_calibration(self):
        """Apply calibration and close dialog"""
        self.accept()
        
    def update_joystick_data(self, joystick_dict):
        """Update joystick visualization in real-time"""
        if hasattr(self, 'controller_viz'):
            self.controller_viz.update_joystick_data(joystick_dict)
    
    def _get_dark_style(self):
        """Return enhanced dark theme stylesheet"""
        return """
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #444444;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #2a2a2a;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 12px 0 12px;
                color: #ffffff;
                background-color: #1e1e1e;
            }
            
            QTextEdit {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 12px;
                color: #e0e0e0;
                font-size: 13px;
                line-height: 1.4;
            }
            
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 8px;
                text-align: center;
                background-color: #2d2d2d;
                font-weight: bold;
                font-size: 12px;
                color: #ffffff;
                min-height: 25px;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #4CAF50, stop:1 #45a049);
                border-radius: 6px;
                margin: 2px;
            }
            
            QLabel {
                color: #e0e0e0;
                font-size: 12px;
            }
        """
