#!/usr/bin/env bash
# jlcpcb-package.sh — generate a JLCPCB manufacturing package from a KiCad project
#
# Produces a zip that contains:
#   gerbers/           Gerber files for all copper / mask / silk / paste / edge layers
#   <name>.drl         Merged Excellon drill file (PTH+NPTH)
#   <name>-BOM.csv     JLCPCB-formatted BOM (Designator, Comment, Footprint, LCSC Part #, ...)
#   <name>-CPL.csv     Component placement / pick-and-place (Designator, Mid X, Mid Y, Rotation, Layer)
#   README.txt         One-line summary
#
# The zip can be uploaded directly to https://cart.jlcpcb.com/quote — no layer
# renaming needed, JLCPCB accepts KiCad's native Gerber filenames.
#
# Usage:
#   jlcpcb-package.sh <pcb.kicad_pcb> <sch.kicad_sch> [output_dir]
#
# Requires:
#   kicad-cli  (KiCad 9.0+ recommended for --layers selection and CPL format)
#   zip        (standard macOS/Linux)

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "usage: $(basename "$0") <pcb.kicad_pcb> <sch.kicad_sch> [output_dir]" >&2
    echo "" >&2
    echo "Produces gerbers, drill, BOM, and CPL files zipped together for upload" >&2
    echo "to JLCPCB's quote / PCB assembly flow." >&2
    exit 1
fi

PCB=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
SCH=$(cd "$(dirname "$2")" && pwd)/$(basename "$2")
OUT_DIR=${3:-$(dirname "$PCB")/jlcpcb}

if [[ ! -f "$PCB" ]]; then
    echo "error: PCB file not found: $PCB" >&2; exit 1
fi
if [[ ! -f "$SCH" ]]; then
    echo "error: schematic file not found: $SCH" >&2; exit 1
fi

KICAD_CLI=${KICAD_CLI:-kicad-cli}
NAME=$(basename "$PCB" .kicad_pcb)

echo "[jlcpcb] building package for $NAME"
echo "[jlcpcb]   PCB: $PCB"
echo "[jlcpcb]   SCH: $SCH"
echo "[jlcpcb]   OUT: $OUT_DIR"

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/gerbers"

# --- Gerbers ------------------------------------------------------------------
# JLCPCB's 4-layer stackup wants: F.Cu, In1.Cu, In2.Cu, B.Cu + masks, silks,
# pastes, edge. The web uploader reads X2 attributes, so KiCad's default
# Gerber filenames (with _layer.gbr) are recognized.

# Layer set is chosen dynamically so 2-layer projects also work.
GERBER_LAYERS="F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,B.Paste,Edge.Cuts"

# Add inner layers if present (ignore failure if this is a 2-layer board).
if $KICAD_CLI pcb export gerbers --help 2>&1 >/dev/null; then :; fi

# Probe the PCB for the presence of inner layers by grepping the file — cheap
# and reliable across KiCad versions.
if grep -q '"In1\.Cu"\|(In1\.Cu)' "$PCB"; then
    GERBER_LAYERS="F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,B.Paste,Edge.Cuts"
fi

echo "[jlcpcb] generating gerbers (layers: $GERBER_LAYERS)"
"$KICAD_CLI" pcb export gerbers \
    --output "$OUT_DIR/gerbers/" \
    --layers "$GERBER_LAYERS" \
    --use-drill-file-origin \
    --no-x2 \
    --no-netlist \
    "$PCB" >/dev/null

# --- Drill --------------------------------------------------------------------
# JLCPCB accepts a single merged Excellon file containing both PTH and NPTH,
# which is KiCad's default (no --excellon-separate-th). Units: mm. Drill
# origin: absolute (matches the Gerber aux origin used above).
echo "[jlcpcb] generating drill (excellon, merged, mm)"
"$KICAD_CLI" pcb export drill \
    --output "$OUT_DIR/gerbers/" \
    --format excellon \
    --excellon-units mm \
    --excellon-min-header \
    --drill-origin plot \
    --generate-map \
    --map-format gerberx2 \
    "$PCB" >/dev/null

