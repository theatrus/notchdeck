#!/usr/bin/env python3
"""Regenerate the NotchDeck One hierarchical schematic from this manifest.

    python3 scripts/notchdeck-one.schgen.py

Places every part from hardware/PARTS.md / NETPLAN.md onto a relevant child
sheet (MCU / Power / Lever / Controls), each resolving to a real KiCad symbol +
footprint, with a per-sheet wiring / pin-assignment note. Components are placed,
not wired — wire them afterwards in eeschema (the notes are the spec).

This is DATA. The generation engine lives in scripts/kschgen.py. To tweak the
board, edit the component lists / notes below and re-run. To start a new board,
copy this file and change the manifest.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kschgen as K

HW = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # hardware/
PROJ_DIR = os.path.join(HW, "notchdeck-one")
NOTCH_SYM = os.path.join(HW, "lib", "symbols", "notchdeck.kicad_sym")
ROOT_UUID = "9b1c0f7a-1d2e-4a3b-8c5d-0e6f7a8b9c01"   # keep stable across regens

# ---- register every symbol library this board draws from --------------------
K.register_stdlib("Device", "R", "C", "LED", "D_Schottky")
K.register_stdlib("Connector", "USB_C_Receptacle_USB2.0_16P",
                  "Conn_ARM_JTAG_SWD_10", "Conn_ARM_SWD_TagConnect_TC2030-NL")
K.register_stdlib("Connector_Generic", "Conn_01x02")
K.register_stdlib("Regulator_Linear", "AP2112K-3.3")
K.register_stdlib("Battery_Management", "MCP73831-2-OT")
K.register_stdlib("Power_Protection", "USBLC6-2SC6")
K.register_stdlib("Transistor_FET", "Q_PMOS_GSD")
K.register_stdlib("Switch", "SW_Push")
K.register_stdlib("LED", "WS2812B")
K.register_stdlib("74xGxx", "74LVC1G125")
K.register_lib("notchdeck", NOTCH_SYM, "E73-2G4M08S1C", "AS5600", "MAX17048")

# ---- footprint shorthands ---------------------------------------------------
R0402 = "Resistor_SMD:R_0402_1005Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
LED0603 = "LED_SMD:LED_0603_1608Metric"
SOT235 = "Package_TO_SOT_SMD:SOT-23-5"
SOT23 = "Package_TO_SOT_SMD:SOT-23"
BTN = "Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A"
WS2812FP = "LED_SMD:LED_OPSCO_SK6812_PLCC4_5.0x5.0mm_P3.1mm"


def R(ref, val):
    return dict(ref=ref, lib_id="Device:R", value=val, fp=R0402)


def C(ref, val, fp=C0402):
    return dict(ref=ref, lib_id="Device:C", value=val, fp=fp)


# ============================ component manifest =============================
MCU = dict(name="MCU", file="mcu.kicad_sch", title="MCU & Programming", page="2",
    big=[
        dict(ref="U1", lib_id="notchdeck:E73-2G4M08S1C", value="E73-2G4M08S1C",
             fp="notchdeck:EBYTE_E73-2G4M08S1C", lcsc="C356849",
             mpn="E73-2G4M08S1C", mfr="Ebyte"),
        dict(ref="J3", lib_id="Connector:Conn_ARM_JTAG_SWD_10", value="SWD",
             fp="Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical_SMD"),
        dict(ref="J4", lib_id="Connector:Conn_ARM_SWD_TagConnect_TC2030-NL",
             value="TC2030_NL",
             fp="Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical"),
    ],
    small=[
        C("C1", "100nF"), C("C2", "100nF"), C("C3", "1uF"), C("C4", "1uF"),
        C("C5", "10uF", C0805), C("C6", "100nF"),
        dict(ref="SW_RST", lib_id="Switch:SW_Push", value="RESET", fp=BTN),
    ])

POWER = dict(name="Power", file="power.kicad_sch",
    title="Power (USB-C / Charge / LDO / Fuel-gauge)", page="3",
    big=[
        dict(ref="J1", lib_id="Connector:USB_C_Receptacle_USB2.0_16P", value="USB-C",
             fp="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
             lcsc="C165948", mpn="TYPE-C-31-M-12"),
    ],
    small=[
        dict(ref="U7", lib_id="Power_Protection:USBLC6-2SC6", value="USBLC6-2SC6",
             fp="Package_TO_SOT_SMD:SOT-23-6", lcsc="C2687116", mpn="USBLC6-2SC6", mfr="ST"),
        R("R1", "5.1k"), R("R2", "5.1k"),
        dict(ref="U3", lib_id="Battery_Management:MCP73831-2-OT", value="MCP73831-2-OT",
             fp=SOT235, lcsc="C424093", mpn="MCP73831T-2ACI/OT", mfr="Microchip"),
        R("R3", "2k"),
        dict(ref="U2", lib_id="Regulator_Linear:AP2112K-3.3", value="AP2112K-3.3",
             fp=SOT235, lcsc="C23380830", mpn="AP2112K-3.3TRG1", mfr="Diodes"),
        C("C7", "1uF"), C("C8", "1uF"), C("C9", "10uF", C0805),
        dict(ref="Q1", lib_id="Transistor_FET:Q_PMOS_GSD", value="AO3401A",
             fp=SOT23, lcsc="C15127", mpn="AO3401A", mfr="AOS"),
        dict(ref="D_PP", lib_id="Device:D_Schottky", value="B5819W",
             fp="Diode_SMD:D_SOD-123", lcsc="C8598", mpn="B5819W", mfr="Slkor"),
        R("R4", "100k"), R("R5", "100k"),
        dict(ref="U4", lib_id="notchdeck:MAX17048", value="MAX17048",
             fp="Package_DFN_QFN:TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm",
             lcsc="C2682616", mpn="MAX17048G+T10", mfr="Analog Devices"),
        C("C10", "100nF"), R("R6", "4.7k"), R("R7", "4.7k"), R("R8", "100k"),
        dict(ref="J2", lib_id="Connector_Generic:Conn_01x02", value="BAT 1S",
             fp="Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
             mpn="S2B-PH-SM4-TB", mfr="JST"),
        dict(ref="U8", lib_id="74xGxx:74LVC1G125", value="74LVC1G125", fp=SOT235,
             dnp=True, lcsc="C52098142", mpn="74LVC1G125W5", mfr="Diodes"),
    ])

LEVER = dict(name="Lever", file="lever.kicad_sch",
    title="Lever sensing (AS5600 magnetic + 4-bit coded-switch)", page="4",
    big=[
        # One 2-pin JST-PH per coded-switch bit (signal + GND), 4 switches from the mascon.
        dict(ref="J5", lib_id="Connector_Generic:Conn_01x02", value="CODE S0",
             fp="Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
             mpn="S2B-PH-SM4-TB", mfr="JST"),
        dict(ref="J6", lib_id="Connector_Generic:Conn_01x02", value="CODE S1",
             fp="Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
             mpn="S2B-PH-SM4-TB", mfr="JST"),
        dict(ref="J7", lib_id="Connector_Generic:Conn_01x02", value="CODE S2",
             fp="Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
             mpn="S2B-PH-SM4-TB", mfr="JST"),
        dict(ref="J8", lib_id="Connector_Generic:Conn_01x02", value="CODE S3",
             fp="Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
             mpn="S2B-PH-SM4-TB", mfr="JST"),
    ],
    small=[
        dict(ref="U5", lib_id="notchdeck:AS5600", value="AS5600",
             fp="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
             lcsc="C499458", mpn="AS5600-ASOM", mfr="AMS"),
        C("C11", "100nF"), C("C12", "1uF"), R("R9", "4.7k"), R("R10", "4.7k"),
        # 4-bit coded-switch input: active-low, per-bit RC debounce
        # (Rpu 10k to +3V3 / Rs 1k series / C 100nF to GND).
        R("R14", "10k"), R("R15", "10k"), R("R16", "10k"), R("R17", "10k"),
        R("R18", "1k"), R("R19", "1k"), R("R20", "1k"), R("R21", "1k"),
        C("C14", "100nF"), C("C15", "100nF"), C("C16", "100nF"), C("C17", "100nF"),
    ])

ctrl = []
for i in range(1, 17):
    ctrl.append(dict(ref=f"SW{i}", lib_id="Switch:SW_Push", value="SW_Push", fp=BTN))
for i in range(1, 17):
    ctrl.append(dict(ref=f"D{i}", lib_id="LED:WS2812B", value="WS2812B", fp=WS2812FP,
                     lcsc="C2843785", mpn="XL-5050RGBC-2812B"))
ctrl += [
    C("C13", "100uF", "Capacitor_SMD:C_1210_3225Metric"),
    R("R11", "330"),
    dict(ref="D17", lib_id="Device:LED", value="LED", fp=LED0603),
    R("R12", "1k"),
    dict(ref="D18", lib_id="Device:LED", value="LED", fp=LED0603),
    R("R13", "1k"),
]
CONTROLS = dict(name="Controls", file="controls.kicad_sch",
    title="Controls (buttons / hat / WS2812 LEDs / status)", page="5",
    big=[], small=ctrl)

# ============================ per-sheet wiring notes ==========================
MCU["note"] = (15, 165, """NotchDeck One — MCU & Programming (U1 Ebyte E73-2G4M08S1C, nRF52840)
Components placed, NOT yet wired. Pad numbers = E73 module pads (per notchdeck:E73 symbol / NETPLAN.md).

