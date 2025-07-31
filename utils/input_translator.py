import time
import math
from PyQt5.QtCore import QObject, pyqtSignal
from utils.settings import SettingsManager

class XInputReport:
    """Simple XInput report structure for vgamepad compatibility"""
    def __init__(self):
        self.wButtons = 0
        self.bLeftTrigger = 0
        self.bRightTrigger = 0
        self.sThumbLX = 0
        self.sThumbLY = 0
        self.sThumbRX = 0
        self.sThumbRY = 0

class InputTranslator(QObject):
    """Translates DS4 HID reports to XInput reports and extracts battery status"""
    
    battery_status_updated = pyqtSignal(int, bool)  # level, is_charging
    calibration_started = pyqtSignal()
    calibration_finished = pyqtSignal(dict)
    calibration_updated = pyqtSignal(dict) # For real-time UI updates

    def __init__(self):
        super().__init__()
        self.xinput_report = XInputReport()
        self.last_battery_check = 0
        
        self.is_calibrating = False
        self.calibration_data = {
            'lx': {'min': 255, 'max': 0, 'center': 128},
            'ly': {'min': 255, 'max': 0, 'center': 128},
            'rx': {'min': 255, 'max': 0, 'center': 128},
            'ry': {'min': 255, 'max': 0, 'center': 128}
        }
        self.deadzone = {
            'lx': 3000,
            'ly': 3000,
            'rx': 3000,
            'ry': 3000
        }

    def start_calibration(self):
        """Starts the stick calibration process"""
        self.is_calibrating = True
        self.calibration_data = {
            'lx': {'min': 255, 'max': 0, 'center': 128},
            'ly': {'min': 255, 'max': 0, 'center': 128},
            'rx': {'min': 255, 'max': 0, 'center': 128},
            'ry': {'min': 255, 'max': 0, 'center': 128}
        }
        # A small delay to ensure the stick is centered before calibration starts
        time.sleep(0.5) 
        self.calibration_started.emit()

    def stop_calibration(self):
        """Stops the stick calibration."""
        self.is_calibrating = False
        
        # Center is assumed to be 128. We don't calculate it from min/max
        # to prevent incorrect center points from causing drift.
        self.calibration_finished.emit(self.calibration_data)
        
    def calibrate(self, hid_report):
        """Records min/max values for sticks and updates UI in real-time."""
        if not hid_report or len(hid_report) < 5:
            return

        lx, ly, rx, ry = hid_report[1], hid_report[2], hid_report[3], hid_report[4]

        self.calibration_data['lx']['min'] = min(self.calibration_data['lx']['min'], lx)
        self.calibration_data['lx']['max'] = max(self.calibration_data['lx']['max'], lx)
        
        self.calibration_data['ly']['min'] = min(self.calibration_data['ly']['min'], ly)
        self.calibration_data['ly']['max'] = max(self.calibration_data['ly']['max'], ly)

        self.calibration_data['rx']['min'] = min(self.calibration_data['rx']['min'], rx)
        self.calibration_data['rx']['max'] = max(self.calibration_data['rx']['max'], rx)

        self.calibration_data['ry']['min'] = min(self.calibration_data['ry']['min'], ry)
        self.calibration_data['ry']['max'] = max(self.calibration_data['ry']['max'], ry)
        
        # Emit signal for real-time UI update
        self.calibration_updated.emit(self.calibration_data)

    def translate(self, hid_report):
        """Translate a single HID report to an XInput report and extract battery"""
        if not hid_report or len(hid_report) < 32:
            return self.xinput_report

        if self.is_calibrating:
            self.calibrate(hid_report)
            return None # No report sent during calibration
            
        # Process battery status (every 2 seconds for more responsive updates)
        current_time = time.time()
        if current_time - self.last_battery_check > 2:
            self.last_battery_check = current_time
            self._extract_battery_info(hid_report)

        # Reset buttons to avoid sticky inputs
        self.xinput_report.wButtons = 0
        
        # Analog Sticks (Left X, Left Y, Right X, Right Y)
        self.xinput_report.sThumbLX = self._normalize_stick(hid_report[1], 'lx')
        self.xinput_report.sThumbLY = self._normalize_stick(hid_report[2], 'ly', invert=True)
        self.xinput_report.sThumbRX = self._normalize_stick(hid_report[3], 'rx')
        self.xinput_report.sThumbRY = self._normalize_stick(hid_report[4], 'ry', invert=True)
        
        # Buttons (Byte 5, 6, 7)
        buttons = hid_report[5]
        
        # D-pad
        dpad = buttons & 0x0F
        if dpad == 0 or dpad == 1 or dpad == 7: self.xinput_report.wButtons |= 0x0001  # DPAD_UP
        if dpad == 1 or dpad == 2 or dpad == 3: self.xinput_report.wButtons |= 0x0008  # DPAD_RIGHT
        if dpad == 3 or dpad == 4 or dpad == 5: self.xinput_report.wButtons |= 0x0002  # DPAD_DOWN
        if dpad == 5 or dpad == 6 or dpad == 7: self.xinput_report.wButtons |= 0x0004  # DPAD_LEFT
            
        # Face buttons
        if buttons & 0x10: self.xinput_report.wButtons |= 0x4000  # X (Square)
        if buttons & 0x20: self.xinput_report.wButtons |= 0x1000  # A (Cross)
        if buttons & 0x40: self.xinput_report.wButtons |= 0x2000  # B (Circle)
        if buttons & 0x80: self.xinput_report.wButtons |= 0x8000  # Y (Triangle)
            
        # Shoulder buttons
        misc_buttons = hid_report[6]
        if misc_buttons & 0x01: self.xinput_report.wButtons |= 0x0100  # LEFT_SHOULDER
        if misc_buttons & 0x02: self.xinput_report.wButtons |= 0x0200  # RIGHT_SHOULDER
            
        # Triggers
        self.xinput_report.bLeftTrigger = hid_report[8]
        self.xinput_report.bRightTrigger = hid_report[9]
        
        # Special buttons
        if misc_buttons & 0x10: self.xinput_report.wButtons |= 0x0020  # BACK (Share)
        if misc_buttons & 0x20: self.xinput_report.wButtons |= 0x0010  # START (Options)
        if misc_buttons & 0x40: self.xinput_report.wButtons |= 0x0040  # LEFT_THUMB
        if misc_buttons & 0x80: self.xinput_report.wButtons |= 0x0080  # RIGHT_THUMB
            
        return self.xinput_report

    def _normalize_stick(self, value, axis, invert=False):
        """Convert 8-bit stick value to 16-bit signed with calibration"""
        calib = self.calibration_data[axis]
        center = 128  # Use a fixed, theoretical center
        min_val = calib.get('min', 0)
        max_val = calib.get('max', 255)

        # Define the negative and positive range from the center
        neg_range = center - min_val
        pos_range = max_val - center

        # Avoid division by zero if calibration data is incomplete
        if neg_range == 0:
            neg_range = 128
        if pos_range == 0:
            pos_range = 127
            
        scaled = 0
        if value > center:
            scaled = ((value - center) / pos_range) * 32767.0
        elif value < center:
            # Note: value - center is negative, so the result is negative
            scaled = ((value - center) / neg_range) * 32768.0
        
        # Apply a fixed deadzone to the scaled value
        deadzone = 4000  # A reasonable deadzone for most controllers
        if abs(scaled) < deadzone:
            scaled = 0
        
        # Clamp the values to the 16-bit signed integer range
        final_value = int(max(-32767, min(32767, scaled)))
        
        if invert:
            return -final_value
        
        return final_value
    
    def _extract_battery_info(self, hid_report):
        """Extract battery information from DS4 HID report"""
        try:
            # DS4 battery info is typically at different positions depending on connection type
            # For USB connection, check byte 30; for Bluetooth, might be different
            if len(hid_report) >= 31:
                # Try USB format first (most common)
                battery_byte = hid_report[30]
                
                # Check if this looks like valid battery data
                if battery_byte != 0:
                    # Charging status is in bit 4 (0x10)
                    is_charging = bool(battery_byte & 0x10)
                    
                    # Battery level is in lower 4 bits (0x0F)
                    level_raw = battery_byte & 0x0F
                    
                    # Convert raw level to percentage
                    # DS4 reports battery in steps of 0-10, convert to 0-100%
                    if level_raw <= 10:
                        level_percent = max(0, min(100, int(level_raw * 10)))
                    else:
                        # Fallback: treat as direct percentage if > 10
                        level_percent = max(0, min(100, level_raw))
                    
                    self.battery_status_updated.emit(level_percent, is_charging)
                    return
            
            # Try alternate positions for Bluetooth connection
            if len(hid_report) >= 13:
                battery_byte = hid_report[12]
                if battery_byte != 0:
                    # Simple conversion for alternate format
                    level_percent = max(0, min(100, battery_byte))
                    is_charging = False  # Assume not charging if using alternate format
                    self.battery_status_updated.emit(level_percent, is_charging)
                    return
            
            # If no valid battery data found, emit default values
            self.battery_status_updated.emit(50, False)  # Default to 50% unknown status
            
        except (IndexError, ValueError) as e:
            # On error, emit safe default values
            self.battery_status_updated.emit(0, False)
