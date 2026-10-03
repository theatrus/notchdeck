#!/usr/bin/env python3
"""Regenerate the NotchDeck One hierarchical schematic from this manifest.

    python3 scripts/notchdeck-one.schgen.py

Places every part from hardware/PARTS.md / NETPLAN.md onto a relevant child
sheet (MCU / Power / Lever / Controls), each resolving to a real KiCad symbol +
footprint. Connectivity and deliberate block layouts are captured here with
visible wires and hierarchical sheet ports. KiCad ERC and an independent netlist
audit validate the result.

The component manifest and Capture layout below are the source of truth.
The reusable KiCad emitters live in scripts/kschgen.py.
"""

import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kschgen as K

HW = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # hardware/
PROJ_DIR = os.path.join(HW, "notchdeck-one")
NOTCH_SYM = os.path.join(HW, "lib", "symbols", "notchdeck.kicad_sym")
ROOT_UUID = "9b1c0f7a-1d2e-4a3b-8c5d-0e6f7a8b9c01"  # keep stable across regens

# ---- register every symbol library this board draws from --------------------
K.register_stdlib("Device", "R", "C", "LED", "D_Schottky")
K.register_stdlib(
    "Connector",
    "USB_C_Receptacle_USB2.0_16P",
    "Conn_ARM_JTAG_SWD_10",
    "Conn_ARM_SWD_TagConnect_TC2030-NL",
)
K.register_stdlib("Connector_Generic", "Conn_01x02", "Conn_01x03", "Conn_01x04", "Conn_01x05", "Conn_01x06")
K.register_stdlib("Regulator_Linear", "AP2112K-3.3")
K.register_stdlib("Battery_Management", "MCP73832-2-OT")
K.register_stdlib("Power_Protection", "USBLC6-2SC6")
K.register_stdlib("Transistor_FET", "Q_PMOS_GSD")
K.register_stdlib("Switch", "SW_Push")
K.register_lib(
    "notchdeck", NOTCH_SYM, "E73-2G4M08S1C", "AS5600", "MAX17048", "SWD_2x05", "SWD_TC2030", "TCA9543APWR"
)

# ---- footprint shorthands ---------------------------------------------------
R0402 = "Resistor_SMD:R_0402_1005Metric"
C0402 = "Capacitor_SMD:C_0402_1005Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
LED0603 = "LED_SMD:LED_0603_1608Metric"
SOT235 = "Package_TO_SOT_SMD:SOT-23-5"
SOT23 = "Package_TO_SOT_SMD:SOT-23"
BTN = "Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A"


def R(ref, val):
    return dict(ref=ref, lib_id="Device:R", value=val, fp=R0402)


def C(ref, val, fp=C0402):
    return dict(ref=ref, lib_id="Device:C", value=val, fp=fp)


# ============================ component manifest =============================
MCU = dict(
    name="MCU",
    file="mcu.kicad_sch",
    title="MCU & Programming",
    page="2",
    big=[
        dict(
            ref="U1",
            lib_id="notchdeck:E73-2G4M08S1C",
            value="E73-2G4M08S1C",
            fp="notchdeck:EBYTE_E73-2G4M08S1C",
        ),
        dict(
            ref="J3",
            lib_id="notchdeck:SWD_2x05",
            value="SWD",
            fp="notchdeck:Samtec_FTSH-105-01-L-DV-K",
        ),
        dict(
            ref="J4",
            lib_id="notchdeck:SWD_TC2030",
            value="TC2030_NL",
            fp="Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical",
            in_bom=False,
        ),
    ],
    small=[
        C("C1", "100nF"),
        C("C2", "100nF"),
        C("C3", "1uF"),
        C("C4", "1uF"),
        C("C5", "10uF", C0805),
        C("C6", "100nF"),
        dict(ref="SW17", lib_id="Switch:SW_Push", value="RESET", fp=BTN),
    ],
)

