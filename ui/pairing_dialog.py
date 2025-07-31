# C:\Users\negro\Desktop\LazyDS4\ui\pairing_dialog.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QListWidget,
                             QPushButton, QHBoxLayout, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal

class PairingDialog(QDialog):
    """
    A dialog for showing discovered Bluetooth devices and initiating pairing.
    """
    pair_device_requested = pyqtSignal(str) # Emits device address

    def __init__(self, devices, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pair New Controller")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        self.layout = QVBoxLayout(self)
        
        self.info_label = QLabel()
        self.layout.addWidget(self.info_label)
        
        self.device_list = QListWidget()
        self.device_list.itemClicked.connect(self.on_device_selected)
        self.layout.addWidget(self.device_list)
        
        button_layout = QHBoxLayout()
        self.pair_button = QPushButton("Pair Selected Device")
        self.pair_button.setEnabled(False)
        self.pair_button.clicked.connect(self.on_pair_clicked)
        button_layout.addWidget(self.pair_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.layout.addLayout(button_layout)
        
        self.update_device_list(devices)
        
        # Apply modern dark theme
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1a, stop:1 #2d2d30);
                color: #ffffff;
                border-radius: 12px;
            }
            
            QLabel {
                color: #ffffff;
                font-weight: 500;
            }
            
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 30, 32, 0.95), stop:1 rgba(20, 20, 22, 0.95));
                color: #ffffff;
                border: 1px solid rgba(100, 100, 100, 0.3);
                border-radius: 8px;
                padding: 8px;
                selection-background-color: rgba(0, 212, 255, 0.3);
                font-family: 'Segoe UI', sans-serif;
            }
            
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px 0px;
            }
            
            QListWidget::item:hover {
                background: rgba(0, 212, 255, 0.1);
            }
            
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 212, 255, 0.4), stop:1 rgba(0, 153, 204, 0.4));
                border: 1px solid rgba(0, 212, 255, 0.6);
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 #357abd);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11px;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5aa3f0, stop:1 #4285d1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #357abd, stop:1 #2968a3);
            }
            
            QPushButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(60, 60, 63, 0.5), stop:1 rgba(45, 45, 48, 0.5));
                color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(100, 100, 100, 0.1);
            }
        """)

    def update_device_list(self, devices):
        self.device_list.clear()
        if devices:
            self.info_label.setText("Found controllers in pairing mode:\nSelect one to pair with Windows.")
            for dev in devices:
                name = dev.get('Name', 'Unknown Device')
                address = dev.get('Address', 'N/A')
                self.device_list.addItem(f"{name} - {address}")
        else:
            self.info_label.setText(
                "No controllers found in pairing mode.\n\n" +
                "To put your DS4 in pairing mode:\n" +
                "1. Turn off the controller\n" +
                "2. Hold SHARE + PS buttons until light bar flashes\n" +
                "3. The light bar should flash rapidly (white/blue)\n" +
                "4. Click 'Refresh' to scan again"
            )

    def on_device_selected(self, item):
        self.pair_button.setEnabled(True)
        
    def on_pair_clicked(self):
        selected_item = self.device_list.currentItem()
        if not selected_item:
            return
            
        device_text = selected_item.text()
        # Extract address from "Name - Address" format
        if ' - ' in device_text:
            address = device_text.split(' - ')[-1].strip()
        else:
            # Fallback to original method if format is different
            address = device_text.split('(')[-1].replace(')', '')
        
        self.pair_device_requested.emit(address)
        self.accept()
