#!/bin/bash

set -e  # Exit on error

ROOTFS_DIR=$HOME/ubuntu-rootfs
export PATH="$PATH:$HOME/.local/usr/bin"

ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
  PROOT_ARCH="x86_64"
elif [ "$ARCH" = "aarch64" ]; then
  PROOT_ARCH="aarch64"
elif [ "$ARCH" = "arm" ] || [ "$ARCH" = "armv7l" ]; then
  PROOT_ARCH="arm"
elif [ "$ARCH" = "i686" ]; then
  PROOT_ARCH="i686"
else
  echo "Unsupported architecture: $ARCH"
  exit 1
fi

# Download and setup PRoot for the detected architecture
if [ ! -e "$ROOTFS_DIR/usr/local/bin/proot" ]; then
  mkdir -p "$ROOTFS_DIR/usr/local/bin"
  wget -O "$ROOTFS_DIR/usr/local/bin/proot" "https://github.com/proot-me/proot/releases/download/v5.3.0/proot-v5.3.0-${PROOT_ARCH}-static"
  chmod 755 "$ROOTFS_DIR/usr/local/bin/proot"
fi

# Start Ubuntu in user-space using PRoot
"$ROOTFS_DIR/usr/local/bin/proot" \
  --rootfs="$ROOTFS_DIR" \
  -0 -w "/root" -b /dev -b /sys -b /proc -b /etc/resolv.conf --kill-on-exit \
  /bin/sh -c "apt-get update && \
  apt-get install -y python3-pip git ufw && \
  git clone https://github.com/bool-anony1764/Hello && \
  cd Hello && \
  g++ -std=c++14 soul.cpp -o soul -pthread && \
  pip install telebot pytz flask aiogram pymongo pyTelegramBotAPI python-telegram-bot motor && \
  python3 soul.py"
