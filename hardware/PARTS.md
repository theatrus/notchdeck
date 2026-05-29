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
| **MCU+radio** | U1 | 1 | Ebyte E73-2G4M08S1C (nRF52840, onboard antenna; USB on pads 27/29/31) | C356849 | E73-2G4M08S1C (Ebyte) | `notchdeck:E73-2G4M08S1C` | `notchdeck:EBYTE_E73-2G4M08S1C` | E73 STEP | **vendor** |
| **3V3 LDO** | U2 | 1 | AP2112K-3.3 | C23380830 | AP2112K-3.3TRG1 (Diodes) | `Regulator_Linear:AP2112K-3.3` | `Package_TO_SOT_SMD:SOT-23-5` | stdlib | stdlib |
| **Charger** | U3 | 1 | MCP73831-2-OT | C424093 | MCP73831T-2ACI/OT (Microchip) | `Battery_Management:MCP73831-2-OT` | `Package_TO_SOT_SMD:SOT-23-5` | stdlib | stdlib |
| **Fuel gauge** | U4 | 1 | MAX17048 | C2682616 | MAX17048G+T10 (Analog Devices) | `notchdeck:MAX17048` | `Package_DFN_QFN:TDFN-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm` *(verify EP vs datasheet)* | stdlib FP | **vendor sym** |
| **USB-C** | J1 | 1 | USB-C 2.0 receptacle 16P | C2765186 | TYPE-C 16PIN 2MD(073) | `Connector:USB_C_Receptacle_USB2.0_16P` | `notchdeck:USB_C_Receptacle_HRO_TYPE-C-31-M-12` *(match JLCPCB part)* | vendor STEP | sym stdlib / **vendor FP** |
| **Lever sensor** | U5 | 1 | AS5600 (12-bit magnetic angle) | C499458 | AS5600-ASOM (AMS) | `notchdeck:AS5600` | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` | stdlib | **vendor sym** |
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

## Parts to vendor into `lib/` (symbol / footprint / 3D)

Follow the same workflow the other BenchBits projects use (see `lib/ATTRIBUTIONS.md`):
download a pre-built KiCad part, drop the `.kicad_mod` into `lib/footprints.pretty/`, the
STEP into `lib/3dmodels/`, append the symbol block to `lib/symbols/notchdeck.kicad_sym`,
and repoint the footprint's 3D path to `${KIPRJMOD}/../lib/3dmodels/<file>.step`.

| Part | Get symbol/footprint/3D from | Notes |
|---|---|---|
| **E73-2G4M08S1C** (U1) | SnapEDA / Component Search Engine (Samacsys); Ebyte datasheet for pad geometry | The load-bearing custom part. **Verify the module exposes USB D+/D- pads** (see risk below) before trusting the footprint. |
| **MAX17048** (U4) | SnapEDA / Component Search Engine (Analog Devices/Maxim) | Footprint is stdlib TDFN-8 2×2 — only the **symbol** needs vendoring. |
| **AS5600** (U5) | SnapEDA (AMS AS5600) | Footprint stdlib SOIC-8 — only the **symbol** needs vendoring. Needs a diametric magnet over the package (mechanical). |
| **USB-C 16P** (J1) | Match the exact JLCPCB part `TYPE-C 16PIN 2MD(073)` — community "TYPE-C-31-M-12" footprint or SnapEDA | Symbol is stdlib; the **footprint** must match the chosen receptacle's pads/posts. |
| **WS2812B-2020** (D1..) | SnapEDA / community if using the 2020 package | Or use the **5050** part (`C2843785`) which maps to the **stdlib** `LED_WS2812B_PLCC4_5.0x5.0mm` footprint — no vendoring. |
| **nPM1300** (U6, optional) | Nordic KiCad library / SnapEDA | Footprint stdlib QFN-32 5×5 — only the **symbol** needs vendoring. |

> Tip: prefer **Component Search Engine (Samacsys)** or **SnapEDA** parts — they bundle
> symbol + footprint + STEP together, which is exactly the "pre-built library + 3D model"
> path requested. Record each import (source + license) in `lib/ATTRIBUTIONS.md`.

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
