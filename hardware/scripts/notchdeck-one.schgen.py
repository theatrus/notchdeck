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

import os, sys

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
K.register_stdlib("Connector_Generic", "Conn_01x02", "Conn_01x03")
K.register_stdlib("Regulator_Linear", "AP2112K-3.3")
K.register_stdlib("Battery_Management", "MCP73832-2-OT")
K.register_stdlib("Power_Protection", "USBLC6-2SC6")
K.register_stdlib("Transistor_FET", "Q_PMOS_GSD")
K.register_stdlib("Switch", "SW_Push")
K.register_stdlib("LED", "WS2812B")
K.register_stdlib("74xGxx", "74AHCT1G125")
K.register_lib(
    "notchdeck", NOTCH_SYM, "E73-2G4M08S1C", "AS5600", "MAX17048", "SWD_2x05", "SWD_TC2030"
)

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
            lcsc="C356849",
            mpn="E73-2G4M08S1C",
            mfr="Ebyte",
        ),
        dict(
            ref="J3",
            lib_id="notchdeck:SWD_2x05",
            value="SWD",
            fp="Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical_SMD",
        ),
        dict(
            ref="J4",
            lib_id="notchdeck:SWD_TC2030",
            value="TC2030_NL",
            fp="Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical",
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
            lcsc="C165948",
            mpn="TYPE-C-31-M-12",
        ),
    ],
    small=[
        dict(
            ref="U7",
            lib_id="Power_Protection:USBLC6-2SC6",
            value="USBLC6-2SC6",
            fp="Package_TO_SOT_SMD:SOT-23-6",
            lcsc="C2687116",
            mpn="USBLC6-2SC6",
            mfr="ST",
        ),
        R("R1", "5.1k"),
        R("R2", "5.1k"),
        dict(
            ref="U3",
            lib_id="Battery_Management:MCP73832-2-OT",
            value="MCP73832-2-OT",
            fp=SOT235,
            mpn="MCP73832T-2ACI/OT",
            mfr="Microchip",
        ),
        R("R3", "2k"),
        dict(
            ref="U2",
            lib_id="Regulator_Linear:AP2112K-3.3",
            value="AP2112K-3.3",
            fp=SOT235,
            lcsc="C23380830",
            mpn="AP2112K-3.3TRG1",
            mfr="Diodes",
        ),
        C("C7", "1uF"),
        C("C8", "1uF"),
        C("C9", "10uF", C0805),
        dict(
            ref="Q1",
            lib_id="Transistor_FET:Q_PMOS_GSD",
            value="AO3401A",
            fp=SOT23,
            lcsc="C15127",
            mpn="AO3401A",
            mfr="AOS",
        ),
        dict(
            ref="D19",
            lib_id="Device:D_Schottky",
            value="B5819W",
            fp="Diode_SMD:D_SOD-123",
            lcsc="C8598",
            mpn="B5819W",
            mfr="Slkor",
        ),
        R("R4", "100k"),
        R("R5", "1k"),
        dict(
            ref="U4",
            lib_id="notchdeck:MAX17048",
            value="MAX17048",
            fp="Package_DFN_QFN:TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm",
            lcsc="C2682616",
            mpn="MAX17048G+T10",
            mfr="Analog Devices",
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
            mpn="S2B-PH-SM4-TB",
            mfr="JST",
        ),
    ],
)

