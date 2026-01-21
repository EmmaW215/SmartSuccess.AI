#!/bin/bash
# Install Systemd Service for SmartSuccess.AI GPU Backend

echo "=========================================="
echo "Installing Systemd Service"
echo "=========================================="
echo ""

SERVICE_FILE="smartsuccess-gpu.service"
SYSTEMD_PATH="/etc/systemd/system/smartsuccess-gpu.service"
CURRENT_DIR="$(pwd)"

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo "❌ Error: $SERVICE_FILE not found in current directory"
    exit 1
fi

echo "1. Copying service file to systemd..."
echo "   Source: $CURRENT_DIR/$SERVICE_FILE"
echo "   Destination: $SYSTEMD_PATH"
echo ""

# Copy service file (requires sudo)
sudo cp "$SERVICE_FILE" "$SYSTEMD_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Service file copied successfully"
else
    echo "❌ Failed to copy service file (check sudo permissions)"
    exit 1
fi

echo ""
echo "2. Reloading systemd daemon..."
sudo systemctl daemon-reload

if [ $? -eq 0 ]; then
    echo "✅ Systemd daemon reloaded"
else
    echo "❌ Failed to reload daemon"
    exit 1
fi

echo ""
echo "3. Enabling service..."
sudo systemctl enable smartsuccess-gpu.service

if [ $? -eq 0 ]; then
    echo "✅ Service enabled (will start on boot)"
else
    echo "❌ Failed to enable service"
    exit 1
fi

echo ""
echo "4. Starting service..."
sudo systemctl start smartsuccess-gpu.service

if [ $? -eq 0 ]; then
    echo "✅ Service started"
else
    echo "❌ Failed to start service"
    echo "   Check logs with: sudo journalctl -u smartsuccess-gpu -n 50"
    exit 1
fi

echo ""
echo "5. Checking service status..."
sleep 2
sudo systemctl status smartsuccess-gpu.service --no-pager

echo ""
echo "=========================================="
echo "✅ Systemd service installed successfully!"
echo "=========================================="
echo ""
echo "Useful commands:"
echo "  Status:    sudo systemctl status smartsuccess-gpu"
echo "  Start:     sudo systemctl start smartsuccess-gpu"
echo "  Stop:      sudo systemctl stop smartsuccess-gpu"
echo "  Restart:   sudo systemctl restart smartsuccess-gpu"
echo "  Logs:      sudo journalctl -u smartsuccess-gpu -f"
echo "  Enable:    sudo systemctl enable smartsuccess-gpu"
echo "  Disable:   sudo systemctl disable smartsuccess-gpu"
