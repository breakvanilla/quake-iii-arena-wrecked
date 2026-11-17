#!/bin/sh
# Packs the built game and mod into a zip that players unpack into their Quake III Arena folder
set -eu

MOD_SRC="$(cd "$(dirname "$0")" && pwd)"
IOQ3="$MOD_SRC/local/engine"
MOD="wrecked-quake-iii-arena"
NAME="Wrecked Quake III Arena"
PK3="$HOME/Library/Application Support/Quake3/$MOD/$MOD.pk3"
OUT="$MOD_SRC/local/dist/$MOD-mac.zip"
STAGE="$(mktemp -d /tmp/$MOD-dist.XXXXXX)"
trap 'rm -rf "$STAGE"' EXIT

PKG="$STAGE/$NAME"
mkdir -p "$PKG/$MOD"
ditto "$IOQ3/build/Release/ioquake3.app" "$PKG/$NAME.app"
# its own identity, so macOS keeps it apart from a plain ioquake3, and quake3:// links stay with that one
PLIST="$PKG/$NAME.app/Contents/Info.plist"
plutil -replace CFBundleIdentifier -string "com.breakvanilla.$MOD" "$PLIST"
plutil -replace CFBundleName -string "$NAME" "$PLIST"
plutil -remove CFBundleURLTypes "$PLIST"
codesign --force --deep -s - "$PKG/$NAME.app" 2>/dev/null
command cp "$PK3" "$PKG/$MOD/"
command cp "$IOQ3/COPYING.txt" "$PKG/LICENSE-ioquake3.txt"

# the launcher and README players get are in package/mac
command cp "$MOD_SRC/package/mac/"* "$PKG/"

mkdir -p "$(dirname "$OUT")"
rm -f "$OUT"
(cd "$STAGE" && ditto -c -k --norsrc --noextattr --noqtn --keepParent "$NAME" "$OUT")
echo "Packed $OUT"
