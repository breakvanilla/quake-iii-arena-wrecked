#!/bin/sh
set -eu

MOD_SRC="$(cd "$(dirname "$0")" && pwd)"
IOQ3="$MOD_SRC/local/engine"
MOD="wrecked-quake-iii-arena"
INSTALL_DIR="$HOME/Library/Application Support/Quake3/$MOD"
STAGE="$(mktemp -d /tmp/$MOD-stage.XXXXXX)"
trap 'rm -rf "$STAGE"' EXIT
IOQ3_REV=87a99d18206e878a20289f05ac3c16005dcae5c3

# local/engine/ is upstream ioquake3 at IOQ3_REV with patches/ on top
if [ ! -d "$IOQ3/.git" ]; then
	git clone https://github.com/ioquake/ioq3 "$IOQ3"
	git -C "$IOQ3" checkout -q "$IOQ3_REV"
	git -C "$IOQ3" apply -q --3way "$MOD_SRC"/patches/*.patch
fi
"$MOD_SRC/tools/update-patches.sh" --check || echo "Note: local/engine/ has changes not in patches/ yet, run tools/update-patches.sh"

# the prefix map keeps this checkout's path out of the binaries' __FILE__ strings
cmake -S "$IOQ3" -B "$IOQ3/build" -Wno-dev -DCMAKE_C_FLAGS="-ffile-prefix-map=$IOQ3/=" \
	-DBUILD_SERVER=ON -DBUILD_CLIENT=ON -DBUILD_RENDERER_GL1=OFF -DBUILD_RENDERER_GL2=ON \
	-DBUILD_GAME_LIBRARIES=OFF -DBUILD_GAME_QVMS=ON > /dev/null
# the qvm rules don't track header or source changes reliably, so always recompile them
rm -f "$IOQ3"/build/qvm.dir/*/*.asm
cmake --build "$IOQ3/build" -j 8 --target \
	ioquake3 renderer_opengl2 ioq3ded cgameqvm_baseq3 qagameqvm_baseq3 uiqvm_baseq3

mkdir -p "$STAGE/vm" "$STAGE/scripts"
command cp -f "$IOQ3"/build/Release/baseq3/vm/cgame.qvm "$IOQ3"/build/Release/baseq3/vm/qagame.qvm \
	"$IOQ3"/build/Release/baseq3/vm/ui.qvm "$STAGE/vm/"
command cp -f "$MOD_SRC"/scripts/*.shader "$STAGE/scripts/"
python3 -I "$MOD_SRC/tools/gen_textures.py" "$STAGE"
python3 -I "$MOD_SRC/tools/gen_chunks.py" "$STAGE"
python3 -I "$MOD_SRC/tools/gen_sounds.py" "$STAGE"

mkdir -p "$INSTALL_DIR"
rm -f "$INSTALL_DIR/$MOD.pk3"
(cd "$STAGE" && zip -qrX "$INSTALL_DIR/$MOD.pk3" vm scripts gfx models sound)

# settings carry over from the plain game
if [ ! -f "$INSTALL_DIR/q3config.cfg" ] && [ -f "$INSTALL_DIR/../baseq3/q3config.cfg" ]; then
	command cp "$INSTALL_DIR/../baseq3/q3config.cfg" "$INSTALL_DIR/"
fi

echo "Installed $INSTALL_DIR/$MOD.pk3"
ls -la "$IOQ3"/build/Release/baseq3/vm/cgame.qvm "$IOQ3"/build/Release/baseq3/vm/qagame.qvm
find "$IOQ3/build/Release" -maxdepth 4 \( -name ioquake3 -o -name 'renderer_opengl2*' \) -type f -exec ls -la {} \;