POWER = dict(
    name="Power",
    file="power.kicad_sch",
    title="Power and battery",
    page="3",
    big=[
        dict(
            ref="J1",
            lib_id="Connector:USB_C_Receptacle_USB2.0_16P",
            value="USB-C",
            fp="Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12",
        ),
    ],
    small=[
        dict(
            ref="U7",
            lib_id="Power_Protection:USBLC6-2SC6",
            value="USBLC6-2SC6",
            fp="Package_TO_SOT_SMD:SOT-23-6",
        ),
        R("R1", "5.1k"),
        R("R2", "5.1k"),
        dict(
            ref="U3",
            lib_id="Battery_Management:MCP73832-2-OT",
            value="MCP73832-2-OT",
            fp=SOT235,
        ),
        R("R3", "2k"),
        dict(
            ref="U2",
            lib_id="Regulator_Linear:AP2112K-3.3",
            value="AP2112K-3.3",
            fp=SOT235,
        ),
        C("C7", "1uF"),
        C("C8", "1uF"),
        C("C9", "10uF", C0805),
        dict(
            ref="Q1",
            lib_id="Transistor_FET:Q_PMOS_GSD",
            value="AO3401A",
            fp=SOT23,
        ),
        dict(
            ref="D19",
            lib_id="Device:D_Schottky",
            value="B5819W",
            fp="Diode_SMD:D_SOD-123",
        ),
        R("R4", "100k"),
        R("R5", "1k"),
        dict(
            ref="U4",
            lib_id="notchdeck:MAX17048",
            value="MAX17048",
            fp="Package_DFN_QFN:TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm",
        ),
        C("C10", "100nF"),
        R("R6", "4.7k"),
        R("R7", "4.7k"),
        R("R8", "100k"),
        dict(
            ref="J2",
            lib_id="Connector_Generic:Conn_01x02",
            value="BAT 1S",
            fp="Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
        ),
    ],
)

LEVER = dict(
    name="Lever",
    file="lever.kicad_sch",
    title="Lever sensing",
    page="4",
    big=[
        dict(
            ref="J5", lib_id="Connector_Generic:Conn_01x06", value="BRAKE / MASCON GRAY",
            fp="Connector_JST:JST_PH_S6B-PH-SM4-TB_1x06-1MP_P2.00mm_Horizontal",
        ),
    ],
    small=[
        dict(
            ref="U5",
            lib_id="notchdeck:AS5600",
            value="AS5600",
            fp="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
        ),
        C("C11", "100nF"),
        C("C12", "1uF"),
        R("R9", "4.7k"),
        R("R10", "4.7k"),
        # 4-bit coded-switch input: active-low, per-bit RC debounce
        # (Rpu 10k to +3V3 / Rs 1k series / C 100nF to GND).
        R("R14", "10k"),
        R("R15", "10k"),
        R("R16", "10k"),
        R("R17", "10k"),
        R("R18", "1k"),
        R("R19", "1k"),
        R("R20", "1k"),
        R("R21", "1k"),
        C("C14", "100nF"),
        C("C15", "100nF"),
        C("C16", "100nF"),
        C("C17", "100nF"),
    ],
)

ctrl = [
    dict(ref="D17", lib_id="Device:LED", value="LED", fp=LED0603),
    R("R12", "1k"),
    dict(ref="D18", lib_id="Device:LED", value="LED", fp=LED0603),
    R("R13", "1k"),
    dict(ref="J15", lib_id="Connector_Generic:Conn_01x06", value="BUTTON MCU FFC",
         fp="Connector_FFC-FPC:JUSHUO_AFA07-S06FCA-00_1x6-1MP_P1.0mm_Horizontal"),
    dict(ref="SW18", lib_id="Switch:SW_Push", value="SELECT", fp=BTN),
    dict(ref="SW19", lib_id="Switch:SW_Push", value="START", fp=BTN),
] + [R("R42", "10k"), C("C44", "100nF"),
     dict(ref="U12", lib_id="Power_Protection:USBLC6-2SC6", value="USBLC6-2SC6", fp="Package_TO_SOT_SMD:SOT-23-6")]
CONTROLS = dict(
    name="Controls",
    file="controls.kicad_sch",
    title="Controls and indicators",
    page="5",
    big=[],
    small=ctrl,
)

# ==================== wired capture and deliberate layout ====================
# Coordinates use 100 mil units; pins and wire corners remain on the 50 mil grid.
K.register_stdlib("power", "+3V3", "GND", "PWR_FLAG")
POWER["small"] += [C("C18", "4.7uF", C0805), C("C19", "4.7uF", C0805), R("R22", "100k")]
CONTROLS["small"] += [
    dict(
        ref="J9",
        lib_id="Connector_Generic:Conn_01x03",
        value="REV F-N-R",
        fp="Connector_JST:JST_PH_S3B-PH-SM4-TB_1x03-1MP_P2.00mm_Horizontal",
    ),
    R("R23", "100k"),
    R("R24", "100k"),
    R("R25", "1k"),
    C("C37", "100nF"),
]

