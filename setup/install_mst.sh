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
mkdir -p /home/$(whoami)/mst_app/data
mkdir -p /home/$(whoami)/mst_app/analyze

# Check if directory creation was successful
if [ $? -eq 0 ]; then
    echo "Directory created successfully."
else
    echo "Error: Failed to create directory."
    exit 1
fi


echo "Setup complete."

echo " coppy udev rules"

sudo cp /home/$(whoami)/mst_app/setup/mst.rules /etc/udev/rules.d/


# Clone Program file at /ohmranger


echo "Copying .desktop file..."
sudo scp /home/mst/mst_app/splash.png /usr/share/plymouth/themes/pix/splash.png
# Copy .desktop file
cp /home/$(whoami)/mst_app/setup/mst_app.desktop /home/$(whoami)/Desktop
# Check if copy was successful
if [ $? -eq 0 ]; then
    echo ".desktop file copied successfully."
else
    echo "Error: Failed to copy .desktop file."
    exit 1
fi

echo "Setting permissions..."
# Set permissions
chmod +x /home/$(whoami)/Desktop/mst_app.desktop
# Check if setting permissions was successful
if [ $? -eq 0 ]; then
    echo "Permissions set successfully."
else
    echo "Error: Failed to set permissions for .desktop file."
    exit 1
fi

# Install Services Mst_app
echo "Install Services App"
# create environment file
source ~/.bashrc 
bash --login -c 'env > ~/mst_app/setup/services/mst.env' 
sudo cp /home/$(whoami)/mst_app/setup/services/mst.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mst.service

echo "Setup complete."
echo "Reboot Now"
sleep 5
sudo reboot

# coppy .Desktop file for run application by desktop
#sudo cp /home/$(whoami)/mst_app/setup/mst_app.desktop ~/.local/share/applications/
#sudo chmod +x ~/.local/share/applications/mst_app.desktop
