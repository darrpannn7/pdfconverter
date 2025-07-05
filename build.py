import os
import sys
import subprocess

def main():
    # Ensure PyInstaller is installed
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Build command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", "DocumentWatermarker",
        "main.py"
    ]

    # Run PyInstaller
    print("Running PyInstaller...")
    subprocess.run(cmd, check=True)
    print("\nBuild complete! Your .exe is in the 'dist' folder.")

if __name__ == "__main__":
    main() 