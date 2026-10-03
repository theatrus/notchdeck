# NotchDeck One — provisional PCB floorplan

2026-10-03, KiCad 10.0.6. The schematic is captured and its connectivity checks
pass. The PCB contains an editable placement study for the requested **4×4 button
layout**. It is **unrouted and not ready for fabrication**.

## Placement

The rectangular outline is **145 × 105 mm**, from (50, 50) to (195, 155) in KiCad
coordinates. Four copper layers and 1.6 mm thickness are provisional; no stackup
or controlled-impedance geometry has been selected. All components are on F.Cu.

| Area | Placement and intent |
|---|---|
| Buttons | SW1–SW16 on a 19 mm square pitch; centers x=122/141/160/179, y=84/103/122/141 mm. First three rows are BTN1–BTN12; bottom row is Up, Down, Left, Right. These are independent inputs, not an electrical scan matrix. |
| RGB | One LED 7 mm above each button, with its bypass capacitor nearby. D1–D16 follow a serpentine chain; alternating rows rotate the footprints to put DIN toward the preceding LED. |
| USB and power | J1 faces the top edge. U7 sits behind it; charger, load sharing, LDO and fuel gauge occupy the upper left. J2 faces the left edge. |
| Radio | U1 at (93, 66), rotated 90°. Its antenna end overhangs the top board edge by approximately 2 mm. An all-layer rule area prohibits pads, tracks, vias and pours at x=81…105, y=43…51.3 mm. Keep other components and enclosure metal out manually; the rule area permits U1's own footprint. |
| Programming | J3 SWD and J4 TC2030 are below the radio; SW17 reset is beside it. Allow probe/cable access in the enclosure. |
| Lever | U5 AS5600 center at (81, 113). The 10 mm radius drawing marks provisional shaft/magnet space, **not a shaft hole or validated mechanical clearance**. |
| Harnesses | J5–J8 face the left edge, ordered S0–S3 top to bottom with local RC networks. J9 reverser faces the bottom edge. |
| Mounting | Four board-only 3.2 mm NPTH holes at (55,55), (190,55), (190,150), (55,150). Enclosure bosses and screw-head clearances remain to be designed. |

RGB references by physical row, left to right:

```
D1   D2   D3   D4
D8   D7   D6   D5
D9   D10  D11  D12
D16  D15  D14  D13
```

The PCB has 116 electrical footprints plus four mechanical mounting holes.
The saved `.kicad_pcb` is the editable source after this initial placement.
`scripts/notchdeck-floorplan.py` records the seed geometry; it is not part of
ordinary schematic generation and must not be used to overwrite subsequent work.

## Checks and evidence

| Check | Result | Evidence / confidence |
|---|---|---|
| Schematic net contract | 116 components, 80 nets, 360 unique pin endpoints, 14 intentional NCs | Deterministic comparison of KiCad's exported netlist against `notchdeck-netcheck.py`; internal connectivity consistency |
| Native ERC | 0 errors, 0 warnings, no exclusions | KiCad 10.0.6 ERC |
| PCB pad/net audit | All 360 endpoint assignments, references, values, footprint IDs and schematic UUID paths match | Deterministic comparison of XML netlist and native PCB pad data; includes duplicated switch/connector pads |
| Native PCB DRC with schematic parity | 0 rule violations, 0 parity issues, **313 unconnected items** | KiCad 10.0.6 under the existing project rules; the remaining airwires are expected because routing has not begun |
| GUI review | Root and all four child sheets opened and visually inspected; PCB opened with placement/ratsnest | Direct visual inspection. Fixed missing sheet-page instances that caused KiCad's automatic-repair warning, and overlapping U7 input wire stubs. |
| Generator retention | Forced regeneration retained placed-symbol UUIDs; subsequent PCB parity audit passed | Native file/UUID check; future schematic generation retains PCB associations for unchanged references |
| 3D preview | Outline, holes and radio overhang inspected | Partial model coverage; not an assembly or enclosure fit check |

Reproduce the principal checks from the repository root:

```sh
make -C hardware verify-notchdeck-one verify-pcb-notchdeck-one
kicad-cli pcb drc --schematic-parity --format json \
  -o /tmp/notchdeck-drc.json hardware/notchdeck-one/notchdeck-one.kicad_pcb
```

