#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Ensure the script is running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root"
    exit 1
fi

# Update package list and install dependencies
echo "Updating package list and installing dependencies..."
apt-get update
apt-get install -y python3 python3-pip sqlite3 git

# Install Tkinter for GUI support
echo "Installing Tkinter..."
apt-get install -y python3-tk

# Clone the repository if it doesn't exist
if [ ! -d "SQLiteTrim" ]; then
    echo "Cloning the repository..."
    git clone https://github.com/g3ntrix/SQLiteTrim.git
fi

cd SQLiteTrim

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Run the main script
echo "Running the SQLiteTrim tool..."
python3 sqlite_trim.py
