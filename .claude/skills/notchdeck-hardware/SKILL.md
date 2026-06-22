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
| Power | `power.kicad_sch` | USB-C J1, ESD U7, charger U3, LDO U2, load-share Q1/D_PP, fuel-gauge U4, battery J2, level-shifter U8 (DNP) |
| Lever | `lever.kicad_sch` | AS5600 U5 + I2C0 pull-ups/decoupling |
| Controls | `controls.kicad_sch` | 16 buttons (SW1–16), 16 WS2812B (D1–16), status/charge LEDs |

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
`                          ├─→ U3 MCP73831 charge in → VBAT → BAT+ (1S Li-ion)`
`                          └─→ D_PP Schottky → VSYS`; `BAT+ → Q1 PMOS load-share → VSYS`
`VSYS → U2 AP2112K-3.3 → +3V3` (feeds E73 VDD(19)+VDDH(23) tied; DCCH(25) open).
Fuel gauge U4 senses BAT+ (CELL=NC for 1-cell), ALRT→FG_ALRT(P0.15) pull-up.
MCP73831 PROG (R3) sets charge current; STAT→CHG_STAT(P0.17)+LED.

## Programming

SWD: SWDIO(37), SWDCLK(39), nRESET(26), +3V3, GND — wired to **both** J3
(2×05 1.27 mm header) and **J4 (`Conn_ARM_SWD_TagConnect_TC2030-NL`, no-legs
Tag-Connect pads)** in parallel. USB-C is the user UF2 upgrade path.

## Lever sensing (firmware-contained choice)

15 discrete detents (EB, B8–B1, N, P1–P5). Two interchangeable front-ends; the
choice is contained in firmware `lever.c`:
- **Option 1 (default): AS5600** magnetic angle on I²C0 — absolute, no homing.
- **Option 2: cam + 4 Gray-coded switches** (Hall DRV5032 or snap-action),
  decodes as 4 GPIO, reusing the freed I²C0 pins + 2 analog spares.

## Status

**Schematic placed, not yet wired.** All parts are on the right sheets with
footprints + per-sheet wiring notes. Next step: inter-sheet hierarchical labels +
power rails in eeschema, per the notes / NETPLAN.md. The `.kicad_pcb` is still an
empty scaffold.