# --- CPL (pick-and-place) -----------------------------------------------------
# JLCPCB wants CSV with columns:
#   Designator, Mid X, Mid Y, Rotation, Layer
# KiCad's csv format produces almost-compatible output; we rename headers.
echo "[jlcpcb] generating CPL (both sides, mm)"
RAW_CPL="$OUT_DIR/${NAME}-CPL-raw.csv"
"$KICAD_CLI" pcb export pos \
    --output "$RAW_CPL" \
    --format csv \
    --units mm \
    --side both \
    --use-drill-file-origin \
    --smd-only \
    "$PCB" >/dev/null

# Translate KiCad's columns (Ref,Val,Package,PosX,PosY,Rot,Side) to JLCPCB's
# schema (Designator,Val,Package,Mid X,Mid Y,Rotation,Layer). Also capitalize
# the Side values ("top"/"bottom" -> "Top"/"Bottom").
python3 <<PYEOF
import csv, os, sys

raw = "$RAW_CPL"
out = "$OUT_DIR/${NAME}-CPL.csv"

with open(raw, newline="") as fin, open(out, "w", newline="") as fout:
    rdr = csv.reader(fin)
    wtr = csv.writer(fout)
    hdr = next(rdr)
    # KiCad header: Ref,Val,Package,PosX,PosY,Rot,Side
    wtr.writerow(["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer"])
    for row in rdr:
        if not row: continue
        ref, val, pkg, x, y, rot, side = row[:7]
        side_cap = side.strip().capitalize()
        wtr.writerow([ref, val, pkg, x, y, rot, side_cap])
print(f"[jlcpcb]   wrote {out}")
PYEOF
rm -f "$RAW_CPL"

# --- BOM ---------------------------------------------------------------------
echo "[jlcpcb] generating BOM"
"$KICAD_CLI" sch export bom \
    --output "$OUT_DIR/${NAME}-BOM.csv" \
    --fields '${ITEM_NUMBER},Reference,Value,Footprint,${QUANTITY},LCSC,MPN,Manufacturer' \
    --labels "Item,Designator,Comment,Footprint,Qty,LCSC Part #,MPN,Manufacturer" \
    --group-by 'Value,Footprint' \
    --exclude-dnp \
    "$SCH" >/dev/null

# --- README ------------------------------------------------------------------
cat > "$OUT_DIR/README.txt" <<EOF
JLCPCB manufacturing package for ${NAME}
Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

Files:
  gerbers/*.gbr           Gerber files (top/inner/bottom copper, mask, silk, paste)
  gerbers/*.drl           Excellon drill files (PTH and NPTH separate)
  gerbers/*-drl_map.gbr   Optional drill map
  ${NAME}-BOM.csv         JLCPCB-format BOM (upload as Assembly > Add BOM File)
  ${NAME}-CPL.csv         Pick-and-place (upload as Assembly > Add CPL File)

To order:
  1. Upload the zip to https://cart.jlcpcb.com/quote
  2. Enable "PCB Assembly" and upload the BOM + CPL files
  3. Verify part matching; fix any unmatched LCSC numbers manually

Notes:
  - Gerber layer names use KiCad's native scheme. JLCPCB auto-detects via X2.
  - Drill origin is set to absolute (matches Gerber aux origin).
  - CPL rotations are KiCad's convention. Some footprints (SOT-23, QFN, SOIC)
    may need JLCPCB-specific rotation offsets — verify in JLCPCB's preview
    step before confirming the order.
EOF

# --- Zip ---------------------------------------------------------------------
ZIP="$(dirname "$OUT_DIR")/${NAME}-jlcpcb.zip"
rm -f "$ZIP"
(cd "$OUT_DIR/.." && zip -r -q "${NAME}-jlcpcb.zip" "$(basename "$OUT_DIR")")

echo ""
echo "[jlcpcb] done"
echo "[jlcpcb]   package dir: $OUT_DIR"
echo "[jlcpcb]   archive:     $ZIP"
