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

Scaffold only. The `.kicad_sch` / `.kicad_pcb` are **valid but empty** (they export and
package cleanly via the Makefile — verified — they just have no components yet). Populate
the schematic in KiCad using [`PARTS.md`](PARTS.md), which maps every block to a real
JLCPCB part and a KiCad symbol/footprint/3D model (stdlib where possible, vendored where
not). Sourcing rationale is in [`../docs/04-bom-sourcing.md`](../docs/04-bom-sourcing.md).

## Workflow

```sh
make help                    # list targets
make docs-notchdeck-one      # schematic SVGs + PCB SVGs + 3D renders + JLCPCB BOM
make bom-notchdeck-one       # just the BOM (jlcpcb_bom.csv)
make jlc-notchdeck-one       # full JLCPCB fab+assembly zip
make clean-docs clean-jlc    # remove generated artifacts
```

Generated outputs (`*/docs/images/`, `*/jlcpcb/`, `*-jlcpcb.zip`, `jlcpcb_bom.csv`) are
git-ignored — regenerate with `make`.

## USB on the E73 — verified

The Ebyte E73-2G4M08S1C **exposes the nRF52840 USB lines**: pad 27 = VBS (VBUS),
pad 29 = D−, pad 31 = D+ (confirmed against Ebyte's pin-definition table; see `PARTS.md`).
The dual-mode USB design works on the module as-is — no parts change needed.

Requires `kicad-cli` (KiCad 10) on `PATH`.
