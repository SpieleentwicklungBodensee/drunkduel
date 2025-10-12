#!/bin/bash

# Local build script for creating Kazeta cart image
# Usage: ./build_cart.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Building Drunk Duel Kazeta Cart..."
echo "=================================="

# Check if running as root for mounting
if [[ $EUID -eq 0 ]]; then
   echo "Please don't run this script as root. It will ask for sudo when needed."
   exit 1
fi

# Check dependencies
check_dependency() {
    if ! command -v "$1" &> /dev/null; then
        echo "Error: $1 is not installed. Please install it first."
        echo "On Ubuntu/Debian: sudo apt-get install $2"
        exit 1
    fi
}

echo "Checking dependencies..."
check_dependency "python3" "python3"
check_dependency "pip3" "python3-pip"
check_dependency "mkfs.ext4" "e2fsprogs"
check_dependency "dd" "coreutils"

# Configuration
CART_SIZE_MB=512
IMG_FILE="drunk_duel_cart.img"
CART_LABEL="DRUNKDUEL"

# Clean up any previous builds
echo "Cleaning up previous builds..."
rm -f "$IMG_FILE" "$IMG_FILE.gz"

# Install Python dependencies if needed
echo "Checking Python dependencies..."
if ! python3 -c "import pygame" 2>/dev/null; then
    echo "Installing pygame..."
    pip3 install --user pygame
fi

# Check if required static files exist
echo "Checking required static files..."
if [ ! -f "cart_icon.png" ]; then
    echo "ERROR: cart_icon.png not found. Please ensure the icon file is present."
    exit 1
fi
echo "✓ Using existing cart_icon.png"

if [ ! -f "drunk_duel.kzi" ]; then
    echo "ERROR: drunk_duel.kzi not found. Please ensure the Kazeta info file is present."
    exit 1
fi
echo "✓ Using existing drunk_duel.kzi"

if [ ! -f "python_runtime" ]; then
    echo "ERROR: python_runtime not found. Please ensure the runtime script is present."
    exit 1
fi
echo "✓ Using existing python_runtime"

# Make python_runtime executable
chmod +x python_runtime

# Create cart image
echo "Creating cart image ($CART_SIZE_MB MB)..."
dd if=/dev/zero of="$IMG_FILE" bs=1M count=$CART_SIZE_MB

echo "Creating ext4 filesystem..."
mkfs.ext4 -F -L "$CART_LABEL" "$IMG_FILE"

# Mount the image
echo "Mounting image for file copying..."
MOUNT_DIR=$(mktemp -d)
sudo mount -o loop "$IMG_FILE" "$MOUNT_DIR"

# Ensure we unmount on exit
trap "sudo umount '$MOUNT_DIR' 2>/dev/null || true; rmdir '$MOUNT_DIR' 2>/dev/null || true" EXIT

# Create content directory
echo "Creating content directory..."
sudo mkdir -p "$MOUNT_DIR/content"

# Copy game files to content directory
echo "Copying game files..."
sudo cp -r . "$MOUNT_DIR/content/"

# Remove unnecessary files from content
echo "Cleaning up unnecessary files..."
sudo rm -rf "$MOUNT_DIR/content/.git" 2>/dev/null || true
sudo rm -rf "$MOUNT_DIR/content/.github" 2>/dev/null || true
sudo rm -rf "$MOUNT_DIR/content/__pycache__" 2>/dev/null || true
sudo rm -rf "$MOUNT_DIR/content/env" 2>/dev/null || true
sudo rm -f "$MOUNT_DIR/content/"*.img 2>/dev/null || true
sudo rm -f "$MOUNT_DIR/content/"*.kzi 2>/dev/null || true
sudo rm -f "$MOUNT_DIR/content/python_runtime" 2>/dev/null || true
sudo rm -f "$MOUNT_DIR/content/build_cart.sh" 2>/dev/null || true
# cart_icon.png stays in content as a game asset

# Copy runtime and kzi file to root
echo "Installing cart files to root..."
sudo cp python_runtime "$MOUNT_DIR/"
sudo cp drunk_duel.kzi "$MOUNT_DIR/"
sudo cp cart_icon.png "$MOUNT_DIR/"

# Set proper permissions
echo "Setting permissions..."
sudo chmod +x "$MOUNT_DIR/python_runtime"
sudo chmod -R 755 "$MOUNT_DIR/content"

# Unmount
echo "Unmounting image..."
sudo umount "$MOUNT_DIR"
rmdir "$MOUNT_DIR"

# Trap cleanup is no longer needed
trap - EXIT

echo "Cart image created: $IMG_FILE"
ls -lh "$IMG_FILE"

# Compress the cart image
echo "Compressing cart image..."
gzip -9 "$IMG_FILE"

echo "Compressed cart image created: $IMG_FILE.gz"
ls -lh "$IMG_FILE.gz"

# Generate checksums
echo "Generating checksums..."
sha256sum "$IMG_FILE.gz" > "$IMG_FILE.gz.sha256"
md5sum "$IMG_FILE.gz" > "$IMG_FILE.gz.md5"

echo ""
echo "Build completed successfully!"
echo "=========================="
echo "Files created:"
echo "- $IMG_FILE.gz (cart image)"
echo "- $IMG_FILE.gz.sha256 (SHA256 checksum)"
echo "- $IMG_FILE.gz.md5 (MD5 checksum)"
echo "- drunk_duel.kzi (cart info)"
echo "- cart_icon.png (cart icon)"
echo ""
echo "To flash to SD card:"
echo "1. Decompress: gunzip $IMG_FILE.gz"
echo "2. Flash: sudo dd if=$IMG_FILE of=/dev/sdX bs=4M status=progress"
echo "   (replace /dev/sdX with your SD card device)"
echo ""
echo "CAUTION: Double-check the device path before flashing!"