POWER:  VDD(19) + VDDH(23) -> +3V3 (tie together = normal-voltage mode; module DC/DC handles REG1).
        DCCH(25) = NC (leave open). Decouple each VDD/VDDH with 100nF (C1,C2) + 1uF (C3,C4); 10uF bulk (C5) on +3V3.
USB:    VBUS(27) -> USB_VBUS(5V)  |  D-(29) -> USB_DM  |  D+(31) -> USB_DP   [from Power sheet, through U7 ESD].
        nRF on-chip USB regulator + vbus_present() read VBUS directly (no GPIO).
SWD:    SWDIO(37), SWDCLK(39), nRESET(26/P0.18), +3V3, GND -> wire to BOTH J3 (2x05) and J4 (TC2030-NL) in parallel.
RESET:  SW_RST: nRESET -> GND (momentary). 100nF (C6) on nRESET. Bootloader double-tap-to-DFU (no BOOT pin).
FW:     NFC pins P0.09/P0.10 used as GPIO -> set CONFIG_NFCT_PINS_AS_GPIO. nRESET enabled in UICR.
        P0.00/P0.01 used as GPIO -> LFCLK = internal RC (no 32.768kHz xtal).

E73 full pad map (signal -> net/function):
 1  P1.11        BTN1 horn-hi (A)        23 VDDH         +3V3 (tie to VDD)
 2  P1.10        BTN2 horn-lo/bell (B)   24 GND          GND
 3  P0.03/AIN1   LEVER_S0 (coded-sw)     25 DCCH         NC (open)
 4  P0.28/AIN4   LEVER_S1 (coded-sw)     26 P0.18/RESET  nRESET (SW_RST + SWD)
 5  GND          GND                     27 VBUS         USB_VBUS (5V)
 6  P1.13        BTN3 door-close (X)     28 P0.15        FG_ALRT  (MAX17048 ALRT)
 7  P0.02/AIN0   REVERSER_AIN (ADC)      29 USB_D-       USB_DM
 8  P0.29/AIN5   spare                   30 P0.17        CHG_STAT (MCP73831 STAT)
 9  P0.31/AIN7   spare                   31 USB_D+       USB_DP
