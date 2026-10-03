# hardware/scripts

Tooling for the BenchBits KiCad projects. Driven via the `Makefile` (preferred)
or run directly. All locate `kicad-cli` via `$KICAD_CLI`, then `PATH`, then the
macOS app bundle (`/Applications/KiCad/KiCad.app/...`).

| Script | Make target | What it does |
|---|---|---|
| `<project>.schgen.py` | `make gen-<project>` | Regenerate the hierarchical schematic from a data manifest. |
| `kschgen.py` | — | Generic generation engine imported by the `*.schgen.py` manifests. |
| `kicad-sch-check.py` | `make check-<project>` | Sanity-check a schematic: component count, missing footprints, duplicate refs, ERC tally. Exits non-zero on a structural problem. |
| `kicad-sch-render.sh` | `make render-<project>` | Render schematic sheet(s) to PNG for a quick visual review. |
| `jlcpcb-package.sh` | `make jlc-<project>` | Gerbers + drill + BOM + CPL → JLCPCB zip. |

## Generating a schematic from a manifest

`scripts/<project>.schgen.py` is **data**: it registers the symbol libraries the
board uses, lists the components per hierarchical sheet (ref / lib_id / value /
footprint / LCSC / MPN / ...), and adds a free-text wiring note per sheet. The
reusable logic lives in `kschgen.py`, which hand-authors KiCad-10 schematic files
in the format used across the BenchBits projects (root sheet of hierarchical
sheet symbols + one child `.kicad_sch` per block, every part resolving to a real
library symbol + footprint, `extends`-derived symbols handled).

```sh
make gen-notchdeck-one      # rewrite the sheets from scripts/notchdeck-one.schgen.py
make check-notchdeck-one    # verify it
make render-notchdeck-one   # eyeball it
```

NotchDeck's manifest now captures **components, wiring, hierarchical ports and
layout**. The `Capture` helper groups local circuits and checks that every pin is
wired or explicitly NC. The root connects MCU, Power, Lever and Controls.
By default, `gen` keeps existing sheets intact. Close the NotchDeck schematic editor,
then use `KSCHGEN_FORCE=1 make gen-notchdeck-one` to apply manifest changes.
Manual editor changes must be reflected in the manifest before a forced rebuild.

`make verify-notchdeck-one` exports KiCad XML and compares **every endpoint** to
`scripts/notchdeck-netcheck.py`, then requires zero ERC violations. This independent
contract checks rail isolation, MCU pads, both I2C buses, USB pairs, the power path,
SWD/reset, all switches, reverser and all sixteen LEDs. Set `NETCHECK_OUT` to a
local directory to retain netlist/JSON reports. It checks both opens and extra pins
(shorts), not just whether an expected pair happens to share a net.

The engine supports component rotation and field offsets. Derived-library symbols
are flattened with property overrides, matching KiCad's library resolver.
Notes render in a fixed-width font; use `K.note_block()` and `K.pin_table()` in
manifests when writing pin maps or wiring tables that need alignment.

**A new board:** copy an existing `*.schgen.py`, change the `register_*` calls,
the component lists and the notes, then add the project to `PROJECTS` in the
`Makefile`. No engine changes needed.

## Notes

- `kicad-sch-render.sh` converts SVG→PNG with the first available of
  `rsvg-convert` / `inkscape` / `cairosvg` / macOS `qlmanage`. Output goes to a
  temp dir (override with `$RENDER_OUT`); pass sheet name(s) to render a subset.
- Derived symbols are now flattened correctly, including their overridden properties;
  no library-mismatch ERC warnings are expected for this project.
