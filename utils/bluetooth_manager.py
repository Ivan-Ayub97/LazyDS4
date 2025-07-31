# C:\Users\negro\Desktop\LazyDS4\utils\bluetooth_manager.py

import subprocess
import logging

class BluetoothManager:
    """
    Handles Bluetooth device discovery and pairing using system tools.
    """
    def discover_devices(self):
        """Discover nearby Bluetooth devices that are in pairing mode."""
        logging.info("Scanning for Bluetooth devices...")
        
        # Try multiple methods for device discovery
        devices = []
        
        # Method 1: PowerShell Get-BluetoothDevice (Windows 10/11)
        try:
            ps_command = "Get-BluetoothDevice -Discoverable -ErrorAction SilentlyContinue | Select-Object Name, DeviceID, Connected, Authenticated | ConvertTo-Json"
            result = subprocess.run(["powershell", "-Command", ps_command], 
                                  capture_output=True, text=True, timeout=10, 
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0 and result.stdout.strip():
                import json
                try:
                    json_data = json.loads(result.stdout.strip())
                    if isinstance(json_data, dict):
                        json_data = [json_data]  # Single device
                    
                    for device in json_data:
                        if device.get('Name') and not device.get('Authenticated', True):
                            devices.append({
                                "Name": device['Name'],
                                "Address": self._extract_address_from_id(device.get('DeviceID', '')),
                                "Connected": device.get('Connected', False),
                                "Authenticated": device.get('Authenticated', False)
                            })
                except json.JSONDecodeError:
                    logging.warning("Failed to parse PowerShell JSON output")
        except Exception as e:
            logging.warning(f"PowerShell method failed: {e}")
        
        # Method 2: Fallback using bluetoothctl (if available)
        if not devices:
            devices = self._discover_with_bluetoothctl()
        
        # Filter for DS4 controllers
        controller_devices = []
        for device in devices:
            name = device.get('Name', '').lower()
            if any(keyword in name for keyword in ['controller', 'dualshock', 'gamepad', 'ds4', 'wireless']):
                controller_devices.append(device)
        
        logging.info(f"Found {len(controller_devices)} potential controllers")
        return controller_devices

    def pair_device(self, address):
        """
        Initiate pairing with a device by opening Windows Bluetooth settings.
        This is the modern, recommended way to handle pairing.
        """
        try:
            logging.info(f"Opening Bluetooth settings to pair device: {address}")
            subprocess.run(["powershell", "-Command", "Start-Process ms-settings:bluetooth"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logging.error(f"Failed to open Bluetooth settings: {e}")
            return False
            
    def _extract_address_from_id(self, device_id):
        """Extract Bluetooth address from a Windows DeviceID"""
        try:
            # DeviceID format is often BTHLE\VID_...\<address>
            parts = device_id.split('_')
            if len(parts) > 1 and len(parts[-1]) == 12:
                return parts[-1]
            
            # Alternative format for some devices
            if '-' in device_id:
                addr = device_id.split('-')[-1]
                if len(addr) == 12:
                    return addr
                    
        except Exception as e:
            logging.warning(f"Could not parse address from DeviceID: {device_id} ({e})")
        
        return device_id # Fallback to full ID if parsing fails

    def _discover_with_bluetoothctl(self):
        """Fallback device discovery using bluetoothctl (Linux-like environments)"""
        logging.info("Attempting fallback discovery with bluetoothctl...")
        try:
            # This is unlikely to work on standard Windows, but provides compatibility
            result = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return []
            
            devices = []
            for line in result.stdout.strip().split("\n"):
                parts = line.strip().split()
                if len(parts) >= 3:
                    devices.append({
                        "Name": " ".join(parts[2:]),
                        "Address": parts[1],
                        "Authenticated": False # Cannot determine from this command
                    })
            return devices
        except (subprocess.CalledProcessError, FileNotFoundError):
            logging.info("bluetoothctl not found, skipping fallback discovery")
            return []
