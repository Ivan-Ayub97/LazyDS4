import logging
from utils.vigem_setup import ViGEmSetup

class ViGEmController:
    def __init__(self):
        self.gamepad = None
        self.vg = None  # Will hold the vgamepad module
        self._connect()

    def _connect(self):
        """Initialize vgamepad and create virtual Xbox 360 gamepad"""
        try:
            # Create ViGEm setup instance for better control
            vigem_setup = ViGEmSetup()
            
            # First, ensure ViGEmBus is installed and working
            if not vigem_setup.setup_vigem():
                raise RuntimeError("ViGEmBus driver installation failed. Please run the application as administrator or install the driver manually from the 'assets' folder.")

            # Import vgamepad only after ensuring ViGEmBus is installed
            import vgamepad as vg
            self.vg = vg

            # Try to create the gamepad
            self.gamepad = vg.VX360Gamepad()
            logging.info("Virtual Xbox 360 controller created successfully.")

        except Exception as e:
            self.close()
            if "VIGEM_ERROR_BUS_NOT_FOUND" in str(e) or "bus not found" in str(e).lower():
                # Try to force reinstall if the driver seems to be missing
                logging.warning("ViGEmBus driver error detected, attempting forced reinstallation...")
                try:
                    vigem_setup = ViGEmSetup()
                    if vigem_setup.force_reinstall_vigem():
                        # Try again after forced reinstallation
                        import vgamepad as vg
                        self.vg = vg
                        self.gamepad = vg.VX360Gamepad()
                        logging.info("Virtual Xbox 360 controller created successfully after forced reinstallation.")
                        return
                except Exception as reinstall_error:
                    logging.error(f"Forced reinstallation failed: {reinstall_error}")
                
                raise RuntimeError("ViGEmBus driver not found, even after attempting forced reinstallation. Please try running the application as an administrator or install the driver manually from the 'assets' folder.")
            else:
                raise RuntimeError(f"Failed to initialize virtual controller: {e}")

    def send_report(self, report):
        """Send an XInput report to the virtual controller"""
        if not self.gamepad or not self.vg:
            return
        
        try:
            # Reset all buttons first
            self.gamepad.reset()
            
            # Map buttons
            if report.wButtons & 0x1000:  # A
                self.gamepad.press_button(self.vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            if report.wButtons & 0x2000:  # B
                self.gamepad.press_button(self.vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
            if report.wButtons & 0x4000:  # X
                self.gamepad.press_button(self.vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            if report.wButtons & 0x8000:  # Y
                self.gamepad.press_button(self.vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
            
            # D-pad
            if report.wButtons & 0x0001:  # Up
                self.gamepad.press_button(self.vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            if report.wButtons & 0x0002:  # Down
                self.gamepad.press_button(self.vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            if report.wButtons & 0x0004:  # Left
                self.gamepad.press_button(self.vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            if report.wButtons & 0x0008:  # Right
                self.gamepad.press_button(self.vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            
            # Shoulder buttons
            if report.wButtons & 0x0100:  # Left shoulder
                self.gamepad.press_button(self.vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
            if report.wButtons & 0x0200:  # Right shoulder
                self.gamepad.press_button(self.vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
            
            # Start/Back
            if report.wButtons & 0x0010:  # Start
                self.gamepad.press_button(self.vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
            if report.wButtons & 0x0020:  # Back
                self.gamepad.press_button(self.vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
            
            # Thumbsticks
            if report.wButtons & 0x0040:  # Left thumb
                self.gamepad.press_button(self.vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
            if report.wButtons & 0x0080:  # Right thumb
                self.gamepad.press_button(self.vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB)
            
            # Analog sticks
            self.gamepad.left_joystick(x_value=report.sThumbLX, y_value=report.sThumbLY)
            self.gamepad.right_joystick(x_value=report.sThumbRX, y_value=report.sThumbRY)
            
            # Triggers
            self.gamepad.left_trigger(value=report.bLeftTrigger)
            self.gamepad.right_trigger(value=report.bRightTrigger)
            
            # Update the virtual gamepad
            self.gamepad.update()
            
        except Exception as e:
            logging.error(f"Error sending report: {e}")

    def close(self):
        """Clean up virtual gamepad resources"""
        if self.gamepad:
            self.gamepad.reset()
            self.gamepad.update()
            self.gamepad = None
        
        logging.info("Virtual controller closed.")
