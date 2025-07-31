import hid
import logging
import time
import threading

class DS4Controller:
    """Optimized DS4 controller with support for USB and Bluetooth"""
    
    # DS4 controller identifiers for different connection types
    DS4_DEVICES = [
        # DualShock 4 v1 (CUH-ZCT1)
        {'vid': 0x054C, 'pid': 0x05C4, 'name': 'DS4 v1 (USB)'},
        # DualShock 4 v2 (CUH-ZCT2)
        {'vid': 0x054C, 'pid': 0x09CC, 'name': 'DS4 v2 (USB)'},
        # DualShock 4 Wireless Adapter
        {'vid': 0x054C, 'pid': 0x0BA0, 'name': 'DS4 Wireless Adapter'},
        # DualShock 4 Bluetooth (appears as audio device)
        {'vid': 0x054C, 'pid': 0x05C4, 'name': 'DS4 v1 (Bluetooth)'},
        {'vid': 0x054C, 'pid': 0x09CC, 'name': 'DS4 v2 (Bluetooth)'},
    ]
    
    # Connection retry settings
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY = 1.0  # seconds
    
    def __init__(self, vendor_id, product_ids):
        self.vendor_id = vendor_id
        self.product_ids = product_ids
        self.device = None
        self.connection_type = None
        self.device_info = None
        self.last_report_time = 0
        self._connect()

    def _connect(self):
        """Enhanced connection logic for USB and Bluetooth with retries"""
        logging.info("Scanning for DS4 controllers...")
        
        for attempt in range(self.MAX_RETRY_ATTEMPTS):
            # Get all available HID devices
            available_devices = hid.enumerate()
            sony_devices = [dev for dev in available_devices if dev['vendor_id'] == self.vendor_id]
            
            if not sony_devices:
                logging.warning(f"No Sony devices found (attempt {attempt + 1})")
                time.sleep(self.RETRY_DELAY)
                continue
            
            logging.info(f"Found {len(sony_devices)} Sony device(s)")
            
            # Try to connect to each potential DS4 device
            for device_info in sony_devices:
                pid = device_info['product_id']
                if pid in self.product_ids:
                    try:
                        self.device = hid.device()
                        self.device.open(device_info['vendor_id'], device_info['product_id'])
                        self.device.set_nonblocking(1)
                        
                        self.device_info = device_info
                        self.connection_type = self._detect_connection_type(device_info)
                        
                        # Test if we can read from the device
                        test_read = self.device.read(64, timeout_ms=100)
                        
                        logging.info(f"Successfully connected to {self.connection_type}")
                        logging.info(f"  Device: {device_info.get('product_string', 'Unknown')}")
                        logging.info(f"  Path: {device_info.get('path', b'').decode()}")
                        
                        return
                    
                    except (IOError, ValueError, OSError) as e:
                        logging.debug(f"Failed to connect to device {hex(pid)}: {e}")
                        if self.device:
                            self.device.close()
                            self.device = None
                        continue
            
            logging.warning("Could not connect to a compatible DS4 controller, retrying...")
            time.sleep(self.RETRY_DELAY)
            
        raise ConnectionError("No compatible DualShock 4 controller found after multiple attempts.")
    
    def _detect_connection_type(self, device_info):
        """Detect if the controller is connected via USB or Bluetooth"""
        path = device_info.get('path', b'').decode() if isinstance(device_info.get('path'), bytes) else str(device_info.get('path', ''))
        
        # USB connections typically have 'usb' in the path
        if 'usb' in path.lower():
            return f"DS4 (USB) - {device_info.get('product_string', 'Unknown')}"
        # Bluetooth connections often have different path patterns
        elif 'bluetooth' in path.lower() or 'hid' in path.lower():
            return f"DS4 (Bluetooth) - {device_info.get('product_string', 'Unknown')}"
        else:
            return f"DS4 (Unknown) - {device_info.get('product_string', 'Unknown')}"

    def is_connected(self):
        """Enhanced connection checking with timeout handling"""
        if not self.device:
            return False
            
        try:
            # Try to read with a short timeout
            current_time = time.time()
            
            # Don't check too frequently to avoid overwhelming the device
            if current_time - self.last_report_time < 0.01:  # 10ms minimum interval
                return True
                
            # Attempt a non-blocking read as a connection test
            test_data = self.device.read(64)
            
            # If we get data or no data (but no error), connection is good
            return True
            
        except (IOError, ValueError, OSError):
            logging.warning("Controller connection lost")
            return False

    def read_input(self):
        """Optimized input reading with error handling"""
        if not self.device:
            raise ConnectionError("DS4 controller not connected.")
            
        try:
            current_time = time.time()
            data = self.device.read(64)
            
            if data:
                self.last_report_time = current_time
                return data
            else:
                # No data available, but connection is still alive
                return None
                
        except (IOError, ValueError, OSError) as e:
            logging.error(f"Error reading from controller: {e}")
            self.close()
            raise ConnectionError("DS4 controller disconnected during read.")

    def close(self):
        """Clean up device connection"""
        if self.device:
            try:
                self.device.close()
            except:
                pass  # Ignore errors during cleanup
            finally:
                self.device = None
                self.device_info = None
                self.connection_type = None
                logging.info("DS4 connection closed.")
                
    def get_device_info(self):
        """Get detailed information about the connected device"""
        if self.device_info:
            return {
                'connection_type': self.connection_type,
                'vendor_id': hex(self.device_info.get('vendor_id', 0)),
                'product_id': hex(self.device_info.get('product_id', 0)),
                'product_string': self.device_info.get('product_string', 'Unknown'),
                'manufacturer_string': self.device_info.get('manufacturer_string', 'Unknown'),
                'serial_number': self.device_info.get('serial_number', 'Unknown')
            }
        return None

