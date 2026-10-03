# BOM and sourcing — Rev E

Rev E has **two separately assembled PCBs**. All installed board components have
selected JLCPCB catalog codes. The following counts and stock observations are
the **2026-10-03 snapshot**, not live availability or reservations.

| Assembly | Installed parts per board | Unique JLCPCB codes | Tracked assembly BOM |
|---|---:|---:|---|
| Logic / handles | 92 | 31 | [notchdeck-one](../hardware/notchdeck-one/bom/jlcpcb-bom.csv) |
| Button / RGB panel | 84 | 13 | [notchdeck-buttons](../hardware/notchdeck-buttons/bom/jlcpcb-bom.csv) |
| Complete set | 176 | 37 across both boards | [Five-set stock requirements](../hardware/jlcpcb-five-set-stock.csv) |

Five sets need **880 installed parts before assembly attrition**, plus five
interconnect cables. Bare programming contacts and mounting holes are excluded
from BOM/CPL. Shared catalog codes are counted across both boards in the five-set
report; do not independently allocate the same stock balance to each board.

## Selected parts and inventory

The [part map](../hardware/PARTS.md) lists every exact MPN, JLCPCB code and KiCad
footprint. Each project's `bom/jlcpcb-parts.json` drives schematic sourcing
properties; `bom/bom.csv` tracks sourcing and `bom/jlcpcb-stock.csv` records dated
observations. See the [logic BOM notes](../hardware/notchdeck-one/bom/README.md)
and [panel BOM notes](../hardware/notchdeck-buttons/bom/README.md).

- **Main MCU:** Ebyte E73-2G4M08S1C / C356849, with onboard antenna.
- **Panel MCU:** STM32G030F6P6TR / C529330, selected from owned private inventory;
  five required. Its recorded community catalog estimate of about $0.80 is not
  a current quote or the cost paid for owned stock.
- **Power:** MCP73832 / C38066, AP2112K / C51118, MAX17048 / C2682616,
  AO3401A / C15127 and B5819W / C8598. The earlier nPM1300 and MCP73831 options
  are not selected; MCP73832's open-drain STAT matters to this circuit.
- **Panel link:** two JUSHUO AFA07-S06FCA-00 / C262712 connectors per set;
  ten needed for five sets. The snapshot records 31,746 publicly available.
- **Keys:** sixteen 1N4148W / C81598 isolation diodes per panel, with an
  STM32-scanned matrix; two functional buttons and Reset remain on the main PCB.

Public JLCPCB **Available Order Qty** covered the combined requirement for all
selections except the panel MCU, covered by owned inventory. Reusable private
inventory is at `~/Dropbox-elec/github/jlcpcb-private-inventory.csv`; balances
stay outside this repository. It is a snapshot, and allocation/reservation detail
was unavailable. Confirm free allocation, assembly attrition, current stock and
fees before an order. No purchases or reservations have been made.

## Cable and external parts

The [system BOM](../hardware/system-bom.csv) lists one **Molex 0151670213**, DigiKey
**WM13121-ND**, per set: six conductors, 1mm pitch, Type A, 177.8mm. The dated
DigiKey observation was 139 available. It is purchased separately and does not
belong in either PCB assembly BOM.

The [panel guide](../hardware/notchdeck-buttons/README.md) records contact-side
orientation, reversed connector numbering, current limits and the end-thickness
tolerance mismatch still requiring sample-fit or supplier approval. Nominal
dimensions alone do not establish production fit.

Mating handle housings/crimps, external AS5600 carriers, microload switches,
magnets/cams, protected cell, keycaps and enclosure are **not a fully sourced kit**.
The PCB stock report does not cover these items. Select exact parts and check
their availability when the mechanical design is finalized.

## Manufacturing exports

From the repository root, with KiCad 10 available:

```sh
make -C hardware verify
make -C hardware jlc
```

Each project produces `<project>/<project>-jlcpcb.zip` under `hardware/`, containing
Gerbers, drill, BOM and `<project>-CPL.csv`. The unzipped files are in
`hardware/<project>/jlcpcb/`. The package script checks that BOM and CPL reference
sets agree. Generated exports are ignored by Git; reviewed BOM snapshots remain
tracked in each `bom/` directory.

**Both boards remain unrouted.** Exporting these files does not release them for
fabrication. Finish the [hardware open work](../hardware/README.md#sourcing-and-remaining-work),
then inspect final assembly eligibility and CPL rotations at JLCPCB. The earlier
May 2026 component-option research has been superseded by these captured selections
and dated stock files; it is not an ordering BOM.
