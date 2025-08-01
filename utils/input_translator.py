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
    joystick_data_updated = pyqtSignal(dict) # For real-time joystick visualization
    drift_detected = pyqtSignal(dict) # Signal when drift is detected: {'has_drift': bool, 'drift_axes': list}

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
        
        # Drift detection system
        self.drift_detection_enabled = True
        self.drift_sample_count = 0
        self.drift_samples = {
            'lx': [],
            'ly': [],
            'rx': [],
            'ry': []
        }
        self.drift_detected_axes = set()
        self.last_drift_check = 0
        self.drift_check_performed = False

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
        
        # Emit real-time joystick data for visualization
        joystick_data = {'lx': lx, 'ly': ly, 'rx': rx, 'ry': ry}
        self.joystick_data_updated.emit(joystick_data)
        
        # Check for drift during normal operation (not calibration)
        if not self.is_calibrating:
            self._check_for_drift(hid_report)

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
        
        # Check for drift (only if not already performed)
        if self.drift_detection_enabled and not self.drift_check_performed:
            self._check_for_drift(hid_report)
            
        return self.xinput_report

    def _normalize_stick(self, value, axis, invert=False):
        """Complex calibration to mitigate joystick drift and provide smooth movement"""
        calib = self.calibration_data[axis]
        center = calib.get('center', 128)
        min_val = calib.get('min', 0)
        max_val = calib.get('max', 255)

        # Use the calibrated center, min, and max to create a dynamic range
        neg_range = center - min_val
        pos_range = max_val - center

        # Avoid division by zero
        neg_range = max(neg_range, 1)
        pos_range = max(pos_range, 1)

        # Normalize to a 16-bit signed integer range
        if value > center:
            scaled = ((value - center) / pos_range) * 32767
        elif value < center:
            scaled = ((value - center) / neg_range) * 32767
        else:
            scaled = 0

        # Implement adaptive deadzone to smooth out drift
        adaptive_deadzone = max(4000, 2000 * (abs(value - center) / max(neg_range, pos_range)))
        if abs(scaled) < adaptive_deadzone:
            scaled = 0

        # Clamp to the 16-bit integer
        final_value = int(max(-32767, min(32767, scaled)))

        return -final_value if invert else final_value

    def draw_joystick(self, painter, joystick_pos, radius=50):
        """Draw a simple representation of a joystick in a given position."""
        painter.save()

        # Set pen and brush
        pen = QPen(QColor(70, 70, 70), 2)
        brush = QBrush(QColor(180, 180, 180))
        painter.setPen(pen)
        painter.setBrush(brush)

        # Calculate center of joystick
        center_x = joystick_pos.x() + radius
        center_y = joystick_pos.y() + radius

        # Draw outer circle for base
        painter.drawEllipse(QPoint(center_x, center_y), radius, radius)

        # Draw inner circle for stick
        stick_radius = max(5, radius // 5)
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.drawEllipse(QPoint(center_x, center_y), stick_radius, stick_radius)

        painter.restore()
    
    def draw_virtual_controller(self, painter, joystick_positions):
        """Draw the virtual controller on the widget."""
        # Left joystick
        self.draw_joystick(painter, joystick_positions['left'], radius=50)

        # Right joystick
        self.draw_joystick(painter, joystick_positions['right'], radius=50)

    
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
    
    def _check_for_drift(self, hid_report):
        """Robust drift detection system that samples stick positions when idle"""
        if not hid_report or len(hid_report) < 5:
            return
            
        current_time = time.time()
        
        # Only check for drift every 0.1 seconds to avoid overwhelming
        if current_time - self.last_drift_check < 0.1:
            return
            
        self.last_drift_check = current_time
        
        # Extract stick values
        lx, ly, rx, ry = hid_report[1], hid_report[2], hid_report[3], hid_report[4]
        current_values = {'lx': lx, 'ly': ly, 'rx': rx, 'ry': ry}
        
        # Check if any buttons are pressed (if so, user is active, skip drift detection)
        buttons_pressed = hid_report[5] != 0 or hid_report[6] != 0
        triggers_pressed = hid_report[8] > 10 or hid_report[9] > 10  # Small threshold for triggers
        
        if buttons_pressed or triggers_pressed:
            # User is active, reset sampling
            self.drift_sample_count = 0
            for axis in self.drift_samples:
                self.drift_samples[axis].clear()
            return
            
        # Collect samples when controller appears idle
        for axis, value in current_values.items():
            self.drift_samples[axis].append(value)
            
        self.drift_sample_count += 1
        
        # After collecting enough samples (3 seconds at ~10Hz = 30 samples), analyze for drift
        if self.drift_sample_count >= 30:
            self._analyze_drift_samples()
            self.drift_check_performed = True
            
    def _analyze_drift_samples(self):
        """Analyze collected samples to determine if drift exists"""
        drift_axes = []
        axis_names = {'lx': 'Left X', 'ly': 'Left Y', 'rx': 'Right X', 'ry': 'Right Y'}
        
        for axis, samples in self.drift_samples.items():
            if len(samples) < 10:  # Need minimum samples
                continue
                
            # Calculate statistics
            avg_value = sum(samples) / len(samples)
            min_value = min(samples)
            max_value = max(samples)
            range_value = max_value - min_value
            
            # Expected center value for DS4 sticks
            expected_center = 128
            
            # Drift detection criteria:
            # 1. Average value significantly off from center (more than 8 units)
            # 2. OR consistent deviation in one direction
            # 3. AND the range is small (indicating consistent offset, not just noise)
            
            center_deviation = abs(avg_value - expected_center)
            is_consistently_off = center_deviation > 8  # More than ~3% off center
            is_stable = range_value < 6  # Values don't vary much (stable drift)
            
            # Additional check: ensure most samples are on the same side of center
            samples_above_center = sum(1 for s in samples if s > expected_center)
            samples_below_center = sum(1 for s in samples if s < expected_center)
            is_consistent_direction = max(samples_above_center, samples_below_center) > len(samples) * 0.8
            
            # Detect drift if consistently off-center and stable
            if is_consistently_off and (is_stable or is_consistent_direction):
                drift_axes.append(axis_names[axis])
                self.drift_detected_axes.add(axis)
                
        # Emit drift detection signal
        has_drift = len(drift_axes) > 0
        drift_info = {
            'has_drift': has_drift,
            'drift_axes': drift_axes,
            'severity': self._calculate_drift_severity() if has_drift else 'none'
        }
        
        self.drift_detected.emit(drift_info)
        
        # Clear samples after analysis
        for axis in self.drift_samples:
            self.drift_samples[axis].clear()
        self.drift_sample_count = 0
        
    def _calculate_drift_severity(self):
        """Calculate overall drift severity"""
        if len(self.drift_detected_axes) == 0:
            return 'none'
        elif len(self.drift_detected_axes) == 1:
            return 'mild'
        elif len(self.drift_detected_axes) == 2:
            return 'moderate'
        else:
            return 'severe'
