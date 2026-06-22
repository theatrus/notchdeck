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

# NotchDeck schematic tooling (hardware/scripts/)

The hierarchical schematic is **generated from a data manifest, not hand-edited.**
Edit the manifest, then regenerate. All tooling lives in `hardware/scripts/` and
is driven by the `hardware/Makefile`.

## The model

```
scripts/notchdeck-one.schgen.py   (DATA: which parts, which sheet, wiring notes)
        │  imports
        ▼
scripts/kschgen.py                (ENGINE: emits KiCad-10 s-expr, reused per board)
        │  writes
        ▼
notchdeck-one/{notchdeck-one,mcu,power,lever,controls}.kicad_sch  (+ updates .kicad_pro)
```

Root sheet = hierarchical sheet symbols → one child `.kicad_sch` per functional
block. Every component resolves to a real library symbol + footprint, on a
100-mil grid, with a per-sheet free-text wiring note. **Components are PLACED,
not wired** — wiring (hierarchical labels + power rails) is done afterwards in
eeschema; the notes are the spec for it.

## Commands

Run from `hardware/`. `kicad-cli` is found via `$KICAD_CLI`, then `PATH`, then
the macOS app bundle, so set `KICAD_CLI` if it isn't on PATH.

```sh
make gen-notchdeck-one      # regenerate sheets from the manifest
make check-notchdeck-one    # component count, missing footprints, dup refs, ERC tally
make render-notchdeck-one   # render every sheet to PNG (paths printed)
```

Direct equivalents (e.g. to render one sheet):

```sh
python3 scripts/notchdeck-one.schgen.py
python3 scripts/kicad-sch-check.py notchdeck-one/notchdeck-one.kicad_sch
scripts/kicad-sch-render.sh notchdeck-one/controls.kicad_sch   # one sheet
scripts/kicad-sch-render.sh notchdeck-one/notchdeck-one.kicad_sch  # whole project
```

To eyeball a sheet, render it then Read the PNG.

## Editing the schematic = editing the manifest

`scripts/notchdeck-one.schgen.py` is data. Component dict keys:
`ref, lib_id, value, fp` (footprint), optional `lcsc, mpn, mfr, dnp, datasheet`.

- **Add/change a part** → edit the `big`/`small` list of the relevant sheet
  (MCU / POWER / LEVER / CONTROLS). If it uses a library not yet registered, add
  a `K.register_stdlib("Lib", "SymbolName")` (KiCad stdlib) or
  `K.register_lib("notchdeck", NOTCH_SYM, "Name")` (vendored) call.
- **Change a wiring note** → edit `<SHEET>["note"] = (x, y, "...")`.
- **`big` vs `small`** → `big` parts get a wide top row (ICs/connectors); `small`
  parts grid below. Layout is auto; tweak only by moving parts between lists.
- Then `make gen-notchdeck-one && make check-notchdeck-one`.

## How the engine works (scripts/kschgen.py)

- Pulls each `(symbol "...")` block verbatim from the library `.kicad_sym`,
  renames it to the full `lib_id`, embeds it in the sheet's `lib_symbols` cache.
- **Handles `(extends ...)`** by also embedding the parent symbol (recursively)
  and resolving pin numbers through it.
- Emits per-component `(instances (path "/<root_uuid>/<sheet_uuid>" ...))` —
  child sheet file UUID == its sheet-symbol UUID in the root (that linkage is
  what makes parts show up as components, not just floating pins).
- Snaps all placement to a 2.54 mm grid so pins stay on-grid.

## Caveats (important)

- **Close KiCad before `gen`.** Regenerating rewrites the `.kicad_sch` files; if
  eeschema has them open it will clash and may overwrite your run on save.
- **Regen reassigns internal UUIDs** (pins/instances) but keeps `ROOT_UUID`
  stable. Regenerate *before* wiring, not after — re-running after you've added
  wires in eeschema will discard them.
- **`extends` symbols** (`AP2112K-3.3`, `USBLC6-2SC6`, `…TC2030-NL`) render fine
  in eeschema but may draw body-less via `kicad-cli` and show a benign
  `lib_symbol_mismatch` in ERC until first saved in eeschema (or **Tools →
  Update Symbols from Library**). Not a real problem.
- **ERC pre-wiring** legitimately shows many `pin_not_connected` /
  `pin_not_driven` / `power_pin_not_driven` — expected for placed-not-wired.
  `check` only *fails* on structural problems (zero components, a missing
  footprint, or a duplicate reference).

## A new board

Copy `scripts/<board>.schgen.py`, change the `register_*` calls, the component
lists and the notes, give it a fresh `ROOT_UUID`, then add the project to
`PROJECTS` in `hardware/Makefile`. No engine changes needed. See
`hardware/scripts/README.md`.
