---
name: kicad-schgen
description: >-
  Generate, validate, and visually review the NotchDeck KiCad hierarchical
  schematic. Use whenever working on hardware/notchdeck-one/*.kicad_sch — adding
  or changing parts, regenerating the sheets, checking footprints / refs / ERC,
  or rendering sheets to PNG. The schematic is generated from a data manifest
  (scripts/notchdeck-one.schgen.py) by an engine (scripts/kschgen.py); do not
  hand-edit the generated .kicad_sch files.
---

# NotchDeck schematic tooling

The schematic, wiring and deliberate block layouts are generated from
`hardware/scripts/notchdeck-one.schgen.py`. Edit this source rather than only the
emitted `.kicad_sch` files. KiCad is used to inspect the resulting design and ERC.

Run from `hardware/`:

```sh
make gen-notchdeck-one                    # creates missing sheets; preserves existing
KSCHGEN_FORCE=1 make gen-notchdeck-one     # apply intentional manifest changes
make check-notchdeck-one                  # structural sanity check
make verify-notchdeck-one                 # all net endpoints + strict ERC
make render-notchdeck-one                 # visual review
```

Close the NotchDeck schematic editor before rebuilding to avoid stale editor saves.
Existing sheet UUIDs are reused. Forced generation replaces editor-only changes;
reflect any such changes in the manifest first. The source uses `Capture` to place
parts, draw orthogonal wires and junctions, add labels/ports and mark intentional
NC pins. All physical pins must be accounted for. `kschgen.py` handles rotation,
field positions, derived symbol flattening and the KiCad hierarchy format.

`notchdeck-netcheck.py` is a separate electrical contract: it checks the complete
exported endpoint sets, including unintended extra connections and isolated pins,
and requires zero KiCad ERC errors or warnings. Do not add blanket exclusions to
make it pass. Review circuit behavior and rendered sheets as well; ERC cannot
prove voltage compatibility, power budgeting or footprint correctness.

Revision B baseline: 116 components, 80 nets, 360 endpoints, 14 intentional NCs.
The PCB has an unrouted 4×4 floorplan. Sourcing selections live in
`hardware/notchdeck-one/bom/jlcpcb-parts.json`; run `make verify-bom-notchdeck-one`
and `make verify-pcb-notchdeck-one` after part changes. See `hardware/README.md`
for pre-fabrication work.