# Rev C: independent magnetic and Gray-code interfaces for two handles.
# U5 is the optional onboard power/combined sensor; remove R37/R38 when J10
# carries an external AS5600. The two mux channels must never be enabled together.
LEVER["title"] = "Power and brake handle interfaces"
LEVER["small"] += [
    dict(ref="U9", lib_id="notchdeck:TCA9543APWR", value="TCA9543APWR",
         fp="Package_SO:TSSOP-14_4.4x5mm_P0.65mm"),
    *[dict(ref=f"U{i}", lib_id="Power_Protection:USBLC6-2SC6", value="USBLC6-2SC6",
           fp="Package_TO_SOT_SMD:SOT-23-6") for i in (10, 11)],
    *[dict(ref=f"J{i}", lib_id="Connector_Generic:Conn_01x04", value=value,
           fp="Connector_JST:JST_PH_S4B-PH-SM4-TB_1x04-1MP_P2.00mm_Horizontal")
      for i, value in [(10, "POWER MAG"), (11, "BRAKE MAG")]],
    dict(ref="J12", lib_id="Connector_Generic:Conn_01x05", value="POWER GRAY",
         fp="Connector_JST:JST_PH_S5B-PH-SM4-TB_1x05-1MP_P2.00mm_Horizontal"),
    *[R(f"R{i}", "4.7k") for i in range(27, 31)],
    *[R(f"R{i}", "10k") for i in range(31, 34)],
    *[R(f"R{i}", "1k") for i in range(34, 37)],
    *[dict(ref=f"R{i}", lib_id="Device:R", value="0",
           fp="Resistor_SMD:R_0603_1608Metric") for i in (37, 38)],
    *[R(f"R{i}", "10k") for i in range(39, 42)],
    *[C(f"C{i}", "100nF") for i in range(38, 44)],
]

# Reviewed JLCPCB selections are versioned separately from the wiring/layout.
# Emit them onto every symbol so KiCad remains the BOM export source of truth.
with open(os.path.join(PROJ_DIR, "bom", "jlcpcb-parts.json")) as source:
    sourcing = json.load(source)
parts_by_ref = {
    c["ref"]: c
    for sheet in (MCU, POWER, LEVER, CONTROLS)
    for c in sheet["big"] + sheet["small"]
}
assigned = set()
for code, part in sourcing["parts"].items():
    for ref in part["references"]:
        assert ref not in assigned, f"Duplicate sourcing assignment: {ref}"
        c = parts_by_ref[ref]
        assert c["fp"] == part["footprint"], f"Sourced footprint mismatch: {ref}"
        c.update(lcsc=code, mpn=part["mpn"], mfr=part["manufacturer"], datasheet=part["datasheet"])
        c["properties"] = {
            "JLCPCB Part Type": part["jlcpcb_category"],
            "BOM Checked": part.get("checked_at_utc", sourcing["checked_at_utc"])[:10],
            "BOM Comments": part["bom_comments"],
        }
        assigned.add(ref)
for ref, note in sourcing["non_assembly"].items():
    assert parts_by_ref[ref].get("in_bom") is False
    parts_by_ref[ref]["properties"] = {"BOM Comments": note}
assert assigned | set(sourcing["non_assembly"]) == set(parts_by_ref)
TITLE = dict(title="NotchDeck One", date="2026-10-03", rev="E", company="BenchBits")
G = 2.54


from notchdeck_capture import Capture as BoardCapture


def Capture(sh):
    return BoardCapture(sh, PROJ_DIR, ROOT_UUID, TITLE, "notchdeck-one")


PWR_PORTS = ["USB_VBUS", "USB_DM", "USB_DP", "I2C1_SCL", "I2C1_SDA", "FG_ALRT", "CHG_STAT"]
LEVER_PORTS = ["I2C0_SCL", "I2C0_SDA", "LEVER_S0", "LEVER_S1", "LEVER_S2", "LEVER_S3",
               "POWER_S0", "POWER_S1", "POWER_S2", "nRESET"]
CTRL_PORTS = ["PANEL_INT", "REVERSER_AIN", "BTN7", "BTN8"]

s = Capture(MCU)
s.place("U1", 40, 30, ref_offset=(-10.16, -35.56), value_offset=(-10.16, -33.02))
pinmap = {
    1: "PANEL_INT",
    3: "LEVER_S0",
    4: "LEVER_S1",
    5: "GND",
    7: "REVERSER_AIN",
    8: "POWER_S0",
    9: "POWER_S1",
    10: "POWER_S2",
    12: "I2C0_SDA",
    14: "I2C0_SCL",
    15: "LEVER_S3",
    18: "LEVER_S2",
    19: "+3V3",
    20: "I2C1_SDA",
    21: "GND",
    22: "I2C1_SCL",
    23: "+3V3",
    24: "GND",
    26: "nRESET",
    27: "USB_VBUS",
    28: "FG_ALRT",
    29: "USB_DM",
    30: "CHG_STAT",
    31: "USB_DP",
    37: "SWDIO",
    39: "SWDCLK",
    40: "BTN7",
    42: "BTN8",
}
for pin, net in pinmap.items():
    s.stub("U1", pin, net)  # same-name local rails join the decoupling power symbols
