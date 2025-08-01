# C:\Users\negro\Desktop\LazyDS4\utils\bluetooth_manager.py

import subprocess
import logging
import time
import json
import re

class BluetoothManager:
    """
    Enhanced Bluetooth device discovery and auto-pairing system for DS4 controllers.
    Uses multiple methods to find and connect to Bluetooth devices automatically.
    """
    
    # DS4 controller identifiers
    DS4_NAMES = ['wireless controller', 'dualshock 4', 'ds4', 'controller', 'gamepad']
    DS4_MAC_PREFIXES = ['04:1E:64', '00:1E:3D', '00:16:FE', '00:1B:DC', '00:18:12']
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def auto_pair_controller(self):
        """
        Comprehensive auto-pairing system that searches for and connects to DS4 controllers.
        Returns True if successfully paired with a controller.
        """
        self.logger.info("Starting comprehensive auto-pairing for DS4 controllers...")
        
        # Step 1: Scan for discoverable devices
        devices = self.discover_devices()
        
        # Step 2: Try to pair with each potential DS4 controller
        for device in devices:
            try:
                if self._is_ds4_controller(device) and not device.get('Connected', False):
                    self.logger.info(f"Attempting to pair with: {device['Name']} ({device.get('Address', 'Unknown')})")
                    
                    if self._pair_with_device(device):
                        self.logger.info(f"Successfully paired with: {device['Name']}")
                        return True
                    else:
                        self.logger.warning(f"Failed to pair with: {device['Name']}")
            except Exception as e:
                self.logger.error(f"Error pairing with {device.get('Name', 'Unknown')}: {e}")
        
        # Step 3: If no discoverable devices, try advanced scanning
        if not devices:
            self.logger.info("No discoverable devices found, trying advanced scanning...")
            return self._advanced_bluetooth_scan()
        
        self.logger.info("No DS4 controllers available for pairing")
        return False
    
    def discover_devices(self):
        """Enhanced device discovery using multiple PowerShell methods."""
        self.logger.info("Scanning for Bluetooth devices...")
        devices = []
        
        # Method 1: Get all Bluetooth devices (paired and unpaired)
        devices.extend(self._get_bluetooth_devices_comprehensive())
        
        # Method 2: Scan for discoverable devices
        devices.extend(self._scan_discoverable_devices())
        
        # Remove duplicates based on address
        unique_devices = []
        seen_addresses = set()
        
        for device in devices:
            addr = device.get('Address', '')
            if addr and addr not in seen_addresses:
                seen_addresses.add(addr)
                unique_devices.append(device)
        
        # Filter for potential DS4 controllers
        controller_devices = [d for d in unique_devices if self._is_ds4_controller(d)]
        
        self.logger.info(f"Found {len(controller_devices)} potential DS4 controllers")
        return controller_devices
    
    def _get_bluetooth_devices_comprehensive(self):
        """Get all Bluetooth devices using comprehensive PowerShell query."""
        devices = []
        
        try:
            # Enhanced PowerShell command to get all Bluetooth devices
            ps_command = """
            $devices = @()
            
            # Get paired devices
            try {
                $pairedDevices = Get-PnpDevice -Class Bluetooth -Status OK,Unknown | Where-Object { 
                    $_.FriendlyName -match '(controller|dualshock|ds4|gamepad|wireless)' 
                }
                foreach ($device in $pairedDevices) {
                    $devices += @{
                        Name = $device.FriendlyName
                        Address = $device.InstanceId
                        Connected = ($device.Status -eq 'OK')
                        Authenticated = $true
                        Type = 'Paired'
                    }
                }
            } catch { }
            
            # Get discoverable devices
            try {
                $discoverableDevices = Get-BluetoothDevice -Discoverable -ErrorAction SilentlyContinue
                foreach ($device in $discoverableDevices) {
                    if ($device.Name -match '(controller|dualshock|ds4|gamepad|wireless)') {
                        $devices += @{
                            Name = $device.Name
                            Address = $device.DeviceID
                            Connected = $device.Connected
                            Authenticated = $device.Authenticated
                            Type = 'Discoverable'
                        }
                    }
                }
            } catch { }
            
            $devices | ConvertTo-Json
            """
            
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True, text=True, timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    json_data = json.loads(result.stdout.strip())
                    if isinstance(json_data, dict):
                        json_data = [json_data]
                    
                    for device in json_data:
                        if device.get('Name'):
                            clean_device = {
                                'Name': device['Name'],
                                'Address': self._extract_address_from_id(device.get('Address', '')),
                                'Connected': device.get('Connected', False),
                                'Authenticated': device.get('Authenticated', False),
                                'Type': device.get('Type', 'Unknown')
                            }
                            devices.append(clean_device)
                            
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Failed to parse comprehensive device scan: {e}")
                    
        except Exception as e:
            self.logger.warning(f"Comprehensive device scan failed: {e}")
        
        return devices
    
    def _scan_discoverable_devices(self):
        """Scan for devices currently in discoverable/pairing mode."""
        devices = []
        
        try:
            # Start a fresh Bluetooth scan
            scan_command = """
            try {
                # Enable Bluetooth discovery
                Add-Type -AssemblyName System.Runtime.WindowsRuntime
                
                # Use basic Get-BluetoothDevice scan
                $devices = Get-BluetoothDevice -Discoverable -ErrorAction SilentlyContinue | Where-Object {
                    $_.Name -match '(controller|dualshock|ds4|gamepad|wireless)' -and 
                    -not $_.Authenticated
                }
                
                $devices | Select-Object Name, DeviceID, Connected, Authenticated | ConvertTo-Json
            } catch {
                Write-Output '[]'
            }
            """
            
            result = subprocess.run(
                ["powershell", "-Command", scan_command],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    json_data = json.loads(result.stdout.strip())
                    if isinstance(json_data, dict):
                        json_data = [json_data]
                    
                    for device in json_data:
                        if device.get('Name'):
                            devices.append({
                                'Name': device['Name'],
                                'Address': self._extract_address_from_id(device.get('DeviceID', '')),
                                'Connected': device.get('Connected', False),
                                'Authenticated': device.get('Authenticated', False),
                                'Type': 'Discoverable'
                            })
                            
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            self.logger.warning(f"Discoverable device scan failed: {e}")
        
        return devices
    
    def _is_ds4_controller(self, device):
        """Check if a device is likely a DS4 controller based on name and address."""
        name = device.get('Name', '').lower()
        address = device.get('Address', '')
        
        # Check device name for DS4 keywords
        name_match = any(keyword in name for keyword in self.DS4_NAMES)
        
        # Check MAC address prefix (if available)
        mac_match = False
        if address and len(address) >= 8:
            for prefix in self.DS4_MAC_PREFIXES:
                if address.upper().startswith(prefix.replace(':', '')):
                    mac_match = True
                    break
        
        return name_match or mac_match
    
    def _pair_with_device(self, device):
        """Attempt to pair with a specific device using PowerShell."""
        address = device.get('Address', '')
        name = device.get('Name', 'Unknown Device')
        
        if not address:
            self.logger.warning(f"No address available for device: {name}")
            return False
        
        try:
            # PowerShell command to attempt pairing
            pair_command = f"""
            try {{
                # Try to pair using Add-BluetoothDevice (Windows 10/11)
                $device = Get-BluetoothDevice -Name "{name}" -ErrorAction SilentlyContinue
                if ($device -and -not $device.Authenticated) {{
                    $result = $device | Add-BluetoothDevice -Confirm:$false -ErrorAction SilentlyContinue
                    if ($result) {{
                        Write-Output "SUCCESS: Paired with {name}"
                    }} else {{
                        Write-Output "FAILED: Could not pair with {name}"
                    }}
                }} else {{
                    Write-Output "INFO: Device already paired or not found"
                }}
            }} catch {{
                Write-Output "ERROR: $($_.Exception.Message)"
            }}
            """
            
            result = subprocess.run(
                ["powershell", "-Command", pair_command],
                capture_output=True, text=True, timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            output = result.stdout.strip()
            self.logger.info(f"Pairing result for {name}: {output}")
            
            # Check if pairing was successful
            if "SUCCESS" in output:
                return True
            elif "already paired" in output.lower():
                # Device might already be paired, try to connect
                return self._connect_to_device(device)
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Error pairing with {name}: {e}")
            return False
    
    def _connect_to_device(self, device):
        """Attempt to connect to an already paired device."""
        name = device.get('Name', 'Unknown Device')
        
        try:
            connect_command = f"""
            try {{
                $device = Get-BluetoothDevice -Name "{name}" -ErrorAction SilentlyContinue
                if ($device -and $device.Authenticated -and -not $device.Connected) {{
                    $result = $device | Connect-BluetoothDevice -ErrorAction SilentlyContinue
                    if ($device.Connected) {{
                        Write-Output "SUCCESS: Connected to {name}"
                    }} else {{
                        Write-Output "FAILED: Could not connect to {name}"
                    }}
                }} else {{
                    Write-Output "INFO: Device not paired or already connected"
                }}
            }} catch {{
                Write-Output "ERROR: $($_.Exception.Message)"
            }}
            """
            
            result = subprocess.run(
                ["powershell", "-Command", connect_command],
                capture_output=True, text=True, timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            output = result.stdout.strip()
            self.logger.info(f"Connection result for {name}: {output}")
            
            return "SUCCESS" in output
            
        except Exception as e:
            self.logger.error(f"Error connecting to {name}: {e}")
            return False
    
    def _advanced_bluetooth_scan(self):
        """Advanced Bluetooth scanning when no discoverable devices are found."""
        self.logger.info("Performing advanced Bluetooth scan...")
        
        try:
            # Try to trigger a new device discovery
            advanced_scan = """
            try {
                # Start Bluetooth device discovery
                Add-Type -AssemblyName System.Runtime.WindowsRuntime
                
                # Use WinRT Bluetooth APIs if available
                [Windows.Devices.Bluetooth.BluetoothAdapter]::GetDefaultAsync().GetResults()
                
                # Wait a moment for discovery
                Start-Sleep -Seconds 3
                
                # Get any new discoverable devices
                $devices = Get-BluetoothDevice -Discoverable -ErrorAction SilentlyContinue | Where-Object {
                    $_.Name -match '(controller|dualshock|ds4|gamepad|wireless)'
                }
                
                $devices | Select-Object Name, DeviceID, Connected, Authenticated | ConvertTo-Json
                
            } catch {
                # Fallback: Just open Bluetooth settings for manual pairing
                Start-Process ms-settings:bluetooth
                Write-Output 'SETTINGS_OPENED'
            }
            """
            
            result = subprocess.run(
                ["powershell", "-Command", advanced_scan],
                capture_output=True, text=True, timeout=20,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if "SETTINGS_OPENED" in result.stdout:
                self.logger.info("Opened Bluetooth settings for manual pairing")
                return True
            
            # Try to process any newly discovered devices
            if result.stdout.strip():
                try:
                    json_data = json.loads(result.stdout.strip())
                    if isinstance(json_data, dict):
                        json_data = [json_data]
                    
                    for device_data in json_data:
                        device = {
                            'Name': device_data.get('Name', ''),
                            'Address': self._extract_address_from_id(device_data.get('DeviceID', '')),
                            'Connected': device_data.get('Connected', False),
                            'Authenticated': device_data.get('Authenticated', False)
                        }
                        
                        if self._is_ds4_controller(device) and not device['Connected']:
                            return self._pair_with_device(device)
                            
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            self.logger.error(f"Advanced scan failed: {e}")
        
        return False

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
