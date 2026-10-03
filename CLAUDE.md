# Claude Code Guidelines — NotchDeck

NotchDeck One: a dual-mode (USB-C + BLE) combined/dual-handle train-master controller built
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
- Wiring and deliberate block layout now live in the manifest. Default generation
  preserves existing sheets; use `KSCHGEN_FORCE=1 make gen-notchdeck-one` to apply
  manifest changes, with the NotchDeck schematic editor closed.
- After changes run `make verify-notchdeck-one`: the complete exported pin/net
  contract and zero ERC errors/warnings are required. Review SVG/PNG exports too.
- Use Makefile targets when possible.
- Don't violate the hard constraints in the `notchdeck-hardware` skill (esp. the
  0x36 two-bus split and the NFC/LFXO/UICR firmware requirements).
- No ERC exclusions are needed. Derived symbols must resolve without library mismatch warnings.

## Firmware

Firmware lives in `firmware/` (see `firmware/README.md`). Handle types are configured independently through Kconfig profiles. See
`docs/06-handle-interfaces.md`; pure decoding/filtering lives in `handle_decode.c`,
sensor access in `lever.c`. Run `make -C firmware test` after behavior changes.