s.nc("U1", 25, 2, 6, 11, 13, 16, 17, 32, 33, 34, 35, 36, 38, 41, 43)
for i in range(1, 6):
    s.place(f"C{i}", 65 + (i - 1) * 8, 28)
s.rail("+3V3", [(f"C{i}", 1) for i in range(1, 6)], 22)
s.rail("GND", [(f"C{i}", 2) for i in range(1, 6)], 33)
s.note(
    63,
    16,
    "3V3 decoupling: C1/C3 at VDD; C2/C4 at VDDH.\nC5 bulk. VDD = VDDH; DCCH intentionally open.",
)
s.place("J3", 28, 66, ref_offset=(-7.62, -20.32), value_offset=(-7.62, -17.78))
s.place("J4", 65, 66, ref_offset=(-7.62, -15.24), value_offset=(-7.62, -12.7))
for r, pmap in [
    ("J3", {1: "+3V3", 2: "SWDIO", 3: "GND", 4: "SWDCLK", 5: "GND", 9: "GND", 10: "nRESET"}),
    ("J4", {1: "+3V3", 2: "SWDIO", 3: "nRESET", 4: "SWDCLK", 5: "GND"}),
]:
    for pin, net in pmap.items():
        s.stub(r, pin, net, kind="power" if net in ("+3V3", "GND") else "label")
s.nc("J3", 6, 7, 8)
s.nc("J4", 6)
s.place("SW17", 93, 62)
s.place("C6", 87, 70)
p = s.pin("SW17", 1)
q = s.pin("C6", 1)
s.wire(p, (q[0], p[1]), q)
s.label("nRESET", (q[0], p[1]))
s.stub("SW17", 2, "GND", kind="power")
s.stub("C6", 2, "GND", kind="power")
for i, n in enumerate(PWR_PORTS + LEVER_PORTS + CTRL_PORTS):
    s.port(n, 132, 10 + 2.5 * i)
s.note(
    10,
    88,
    "SWD headers are parallel; VTref is 3V3. SWO is unused.\nReset: P0.18 / UICR reset enabled; also resets handle mux.\nRev E leaves NFC pins unconnected; no NFC pin setup required.\nRev E frees 14 GPIOs; still use calibrated RC LFCLK, no LFXO.\nP0.29/P0.31/P0.30 = power Gray bits S0/S1/S2. P1.11 = panel IRQ.",
)
s.finish()

# Power: reversed PMOS load-share orientation is intentional: D=BAT+, S=VSYS.
s = Capture(POWER)
s.place("J1", 16, 24, ref_offset=(-10.16, -27.94), value_offset=(-10.16, -25.4))
s.place("U7", 53, 23, ref_offset=(-5.08, -12.7), value_offset=(-5.08, -10.16))
for pin in ["A4", "A9", "B4", "B9"]:
    s.stub("J1", pin, "USB_VBUS")
for pin in ["A1", "A12", "B1", "B12", "SH"]:
    s.stub("J1", pin, "GND", kind="power")
s.nc("J1", "A8", "B8")
for pins, ep, y, x in [(["A7", "B7"], 1, 23, 32), (["A6", "B6"], 3, 25, 36)]:
    joint = (x * G, y * G)
    for pin in pins:
        p = s.pin("J1", pin)
        s.wire(p, (joint[0], p[1]), joint)
    end = s.pin("U7", ep)
    s.wire(joint, (45 * G, joint[1]), (45 * G, end[1]), end)
for a, b, n in [(1, 6, "USB_DM"), (3, 4, "USB_DP")]:
    # The input already has a wire from J1; a reverse stub overlaps it.
    s.label(n, s.pin("U7", a), 180)
    s.stub("U7", b, n)
s.stub("U7", 5, "USB_VBUS")
s.stub("U7", 2, "GND", kind="power")
for ref, pin, x in [("R1", "A5", 32), ("R2", "B5", 41)]:
    s.place(ref, x, 13)
    a = s.pin("J1", pin)
    b = s.pin(ref, 2)
    s.wire(a, (b[0], a[1]), b)
    s.stub(ref, 1, "GND", kind="power")
