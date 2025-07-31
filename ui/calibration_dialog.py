from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QTextEdit, QGroupBox,
                             QFrame, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette
from .modern_widgets import ModernButton, ModernLabel


class CalibrationDialog(QDialog):
    """Dialog for controller stick calibration process"""
    
    calibration_requested = pyqtSignal()
    calibration_completed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Controller Calibration")
        self.setModal(True)
        self.setFixedSize(700, 600)  # Increased size to avoid overlapping
        self.setStyleSheet(self._get_dark_style())
        
        self.calibration_timer = None
        self.calibration_time = 10  # seconds
        self.time_remaining = self.calibration_time
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the calibration dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = ModernLabel("Controller Calibration", font_size=18, bold=True)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Instructions group
        instructions_group = QGroupBox("Instructions")
        instructions_layout = QVBoxLayout(instructions_group)
        
        instructions_text = QTextEdit()
        instructions_text.setFixedHeight(130)  # Fixed height instead of maximum
        instructions_text.setReadOnly(True)
        instructions_text.setPlainText(
            "This calibration will help correct stick drift issues.\n\n"
            "When you start calibration:\n"
            "1. Leave both analog sticks in the center position for 2 seconds\n"
            "2. Move each stick in complete circles several times\n"
            "3. Push each stick to all extreme positions (up, down, left, right)\n"
            "4. Return sticks to center when the timer completes\n\n"
            "The calibration will run for 10 seconds."
        )
        instructions_layout.addWidget(instructions_text)
        layout.addWidget(instructions_group)
        
        # Calibration status group
        status_group = QGroupBox("Calibration Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = ModernLabel("Ready to calibrate", font_size=12)
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.calibration_time)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(status_group)
        
        # Calibration data display
        data_group = QGroupBox("Calibration Data")
        data_group.setFixedHeight(180)  # Fixed height to prevent overlap
        data_layout = QGridLayout(data_group)
        data_layout.setSpacing(10)  # Add spacing between elements
        
        # Headers
        data_layout.addWidget(ModernLabel("Axis", bold=True), 0, 0)
        data_layout.addWidget(ModernLabel("Min", bold=True), 0, 1)
        data_layout.addWidget(ModernLabel("Max", bold=True), 0, 2)
        data_layout.addWidget(ModernLabel("Center", bold=True), 0, 3)
        
        # Create labels for each axis
        self.data_labels = {}
        axes = [('Left X', 'lx'), ('Left Y', 'ly'), ('Right X', 'rx'), ('Right Y', 'ry')]
        
        for i, (name, key) in enumerate(axes, 1):
            data_layout.addWidget(ModernLabel(name), i, 0)
            self.data_labels[key] = {
                'min': ModernLabel("--"),
                'max': ModernLabel("--"),
                'center': ModernLabel("128")  # Default center value
            }
            data_layout.addWidget(self.data_labels[key]['min'], i, 1)
            data_layout.addWidget(self.data_labels[key]['max'], i, 2)
            data_layout.addWidget(self.data_labels[key]['center'], i, 3)
        
        layout.addWidget(data_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
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
        
        layout.addLayout(button_layout)
        
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
        
    def _get_dark_style(self):
        """Return dark theme stylesheet"""
        return """
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
            
            QTextEdit {
                background-color: #3a3a3a;
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
            }
            
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 6px;
                text-align: center;
                background-color: #3a3a3a;
            }
            
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """
