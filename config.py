import os
from pathlib import Path

# Base directory for storing configuration and keys
BASE_DIR = Path.home() / '.khcrypt'
KEY_FILE = BASE_DIR / '.auth_key'
LOG_FILE = BASE_DIR / 'auth.log'

# Security settings
ENCRYPTION_KEY = os.getenv('KHCRYPT_KEY', '')  # Set this in .env file
MAX_FAILED_ATTEMPTS = 3
AUTO_LOCK_DELAY = 5  # seconds

# USB detection settings
SCAN_INTERVAL = 1  # seconds
ALLOWED_DRIVE_TYPES = ['removable', 'usb']

# System-specific commands
SYSTEM_COMMANDS = {
    'windows': {
        'lock': 'rundll32.exe user32.dll,LockWorkStation',
        'shutdown': 'shutdown /s /t 0',
    },
    'linux': {
        'lock': 'xset dpms force off',
        'shutdown': 'shutdown -h now',
    },
    'darwin': {  # macOS
        'lock': 'pmset displaysleepnow',
        'shutdown': 'shutdown -h now',
    }
}

# Logging configuration
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

# Create base directory if it doesn't exist
BASE_DIR.mkdir(parents=True, exist_ok=True) 