LEVER = dict(
    name="Lever",
    file="lever.kicad_sch",
    title="Lever sensing",
    page="4",
    big=[
        # One 2-pin JST-PH per coded-switch bit (signal + GND), 4 switches from the mascon.
        dict(
            ref="J5",
            lib_id="Connector_Generic:Conn_01x02",
            value="CODE S0",
            fp="Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
            mpn="S2B-PH-SM4-TB",
            mfr="JST",
        ),
        dict(
            ref="J6",
            lib_id="Connector_Generic:Conn_01x02",
            value="CODE S1",
            fp="Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
            mpn="S2B-PH-SM4-TB",
            mfr="JST",
        ),
        dict(
            ref="J7",
            lib_id="Connector_Generic:Conn_01x02",
            value="CODE S2",
            fp="Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
            mpn="S2B-PH-SM4-TB",
            mfr="JST",
        ),
        dict(
            ref="J8",
            lib_id="Connector_Generic:Conn_01x02",
            value="CODE S3",
            fp="Connector_JST:JST_PH_S2B-PH-SM4-TB_1x02-1MP_P2.00mm_Horizontal",
            mpn="S2B-PH-SM4-TB",
            mfr="JST",
        ),
    ],
    small=[
        dict(
            ref="U5",
            lib_id="notchdeck:AS5600",
            value="AS5600",
            fp="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
            lcsc="C499458",
            mpn="AS5600-ASOM",
            mfr="AMS",
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

ctrl = []
for i in range(1, 17):
    ctrl.append(dict(ref=f"SW{i}", lib_id="Switch:SW_Push", value="SW_Push", fp=BTN))
for i in range(1, 17):
    ctrl.append(
        dict(
            ref=f"D{i}",
            lib_id="LED:WS2812B",
            value="WS2812B",
            fp=WS2812FP,
            lcsc="C2843785",
            mpn="XL-5050RGBC-2812B",
        )
    )
ctrl += [
    C("C13", "1uF", C0805),
    R("R11", "330"),
    dict(ref="D17", lib_id="Device:LED", value="LED", fp=LED0603),
    R("R12", "1k"),
    dict(ref="D18", lib_id="Device:LED", value="LED", fp=LED0603),
    R("R13", "1k"),
]
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
        ref="U8",
        lib_id="74xGxx:74AHCT1G125",
        value="74AHCT1G125",
        fp=SOT235,
        mpn="SN74AHCT1G125DBVR",
        mfr="Texas Instruments",
    ),
    C("C20", "100nF"),
    dict(
        ref="J9",
        lib_id="Connector_Generic:Conn_01x03",
        value="REV F-N-R",
        fp="Connector_JST:JST_PH_S3B-PH-SM4-TB_1x03-1MP_P2.00mm_Horizontal",
        mpn="S3B-PH-SM4-TB",
        mfr="JST",
    ),
    R("R23", "100k"),
    R("R24", "100k"),
    R("R25", "1k"),
    C("C37", "100nF"),
    R("R26", "100k"),
] + [C(f"C{i}", "100nF") for i in range(21, 37)]
TITLE = dict(title="NotchDeck One", date="2026-10-02", rev="B", company="BenchBits")
G = 2.54


class Capture:
    def __init__(self, sh):
        self.sh = sh
        sh["_dir"] = PROJ_DIR
        sh["uuid"] = K._schematic_uuid(os.path.join(PROJ_DIR, sh["file"])) or K.U()
        self.path = f"/{ROOT_UUID}/{sh['uuid']}"
        self.parts = {c["ref"]: c for c in sh.get("big", []) + sh.get("small", [])}
        self.placed = {}
        self.extra = []
        self.segments = []
        self.points = set()
        self.connected = set()
        self.power_count = 0
        self.notes = []

    def place(self, ref, x, y, angle=0, **kw):
        c = dict(self.parts[ref], x=x * G, y=y * G, angle=angle, **kw)
        self.placed[ref] = c
        return c

    def pin(self, ref, n):
        self.connected.add((ref, str(n)))
        return K.pin_at(self.placed[ref], str(n))[:2]

    def wire(self, *points):
        for a, b in zip(points, points[1:]):
            a, b = tuple(round(v, 4) for v in a), tuple(round(v, 4) for v in b)
            assert a[0] == b[0] or a[1] == b[1], (a, b)
            if a != b:
                self.segments.append((a, b))
                self.points.update((a, b))

    def join(self, a, b, via=()):
        self.wire(self.pin(*a), *via, self.pin(*b))

    def label(self, net, p, angle=0):
        self.points.add(p)
        self.extra.append(K.w_label(net, *p, angle))

    def stub(self, ref, pin, net, length=2, kind="label"):
        x, y, a = K.pin_at(self.placed[ref], str(pin))
        dx, dy = K._OUTWARD[a]
        p = (round(x + dx * length * G, 4), round(y + dy * length * G, 4))
        self.wire(self.pin(ref, pin), p)
        if kind == "power":
            self.power(net, p)
        else:
            self.label(net, p, K._lbl_angle(dx, dy))
        return p

    def nc(self, ref, *pins):
        for n in pins:
            x, y = self.pin(ref, n)
            self.extra.append(f'\t(no_connect (at {x} {y}) (uuid "{K.U()}"))\n')

    def power(self, net, p, flag=False):
        if net not in ("GND", "+3V3") and not flag:
            self.label(net, p)
            return
        self.power_count += 1
        ref = f"#PWR{int(self.sh['page'])*100+self.power_count:03}"
        sym = "PWR_FLAG" if flag else net
        self.placed[ref] = dict(
            ref=ref,
            lib_id="power:" + sym,
            value=sym,
            x=p[0],
            y=p[1],
            in_bom=False,
            hide_value=net == "GND",
            value_offset=(-2.54, -3.81),
        )
        self.points.add(p)

    def rail(self, net, pins, y, flag=False):
        ps = [self.pin(*p) for p in pins]
        yy = y * G
        xs = sorted(set(p[0] for p in ps))
        for p in ps:
            self.wire(p, (p[0], yy))
        for a, b in zip(xs, xs[1:]):
            self.wire((a, yy), (b, yy))
        self.power(net, (xs[0], yy))
        if flag:
            self.power(net, (xs[-1], yy), flag=True)

    def port(self, net, x, y, shape="bidirectional"):
        p = (x * G, y * G)
        q = ((x + 10) * G, y * G)
        self.extra.append(K.w_hlabel(net, *p, 180, shape))
        self.wire(p, q)
        self.label(net, q)

    def note(self, x, y, text):
        self.notes.append((x * G, y * G, text))

    def finish(self):
        assert not set(self.parts) - set(self.placed), set(self.parts) - set(self.placed)
        missing = {
            (r, p["number"])
            for r, c in self.placed.items()
            if not r.startswith("#")
            for p in K.pin_geom(c["lib_id"])
        } - self.connected
        assert not missing, missing
        edges = set()
        for a, b in self.segments:
            pts = sorted(
                {
                    p
                    for p in self.points
                    if (a[0] == b[0] == p[0] and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))
                    or (a[1] == b[1] == p[1] and min(a[0], b[0]) <= p[0] <= max(a[0], b[0]))
                }
            )
            edges.update(zip(pts, pts[1:]))
        from collections import Counter

        degree = Counter(p for e in edges for p in e)
        wiring = "".join(K.w_wire(*a, *b) for a, b in sorted(edges))
        wiring += "".join(K.w_junction(*p) for p, n in degree.items() if n > 2) + "".join(
            self.extra
        )
        self.sh.update(
            comps=[(c, [(self.path, r)]) for r, c in self.placed.items()],
            wiring=wiring,
            notes=self.notes,
        )
        K.write_wired_child(self.sh, "notchdeck-one", ROOT_UUID, TITLE, "A3")


