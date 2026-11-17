#!/bin/sh
# Writes the changes made in local/engine/ back into patches/, one patch per part of the engine.
# With --check, only reports whether patches/ is out of date (exit 1).
set -eu

MOD_SRC="$(cd "$(dirname "$0")/.." && pwd)"
IOQ3="$MOD_SRC/local/engine"
REV="$(sed -n 's/^IOQ3_REV=//p' "$MOD_SRC/build.sh")"
TMP="$(mktemp -d /tmp/wrecked-patches.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT
OUT="$TMP/patches"
mkdir "$OUT"

# file name and the engine paths it covers
PARTS="
01-collision-holes:code/qcommon cmake
02-server:code/server
03-game:code/game
04-cgame:code/cgame
05-client-crater-meshes:code/client
06-renderer:code/renderergl2 code/renderercommon code/sdl
"

# new files show up in the diff only once git knows about them; a copy of the index keeps local/engine/'s own untouched
cp "$IOQ3/.git/index" "$TMP/index"
export GIT_INDEX_FILE="$TMP/index"
git -C "$IOQ3" add --intent-to-add .
diff_engine() {
	git -C "$IOQ3" -c core.quotepath=off -c diff.noprefix=false -c diff.mnemonicPrefix=false \
		diff --no-color --no-ext-diff --no-renames --full-index "$REV" -- "$@"
}

echo "$PARTS" | while IFS=: read -r name paths; do
	[ -n "$name" ] || continue
	# shellcheck disable=SC2086
	diff_engine $paths > "$OUT/$name.patch"
	[ -s "$OUT/$name.patch" ] || rm -f "$OUT/$name.patch"
done
covered="$(echo "$PARTS" | cut -s -d: -f2)"
# shellcheck disable=SC2086
stray="$(git -C "$IOQ3" diff --name-only "$REV" -- . $(for p in $covered; do printf ':!%s ' "$p"; done))"
if [ -n "$stray" ]; then
	echo "Changed files outside every patch group, add them to PARTS in $0:" >&2
	echo "$stray" >&2
	exit 1
fi

if [ "${1:-}" = "--check" ]; then
	diff -r -q "$MOD_SRC/patches" "$OUT" > /dev/null
	exit
fi
mkdir -p "$MOD_SRC/patches"
rm -f "$MOD_SRC"/patches/*.patch
cp "$OUT"/*.patch "$MOD_SRC/patches/"
ls -l "$MOD_SRC"/patches/*.patch
