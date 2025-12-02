#!/usr/bin/env bash
set -euo pipefail

APP_NAME="PDF Split"
APP_BUNDLE="dist/$APP_NAME.app"
DMG_NAME="${APP_NAME// /}_Unsigned.dmg"
STAGE_DIR="build/.dmg-stage"

if [[ ! -d "$APP_BUNDLE" ]]; then
  echo "App bundle not found: $APP_BUNDLE" >&2
  exit 1
fi

rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR"
cp -R "$APP_BUNDLE" "$STAGE_DIR/"
ln -s /Applications "$STAGE_DIR/Applications"
rm -f "$DMG_NAME"
hdiutil create "$DMG_NAME" -volname "$APP_NAME" -fs HFS+ -srcfolder "$STAGE_DIR"
echo "Created $DMG_NAME"
