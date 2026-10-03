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
| Controls | `controls.kicad_sch` | FFC J15, SW18/19 Select/Start, status/charge LEDs, J9 reverser |

## Hard constraints (do not violate)

1. **Two I²C buses.** AS5600 (U5) and MAX17048 (U4) **both answer at address
   0x36** → they MUST be on separate buses. AS5600 = **TWIM0** (SDA P0.26/pad12,
   SCL P0.06/pad14); MAX17048 = **TWIM1** (SDA P0.12/pad20, SCL P0.07/pad22).
   4.7 kΩ pull-ups per bus to +3V3.
2. **Rev E frees former button GPIOs.** NFC pins P0.09/P0.10 are NC; older Rev C/D firmware used them as buttons. Do not drive panel wiring with the old overlay.
3. **No LFXO.** No 32.768kHz crystal is populated; retain internal RC LFCLK. P0.00/P0.01 are now NC.
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
J5 pins2–5 carry four brake/combined Gray bits; J12 pins2–4 carry three power
bits on P0.29/P0.31/P0.30. Both use pin1 GND and final pin 3V3 (unwired in passive harnesses).
Rev D replaces the individual Rev C bit connectors with 6-pin/5-pin keyed ports. Rev E leaves fourteen former button/RGB GPIOs NC. New cam maps reserve all-open as invalid.

## Status

**Revision E is wired on two assemblies.** `make verify` checks the main 318 endpoints and panel 235 endpoints, strict zero ERC, PCB nets/UUIDs and both BOMs. Both PCBs are unrouted. Main is 115×90mm/four layers; panel is 86×120mm/two layers with 4×4 buttons. Main SW18/19 retain Select/Start; the STM32G030 scans the diode matrix and controls USB-only RGB locally. FFC main J15 pin n connects to panel J1 pin 7−n with the specified Molex Type A cable. See `hardware/notchdeck-buttons/README.md` for bonded pin aliases, I²C target 0x20, SWD and firmware requirements. Panel and main integration firmware remain unimplemented. Q1 and charger constraints are unchanged; both boards have fully assigned JLCPCB BOMs. See `hardware/README.md` for pre-fabrication work.