10  P0.30/AIN6   spare                   32 P0.20        BTN5 ATS-reset (L)
11  P0.00/XL1    BTN11 (GPIO, no LFXO)   33 P0.13        BTN6 cab/view (R)
12  P0.26        I2C0_SDA -> AS5600      34 P0.22        HAT_UP
13  P0.01/XL2    BTN12 (GPIO, no LFXO)   35 P0.24        HAT_DOWN
14  P0.06        I2C0_SCL -> AS5600      36 P1.00        HAT_LEFT
15  P0.05/AIN3   LEVER_S3 (coded-sw)     37 SWDIO        SWDIO (J3/J4)
16  P0.08        WS2812_DIN              38 P1.02        HAT_RIGHT
17  P1.09        BTN4 door-open (Y)      39 SWDCLK       SWDCLK (J3/J4)
18  P0.04/AIN2   LEVER_S2 (coded-sw)     40 P1.04        BTN7 select
19  VDD          +3V3                    41 P0.09/NFC1   BTN9 pantograph
20  P0.12        I2C1_SDA -> MAX17048    42 P1.06        BTN8 start
21  GND          GND                     43 P0.10/NFC2   BTN10 headlight
22  P0.07        I2C1_SCL -> MAX17048""")

POWER["note"] = (15, 175, """NotchDeck One — Power path (USB -> Charge -> Load-share -> 3V3) + Fuel-gauge.  Placed, not wired. See NETPLAN.md "Power architecture".