s.place("D19", 84, 14, 180, ref_offset=(-2.54, -5.08), value_offset=(-5.08, -2.54))
s.place("Q1", 84, 27, 90, ref_offset=(-2.54, -8.89), value_offset=(-5.08, -6.35))
s.stub("D19", 2, "USB_VBUS")
s.stub("Q1", 3, "BAT+")
d = s.pin("D19", 1)
q = s.pin("Q1", 2)
s.wire(d, (96 * G, d[1]), (96 * G, q[1]), q)
s.label("VSYS", (96 * G, q[1]))
s.power("VSYS", (96 * G, q[1]), flag=True)
s.place("R5", 80, 38, 90, ref_offset=(-2.54, -5.08), value_offset=(-2.54, -2.54))
s.place("R4", 92, 44)
s.stub("R5", 1, "USB_VBUS")
a = s.pin("R5", 2)
b = s.pin("Q1", 1)
c = s.pin("R4", 1)
s.wire(a, (92 * G, a[1]), c)
s.wire(b, (92 * G, b[1]), (92 * G, a[1]))
s.stub("R4", 2, "GND", kind="power")
s.note(
    74,
    52,
    "Q1: D = BAT+, S = VSYS.\nR5 1k from VBUS; R4 100k to GND.\nBody diode blocks VSYS charging BAT+.",
)
s.place("U2", 128, 25, ref_offset=(-5.08, -10.16), value_offset=(-5.08, -7.62))
s.place("C7", 116, 28)
s.place("C8", 139, 28)
s.place("C9", 150, 28)
a = s.pin("U2", 1)
b = s.pin("U2", 3)
c = s.pin("C7", 1)
s.wire(a, (c[0], a[1]), c)
s.wire(b, (121 * G, b[1]), (121 * G, a[1]))
s.label("VSYS", (c[0], a[1]))
a = s.pin("U2", 5)
for r in ["C8", "C9"]:
    p = s.pin(r, 1)
    s.wire(a, (p[0], a[1]), p)
s.power("+3V3", (150 * G, a[1]))
s.nc("U2", 4)
s.rail("GND", [("U2", 2), ("C7", 2), ("C8", 2), ("C9", 2)], 36)
s.place("U3", 38, 67, ref_offset=(-5.08, -12.7), value_offset=(-5.08, -10.16))
s.place("R3", 25, 72)
a = s.pin("U3", 5)
b = s.pin("R3", 1)
s.wire(a, (b[0], a[1]), b)
s.stub("R3", 2, "GND", kind="power")
s.stub("U3", 2, "GND", kind="power")
s.place("C18", 20, 57)
s.place("C19", 58, 69)
s.place("J2", 72, 66)
s.rail("USB_VBUS", [("U3", 4), ("C18", 1)], 51, flag=True)
s.stub("C18", 2, "GND", kind="power")
a = s.pin("U3", 3)
b = s.pin("C19", 1)
c = s.pin("J2", 1)
s.wire(a, (b[0], a[1]), b)
s.wire((b[0], a[1]), (c[0], a[1]), c)
s.label("BAT+", a)
s.stub("J2", 2, "GND", kind="power")
s.stub("C19", 2, "GND", kind="power")
s.stub("U3", 1, "CHG_STAT")
s.place("R22", 53, 81)
s.stub("R22", 1, "+3V3", kind="power")
s.stub("R22", 2, "CHG_STAT")
s.note(
    10,
    89,
    "U3 is MCP73832 (open-drain STAT), not MCP73831.\nR3 = 2k: 500mA charge. Match cell and USB source budget.\nJ2: protected 1S Li-ion pack, pin 1 positive, pin 2 GND.",
)
s.place("U4", 115, 70, ref_offset=(-10.16, -12.7), value_offset=(-10.16, -10.16))
s.place("C10", 100, 65)
s.stub("U4", 3, "BAT+")
s.stub("U4", 2, "BAT+")
s.stub("C10", 1, "BAT+")
s.stub("C10", 2, "GND", kind="power")
for pin in [1, 4, 6, 9]:
    s.stub("U4", pin, "GND", kind="power")
for pin, net in [(5, "FG_ALRT"), (7, "I2C1_SCL"), (8, "I2C1_SDA")]:
    s.stub("U4", pin, net)
for r, net, x in [("R6", "I2C1_SDA", 134), ("R7", "I2C1_SCL", 143), ("R8", "FG_ALRT", 152)]:
    s.place(r, x, 63)
    s.stub(r, 2, net)
s.rail("+3V3", [("R6", 1), ("R7", 1), ("R8", 1)], 58)
s.note(
    100,
    83,
    "MAX17048: I2C1 / address 0x36.\nCELL + VDD -> BAT+; CTG/QSTRT/EP -> GND.\nAS5600 has its own bus to avoid address collision.",
)
for i, n in enumerate(PWR_PORTS):
    s.port(n, 12 + 21 * i, 94)
