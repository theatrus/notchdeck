#!/usr/bin/env python3
"""Audit KiCad's exported connectivity against the controller's electrical contract.

Independent of the placement/generation manifest. Every physical component pin
must belong to exactly one expected net, or the explicit no-connect list.
Runs strict ERC (including warnings); no blanket ERC exclusions are accepted.
"""

from pathlib import Path
import importlib.util
import json
import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET

HW = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("schcheck", HW / "scripts/kicad-sch-check.py")
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def endpoints(text):
    return set(text.split())


def audit(xml_file):
    doc = ET.parse(xml_file)
    actual = {}
    by_pin = {}
    for net in doc.findall("./nets/net"):
        name = net.get("name")
        pins = {f"{n.get('ref')}.{n.get('pin')}" for n in net.findall("node")}
        actual[name] = pins
        for pin in pins:
            assert pin not in by_pin, f"{pin}: appears on two nets"
            by_pin[pin] = name
    expected = {}

    def net(name, pins):
        expected[name] = endpoints(pins) if isinstance(pins, str) else set(pins)

    net(
        "+3V3",
        """C1.1 C2.1 C3.1 C4.1 C5.1 C8.1 C9.1 C11.1 C12.1
        J3.1 J4.1 J9.1 R6.1 R7.1 R8.1 R9.1 R10.1 R12.1 R13.1
        R14.1 R15.1 R16.1 R17.1 R22.1 R23.1 U1.19 U1.23 U2.5 U5.1 U5.2""",
    )
    net(
        "/USB_VBUS",
        endpoints("C13.1 C18.1 C20.1 D19.2 J1.A4 J1.A9 J1.B4 J1.B9 R5.1 U1.27 U3.4 U7.5 U8.5")
        | {f"D{i}.1" for i in range(1, 17)}
        | {f"C{i}.1" for i in range(21, 37)},
    )
    net("/Power/BAT+", "C10.1 C19.1 J2.1 Q1.3 U3.3 U4.2 U4.3")
    net("/Power/VSYS", "C7.1 D19.1 Q1.2 U2.1 U2.3")
    net(
        "GND",
        endpoints("""D17.1 J1.A1 J1.A12 J1.B1 J1.B12 J1.SH J2.2 J3.3 J3.5 J3.9 J4.5
        J5.2 J6.2 J7.2 J8.2 J9.3 R1.1 R2.1 R3.2 R4.2 R24.2 R26.2
        U1.5 U1.21 U1.24 U2.2 U3.2 U4.1 U4.4 U4.6 U4.9 U5.4 U5.8 U7.2 U8.1 U8.3""")
        | {f"C{i}.2" for i in range(1, 38)}
        | {f"D{i}.3" for i in range(1, 17)}
        | {f"SW{i}.2" for i in range(1, 18)},
    )
    for i, pad in enumerate([1, 2, 6, 17, 32, 33, 40, 42, 41, 43, 11, 13], 1):
        net(f"/BTN{i}", f"SW{i}.1 U1.{pad}")
    for name, sw, pad in [("UP", 13, 34), ("DOWN", 14, 35), ("LEFT", 15, 36), ("RIGHT", 16, 38)]:
        net("/HAT_" + name, f"SW{sw}.1 U1.{pad}")
    for name, pins in {
        "/I2C0_SDA": "R9.2 U1.12 U5.6",
        "/I2C0_SCL": "R10.2 U1.14 U5.7",
        "/I2C1_SDA": "R6.2 U1.20 U4.8",
        "/I2C1_SCL": "R7.2 U1.22 U4.7",
        "/FG_ALRT": "R8.2 U1.28 U4.5",
        "/CHG_STAT": "D18.1 R22.2 U1.30 U3.1",
        "/USB_DM": "J1.A7 J1.B7 U1.29 U7.1 U7.6",
        "/USB_DP": "J1.A6 J1.B6 U1.31 U7.3 U7.4",
        "/MCU/SWDIO": "J3.2 J4.2 U1.37",
        "/MCU/SWDCLK": "J3.4 J4.4 U1.39",
        "/MCU/nRESET": "C6.1 J3.10 J4.3 SW17.1 U1.26",
        "/REVERSER_AIN": "C37.1 R25.2 U1.7",
        "/WS2812_DIN": "R26.1 U1.16 U8.2",
        "/Controls/LED_DATA": "D1.4 R11.2",
        "/Controls/LED_ROW2": "D8.2 D9.4",
    }.items():
        net(name, pins)
    for i, pad in enumerate([3, 4, 18, 15]):
        net(f"/LEVER_S{i}", f"C{14+i}.1 R{18+i}.2 U1.{pad}")
    # Internal wires are checked by endpoint sets, independent of KiCad's auto names.
    internal = [
        "J1.A5 R1.2",
        "J1.B5 R2.2",
        "Q1.1 R4.1 R5.2",
        "R3.1 U3.5",
        "J9.2 R23.2 R24.1 R25.1",
        "D17.2 R12.2",
        "D18.2 R13.2",
        "R11.1 U8.4",
    ]
    internal += [f"J{5+i}.1 R{14+i}.2 R{18+i}.1" for i in range(4)]
    internal += [f"D{i}.2 D{i+1}.4" for i in range(1, 16) if i != 8]
    for pins in internal:
        first = pins.split()[0]
        net(by_pin[first], pins)
    nc = endpoints("D16.2 J1.A8 J1.B8 J3.6 J3.7 J3.8 J4.6 U1.8 U1.9 U1.10 U1.25 U2.4 U5.3 U5.5")
    for pin in nc:
        name = by_pin[pin]
        assert name.startswith("unconnected-"), f"{pin}: expected explicit NC, got {name}"
        net(name, {pin})
    assert (
        actual.keys() == expected.keys()
    ), f"Unexpected/missing nets: {actual.keys() ^ expected.keys()}"
    for name, pins in expected.items():
        assert (
            pins == actual[name]
        ), f"{name}: missing {pins-actual[name]}, unexpected {actual[name]-pins}"
    # Values/variants crucial to the power path and input interface.
    comps = {c.get("ref"): c for c in doc.findall("./components/comp")}
    assert len(comps) == 116, f"Unexpected component count: {len(comps)}"
    for ref, value in {
        "U3": "MCP73832-2-OT",
        "U8": "74AHCT1G125",
        "Q1": "AO3401A",
        "R3": "2k",
        "R4": "100k",
        "R5": "1k",
        "C13": "1uF",
    }.items():
        assert comps[ref].findtext("value") == value, (ref, value)
    for ref, comp in comps.items():
        assert comp.findtext("footprint"), f"{ref}: no footprint"
    print(
        f"PASS: {len(comps)} components, {len(actual)} nets, {len(by_pin)} pin endpoints; {len(nc)} intentional NC pins"
    )
    return {name: sorted(pins) for name, pins in sorted(actual.items())}


