import os
import sys
import logging
from pathlib import Path
from typing import Dict, Optional

from main import USBDetector

def generate_encryption_key() -> str:
    """Generate a secure encryption key."""
    return os.urandom(32).hex()

def save_encryption_key(key: str):
    """Save the encryption key to .env file."""
    env_path = Path('.env')
    if not env_path.exists():
        with open(env_path, 'w') as f:
            f.write(f'KHCRYPT_KEY={key}\n')
        print("Encryption key generated and saved to .env file")
    else:
        print("Encryption key already exists in .env file")

def register_usb(device_path: str, detector: USBDetector) -> bool:
    """Register a new USB device."""
    uuid = detector.get_usb_uuid(device_path)
    if not uuid:
        print(f"Could not get UUID for device: {device_path}")
        return False
    
    # Generate a unique key for this USB
    key = os.urandom(16).hex()
    
    # Load existing registered USBs
    registered_usbs: Dict[str, str] = {}
    if KEY_FILE.exists():
        try:
            with open(KEY_FILE, 'rb') as f:
                encrypted_data = f.read()
                decrypted_data = detector.decrypt_data(encrypted_data)
                registered_usbs = eval(decrypted_data.decode())
        except Exception as e:
            logging.error(f"Error loading registered USBs: {e}")
    
    # Add new USB
    registered_usbs[uuid] = key
    
    # Save updated list
    try:
        encrypted_data = detector.encrypt_data(str(registered_usbs).encode())
        with open(KEY_FILE, 'wb') as f:
            f.write(encrypted_data)
        print(f"Successfully registered USB device: {device_path}")
        print(f"UUID: {uuid}")
        print(f"Key: {key}")
        return True
    except Exception as e:
        print(f"Error registering USB: {e}")
        return False

def list_usb_devices(detector: USBDetector):
    """List all available USB devices."""
    devices = detector.detect_usb_devices()
    if not devices:
        print("No USB devices found")
        return
    
    print("\nAvailable USB devices:")
    for i, device in enumerate(devices, 1):
        uuid = detector.get_usb_uuid(device)
        status = "Registered" if uuid in detector.registered_usbs else "Unregistered"
        print(f"{i}. {device} - {status}")

def main():
    # Configure logging
    logging.basicConfig(
        filename=LOG_FILE,
        level=getattr(logging, 'INFO'),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Check for encryption key
    if not ENCRYPTION_KEY:
        key = generate_encryption_key()
        save_encryption_key(key)
    
    detector = USBDetector()
    
    while True:
        print("\nKHCrypt USB Authentication Setup")
        print("1. List USB devices")
        print("2. Register new USB")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            list_usb_devices(detector)
        elif choice == '2':
            list_usb_devices(detector)
            device_num = input("\nEnter the number of the USB to register (or 'c' to cancel): ")
            if device_num.lower() == 'c':
                continue
            
            try:
                device_num = int(device_num)
                devices = detector.detect_usb_devices()
                if 1 <= device_num <= len(devices):
                    register_usb(devices[device_num - 1], detector)
                else:
                    print("Invalid device number")
            except ValueError:
                print("Please enter a valid number")
        elif choice == '3':
            print("Setup complete. You can now run main.py to start the authentication service.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 