s.power("GND", (12 * G, 108 * G))
s.power("GND", (12 * G, 108 * G), flag=True)
s.finish()

s = Capture(LEVER)
s.place("U9", 28, 23, ref_offset=(7.62, -22.86), value_offset=(7.62, -20.32))
for pin, net in {13: "I2C0_SDA", 12: "I2C0_SCL", 3: "nRESET",
                 5: "POWER_MAG_SDA", 6: "POWER_MAG_SCL",
                 9: "BRAKE_MAG_SDA", 10: "BRAKE_MAG_SCL",
                 4: "MUX_INT0", 8: "MUX_INT1"}.items():
    end = s.stub("U9", pin, net)
    if net in ("I2C0_SDA", "I2C0_SCL", "nRESET"):
        s.extra.pop()
        s.extra.append(K.w_hlabel(net, *end, 180, "bidirectional"))
for pin in (1, 2, 7):
    s.stub("U9", pin, "GND", kind="power")
s.stub("U9", 14, "+3V3", kind="power")
s.nc("U9", 11)
s.place("C38", 9, 15)
s.stub("C38", 1, "+3V3", kind="power")
s.stub("C38", 2, "GND", kind="power")
for ref, net, x, y in [
    ("R9", "I2C0_SDA", 10, 35), ("R10", "I2C0_SCL", 19, 35),
    ("R39", "nRESET", 18, 10),
    ("R40", "MUX_INT0", 43, 35), ("R41", "MUX_INT1", 53, 35),
    ("R27", "POWER_MAG_SDA", 65, 13), ("R28", "POWER_MAG_SCL", 77, 13),
    ("R29", "BRAKE_MAG_SDA", 65, 26), ("R30", "BRAKE_MAG_SCL", 77, 26),
]:
    s.place(ref, x, y)
    s.stub(ref, 1, "+3V3", kind="power")
    a = s.pin(ref, 2)
    b = (a[0], a[1] + 2 * G)
    c = (b[0] + 2 * G, b[1])
    s.wire(a, b, c)
    s.label(net, c)
s.note(45, 6, "U9: 0x70 (A0=A1=0)\nCH0 power/combined; CH1 brake\nINT inputs held high; INT output unused")

s.place("U5", 105, 23, ref_offset=(-10.16, -12.7), value_offset=(-10.16, -10.16))
for ref, x in [("C11", 138), ("C12", 147)]:
    s.place(ref, x, 17)
    s.stub(ref, 1, "+3V3", kind="power")
    s.stub(ref, 2, "GND", kind="power")
for pin in (1, 2):
    s.stub("U5", pin, "+3V3", kind="power")
for pin in (4, 8):
    s.stub("U5", pin, "GND", kind="power")
s.nc("U5", 3, 5)
for pin, ref, net, y in [(6, "R37", "POWER_MAG_SDA", 23), (7, "R38", "POWER_MAG_SCL", 28)]:
    s.place(ref, 132, y, 90, ref_offset=(-2.54, -5.08), value_offset=(-2.54, -2.54))
    p, q = s.pin("U5", pin), s.pin(ref, 1)
    s.wire(p, (118 * G, p[1]), (118 * G, q[1]), q)
    s.label("U5_" + net, (120 * G, q[1]))
    s.stub(ref, 2, net)
s.note(91, 33, "Onboard U5: 3.3V mode, DIR=GND.\nREMOVE R37 AND R38 for external power sensor on J10.\nOnly one AS5600 may be connected on each channel.")

for j, esd, cap, prefix, x in [("J10", "U10", "C39", "POWER", 20), ("J11", "U11", "C40", "BRAKE", 87)]:
    s.place(j, x, 49, 180, ref_offset=(-2.54, -8.89), value_offset=(-2.54, -6.35))
    s.place(esd, x + 28, 48, ref_offset=(7.62, -12.7), value_offset=(7.62, -10.16))
    for pin, net in [(1, "+3V3"), (2, "GND"), (3, prefix + "_MAG_SDA"), (4, prefix + "_MAG_SCL")]:
        s.stub(j, pin, net)
    for pin, net in [(1, prefix + "_MAG_SDA"), (6, prefix + "_MAG_SDA"),
                     (3, prefix + "_MAG_SCL"), (4, prefix + "_MAG_SCL")]:
        s.stub(esd, pin, net)
    s.stub(esd, 5, "+3V3", kind="power")
    s.stub(esd, 2, "GND", kind="power")
    s.place(cap, x + 46, 48)
    s.stub(cap, 1, "+3V3", kind="power")
    s.stub(cap, 2, "GND", kind="power")
