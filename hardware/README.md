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

**Revision B schematic wired and verified (2026-10-02).** The root sheet connects
MCU, Power, Lever and Controls with explicit hierarchical ports and visible wires.
Local circuits show USB pair joins and ESD, the battery load-share, charger/LDO,
RC lever inputs, switch returns, reverser divider/filter and both RGB chain rows.

The wiring and layout are captured in [`scripts/notchdeck-one.schgen.py`](scripts/notchdeck-one.schgen.py).
`make verify-notchdeck-one` checks KiCad's exported netlist against an independent
pin-level contract: **116 components, 80 nets, 360 pin endpoints, 14 explicit NCs**.
KiCad 10.0.6 ERC reports **zero errors and zero warnings**, without exclusions.
All components have footprints. The PCB now has a **provisional 145 × 105 mm,
four-layer floorplan with a 4×4 button layout on 19 mm pitch** (2026-10-03).
All 116 electrical footprints match the schematic, with four added mounting holes.
Native PCB DRC reports zero rule/parity violations and **313 unrouted connections**.
See [`FLOORPLAN.md`](notchdeck-one/FLOORPLAN.md) for placement details, evidence and
remaining mechanical/electrical review items. The board is not ready to fabricate.

Electrical corrections made during capture:

- Q1 drain goes to BAT+, source to VSYS; R4 pulls its gate down and R5 connects
  VBUS to the gate. The former source/drain note would allow unwanted charging
  through the body diode.
- U3 is **MCP73832T-2ACI/OT**, whose open-drain STAT safely pulls up to 3V3.
  Do not substitute the MCP73831 without addressing its driven-high STAT voltage.
- MAX17048 CELL and VDD connect to BAT+ per the ADI pin table.
- RGB LEDs use USB VBUS with a populated **SN74AHCT1G125DBVR** buffer; RGB is off
  during battery operation. C20 and C21–C36 provide local decoupling. C13 is 1uF,
  reducing the directly connected VBUS capacitance from the former 100uF bulk.
- J9 adds the missing center-off SPDT reverser input: 3V3 / midpoint / GND,
  filtered by R25/C37. D17 indicates 3V3; D18 indicates active charging.
- E73 GPIO electrical types are corrected (especially pad 28, incorrectly marked
  as power input). Passive SWD connector variants model the two parallel headers;
  attach only one probe at a time. `SW_RST` is now SW17 and `D_PP` is D19.

This is a connectivity-verified schematic, not a fabrication release. Review the
500mA charge setting against the selected protected cell and USB source, total USB
current and inrush, LDO dropout/thermal behavior, exact LED sourcing/pad orientation,
and MAX17048 exposed-pad land pattern before layout/fabrication. The firmware still
has a development-kit overlay; a board definition must implement NETPLAN's GPIOs,
USB-absent LED handling and a suitable LED brightness/current limit. Updated U3/U8
procurement IDs must be selected; stale LCSC IDs were removed.

## Workflow

```sh
make help                    # list targets
make gen-notchdeck-one       # generate missing sheets; preserve existing schematic
make check-notchdeck-one     # structural sanity check
make verify-notchdeck-one    # strict ERC + all expected net endpoints
make verify-pcb-notchdeck-one # schematic/PCB pad-net and UUID consistency
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
