import os
import sys

from PyQt5.QtCore import (QEasingCurve, QObject, QPropertyAnimation, QRect, Qt,
                          QTimer, pyqtSignal)
from PyQt5.QtGui import (QColor, QFont, QIcon, QLinearGradient, QPainter,
                         QPalette, QPixmap)
from PyQt5.QtWidgets import (QApplication, QDialog, QFrame,
                             QGraphicsDropShadowEffect, QGridLayout,
                             QHBoxLayout, QLabel, QMainWindow, QMessageBox,
                             QPushButton, QScrollArea, QSizePolicy,
                             QSpacerItem, QSplitter, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget)

from .battery_widget import BatteryWidget
from .calibration_dialog import CalibrationDialog
from .input_info_widget import InputInfoWidget
from .interactive_controller import InteractiveControllerWidget
from .modern_header import ModernHeaderWidget
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
        self.setWindowTitle("LazyDS4 2.1")
        self.setGeometry(100, 100, 1080, 700)
        self.setFixedSize(1080, 680)  # Fixed size - cannot be resized
        self.setWindowIcon(QIcon(resource_path("assets/icon.png")))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(8, 6, 8, 6)
        self.layout.setSpacing(4)

        self._create_widgets()
        self._apply_dark_theme()

    def _create_widgets(self):
        """Create all UI widgets"""
        # Add shadow effect to main window
        self._add_shadow_effects()

        # Modern header
        self.header_widget = ModernHeaderWidget()
        self.layout.addWidget(self.header_widget)

        # Create tabs with optimized spacing and margins
        self.tabs = QTabWidget()
        self.tabs.setContentsMargins(4, 4, 4, 4)
        self.tabs.setDocumentMode(True)

        # Main control tab
        control_tab = QWidget()
        # Changed to VBoxLayout for better control
        control_layout = QVBoxLayout(control_tab)
        control_layout.setContentsMargins(8, 6, 8, 6)
        control_layout.setSpacing(6)

        # Controller and battery widgets layout
        main_layout = QHBoxLayout()

        # Left side: Controller info and status (with premium card container)
        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(5, 5, 5, 5)
        left_panel.setSpacing(8)

        # Create premium card container for controller section
        controller_card = QFrame()
        controller_card.setAccessibleName("card")
        controller_card_layout = QVBoxLayout(controller_card)
        controller_card_layout.setContentsMargins(8, 6, 8, 6)
        controller_card_layout.setSpacing(4)

        # Controller widget
        self.controller_widget = InteractiveControllerWidget()
        controller_card_layout.addWidget(self.controller_widget)

        # Controller details with enhanced styling
        self.controller_info_label = QLabel("No controller connected")
        self.controller_info_label.setFont(
            QFont("Segoe UI", 9, QFont.Weight.Medium))
        self.controller_info_label.setAlignment(Qt.AlignCenter)
        self.controller_info_label.setAccessibleName("controller_info")
        controller_card_layout.addWidget(self.controller_info_label)

        left_panel.addWidget(controller_card)

        main_layout.addLayout(left_panel)

        # Right side: Battery and input info (with premium card containers)
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(5, 5, 5, 5)
        right_panel.setSpacing(8)

        # Battery widget in premium card
        battery_card = QFrame()
        battery_card.setAccessibleName("card")
        battery_card_layout = QVBoxLayout(battery_card)
        battery_card_layout.setContentsMargins(8, 4, 8, 4)
        battery_card_layout.setSpacing(4)

        battery_label = QLabel("Battery Status")
        battery_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        battery_label.setAlignment(Qt.AlignCenter)
        battery_label.setAccessibleName("section_title")
        battery_card_layout.addWidget(battery_label)

        self.battery_widget = BatteryWidget()
        battery_card_layout.addWidget(self.battery_widget)
        right_panel.addWidget(battery_card)
        self._add_card_shadow(battery_card)

        # Input info widget in premium card
        input_card = QFrame()
        input_card.setAccessibleName("card")
        input_card_layout = QVBoxLayout(input_card)
        input_card_layout.setContentsMargins(8, 4, 8, 4)
        input_card_layout.setSpacing(3)

        input_label = QLabel("Controller Input")
        input_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        input_label.setAlignment(Qt.AlignCenter)
        input_label.setAccessibleName("section_title")
        input_card_layout.addWidget(input_label)

        self.input_info_widget = InputInfoWidget()
        input_card_layout.addWidget(self.input_info_widget)
        right_panel.addWidget(input_card)
        self._add_card_shadow(input_card)

        main_layout.addLayout(right_panel)

        control_layout.addLayout(main_layout)

        # Divider line
        div_line = QFrame()
        div_line.setFrameShape(QFrame.HLine)
        div_line.setFrameShadow(QFrame.Sunken)
        control_layout.addWidget(div_line)

        # Control buttons in premium card container
        button_card = QFrame()
        button_card.setAccessibleName("card")
        button_card_layout = QVBoxLayout(button_card)
        button_card_layout.setContentsMargins(8, 6, 8, 6)
        button_card_layout.setSpacing(6)

        # Button section title
        button_section_label = QLabel("Controller Actions")
        button_section_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        button_section_label.setAlignment(Qt.AlignCenter)
        button_section_label.setAccessibleName("section_title")
        button_card_layout.addWidget(button_section_label)

        # Control buttons with modern styling - split into two rows
        button_row1 = QHBoxLayout()
        button_row1.setContentsMargins(0, 0, 0, 0)
        button_row1.setSpacing(4)

        button_row2 = QHBoxLayout()
        button_row2.setContentsMargins(0, 0, 0, 0)
        button_row2.setSpacing(4)

        # First row buttons
        self.start_button = QPushButton(" Start")
        self.start_button.setIcon(
            QIcon(resource_path("assets/check-circle.svg")))
        self.start_button.setAccessibleName("start")
        self.start_button.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.start_button.clicked.connect(self._on_start_clicked)
        self._add_button_shadow(self.start_button)
        button_row1.addWidget(self.start_button)

        self.stop_button = QPushButton(" Stop")
        self.stop_button.setIcon(
            QIcon(resource_path("assets/alert-triangle.svg")))
        self.stop_button.setAccessibleName("stop")
        self.stop_button.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.stop_button.setEnabled(False)
        self._add_button_shadow(self.stop_button)
        button_row1.addWidget(self.stop_button)

        # Second row buttons
        self.pair_button = QPushButton(" Pair")
        self.pair_button.setIcon(QIcon(resource_path("assets/bluetooth.svg")))
        self.pair_button.setAccessibleName("pair")
        self.pair_button.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.pair_button.clicked.connect(self._on_pair_clicked)
        self._add_button_shadow(self.pair_button)
        button_row2.addWidget(self.pair_button)

        self.calibrate_button = QPushButton(" Calibrate")
        self.calibrate_button.setIcon(
            QIcon(resource_path("assets/settings.svg")))
        self.calibrate_button.setAccessibleName("calibrate")
        self.calibrate_button.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.calibrate_button.clicked.connect(self._on_calibrate_clicked)
        # Only enabled when controller is connected
        self.calibrate_button.setEnabled(False)
        self._add_button_shadow(self.calibrate_button)
        button_row2.addWidget(self.calibrate_button)

        # Drift warning elements (initially hidden)
        self.drift_warning_label = QLabel(
            "⚠️ Stick drift detected! Calibration recommended.")
        self.drift_warning_label.setFont(
            QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.drift_warning_label.setAlignment(Qt.AlignCenter)
        self.drift_warning_label.setVisible(False)

        button_card_layout.addLayout(button_row1)
        button_card_layout.addLayout(button_row2)

        # Add drift warning inside button card (initially hidden)
        self.drift_warning_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 152, 0, 0.15), stop:1 rgba(255, 152, 0, 0.08));
                border: 2px solid #ff9800;
                border-radius: 8px;
                padding: 8px 12px;
                color: #ff9800;
                margin: 4px 0px;
                font-weight: 600;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
                font-size: 8px;
            }
        """)
        button_card_layout.addWidget(self.drift_warning_label)

        control_layout.addWidget(button_card)
        self._add_card_shadow(button_card)

        # Add minimal stretch to prevent overlapping
        control_layout.addStretch(0)  # Minimal stretch

        # Initialize drift detection features
        self.drift_blink_timer = QTimer()
        self.drift_blink_timer.timeout.connect(self._blink_calibration_button)
        self.drift_blink_state = False
        self.drift_detected = False

        # Add test button for drift detection in a small card (temporary for testing)
        test_card = QFrame()
        test_card.setAccessibleName("card")
        test_card_layout = QHBoxLayout(test_card)
        test_card_layout.setContentsMargins(6, 3, 6, 3)

        test_drift_button = QPushButton(" Test Drift")
        test_drift_button.setIcon(QIcon(resource_path("assets/activity.svg")))
        test_drift_button.setFont(QFont("Segoe UI", 7))
        test_drift_button.setAccessibleName("test")
        test_drift_button.clicked.connect(self._test_drift_detection)
        test_card_layout.addWidget(test_drift_button)

        control_layout.addWidget(test_card)
        self._add_card_shadow(test_card)

        self.tabs.addTab(control_tab, "Controller")
        self.tabs.setTabIcon(0, QIcon(resource_path("assets/refresh-ccw.svg")))

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

        clear_log_button = QPushButton(" Clear Log")
        clear_log_button.setIcon(
            QIcon(resource_path("assets/refresh-ccw.svg")))
        clear_log_button.clicked.connect(self.log_output.clear)
        log_layout.addWidget(clear_log_button)

        self.tabs.addTab(log_tab, "Log")
        self.tabs.setTabIcon(1, QIcon(resource_path("assets/bar-chart.svg")))

        # Settings tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)

        settings_label = QLabel("Information")
        settings_label.setPixmap(
            QPixmap(resource_path("assets/info-icon.png")))
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
        self.reinstall_button = QPushButton(" Reinstall ViGEmBus Driver")
        self.reinstall_button.setIcon(
            QIcon(resource_path("assets/shield.svg")))
        self.reinstall_button.setAccessibleName("reinstall")
        self.reinstall_button.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.reinstall_button.clicked.connect(self._on_reinstall_vigem)
        self._add_button_shadow(self.reinstall_button)
        settings_layout.addWidget(self.reinstall_button)

        self.tabs.addTab(settings_tab, "Info")
        self.tabs.setTabIcon(2, QIcon(resource_path("assets/settings.svg")))

        # Add tabs to the main layout with minimal stretch
        self.layout.addWidget(self.tabs)
        # Remove addStretch() to keep the layout compact in fixed window

    def _add_shadow_effects(self):
        """Add shadow effects to the main window and key elements"""
        # Add shadow effect to the main window
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

    def _add_button_shadow(self, button):
        """Add enhanced shadow effect to buttons"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        button.setGraphicsEffect(shadow)

    def _add_card_shadow(self, card):
        """Add premium shadow effect to card containers"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 6)
        card.setGraphicsEffect(shadow)

    def _apply_dark_theme(self):
        """Apply a modern dark theme with gradients, shadows, and rounded corners"""
        self.setStyleSheet("""
            /* Main Window Styling */
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0e0e0e, stop:1 #1c1c1c);
                color: #ffffff;
                border: 1px solid #333;
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

            /* Section Title Labels */
            QLabel[accessibleName="section_title"] {
                color: #00d4ff;
                font-weight: 700;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1px;
                text-shadow: 0 1px 3px rgba(0, 212, 255, 0.3);
                margin-bottom: 8px;
            }

            /* Controller Info Labels */
            QLabel[accessibleName="controller_info"] {
                color: #e0e0e0;
                background: rgba(0, 212, 255, 0.05);
                border: 1px solid rgba(0, 212, 255, 0.15);
                border-radius: 8px;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9px;
                line-height: 1.4;
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
                    stop:0 rgba(25, 25, 28, 0.98), stop:1 rgba(15, 15, 18, 0.98));
                border: 1px solid rgba(0, 212, 255, 0.2);
                border-radius: 8px;
                margin-top: 4px;
                box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
            }

            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 45, 48, 0.92), stop:0.5 rgba(35, 35, 38, 0.92), stop:1 rgba(25, 25, 28, 0.92));
                color: #c0c0c0;
                border: 1px solid rgba(120, 120, 120, 0.18);
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 16px;
                margin-right: 2px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-weight: 600;
                font-size: 7px;
                min-width: 60px;
                max-width: 90px;
                text-transform: uppercase;
                letter-spacing: 0.6px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12),
                           inset 0 1px 0 rgba(255, 255, 255, 0.05);
                text-shadow: 0 1px 1px rgba(0, 0, 0, 0.3);
            }

            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00d4ff, stop:0.3 #00c4ef, stop:0.7 #00b3df, stop:1 #0099cc);
                color: #ffffff;
                border: 2px solid #00d4ff;
                font-weight: 800;
                box-shadow: 0 4px 12px rgba(0, 212, 255, 0.4),
                           0 1px 3px rgba(0, 0, 0, 0.3),
                           inset 0 1px 0 rgba(255, 255, 255, 0.15);
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.4);
                transform: translateY(-2px);
            }

            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 212, 255, 0.25), stop:0.5 rgba(0, 180, 230, 0.25), stop:1 rgba(0, 153, 204, 0.25));
                color: #ffffff;
                border: 2px solid rgba(0, 212, 255, 0.4);
                box-shadow: 0 2px 8px rgba(0, 212, 255, 0.2),
                           inset 0 1px 0 rgba(255, 255, 255, 0.08);
                transform: translateY(-1px);
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
            }

            /* Modern Buttons with Advanced Styling */
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:0.5 #3c7fc7, stop:1 #357abd);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 6px;
                padding: 8px 12px;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-weight: 600;
                font-size: 8px;
                min-height: 18px;
                max-height: 32px;
                text-align: center;
                letter-spacing: 0.4px;
                text-transform: uppercase;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1);
                text-shadow: 0 1px 1px rgba(0, 0, 0, 0.3);
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5aa3f0, stop:0.3 #4d96e8, stop:0.7 #4285d1, stop:1 #3976c2);
                border: 2px solid rgba(255, 255, 255, 0.25);
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(74, 144, 226, 0.3),
                           0 2px 6px rgba(0, 0, 0, 0.2),
                           inset 0 1px 0 rgba(255, 255, 255, 0.15);
                text-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
            }

            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2968a3, stop:0.5 #357abd, stop:1 #4a90e2);
                transform: translateY(1px);
                box-shadow: inset 0 3px 8px rgba(0, 0, 0, 0.4),
                           0 1px 3px rgba(0, 0, 0, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.08);
                text-shadow: 0 1px 1px rgba(0, 0, 0, 0.5);
            }

            QPushButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(60, 60, 63, 0.5), stop:1 rgba(45, 45, 48, 0.5));
                color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(100, 100, 100, 0.1);
            }

            /* Special Button Styles with Premium Effects */
            QPushButton[accessibleName="start"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4caf50, stop:0.3 #43a047, stop:0.7 #388e3c, stop:1 #2e7d32);
                box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            }

            QPushButton[accessibleName="start"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66bb6a, stop:0.3 #5cb35f, stop:0.7 #4caf50, stop:1 #43a047);
                box-shadow: 0 8px 24px rgba(76, 175, 80, 0.5),
                           0 2px 8px rgba(0, 0, 0, 0.3),
                           inset 0 1px 0 rgba(255, 255, 255, 0.15);
            }

            QPushButton[accessibleName="stop"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f44336, stop:0.3 #e53935, stop:0.7 #d32f2f, stop:1 #c62828);
                box-shadow: 0 4px 12px rgba(244, 67, 54, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            }

            QPushButton[accessibleName="stop"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ef5350, stop:0.3 #f44336, stop:0.7 #e53935, stop:1 #d32f2f);
                box-shadow: 0 8px 24px rgba(244, 67, 54, 0.5),
                           0 2px 8px rgba(0, 0, 0, 0.3),
                           inset 0 1px 0 rgba(255, 255, 255, 0.15);
            }

            QPushButton[accessibleName="pair"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ff9800, stop:0.3 #fb8c00, stop:0.7 #f57c00, stop:1 #ef6c00);
                box-shadow: 0 4px 12px rgba(255, 152, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            }

            QPushButton[accessibleName="pair"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffb74d, stop:0.3 #ffa726, stop:0.7 #ff9800, stop:1 #fb8c00);
                box-shadow: 0 8px 24px rgba(255, 152, 0, 0.5),
                           0 2px 8px rgba(0, 0, 0, 0.3),
                           inset 0 1px 0 rgba(255, 255, 255, 0.15);
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

            /* Test Button Styling */
            QPushButton[accessibleName="test"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(120, 120, 120, 0.6), stop:1 rgba(80, 80, 80, 0.6));
                color: #cccccc;
                border: 1px solid rgba(150, 150, 150, 0.3);
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 7px;
                min-height: 14px;
                max-height: 24px;
            }

            QPushButton[accessibleName="test"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(140, 140, 140, 0.7), stop:1 rgba(100, 100, 100, 0.7));
                color: #ffffff;
            }

            /* Premium TextEdit with Advanced Styling */
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(25, 25, 28, 0.98), stop:0.5 rgba(20, 20, 23, 0.98), stop:1 rgba(15, 15, 18, 0.98));
                color: #f0f0f0;
                border: 2px solid rgba(100, 100, 100, 0.2);
                border-radius: 14px;
                padding: 18px;
                selection-background-color: rgba(0, 212, 255, 0.35);
                font-family: 'Cascadia Code', 'Consolas', 'Fira Code', monospace;
                font-size: 10px;
                line-height: 1.5;
                box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.3),
                           0 1px 3px rgba(0, 0, 0, 0.2);
            }

            QTextEdit:focus {
                border: 2px solid #00d4ff;
                box-shadow: 0 0 16px rgba(0, 212, 255, 0.4),
                           inset 0 2px 6px rgba(0, 0, 0, 0.3),
                           0 2px 8px rgba(0, 0, 0, 0.3);
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 30, 33, 0.98), stop:0.5 rgba(25, 25, 28, 0.98), stop:1 rgba(20, 20, 23, 0.98));
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

            /* Premium Card Containers */
            QFrame[accessibleName="card"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 30, 33, 0.95), stop:0.5 rgba(25, 25, 28, 0.95), stop:1 rgba(20, 20, 23, 0.95));
                border: 1px solid rgba(0, 212, 255, 0.15);
                border-radius: 10px;
                margin: 3px;
                box-shadow: 0 3px 12px rgba(0, 0, 0, 0.25),
                           0 1px 3px rgba(0, 0, 0, 0.15),
                           inset 0 1px 0 rgba(255, 255, 255, 0.06);
            }

            /* Divider lines */
            QFrame[frameShape="4"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 212, 255, 0.0), stop:0.5 rgba(0, 212, 255, 0.4), stop:1 rgba(0, 212, 255, 0.0));
                border: none;
                max-height: 2px;
                margin: 10px 0px;
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
        # Update both the old status label (if it exists) and the new header
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Status: {message}")
        if hasattr(self, 'header_widget'):
            is_running = "running" in message.lower() or "active" in message.lower()
            self.header_widget.update_status(message, is_running)

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
        self.append_log(
            "[INFO] Attempting to auto-pair with a Bluetooth controller...")
        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:
            from utils.bluetooth_manager import BluetoothManager
            bt_manager = BluetoothManager()

            # Attempt auto pairing with DS4 controller
            if bt_manager.auto_pair_controller():
                self.append_log(
                    "[SUCCESS] Paired with a Bluetooth controller!")
                QMessageBox.information(self, "Pairing Successful",
                                        "A Bluetooth controller has been paired successfully.")
            else:
                self.append_log(
                    "[INFO] No available controllers found for pairing.")
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

        # Apply dark theme to message box with better text visibility
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2E2F30;
                color: #FFFFFF;
                font-size: 12px;
            }
            QMessageBox QLabel {
                color: #FFFFFF;
                background-color: transparent;
                font-size: 12px;
                font-weight: normal;
            }
            QMessageBox QPushButton {
                background-color: #4A4B4C;
                color: #FFFFFF;
                border: 1px solid #6A6B6C;
                padding: 8px 16px;
                min-width: 80px;
                font-weight: bold;
                border-radius: 4px;
            }
            QMessageBox QPushButton:hover {
                background-color: #6A6B6C;
                border: 1px solid #8A8B8C;
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

                # Start monitoring installation progress
                self._start_vigem_installation_monitoring(vigem_setup)

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
                # Use same dark theme
                follow_up.setStyleSheet(msg.styleSheet())
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
            # Refresh UI elements after calibration
            self._refresh_ui_after_calibration()
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
        # Check if controller is connected before testing drift detection
        if not self.app.ds4 or not self.app.ds4.is_connected():
            self.append_log(
                "[TEST] Cannot test drift detection: No controller connected")
            QMessageBox.warning(self, "No Controller",
                                "Please connect a controller first before testing drift detection.")
            return

        # Simulate drift detection for testing
        test_drift_info = {
            'has_drift': True,
            'drift_axes': ['Left X', 'Right Y'],
            'severity': 'moderate'
        }

        self.on_drift_detected(test_drift_info)
        self.append_log(
            "[TEST] Drift detection test triggered manually (controller is connected).")

    def _refresh_ui_after_calibration(self):
        """Refresh UI elements after calibration is completed"""
        # Clear any drift warnings since calibration should fix drift issues
        self.drift_detected = False
        self.drift_warning_label.setVisible(False)
        self._stop_calibration_button_blink()

        # Update controller widget to reflect new calibration
        if hasattr(self.controller_widget, 'update'):
            self.controller_widget.update()

        # Reset drift detection for fresh analysis with new calibration
        if self.app.translator:
            self.app.translator.drift_check_performed = False
            self.app.translator.drift_detected_axes.clear()
            for axis in self.app.translator.drift_samples:
                self.app.translator.drift_samples[axis].clear()
            self.app.translator.drift_sample_count = 0

        self.append_log(
            "[INFO] UI refreshed after calibration - drift detection reset.")

    def _start_vigem_installation_monitoring(self, vigem_setup):
        """Start monitoring ViGEmBus installation progress"""
        self.vigem_monitor_timer = QTimer()
        self.vigem_monitor_count = 0
        self.vigem_setup_instance = vigem_setup

        def check_installation():
            self.vigem_monitor_count += 1

            # Check every 5 seconds, up to 12 times (60 seconds total)
            if vigem_setup.is_vigem_installed(test_functionality=True):
                self.vigem_monitor_timer.stop()
                self.append_log(
                    "[SUCCESS] ViGEmBus installation completed and verified successfully!")
                self.append_log(
                    "[INFO] You can now start the LazyDS4 service.")
                return
            elif self.vigem_monitor_count >= 12:
                self.vigem_monitor_timer.stop()
                if vigem_setup.is_vigem_installed(test_functionality=False):
                    self.append_log(
                        "[INFO] ViGEmBus driver files detected - installation appears to be completed.")
                else:
                    self.append_log(
                        "[WARNING] Installation monitoring timeout. Please verify ViGEmBus was installed correctly.")
                return
            else:
                elapsed_time = self.vigem_monitor_count * 5
                self.append_log(
                    f"[INFO] Monitoring installation progress... ({elapsed_time}s elapsed)")

        self.vigem_monitor_timer.timeout.connect(check_installation)
        self.vigem_monitor_timer.start(5000)  # Check every 5 seconds
