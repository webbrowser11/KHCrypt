# KHCrypt - USB-Based Authentication System

A secure, cross-platform USB authentication system that provides automatic system locking and unlocking based on USB drive presence.

## Features

- 🔐 Unique USB identification using UUID and encrypted key file
- 🔄 Automatic authentication on USB insertion
- 🔒 Auto-lock on USB removal
- 🌐 Cross-platform support (Windows, Linux, macOS)
- 🔑 Encrypted authentication keys
- 📝 Authentication logging
- 🔄 Multiple USB support

## Requirements

- Python 3.8 or higher
- Operating System: Windows, Linux, or macOS
- USB drive for authentication

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/KHCrypt.git
cd KHCrypt
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your USB drive:
```bash
python setup.py
```

## Usage

1. Run the authentication service:
```bash
python main.py
```

2. Insert your registered USB drive to unlock the system
3. Remove the USB drive to automatically lock the system

## Security Features

- AES-256 encryption for authentication keys
- UUID verification
- Hidden encrypted key file
- Authentication logging
- Multiple USB support for backup

## Configuration

Edit `config.py` to customize:
- Lock/unlock behavior
- Logging settings
- Security parameters

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please read CONTRIBUTING.md for details. 