#!/bin/sh
cd "$(dirname "$0")"
# the first launch opens in a window, so macOS's network prompt can be clicked; full screen is in Setup, System
if [ ! -f "$HOME/Library/Application Support/Quake3/wrecked-quake-iii-arena/q3config.cfg" ]; then
	set -- +set r_fullscreen 0 +set r_mode -1 +set r_customwidth 1280 +set r_customheight 720 "$@"
fi
# fs_basepath: macOS may run the app from a hidden copy elsewhere, away from baseq3
open -n "Wrecked Quake III Arena.app" --args +set fs_basepath "$PWD" +set fs_game wrecked-quake-iii-arena "$@"