def main():
    cli = helper.find_cli()
    schematic = HW / "notchdeck-one/notchdeck-one.kicad_sch"
    project = json.loads(schematic.with_suffix(".kicad_pro").read_text())
    assert not project.get("erc", {}).get(
        "erc_exclusions"
    ), "ERC exclusions must be reviewed explicitly"
    with tempfile.TemporaryDirectory(prefix="notchdeck-audit-") as tmp:
        xml_file, erc_file = Path(tmp) / "netlist.xml", Path(tmp) / "erc.json"
        subprocess.run(
            [
                cli,
                "sch",
                "export",
                "netlist",
                "--format",
                "kicadxml",
                "-o",
                str(xml_file),
                str(schematic),
            ],
            check=True,
        )
        result = audit(xml_file)
        subprocess.run(
            [
                cli,
                "sch",
                "erc",
                "--format",
                "json",
                "--exit-code-violations",
                "-o",
                str(erc_file),
                str(schematic),
            ],
            check=True,
        )
        report = json.loads(erc_file.read_text())
        violations = [v for s in report["sheets"] for v in s["violations"]]
        assert not violations, violations
        print("PASS: KiCad ERC, zero errors and zero warnings")
        if output := os.environ.get("NETCHECK_OUT"):
            folder = Path(output)
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "nets.json").write_text(json.dumps(result, indent=2) + "\n")
            (folder / "erc.json").write_text(erc_file.read_text())
            (folder / "netlist.xml").write_text(xml_file.read_text())


if __name__ == "__main__":
    main()
