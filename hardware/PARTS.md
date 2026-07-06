# NotchDeck One — parts mapping (real parts → KiCad symbols / footprints / 3D)

Maps every BOM line to a **real, JLCPCB-sourced part** (see
[`../docs/04-bom-sourcing.md`](../docs/04-bom-sourcing.md)) and to a concrete KiCad
**symbol + footprint + 3D model**, preferring **KiCad standard libraries** and falling
back to **vendored pre-built library parts** (with 3D) only where the stdlib lacks them.

Verified against the installed **KiCad 10** standard libraries. Symbol/footprint
properties to set on each part so the BOM/CPL flow works: `Value`, `Footprint`,
`LCSC`, `MPN`, `Manufacturer` (the Makefile/`jlcpcb-package.sh` export these columns).

Legend — **Status**: `stdlib` = ships with KiCad · `vendor` = drop into `lib/` (see below).

## Default build (Option B power path)

| Block | Ref | Qty | Part / Value | LCSC | MPN (Manufacturer) | KiCad symbol | Footprint | 3D | Status |
|---|---|---|---|---|---|---|---|---|---|
| **MCU+radio** | U1 | 1 | Ebyte E73-2G4M08S1C (nRF52840, onboard antenna; USB on pads 27/29/31) | C356849 | E73-2G4M08S1C (Ebyte) | `notchdeck:E73-2G4M08S1C` | `notchdeck:EBYTE_E73-2G4M08S1C` | E73 STEP | **vendored ✓** |
| **3V3 LDO** | U2 | 1 | AP2112K-3.3 | C23380830 | AP2112K-3.3TRG1 (Diodes) | `Regulator_Linear:AP2112K-3.3` | `Package_TO_SOT_SMD:SOT-23-5` | stdlib | stdlib |
| **Charger** | U3 | 1 | MCP73831-2-OT | C424093 | MCP73831T-2ACI/OT (Microchip) | `Battery_Management:MCP73831-2-OT` | `Package_TO_SOT_SMD:SOT-23-5` | stdlib | stdlib |
| **Fuel gauge** | U4 | 1 | MAX17048 | C2682616 | MAX17048G+T10 (Analog Devices) | `notchdeck:MAX17048` | `Package_DFN_QFN:TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm` *(verify EP vs land pattern)* | stdlib FP | **sym authored ✓** |
| **USB-C** | J1 | 1 | USB-C 2.0 receptacle 16P (HRO) | C165948 | TYPE-C-31-M-12 | `Connector:USB_C_Receptacle_USB2.0_16P` | `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` | stdlib | **all stdlib ✓** |
| **Lever sensor** | U5 | 1 | AS5600 (12-bit magnetic angle) | C499458 | AS5600-ASOM (AMS) | `notchdeck:AS5600` | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` | stdlib | **sym authored ✓** |
| **Notch/status LEDs** | D1.. | ~16 | WS2812B (addressable RGB) | C965555 *(2020)* / C2843785 *(5050)* | WS2812B-2020 / XL-5050RGBC-2812B | `LED:WS2812B` | 2020: `notchdeck:LED_WS2812B-2020` · 5050: `LED_SMD:LED_WS2812B_PLCC4_5.0x5.0mm` | stdlib (5050) | sym stdlib / FP per pkg |
| **Cab buttons** | SW1.. | ≤16 | SMD tactile | *(pick in-stock)* | e.g. TS-1187A / SKRPACE010 | `Switch:SW_Push` | stdlib `Button_Switch_SMD:*` or vendored | stdlib | stdlib |
| **Battery conn.** | J2 | 1 | JST-PH 2-pin | *(in-stock)* | S2B-PH-SM4-TB (JST) | `Connector:Conn_01x02` *(or Connector_JST sym)* | `Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal` | stdlib | stdlib |
| **CC resistors** | R1,R2 | 2 | 5.1 kΩ 0402 | *(in-stock)* | — | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | stdlib | stdlib |
| **Decoupling** | C1.. | n | 100 nF / 1 µF / 10 µF 0402-0805 | *(in-stock)* | — | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` (etc.) | stdlib | stdlib |
| **Charge-rate R** | R3 | 1 | MCP73831 PROG (set Icharge) | *(in-stock)* | — | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | stdlib | stdlib |
| **Status/charge LEDs** | D17.. | 1-2 | 0603 LED | *(in-stock)* | — | `Device:LED` | `LED_SMD:LED_0603_1608Metric` | stdlib | stdlib |

## Optional: Option A integrated PMIC (replaces U2/U3/U4)

| Block | Ref | Part | LCSC | MPN | KiCad symbol | Footprint | 3D | Status |
|---|---|---|---|---|---|---|---|---|
| PMIC | U6 | nPM1300 | C7501206 | nPM1300-QEAA (Nordic) | `notchdeck:nPM1300` | `Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.6x3.6mm` | vendor STEP | **vendor sym** |