s.note(8, 55, "J10/J11: 1=3V3  2=GND  3=SDA  4=SCL. Internal harness <=20cm target, 100kHz; verify rise time.\n3.3V sensors only; no extra harness pull-ups. No hot-plug. External sensors require local decoupling.")

# Rev D: one polarized harness per cam. Distinct 5/6-pin housings distinguish
# these contact ports from the 4-pin magnetic ports. Existing GPIOs are unchanged.
for count, y, j, pus, rss, caps, prefix, raw_prefix in [
    (4, 72, "J5", 14, 18, 14, "LEVER", "BRAKE"),
    (3, 99, "J12", 31, 34, 41, "POWER", "POWER"),
]:
    s.place(j, 12, y, 180, ref_offset=(-2.54, -15.24), value_offset=(10.16, -12.7))
    s.stub(j, 1, "GND")
    s.stub(j, count + 2, "+3V3")
    for i in range(count):
        x = 45 + 31 * i if count == 4 else 43 + 29 * i
        pu, rs, cap = f"R{pus+i}", f"R{rss+i}", f"C{caps+i}"
        raw = f"{raw_prefix}_RAW_S{i}"
        s.stub(j, i + 2, raw)
        s.place(pu, x - 8, y - 7)
        s.place(rs, x, y, 90, ref_offset=(-2.54, -5.08), value_offset=(-2.54, -2.54))
        s.place(cap, x + 9, y + 5)
        p, q = s.pin(rs, 1), s.pin(pu, 2)
        end = ((x - 13) * G, p[1])
        s.wire(end, p)
        s.label(raw, end)
        s.wire(q, (q[0], p[1]))
        s.stub(pu, 1, "+3V3", kind="power")
        p, q = s.pin(rs, 2), s.pin(cap, 1)
        s.wire(p, (q[0], p[1]), q)
        s.label(f"{prefix}_S{i}", (q[0], p[1]))
        s.stub(cap, 2, "GND", kind="power")
s.note(8, 83, "REV D GRAY HARNESS: J5 brake/mascon: 1=GND, 2..5=S0..S3, 6=3V3. J12 power: 1=GND, 2..4=S0..S2, 5=3V3.\nDry contacts connect bits to GND; leave 3V3 unpopulated in passive harness. Open=1, closed=0; all-open is invalid.\n10k / 1k / 100nF + software debounce. Use microload contacts qualified for 3.3V / 0.33mA. Not compatible with Rev C cables.")
for i, n in enumerate([n for n in LEVER_PORTS if n not in ("I2C0_SDA", "I2C0_SCL", "nRESET")]):
    s.port(n, 132, 84 + i * 2)
s.finish()

s = Capture(CONTROLS)
# Rev E intelligent button board: 0x20 on I2C0 upstream of the handle mux.
s.place("J15",18,22,180,ref_offset=(-2.54,-12.7),value_offset=(-2.54,-10.16))
for pin,net in {1:"GND",2:"+3V3",3:"I2C0_SDA",4:"I2C0_SCL",5:"PANEL_INT",6:"USB_VBUS"}.items():
    s.stub("J15",pin,net)
s.place("U12",47,24,ref_offset=(7.62,-12.7),value_offset=(7.62,-10.16))
for pin,net in {1:"I2C0_SDA",6:"I2C0_SDA",3:"I2C0_SCL",4:"I2C0_SCL",5:"+3V3",2:"GND"}.items():
    s.stub("U12",pin,net,kind="power" if net in ("+3V3","GND") else "label")
s.place("R42",77,20);s.stub("R42",1,"+3V3",kind="power");s.stub("R42",2,"PANEL_INT")
s.place("C44",91,20);s.stub("C44",1,"+3V3",kind="power");s.stub("C44",2,"GND",kind="power")
for ref,n,x in [("SW18","BTN7",25),("SW19","BTN8",58)]:
    s.place(ref,x,50,ref_offset=(-2.54,-6.35),value_offset=(-2.54,-3.81))
    s.stub(ref,1,n);s.stub(ref,2,"GND",kind="power")