FLOW:  USB-C VBUS(5V) --[U7 ESD]--+--> E73 VBUS(27)
                                  +--> U3 MCP73831 VIN (charge in)
                                  +--> D_PP Schottky --> VSYS
       BAT+ --> Q1 PMOS (load-share) --> VSYS --> U2 AP2112K-3.3 --> +3V3
USB-C (J1): VBUS(A4/A9/B4/B9)->USB_VBUS;  CC1->R1, CC2->R2, 5.1k each to GND (UFP/sink);
            D+(A6/B6) -> USB_DP, D-(A7/B7) -> USB_DM (to E73 via U7);  SBU1/2 = NC;  Shield -> GND.
U7 USBLC6-2SC6: place at connector, protects D+/D-/VBUS.
CHARGER U3 (MCP73831-2-OT): VDD<-USB_VBUS;  VBAT->BAT+;  PROG via R3 sets Ichg (2k~=500mA, 10k~=100mA: match cell);
            STAT -> CHG_STAT (P0.17) + charge LED (on Controls sheet).
LOAD-SHARE: Q1 (AO3401A) P-FET source=BAT+, drain=VSYS, gate pulled to USB_VBUS via R4 (100k); R5 (100k) gate series.
            D_PP (B5819W) USB_VBUS -> VSYS. Battery feeds load only when USB absent.
LDO U2 (AP2112K-3.3): VIN<-VSYS, EN->VIN (always-on), C7 1uF in / C8 1uF out, VOUT-> +3V3.  C9 10uF bulk on +3V3.
FUEL GAUGE U4 (MAX17048): VDD->BAT+;  CELL(2)=NC (1-cell);  CTG/GND/EP/QSTRT -> GND;  ALRT-> FG_ALRT(P0.15) via R8 pull-up.
            C10 100nF decouple.  I2C1 (TWIM1): SDA=P0.12(20), SCL=P0.07(22); R6/R7 4.7k pull-ups to +3V3.
BATTERY J2 (JST-PH): pin1 BAT+, pin2 GND (1S Li-ion).
U8 (74LVC1G125) = DNP: only populate if WS2812 strip runs at 5V (level-shift WS2812_DIN).  Default DNP (3V3 strip).""")

LEVER["note"] = (15, 165, """NotchDeck One — Lever sensing: AS5600 magnetic angle (I2C0) + 4-bit coded-switch input (J5).  Placed, not wired. See NETPLAN.md "Lever sensing".

AS5600 U5:  VDD5V(1) + VDD3V3(2) -> +3V3 (3.3V mode: tie both).   GND(4) -> GND.   DIR(8) -> GND (CW = increasing).
            SDA(6) / SCL(7) -> I2C0 bus.   OUT(3) = NC,  PGO(5) = NC.   C11 100nF + C12 1uF decouple.
