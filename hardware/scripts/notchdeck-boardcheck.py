#!/usr/bin/env python3
"""Read-only schematic/PCB pad-net and identity audit; run with KiCad Python."""

from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import pcbnew as P


def main():
    project = Path(__file__).resolve().parents[1] / "notchdeck-one"
    with tempfile.TemporaryDirectory(prefix="notchdeck-boardcheck-") as tmp:
        netfile = Path(tmp) / "netlist.xml"
        subprocess.run(
            [
                os.environ.get("KICAD_CLI", "kicad-cli"),
                "sch",
                "export",
                "netlist",
                "--format",
                "kicadxml",
                "-o",
                str(netfile),
                str(project / "notchdeck-one.kicad_sch"),
            ],
            check=True,
        )
        tree = ET.parse(netfile)
        # Inspect a copy: pcbnew's project serialization must never touch the
        # user's design rules or settings during this read-only audit.
        boardfile = Path(tmp) / "audit.kicad_pcb"
        shutil.copyfile(project / "notchdeck-one.kicad_pcb", boardfile)
        board = P.LoadBoard(str(boardfile))
    components = {c.attrib["ref"]: c for c in tree.findall(".//components/comp")}
    expected = {}
    for net in tree.findall(".//nets/net"):
        name = net.attrib["name"]
        if name.startswith("unconnected-("):
            name = name.replace("/", "{slash}")
        for node in net.findall("node"):
            expected[(node.attrib["ref"], node.attrib["pin"])] = name
    fps = {
        fp.GetReference(): fp
        for fp in board.GetFootprints()
        if not fp.GetAttributes() & P.FP_BOARD_ONLY
    }
    assert set(fps) == set(components), "Schematic and PCB references differ"
    actual = {}
    for ref, fp in fps.items():
        comp = components[ref]
        assert fp.GetValue() == comp.findtext("value"), f"Value mismatch: {ref}"
        assert fp.GetFPIDAsString() == comp.findtext(
            "footprint"
        ), f"Footprint mismatch: {ref}"
        fields = {f.attrib["name"]: f.text or "" for f in comp.findall("fields/field")}
        pcb_fields = {f.GetName(): f.GetText() for f in fp.GetFields()}
        for name in (
            "LCSC",
            "MPN",
            "Manufacturer",
            "BOM Comments",
            "BOM Checked",
            "JLCPCB Part Type",
        ):
            assert pcb_fields.get(name, "") == fields.get(
                name, ""
            ), f"{name} mismatch: {ref}"
        assert pcb_fields.get("Datasheet", "") == comp.findtext(
            "datasheet", ""
        ), f"Datasheet mismatch: {ref}"
        excluded = comp.find("property[@name='exclude_from_bom']") is not None
        assert (
            bool(fp.GetAttributes() & P.FP_EXCLUDE_FROM_BOM) == excluded
        ), f"BOM exclusion mismatch: {ref}"
        assert (
            bool(fp.GetAttributes() & P.FP_EXCLUDE_FROM_POS_FILES) == excluded
        ), f"Placement exclusion mismatch: {ref}"
        path = comp.find("sheetpath").attrib["tstamps"] + comp.findtext("tstamps")
        assert fp.GetPath().AsString().rstrip("/") == path.rstrip(
            "/"
        ), f"Identity mismatch: {ref}"
        for pad in fp.Pads():
            pin = pad.GetNumber()
            if pin in ("", "MP"):
                assert (
                    not pad.GetNetname()
                ), f"Unexpected mechanical pad net: {ref}.{pin}"
                continue
            key = (ref, pin)
            net = pad.GetNetname()
            assert key in expected, f"Unexpected PCB pad: {key}"
            assert (
                net == expected[key]
            ), f"Net mismatch: {key}: {net} != {expected[key]}"
            actual[key] = net
    assert actual == expected, f"Missing pads: {set(expected) - set(actual)}"
    print(
        f"PASS: {len(fps)} footprints, {len(set(actual.values()))} nets, "
        f"{len(actual)} unique pin endpoints, sourcing fields and all schematic UUID paths match"
    )
    print(
        f"PCB stage: {len(board.GetTracks())} tracks/vias, "
        f"{board.GetCopperLayerCount()} copper layers; routing is not assessed by this audit"
    )


if __name__ == "__main__":
    main()
