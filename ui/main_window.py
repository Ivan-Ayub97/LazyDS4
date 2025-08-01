import os
import sys

from PyQt5.QtCore import (QEasingCurve, QObject, QPropertyAnimation, QRect, Qt,
                          QTimer, pyqtSignal)
from PyQt5.QtGui import (QColor, QFont, QIcon, QLinearGradient, QPainter,
                         QPalette, QPixmap)
from PyQt5.QtWidgets import (QApplication, QDialog, QFrame,
                             QGraphicsDropShadowEffect, QHBoxLayout, QLabel,
                             QMainWindow, QMessageBox, QPushButton,
                             QScrollArea, QSizePolicy, QSpacerItem, QSplitter,
                             QTabWidget, QTextEdit, QVBoxLayout, QWidget)

from .battery_widget import BatteryWidget
from .calibration_dialog import CalibrationDialog
from .input_info_widget import InputInfoWidget
from .interactive_controller import InteractiveControllerWidget
from .pairing_dialog import PairingDialog


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class LogSignal(QObject):
    """Signal for logging messages to the UI"""
    log_message = pyqtSignal(str)


class MainWindow(QMainWindow):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.setWindowTitle("LazyDS4 2.0")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon(resource_path("assets/icon.ico")))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self._create_widgets()
        self._apply_dark_theme()

    def _create_widgets(self):
        """Create all UI widgets"""
        # Add shadow effect to main window
        self._add_shadow_effects()

        # Title and status card
        title_frame = QFrame()
        title_frame.setAccessibleName("card")
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(20, 15, 20, 15)

        title_label = QLabel("DualShock 4 to Xinput Controller")
        title_label.setAccessibleName("title")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)

        self.status_label = QLabel("Status: Service Stopped")
        self.status_label.setAccessibleName("status")
        self.status_label.setFont(QFont("Segoe UI", 11, QFont.Medium))
        self.status_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.status_label)

        self.layout.addWidget(title_frame)

        # Create tabs
        self.tabs = QTabWidget()

        # Main control tab
        control_tab = QWidget()
        control_layout = QVBoxLayout(control_tab)

        # Controller and battery widgets layout
        main_layout = QHBoxLayout()

        # Left side: Controller info and status
        left_panel = QVBoxLayout()

        # Controller widget
        self.controller_widget = InteractiveControllerWidget()
        left_panel.addWidget(self.controller_widget)

        # Controller details
        self.controller_info_label = QLabel("No controller connected")
        self.controller_info_label.setFont(QFont("Segoe UI", 9))
        self.controller_info_label.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(self.controller_info_label)

        main_layout.addLayout(left_panel)

        # Right side: Battery and input info
        right_panel = QVBoxLayout()
        right_panel.setSpacing(20)

        # Battery widget
        battery_section = QVBoxLayout()
        battery_label = QLabel("Battery Status")
        battery_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        battery_label.setAlignment(Qt.AlignCenter)
        battery_section.addWidget(battery_label)
        self.battery_widget = BatteryWidget()
        battery_section.addWidget(self.battery_widget)
        right_panel.addLayout(battery_section)

        # Input info widget
        self.input_info_widget = InputInfoWidget()
        right_panel.addWidget(self.input_info_widget)

        main_layout.addLayout(right_panel)

        control_layout.addLayout(main_layout)

        # Control buttons with modern styling
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.start_button = QPushButton("▶ Start Service")
        self.start_button.setAccessibleName("start")
        self.start_button.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.start_button.clicked.connect(self._on_start_clicked)
        self._add_button_shadow(self.start_button)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("⏹ Stop Service")
        self.stop_button.setAccessibleName("stop")
        self.stop_button.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.stop_button.setEnabled(False)
        self._add_button_shadow(self.stop_button)
        button_layout.addWidget(self.stop_button)

        # Add Bluetooth pairing button
        self.pair_button = QPushButton("📱 Pair Controller")
        self.pair_button.setAccessibleName("pair")
        self.pair_button.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.pair_button.clicked.connect(self._on_pair_clicked)
        self._add_button_shadow(self.pair_button)
        button_layout.addWidget(self.pair_button)

        # Add calibration button
        self.calibrate_button = QPushButton("🎯 Calibrate Controller")
        self.calibrate_button.setAccessibleName("calibrate")
        self.calibrate_button.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.calibrate_button.clicked.connect(self._on_calibrate_clicked)
        # Only enabled when controller is connected
        self.calibrate_button.setEnabled(False)
        self._add_button_shadow(self.calibrate_button)
        button_layout.addWidget(self.calibrate_button)

        # Drift warning elements (initially hidden)
        self.drift_warning_label = QLabel("⚠️ Stick drift detected! Calibration recommended.")
        self.drift_warning_label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.drift_warning_label.setAlignment(Qt.AlignCenter)
        self.drift_warning_label.setVisible(False)
        self.drift_warning_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 152, 0, 0.15);
                border: 2px solid #ff9800;
                border-radius: 8px;
                padding: 8px;
                color: #ff9800;
                margin: 4px;
            }
        """)

        control_layout.addLayout(button_layout)

        # Add drift warning below buttons (initially hidden)
        control_layout.addWidget(self.drift_warning_label)

        control_layout.addStretch()

        # Initialize drift detection features
        self.drift_blink_timer = QTimer()
        self.drift_blink_timer.timeout.connect(self._blink_calibration_button)
        self.drift_blink_state = False
        self.drift_detected = False

        # Add test button for drift detection (temporary for testing)
        test_drift_button = QPushButton("🧪 Test Drift Detection")
        test_drift_button.setFont(QFont("Segoe UI", 8))
        test_drift_button.clicked.connect(self._test_drift_detection)
        control_layout.addWidget(test_drift_button)

        self.tabs.addTab(control_tab, "Controller")

        # Log tab
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)

        log_label = QLabel("Application Log:")
        log_label.setFont(QFont("Segoe UI", 10))
        log_layout.addWidget(log_label)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_output)

        clear_log_button = QPushButton("Clear Log")
        clear_log_button.clicked.connect(self.log_output.clear)
        log_layout.addWidget(clear_log_button)

        self.tabs.addTab(log_tab, "Log")

        # Settings tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)

        settings_label = QLabel("Info app:")
        settings_label.setFont(QFont("Segoe UI", 10))
        settings_layout.addWidget(settings_label)

        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText("""
