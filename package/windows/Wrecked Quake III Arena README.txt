Wrecked Quake III Arena (Windows)
by breakVanilla (https://breakvanilla.com, https://github.com/breakvanilla, youtube.com/@BreakVanilla)

Destructible walls for Quake III Arena: rockets blast craters into walls, other weapons chip, melt and bore into them, rubble piles up on the floor.

What you need
- Your own copy of Quake III Arena with the 1.32 point release: the baseq3 folder with pak0.pk3 through pak8.pk3. The Steam version already has them; a CD install needs the 1.32 point release first.
- 64-bit Windows 10 or newer.

Where the game folder is
In Steam, right-click Quake III Arena, then Manage, Browse local files. Otherwise it is the folder you installed the game to, the one that holds baseq3.

Install
1. Copy everything from this folder into your Quake III Arena folder, next to baseq3.
2. Double-click "Play Wrecked Quake III Arena.bat".
3. If "Windows protected your PC" appears, click "More info", then "Run anyway".

Settings
Open the console with the ~ key or Shift+Esc and type:
- cg_destruction 0 to turn the effects off
- cg_shake 0 to turn the view shake off
- cg_rubbleTime N for the seconds rubble stays on the floor (25 by default)

Uninstall
Delete what you copied: "Wrecked Quake III Arena.exe", "Play Wrecked Quake III Arena.bat", renderer_opengl2.dll, SDL2.dll, the wrecked-quake-iii-arena folder, "Wrecked Quake III Arena README.txt" and LICENSE-ioquake3.txt. The game's own files are not changed. Settings are in %APPDATA%\Quake3\wrecked-quake-iii-arena.

Problems
Type "logfile 2" in the console; from then on the game writes qconsole.log to %APPDATA%\Quake3\wrecked-quake-iii-arena. Report problems at https://github.com/breakvanilla/quake-iii-arena-wrecked/issues.

License
The game runs on ioquake3 (https://ioquake3.org), changed for this mod, under the GNU GPL version 2 or later, see LICENSE-ioquake3.txt. Source code: https://github.com/breakvanilla/quake-iii-arena-wrecked