PWR_PORTS = ["USB_VBUS", "USB_DM", "USB_DP", "I2C1_SCL", "I2C1_SDA", "FG_ALRT", "CHG_STAT"]
LEVER_PORTS = ["I2C0_SCL", "I2C0_SDA", "LEVER_S0", "LEVER_S1", "LEVER_S2", "LEVER_S3"]
BUTTONS = [f"BTN{i}" for i in range(1, 13)] + ["HAT_UP", "HAT_DOWN", "HAT_LEFT", "HAT_RIGHT"]
CTRL_PORTS = ["WS2812_DIN", "REVERSER_AIN"] + BUTTONS

s = Capture(MCU)
s.place("U1", 40, 30, ref_offset=(-10.16, -35.56), value_offset=(-10.16, -33.02))
pinmap = {
    1: "BTN1",
    2: "BTN2",
    3: "LEVER_S0",
    4: "LEVER_S1",
    5: "GND",
    6: "BTN3",
    7: "REVERSER_AIN",
    11: "BTN11",
    12: "I2C0_SDA",
    13: "BTN12",
    14: "I2C0_SCL",
    15: "LEVER_S3",
    16: "WS2812_DIN",
    17: "BTN4",
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
    32: "BTN5",
    33: "BTN6",
    34: "HAT_UP",
    35: "HAT_DOWN",
    36: "HAT_LEFT",
    37: "SWDIO",
    38: "HAT_RIGHT",
    39: "SWDCLK",
    40: "BTN7",
    41: "BTN9",
    42: "BTN8",
    43: "BTN10",
}
for pin, net in pinmap.items():
    s.stub("U1", pin, net)  # same-name local rails join the decoupling power symbols
s.nc("U1", 8, 9, 10, 25)
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
    s.port(n, 132, 12 + 2.5 * i)
