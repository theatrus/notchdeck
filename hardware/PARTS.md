# NotchDeck Rev G logic / Rev E panel — selected JLCPCB parts

The logic and button assemblies contain **213 installed parts across 44 JLCPCB codes** per complete set. Stock rows retain their observation dates; actuator additions were checked on **2026-10-04 PDT**; five sets need **1,065 installed parts**, before attrition.

The button MCU is **STM32G030F6P6TR / C529330**, selected from the shared private inventory. Its small TSSOP-20 package, internal oscillator, I²C target and timer/DMA support fit the scanner without external flash or a crystal. The community catalog estimate was about $0.80; owned-stock purchase cost is not recorded. Private balances stay outside this repository.

- [Logic assembly BOM](notchdeck-one/bom/jlcpcb-bom.csv) and [button assembly BOM](notchdeck-buttons/bom/jlcpcb-bom.csv).
- [Combined stock requirement for five sets](jlcpcb-five-set-stock.csv), counting shared parts on both boards.
- [System BOM](system-bom.csv): one DigiKey Molex 0151670213 FFC per set, excluded from PCB assembly BOMs.
- Part selection JSON under each board’s `bom/` drives schematic properties. Dated public stock and tracking exports live beside it.

## Exact selections

References are prefixed L (logic) or B (button). Quantities are per complete set.

