import subprocess
import sys


def install_packages():
    """
    Installs the required Python packages for the LazyDS4 program
    by calling pip as a subprocess.
    """
    # List of packages to install
    packages = [
        'hidapi',
        'pyserial',
        'pygame',
        'vgamepad',  # Corrected package name
        'PyQt5',
    ]

    print("Checking and installing required packages...")

    try:
        # Construct the command to run pip install for all packages
        # sys.executable ensures we use the same Python interpreter
        # that is running the script.
        command = [sys.executable, '-m', 'pip', 'install'] + packages

        # Run the command and capture the output
        subprocess.check_call(command)

        print("\nAll packages have been successfully installed!")

    except subprocess.CalledProcessError as e:
        print(f"\nAn error occurred during package installation: {e}")
        print("Please check your internet connection and ensure pip is up to date.")
        print("You can try running 'python -m pip install --upgrade pip' first.")
    except FileNotFoundError:
        print("\nError: Python or pip executable not found.")
        print("Please ensure Python is installed and added to your system's PATH.")


if __name__ == "__main__":
    install_packages()