## Power-path, protection & programming (from the net plan)

The parts `NETPLAN.md` flagged as "not yet in BOM" — all map to **KiCad stdlib symbols** with
shipped 3D, all stocked at JLCPCB.

| Block | Ref | Part / value | LCSC | MPN (Manufacturer) | KiCad symbol | Footprint | Status |
|---|---|---|---|---|---|---|---|
| **USB ESD** | U7 | USBLC6-2SC6 | C2687116 | USBLC6-2SC6 (ST) | `Power_Protection:USBLC6-2SC6` | `Package_TO_SOT_SMD:SOT-23-6` | stdlib |
| **Power-path PMOS** | Q1 | AO3401A (P-ch, load-share) | C15127 *(basic)* | AO3401A (AOS) | `Transistor_FET:Q_PMOS_GSD` | `Package_TO_SOT_SMD:SOT-23` | stdlib |
| **Power-path diode** | D_PP | B5819W Schottky (VBUS→VSYS) | C8598 *(basic)* | B5819W (Slkor) | `Device:D_Schottky` | `Diode_SMD:D_SOD-123` | stdlib |
| **Reset button** | SW_RST | SMD tactile | *(in-stock)* | e.g. TS-1187A | `Switch:SW_Push` | `Button_Switch_SMD:*` | stdlib |
| **SWD header** | J3 | 2×5 1.27 mm (Cortex debug) | *(in-stock / Tag-Connect)* | — | `Connector:Conn_ARM_JTAG_SWD_10` | `Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical_SMD` | stdlib |
| **WS2812 level shift** *(opt, DNP unless strip @5 V)* | U8 | 74LVC1G125 | C52098142 | 74LVC1G125W5 (Diodes) | `74xGxx:74LVC1G125` | `Package_TO_SOT_SMD:SOT-23-5` | stdlib |
| **Gate / pull resistors** | R_PP.. | 100 kΩ 0402 | *(in-stock)* | — | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | stdlib |
| **I²C pull-ups** | R_I2C.. | 4.7 kΩ 0402 ×4 | *(in-stock)* | — | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | stdlib |

Notes: AO3401A + B5819W are **JLCPCB basic parts** (no feeder fee). SWD: a Tag-Connect
`TC2030-IDC-NL` footprint is the no-connector alternative to the 2×5 header. The level shifter is
only populated if the WS2812 strip is run at 5 V (3.3 V data into a 5 V strip can be marginal);
default-DNP if the strip runs at 3.3 V.

## Coded-switch lever input (Option 2 — 4-bit binary/Gray, coexists with AS5600)

A 4-bit coded switch reports notch position as pure GPIO (see `NETPLAN.md` → "Lever sensing").
Its 4 bits are on **dedicated GPIO** (P0.03/P0.28/P0.04/P0.05), so this coexists with the AS5600
(U5) — populate either front-end or both. The switches themselves live in the **mascon handle** and
wire in on a harness: **one 2-pin JST-PH per bit** (signal + GND), each bit active-low with an
on-board RC debounce. These are on-board parts of the default build (on the Lever sheet):

| Block | Ref | Qty | Part / value | MPN (Manufacturer) | KiCad symbol | Footprint | Status |
|---|---|---|---|---|---|---|---|
| **Coded-switch conn.** | J5–J8 | 4 | JST-PH 2-pin (per bit: signal + GND) | S2B-PH-SM4-TB (JST) | `Connector_Generic:Conn_01x02` | `Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal` | stdlib |
| **Bit pull-ups** | R14–R17 | 4 | 10 kΩ 0402 (to +3V3) | — | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | stdlib |
| **Bit series R** | R18–R21 | 4 | 1 kΩ 0402 (RC debounce + GPIO/ESD limit) | — | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | stdlib |
| **Debounce caps** | C14–C17 | 4 | 100 nF 0402 (to GND) | — | `Device:C` | `Capacitor_SMD:C_0402_1005Metric` | stdlib |

Debounce per bit: `+3V3 → 10k pull-up → bit line (Jn.1, switch to GND)`, then `1k series → GPIO`
with `100 nF → GND`. τ ≈ 1.1 ms on release / 0.1 ms on press — a small hardware debounce; firmware
adds a few ms on top. The 1 kΩ series also limits cap-discharge current and gives cable ESD margin.
All stdlib; same JST-PH family as the battery J2, so no new symbols/footprints. (If any switch is a
maintained/latching type or a shared-common wafer, tie its common to a GND pin and keep the per-bit
RC — the topology is unchanged.)

### On-board cam alternative (in place of the mascon harness)

If the 4 switches are actuated by an **on-board cam** on the shaft rather than an external mascon,
drop J5–J8 and drive the same 4 nets (LEVER_S0–S3) from a cam switch element — pick one:

| Block | Ref | Part | LCSC | MPN | KiCad symbol | Footprint | Status |
|---|---|---|---|---|---|---|---|
| Hall switch ×4 (recommended) | U5a–d | DRV5032FB | C2655033 | DRV5032FBDBZR (TI) | generic 3-pin / vendor | `Package_TO_SOT_SMD:SOT-23` | **vendor sym** (not in stdlib) |
| or snap-action ×4 | SW_La–d | SS-5GL (Omron) | C87120 | SS-5GL2 | `Switch:SW_SPST` | through-hole / hand-mount | stdlib sym |
| Hall pull-ups / lobe magnets | — | 4.7 kΩ + small NdFeB | — | — | `Device:R` | `Resistor_SMD:R_0402_1005Metric` | stdlib |

Notes: DRV5032FB is contactless (no wear), SOT-23, JLCPCB-stocked (~13k, $0.20) — needs a 3-pin
Hall-switch symbol (generic or vendored; not in KiCad stdlib). SS-5GL is the authentic cam
microswitch (through-hole, ~$0.60) — most authentic feel, but contacts wear and it's hand-mounted.

## Library status (what's in `lib/` now)

All default-build parts now resolve to a symbol + footprint + 3D model. Verified with
`kicad-cli sym upgrade` (symbols parse) and `kicad-cli fp upgrade` (footprint parses).

| Part | Symbol | Footprint | 3D | Done? |
|---|---|---|---|---|
| **E73-2G4M08S1C** (U1) | `notchdeck:E73-2G4M08S1C` (43 pins) | `notchdeck:EBYTE_E73-2G4M08S1C` (43 pads) | `lib/3dmodels/EBYTE_E73-2G4M08S1C.step` | ✅ vendored from nrfmicro (public domain) |
| **AS5600** (U5) | `notchdeck:AS5600` (authored, datasheet pinout) | stdlib `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` | stdlib (shipped) | ✅ |
| **MAX17048** (U4) | `notchdeck:MAX17048` (authored, datasheet pinout, incl. EP=pin9) | stdlib `Package_DFN_QFN:TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm` | stdlib (shipped) | ✅ |
| **USB-C** (J1) | stdlib `Connector:USB_C_Receptacle_USB2.0_16P` | stdlib `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` | stdlib (shipped) | ✅ all stdlib (use LCSC C165948) |
| AP2112K / MCP73831 / WS2812B(5050) / passives / JST | stdlib | stdlib | stdlib | ✅ |
| **nPM1300** (U6, Option A only) | _not yet_ — Nordic KiCad lib / SnapEDA | stdlib `Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.6x3.6mm` | needs STEP | ☐ deferred (only for Option A) |

Notes / to verify in KiCad GUI:
- Authored AS5600/MAX17048 symbols: double-check pin↔number against the datasheet figure
  (done from datasheet, but confirm in ERC) and that the MAX17048 stdlib EP land matches the
  Maxim recommended land pattern.
- E73 3D model: confirm orientation/offset aligns with the footprint origin in the 3D viewer
  (vendored STEP placed at 0/0/0 — may need a rotate/offset tweak).
- If you prefer the 2020 WS2812B (`C965555`) over the 5050, that footprint must be vendored;
  the 5050 (`C2843785`) is stdlib and needs nothing.

> The import workflow (for nPM1300 or any future part) lives in `lib/ATTRIBUTIONS.md`:
> drop `.kicad_mod` → `lib/footprints.pretty/`, STEP → `lib/3dmodels/`, append the symbol to
> `lib/symbols/notchdeck.kicad_sym`, repoint the 3D path to `${KIPRJMOD}/../lib/3dmodels/`.

## ✓ Verified — E73 exposes USB (dual-mode confirmed)

Confirmed from Ebyte's official E73-2G4M08S1C pin-definition table (43 pads total): the
module brings the nRF52840 USB lines out to castellated pads, so the dual-mode USB design
works on the E73 as-is — **no parts change, bare-chip fallback not needed.**

| Pad | Name | Function | Wire to |
|---|---|---|---|
| 27 | VBS | USB 5V (VBUS) — feeds nRF52840 USB regulator + VBUS-detect | USB-C VBUS (+ `vbus_present()` sense) |
| 29 | D− | USB D− | USB-C D− (CC-side pair) |
| 31 | D+ | USB D+ | USB-C D+ |

Corroborated by USB(-C) boards built on this exact module: joric/nrfmicro and
ddB0515/nRF52840-BBoard. Source: <https://www.cdebyte.com/products/E73-2G4M08S1C/2>.

## JLCPCB assembly notes

- BOM/CPL are generated by `make jlc-notchdeck-one` (→ `notchdeck-one-jlcpcb.zip`).
- Set `LCSC` on every assembled part so JLCPCB auto-matches; mark non-assembled parts DNP.
- QFN/SOT/DFN parts may need JLCPCB-specific **rotation offsets** — verify in JLCPCB's CPL
  preview before confirming (the package script's README.txt reiterates this).