I2C0 (TWIM0): SDA = P0.26 (pad 12),  SCL = P0.06 (pad 14).   R9 / R10 = 4.7k pull-ups to +3V3.
!! AS5600 and MAX17048 SHARE I2C addr 0x36 -> they MUST be on separate buses. AS5600 = TWIM0, MAX17048 = TWIM1.
MECH: diametric magnet centered over the package on the lever shaft, 0.5-3mm air-gap.

CODED-SWITCH INPUT (J5-J8) — coexists with AS5600; populate either front-end, or both. Switches live in the mascon, wired in on the harness.
  ONE 2-pin JST-PH per bit:  J5=LEVER_S0  J6=LEVER_S1  J7=LEVER_S2  J8=LEVER_S3.   Each: pin1 = bit line, pin2 = GND.
  4-bit binary/Gray code, ACTIVE-LOW: each switch bridges its connector (bit line -> GND); open = high (held by pull-up).
  Per-bit input circuit (small RC debounce), one of 4:
        +3V3 --[Rpu 10k]--+-- Jn.1 (bit line, switch to GND)
                          +--[Rs 1k]--+-- E73 GPIO      tau_release ~1.1ms ((Rpu+Rs)*C), tau_press ~0.1ms (Rs*C)
                                      +--[C 100nF]-- GND   Rs also limits cap-discharge / adds cable ESD margin.
     bit0(J5): Rpu R14 / Rs R18 / C C14    bit1(J6): R15 / R19 / C15    bit2(J7): R16 / R20 / C16    bit3(J8): R17 / R21 / C17
  GPIO (4 dedicated spares, so it does NOT collide with AS5600 on I2C0):
     LEVER_S0 = P0.03/AIN1 (pad 3)   LEVER_S1 = P0.28/AIN4 (pad 4)   LEVER_S2 = P0.04/AIN2 (pad 18)   LEVER_S3 = P0.05/AIN3 (pad 15)
  FW: read the 4 GPIO, de-Gray/decode to a notch index in lever.c; notch->HID table stays sensor-agnostic. Ext 10k already sets the level (internal pull-ups optional).""")

CONTROLS["note"] = (15, 168, """NotchDeck One — Controls: buttons, hat, WS2812 LEDs, status.  Placed, not wired. See NETPLAN.md.

BUTTONS (active-low to GND, internal pull-ups, debounce in FW):
  SW1 BTN1 horn-hi  P1.11(1)    SW5 BTN5 L/ATS    P0.20(32)   SW9  BTN9 panto   P0.09(41)   SW13 HAT_UP    P0.22(34)
  SW2 BTN2 horn-lo  P1.10(2)    SW6 BTN6 R/cab    P0.13(33)   SW10 BTN10 head   P0.10(43)   SW14 HAT_DOWN  P0.24(35)
  SW3 BTN3 door-cl  P1.13(6)    SW7 BTN7 select   P1.04(40)   SW11 BTN11        P0.00(11)   SW15 HAT_LEFT  P1.00(36)
  SW4 BTN4 door-op  P1.09(17)   SW8 BTN8 start    P1.06(42)   SW12 BTN12        P0.01(13)   SW16 HAT_RIGHT P1.02(38)
WS2812 (D1..D16, addressable RGB): VDD -> +3V3 (or VBUS+U8 level-shift). Chain DOUT(n) -> DIN(n+1).
  R11 330ohm series on WS2812_DIN from E73 P0.08(16) into D1.  C13 100uF bulk across strip V+/GND (add 100nF/LED ideally).
STATUS LEDs: D17 (status) + R12 1k ;  D18 (charge) + R13 1k <- CHG_STAT(P0.17).  Anodes -> +3V3 or GPIO per use.""")

# ============================ generate =======================================
K.build(
    project="notchdeck-one",
    proj_dir=PROJ_DIR,
    root_uuid=ROOT_UUID,
    title=dict(title="NotchDeck One", date="2026-05-29", rev="A", company="BenchBits",
               comments=["Dual-mode (USB + BLE) one-handle train master controller",
                         "Top-level — hierarchical sheets per functional block"]),
    sheets=[MCU, POWER, LEVER, CONTROLS],
)
