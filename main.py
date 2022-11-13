import os
import sys
import time
import logging
import platform
import subprocess
from pathlib import Path
from typing import Optional, List, Dict

import psutil
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

from config import *

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT
)

class USBDetector:
    def __init__(self):
        self.system = platform.system().lower()
        self.registered_usbs: Dict[str, str] = {}  # UUID -> encrypted key
        self.load_registered_usbs()
        
    def load_registered_usbs(self):
        """Load registered USB devices from the key file."""
        if KEY_FILE.exists():
            try:
                with open(KEY_FILE, 'rb') as f:
                    encrypted_data = f.read()
                    decrypted_data = self.decrypt_data(encrypted_data)
                    self.registered_usbs = eval(decrypted_data.decode())
            except Exception as e:
                logging.error(f"Error loading registered USBs: {e}")

    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using AES-256."""
        if not ENCRYPTION_KEY:
            raise ValueError("Encryption key not set")
        
        key = ENCRYPTION_KEY.encode().ljust(32)[:32]
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data, AES.block_size))
        return cipher.iv + ct_bytes

    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using AES-256."""
        if not ENCRYPTION_KEY:
            raise ValueError("Encryption key not set")
        
        key = ENCRYPTION_KEY.encode().ljust(32)[:32]
        iv = encrypted_data[:16]
        ct = encrypted_data[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(ct), AES.block_size)

    def get_usb_uuid(self, device_path: str) -> Optional[str]:
        """Get UUID of a USB device."""
        try:
            if self.system == 'linux':
                result = subprocess.run(['lsblk', '-o', 'UUID', device_path], 
                                     capture_output=True, text=True)
                return result.stdout.strip().split('\n')[1]
            elif self.system == 'windows':
                result = subprocess.run(['wmic', 'diskdrive', 'where', 
                                      f'DeviceID="{device_path}"', 'get', 'SerialNumber'],
                                     capture_output=True, text=True)
                return result.stdout.strip().split('\n')[1]
            elif self.system == 'darwin':
                result = subprocess.run(['diskutil', 'info', device_path],
                                     capture_output=True, text=True)
                for line in result.stdout.split('\n'):
                    if 'Disk / Partition UUID:' in line:
                        return line.split(':')[1].strip()
        except Exception as e:
            logging.error(f"Error getting USB UUID: {e}")
        return None

    def detect_usb_devices(self) -> List[str]:
        """Detect currently connected USB devices."""
        usb_devices = []
        for partition in psutil.disk_partitions():
            if any(drive_type in partition.opts.lower() for drive_type in ALLOWED_DRIVE_TYPES):
                usb_devices.append(partition.device)
        return usb_devices

    def verify_usb(self, device_path: str) -> bool:
        """Verify if a USB device is registered and valid."""
        uuid = self.get_usb_uuid(device_path)
        if not uuid:
            return False
        
        return uuid in self.registered_usbs

    def lock_system(self):
        """Lock the system using platform-specific commands."""
        try:
            command = SYSTEM_COMMANDS[self.system]['lock']
            subprocess.run(command.split())
            logging.info("System locked successfully")
        except Exception as e:
            logging.error(f"Error locking system: {e}")

    def unlock_system(self):
        """Unlock the system (implementation depends on OS)."""
        logging.info("System unlocked successfully")

    def monitor_usb_events(self):
        """Monitor USB insertion and removal events."""
        previous_devices = set(self.detect_usb_devices())
        
        while True:
            current_devices = set(self.detect_usb_devices())
            
            # Check for new devices
            new_devices = current_devices - previous_devices
            for device in new_devices:
                if self.verify_usb(device):
                    self.unlock_system()
                else:
                    logging.warning(f"Unauthorized USB device detected: {device}")
            
            # Check for removed devices
            removed_devices = previous_devices - current_devices
            if removed_devices:
                self.lock_system()
            
            previous_devices = current_devices
            time.sleep(SCAN_INTERVAL)

def main():
    try:
        detector = USBDetector()
        logging.info("Starting USB authentication service")
        detector.monitor_usb_events()
    except KeyboardInterrupt:
        logging.info("Service stopped by user")
    except Exception as e:
        logging.error(f"Service error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 