| References | Qty | MPN | Manufacturer | JLCPCB | Footprint |
|---|---:|---|---|---|---|
| L: C1… (18; exact list in CSV); B: C21… (21; exact list in CSV) | 39 | CL05B104KO5NNNC | Samsung Electro-Mechanics | [C1525](https://jlcpcb.com/partdetail/C1525) | `Capacitor_SMD:C_0402_1005Metric` |
| L: C18, C19; B: C2 | 3 | CL21A475KAQNNNE | Samsung Electro-Mechanics | [C1779](https://jlcpcb.com/partdetail/C1779) | `Capacitor_SMD:C_0805_2012Metric` |
| L: D18 | 1 | KT-0603R | Hubei KENTO Elec | [C2286](https://jlcpcb.com/partdetail/C2286) | `LED_SMD:LED_0603_1608Metric` |
| L: R3 | 1 | 0402WGF2001TCE | UNI-ROYAL | [C4109](https://jlcpcb.com/partdetail/C4109) | `Resistor_SMD:R_0402_1005Metric` |
| B: U8 | 1 | SN74AHCT1G125DBVR | TI | [C7484](https://jlcpcb.com/partdetail/C7484) | `Package_TO_SOT_SMD:SOT-23-5` |
| L: U7, U10, U11, U12; B: U2 | 5 | USBLC6-2SC6 | ST | [C7519](https://jlcpcb.com/partdetail/C7519) | `Package_TO_SOT_SMD:SOT-23-6` |
| L: Q5, Q6 | 2 | 2N7002 | JSCJ | [C8545](https://jlcpcb.com/partdetail/C8545) | `Package_TO_SOT_SMD:SOT-23` |
| L: D19 | 1 | B5819W SL | JSCJ | [C8598](https://jlcpcb.com/partdetail/C8598) | `Diode_SMD:D_SOD-123` |
| L: R5… (15; exact list in CSV) | 15 | 0402WGF1001TCE | UNI-ROYAL | [C11702](https://jlcpcb.com/partdetail/C11702) | `Resistor_SMD:R_0402_1005Metric` |
| L: Q1 | 1 | AO3401A | AOS | [C15127](https://jlcpcb.com/partdetail/C15127) | `Package_TO_SOT_SMD:SOT-23` |
| L: C5, C9 | 2 | CL21A106KAYNNNE | Samsung Electro-Mechanics | [C15850](https://jlcpcb.com/partdetail/C15850) | `Capacitor_SMD:C_0805_2012Metric` |
| L: R37, R38 | 2 | 0603WAF0000T5E | UNI-ROYAL | [C21189](https://jlcpcb.com/partdetail/C21189) | `Resistor_SMD:R_0603_1608Metric` |
| L: R60 | 1 | 0603WAF1000T5E | UNI-ROYAL | [C22775](https://jlcpcb.com/partdetail/C22775) | `Resistor_SMD:R_0603_1608Metric` |
| L: R43, R44, R45, R58, R56; B: R11 | 6 | 0402WGF3300TCE | UNI-ROYAL | [C25104](https://jlcpcb.com/partdetail/C25104) | `Resistor_SMD:R_0402_1005Metric` |
| L: R4… (12; exact list in CSV); B: R26, R6, R7 | 15 | 0402WGF1003TCE | UNI-ROYAL | [C25741](https://jlcpcb.com/partdetail/C25741) | `Resistor_SMD:R_0402_1005Metric` |
| L: R14… (12; exact list in CSV); B: R1, R2, R3, R4, R5 | 17 | 0402WGF1002TCE | UNI-ROYAL | [C25744](https://jlcpcb.com/partdetail/C25744) | `Resistor_SMD:R_0402_1005Metric` |
| L: R6, R7, R9, R10, R27, R28, R29, R30 | 8 | 0402WGF4701TCE | UNI-ROYAL | [C25900](https://jlcpcb.com/partdetail/C25900) | `Resistor_SMD:R_0402_1005Metric` |
| L: R1, R2 | 2 | 0402WGF5101TCE | UNI-ROYAL | [C25905](https://jlcpcb.com/partdetail/C25905) | `Resistor_SMD:R_0402_1005Metric` |
| B: C13 | 1 | CL21B105KBFNNNE | Samsung Electro-Mechanics | [C28323](https://jlcpcb.com/partdetail/C28323) | `Capacitor_SMD:C_0805_2012Metric` |
| L: U3 | 1 | MCP73832T-2ACI/OT | MICROCHIP | [C38066](https://jlcpcb.com/partdetail/C38066) | `Package_TO_SOT_SMD:SOT-23-5` |
| L: U2 | 1 | AP2112K-3.3TRG1 | DIODES | [C51118](https://jlcpcb.com/partdetail/C51118) | `Package_TO_SOT_SMD:SOT-23-5` |
| L: C3, C4, C7, C8, C12, C47 | 6 | CL05A105KA5NQNC | Samsung Electro-Mechanics | [C52923](https://jlcpcb.com/partdetail/C52923) | `Capacitor_SMD:C_0402_1005Metric` |
| B: D20… (16; exact list in CSV) | 16 | 1N4148W | ST(Semtech) | [C81598](https://jlcpcb.com/partdetail/C81598) | `Diode_SMD:D_SOD-123` |
| L: J1 | 1 | TYPE-C-31-M-12 | Korean Hroparts Elec | [C165948](https://jlcpcb.com/partdetail/C165948) | `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` |
| L: Q2, Q3, Q4 | 3 | ZXMS6005DGTA | DIODES | [C174045](https://jlcpcb.com/partdetail/C174045) | `Package_TO_SOT_SMD:SOT-223-3_TabPin2` |
| L: J15; B: J1 | 2 | AFA07-S06FCA-00 | JUSHUO | [C262712](https://jlcpcb.com/partdetail/C262712) | `Connector_FFC-FPC:JUSHUO_AFA07-S06FCA-00_1x6-1MP_P1.0mm_Horizontal` |
| L: J9 | 1 | S3B-PH-SM4-TB(LF)(SN) | JST | [C265101](https://jlcpcb.com/partdetail/C265101) | `Connector_JST:JST_PH_S3B-PH-SM4-TB_1x03-1MP_P2.00mm_Horizontal` |
| L: J10, J11, J19 | 3 | S4B-PH-SM4-TB(LF)(SN) | JST | [C265102](https://jlcpcb.com/partdetail/C265102) | `Connector_JST:JST_PH_S4B-PH-SM4-TB_1x04-1MP_P2.00mm_Horizontal` |
| L: J12 | 1 | S5B-PH-SM4-TB(LF)(SN) | JST | [C265104](https://jlcpcb.com/partdetail/C265104) | `Connector_JST:JST_PH_S5B-PH-SM4-TB_1x05-1MP_P2.00mm_Horizontal` |
| L: J5 | 1 | S6B-PH-SM4-TB(LF)(SN) | JST | [C265405](https://jlcpcb.com/partdetail/C265405) | `Connector_JST:JST_PH_S6B-PH-SM4-TB_1x06-1MP_P2.00mm_Horizontal` |
| L: J16, J17, J18 | 3 | S2B-PH-SM4-TB(LF)(SN) | JST | [C295747](https://jlcpcb.com/partdetail/C295747) | `Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal` |
| L: C45, C46 | 2 | CL32B226KAJNNNE | Samsung Electro-Mechanics | [C309062](https://jlcpcb.com/partdetail/C309062) | `Capacitor_SMD:C_1210_3225Metric` |
| L: SW17, SW18, SW19; B: SW1… (16; exact list in CSV) | 19 | TS-1187A-B-A-B | XKB Connection | [C318884](https://jlcpcb.com/partdetail/C318884) | `Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A` |
| L: U1 | 1 | E73-2G4M08S1C | Ebyte | [C356849](https://jlcpcb.com/partdetail/C356849) | `notchdeck:EBYTE_E73-2G4M08S1C` |
| L: J3 | 1 | FTSH-105-01-L-DV-K-TR | Samtec | [C448647](https://jlcpcb.com/partdetail/C448647) | `notchdeck:Samtec_FTSH-105-01-L-DV-K` |
| L: U5 | 1 | AS5600-ASOT | ams | [C499458](https://jlcpcb.com/partdetail/C499458) | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` |
| B: U1 | 1 | STM32G030F6P6TR | ST | [C529330](https://jlcpcb.com/partdetail/C529330) | `Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm` |
| L: J2 | 1 | 430450401 | Molex | [C585880](https://jlcpcb.com/partdetail/C585880) | `Connector_Molex:Molex_Micro-Fit_3.0_43045-0400_2x02_P3.00mm_Horizontal` |
| L: D17 | 1 | XL-1608SYGC-06 | XINGLIGHT | [C965805](https://jlcpcb.com/partdetail/C965805) | `LED_SMD:LED_0603_1608Metric` |
| L: U9 | 1 | TCA9543APWR | TI | [C2653307](https://jlcpcb.com/partdetail/C2653307) | `Package_SO:TSSOP-14_4.4x5mm_P0.65mm` |
| L: U4 | 1 | MAX17048G+T10 | MAXIM | [C2682616](https://jlcpcb.com/partdetail/C2682616) | `Package_DFN_QFN:TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm` |
| B: D1… (16; exact list in CSV) | 16 | XL-5050RGBC-2812B | XINGLIGHT | [C2843785](https://jlcpcb.com/partdetail/C2843785) | `notchdeck:LED_XINGLIGHT_XL-5050RGBC-2812B` |
| L: U13 | 1 | TPS259461LRPWR | Texas Instruments | [C3662776](https://jlcpcb.com/partdetail/C3662776) | `notchdeck:TI_RPW0010A` |
| L: D20, D21, D22, D23, D24 | 5 | B360A | FUXINSEMI | [C6807778](https://jlcpcb.com/partdetail/C6807778) | `Diode_SMD:D_SMA` |

## Selection constraints

Actuator Q2–4 use owned ZXMS6005DGTA; U13 is TPS259461LRPWR (full battery-input electronic limiter, latched thermal shutdown). No disposable fuse is selected. Five B360A diodes and two 22µF/25V capacitors also use owned stock. See [actuator protection and limits](notchdeck-one/ACTUATORS.md).

Use MCP73832 open-drain STAT, not MCP73831. Retain TI AHCT for the 3V3-to-USB5V RGB buffer; AHC/HC is not equivalent. RGB C2843785 and the keyed Samtec SWD header use project-local footprints transcribed from manufacturer drawings; see [attributions](lib/ATTRIBUTIONS.md). The E73 footprint/antenna clearance and MAX17048 exposed pad still need final package review.

Button U1 uses internally bonded pins in TSSOP-20; configure only the chosen alias and leave other aliases high impedance. See [button-board interface](notchdeck-buttons/README.md). FFC J15/J1 use identical bottom-contact connectors with reversed pin assignment for the specified Type A cable.

Logic J4 and button J2 are bare Tag-Connect contacts, excluded from BOM and CPL. Both boards have four PCB-only holes. External handle mechanisms, magnetic sensor carriers, harnesses, protected battery, keycaps and enclosure remain separate unsourced items.

Run `make -C hardware verify` after changing selections. Both PCBs are unrouted; available parts and clean ERC do not establish fabrication readiness.
