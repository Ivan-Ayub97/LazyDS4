"""
ViGEmBus Setup Utility
Handles automatic installation and verification of the ViGEmBus driver
"""

import os
import sys
import subprocess
import platform
import winreg
import logging
import time
from pathlib import Path


class ViGEmSetup:
    def __init__(self):
        self.arch = "x64" if platform.machine().endswith('64') else "x86"
        self.logger = logging.getLogger(__name__)
        
    def is_vigem_installed(self, test_functionality=False):
        """Check if ViGEmBus is already installed on the system"""
        registry_found = False
        files_found = False
        
        try:
            # Check registry for ViGEmBus installation
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                              r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall") as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                if "ViGEmBus" in display_name:
                                    self.logger.info(f"Found ViGEmBus installation: {display_name}")
                                    registry_found = True
                                    break
                            except FileNotFoundError:
                                pass
                        i += 1
                    except OSError:
                        break
                        
            # Also check system32 for the driver files
            system32_path = Path(os.environ.get("SYSTEMROOT", "C:\\Windows")) / "System32" / "drivers"
            vigem_files = ["ViGEmBus.sys"]
            
            for file in vigem_files:
                if (system32_path / file).exists():
                    self.logger.info(f"Found ViGEmBus driver file: {file}")
                    files_found = True
                    break
                    
        except Exception as e:
            self.logger.warning(f"Error checking ViGEmBus installation: {e}")
        
        # If basic checks pass and we want to test functionality
        if (registry_found or files_found) and test_functionality:
            return self._test_vigem_functionality()
            
        return registry_found or files_found
    
    def _test_vigem_functionality(self):
        """Test if ViGEmBus is actually working by trying to create a virtual gamepad"""
        try:
            import vgamepad as vg
            test_gamepad = vg.VX360Gamepad()
            test_gamepad.reset()
            test_gamepad.update()
            del test_gamepad
            self.logger.info("ViGEmBus functionality test passed")
            return True
        except Exception as e:
            self.logger.warning(f"ViGEmBus functionality test failed: {e}")
            return False
    
    def get_installer_path(self):
        """Get the path to the appropriate ViGEmBus installer"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable - look in assets folder
            base_path = Path(sys.executable).parent
            installer_path = base_path / "assets" / "ViGEmBus_1.22.0_x64_x86_arm64.exe"
            if installer_path.exists():
                return installer_path
        else:
            # Running as script - look in assets folder relative to project root
            base_path = Path(__file__).parent.parent
            installer_path = base_path / "assets" / "ViGEmBus_1.22.0_x64_x86_arm64.exe"
            if installer_path.exists():
                return installer_path
        
        # Fallback: try to find it in the vgamepad package
        try:
            import vgamepad
            vgamepad_path = Path(vgamepad.__file__).parent
            installer_path = vgamepad_path / "win" / "vigem" / "install" / self.arch / f"ViGEmBusSetup_{self.arch}.msi"
            if installer_path.exists():
                return installer_path
        except ImportError:
            pass
            
        return None
    
    def install_vigem(self, silent=False):
        """Install ViGEmBus driver with proper UI and admin privileges"""
        installer_path = self.get_installer_path()
        
        if not installer_path:
            raise FileNotFoundError("ViGEmBus installer not found. Please install it manually from https://github.com/ViGEm/ViGEmBus/releases")
        
        self.logger.info(f"Installing ViGEmBus from: {installer_path}")
        
        try:
            import ctypes
            import ctypes.wintypes as wintypes
            
            # Check if we're already running as administrator
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            except:
                is_admin = False
            
            if not is_admin:
                self.logger.info("Requesting administrator privileges for ViGEmBus installation...")
                # Use ShellExecute with "runas" to request admin privileges
                result = ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "runas",  # Request elevation
                    str(installer_path),
                    "",  # No parameters - show the full installer UI
                    str(installer_path.parent),  # Working directory
                    1  # SW_SHOWNORMAL - Show the installer window
                )
                
                # ShellExecute returns > 32 for success
                if result > 32:
                    self.logger.info("ViGEmBus installer launched with admin privileges. Please follow the on-screen instructions.")
                    return True
                else:
                    error_codes = {
                        0: "Out of memory or resources",
                        2: "File not found",
                        3: "Path not found",
                        5: "Access denied",
                        8: "Out of memory",
                        26: "Sharing violation",
                        27: "File association incomplete",
                        29: "DDE transaction failed",
                        30: "DDE transaction timed out",
                        31: "No application associated"
                    }
                    error_msg = error_codes.get(result, f"Unknown error (code {result})")
                    self.logger.error(f"Failed to launch installer: {error_msg}")
                    return False
            else:
                # We're already admin, run directly
                self.logger.info("Running as administrator, launching installer directly...")
                if installer_path.suffix.lower() == '.exe':
                    # For .exe files, run without silent mode to show the UI
                    result = subprocess.run(
                        [str(installer_path)],
                        check=False,  # Don't raise exception on non-zero exit
                        creationflags=subprocess.CREATE_NO_WINDOW if silent else 0
                    )
                    if result.returncode == 0:
                        self.logger.info("ViGEmBus installation completed successfully")
                        return True
                    else:
                        self.logger.warning(f"Installer exited with code {result.returncode}")
                        return False
                else:
                    # For MSI files
                    cmd = ["msiexec", "/i", str(installer_path)]
                    if silent:
                        cmd.extend(["/quiet", "/norestart"])
                    
                    result = subprocess.run(cmd, check=False)
                    if result.returncode == 0:
                        self.logger.info("ViGEmBus installation completed successfully")
                        return True
                    else:
                        self.logger.warning(f"MSI installer exited with code {result.returncode}")
                        return False
                
        except Exception as e:
            self.logger.error(f"Unexpected error during installation: {e}")
            return False
    
    def setup_vigem(self, force_install=False):
        """Main setup function - check and install ViGEmBus if needed"""
        if not force_install and self.is_vigem_installed(test_functionality=True):
            self.logger.info("ViGEmBus is already installed and working")
            return True
        
        if force_install:
            self.logger.info("Forcing ViGEmBus reinstallation...")
        else:
            self.logger.info("ViGEmBus not found or not working, attempting installation...")
        
        try:
            success = self.install_vigem(silent=True)
            if success:
                # Wait and monitor for installation completion
                self.logger.info("Monitoring installation progress...")
                
                # Wait for installation to complete (up to 60 seconds)
                for i in range(12):  # 12 * 5 seconds = 60 seconds max wait
                    time.sleep(5)
                    if self.is_vigem_installed(test_functionality=True):
                        self.logger.info("ViGEmBus installation completed and verified successfully")
                        return True
                    self.logger.info(f"Installation in progress... ({(i+1)*5}s elapsed)")
                
                # Final check after timeout
                if self.is_vigem_installed(test_functionality=False):
                    self.logger.info("ViGEmBus driver files detected - installation appears successful")
                    return True
                else:
                    self.logger.warning("ViGEmBus installation timeout - driver may still be installing")
                    return False
            else:
                self.logger.error("ViGEmBus installation failed to launch")
                return False
        except Exception as e:
            self.logger.error(f"Error during ViGEmBus setup: {e}")
            return False
    
    def force_reinstall_vigem(self):
        """Force reinstallation of ViGEmBus driver"""
        return self.setup_vigem(force_install=True)


def ensure_vigem_installed():
    """Utility function to ensure ViGEmBus is installed"""
    setup = ViGEmSetup()
    return setup.setup_vigem()


if __name__ == "__main__":
    # Test the setup
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    setup = ViGEmSetup()
    
    print(f"System architecture: {setup.arch}")
    print(f"ViGEmBus installed: {setup.is_vigem_installed()}")
    
    installer_path = setup.get_installer_path()
    if installer_path:
        print(f"Installer found at: {installer_path}")
    else:
        print("Installer not found")
        
    if not setup.is_vigem_installed():
        print("Installing ViGEmBus...")
        success = setup.setup_vigem()
        print(f"Installation {'successful' if success else 'failed'}")
