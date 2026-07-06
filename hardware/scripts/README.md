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

Components are **placed, not wired** — laid out on a 100-mil grid with refs,
values, footprints and a per-sheet wiring note. Wiring is done afterwards in
eeschema (the notes are the spec). By default, re-running `gen` creates missing
sheets and keeps existing `.kicad_sch` files intact, reusing their UUIDs in
project metadata. Use `KSCHGEN_FORCE=1 make gen-<project>` only when you
intentionally want to rebuild generated sheets from the manifest.
Notes render in a fixed-width font; use `K.note_block()` and `K.pin_table()` in
manifests when writing pin maps or wiring tables that need alignment.

**A new board:** copy an existing `*.schgen.py`, change the `register_*` calls,
the component lists and the notes, then add the project to `PROJECTS` in the
`Makefile`. No engine changes needed.

## Notes

- `kicad-sch-render.sh` converts SVG→PNG with the first available of
  `rsvg-convert` / `inkscape` / `cairosvg` / macOS `qlmanage`. Output goes to a
  temp dir (override with `$RENDER_OUT`); pass sheet name(s) to render a subset.
- `extends`-based library symbols (e.g. `AP2112K-3.3`, `USBLC6-2SC6`,
  `…TC2030-NL`) draw correctly in eeschema but may render body-less via
  `kicad-cli` and show a benign `lib_symbol_mismatch` in ERC until first saved in
  eeschema (or **Tools → Update Symbols from Library**).