The pad audit uses KiCad's Python runtime (override `KICAD_PYTHON` in the Makefile
on other installations). It inspects a temporary PCB copy so it cannot rewrite
project settings. Native CLI reports and previews are generated under the ignored
`docs/images/` directory.

## Open work before routing and fabrication

1. Settle enclosure, switch/keycap parts, lever/magnet axis, mounting bosses and
   connector access. This board shape and all mechanical coordinates are provisional.
2. Validate the exact E73 land pattern and antenna clearance against the module
   drawing and enclosure. Its current footprint has no courtyard and uses drilled
   internal pads; a clean native DRC does not validate that geometry.
3. Resolve the exact RGB LED part and pin-1/pad convention (WS2812B symbol versus
   the selected SK6812-family footprint), MAX17048 package/exposed-pad dimensions,
   and remaining MPNs. The sourcing analyzer reports only 17/34 unique BOM lines
   with MPNs. No part substitutions were made during floorplanning.
4. Review the existing 500 mA charge setting against the protected cell and USB
   current budget, LED brightness limit/inrush, and LDO dropout/dissipation. The
   connectivity checks do not establish electrical or thermal margins.
5. Place an uninterrupted reference plane, route USB through U7 with a short ESD
   ground return, and review local VBUS bypassing at U7. The EMC analyzer flags its
   nearest existing bypass approximately 10 mm away. Final placement and routing
   should resolve this before sign-off. Route short local decoupling loops before
   the button fanout; keep LED supply current away from sensor returns.
6. Add ground stitching, test access and assembly fiducials when routing and
   manufacturing requirements are set. No copper planes, traces or vias exist yet.
7. Implement the board-specific firmware pin map, reset/NFC configuration, internal
   RC LFCLK, separate I2C buses, and USB-dependent RGB behavior described in
   [`NETPLAN.md`](../NETPLAN.md). The development-kit overlay is not that board definition.

## Analyzer triage and review limits

`analyze_schematic.py`, `analyze_pcb.py --full`, `cross_analysis.py`, the EMC analyzer
and the thermal analyzer were run. Cross-analysis reported no findings. Their
topology reports supplement the native checks; they are not hardware validation.

- **RS-001, missing 3V3 source:** analyzer hierarchy false positive. Native XML
  places U2.5, U1.19 and U1.23 together on global `+3V3`; ERC is clean.
- **PU-001, reset pull-up:** heuristic remains a firmware/reset-configuration
  review item. The schematic relies on the MCU's reset behavior; no external
  resistor was added merely to satisfy the heuristic.
- **EMC missing ground plane/stitching and PCB unrouted errors:** accurate for this
  placement stage and still open. No EMC pass or numerical compliance claim is made.
- **Connector filtering / TC2030 ground-pin heuristics:** the standard programming
  interfaces and existing lever RC filters require context. External harness ESD
  needs review against cable length and enclosure accessibility; no blanket ferrite
  additions or connector pinout changes were applied.
- **Datasheets:** manufacturer PDFs for AP2112, MCP73832, SN74AHCT1G125 and AO3401A
  were cached locally. AP2112 SOT25 pin table (p. 2), MCP73831/2 pin descriptions
  (§3), and SN74AHCT1G125 pin functions (table 4-1) were manually cross-checked.
  See [`NETPLAN.md`](../NETPLAN.md#verified-capture-references-2026-10-02) for the
  prior capture references. Full current manufacturer pin/land-pattern coverage
  and structured extraction are incomplete; all-part electrical correctness is
  **not** established by the net/PCB consistency results.
- **Thermal:** analyzer skipped assessment because no quantifiable dissipation
  data/extraction cache was available. Zero assessed components is not a pass.
- **SPICE:** not run; no supported simulator installed. **Lifecycle:** not run;
  distributor credentials unavailable. **Gerber/DFM:** not run; this is an unrouted
  floorplan with no fabrication release. **Prior-review delta:** previous board
  was an empty scaffold; no prior routed-layout review exists for comparison.

Trust summary: high confidence in native connectivity/parity results and recorded
placement coordinates; limited confidence in complete part/package, mechanical,
power, thermal and EMC suitability until the open work above is completed.
