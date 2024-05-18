#!/bin/bash

echo "Installing required libraries..."
# Install required libraries
sudo apt-get update
sudo apt-get install -y python3-pandas python3-matplotlib python3-pyqt5 python3-numpy

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "Libraries installed successfully."
else
    echo "Error: Failed to install libraries."
    exit 1
fi

echo "Creating directory..."
# Create directory
mkdir -p /home/$(whoami)/mst_app

# Check if directory creation was successful
if [ $? -eq 0 ]; then
    echo "Directory created successfully."
else
    echo "Error: Failed to create directory."
    exit 1
fi

echo "Setup complete."


# Clone Program file at /ohmranger


echo "Copying .desktop file..."
# Copy .desktop file
cp /home/$(whoami)/mst_app/setup/mst_app.desktop ~/.local/share/applications/
# Check if copy was successful
if [ $? -eq 0 ]; then
    echo ".desktop file copied successfully."
else
    echo "Error: Failed to copy .desktop file."
    exit 1
fi

echo "Setting permissions..."
# Set permissions
chmod +x ~/.local/share/applications/mst_app.desktop
# Check if setting permissions was successful
if [ $? -eq 0 ]; then
    echo "Permissions set successfully."
else
    echo "Error: Failed to set permissions for .desktop file."
    exit 1
fi

echo "Setup complete."
# coppy .Desktop file for run application by desktop
#sudo cp /home/$(whoami)/mst_app/setup/mst_app.desktop ~/.local/share/applications/
#sudo chmod +x ~/.local/share/applications/mst_app.desktop