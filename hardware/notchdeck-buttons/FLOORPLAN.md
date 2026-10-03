# Button board — Rev E floorplan

**86×120mm**, two layers, provisional 1.6mm thickness; outline (50,50)…(136,170). All components are on top. Four 3.2mm NPTH holes at (55,55), (131,55), (131,165), (55,165) require enclosure boss/keycap clearance review. There are 85 electrical footprints plus four board-only holes. No tracks, vias or planes are present.

SW1–SW16 are a 4×4 grid on **19mm pitch**: x64.5/83.5/102.5/121.5 and y72/91/110/129. Each RGB LED is 7mm above its switch, with local 100nF. D1–D16 form a serpentine chain; LED ordering by row is `1 2 3 4 / 8 7 6 5 / 9 10 11 12 / 16 15 14 13`. Isolation diodes D20–D35 sit beside their switches. PCB spacing is provisional; keycaps and stems are not selected.

U1 STM32G030 is at (94,147), rotated 90°. Its decoupling, reset, column pull-ups and VBUS divider occupy the lower electronics strip. U8 AHCT at (118,151) drives RGB. J2 Tag-Connect at (66,154) needs unobstructed probe access. J1 six-way FFC at (93,165) faces the lower edge; U2 protects SDA/SCL. Route C1/VDD/GND as a short loop, keep LED return current out of the I²C/MCU reference path, and add ground fill/stitching after signal routing.

Native checks: **zero ERC violations**, 56 nets/235 endpoints/four intentional NCs, all schematic/PCB nets and UUIDs match, **zero DRC rule/parity violations and 211 unconnected items**. The assembly BOM/CPL has 84 parts; bare J2 is excluded. The independent panel audit checks every matrix diode, LED link and the Type A FFC reversal.

See [panel interface](README.md) for the exact cable, pinout, stock, ratings, tolerance caveat and firmware requirements. This is a floorplan, not a production release. Final enclosure/cable fit, current budget, firmware, component orientation and complete routing remain open.
