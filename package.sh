#!/bin/sh
printf "run package..."

CURR_DIR="$(dirname "$(readlink -f "$0")")"
printf "\nCURR_DIR=%s" "$CURR_DIR"

printf "\nclean-up build artifacts..."
rm -rv "$CURR_DIR/build"
rm -rv "$CURR_DIR/dist"
rm -rv "$CURR_DIR/lnxngfmsdm_gui.spec"

printf "\ncompile binary..."
pyinstaller --onefile --add-data 'images:images' lnxngfmsdm_gui.py

printf "\ncopy binary..."
cp -v "$CURR_DIR/dist/lnxngfmsdm_gui" "$CURR_DIR/lnxngfmsdm.AppDir/usr/bin"

printf "\npackage binary..."
ARCH=x86_64 tools/appimagetool-x86_64.AppImage lnxngfmsdm.AppDir