Application developed by Iván Eduardo Chavez Ayub. @Ivan-Ayub97 on GitHub.
MIT License.

• Supported Controllers: DualShock 4 (v1 & v2)
• Virtual Controller: Xbox 360 (XInput)
• Connection: USB or Bluetooth
• Polling Rate: ~1ms (1000Hz)

Button Mapping:
• Square  → X
• Cross   → A
• Circle  → B
• Triangle → Y
• L1/R1   → LB/RB
• L2/R2   → LT/RT
• Share   → Back
• Options → Start
• PS Button → Guide
        """)
        settings_layout.addWidget(info_text)

        # Add a button to force reinstall ViGEmBus
        self.reinstall_button = QPushButton("⚙️ Reinstall ViGEmBus Driver")
        self.reinstall_button.setAccessibleName("reinstall")
        self.reinstall_button.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.reinstall_button.clicked.connect(self._on_reinstall_vigem)
        self._add_button_shadow(self.reinstall_button)
        settings_layout.addWidget(self.reinstall_button)

        self.tabs.addTab(settings_tab, "Info")

        self.layout.addWidget(self.tabs)

    def _add_shadow_effects(self):
        """Add shadow effects to the main window and key elements"""
        # Add shadow effect to the main window
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

    def _add_button_shadow(self, button):
        """Add subtle shadow effect to buttons"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 2)
        button.setGraphicsEffect(shadow)

    def _apply_dark_theme(self):
        """Apply a modern dark theme with gradients, shadows, and rounded corners"""
        self.setStyleSheet("""
            /* Main Window Styling */
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1a, stop:1 #2d2d30);
                color: #ffffff;
            }

            /* Central Widget */
            QWidget#centralWidget {
                background: transparent;
            }

            /* Labels */
            QLabel {
                color: #ffffff;
                font-weight: 500;
            }

            /* Title Labels */
            QLabel[accessibleName="title"] {
                color: #00d4ff;
                font-weight: bold;
                text-shadow: 0px 0px 10px rgba(0, 212, 255, 0.3);
            }

            /* Status Label */
            QLabel[accessibleName="status"] {
                color: #ffffff;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 212, 255, 0.1), stop:1 rgba(0, 212, 255, 0.05));
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 8px;
                padding: 8px 16px;
                margin: 4px;
            }

            /* Modern TabWidget */
            QTabWidget {
                background: transparent;
                border: none;
            }

            QTabWidget::pane {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 45, 48, 0.95), stop:1 rgba(35, 35, 38, 0.95));
                border: 1px solid rgba(100, 100, 100, 0.3);
                border-radius: 12px;
                margin-top: 8px;
            }

            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(60, 60, 63, 0.8), stop:1 rgba(45, 45, 48, 0.8));
                color: #cccccc;
                border: 1px solid rgba(100, 100, 100, 0.2);
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 25px;
                margin-right: 3px;
                font-weight: 500;
                min-width: 80px;
            }

            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00d4ff, stop:1 #0099cc);
                color: #ffffff;
                border: 1px solid #00d4ff;
                font-weight: bold;
            }

            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 212, 255, 0.2), stop:1 rgba(0, 153, 204, 0.2));
                color: #ffffff;
            }

            /* Modern Buttons */
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 #357abd);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11px;
                min-height: 16px;
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5aa3f0, stop:1 #4285d1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                transform: translateY(-1px);
            }

            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #357abd, stop:1 #2968a3);
                transform: translateY(1px);
            }

            QPushButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(60, 60, 63, 0.5), stop:1 rgba(45, 45, 48, 0.5));
                color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(100, 100, 100, 0.1);
            }

            /* Special Button Styles */
            QPushButton[accessibleName="start"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:1 #388e3c);
            }

            QPushButton[accessibleName="start"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66bb6a, stop:1 #4caf50);
            }

            QPushButton[accessibleName="stop"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f44336, stop:1 #d32f2f);
            }

            QPushButton[accessibleName="stop"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ef5350, stop:1 #f44336);
            }

            QPushButton[accessibleName="pair"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9800, stop:1 #f57c00);
            }

            QPushButton[accessibleName="pair"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffb74d, stop:1 #ff9800);
            }

            QPushButton[accessibleName="reinstall"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #9c27b0, stop:1 #7b1fa2);
            }

            QPushButton[accessibleName="reinstall"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ba68c8, stop:1 #9c27b0);
            }

            QPushButton[accessibleName="calibrate"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #607d8b, stop:1 #455a64);
            }

            QPushButton[accessibleName="calibrate"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #78909c, stop:1 #607d8b);
            }

            /* Modern TextEdit */
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 30, 32, 0.95), stop:1 rgba(20, 20, 22, 0.95));
                color: #ffffff;
                border: 1px solid rgba(100, 100, 100, 0.3);
                border-radius: 8px;
                padding: 12px;
                selection-background-color: rgba(0, 212, 255, 0.3);
                font-family: 'Consolas', 'Monaco', monospace;
            }

            QTextEdit:focus {
                border: 2px solid #00d4ff;
            }

            /* Scrollbars */
            QScrollBar:vertical {
                background: rgba(45, 45, 48, 0.3);
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:1 #0099cc);
                border-radius: 6px;
                min-height: 20px;
            }

            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #33ddff, stop:1 #00b3e6);
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar:horizontal {
                background: rgba(45, 45, 48, 0.3);
                height: 12px;
                border-radius: 6px;
                margin: 0;
            }

            QScrollBar::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00d4ff, stop:1 #0099cc);
                border-radius: 6px;
                min-width: 20px;
            }

            QScrollBar::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #33ddff, stop:1 #00b3e6);
            }

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }

            /* Modern Frames */
            QFrame {
                background: transparent;
                border: none;
            }

            QFrame[accessibleName="card"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 45, 48, 0.8), stop:1 rgba(35, 35, 38, 0.8));
                border: 1px solid rgba(100, 100, 100, 0.2);
                border-radius: 12px;
                margin: 8px;
            }
        """)

    def _on_start_clicked(self):
        """Handle start button click"""
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.app.start()

    def _on_stop_clicked(self):
        """Handle stop button click"""
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.app.stop()

    def update_status(self, message):
        self.status_label.setText(f"Status: {message}")

    def append_log(self, message):
        self.log_output.append(message)

    def update_controller_info(self, info_dict):
        """Update controller information display"""
        if info_dict:
            connection_type = info_dict.get('connection_type', 'Unknown')
            vendor_id = info_dict.get('vendor_id', 'Unknown')
            product_id = info_dict.get('product_id', 'Unknown')
            serial = info_dict.get('serial_number', 'Unknown')

            info_text = f"{connection_type}\nVID: {vendor_id} | PID: {product_id}\nSerial: {serial}"
            self.controller_info_label.setText(info_text)

            # Enable calibration button when controller is connected
            self.calibrate_button.setEnabled(True)

            # Also log the full info
            full_info = "\n".join([f"{k}: {v}" for k, v in info_dict.items()])
            self.append_log(f"[INFO] Controller Connected:\n{full_info}")
        else:
            self.controller_info_label.setText("No controller connected")
            # Disable calibration button when no controller
            self.calibrate_button.setEnabled(False)

    def update_battery_status(self, level, is_charging):
        """Update battery widget with new status"""
        self.battery_widget.update_battery_status(
            level, is_charging, is_connected=True)

    def on_controller_disconnected(self):
        """Handle controller disconnection"""
        self.battery_widget.update_battery_status(0, False, is_connected=False)
        # Disable calibration button when controller disconnects
        self.calibrate_button.setEnabled(False)

    def show_battery_warning(self, level):
        """Show low battery warning dialog"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Low Battery Warning")
        msg.setText(f"Controller battery is low: {level}%")
        msg.setInformativeText(
            "Please charge your controller soon to avoid disconnection.")
        msg.setWindowIcon(QIcon("assets/icon.ico"))

        # Apply dark theme to message box
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2E2F30;
                color: #F0F0F0;
            }
            QMessageBox QPushButton {
                background-color: #4A4B4C;
                color: #F0F0F0;
                border: 1px solid #6A6B6C;
                padding: 5px 15px;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #6A6B6C;
            }
        """)

        msg.exec_()
        self.append_log(f"[WARNING] Low battery: {level}%")

    def closeEvent(self, event):
        """Ensure the background thread is stopped on exit"""
        self.app.stop()
        event.accept()

    def _on_pair_clicked(self):
        """Handle pair controller button click"""
        self.append_log("[INFO] Attempting to auto-pair with a Bluetooth controller...")
        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:
            from utils.bluetooth_manager import BluetoothManager
            bt_manager = BluetoothManager()

            # Attempt auto pairing with DS4 controller
            if bt_manager.auto_pair_controller():
                self.append_log("[SUCCESS] Paired with a Bluetooth controller!")
                QMessageBox.information(self, "Pairing Successful",
                                        "A Bluetooth controller has been paired successfully.")
            else:
                self.append_log("[INFO] No available controllers found for pairing.")
                QMessageBox.warning(self, "Pairing Failed",
                                    "Could not find or pair any new controllers.")
        except Exception as e:
            self.append_log(f"[ERROR] Failed to pair with device: {e}")

        QApplication.restoreOverrideCursor()

    def _on_reinstall_vigem(self):
        """Handle the reinstall ViGEmBus button click"""
        # Show information dialog first
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("ViGEmBus Driver Installation")
        msg.setText("Installing ViGEmBus Driver")
        msg.setInformativeText(
            "The ViGEmBus installer will now launch. You will need to:\n\n"
            "1. Accept the UAC prompt (Administrator privileges required)\n"
            "2. Accept the license agreement in the installer\n"
            "3. Follow the installation wizard\n\n"
            "Click OK to continue."
        )
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Ok)

        # Apply dark theme to message box
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2E2F30;
                color: #F0F0F0;
            }
            QMessageBox QPushButton {
                background-color: #4A4B4C;
                color: #F0F0F0;
                border: 1px solid #6A6B6C;
                padding: 5px 15px;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #6A6B6C;
            }
        """)

        if msg.exec_() != QMessageBox.Ok:
            return

        self.append_log("[INFO] Starting ViGEmBus driver installation...")

        try:
            from utils.vigem_setup import ViGEmSetup
            vigem_setup = ViGEmSetup()

            # Stop the service if it's running
            if self.app.running.is_set():
                self.app.stop()
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                self.append_log(
                    "[INFO] Service stopped for driver installation.")

            # Launch the installer (non-blocking)
            success = vigem_setup.install_vigem(silent=False)

            if success:
                self.append_log(
                    "[INFO] ViGEmBus installer launched. Please complete the installation process.")

                # Show follow-up message
                follow_up = QMessageBox()
                follow_up.setIcon(QMessageBox.Information)
                follow_up.setWindowTitle("Installation In Progress")
                follow_up.setText("ViGEmBus Installer Launched")
                follow_up.setInformativeText(
                    "The ViGEmBus installer is now running. After completing the installation:\n\n"
                    "1. Close the installer window\n"
                    "2. Restart LazyDS4 if needed\n"
                    "3. Try starting the service again\n\n"
                    "The installation may take a few minutes to complete."
                )
                follow_up.setStyleSheet(msg.styleSheet())  # Use same dark theme
                follow_up.exec_()

            else:
                self.append_log(
                    "[ERROR] Failed to launch ViGEmBus installer. Check the log for details.")
                QMessageBox.critical(self, "Installation Failed",
                                     "Failed to launch the ViGEmBus installer. Please try running LazyDS4 as an administrator or install ViGEmBus manually from the assets folder.")
        except Exception as e:
            self.append_log(
                f"[ERROR] An unexpected error occurred during installation: {e}")
            QMessageBox.critical(self, "Installation Error",
                                f"An error occurred while trying to install ViGEmBus: {str(e)}")

    def _on_pair_device_requested(self, device_address):
        """Handle pairing request from dialog"""
        self.append_log(
            f"[INFO] Attempting to pair with device: {device_address}")

        try:
            from utils.bluetooth_manager import BluetoothManager
            bt_manager = BluetoothManager()
            success = bt_manager.pair_device(device_address)

            if success:
                QMessageBox.information(self, "Pairing Initiated",
                                        "Windows Bluetooth settings have been opened.\n"
                                        "Please complete the pairing process in the Settings window.")
            else:
                QMessageBox.warning(self, "Pairing Failed",
                                    "Could not open Bluetooth settings.")
        except Exception as e:
            self.append_log(f"[ERROR] Failed to initiate pairing: {e}")

    def _on_calibrate_clicked(self):
        """Handle calibrate controller button click"""
        if not self.app.translator:
            QMessageBox.warning(self, "No Controller",
                                "Please connect a controller first before calibration.")
            return

        self.append_log("[INFO] Starting controller calibration...")

        # Create and show calibration dialog
        calibration_dialog = CalibrationDialog(self)

        # Connect signals
        calibration_dialog.calibration_requested.connect(
            lambda: self.app.translator.start_calibration()
        )
        calibration_dialog.calibration_completed.connect(
            lambda: self.app.translator.stop_calibration()
        )

        # Connect calibration data updates (both real-time and final)
        self.app.translator.calibration_updated.connect(
            calibration_dialog.update_calibration_data
        )
        self.app.translator.calibration_finished.connect(
            calibration_dialog.update_calibration_data
        )

        # Connect real-time joystick data to visualization widget
        self.app.translator.joystick_data_updated.connect(
            calibration_dialog.controller_viz.update_joystick_data
        )

        # Show the dialog
        result = calibration_dialog.exec_()

        if result == QDialog.Accepted:
            self.append_log(
                "[SUCCESS] Controller calibration completed and applied.")
        else:
            self.append_log("[INFO] Controller calibration cancelled.")

    def on_drift_detected(self, drift_info):
        """Handle drift detection signal from input translator"""
        has_drift = drift_info.get('has_drift', False)
        drift_axes = drift_info.get('drift_axes', [])
        severity = drift_info.get('severity', 'none')

        if has_drift:
            self.drift_detected = True
            axes_text = ', '.join(drift_axes)

            # Update warning label with specific information
            self.drift_warning_label.setText(
                f"⚠️ Stick drift detected on {axes_text}! Calibration recommended."
            )

            # Show warning and start blinking
            self.drift_warning_label.setVisible(True)
            self._start_calibration_button_blink()

            # Log the drift detection
            self.append_log(
                f"[DRIFT DETECTED] Stick drift found on {axes_text} ({severity} severity). "
                "Consider running calibration to fix this issue."
            )

            # Update warning color based on severity
            self._update_drift_warning_color(severity)
        else:
            # No drift detected
            self.drift_detected = False
            self.drift_warning_label.setVisible(False)
            self._stop_calibration_button_blink()

    def _start_calibration_button_blink(self):
        """Start blinking the calibration button to draw attention"""
        if not self.drift_blink_timer.isActive():
            self.drift_blink_timer.start(800)  # Blink every 800ms

    def _stop_calibration_button_blink(self):
        """Stop blinking the calibration button"""
        if self.drift_blink_timer.isActive():
            self.drift_blink_timer.stop()
            self.drift_blink_state = False
            self._reset_calibration_button_style()

    def _blink_calibration_button(self):
        """Toggle calibration button appearance for blinking effect"""
        if not self.drift_detected or not self.calibrate_button.isEnabled():
            self._stop_calibration_button_blink()
            return

        self.drift_blink_state = not self.drift_blink_state

        if self.drift_blink_state:
            # Highlighted state - orange/red to indicate attention needed
            self.calibrate_button.setStyleSheet("""
                QPushButton[accessibleName="calibrate"] {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ff9800, stop:1 #f57c00);
                    border: 2px solid #ffb74d;
                    box-shadow: 0 0 10px rgba(255, 152, 0, 0.6);
                }
            """)
        else:
            # Normal state
            self._reset_calibration_button_style()

    def _reset_calibration_button_style(self):
        """Reset calibration button to normal style"""
        self.calibrate_button.setStyleSheet("""
            QPushButton[accessibleName="calibrate"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #607d8b, stop:1 #455a64);
            }
            QPushButton[accessibleName="calibrate"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #78909c, stop:1 #607d8b);
            }
        """)

    def _update_drift_warning_color(self, severity):
        """Update drift warning color based on severity"""
        if severity == 'mild':
            color = '#ffeb3b'  # Yellow
            bg_color = 'rgba(255, 235, 59, 0.15)'
        elif severity == 'moderate':
            color = '#ff9800'  # Orange
            bg_color = 'rgba(255, 152, 0, 0.15)'
        elif severity == 'severe':
            color = '#f44336'  # Red
            bg_color = 'rgba(244, 67, 54, 0.15)'
        else:
            color = '#ff9800'  # Default orange
            bg_color = 'rgba(255, 152, 0, 0.15)'

        self.drift_warning_label.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                border: 2px solid {color};
                border-radius: 8px;
                padding: 8px;
                color: {color};
                margin: 4px;
            }}
        """)

    def _test_drift_detection(self):
        """Test method to manually trigger drift detection (for testing purposes)"""
        # Simulate drift detection for testing
        test_drift_info = {
            'has_drift': True,
            'drift_axes': ['Left X', 'Right Y'],
            'severity': 'moderate'
        }

        self.on_drift_detected(test_drift_info)
        self.append_log("[TEST] Drift detection test triggered manually.")
