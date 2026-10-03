# NotchDeck One — selected JLCPCB parts

The current assembly BOM has **144 components across 32 JLCPCB catalog part numbers**.
Selections were checked on **2026-10-03**. The schematic exports the selected LCSC
code, exact manufacturer/MPN, datasheet and assembly notes for each component.

- [JLCPCB upload BOM](notchdeck-one/bom/jlcpcb-bom.csv)
- [Tracking BOM](notchdeck-one/bom/bom.csv)
- [Reviewed selection data and dated stock snapshot](notchdeck-one/bom/jlcpcb-parts.json)
- [Direct JLCPCB available-stock audit, 2026-10-03](notchdeck-one/bom/jlcpcb-stock.csv)
- [Sourcing evidence, changes and review limits](notchdeck-one/bom/README.md)

The PCB remains an unrouted placement study. Catalog matching does not establish
assembly eligibility, final stock, electrical margins or enclosure fit.

## Current assembly

| References | Qty | Selected MPN | Manufacturer | JLCPCB part | KiCad footprint |
|---|---:|---|---|---|---|
| C1… (see CSV for exact list) | 33 | CL05B104KO5NNNC | Samsung Electro-Mechanics | [C1525](https://jlcpcb.com/partdetail/C1525) | `Capacitor_SMD:C_0402_1005Metric` |
| C18, C19 | 2 | CL21A475KAQNNNE | Samsung Electro-Mechanics | [C1779](https://jlcpcb.com/partdetail/C1779) | `Capacitor_SMD:C_0805_2012Metric` |
| D18 | 1 | KT-0603R | Hubei KENTO Elec | [C2286](https://jlcpcb.com/partdetail/C2286) | `LED_SMD:LED_0603_1608Metric` |
| R3 | 1 | 0402WGF2001TCE | UNI-ROYAL | [C4109](https://jlcpcb.com/partdetail/C4109) | `Resistor_SMD:R_0402_1005Metric` |
| U8 | 1 | SN74AHCT1G125DBVR | TI | [C7484](https://jlcpcb.com/partdetail/C7484) | `Package_TO_SOT_SMD:SOT-23-5` |
| U7, U10, U11 | 3 | USBLC6-2SC6 | ST | [C7519](https://jlcpcb.com/partdetail/C7519) | `Package_TO_SOT_SMD:SOT-23-6` |
| D19 | 1 | B5819W SL | JSCJ | [C8598](https://jlcpcb.com/partdetail/C8598) | `Diode_SMD:D_SOD-123` |
| R5, R12, R13, R18, R19, R20, R21, R25, R34, R35, R36 | 11 | 0402WGF1001TCE | UNI-ROYAL | [C11702](https://jlcpcb.com/partdetail/C11702) | `Resistor_SMD:R_0402_1005Metric` |
| Q1 | 1 | AO3401A | AOS | [C15127](https://jlcpcb.com/partdetail/C15127) | `Package_TO_SOT_SMD:SOT-23` |
| C5, C9 | 2 | CL21A106KAYNNNE | Samsung Electro-Mechanics | [C15850](https://jlcpcb.com/partdetail/C15850) | `Capacitor_SMD:C_0805_2012Metric` |
| R37, R38 | 2 | 0603WAF0000T5E | UNI-ROYAL | [C21189](https://jlcpcb.com/partdetail/C21189) | `Resistor_SMD:R_0603_1608Metric` |
| R11 | 1 | 0402WGF3300TCE | UNI-ROYAL | [C25104](https://jlcpcb.com/partdetail/C25104) | `Resistor_SMD:R_0402_1005Metric` |
| R4, R8, R22, R23, R24, R26 | 6 | 0402WGF1003TCE | UNI-ROYAL | [C25741](https://jlcpcb.com/partdetail/C25741) | `Resistor_SMD:R_0402_1005Metric` |
| R14, R15, R16, R17, R31, R32, R33, R39, R40, R41 | 10 | 0402WGF1002TCE | UNI-ROYAL | [C25744](https://jlcpcb.com/partdetail/C25744) | `Resistor_SMD:R_0402_1005Metric` |
| R6, R7, R9, R10, R27, R28, R29, R30 | 8 | 0402WGF4701TCE | UNI-ROYAL | [C25900](https://jlcpcb.com/partdetail/C25900) | `Resistor_SMD:R_0402_1005Metric` |
| R1, R2 | 2 | 0402WGF5101TCE | UNI-ROYAL | [C25905](https://jlcpcb.com/partdetail/C25905) | `Resistor_SMD:R_0402_1005Metric` |
| C13 | 1 | CL21B105KBFNNNE | Samsung Electro-Mechanics | [C28323](https://jlcpcb.com/partdetail/C28323) | `Capacitor_SMD:C_0805_2012Metric` |
| U3 | 1 | MCP73832T-2ACI/OT | MICROCHIP | [C38066](https://jlcpcb.com/partdetail/C38066) | `Package_TO_SOT_SMD:SOT-23-5` |
| U2 | 1 | AP2112K-3.3TRG1 | DIODES | [C51118](https://jlcpcb.com/partdetail/C51118) | `Package_TO_SOT_SMD:SOT-23-5` |
| C3, C4, C7, C8, C12 | 5 | CL05A105KA5NQNC | Samsung Electro-Mechanics | [C52923](https://jlcpcb.com/partdetail/C52923) | `Capacitor_SMD:C_0402_1005Metric` |
| J1 | 1 | TYPE-C-31-M-12 | Korean Hroparts Elec | [C165948](https://jlcpcb.com/partdetail/C165948) | `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` |
| J9 | 1 | S3B-PH-SM4-TB(LF)(SN) | JST | [C265101](https://jlcpcb.com/partdetail/C265101) | `Connector_JST:JST_PH_S3B-PH-SM4-TB_1x03-1MP_P2.00mm_Horizontal` |
| J10, J11 | 2 | S4B-PH-SM4-TB(LF)(SN) | JST | [C265102](https://jlcpcb.com/partdetail/C265102) | `Connector_JST:JST_PH_S4B-PH-SM4-TB_1x04-1MP_P2.00mm_Horizontal` |
| J2, J5, J6, J7, J8, J12, J13, J14 | 8 | S2B-PH-SM4-TB(LF)(SN) | JST | [C295747](https://jlcpcb.com/partdetail/C295747) | `Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal` |
| SW1… (see CSV for exact list) | 17 | TS-1187A-B-A-B | XKB Connection | [C318884](https://jlcpcb.com/partdetail/C318884) | `Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A` |
| U1 | 1 | E73-2G4M08S1C | Ebyte | [C356849](https://jlcpcb.com/partdetail/C356849) | `notchdeck:EBYTE_E73-2G4M08S1C` |
| J3 | 1 | FTSH-105-01-L-DV-K-TR | Samtec | [C448647](https://jlcpcb.com/partdetail/C448647) | `notchdeck:Samtec_FTSH-105-01-L-DV-K` |
| U5 | 1 | AS5600-ASOT | ams | [C499458](https://jlcpcb.com/partdetail/C499458) | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` |
| D17 | 1 | XL-1608SYGC-06 | XINGLIGHT | [C965805](https://jlcpcb.com/partdetail/C965805) | `LED_SMD:LED_0603_1608Metric` |
| U9 | 1 | TCA9543APWR | TI | [C2653307](https://jlcpcb.com/partdetail/C2653307) | `Package_SO:TSSOP-14_4.4x5mm_P0.65mm` |
| U4 | 1 | MAX17048G+T10 | MAXIM | [C2682616](https://jlcpcb.com/partdetail/C2682616) | `Package_DFN_QFN:TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm` |
| D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, D12, D13, D14, D15, D16 | 16 | XL-5050RGBC-2812B | XINGLIGHT | [C2843785](https://jlcpcb.com/partdetail/C2843785) | `notchdeck:LED_XINGLIGHT_XL-5050RGBC-2812B` |

## Symbols, footprints and models

The generated schematic retains functional symbol values (for example `WS2812B`
and `LED`); the **MPN/LCSC fields select the purchased part**. The generator loads
`notchdeck-one/bom/jlcpcb-parts.json` and rejects missing or duplicate assignments.
Part choices belong in that file; circuitry and symbol selection remain in
`scripts/notchdeck-one.schgen.py`.

Standard KiCad symbols/footprints are used where they match. E73, AS5600, MAX17048
TCA9543A and passive SWD connector symbols are project-local; their provenance is in
[lib/ATTRIBUTIONS.md](lib/ATTRIBUTIONS.md). The selected RGB LED and keyed Samtec
header now use project-local footprints drawn from manufacturer dimensions.
They do not yet have dedicated 3D models. Standard library models and the vendored
E73 STEP are previews, not evidence of mechanical fit.

J4 is a bare TC2030-NL contact pattern, excluded from BOM and placement output.
The four PCB-only mounting holes likewise have no assembly part. Mating cables,
protected cell, programming probe, magnet, lever/cam hardware, external switches,
keycaps and enclosure are outside this PCB BOM.

## Electrical selection constraints

- U3: **MCP73832T-2ACI/OT / C38066**, open-drain STAT; no MCP73831 substitution.
- U8: **SN74AHCT1G125DBVR / C7484**, TTL-compatible input at a 5 V supply.
  An AHC/HC part is not a drop-in replacement.
- U2: **Diodes AP2112K-3.3TRG1 / C51118**; the previous code identified a different manufacturer.
- U7: **ST USBLC6-2SC6 / C7519**; the previous code identified a different manufacturer.
- D1–D16: **XINGLIGHT XL-5050RGBC-2812B / C2843785**, 5050 four-pad package;
  use its documented pad map and USB-only supply, with a firmware current limit.
- D17: **XL-1608SYGC-06 / C965805**, low-voltage yellow-green indicator.
  D18: **KT-0603R / C2286**, red charge indicator. They must remain separate BOM rows.
- J2, J5–J8 and J12–J14 share the same two-pin JST part; harness functions and pin assignments
  differ. J9 uses the matching three-pin family member.
- U4 remains **MAX17048G+T10 / C2682616**. Its exact exposed-pad land pattern still
  needs review, as does the imported E73 footprint and antenna clearance.

Alternative PMIC and cam/Hall architectures in [the design research](../docs/04-bom-sourcing.md)
are not populated or sourced by this BOM. See [NETPLAN.md](NETPLAN.md) for the
implemented wiring and [FLOORPLAN.md](notchdeck-one/FLOORPLAN.md) for open layout work.

## Regeneration and checks

```sh
# Close the NotchDeck schematic editor before forced generation.
KSCHGEN_FORCE=1 make gen-notchdeck-one
make verify-notchdeck-one verify-pcb-notchdeck-one verify-bom-notchdeck-one
```

Run from `hardware/`. The PCB must be updated from the schematic after a part or
footprint change. Refresh the tracked CSV snapshots after checks pass. Direct JLCPCB
stock observations are recorded separately from the older community snapshot;
recheck availability and CPL orientation in
JLCPCB before any future assembly order.
