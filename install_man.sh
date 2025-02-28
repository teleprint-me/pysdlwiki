#!/bin/bash

INSTALL_DIR="/usr/local/share/man/man3"
SRC_DIR="output/man"

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit
fi

case "$1" in
    install)
        echo "Installing SDL Wiki Man pages..."
        mkdir -pv "$INSTALL_DIR"
        cp -v "$SRC_DIR"/SDL_*.3.gz "$INSTALL_DIR"
        mandb
        echo "Installation complete."
        ;;
    uninstall)
        echo "Uninstalling SDL Wiki Man pages..."
        rm -v "$INSTALL_DIR"/SDL_*.3.gz
        mandb
        echo "Uninstallation complete."
        ;;
    *)
        echo "Usage: $0 {install|uninstall}"
        exit 1
        ;;
esac