s.note(
    10,
    88,
    "SWD headers are parallel; VTref is 3V3. SWO is unused.\nReset: P0.18 / UICR reset enabled; double-tap enters bootloader.\nNFC pins P0.09/P0.10 must be configured as GPIO.\nP0.00/P0.01 are buttons: use calibrated RC LFCLK, no LFXO.\nSpare analog GPIOs P0.29/P0.31/P0.30 are intentionally NC.",
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
s.place("U5", 38, 27, ref_offset=(-10.16, -12.7), value_offset=(-10.16, -10.16))
s.place("C11", 14, 27)
s.place("C12", 23, 27)
s.rail("+3V3", [("C11", 1), ("C12", 1)], 20)
s.rail("GND", [("C11", 2), ("C12", 2)], 34)
for pin in [1, 2]:
    s.stub("U5", pin, "+3V3", kind="power")
for pin in [4, 8]:
    s.stub("U5", pin, "GND", kind="power")
s.nc("U5", 3, 5)
for pin, net, r, x in [(6, "I2C0_SDA", "R9", 59), (7, "I2C0_SCL", "R10", 72)]:
    s.place(r, x, 20)
    a = s.pin("U5", pin)
    b = s.pin(r, 2)
    s.wire(a, (b[0], a[1]), b)
    s.label(net, (b[0], a[1]))
    s.stub(r, 1, "+3V3", kind="power")
s.note(
    90,
    18,
    "AS5600: 3.3V mode, VDD5V tied to VDD3V3.\nI2C0 / 0x36; separate from the fuel gauge.\nDIR = GND, clockwise increases angle.\nOUT and PGO intentionally unused.",
)
for i in range(4):
    x = 18 + 37 * i
    y = 62
    j = f"J{5+i}"
    pu = f"R{14+i}"
    rs = f"R{18+i}"
    cap = f"C{14+i}"
    s.place(j, x, y, 180, ref_offset=(-2.54, -7.62), value_offset=(-2.54, -5.08))
    s.place(pu, x + 9, y - 10)
    s.place(rs, x + 17, y, 90, ref_offset=(-2.54, -5.08), value_offset=(-2.54, -2.54))
    s.place(cap, x + 24, y + 8)
    p = s.pin(j, 1)
    q = s.pin(rs, 1)
    b = s.pin(pu, 2)
    s.wire(p, q)
    s.wire(b, (b[0], p[1]))
    s.stub(pu, 1, "+3V3", kind="power")
    p = s.pin(rs, 2)
    q = s.pin(cap, 1)
    s.wire(p, (q[0], p[1]), q)
    s.label(f"LEVER_S{i}", (q[0], p[1]))
    s.stub(cap, 2, "GND", kind="power")
    s.stub(j, 2, "GND", kind="power")
    s.note(x - 2, 80, f"S{i}: switch closes to GND.\n10k pull-up / 1k series / 100nF.")
for i, n in enumerate(LEVER_PORTS):
    s.port(n, 15 + i * 24, 94)
s.note(
    12,
    103,
    "J5-J8: pin 1 = switch signal, pin 2 = GND. Both sensing front-ends may be populated.\nRC release ~1.1ms, press ~0.1ms. Firmware still debounces and decodes binary/Gray detent codes.",
)
s.finish()

s = Capture(CONTROLS)
for i, n in enumerate(BUTTONS):
    x = 17 + (i % 4) * 30
    y = 14 + (i // 4) * 10
    r = f"SW{i+1}"
    s.place(r, x, y, ref_offset=(-2.54, -6.35), value_offset=(-2.54, -3.81), hide_value=True)
    p = s.stub(r, 1, n)
    s.extra.pop()
    s.extra.append(K.w_hlabel(n, *p, 180, "passive"))
    s.stub(r, 2, "GND", kind="power")
s.note(60, 50, "Buttons/hat: active-low; MCU internal pull-ups + firmware debounce.")
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
s.place("U8", 34, 60, ref_offset=(-5.08, -8.89), value_offset=(-7.62, -6.35))
s.stub("U8", 1, "GND", kind="power")
s.stub("U8", 3, "GND", kind="power")
s.stub("U8", 5, "USB_VBUS")
p = s.stub("U8", 2, "WS2812_DIN")
s.extra.pop()
s.extra.append(K.w_hlabel("WS2812_DIN", *p, 180, "input"))
s.place("R26", 18, 65)
s.stub("R26", 1, "WS2812_DIN")
s.stub("R26", 2, "GND", kind="power")
s.place("R11", 48, 60, 90, ref_offset=(-2.54, -5.08), value_offset=(-2.54, -2.54))
s.join(("U8", 4), ("R11", 1))
s.stub("R11", 2, "LED_DATA")
s.place("C20", 62, 61)
s.stub("C20", 1, "USB_VBUS")
s.stub("C20", 2, "GND", kind="power")
s.place("C13", 76, 61)
s.stub("C13", 1, "USB_VBUS")
s.stub("C13", 2, "GND", kind="power")
s.note(
    87,
    59,
    "RGB: USB 5V only; 100nF at each LED.\nC13 1uF limits direct VBUS capacitance.\nBudget LEDs + charger against USB source.\nDrive DIN low while USB is absent.",
)
for row in range(2):
    y = 76 + 16 * row
    for col in range(8):
        i = row * 8 + col + 1
        x = 12 + 16 * col
        r = f"D{i}"
        cap = f"C{20+i}"
        s.place(r, x, y, ref_offset=(-3.81, -6.35), value_offset=(-3.81, 6.35), hide_value=True)
        s.place(cap, x + 5, y - 2.5, ref_offset=(1.27, -2.54), value_offset=(1.27, 2.54))
        if col:
            s.join((f"D{i-1}", 2), (r, 4))
    s.rail(
        "USB_VBUS",
        [(f"D{row*8+i}", 1) for i in range(1, 9)] + [(f"C{20+row*8+i}", 1) for i in range(1, 9)],
        y - 5,
    )
    s.rail(
        "GND",
        [(f"D{row*8+i}", 3) for i in range(1, 9)] + [(f"C{20+row*8+i}", 2) for i in range(1, 9)],
        y + 5,
    )
s.stub("D1", 4, "LED_DATA")
s.stub("D8", 2, "LED_ROW2", length=8)
s.stub("D9", 4, "LED_ROW2")
s.nc("D16", 2)
s.port("USB_VBUS", 136, 96)
s.finish()

blocks = ""
wiring = ""
pro = []
mcu_pins = []
for sh, ports, y, h in [
    (POWER, PWR_PORTS, 12, 19),
    (LEVER, LEVER_PORTS, 34, 16),
    (CONTROLS, CTRL_PORTS, 54, 42),
]:
    pins = []
    for i, n in enumerate(ports):
        yy = (y + 3 + i * 2) * G
        pins.append((n, "bidirectional", 108 * G, yy, 180))
        mcu_pins.append((n, "bidirectional", 57 * G, yy, 0))
        wiring += K.w_wire(57 * G, yy, 108 * G, yy) + K.w_label(n, 73 * G, yy)
    if sh is CONTROLS:
        for i, n in enumerate(["CHG_STAT", "USB_VBUS"]):
            yy = (y + 3 + len(ports) * 2 + i * 2) * G
            pins.append((n, "input", 108 * G, yy, 180))
            wiring += K.w_wire(100 * G, yy, 108 * G, yy) + K.w_label(n, 100 * G, yy, 180)
    blocks += K.w_sheet(sh["name"], sh["file"], sh["uuid"], 108 * G, y * G, 41 * G, h * G, pins,
                        project="notchdeck-one", parent_path=f"/{ROOT_UUID}", page=sh["page"])
    pro.append([sh["uuid"], sh["name"]])
blocks += K.w_sheet(MCU["name"], MCU["file"], MCU["uuid"], 20 * G, 12 * G, 37 * G, 84 * G, mcu_pins,
                    project="notchdeck-one", parent_path=f"/{ROOT_UUID}", page=MCU["page"])
pro.insert(0, [MCU["uuid"], MCU["name"]])
wiring += K.text_note(
    "NOTCHDECK ONE / CONTROLLER INTERCONNECT\n3V3 and GND are global power rails; signals use explicit hierarchical ports.",
    20 * G,
    7 * G,
)
wiring += K.text_note(
    "Two isolated I2C buses: AS5600 and MAX17048 both use address 0x36.\nUSB powers the RGB array; battery powers controller + sensors. PCB is a provisional, unrouted floorplan.",
    20 * G,
    104 * G,
)
K.write_root("notchdeck-one", PROJ_DIR, ROOT_UUID, TITLE, blocks, wiring, pro, paper="A3")
