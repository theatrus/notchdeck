---
name: notchdeck-hardware
description: >-
  NotchDeck One hardware design reference — the dual-mode (USB + BLE) one-handle
  train master controller built on an Ebyte E73-2G4M08S1C (nRF52840). Use when
  reasoning about the schematic, pin assignments, power architecture, the I2C
  bus split, programming/SWD, the lever sensor options, or which part goes where.
  The source-of-truth docs are hardware/PARTS.md and hardware/NETPLAN.md.
---

# NotchDeck One — hardware design reference

Dual-mode (USB-C wired + BLE) one-handle train-master controller. MCU+radio is
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
| Lever | `lever.kicad_sch` | AS5600 U5 + I2C0 pull-ups/decoupling |
| Controls | `controls.kicad_sch` | 16 buttons (SW1–16), 16 WS2812B (D1–16), status/charge LEDs, U8 AHCT buffer, J9 reverser |

## Hard constraints (do not violate)

1. **Two I²C buses.** AS5600 (U5) and MAX17048 (U4) **both answer at address
   0x36** → they MUST be on separate buses. AS5600 = **TWIM0** (SDA P0.26/pad12,
   SCL P0.06/pad14); MAX17048 = **TWIM1** (SDA P0.12/pad20, SCL P0.07/pad22).
   4.7 kΩ pull-ups per bus to +3V3.
2. **NFC pins as GPIO.** P0.09/P0.10 (pads 41/43) are reused as GPIO → firmware
   must set `CONFIG_NFCT_PINS_AS_GPIO`.
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

## Lever sensing (firmware-contained choice)

15 discrete detents (EB, B8–B1, N, P1–P5). Two interchangeable front-ends; the
choice is contained in firmware `lever.c`:
- **Option 1 (default): AS5600** magnetic angle on I²C0 — absolute, no homing.
- **Option 2: cam + 4 Gray-coded switches** (Hall DRV5032 or snap-action),
  decodes as 4 GPIO, using dedicated P0.03/P0.28/P0.04/P0.05 pins; both front-ends can coexist.

## Status

**Revision B is wired.** Run `make verify-notchdeck-one`: zero ERC violations,
all 360 endpoints checked. Q1 drain=BAT+, source=VSYS; R4 pulls gate down, R5=1k
from VBUS to gate. U3 is MCP73832 (open-drain STAT). RGB is USB-only through U8
SN74AHCT1G125, with local decoupling; firmware must hold DIN low without USB.
J9 is a 3-pin SPDT center-off reverser with midpoint bias and ADC filtering.
The PCB has an unrouted 4×4 floorplan and a fully assigned JLCPCB catalog BOM.
See `hardware/README.md` for remaining electrical,
procurement, firmware and layout checks before fabrication.
