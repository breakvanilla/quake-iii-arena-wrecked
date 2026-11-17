#!/bin/sh
# Cross-builds the game for 64-bit Windows and packs it with the mod into a zip that players unpack into their Quake III Arena folder
set -eu

MOD_SRC="$(cd "$(dirname "$0")" && pwd)"
IOQ3="$MOD_SRC/local/engine"
BUILD="$IOQ3/build-win64"
MOD="wrecked-quake-iii-arena"
NAME="Wrecked Quake III Arena"
PK3="$HOME/Library/Application Support/Quake3/$MOD/$MOD.pk3"
OUT="$MOD_SRC/local/dist/$MOD-windows.zip"
STAGE="$(mktemp -d /tmp/$MOD-win.XXXXXX)"
trap 'rm -rf "$STAGE"' EXIT

cmake -S "$IOQ3" -B "$BUILD" -Wno-dev -DCMAKE_TOOLCHAIN_FILE="$MOD_SRC/mingw-w64.cmake" -DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_C_FLAGS="-ffile-prefix-map=$IOQ3/=" \
	-DBUILD_SERVER=ON -DBUILD_CLIENT=ON -DBUILD_RENDERER_GL1=OFF -DBUILD_RENDERER_GL2=ON \
	-DBUILD_GAME_LIBRARIES=OFF -DBUILD_GAME_QVMS=OFF > /dev/null
cmake --build "$BUILD" -j 8 --target ioquake3 renderer_opengl2 ioq3ded

PKG="$STAGE/$NAME"
mkdir -p "$PKG/$MOD"
command cp "$BUILD/Release/ioquake3.exe" "$PKG/$NAME.exe"
command cp "$BUILD/Release/renderer_opengl2.dll" "$BUILD/Release/SDL2.dll" "$PKG/"
command cp "$PK3" "$PKG/$MOD/"
command cp "$IOQ3/COPYING.txt" "$PKG/LICENSE-ioquake3.txt"

# the launcher and README players get are in package/windows, with Windows line ends
for f in "$MOD_SRC/package/windows/"*; do
	sed 's/$/\r/' "$f" > "$PKG/$(basename "$f")"
done

mkdir -p "$(dirname "$OUT")"
rm -f "$OUT"
(cd "$STAGE" && zip -qrX "$OUT" "$NAME")
echo "Packed $OUT"
