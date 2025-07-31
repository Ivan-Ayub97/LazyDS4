from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from .modern_widgets import ModernProgressBar, GlowLabel

class ControllerWidget(QFrame):
    """Stylized widget for real-time controller input visualization"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.controller_connected = False
        self._apply_style()
        
    def init_ui(self):
        """Initialize the UI components of the widget"""
        main_layout = QVBoxLayout(self)
        
        # Top section: Connection status
        status_layout = QHBoxLayout()
        self.connection_status = QLabel("CONTROLLER DISCONNECTED")
        self.connection_status.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.connection_status.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.connection_status)
        main_layout.addLayout(status_layout)
        
        # Middle section: Analog sticks and D-pad
        middle_layout = QHBoxLayout()
        
        # Left stick and D-pad
        left_section = QGridLayout()
        left_section.addWidget(GlowLabel("Left Stick"), 0, 0, 1, 2, Qt.AlignCenter)
        self.left_stick_x = QLabel("X: 0")
        self.left_stick_y = QLabel("Y: 0")
        left_section.addWidget(self.left_stick_x, 1, 0, Qt.AlignCenter)
        left_section.addWidget(self.left_stick_y, 1, 1, Qt.AlignCenter)
        
        left_section.addWidget(GlowLabel("D-Pad"), 2, 0, 1, 2, Qt.AlignCenter)
        self.dpad_status = QLabel("-")
        self.dpad_status.setFont(QFont("Segoe UI", 14, QFont.Bold))
        left_section.addWidget(self.dpad_status, 3, 0, 1, 2, Qt.AlignCenter)
        
        middle_layout.addLayout(left_section)
        middle_layout.addStretch()
        
        # Right stick and face buttons
        right_section = QGridLayout()
        right_section.addWidget(GlowLabel("Right Stick"), 0, 0, 1, 2, Qt.AlignCenter)
        self.right_stick_x = QLabel("X: 0")
        self.right_stick_y = QLabel("Y: 0")
        right_section.addWidget(self.right_stick_x, 1, 0, Qt.AlignCenter)
        right_section.addWidget(self.right_stick_y, 1, 1, Qt.AlignCenter)
        
        right_section.addWidget(GlowLabel("Face Buttons"), 2, 0, 1, 2, Qt.AlignCenter)
        self.button_status = QLabel("-")
        self.button_status.setFont(QFont("Segoe UI", 12))
        right_section.addWidget(self.button_status, 3, 0, 1, 2, Qt.AlignCenter)
        
        middle_layout.addLayout(right_section)
        main_layout.addLayout(middle_layout)
        
        # Bottom section: Triggers
        trigger_layout = QGridLayout()
        trigger_layout.addWidget(QLabel("Left Trigger"), 0, 0, Qt.AlignCenter)
        self.left_trigger = ModernProgressBar()
        trigger_layout.addWidget(self.left_trigger, 1, 0)
        
        trigger_layout.addWidget(QLabel("Right Trigger"), 0, 1, Qt.AlignCenter)
        self.right_trigger = ModernProgressBar()
        trigger_layout.addWidget(self.right_trigger, 1, 1)
        
        main_layout.addLayout(trigger_layout)
        self.setLayout(main_layout)
        
    def _apply_style(self):
        """Apply custom styling for the widget"""
        self.setStyleSheet("""
            ControllerWidget {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2C2C2C, stop:1 #3C3C3C);
                border: 1px solid #1A1A1A;
                border-radius: 12px;
                padding: 15px;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 10px;
            }
        """)

    def update_connection_status(self, connected):
        """Update the connection status display"""
        self.controller_connected = connected
        if connected:
            self.connection_status.setText("CONTROLLER CONNECTED")
            self.connection_status.setStyleSheet("color: #2ECC71;") # Green
        else:
            self.connection_status.setText("CONTROLLER DISCONNECTED")
            self.connection_status.setStyleSheet("color: #E74C3C;") # Red
            self._reset_inputs()
            
    def update_inputs(self, xinput_report):
        """Update all input visualizations"""
        if not self.controller_connected:
            return
            
        # Triggers
        self.left_trigger.setValue(xinput_report.bLeftTrigger)
        self.right_trigger.setValue(xinput_report.bRightTrigger)
        
        # Analog sticks
        self.left_stick_x.setText(f"X: {xinput_report.sThumbLX:6d}")
        self.left_stick_y.setText(f"Y: {xinput_report.sThumbLY:6d}")
        self.right_stick_x.setText(f"X: {xinput_report.sThumbRX:6d}")
        self.right_stick_y.setText(f"Y: {xinput_report.sThumbRY:6d}")
        
        # D-pad
        dpad_str = ""
        if xinput_report.wButtons & 0x0001: dpad_str += "↑ "
        if xinput_report.wButtons & 0x0002: dpad_str += "↓ "
        if xinput_report.wButtons & 0x0004: dpad_str += "← "
        if xinput_report.wButtons & 0x0008: dpad_str += "→ "
        self.dpad_status.setText(dpad_str if dpad_str else "-")
        
        # Face buttons
        button_str = ""
        if xinput_report.wButtons & 0x1000: button_str += "A " # Cross
        if xinput_report.wButtons & 0x2000: button_str += "B " # Circle
        if xinput_report.wButtons & 0x4000: button_str += "X " # Square
        if xinput_report.wButtons & 0x8000: button_str += "Y " # Triangle
        self.button_status.setText(button_str if button_str else "-")

    def _reset_inputs(self):
        """Reset all input displays to their default state"""
        self.left_trigger.setValue(0)
        self.right_trigger.setValue(0)
        self.left_stick_x.setText("X: 0")
        self.left_stick_y.setText("Y: 0")
        self.right_stick_x.setText("X: 0")
        self.right_stick_y.setText("Y: 0")
        self.dpad_status.setText("-")
        self.button_status.setText("-")
