# Claude Code Guidelines — NotchDeck

NotchDeck One: a dual-mode (USB-C + BLE) one-handle train-master controller built
on an Ebyte **E73-2G4M08S1C** (nRF52840) module. This repo holds the KiCad
hardware (`hardware/`), firmware (`firmware/`), and design docs (`docs/`).

## Skills (read these first)

Two project skills in `.claude/skills/` cover the hardware work — prefer them over
re-deriving anything:

- **`notchdeck-hardware`** — design reference: sheet structure, the E73 pad map,
  the hard constraints (two I²C buses, NFC-as-GPIO, no-LFXO, nRESET/UICR), power
  architecture, programming, lever options.
- **`kicad-schgen`** — how to generate / validate / render the schematic with the
  `hardware/scripts/` tooling. **The schematic is generated from a data manifest,
  not hand-edited.**

## Source of truth

- `hardware/PARTS.md` — every BOM line → real JLCPCB part + KiCad symbol/footprint/3D.
- `hardware/NETPLAN.md` — E73 pad → net plan, power architecture, I²C plan, wiring.
- `hardware/scripts/README.md` — the generation / check / render scripts.
- Per-sheet **on-canvas notes** in the schematic carry the wiring/pin spec.

## Hardware workflow

Run from `hardware/`. Set `KICAD_CLI` if `kicad-cli` isn't on PATH (on macOS it's
in the KiCad app bundle; the scripts fall back to it automatically).

```sh
make gen-notchdeck-one       # regenerate the schematic from its manifest
make check-notchdeck-one     # components / footprints / dup refs / ERC tally
make render-notchdeck-one    # render sheets to PNG for visual review
make docs-notchdeck-one      # schematic + PCB SVGs + 3D renders + JLCPCB BOM
make bom-notchdeck-one       # JLCPCB BOM only
make jlc-notchdeck-one       # full JLCPCB fab+assembly zip
```

## Rules

- **Don't hand-edit `hardware/notchdeck-one/*.kicad_sch`** — edit the manifest
  `hardware/scripts/notchdeck-one.schgen.py` and `make gen-notchdeck-one`.
- **Close KiCad before regenerating** (eeschema open on those files will clash).
- **Regenerate before wiring, not after** — regen reassigns internal UUIDs and
  would discard wires added in eeschema. The schematic is currently *placed, not
  wired*; wiring is the next phase, done in eeschema per the sheet notes.
- Use Makefile targets when possible.
- Don't violate the hard constraints in the `notchdeck-hardware` skill (esp. the
  0x36 two-bus split and the NFC/LFXO/UICR firmware requirements).
- `extends`-based symbols show a benign `lib_symbol_mismatch` in ERC until first
  saved in eeschema — not a real error.

## Firmware

Firmware lives in `firmware/` (see `firmware/README.md`). The lever sensor choice
(AS5600 vs cam switches) is contained in firmware `lever.c`; the notch→HID table
is sensor-agnostic.
