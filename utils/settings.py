"""
Settings and Configuration Management for LazyDS4
Handles user preferences and application configuration
"""

import json
import os
import logging
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal


class SettingsManager(QObject):
    """Manages application settings and user preferences"""
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.settings_file = self._get_settings_path()
        self.default_settings = {
            "general": {
                "auto_start_service": False,
                "minimize_to_tray": False,
                "start_with_windows": False,
                "close_to_tray": True,
                "show_battery_warnings": True,
                "battery_warning_threshold": 20,
                "battery_critical_threshold": 10,
                "polling_rate_ms": 1,
                "auto_reconnect": True,
                "reconnect_attempts": 5,
                "reconnect_delay": 2.0,
                "cpu_priority": "normal",  # low, normal, high, realtime
                "prefer_wired_connection": True,
                "enable_statistics": True
            },
            "ui": {
                "theme": "dark",
                "accent_color": "#0078d4",
                "show_advanced_info": False,
                "show_input_overlay": False,
                "overlay_opacity": 80,
                "show_fps_counter": False,
                "log_level": "INFO",
                "window_geometry": None,
                "window_opacity": 100,
                "remember_window_position": True,
                "enable_animations": True,
                "compact_mode": False
            },
            "controller": {
                # Stick settings
                "stick_deadzone_left_x": 3000,
                "stick_deadzone_left_y": 3000,
                "stick_deadzone_right_x": 3000,
                "stick_deadzone_right_y": 3000,
                "stick_sensitivity": 1.0,
                "anti_deadzone": 0.15,
                "response_curve": "linear",  # linear, quadratic, cubic, custom
                
                # Trigger settings
                "trigger_deadzone": 0,
                "trigger_sensitivity": 1.0,
                "trigger_threshold": 5,
                
                # Haptic feedback
                "vibration_enabled": True,
                "vibration_strength": 100,
                "led_enabled": True,
                "led_color": "#0066CC",
                "led_brightness": 50,
                
                # Advanced features
                "adaptive_polling": True,
                "enable_gyroscope": False,
                "gyro_sensitivity": 1.0,
                "enable_touchpad_mouse": False,
                "touchpad_sensitivity": 2.0,
                "enable_motion_controls": False,
                "stick_click_protection": True,
                "double_tap_time_ms": 300
            },
            "profiles": {
                "enabled": True,
                "active_profile": "default",
                "auto_switch": False,
                "game_detection": False,
                "profiles_list": {
                    "default": {
                        "name": "Default Profile",
                        "description": "Standard gaming profile",
                        "stick_deadzone_left_x": 3000,
                        "stick_deadzone_left_y": 3000,
                        "stick_deadzone_right_x": 3000,
                        "stick_deadzone_right_y": 3000,
                        "stick_sensitivity": 1.0,
                        "trigger_sensitivity": 1.0,
                        "vibration_strength": 100
                    },
                    "fps": {
                        "name": "FPS Games",
                        "description": "Optimized for first-person shooters",
                        "stick_deadzone_left_x": 2000,
                        "stick_deadzone_left_y": 2000,
                        "stick_deadzone_right_x": 1500,
                        "stick_deadzone_right_y": 1500,
                        "stick_sensitivity": 1.2,
                        "trigger_sensitivity": 1.1,
                        "vibration_strength": 80
                    },
                    "racing": {
                        "name": "Racing Games",
                        "description": "Optimized for racing games",
                        "stick_deadzone_left_x": 1000,
                        "stick_deadzone_left_y": 4000,
                        "stick_deadzone_right_x": 4000,
                        "stick_deadzone_right_y": 4000,
                        "stick_sensitivity": 0.8,
                        "trigger_sensitivity": 1.3,
                        "vibration_strength": 120
                    }
                }
            },
            "advanced": {
                "enable_macro_support": False,
                "enable_rapid_fire": False,
                "rapid_fire_rate_hz": 10,
                "input_buffer_size": 64,
                "max_input_lag_ms": 16,
                "enable_input_logging": False,
                "log_file_max_size_mb": 10,
                "audio_feedback_enabled": False,
                "speaker_volume": 50,
                "microphone_monitoring": False,
                "connection_timeout_ms": 5000,
                "enable_bluetooth_le": True
            },
            "calibration": {
                "left_stick": {
                    "x": {"min": 0, "max": 255, "center": 128},
                    "y": {"min": 0, "max": 255, "center": 128}
                },
                "right_stick": {
                    "x": {"min": 0, "max": 255, "center": 128},
                    "y": {"min": 0, "max": 255, "center": 128}
                },
                "triggers": {
                    "left": {"min": 0, "max": 255},
                    "right": {"min": 0, "max": 255}
                },
                "auto_calibrate": False,
                "calibration_samples": 1000
            },
            "statistics": {
                "session_time_minutes": 0,
                "total_usage_hours": 0.0,
                "button_press_counts": {},
                "connection_count": 0,
                "last_used": None,
                "average_input_lag_ms": 0.0,
                "peak_input_lag_ms": 0.0
            }
        }
        self.settings = self.load_settings()
    
    def _get_settings_path(self):
        """Get the path for settings file"""
        # Use AppData on Windows
        if os.name == 'nt':
            app_data = os.getenv('APPDATA')
            settings_dir = Path(app_data) / 'LazyDS4'
        else:
            # Use home directory on other systems
            settings_dir = Path.home() / '.lazyds4'
        
        settings_dir.mkdir(exist_ok=True)
        return settings_dir / 'settings.json'
    
    def load_settings(self):
        """Load settings from file or create default ones"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                
                # Merge with defaults to ensure all keys exist
                settings = self._merge_settings(self.default_settings, loaded_settings)
                logging.info(f"Settings loaded from {self.settings_file}")
                return settings
            else:
                logging.info("Creating default settings file")
                self.save_settings(self.default_settings)
                return self.default_settings.copy()
        
        except Exception as e:
            logging.error(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self, settings=None):
        """Save settings to file"""
        if settings is None:
            settings = self.settings
        
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            logging.info(f"Settings saved to {self.settings_file}")
            return True
        except Exception as e:
            logging.error(f"Error saving settings: {e}")
            return False
    
    def _merge_settings(self, default, loaded):
        """Recursively merge loaded settings with defaults"""
        result = default.copy()
        
        for key, value in loaded.items():
            if key in result:
                if isinstance(value, dict) and isinstance(result[key], dict):
                    result[key] = self._merge_settings(result[key], value)
                else:
                    result[key] = value
        
        return result
    
    def get(self, category, key, default=None):
        """Get a specific setting value"""
        try:
            return self.settings.get(category, {}).get(key, default)
        except:
            return default
    
    def set(self, category, key, value):
        """Set a specific setting value"""
        if category not in self.settings:
            self.settings[category] = {}
        
        old_value = self.settings[category].get(key)
        self.settings[category][key] = value
        
        # Auto-save on change
        self.save_settings()
        
        # Emit signal if value changed
        if old_value != value:
            self.settings_changed.emit({
                'category': category,
                'key': key,
                'value': value,
                'old_value': old_value
            })
    
    def get_category(self, category):
        """Get all settings for a category"""
        return self.settings.get(category, {}).copy()
    
    def set_category(self, category, settings_dict):
        """Set all settings for a category"""
        self.settings[category] = settings_dict.copy()
        self.save_settings()
        self.settings_changed.emit({
            'category': category,
            'settings': settings_dict
        })
    
    def reset_to_defaults(self, category=None):
        """Reset settings to defaults"""
        if category:
            if category in self.default_settings:
                self.settings[category] = self.default_settings[category].copy()
        else:
            self.settings = self.default_settings.copy()
        
        self.save_settings()
        self.settings_changed.emit({'reset': True, 'category': category})
    
    def export_settings(self, file_path):
        """Export settings to a file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, file_path):
        """Import settings from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # Merge and validate
            self.settings = self._merge_settings(self.default_settings, imported_settings)
            self.save_settings()
            self.settings_changed.emit({'imported': True})
            return True
        except Exception as e:
            logging.error(f"Error importing settings: {e}")
            return False
    
    def get_settings_info(self):
        """Get information about the settings file"""
        try:
            if self.settings_file.exists():
                stat = self.settings_file.stat()
                return {
                    'path': str(self.settings_file),
                    'size': stat.st_size,
                    'modified': stat.st_mtime,
                    'exists': True
                }
            else:
                return {
                    'path': str(self.settings_file),
                    'exists': False
                }
        except Exception as e:
            return {'error': str(e)}
    
    # Profile Management Methods
    def create_profile(self, name, description="", base_profile="default"):
        """Create a new controller profile"""
        if "profiles" not in self.settings:
            self.settings["profiles"] = self.default_settings["profiles"].copy()
        
        # Copy settings from base profile
        base_settings = self.settings["profiles"]["profiles_list"].get(
            base_profile, self.default_settings["profiles"]["profiles_list"]["default"]
        ).copy()
        
        base_settings["name"] = name
        base_settings["description"] = description
        
        self.settings["profiles"]["profiles_list"][name.lower().replace(" ", "_")] = base_settings
        self.save_settings()
        return True
    
    def delete_profile(self, profile_id):
        """Delete a controller profile"""
        if profile_id == "default":
            return False  # Can't delete default profile
        
        if profile_id in self.settings.get("profiles", {}).get("profiles_list", {}):
            del self.settings["profiles"]["profiles_list"][profile_id]
            
            # Switch to default if deleted profile was active
            if self.settings["profiles"]["active_profile"] == profile_id:
                self.settings["profiles"]["active_profile"] = "default"
            
            self.save_settings()
            return True
        return False
    
    def switch_profile(self, profile_id):
        """Switch to a different controller profile"""
        if profile_id in self.settings.get("profiles", {}).get("profiles_list", {}):
            self.settings["profiles"]["active_profile"] = profile_id
            self.save_settings()
            self.settings_changed.emit({
                'profile_switched': True, 
                'active_profile': profile_id
            })
            return True
        return False
    
    def get_active_profile(self):
        """Get the currently active profile settings"""
        active_id = self.get("profiles", "active_profile", "default")
        return self.settings.get("profiles", {}).get("profiles_list", {}).get(
            active_id, self.default_settings["profiles"]["profiles_list"]["default"]
        )
    
    def get_all_profiles(self):
        """Get all available profiles"""
        return self.settings.get("profiles", {}).get("profiles_list", {})
    
    # Statistics Methods
    def update_session_time(self, minutes):
        """Update session usage time"""
        if "statistics" not in self.settings:
            self.settings["statistics"] = self.default_settings["statistics"].copy()
        
        self.settings["statistics"]["session_time_minutes"] += minutes
        self.settings["statistics"]["total_usage_hours"] += minutes / 60.0
        self.save_settings()
    
    def record_button_press(self, button_name):
        """Record button press for statistics"""
        if "statistics" not in self.settings:
            self.settings["statistics"] = self.default_settings["statistics"].copy()
        
        if "button_press_counts" not in self.settings["statistics"]:
            self.settings["statistics"]["button_press_counts"] = {}
        
        counts = self.settings["statistics"]["button_press_counts"]
        counts[button_name] = counts.get(button_name, 0) + 1
    
    def update_input_lag_stats(self, lag_ms):
        """Update input lag statistics"""
        if "statistics" not in self.settings:
            self.settings["statistics"] = self.default_settings["statistics"].copy()
        
        stats = self.settings["statistics"]
        
        # Update average (simple moving average)
        current_avg = stats.get("average_input_lag_ms", 0.0)
        stats["average_input_lag_ms"] = (current_avg * 0.9) + (lag_ms * 0.1)
        
        # Update peak
        stats["peak_input_lag_ms"] = max(stats.get("peak_input_lag_ms", 0.0), lag_ms)
    
    def get_statistics(self):
        """Get usage statistics"""
        return self.settings.get("statistics", self.default_settings["statistics"]).copy()
    
    def reset_statistics(self):
        """Reset all usage statistics"""
        self.settings["statistics"] = self.default_settings["statistics"].copy()
        self.save_settings()
    
    # Advanced Settings Validation
    def validate_setting(self, category, key, value):
        """Validate a setting value before applying"""
        validation_rules = {
            "general": {
                "polling_rate_ms": lambda x: isinstance(x, (int, float)) and 0.1 <= x <= 100,
                "reconnect_attempts": lambda x: isinstance(x, int) and 1 <= x <= 10,
                "cpu_priority": lambda x: x in ["low", "normal", "high", "realtime"]
            },
            "controller": {
                "stick_sensitivity": lambda x: isinstance(x, (int, float)) and 0.1 <= x <= 5.0,
                "vibration_strength": lambda x: isinstance(x, int) and 0 <= x <= 150,
                "response_curve": lambda x: x in ["linear", "quadratic", "cubic", "custom"]
            },
            "ui": {
                "window_opacity": lambda x: isinstance(x, int) and 10 <= x <= 100,
                "overlay_opacity": lambda x: isinstance(x, int) and 10 <= x <= 100
            }
        }
        
        if category in validation_rules and key in validation_rules[category]:
            return validation_rules[category][key](value)
        
        return True  # No validation rule found, assume valid
    
    def set_validated(self, category, key, value):
        """Set a setting value with validation"""
        if self.validate_setting(category, key, value):
            self.set(category, key, value)
            return True
        else:
            logging.warning(f"Invalid value for {category}.{key}: {value}")
            return False
