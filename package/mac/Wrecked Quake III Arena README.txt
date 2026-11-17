Wrecked Quake III Arena (macOS)
by breakVanilla (https://breakvanilla.com, https://github.com/breakvanilla, youtube.com/@BreakVanilla)

Destructible walls for Quake III Arena: rockets blast craters into walls, other weapons chip, melt and bore into them, rubble piles up on the floor.

What you need
- Your own copy of Quake III Arena with the 1.32 point release: the baseq3 folder with pak0.pk3 through pak8.pk3. The Steam version already has them; a CD install needs the 1.32 point release first.
- macOS 11 or newer, Apple silicon or Intel.

Install
1. Copy everything from this folder into your Quake III Arena folder, next to baseq3.
2. Double-click "Play Wrecked Quake III Arena.command".
3. If macOS says it can't verify it, click "Done", open System Settings, Privacy & Security, scroll down, click "Open Anyway" next to it and confirm. Do the same if macOS then asks about "Wrecked Quake III Arena.app". If the game folder is in Downloads, Documents or Desktop, click "Allow" when asked.

Settings
Open the console with the ~ key or Shift+Esc and type:
- cg_destruction 0 to turn the effects off
- cg_shake 0 to turn the view shake off
- cg_rubbleTime N for the seconds rubble stays on the floor (25 by default)

Uninstall
Delete what you copied: "Wrecked Quake III Arena.app", "Play Wrecked Quake III Arena.command", the wrecked-quake-iii-arena folder, "Wrecked Quake III Arena README.txt" and LICENSE-ioquake3.txt. The game's own files are not changed. Settings are in ~/Library/Application Support/Quake3/wrecked-quake-iii-arena.

Problems
Type "logfile 2" in the console; from then on the game writes qconsole.log to ~/Library/Application Support/Quake3/wrecked-quake-iii-arena. Report problems at https://github.com/breakvanilla/quake-iii-arena-wrecked/issues.

License
The game runs on ioquake3 (https://ioquake3.org), changed for this mod, under the GNU GPL version 2 or later, see LICENSE-ioquake3.txt. Source code: https://github.com/breakvanilla/quake-iii-arena-wrecked
