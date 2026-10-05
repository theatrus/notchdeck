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
        R14.1 R15.1 R16.1 R17.1 R22.1 R23.1 U1.19 U1.23 U2.5 U5.1 U5.2
        C38.1 C39.1 C40.1 J10.1 J11.1 J5.6 J12.5 U9.14 U10.5 U11.5
        R27.1 R28.1 R29.1 R30.1 R31.1 R32.1 R33.1 R39.1 R40.1 R41.1 J15.2 R42.1 U12.5 C44.1 R57.1 R59.1""",
    )
    net(
        "/USB_VBUS",
        endpoints("C18.1 J15.6 D19.2 J1.A4 J1.A9 J1.B4 J1.B9 R5.1 U1.27 U3.4 U7.5"),
    )
    net("/Actuators/BAT_RAW", "J2.1 J2.2 U13.5 C47.1 R52.1 D24.1")
    net("/BAT_PROT", "C10.1 C19.1 Q1.3 U3.3 U4.2 U4.3 U13.6 D23.1 D24.2 C45.1 C46.1 J16.1 J17.1 J18.1 D20.1 D21.1 D22.1")
    net("/Power/VSYS", "C7.1 D19.1 Q1.2 U2.1 U2.3")
    net(
        "GND",
        endpoints("""D17.1 J1.A1 J1.A12 J1.B1 J1.B12 J1.SH J2.3 J2.4 J3.3 J3.5 J3.9 J4.5
        J5.1 J9.3 R1.1 R2.1 R4.2 R24.2
        U1.5 U1.21 U1.24 U2.2 U3.2 U4.1 U4.4 U4.6 U4.9 U5.4 U5.8 U7.2 U12.2
        J15.1 SW18.2 SW19.2 J10.2 J11.2 J12.1 U9.1 U9.2 U9.7 U10.2 U11.2""")
        | {f"C{i}.2" for i in range(1, 45) if i not in (13,20) and not 21 <= i <= 36}
        | endpoints("SW17.2 Q2.3 Q3.3 Q4.3 R46.2 R47.2 R48.2 C45.2 C46.2 J19.1 U13.8 U13.2 Q5.2 C47.2 C48.2 R53.2 R55.2 R58.2 D23.2 Q6.2"),
    )
    net("/ACT_EN", "U1.35 R54.1")
    net("/BAT_nFAULT", "U1.36 R57.2 U13.4")
    net("/Actuators/BAT_ENABLE", "U13.1 R52.2 R53.1")
    net("/CHARGE_ENABLE", "Q5.3 Q6.1 R59.2")
    net("/BTN7", "SW18.1 U1.40")
    net("/BTN8", "SW19.1 U1.42")
    net("/PANEL_INT", "J15.5 R42.2 U1.1")
    for i, (name, pad) in enumerate([( "SOL1",32),("SOL2",33),("BUZZ",34)]):
        net(f"/{name}_PWM", f"U1.{pad} R{43+i}.1 R{49+i}.1")
        net(f"/Actuators/{name}_LOW", f"Q{2+i}.2 D{20+i}.2 J{16+i}.2")
        net(f"/Actuators/{name}_PWM_EXT", f"R{49+i}.2 J19.{2+i}")
    for name, pins in {
        "/I2C0_SDA": "R9.2 U1.12 U9.13 J15.3 U12.1 U12.6",
        "/I2C0_SCL": "R10.2 U1.14 U9.12 J15.4 U12.3 U12.4",
        "/Lever/POWER_MAG_SDA": "U9.5 R27.2 R37.2 J10.3 U10.1 U10.6",
        "/Lever/POWER_MAG_SCL": "U9.6 R28.2 R38.2 J10.4 U10.3 U10.4",
        "/Lever/BRAKE_MAG_SDA": "U9.9 R29.2 J11.3 U11.1 U11.6",
        "/Lever/BRAKE_MAG_SCL": "U9.10 R30.2 J11.4 U11.3 U11.4",
        "/Lever/U5_POWER_MAG_SDA": "R37.1 U5.6",
        "/Lever/U5_POWER_MAG_SCL": "R38.1 U5.7",
        "/Lever/MUX_INT0": "R40.2 U9.4",
        "/Lever/MUX_INT1": "R41.2 U9.8",
        "/I2C1_SDA": "R6.2 U1.20 U4.8",
        "/I2C1_SCL": "R7.2 U1.22 U4.7",
        "/FG_ALRT": "R8.2 U1.28 U4.5",
        "/CHG_STAT": "D18.1 R22.2 U1.30 U3.1",
        "/USB_DM": "J1.A7 J1.B7 U1.29 U7.1 U7.6",
        "/USB_DP": "J1.A6 J1.B6 U1.31 U7.3 U7.4",
        "/MCU/SWDIO": "J3.2 J4.2 U1.37",
        "/MCU/SWDCLK": "J3.4 J4.4 U1.39",
        "/nRESET": "C6.1 J3.10 J4.3 SW17.1 U1.26 U9.3 R39.2",
        "/REVERSER_AIN": "C37.1 R25.2 U1.7",
    }.items():
        net(name, pins)
    for i, pad in enumerate([3, 4, 18, 15]):
        net(f"/LEVER_S{i}", f"C{14+i}.1 R{18+i}.2 U1.{pad}")
    for i, pad in enumerate([8, 9, 10]):
        net(f"/POWER_S{i}", f"C{41+i}.1 R{34+i}.2 U1.{pad}")
    # Internal wires are checked by endpoint sets, independent of KiCad's auto names.
    internal = [
        "J1.A5 R1.2",
        "J1.B5 R2.2",
        "Q1.1 R4.1 R5.2",
        "R3.1 U3.5",
        "R3.2 Q6.3",
        "J9.2 R23.2 R24.1 R25.1",
        "D17.2 R12.2",
        "D18.2 R13.2",
        "Q5.1 R54.2 R55.1",
        "U13.9 R56.1",
        "R56.2 R58.1",
        "U13.7 R60.2",
        "R60.1 C48.1",
    ]
    internal += [f"J5.{2+i} R{14+i}.2 R{18+i}.1" for i in range(4)]
    internal += [f"J12.{2+i} R{31+i}.2 R{34+i}.1" for i in range(3)]
    internal += [f"R{43+i}.2 R{46+i}.1 Q{2+i}.1" for i in range(3)]
    for pins in internal:
        first = pins.split()[0]
        net(by_pin[first], pins)
    nc = endpoints("J1.A8 J1.B8 J3.6 J3.7 J3.8 J4.6 U1.25 U2.4 U5.3 U5.5 U9.11 U13.3 U13.10")
    nc |= {f"U1.{p}" for p in (2,6,11,13,16,17,38,41,43)}
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
    assert len(comps) == 130, f"Unexpected component count: {len(comps)}"
    for ref, value in {
        "U3": "MCP73832-2-OT",
        "U9": "TCA9543APWR",
        "R37": "0",
        "R38": "0",
        "Q1": "AO3401A",
        "R3": "2k",
        "R4": "100k",
        "R5": "1k",
        "R42": "10k",
        "SW18": "SELECT",
        "SW19": "START",
        **{f"Q{i}": "ZXMS6005DGTA" for i in (2,3,4)},
        **{f"D{i}": "B360A" for i in (20,21,22,23,24)},
        **{f"R{i}": "330" for i in (43,44,45,56,58)},
        **{f"R{i}": "100k" for i in (46,47,48,52,53,55,59)},
        **{f"R{i}": "1k" for i in (49,50,51,54)},
        "R60": "100", "U13": "TPS259461LRPWR", "Q5": "2N7002", "Q6": "2N7002", "R57": "10k",
        "C45": "22uF", "C46": "22uF", "C47": "1uF", "C48": "100nF",
    }.items():
        assert comps[ref].findtext("value") == value, (ref, value)
    assert "F1" not in comps, "Use electronic/resettable protection only"
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
        erc_run = subprocess.run(
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
            check=False,
        )
        report = json.loads(erc_file.read_text())
        violations = [v for s in report["sheets"] for v in s["violations"]]
        if violations:
            from collections import Counter
            print("ERC violation types:", dict(Counter(v["type"] for v in violations)))
            for violation in violations[:8]:
                print(json.dumps(violation, indent=2))
        assert not violations, f"{len(violations)} ERC violations"
        erc_run.check_returncode()
        print("PASS: KiCad ERC, zero errors and zero warnings")
        if output := os.environ.get("NETCHECK_OUT"):
            folder = Path(output)
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "nets.json").write_text(json.dumps(result, indent=2) + "\n")
            (folder / "erc.json").write_text(erc_file.read_text())
            (folder / "netlist.xml").write_text(xml_file.read_text())


if __name__ == "__main__":
    main()
