# CodeLogger 2.0 - Advanced Monitoring Tool

![HEADER](src/codelogger.jpg)

CodeLogger 2.0 is a comprehensive monitoring tool that records keystrokes, captures screenshots, monitors clipboard activity, gathers system information, and sends reports via email. The tool uses encryption to secure collected data.

> **DISCLAIMER**: This tool is for educational and legitimate security testing purposes only. Unauthorized monitoring of computers or devices without consent is illegal in most jurisdictions. Always obtain proper authorization before deployment.

## Features

- 🔑 **Keylogging**: Records all keyboard input
- 📸 **Screenshot Capture**: Periodically captures screen images
- 📋 **Clipboard Monitoring**: Tracks clipboard content changes
- 🖥️ **System Information**: Collects hardware, network, and user details
- 📧 **Email Reporting**: Automatically sends collected data to specified email
- 🔒 **Encryption**: Secures logged data with PBKDF2 and Fernet encryption
- ⏱️ **Scheduling**: Configurable intervals for data collection and reporting
- 📊 **HTML Reports**: Creates beautiful HTML and text reports
- 🧙‍♂️ **Configuration Wizard**: Easy setup with interactive prompts
- 💻 **Command Line Interface**: Powerful CLI options for flexibility

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Folder Structure](#folder-structure)
- [Precautions](#precautions)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

- Python 3.6+
- Required Python packages (see requirements.txt)

## Installation

```bash
# Clone the repository
git clone https://github.com/karthik558/CodeLogger.git

# Navigate to the project directory
cd CodeLogger

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the main program
python CodeLogger.py

# Run with configuration wizard
python CodeLogger.py --config

# Generate a report without starting monitoring
python CodeLogger.py --report-only

# Check the status of CodeLogger services
python CodeLogger.py --status

# Decrypt a file encrypted by CodeLogger
python CodeLogger.py --decrypt path/to/encrypted_file

# Show version information
python CodeLogger.py --version
```

# To stop the program
Press Ctrl+C in the terminal or Ctrl+Z (Command+Z on macOS) while typing

## Folder Structure

When running CodeLogger, the following folder structure will be created:

```
CodeLogger/
├── CodeLogger.py
├── config.json          # Configuration file
├── output/              # Main output directory
│   ├── codelogger.log   # Log file for program operations
│   ├── key.txt          # Keylog storage
│   ├── clipboard_history.txt # Clipboard monitoring storage
│   ├── screenshots/     # Directory for captured screenshots
│   │   └── screenshot_YYYYMMDD_HHMMSS.png
│   ├── system_info/     # Directory for system information
│   │   └── system_info_YYYYMMDD_HHMMSS.json
│   └── reports/         # Directory for generated reports
│       ├── report_YYYYMMDD_HHMMSS.html
│       └── report_YYYYMMDD_HHMMSS.txt
```

## Precautions

- Always obtain proper authorization before deploying this tool
- When using the email functionality, it's recommended to use app-specific passwords
- Change the default encryption password and salt in the configuration
- Be aware of privacy laws and regulations in your jurisdiction

## Contributing

Contributions to the project are welcome. Please feel free to submit a pull request or open an issue to suggest improvements or report bugs.

## License

This project is licensed under the [MIT License](LICENSE).