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

# Importación de los widgets personalizados de la aplicación
from .battery_widget import BatteryWidget
from .calibration_dialog import CalibrationDialog
from .input_info_widget import InputInfoWidget
from .interactive_controller import InteractiveControllerWidget
from .modern_header import ModernHeaderWidget
from .pairing_dialog import PairingDialog


def resource_path(relative_path):
    """ Obtiene la ruta absoluta a un recurso, funciona para desarrollo y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class LogSignal(QObject):
    """Señal para enviar mensajes de log a la UI"""
    log_message = pyqtSignal(str)


class MainWindow(QMainWindow):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.setWindowTitle("LazyDS4 2.1")
        self.setGeometry(100, 100, 1080, 700)
        self.setFixedSize(1080, 680)  # Tamaño fijo para mantener el diseño
        self.setWindowIcon(QIcon(resource_path("assets/icon.png")))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        # Márgenes y espaciado mejorados para una apariencia más limpia
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)

        self._create_widgets()
        self._apply_dark_theme()

    def _create_widgets(self):
        """Crea todos los widgets de la UI"""
        self._add_shadow_effects()

        # Encabezado moderno
        self.header_widget = ModernHeaderWidget()
        self.layout.addWidget(self.header_widget)

        # Sistema de pestañas
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)  # Estilo de pestañas moderno

        # Pestaña "Controller"
        control_tab = QWidget()
        control_layout = QVBoxLayout(control_tab)
        control_layout.setContentsMargins(10, 15, 10, 15)
        control_layout.setSpacing(15)

        # Layout principal horizontal (control a la izquierda, info a la derecha)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)

        # Panel izquierdo: Visualización del control
        left_panel = QVBoxLayout()
        controller_card = QFrame()
        controller_card.setAccessibleName("card")
        controller_card_layout = QVBoxLayout(controller_card)
        controller_card_layout.setContentsMargins(10, 10, 10, 10)
        self.controller_widget = InteractiveControllerWidget()
        controller_card_layout.addWidget(self.controller_widget)
        self.controller_info_label = QLabel("No controller connected")
        self.controller_info_label.setAlignment(Qt.AlignCenter)
        self.controller_info_label.setAccessibleName("controller_info")
        controller_card_layout.addWidget(self.controller_info_label)
        left_panel.addWidget(controller_card)
        self._add_card_shadow(controller_card)
        main_layout.addLayout(left_panel, 2)  # Más espacio para el control

        # Panel derecho: Batería, inputs y botones
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        # Tarjeta de Batería
        battery_card = QFrame()
        battery_card.setAccessibleName("card")
        battery_card_layout = QVBoxLayout(battery_card)
        battery_card_layout.setContentsMargins(15, 10, 15, 10)
        battery_label = QLabel("Battery Status")
        battery_label.setAccessibleName("section_title")
        battery_label.setAlignment(Qt.AlignCenter)
        battery_card_layout.addWidget(battery_label)
        self.battery_widget = BatteryWidget()
        battery_card_layout.addWidget(self.battery_widget, 0, Qt.AlignCenter)
        right_panel.addWidget(battery_card)
        self._add_card_shadow(battery_card)

        # Tarjeta de Información de Inputs
        input_card = QFrame()
        input_card.setAccessibleName("card")
        input_card_layout = QVBoxLayout(input_card)
        input_card_layout.setContentsMargins(15, 10, 15, 10)
        input_label = QLabel("Controller Input Data")
        input_label.setAccessibleName("section_title")
        input_label.setAlignment(Qt.AlignCenter)
        input_card_layout.addWidget(input_label)
        self.input_info_widget = InputInfoWidget()
        input_card_layout.addWidget(self.input_info_widget)
        right_panel.addWidget(input_card)
        self._add_card_shadow(input_card)
        right_panel.addStretch()
        main_layout.addLayout(right_panel, 1)  # Menos espacio para la info

        control_layout.addLayout(main_layout)

        # Línea divisoria sutil
        div_line = QFrame()
        div_line.setFrameShape(QFrame.HLine)
        div_line.setFrameShadow(QFrame.Sunken)
        control_layout.addWidget(div_line)

        # Layout de botones de control
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.start_button = QPushButton(" Start Service")
        self.start_button.setIcon(
            QIcon(resource_path("assets/check-circle.svg")))
        self.start_button.setAccessibleName("start")
        self.start_button.clicked.connect(self._on_start_clicked)
        self._add_button_shadow(self.start_button)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton(" Stop Service")
        self.stop_button.setIcon(
            QIcon(resource_path("assets/alert-triangle.svg")))
        self.stop_button.setAccessibleName("stop")
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.stop_button.setEnabled(False)
        self._add_button_shadow(self.stop_button)
        button_layout.addWidget(self.stop_button)

        self.pair_button = QPushButton(" Pair Controller")
        self.pair_button.setIcon(QIcon(resource_path("assets/bluetooth.svg")))
        self.pair_button.setAccessibleName("pair")
        self.pair_button.clicked.connect(self._on_pair_clicked)
        self._add_button_shadow(self.pair_button)
        button_layout.addWidget(self.pair_button)

        self.calibrate_button = QPushButton(" Calibrate")
        self.calibrate_button.setIcon(
            QIcon(resource_path("assets/settings.svg")))
        self.calibrate_button.setAccessibleName("calibrate")
        self.calibrate_button.clicked.connect(self._on_calibrate_clicked)
        self.calibrate_button.setEnabled(False)
        self._add_button_shadow(self.calibrate_button)
        button_layout.addWidget(self.calibrate_button)
        control_layout.addLayout(button_layout)

        # Etiqueta de advertencia de drift (inicialmente oculta)
        self.drift_warning_label = QLabel(
            "⚠️ Stick drift detected! Calibration recommended.")
        self.drift_warning_label.setAlignment(Qt.AlignCenter)
        self.drift_warning_label.setVisible(False)
        self.drift_warning_label.setAccessibleName("drift_warning")
        control_layout.addWidget(self.drift_warning_label)

        self.drift_blink_timer = QTimer()
        self.drift_blink_timer.timeout.connect(self._blink_calibration_button)
        self.drift_blink_state = False
        self.drift_detected = False

        self.tabs.addTab(control_tab, "Controller")
        self.tabs.setTabIcon(0, QIcon(resource_path("assets/refresh-ccw.svg")))

        # Pestaña "Log"
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        log_layout.addWidget(self.log_output)
        self.tabs.addTab(log_tab, "Log")
        self.tabs.setTabIcon(1, QIcon(resource_path("assets/bar-chart.svg")))

        # Pestaña "Info"
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setHtml("""
            <h3>LazyDS4</h3>
            <p>Application developed by Iván Eduardo Chavez Ayub. @Ivan-Ayub97 on GitHub.</p>
            <p><b>License:</b> MIT License.</p>
            <hr>
            <h4>Features</h4>
            <ul>
                <li><b>Supported Controllers:</b> DualShock 4 (v1 & v2)</li>
                <li><b>Virtual Controller:</b> Xbox 360 (XInput)</li>
                <li><b>Connection:</b> USB or Bluetooth</li>
                <li><b>Polling Rate:</b> ~1ms (1000Hz)</li>
            </ul>
        """)
        settings_layout.addWidget(info_text)
        self.reinstall_button = QPushButton(" Reinstall ViGEmBus Driver")
        self.reinstall_button.setIcon(
            QIcon(resource_path("assets/shield.svg")))
        self.reinstall_button.setAccessibleName("reinstall")
        self.reinstall_button.clicked.connect(self._on_reinstall_vigem)
        self._add_button_shadow(self.reinstall_button)
        settings_layout.addWidget(self.reinstall_button)
        self.tabs.addTab(settings_tab, "Info")
        self.tabs.setTabIcon(2, QIcon(resource_path("assets/settings.svg")))

        self.layout.addWidget(self.tabs)

    def _add_shadow_effects(self):
        """Añade efectos de sombra a elementos clave para darles profundidad."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 90))
        shadow.setOffset(0, 5)
        self.central_widget.setGraphicsEffect(shadow)

    def _add_button_shadow(self, button):
        shadow = QGraphicsDropShadowEffect(button)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        button.setGraphicsEffect(shadow)

    def _add_card_shadow(self, card):
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 6)
        card.setGraphicsEffect(shadow)

    def _apply_dark_theme(self):
        """Aplica el tema oscuro mejorado con tipografía y estilos refinados."""
        self.setStyleSheet("""
            QMainWindow {
                background: #1e1e1e;
            }
            QWidget {
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            /* Títulos de sección */
            QLabel[accessibleName="section_title"] {
                color: #00d4ff;
                font-weight: 700;
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 8px;
            }

            /* Etiqueta de información del control */
            QLabel[accessibleName="controller_info"] {
                color: #cccccc;
                background: rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                line-height: 1.5;
            }

            /* Etiqueta de advertencia de Drift */
            QLabel[accessibleName="drift_warning"] {
                background: rgba(255, 152, 0, 0.15);
                border: 1px solid #ff9800;
                border-radius: 8px;
                padding: 8px;
                color: #ff9800;
                font-weight: 600;
                font-size: 12px;
                margin-top: 5px;
            }

            /* Estilo de las pestañas */
            QTabWidget::pane {
                background: #2a2a2e;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                margin-top: -1px;
            }
            QTabBar::tab {
                background: #2a2a2e;
                color: #c0c0c0;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #0078d4;
                color: white;
                border-bottom: 2px solid #00d4ff;
            }
            QTabBar::tab:hover:!selected {
                background: #3a3a3e;
            }

            /* Estilo de los botones */
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 18px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #3f3f3f;
                color: #888888;
            }
            QPushButton[accessibleName="start"] { background-color: #4CAF50; }
            QPushButton[accessibleName="start"]:hover { background-color: #5cb85c; }
            QPushButton[accessibleName="stop"] { background-color: #f44336; }
            QPushButton[accessibleName="stop"]:hover { background-color: #e53935; }
            QPushButton[accessibleName="pair"] { background-color: #ff9800; }
            QPushButton[accessibleName="pair"]:hover { background-color: #fb8c00; }
            QPushButton[accessibleName="calibrate"] { background-color: #607d8b; }
            QPushButton[accessibleName="calibrate"]:hover { background-color: #78909c; }
            QPushButton[accessibleName="reinstall"] { background-color: #9c27b0; }
            QPushButton[accessibleName="reinstall"]:hover { background-color: #ab47bc; }

            /* Estilo de los campos de texto */
            QTextEdit {
                background: #2a2a2e;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                font-family: 'Consolas', monospace;
            }

            /* Estilo de las tarjetas (contenedores) */
            QFrame[accessibleName="card"] {
                background: #2a2a2e;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
            }

            /* Líneas divisorias */
            QFrame[frameShape="4"] {
                border: none;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                margin: 5px 0px;
            }
        """)

    def _on_start_clicked(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.app.start()

    def _on_stop_clicked(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.app.stop()

    def update_status(self, message):
        is_running = "running" in message.lower(
        ) or "active" in message.lower() or "connected" in message.lower()
        self.header_widget.update_status(message, is_running)

    def append_log(self, message):
        self.log_output.append(message)

    def update_controller_info(self, info_dict):
        if info_dict:
            connection_type = info_dict.get('connection_type', 'Unknown')
            vendor_id = info_dict.get('vendor_id', 'Unknown')
            product_id = info_dict.get('product_id', 'Unknown')
            serial = info_dict.get('serial_number', 'Unknown')
            info_text = f"TYPE: {connection_type}\nVID: {vendor_id} | PID: {product_id}\nSERIAL: {serial}"
            self.controller_info_label.setText(info_text)
            self.calibrate_button.setEnabled(True)
            self.controller_connected.emit(True)
        else:
            self.controller_info_label.setText("No controller connected")
            self.calibrate_button.setEnabled(False)
            self.controller_connected.emit(False)

    def update_battery_status(self, level, is_charging):
        self.battery_widget.update_battery_status(
            level, is_charging, is_connected=True)

    def on_controller_disconnected(self):
        self.battery_widget.update_battery_status(0, False, is_connected=False)
        self.calibrate_button.setEnabled(False)
        self.controller_info_label.setText("No controller connected")

    def show_battery_warning(self, level):
        QMessageBox.warning(self, "Low Battery",
                            f"Controller battery is low: {level}%")

    def closeEvent(self, event):
        self.app.stop()
        event.accept()

    def _on_pair_clicked(self):
        self.append_log("[INFO] Opening Bluetooth pairing dialog...")
        try:
            from utils.bluetooth_manager import BluetoothManager
            bt_manager = BluetoothManager()
            devices = bt_manager.discover_devices()
            dialog = PairingDialog(devices, self)
            dialog.pair_device_requested.connect(
                self._on_pair_device_requested)
            dialog.exec_()
        except Exception as e:
            self.append_log(f"[ERROR] Failed to open pairing dialog: {e}")

    def _on_reinstall_vigem(self):
        reply = QMessageBox.information(self, "ViGEmBus Installation",
                                        "This will launch the ViGEmBus installer. Administrator privileges are required. Continue?",
                                        QMessageBox.Ok | QMessageBox.Cancel)
        if reply == QMessageBox.Ok:
            self.append_log("[INFO] Starting ViGEmBus driver installation...")
            try:
                from utils.vigem_setup import ViGEmSetup
                vigem_setup = ViGEmSetup()
                if self.app.running.is_set():
                    self.app.stop()
                success = vigem_setup.install_vigem(silent=False)
                if success:
                    QMessageBox.information(
                        self, "Installer Launched", "Please complete the installation process.")
                else:
                    QMessageBox.critical(
                        self, "Installation Failed", "Failed to launch the ViGEmBus installer.")
            except Exception as e:
                self.append_log(f"[ERROR] ViGEmBus installation error: {e}")

    def _on_pair_device_requested(self, device_address):
        self.append_log(
            f"[INFO] Attempting to pair with device: {device_address}")
        try:
            from utils.bluetooth_manager import BluetoothManager
            bt_manager = BluetoothManager()
            if bt_manager.pair_device(device_address):
                QMessageBox.information(
                    self, "Pairing Initiated", "Windows Bluetooth settings opened. Please complete pairing there.")
            else:
                QMessageBox.warning(self, "Pairing Failed",
                                    "Could not open Bluetooth settings.")
        except Exception as e:
            self.append_log(f"[ERROR] Failed to initiate pairing: {e}")

    def _on_calibrate_clicked(self):
        if not self.app.translator:
            QMessageBox.warning(self, "No Controller",
                                "Please connect a controller first.")
            return
        self.append_log("[INFO] Starting controller calibration...")
        dialog = CalibrationDialog(self)
        dialog.calibration_requested.connect(
            self.app.translator.start_calibration)
        dialog.calibration_completed.connect(
            self.app.translator.stop_calibration)
        self.app.translator.calibration_updated.connect(
            dialog.update_calibration_data)
        self.app.translator.calibration_finished.connect(
            dialog.update_calibration_data)
        self.app.translator.joystick_data_updated.connect(
            dialog.controller_viz.update_joystick_data)
        if dialog.exec_() == QDialog.Accepted:
            self.append_log(
                "[SUCCESS] Controller calibration completed and applied.")
        else:
            self.append_log("[INFO] Controller calibration cancelled.")

    def on_drift_detected(self, drift_info):
        has_drift = drift_info.get('has_drift', False)
        if has_drift:
            self.drift_detected = True
            axes_text = ', '.join(drift_info.get('drift_axes', []))
            self.drift_warning_label.setText(
                f"⚠️ Stick drift detected on {axes_text}! Calibration recommended.")
            self.drift_warning_label.setVisible(True)
            self._start_calibration_button_blink()
        else:
            self.drift_detected = False
            self.drift_warning_label.setVisible(False)
            self._stop_calibration_button_blink()

    def _start_calibration_button_blink(self):
        if not self.drift_blink_timer.isActive():
            self.drift_blink_timer.start(800)

    def _stop_calibration_button_blink(self):
        if self.drift_blink_timer.isActive():
            self.drift_blink_timer.stop()
            self._reset_calibration_button_style()

    def _blink_calibration_button(self):
        if not self.calibrate_button.isEnabled():
            self._stop_calibration_button_blink()
            return
        self.drift_blink_state = not self.drift_blink_state
        if self.drift_blink_state:
            self.calibrate_button.setStyleSheet(
                "QPushButton[accessibleName=\"calibrate\"] { background-color: #ff9800; }")
        else:
            self._reset_calibration_button_style()

    def _reset_calibration_button_style(self):
        self.calibrate_button.setStyleSheet(
            "QPushButton[accessibleName=\"calibrate\"] { background-color: #607d8b; }")
