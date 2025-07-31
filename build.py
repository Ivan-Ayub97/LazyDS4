#!/usr/bin/env python3
"""
Build script for LazyDS4
Creates the executable using PyInstaller with proper vgamepad dependencies
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path
from datetime import datetime


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}")
    
    # Remove spec file if it was auto-generated
    spec_files = ['LazyDS4.spec']
    for spec_file in spec_files:
        if os.path.exists(spec_file):
            print(f"Keeping existing {spec_file}")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building LazyDS4 executable...")
    
    # Check if spec file exists
    spec_file = "LazyDS4.spec"
    if not os.path.exists(spec_file):
        print(f"Error: {spec_file} not found!")
        return False
    
    try:
        # Run PyInstaller
        cmd = [sys.executable, "-m", "PyInstaller", spec_file]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("Build completed successfully!")
        print(f"Executable created at: dist/LazyDS4.exe")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def verify_dependencies():
    """Verify that all required dependencies are available"""
    print("Verifying dependencies...")
    
    required_packages = {
        'PyQt5': 'PyQt5',
        'hid': 'hidapi',
        'vgamepad': 'vgamepad'
    }
    missing_packages = []
    
    for package_name, install_name in required_packages.items():
        try:
            if package_name == 'vgamepad':
                # Special handling for vgamepad - don't initialize it during build
                import importlib.util
                spec = importlib.util.find_spec(package_name)
                if spec is None:
                    raise ImportError(f"No module named '{package_name}'")
                print(f"✓ {package_name} (found, but not initialized - this is normal)")
            else:
                __import__(package_name)
                print(f"✓ {package_name}")
        except ImportError:
            missing_packages.append(install_name)
            print(f"✗ {package_name}")
        except Exception as e:
            if package_name == 'vgamepad' and 'VIGEM_ERROR_BUS_NOT_FOUND' in str(e):
                # This is expected - vgamepad is installed but ViGEmBus is not
                print(f"✓ {package_name} (installed, ViGEmBus not found - this is expected during build)")
            else:
                print(f"⚠ {package_name} (warning: {e})")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install " + " ".join(missing_packages))
        return False
    
    return True

def verify_assets():
    """Verify that all required assets are present"""
    print("Verifying assets...")
    
    required_assets = [
        'assets/icon.ico',
        'assets/icon.png', 
        'assets/small_image.bmp',
        'assets/ViGEmBus_1.22.0_x64_x86_arm64.exe'
    ]
    
    missing_assets = []
    for asset in required_assets:
        if os.path.exists(asset):
            print(f"✓ {asset}")
        else:
            missing_assets.append(asset)
            print(f"✗ {asset}")
    
    if missing_assets:
        print(f"\nMissing assets: {', '.join(missing_assets)}")
        print("Please ensure all required assets are in the assets/ directory.")
        return False
    
    return True

def create_installer():
    """Create installer using Inno Setup"""
    print("Creating installer with Inno Setup...")
    
    # Check if Inno Setup is available
    inno_setup_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe"
    ]
    
    iscc_path = None
    for path in inno_setup_paths:
        if os.path.exists(path):
            iscc_path = path
            break
    
    if not iscc_path:
        print("Warning: Inno Setup Compiler (ISCC.exe) not found.")
        print("Please install Inno Setup to create installer packages.")
        print("Available at: https://jrsoftware.org/isinfo.php")
        return False
    
    # Check if setup script exists
    setup_script = "Setup.iss"
    if not os.path.exists(setup_script):
        print(f"Error: {setup_script} not found!")
        return False
    
    try:
        # Run Inno Setup Compiler
        cmd = [iscc_path, setup_script]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("Installer created successfully!")
        
        # Find the created installer
        output_dir = Path("Output")
        if output_dir.exists():
            installer_files = list(output_dir.glob("*.exe"))
            if installer_files:
                installer_path = installer_files[0]
                size_mb = installer_path.stat().st_size / (1024 * 1024)
                print(f"Installer: {installer_path}")
                print(f"Installer size: {size_mb:.1f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Installer creation failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main build function"""
    print("LazyDS4 Build Script")
    print("=" * 50)
    
    # Start timer
    start_time = time.time()
    
    # Verify dependencies and assets
    if not verify_dependencies() or not verify_assets():
        return False
    
    # Clean previous builds
    clean_build()
    
    # Build executable
    if not build_executable():
        return False
    
    # Create installer
    if not create_installer():
        # Don't fail the whole build if installer creation fails
        print("\nBuild process finished with warnings.")
    
    # End timer and show duration
    duration = time.time() - start_time
    print(f"\nTotal build time: {duration:.2f} seconds")
    
    print("=" * 50)
    print("Build process finished successfully!")
    print("You can find the executable at: dist/LazyDS4.exe")
    print("Installer (if created) is in: Output/")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
