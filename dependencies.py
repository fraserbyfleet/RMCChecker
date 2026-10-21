import sys
import subprocess

REQUIRED_PACKAGES = {
    "pandas": "pandas",
    "openpyxl": "openpyxl",
    "lxml": "lxml",
    "beautifulsoup4": "bs4"
}

def ensure_package(package, module):

    try:
        __import__(module)

    except ImportError:

        print(f"Installing {package}...")

        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            package
        ])

def install_dependencies():

    for package, module in REQUIRED_PACKAGES.items():
        ensure_package(package, module)