# Logic board — Rev E floorplan

2026-10-03, KiCad 10.0.6. **Unrouted placement study**, 115×90mm from (50,50) to (165,140), four copper layers, provisional 1.6mm thickness. All parts are on top; four 3.2mm mounting holes are 5mm from the corners. There are 93 electrical footprints and four board-only holes.

The button matrix, RGB LEDs, AHCT buffer and their local passives moved to [notchdeck-buttons](../notchdeck-buttons/FLOORPLAN.md). Main SW18 Select at (128,104) and SW19 Start at (147,104) retain direct BTN7/BTN8 inputs; SW17 remains Reset. J15 FFC at (135,54.2), facing the top, connects the button MCU; U12/C44 protect and bypass its I²C/3V3 port. R42 pulls IRQ up.

USB and power remain upper left. E73 is at (93,66), rotated 90°, antenna overhanging the top edge by about 2mm. The all-layer rule area at x81…105/y43…51.3 prohibits copper/pads/vias; enclosure-metal clearance and exact module footprint remain review items. Main SWD and Tag-Connect remain below the radio. J12 power Gray faces left at (55.8,115); J5 brake/mascon Gray faces right at (159.2,109). J10/J11 magnetic ports face down at (119,134.2)/(145,134.2); J9 reverser is at (79,134.2). U5 remains at (81,113), with both R37/R38 removable for an external J10 sensor. No shaft hole or validated magnet envelope is provided.

Native checks: **zero ERC violations**, complete 318-endpoint/74-net contract including 25 intentional NCs, all schematic/PCB nets and UUID paths match, **zero DRC rule/parity issues and 249 unconnected items**. Sourcing fields, 92 assembly parts and bare J4 exclusion match. These checks do not verify routing, mechanical fit or electrical/thermal margins.

The saved PCB is editable in KiCad. `scripts/notchdeck-floorplan.py --project notchdeck-one` records the provisional seed geometry; `--replace-unrouted` is intentionally explicit and must not overwrite subsequent placement work. Do not use it once routing begins.

Before fabrication, resolve [hardware open work](../README.md#sourcing-and-remaining-work), exact E73/MAX17048 land patterns, magnet/handle mechanics, USB/current budget and local decoupling. Route uninterrupted reference planes, USB via its ESD array with short ground return, and keep RGB return current separate from sensor return paths. Add test access, fiducials and ground stitching as needed. Historical Rev B analyzer results are not a Rev E EMC/thermal/DFM approval.
