
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class InputInfoWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self._apply_style()

    def init_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Create labels for all inputs
        self.labels = {
            'left_stick': QLabel("Left Stick: (0, 0)"),
            'right_stick': QLabel("Right Stick: (0, 0)"),
            'triggers': QLabel("Triggers: L2=0, R2=0"),
            'dpad': QLabel("D-Pad: -"),
            'buttons': QLabel("Buttons: -"),
            'shoulders': QLabel("Shoulders: -"),
        }
        
        # Add labels to the grid
        layout.addWidget(self.labels['left_stick'], 0, 0)
        layout.addWidget(self.labels['right_stick'], 0, 1)
        layout.addWidget(self.labels['triggers'], 1, 0)
        layout.addWidget(self.labels['dpad'], 1, 1)
        layout.addWidget(self.labels['buttons'], 2, 0)
        layout.addWidget(self.labels['shoulders'], 2, 1)

    def _apply_style(self):
        self.setStyleSheet('''
            InputInfoWidget {
                background-color: #2c3e50;
                border-radius: 8px;
                margin-top: 10px;
            }
            QLabel {
                color: #ecf0f1;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 14px;
            }
        ''')

    def update_inputs(self, report):
        # Joysticks
        self.labels['left_stick'].setText(f"Left Stick:  ({report.sThumbLX:6d}, {report.sThumbLY:6d})")
        self.labels['right_stick'].setText(f"Right Stick: ({report.sThumbRX:6d}, {report.sThumbRY:6d})")

        # Triggers
        self.labels['triggers'].setText(f"Triggers: L2={report.bLeftTrigger:3d}, R2={report.bRightTrigger:3d}")

        # D-Pad
        dpad_map = {0x0001: 'Up', 0x0002: 'Down', 0x0004: 'Left', 0x0008: 'Right'}
        dpad_active = [name for flag, name in dpad_map.items() if report.wButtons & flag]
        self.labels['dpad'].setText(f"D-Pad: {', '.join(dpad_active) or '-'}")

        # Face Buttons
        button_map = {0x1000: 'A (✕)', 0x2000: 'B (○)', 0x4000: 'X (□)', 0x8000: 'Y (△)'}
        buttons_active = [name for flag, name in button_map.items() if report.wButtons & flag]
        self.labels['buttons'].setText(f"Buttons: {', '.join(buttons_active) or '-'}")

        # Shoulder Buttons
        shoulder_map = {0x0100: 'L1', 0x0200: 'R1'}
        shoulders_active = [name for flag, name in shoulder_map.items() if report.wButtons & flag]
        self.labels['shoulders'].setText(f"Shoulders: {', '.join(shoulders_active) or '-'}")

