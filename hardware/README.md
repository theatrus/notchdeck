# NotchDeck — hardware

KiCad 10 project for **NotchDeck One**. Structure and tooling are patterned on the other
BenchBits hardware projects (tsumikoro / pulsarfab): a `Makefile` driving `kicad-cli` for
doc generation and JLCPCB packaging, a shared project-local `lib/`, and one subdirectory
per PCB.

```
hardware/
├── Makefile                 # docs / bom / jlc targets (kicad-cli), per-project template
├── scripts/jlcpcb-package.sh# gerbers + drill + BOM + CPL -> <project>-jlcpcb.zip
├── sym-lib-table            # project-local symbol library  (notchdeck:)
├── fp-lib-table             # project-local footprint library (notchdeck:)
├── lib/
│   ├── symbols/notchdeck.kicad_sym   # vendored symbols (see ATTRIBUTIONS.md)
│   ├── footprints.pretty/            # vendored footprints
│   ├── 3dmodels/                     # vendored STEP models
│   └── ATTRIBUTIONS.md               # source + license per vendored part
├── datasheets/
├── PARTS.md                 # real-part -> KiCad symbol/footprint/3D mapping (START HERE)
└── notchdeck-one/           # the PCB
    ├── notchdeck-one.kicad_pro / .kicad_sch / .kicad_pcb
    └── sym-lib-table / fp-lib-table
```

## Status

**Schematic populated, not yet wired.** The hierarchical schematic (root + MCU / Power /
Lever / Controls sheets) is generated from a data manifest,
[`scripts/notchdeck-one.schgen.py`](scripts/notchdeck-one.schgen.py) — every part from
[`PARTS.md`](PARTS.md) is placed and resolves to a real symbol + footprint, with a per-sheet
wiring / pin-assignment note drawn from [`NETPLAN.md`](NETPLAN.md). Inter-sheet wiring
(hierarchical labels + power rails) is the next step, done in eeschema per the notes. The
`.kicad_pcb` is still an empty scaffold. Sourcing rationale:
[`../docs/04-bom-sourcing.md`](../docs/04-bom-sourcing.md).

## Workflow

```sh
make help                    # list targets
make gen-notchdeck-one       # regenerate the schematic from its manifest
make check-notchdeck-one     # sanity-check (components / footprints / dup refs / ERC)
make render-notchdeck-one    # render sheets to PNG for visual review
make docs-notchdeck-one      # schematic SVGs + PCB SVGs + 3D renders + JLCPCB BOM
make bom-notchdeck-one       # just the BOM (jlcpcb_bom.csv)
make jlc-notchdeck-one       # full JLCPCB fab+assembly zip
make clean-docs clean-jlc    # remove generated artifacts
```

See [`scripts/README.md`](scripts/README.md) for the generation / check / render tooling.

Generated outputs (`*/docs/images/`, `*/jlcpcb/`, `*-jlcpcb.zip`, `jlcpcb_bom.csv`) are
git-ignored — regenerate with `make`.

## USB on the E73 — verified

The Ebyte E73-2G4M08S1C **exposes the nRF52840 USB lines**: pad 27 = VBS (VBUS),
pad 29 = D−, pad 31 = D+ (confirmed against Ebyte's pin-definition table; see `PARTS.md`).
The dual-mode USB design works on the module as-is — no parts change needed.

Requires `kicad-cli` (KiCad 10) on `PATH`.
