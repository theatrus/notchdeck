# Claude Code Guidelines — NotchDeck

NotchDeck One: a dual-mode (USB-C + BLE) combined/dual-handle train-master controller built
on an Ebyte **E73-2G4M08S1C** (nRF52840) module. This repo holds the KiCad
hardware (`hardware/`), firmware (`firmware/`), and design docs (`docs/`).

## Skills (read these first)

Two project skills in `.claude/skills/` cover the hardware work — prefer them over
re-deriving anything:

- **`notchdeck-hardware`** — design reference: sheet structure, the E73 pad map,
  the hard constraints (isolated I²C address domains, no-LFXO, nRESET/UICR), power
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
in the KiCad app bundle). Native Makefile exports need this setting even where
individual scripts provide an app-bundle fallback.

```sh
make gen-notchdeck-one gen-notchdeck-buttons  # create missing sheets; preserve existing
make verify                 # both boards: nets/ERC, PCB parity and BOM audits
make render-notchdeck-one render-notchdeck-buttons
make docs                   # both boards: images and JLCPCB BOMs
make jlc                    # separate fab+assembly ZIPs (still unrouted)
```

## Rules

- **Don't hand-edit generated `.kicad_sch` files** — edit `hardware/scripts/<project>.schgen.py` and run `make gen-<project>` for notchdeck-one or notchdeck-buttons.
- **Close KiCad before regenerating** (eeschema open on those files will clash).
- Wiring and deliberate block layout now live in the manifest. Default generation
  preserves existing sheets; use `KSCHGEN_FORCE=1 make gen-<project>` to apply
  manifest changes, with the affected schematic editor closed.
- After changes run `make verify`: both boards’ complete exported pin/net
  contract and zero ERC errors/warnings are required. Review SVG/PNG exports too.
- Use Makefile targets when possible.
- Don't violate the hard constraints in the `notchdeck-hardware` skill (esp. the
  0x36 address isolation and the LFCLK/UICR firmware requirements). Rev E NFC
  pins are NC; Rev C/D's NFC-as-GPIO button wiring is historical.
- No ERC exclusions are needed. Derived symbols must resolve without library mismatch warnings.

## Firmware

Firmware lives in `firmware/` (see `firmware/README.md`). Handle types are configured independently through Kconfig profiles. See
`docs/06-handle-interfaces.md`; pure decoding/filtering lives in `handle_decode.c`,
sensor access in `lever.c`. Run `make -C firmware test` after behavior changes.

## Rev E split panel

`notchdeck-one` is the 115×90mm logic/handle PCB; `notchdeck-buttons` is the 86×120mm STM32G030 key/RGB PCB. The FFC is six-way Type A, main J15 pin n to button J1 pin 7−n. Main keeps Select/Start plus Reset. Panel firmware and main I²C integration remain open; do not treat the Rev C/D overlay as compatible. See `hardware/notchdeck-buttons/README.md`. `make -C hardware verify` and `make -C hardware jlc` cover both assemblies.
