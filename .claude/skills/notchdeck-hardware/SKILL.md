---
name: notchdeck-hardware
description: >-
  NotchDeck One hardware design reference — the dual-mode (USB + BLE) combined/dual-handle
  train master controller built on an Ebyte E73-2G4M08S1C (nRF52840). Use when
  reasoning about the schematic, pin assignments, power architecture, the I2C
  bus split, programming/SWD, the lever sensor options, or which part goes where.
  The source-of-truth docs are hardware/PARTS.md and hardware/NETPLAN.md.
---

# NotchDeck One — hardware design reference

Dual-mode (USB-C wired + BLE) combined/dual-handle train-master controller. MCU+radio is
the **Ebyte E73-2G4M08S1C** module (nRF52840, on-board antenna, USB pads exposed).
Lives in `hardware/notchdeck-one/`. To modify the schematic, use the
**kicad-schgen** skill (it is generated from a manifest, not hand-edited).

## Source of truth

- `hardware/PARTS.md` — every BOM line → real JLCPCB part + KiCad symbol /
  footprint / 3D model. **Start here for parts.**
- `hardware/NETPLAN.md` — E73 pad → peripheral net plan, power architecture, I2C
  plan, lever options, programming/reset. **Start here for wiring.**
- `docs/0*.md` — research, emulation-protocol spec, hardware/firmware arch, BOM
  sourcing, firmware update.
- The full E73 43-pad map also lives in the **MCU sheet's on-canvas note**.

## Hierarchical sheet structure

| Sheet | File | Holds |
|---|---|---|
| MCU & Programming | `mcu.kicad_sch` | U1 E73, decoupling, SWD header J3, Tag-Connect J4, reset |
| Power | `power.kicad_sch` | USB-C J1, ESD U7, charger U3, LDO U2, load-share Q1/D19, fuel-gauge U4, battery J2 |
| Lever | `lever.kicad_sch` | AS5600 U5, TCA9543A U9, dual magnetic ports and 7 Gray inputs |
| Controls | `controls.kicad_sch` | 16 buttons (SW1–16), 16 WS2812B (D1–16), status/charge LEDs, U8 AHCT buffer, J9 reverser |

## Hard constraints (do not violate)

1. **Two I²C buses.** AS5600 (U5) and MAX17048 (U4) **both answer at address
   0x36** → they MUST be on separate buses. AS5600 = **TWIM0** (SDA P0.26/pad12,
   SCL P0.06/pad14); MAX17048 = **TWIM1** (SDA P0.12/pad20, SCL P0.07/pad22).
   4.7 kΩ pull-ups per bus to +3V3.
2. **NFC pins as GPIO.** P0.09/P0.10 (pads 41/43) are reused as GPIO → firmware
   must set `nfct-pins-as-gpios` in the UICR devicetree node.
3. **No LFXO.** P0.00/P0.01 (pads 11/13) are GPIO → LFCLK runs from the internal
   RC (fine for BLE). To fit a 32.768 kHz crystal, reclaim these and drop
   BTN11/BTN12.
4. **nRESET in UICR.** P0.18 (pad 26) is `nRESET` → enable reset in UICR (Zephyr
   default). Bootloader double-tap-to-DFU; no separate BOOT pin.

## Power architecture

`USB-C VBUS(5V) ──[U7 ESD]──┬─→ E73 VBUS(27)` (on-chip USB reg + vbus_present())
`                          ├─→ U3 MCP73832 charge in → VBAT → BAT+ (1S Li-ion)`
`                          └─→ D19 Schottky → VSYS`; `BAT+ → Q1 PMOS load-share → VSYS`
`VSYS → U2 AP2112K-3.3 → +3V3` (feeds E73 VDD(19)+VDDH(23) tied; DCCH(25) open).
Fuel gauge U4 senses BAT+ (CELL and VDD to BAT+), ALRT→FG_ALRT(P0.15) pull-up.
MCP73832 PROG (R3) sets charge current; STAT→CHG_STAT(P0.17)+LED.

## Programming

SWD: SWDIO(37), SWDCLK(39), nRESET(26), +3V3, GND — wired to **both** J3
(2×05 1.27 mm header) and **J4 (`Conn_ARM_SWD_TagConnect_TC2030-NL`, no-legs
Tag-Connect pads)** in parallel. USB-C is the user UF2 upgrade path.

## Handle sensing

Combined 15-position mascon, or separate power Off/P1–P5 and brake Release/B1–B8/EB.
Each handle independently selects AS5600 magnetic or Gray contacts in firmware.
See `docs/06-handle-interfaces.md` for connector pinouts, cam maps and calibration.
U9 TCA9543A (0x70) separates two address-0x36 magnetic channels on TWIM0; enable
only one at a time. Channel0=power/combined J10/U5, channel1=brake J11. Remove both
R37/R38 before using an external sensor on J10. MAX17048 stays on TWIM1.
J5–J8 are four brake/combined Gray bits; J12–J14 use P0.29/P0.31/P0.30 for three
power bits. No spare GPIO remains. New cam maps reserve all-open as invalid.

## Status

**Revision C is wired.** Run `make verify-notchdeck-one`: zero ERC violations,
all 442 endpoints checked. Q1 drain=BAT+, source=VSYS; R4 pulls gate down, R5=1k
from VBUS to gate. U3 is MCP73832 (open-drain STAT). RGB is USB-only through U8
SN74AHCT1G125, with local decoupling; firmware must hold DIN low without USB.
J9 is a 3-pin SPDT center-off reverser with midpoint bias and ADC filtering.
The PCB has an unrouted 4×4 floorplan and a fully assigned JLCPCB catalog BOM.
See `hardware/README.md` for remaining electrical,
procurement, firmware and layout checks before fabrication.
