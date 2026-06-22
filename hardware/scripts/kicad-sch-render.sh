#!/usr/bin/env bash
# kicad-sch-render — render schematic sheet(s) to PNG for quick visual review.
#
#   scripts/kicad-sch-render.sh <file.kicad_sch> [sheet-name ...]
#
# Exports the given .kicad_sch to SVG via kicad-cli and converts each SVG to a
# PNG (first available of rsvg-convert / inkscape / cairosvg / macOS qlmanage).
# With no sheet names, every produced SVG is converted. Prints the PNG paths.
#
# Pass a CHILD .kicad_sch to render just that one sheet; pass the ROOT to render
# the whole project (one SVG per sheet). Output goes to a temp dir (override with
# $RENDER_OUT). kicad-cli is located via $KICAD_CLI, then PATH, then the macOS
# app bundle.
set -euo pipefail

[ $# -ge 1 ] || { echo "usage: kicad-sch-render.sh <file.kicad_sch> [sheet-name ...]" >&2; exit 1; }
SCH="$1"; shift
[ -f "$SCH" ] || { echo "kicad-sch-render: no such file: $SCH" >&2; exit 1; }

find_cli() {
  if [ -n "${KICAD_CLI:-}" ] && command -v "$KICAD_CLI" >/dev/null 2>&1; then echo "$KICAD_CLI"; return; fi
  if command -v kicad-cli >/dev/null 2>&1; then echo kicad-cli; return; fi
  for c in /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli /usr/bin/kicad-cli /usr/local/bin/kicad-cli; do
    [ -x "$c" ] && { echo "$c"; return; }
  done
  echo "kicad-sch-render: kicad-cli not found (set \$KICAD_CLI)" >&2; exit 1
}
CLI="$(find_cli)"

base="$(basename "${SCH%.kicad_sch}")"
OUT="${RENDER_OUT:-${TMPDIR:-/tmp}/kicad-render/$base}"
rm -rf "$OUT"; mkdir -p "$OUT"

"$CLI" sch export svg --output "$OUT" "$SCH" >/dev/null

# select which SVGs to convert (bash 3.2 compatible — macOS ships bash 3.2)
SVGS=()
for s in "$OUT"/*.svg; do [ -e "$s" ] && SVGS+=("$s"); done
if [ $# -gt 0 ]; then
  sel=(); for name in "$@"; do
    for s in "${SVGS[@]}"; do case "$s" in *"$name"*.svg) sel+=("$s");; esac; done
  done
  SVGS=("${sel[@]}")
fi
[ ${#SVGS[@]} -gt 0 ] || { echo "kicad-sch-render: no SVGs produced" >&2; exit 1; }

convert() {  # $1 svg  $2 png
  if command -v rsvg-convert >/dev/null 2>&1; then rsvg-convert -w 1700 "$1" -o "$2"
  elif command -v inkscape >/dev/null 2>&1; then inkscape -w 1700 "$1" -o "$2" >/dev/null 2>&1
  elif python3 -c 'import cairosvg' >/dev/null 2>&1; then python3 -c "import cairosvg,sys;cairosvg.svg2png(url=sys.argv[1],write_to=sys.argv[2],output_width=1700)" "$1" "$2"
  elif command -v qlmanage >/dev/null 2>&1; then qlmanage -t -s 1700 -o "$(dirname "$2")" "$1" >/dev/null 2>&1 && mv "$1.png" "$2"
  else echo "kicad-sch-render: no SVG->PNG converter (install librsvg/inkscape/cairosvg)" >&2; return 1; fi
}

for s in "${SVGS[@]}"; do
  png="${s%.svg}.png"
  if convert "$s" "$png"; then echo "$png"; fi
done