for i,n in enumerate(["PANEL_INT","BTN7","BTN8","I2C0_SDA","I2C0_SCL"]):s.port(n,20+26*i,70)
s.note(8,79,"J15 -> button J1: 6-way 1mm FFC, Molex 0151670213 Type A (same-side).\nBOTTOM contacts at both ends: main pin n -> button pin 7-n. Not a 1:1 harness.\nMain pinout: 1 GND / 2 3V3 / 3 SDA / 4 SCL / 5 IRQ_N / 6 USB 5V.\n3V3 keeps keys alive on battery; 5V RGB is USB only. Power off before insertion.\nSW18/SW19 remain direct Select/Start. I2C0=100kHz; panel address 0x20.\nExisting R9/R10 provide SDA/SCL pull-ups; no additional panel pull-ups.")
s.place("J9", 139, 17, ref_offset=(-2.54, -8.89), value_offset=(-5.08, -6.35))
s.stub("J9", 1, "+3V3", kind="power")
s.stub("J9", 3, "GND", kind="power")
s.place("R23", 120, 20)
s.place("R24", 120, 32)
s.place("R25", 133, 26, 90, ref_offset=(-2.54, -5.08), value_offset=(-2.54, -2.54))
s.place("C37", 146, 33)
p = s.pin("J9", 2)
a = s.pin("R23", 2)
b = s.pin("R24", 1)
c = s.pin("R25", 1)
s.wire(p, (125 * G, p[1]), (125 * G, 26 * G), (120 * G, 26 * G))
s.wire(a, b)
s.wire((120 * G, 26 * G), c)
s.stub("R23", 1, "+3V3", kind="power")
s.stub("R24", 2, "GND", kind="power")
a = s.pin("R25", 2)
b = s.pin("C37", 1)
s.wire(a, (b[0], a[1]), b)
s.label("REVERSER_AIN", (b[0], a[1]))
s.stub("C37", 2, "GND", kind="power")
s.port("REVERSER_AIN", 126, 43)
s.note(122, 48, "J9: 1=3V3, 2=common, 3=GND.\nSPDT center-off: F / N / R.")
for r, c, y in [("R12", "D17", 58), ("R13", "D18", 76)]:
    s.place(r, 149, y)
    s.place(c, 149, y + 4, 90, ref_offset=(3.81, -1.27), value_offset=(3.81, 1.27), hide_value=True)
    s.join((r, 2), (c, 2))
    s.stub(r, 1, "+3V3", kind="power")
s.stub("D17", 1, "GND", kind="power")
s.stub("D18", 1, "CHG_STAT")
s.port("CHG_STAT", 134, 82)
s.port("USB_VBUS", 136, 96)
s.finish()

blocks = ""
wiring = ""
pro = []
mcu_pins = []
for sh, ports, y, h in [
    (POWER, PWR_PORTS, 12, 18),
    (LEVER, LEVER_PORTS, 33, 22),
    (CONTROLS, CTRL_PORTS, 58, 22),
]:
    pins = []
    for i, n in enumerate(ports):
        yy = (y + 3 + i * 2) * G
        pins.append((n, "bidirectional", 108 * G, yy, 180))
        mcu_pins.append((n, "bidirectional", 57 * G, yy, 0))
        wiring += K.w_wire(57 * G, yy, 108 * G, yy) + K.w_label(n, 73 * G, yy)
    if sh is CONTROLS:
        for i, n in enumerate(["CHG_STAT", "USB_VBUS", "I2C0_SDA", "I2C0_SCL"]):
            yy = (y + 3 + len(ports) * 2 + i * 2) * G
            pins.append((n, "bidirectional" if n.startswith("I2C0_") else "input", 108 * G, yy, 180))
            wiring += K.w_wire(100 * G, yy, 108 * G, yy) + K.w_label(n, 100 * G, yy, 180)
    blocks += K.w_sheet(sh["name"], sh["file"], sh["uuid"], 108 * G, y * G, 41 * G, h * G, pins,
                        project="notchdeck-one", parent_path=f"/{ROOT_UUID}", page=sh["page"])
    pro.append([sh["uuid"], sh["name"]])
blocks += K.w_sheet(MCU["name"], MCU["file"], MCU["uuid"], 20 * G, 12 * G, 37 * G, 88 * G, mcu_pins,
                    project="notchdeck-one", parent_path=f"/{ROOT_UUID}", page=MCU["page"])
pro.insert(0, [MCU["uuid"], MCU["name"]])
wiring += K.text_note(
    "NOTCHDECK ONE / CONTROLLER INTERCONNECT\n3V3 and GND are global power rails; signals use explicit hierarchical ports.",
    20 * G,
    7 * G,
)
wiring += K.text_note(
    "Handle mux: I2C0 -> independent power/brake AS5600 channels (0x36); MAX17048 stays on I2C1.\nUSB powers the RGB array; battery powers controller + sensors. PCB is a provisional, unrouted floorplan.",
    20 * G,
    104 * G,
)
K.write_root("notchdeck-one", PROJ_DIR, ROOT_UUID, TITLE, blocks, wiring, pro, paper="A3")
