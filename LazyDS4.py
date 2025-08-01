#!/usr/bin/env python3
"""
LazyDS4 - A direct DualShock 4 to XInput mapper
Translates HID input from a DualShock 4 controller to a virtual Xbox 360 controller
"""

from utils.input_translator import InputTranslator
from ui.main_window import LogSignal, MainWindow
from core.vigem_controller import ViGEmController
from core.ds4_controller import DS4Controller
import logging
import os
import sys
import threading
import time

# Configure logging
log_format = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)

# For gracefully handling Qt imports
try:
    from PyQt5.QtCore import QObject, QTimer, pyqtSignal
    from PyQt5.QtWidgets import QApplication
except ImportError:
    logging.error("PyQt5 not found. Please install it with: pip install PyQt5")
    sys.exit(1)


# Configuration
VENDOR_ID = 0x054C
PRODUCT_ID_DS4_V1 = 0x05C4
PRODUCT_ID_DS4_V2 = 0x09CC


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class LazyDS4(QObject):
    """Main application logic, designed to run with a GUI"""
    status_updated = pyqtSignal(str)
    log_updated = pyqtSignal(str)
    controller_connected = pyqtSignal(bool)
    controller_info_updated = pyqtSignal(dict)
    input_received = pyqtSignal(object)
    battery_status_updated = pyqtSignal(int, bool)  # level, is_charging
    drift_detected = pyqtSignal(dict)  # Relay drift detection signal

    def __init__(self):
        super().__init__()
        self.ds4 = None
        self.vigem = None
        self.translator = None
        self.running = threading.Event()  # Use threading.Event for safer thread control
        self.thread = None

    def start(self):
        """Starts the controller detection and input loop in a background thread."""
        if not self.running.is_set():
            self.running.set()  # Set the event to True
            self.thread = threading.Thread(
                target=self._run_loop, daemon=True)  # Run as daemon
            self.thread.start()
            self.status_updated.emit(
                "Service Started. Searching for controller...")
            self.log_updated.emit("LazyDS4 service started.")

    def stop(self):
        """Stops the service and cleans up resources."""
        if self.running.is_set():
            self.running.clear()  # Clear the event to signal the thread to stop
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=2)  # Wait for the thread to finish
            self._disconnect_controller()
            self.status_updated.emit("Service Stopped")
            self.log_updated.emit("LazyDS4 service stopped.")

    def _run_loop(self):
        """Main application loop for controller management."""
        while self.running.is_set():
            try:
                if self.ds4 is None or not self.ds4.is_connected():
                    if self.ds4:
                        self._disconnect_controller()
                    self._connect_controller()
                else:
                    self._process_input()
            except ConnectionError as e:
                self.log_updated.emit(f"[ERROR] Connection lost: {e}")
                self._disconnect_controller()
                time.sleep(3)  # Wait before trying to reconnect
            except Exception as e:
                logging.error(f"Unhandled error in main loop: {e}")
                self.log_updated.emit(
                    f"[CRITICAL] An unexpected error occurred: {e}")
                self._disconnect_controller()
                time.sleep(5)  # Wait longer after critical errors

            # Optimized polling rate (2ms) to balance performance and CPU usage
            time.sleep(0.002)

    def _connect_controller(self):
        """Attempt to connect to DS4 and ViGEm"""
        try:
            self.ds4 = DS4Controller(vendor_id=VENDOR_ID, product_ids=[
                                     PRODUCT_ID_DS4_V1, PRODUCT_ID_DS4_V2])
            if self.ds4.is_connected():
                self.vigem = ViGEmController()
                self.translator = InputTranslator()
                self.status_updated.emit(
                    "DS4 Connected - Virtual Xbox controller active")
                self.log_updated.emit(
                    f"Controller: {self.ds4.connection_type}")
                self.controller_connected.emit(True)
                self.controller_info_updated.emit(self.ds4.get_device_info())
                self.translator.battery_status_updated.connect(
                    self.battery_status_updated)
                # Connect drift detection signal
                self.translator.drift_detected.connect(self._on_drift_detected)
        except Exception as e:
            self.log_updated.emit(f"Controller search failed: {e}")
            time.sleep(5)  # Wait before retrying

    def _disconnect_controller(self):
        """Disconnect all controllers"""
        if self.vigem:
            self.vigem.close()
            self.vigem = None
        if self.ds4:
            self.ds4.close()
            self.ds4 = None
        self.translator = None
        self.status_updated.emit("Controller Disconnected")
        self.log_updated.emit("Controllers disconnected.")
        self.controller_connected.emit(False)

    def _process_input(self):
        """Read, translate, and send controller input"""
        try:
            hid_report = self.ds4.read_input()
            if hid_report:
                xinput_report = self.translator.translate(hid_report)
                # Don't send reports during calibration (translator returns None)
                if xinput_report is not None:
                    self.vigem.send_report(xinput_report)
                    self.input_received.emit(xinput_report)
        except Exception as e:
            self.log_updated.emit(f"[ERROR] Input processing error: {e}")
            # Propagate as a connection error
            raise ConnectionError("Failed to process controller input.")
    
    def _on_drift_detected(self, drift_info):
        """Relay drift detection signal from translator to main window"""
        self.drift_detected.emit(drift_info)


def main():
    """Main entry point for the GUI application"""
    app = QApplication(sys.argv)

    # Create main app logic instance
    lazy_ds4_app = LazyDS4()

    # Create the main window
    main_win = MainWindow(lazy_ds4_app)

    # Connect signals from app logic to UI
    lazy_ds4_app.status_updated.connect(main_win.update_status)
    lazy_ds4_app.log_updated.connect(main_win.append_log)
    lazy_ds4_app.controller_connected.connect(
        main_win.controller_widget.update_connection_status)
    lazy_ds4_app.input_received.connect(
        main_win.controller_widget.update_inputs)
    lazy_ds4_app.input_received.connect(
        main_win.input_info_widget.update_inputs)
    lazy_ds4_app.controller_info_updated.connect(
        main_win.update_controller_info)

    # Handle controller disconnection for battery widget
    lazy_ds4_app.controller_connected.connect(
        lambda connected: main_win.on_controller_disconnected() if not connected else None)

    # Connect battery signals
    lazy_ds4_app.battery_status_updated.connect(main_win.update_battery_status)
    main_win.battery_widget.battery_low_warning.connect(
        main_win.show_battery_warning)
    
    # Connect drift detection signal
    lazy_ds4_app.drift_detected.connect(main_win.on_drift_detected)

    # Show the window and run the app
    main_win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
