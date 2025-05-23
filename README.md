<div align="center">
<img src="https://raw.githubusercontent.com/FoORK-Lab/pass-gen-dependencies/refs/heads/main/CodeLogger.png" alt="CodeLogger 2.0 Logo" width="500" style="border-radius: 15px;"/>

### 🔐 Advanced Security Monitoring Tool 🔍

[![GitHub license](https://img.shields.io/github/license/karthik558/CodeLogger?color=blue&style=for-the-badge)](LICENSE)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg?style=for-the-badge)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/karthik558/CodeLogger/pulls)
[![Last Updated](https://img.shields.io/badge/last%20updated-May%202025-orange)](https://github.com/karthik558/CodeLogger)

</div>

## Overview

CodeLogger 2.0 is a comprehensive security monitoring tool that records keystrokes, captures screenshots, monitors clipboard activity, gathers system information, and sends reports via email. The tool uses advanced encryption to secure collected data.

> ⚠️ **DISCLAIMER**: This tool is for educational and legitimate security testing purposes only. Unauthorized monitoring of computers or devices without consent is illegal in most jurisdictions. Always obtain proper authorization before deployment.

## Key Features

<table>
  <tr>
    <td width="50%">
      <h3>Monitoring Capabilities</h3>
      <ul>
        <li>🔑 <b>Keylogging</b>: Records all keyboard input</li>
        <li>📸 <b>Screenshot Capture</b>: Periodically captures screen images</li>
        <li>📋 <b>Clipboard Monitoring</b>: Tracks clipboard content changes</li>
        <li>🖥️ <b>System Information</b>: Collects hardware, network, and user details</li>
      </ul>
    </td>
    <td width="50%">
      <h3>Advanced Features</h3>
      <ul>
        <li>📧 <b>Email Reporting</b>: Automatically sends collected data to specified email</li>
        <li>🔒 <b>Encryption</b>: Secures logged data with PBKDF2 and Fernet encryption</li>
        <li>⏱️ <b>Scheduling</b>: Configurable intervals for data collection and reporting</li>
        <li>📊 <b>HTML Reports</b>: Creates beautiful HTML and text reports</li>
        <li>🧙‍♂️ <b>Configuration Wizard</b>: Easy setup with interactive prompts</li>
        <li>💻 <b>Command Line Interface</b>: Powerful CLI options for flexibility</li>
      </ul>
    </td>
  </tr>
</table>

## Table of Contents

<details open>
  <summary>Click to expand/collapse</summary>
  <ol>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#folder-structure">Folder Structure</a></li>
    <li><a href="#precautions">Precautions</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

## Prerequisites

<details>
  <summary><b>Required Software & Dependencies</b></summary>
  
  * **Python 3.6 or higher**
  * **Required Python Packages** (automatically installed via requirements.txt):
    * pynput - For keyboard monitoring
    * pillow - For screenshot capabilities
    * cryptography - For encryption functions
    * requests - For API communication
    * psutil - For system information collection
</details>

## Installation

<details>
  <summary><b>Step-by-Step Installation Guide</b></summary>

```bash
# Clone the repository
git clone https://github.com/karthik558/CodeLogger.git

# Navigate to the project directory
cd CodeLogger

# Install dependencies
pip install -r requirements.txt
```

> **Note**: For macOS users, you may need to grant additional permissions for the tool to function properly.

</details>

## Usage

<details>
  <summary><b>Command Line Options</b></summary>
  
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
</details>

<details>
  <summary><b>Running the Program</b></summary>
  
  1. Configure the tool using the configuration wizard:
     ```bash
     python CodeLogger.py --config
     ```
  
  2. Start monitoring:
     ```bash
     python CodeLogger.py
     ```
     
  3. To stop the program:
     - Press `Ctrl+C` in the terminal 
     - Or `Ctrl+Z` (`Command+Z` on macOS) while typing
</details>

## Folder Structure

<details>
  <summary><b>Project Directory Organization</b></summary>

  When running CodeLogger, the following folder structure will be created:

  ```
  CodeLogger/
  ├── CodeLogger.py      # Main executable script
  ├── config.json        # Configuration file
  ├── output/            # Main output directory
  │   ├── codelogger.log # Log file for program operations
  │   ├── key.txt        # Keylog storage
  │   ├── clipboard_history.txt # Clipboard monitoring storage
  │   ├── screenshots/   # Directory for captured screenshots
  │   │   └── screenshot_YYYYMMDD_HHMMSS.png
  │   ├── system_info/   # Directory for system information
  │   │   └── system_info_YYYYMMDD_HHMMSS.json
  │   └── reports/       # Directory for generated reports
  │       ├── report_YYYYMMDD_HHMMSS.html
  │       └── report_YYYYMMDD_HHMMSS.txt
  ├── src/               # Source assets
  │   └── codelogger.jpg # Project logo
  └── requirements.txt   # Python dependencies
  ```
</details>

## Precautions

<div class="warning" style="padding: 10px; background-color: #161b22; border-left: 4px solid #FF9800; margin-bottom: 10px;">
  <p><strong>Important Security and Legal Considerations:</strong></p>
  <ul>
    <li>✅ Always obtain proper authorization before deploying this tool</li>
    <li>🔑 When using the email functionality, it's recommended to use app-specific passwords</li>
    <li>🔄 Change the default encryption password and salt in the configuration</li>
    <li>⚖️ Be aware of privacy laws and regulations in your jurisdiction</li>
    <li>🚫 Never use this tool for malicious purposes or unauthorized surveillance</li>
  </ul>
</div>

## Contributing

  <summary><b>How to Contribute</b></summary>
  
  We welcome contributions to CodeLogger! Here's how you can help:
  
  1. **Fork** the repository
  2. **Create a branch** for your feature: `git checkout -b feature/amazing-feature`
  3. **Commit** your changes: `git commit -m 'Add some amazing feature'`
  4. **Push** to your branch: `git push origin feature/amazing-feature`
  5. Open a **Pull Request**
  
  For bug reports, feature requests, or feedback, please open an **Issue**.

## License

  <summary><b>MIT License Terms</b></summary>
  
  This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.
  
  Copyright (c) 2025 CodeLogger Contributors

---

<div align="center">
  <p>Made with ❤️ by <a href="https://karthiklal.in">KARTHIK LAL</a></p>
    <p>
      <a href="https://github.com/karthik558/CodeLogger/issues">Report Bug</a> •
      <a href="https://github.com/karthik558/CodeLogger/issues">Request Feature</a>
    </p>
</div>