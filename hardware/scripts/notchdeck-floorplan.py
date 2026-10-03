#!/usr/bin/env python3
"""Seed a provisional, unrouted PCB with KiCad's pcbnew API.

Run with KiCad's bundled Python on macOS. The saved PCB is the editable source
of truth after this initial placement; this script is NOT run by `make gen`.
Refuses to replace a populated board without --replace-unrouted, and never
replaces a board containing tracks, vias or copper pours.
"""

import argparse
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import pcbnew as P

HW = Path(__file__).resolve().parents[1]
PROJECT = HW / "notchdeck-one"
LIB = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")

# Absolute board coordinates, millimetres, top view. All components on F.Cu.
# Button centers are on a 19 mm square grid. LEDs follow a serpentine chain.
PLACEMENT = {
    "J1": (65, 54.4, 180),
    "U7": (65, 63.8, 0),
    "R1": (61.5, 62.2, 90),
    "R2": (68.5, 62.2, 90),
    "J2": (55.8, 79, 270),
    "U3": (66, 72, 0),
    "R3": (69, 69.5, 90),
    "C18": (69.5, 73, 90),
    "C19": (62.5, 74, 90),
    "R22": (71.5, 66.5, 0),
    "Q1": (76, 73, 0),
    "R4": (73, 73, 90),
    "R5": (73, 70.5, 90),
    "D19": (77, 67, 0),
    "U2": (84, 74, 0),
    "C7": (81, 73, 90),
    "C8": (87, 73, 90),
    "C9": (89.5, 74, 90),
    "U4": (64, 83, 0),
    "C10": (61.5, 83, 90),
    "R6": (67, 82, 0),
    "R7": (67, 84, 0),
    "R8": (67, 86, 0),
    "U1": (93, 66, 90),
    "C1": (92.5, 68.5, 90),
    "C3": (94.8, 68.5, 90),
    "C2": (97.2, 68.5, 90),
    "C4": (99.5, 68.5, 90),
    "C5": (102, 68.5, 90),
    "SW17": (105.5, 61, 0),
    "C6": (102, 65.5, 90),
    "J3": (93, 82, 0),
    "J4": (104, 80, 0),
    "U5": (81, 113, 0),
    "C11": (75.7, 111.5, 90),
    "C12": (75.7, 114, 90),
    "R9": (86.5, 111.5, 90),
    "R10": (86.5, 114, 90),
    "J9": (79, 149.2, 0),
    "R23": (78, 143, 90),
    "R24": (80.5, 143, 90),
    "R25": (84, 143, 0),
    "C37": (87, 143, 90),
    "U8": (111, 72, 0),
    "R26": (108, 73, 90),
    "C20": (114, 71, 90),
    "R11": (114.5, 74, 0),
    "C13": (119, 72, 90),
    "D17": (73, 54, 0),
    "R12": (73, 56.5, 0),
    "D18": (78, 54, 0),
    "R13": (78, 56.5, 0),
}
# Rev C dual handle interfaces. Preserve the original button grid.
PLACEMENT.update({
    "U9": (103, 96, 0), "U10": (133, 65, 0), "U11": (158, 65, 0),
    "J10": (133, 55.8, 180), "J11": (158, 55.8, 180),
    "J12": (55.8, 115, 270), "J5": (189.2, 114, 90),
    "R9": (96, 91, 90), "R10": (98, 91, 90),
    "R27": (99, 103, 0), "R28": (102, 103, 0),
    "R29": (105, 103, 0), "R30": (108, 103, 0),
    "R37": (87, 111, 90), "R38": (87, 114, 90), "R39": (106, 69, 90),
    "R40": (98, 98, 90), "R41": (98, 100, 90),
    "C38": (103, 100.3, 0), "C39": (137, 65, 90), "C40": (162, 65, 90),
})
# Rev D consolidates each Gray cam into a single polarized harness.
for i in range(3):
    PLACEMENT[f"R{31+i}"] = (62, 109 + 7*i, 90)
    PLACEMENT[f"R{34+i}"] = (64, 111 + 7*i, 0)
    PLACEMENT[f"C{41+i}"] = (66.5, 111 + 7*i, 90)
for i in range(4):
    PLACEMENT[f"R{14+i}"] = (97, 110 + 7*i, 90)
    PLACEMENT[f"R{18+i}"] = (100, 112 + 7*i, 0)
    PLACEMENT[f"C{14+i}"] = (103, 112 + 7*i, 90)
for row in range(4):
    for col in range(4):
        x, y = 122 + col * 19, 84 + row * 19
        PLACEMENT[f"SW{row*4+col+1}"] = (x, y, 0)
        led = row * 4 + (col + 1 if row % 2 == 0 else 4 - col)
        # DIN on the left for left-to-right rows; reverse for return rows.
        PLACEMENT[f"D{led}"] = (x, y - 7, 180 if row % 2 == 0 else 0)
        PLACEMENT[f"C{led+20}"] = (x, y - 10.8, 0)


def mm(x, y):
    return P.VECTOR2I(P.FromMM(x), P.FromMM(y))


def field_style(field, size=0.8):
    field.SetTextSize(mm(size, size))
    field.SetTextThickness(P.FromMM(0.12))
    field.SetTextAngle(P.EDA_ANGLE(0, P.DEGREES_T))


def text(board, value, x, y, size=1, layer=P.F_SilkS):
    item = P.PCB_TEXT(board)
    item.SetText(value)
    item.SetPosition(mm(x, y))
    item.SetLayer(layer)
    field_style(item, size)
    board.Add(item)


def line(board, a, b, layer=P.Edge_Cuts, width=0.05):
    item = P.PCB_SHAPE(board)
    item.SetShape(P.SHAPE_T_SEGMENT)
    item.SetStart(mm(*a))
    item.SetEnd(mm(*b))
    item.SetLayer(layer)
    item.SetWidth(P.FromMM(width))
    board.Add(item)


def load_footprint(lid):
    lib, name = lid.split(":", 1)
    folder = (
        HW / "lib/footprints.pretty" if lib == "notchdeck" else LIB / (lib + ".pretty")
    )
    fp = P.FootprintLoad(str(folder), name)
    if fp is None:
        raise ValueError(f"Missing footprint: {lid}")
    fp.SetFPID(P.LIB_ID(lib, name))
    return fp


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=PROJECT / "notchdeck-one.kicad_pcb")
    ap.add_argument("--replace-unrouted", action="store_true")
    args = ap.parse_args()
    if args.output.exists():
        with tempfile.TemporaryDirectory(prefix="notchdeck-existing-") as tmp:
            oldfile = Path(tmp) / "existing.kicad_pcb"
            shutil.copyfile(args.output, oldfile)
            old = P.LoadBoard(str(oldfile))
        if len(old.GetTracks()) or any(not z.GetIsRuleArea() for z in old.Zones()):
            ap.error("Refusing to overwrite routing or copper zones")
        if len(old.GetFootprints()) and not args.replace_unrouted:
            ap.error(
                "Board already populated; edit it in KiCad or explicitly use --replace-unrouted"
            )
    with tempfile.TemporaryDirectory(prefix="notchdeck-floorplan-") as tmp:
        netfile = Path(tmp) / "schematic.xml"
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
                str(PROJECT / "notchdeck-one.kicad_sch"),
            ],
            check=True,
        )
        tree = ET.parse(netfile)
    board = P.BOARD()
    board.SetCopperLayerCount(4)
    board.GetDesignSettings().SetBoardThickness(P.FromMM(1.6))
    title = board.GetTitleBlock()
    title.SetTitle("NotchDeck One - provisional floorplan")
    title.SetRevision("D")
    title.SetDate("2026-10-03")
    title.SetCompany("BenchBits")
    nets, pins = {}, {}
    for n in tree.findall(".//nets/net"):
        name = n.attrib["name"]
        if name.startswith("unconnected-("):
            name = name.replace("/", "{slash}")
        net = P.NETINFO_ITEM(board, name)
        board.Add(net)
        nets[name] = net
        for node in n.findall("node"):
            pins[(node.attrib["ref"], node.attrib["pin"])] = (net, node.attrib)
    components = tree.findall(".//components/comp")
    assert {c.attrib["ref"] for c in components} == set(PLACEMENT)
    placed = {}
    for c in components:
        ref = c.attrib["ref"]
        fp = load_footprint(c.findtext("footprint"))
        fp.SetReference(ref)
        fp.SetValue(c.findtext("value"))
        fp.SetField("Datasheet", c.findtext("datasheet", ""))
        excluded = c.find("property[@name='exclude_from_bom']") is not None
        attrs = fp.GetAttributes()
        if excluded:
            attrs |= P.FP_EXCLUDE_FROM_BOM | P.FP_EXCLUDE_FROM_POS_FILES
        else:
            attrs &= ~P.FP_EXCLUDE_FROM_BOM
        fp.SetAttributes(attrs)
        path = P.KIID_PATH()
        ids = c.find("sheetpath").attrib["tstamps"].strip("/").split("/")
        ids += c.findtext("tstamps").split()
        for uid in ids:
            path.push_back(P.KIID(uid))
        fp.SetPath(path)
        fp.SetSheetname(c.find("sheetpath").attrib["names"])
        fp.SetSheetfile(c.find("property[@name='Sheetfile']").attrib["value"])
        for prop in c.findall("property"):
            if prop.attrib["name"] not in ("Sheetname", "Sheetfile"):
                fp.SetField(prop.attrib["name"], prop.attrib.get("value", ""))
        fp.Value().SetVisible(False)
        for field in fp.GetFields():
            if field.GetName() != "Reference":
                field.SetVisible(False)
        board.Add(fp)
        x, y, angle = PLACEMENT[ref]
        fp.SetOrientationDegrees(angle)
        fp.SetPosition(mm(x, y))
        fp.Reference().SetPosition(mm(x, y + 3.8 if ref.startswith("SW") else y - 3.5))
        if ref.startswith(("R", "C")):
            fp.Reference().SetLayer(P.F_Fab)
            fp.Reference().SetPosition(mm(x, y - 1.5))
        elif ref.startswith("D") and int(ref[1:]) <= 16:
            fp.Reference().SetPosition(mm(x - 5.2, y))
        elif ref.startswith("J") and ref not in ("J1", "J3", "J4", "J9"):
            fp.Reference().SetPosition(mm(x + 6.5, y + 3))
        if ref == "J1":
            fp.Reference().SetPosition(mm(59, 54))
        if ref == "J2":
            fp.Reference().SetPosition(mm(55.8, 85))
        if ref == "J3":
            fp.Reference().SetPosition(mm(93, 74.5))
        if ref == "J9":
            fp.Reference().SetPosition(mm(87.5, 149))
        if ref == "U7":
            fp.Reference().SetPosition(mm(65, 66.5))
        if ref in ("U10", "U11"):
            fp.Reference().SetPosition(mm(x - 4, y))
        if ref in ("J10", "J11"):
            fp.Reference().SetPosition(mm(x + 8, y))
        if ref == "J12":
            fp.Reference().SetPosition(mm(56, 105))
        if ref == "J5":
            fp.Reference().SetPosition(mm(189, 103))
        if ref in ("D17", "D18"):
            fp.Reference().SetLayer(P.F_Fab)
        if ref == "U1":
            fp.Reference().SetPosition(mm(102, 53))
            for item in fp.GraphicalItems():
                if isinstance(item, P.PCB_TEXT):
                    item.SetLayer(P.F_Fab)
        field_style(fp.Reference())
        for pad in fp.Pads():
            entry = pins.get((ref, pad.GetNumber()))
            if entry:
                net, node = entry
                pad.SetNet(net)
                pad.SetPinFunction(node.get("pinfunction", ""))
                pad.SetPinType(node.get("pintype", ""))
            elif pad.GetNumber() not in ("", "MP"):
                raise ValueError(f"Unexpected pad {ref}.{pad.GetNumber()}")
        placed[ref] = fp

    for a, b in [
        ((50, 50), (195, 50)),
        ((195, 50), (195, 155)),
        ((195, 155), (50, 155)),
        ((50, 155), (50, 50)),
    ]:
        line(board, a, b)
    # Four provisional M3 mounting holes, excluded from schematic/BOM/positions.
    for i, (x, y) in enumerate([(55, 55), (190, 55), (190, 150), (55, 150)], 1):
        fp = load_footprint("MountingHole:MountingHole_3.2mm_M3")
        fp.SetReference(f"H{i}")
        fp.SetValue("M3 provisional")
        fp.SetAttributes(
            fp.GetAttributes()
            | P.FP_EXCLUDE_FROM_BOM
            | P.FP_EXCLUDE_FROM_POS_FILES
            | P.FP_BOARD_ONLY
        )
        board.Add(fp)
        fp.SetPosition(mm(x, y))
        fp.Value().SetVisible(False)
        fp.Reference().SetPosition(mm(x, y + 4.5 if y < 100 else y - 4.5))
        field_style(fp.Reference())

    # Radio's antenna end overhangs the north edge. No copper in this region
    # on any of the four layers. Footprint exclusion is manual because U1's
    # own antenna body must overlap the region.
    z = P.ZONE(board)
    z.SetIsRuleArea(True)
    layers = P.LSET()
    for layer in (P.F_Cu, P.In1_Cu, P.In2_Cu, P.B_Cu):
        layers.AddLayer(layer)
    z.SetLayerSet(layers)
    z.SetZoneName("U1 ANTENNA - NO COPPER ALL LAYERS")
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowPads(True)
    z.SetDoNotAllowZoneFills(True)
    z.Outline().NewOutline()
    for x, y in [(81, 43), (105, 43), (105, 51.3), (81, 51.3)]:
        z.Outline().Append(P.FromMM(x), P.FromMM(y))
    board.Add(z)
    text(board, "ANTENNA: NO COPPER / METAL", 93, 46, 0.8, P.Dwgs_User)
    text(board, "NOTCHDECK ONE", 145, 69, 1.3)
    text(board, "REV D / DUAL + MASCON", 177, 65, 0.8)
    text(board, "USB", 60, 66, 0.8)
    text(board, "BAT+  GND", 59, 91, 0.8)
    text(board, "3V3", 73, 51, 0.8)
    text(board, "CHG", 78, 51, 0.8)
    text(board, "SWD", 93, 90, 1)
    text(board, "TC2030", 104, 87, 1)
    text(board, "RESET", 106, 56, 0.8)
    text(board, "POWER / COMBINED AXIS", 81, 123, 1)
    text(board, "Align magnet to U5 center", 82, 127, 0.8, P.Dwgs_User)
    text(board, "REV F / N / R", 82, 139, 1)
    text(
        board, "PROVISIONAL 145 x 105 mm - MECHANICS TBD", 122.5, 158, 1.2, P.Dwgs_User
    )
    text(board, "UNROUTED / DO NOT FABRICATE", 146, 150, 1)
    for row in range(4):
        for col in range(4):
            n = row * 4 + col + 1
            name = f"BTN {n}" if n <= 12 else ["UP", "DOWN", "LEFT", "RIGHT"][n - 13]
            text(board, name, 122 + col * 19, 84 + row * 19 + 6, 0.8)
    text(board, "POWER MAG", 133, 61.5, 0.8)
    text(board, "BRAKE MAG", 158, 61.5, 0.8)
    text(board, "J10 EXT: REMOVE R37/R38", 81, 134, 0.8)
    text(board, "POWER GRAY", 62, 101, 0.8)
    for value, x in [("BRAKE / MASCON", 190), ("GRAY", 187)]:
        item = P.PCB_TEXT(board)
        item.SetText(value)
        item.SetPosition(mm(x, 135))
        item.SetLayer(P.F_SilkS)
        field_style(item, 0.8)
        item.SetTextAngle(P.EDA_ANGLE(90, P.DEGREES_T))
        board.Add(item)
    for value, x, y in [
        ("J12 POWER: 1 GND / 2 S0 / 3 S1 / 4 S2 / 5 3V3", 84, 119),
        ("J5 BRAKE / MASCON: 1 GND / 2 S0 / 3 S1 / 4 S2 / 5 S3 / 6 3V3", 161, 130),
        ("GRAY CONTACTS: LEAVE 3V3 WIRE OUT", 108, 137),
    ]:
        item = P.PCB_TEXT(board)
        item.SetText(value)
        item.SetPosition(mm(x, y))
        item.SetLayer(P.B_SilkS)
        item.SetMirrored(True)
        field_style(item, 0.8)
        board.Add(item)
    # Reserve physical shaft/magnet space as a drawing, not a copper exclusion.
    ring = P.PCB_SHAPE(board)
    ring.SetShape(P.SHAPE_T_CIRCLE)
    ring.SetCenter(mm(81, 113))
    ring.SetEnd(mm(91, 113))
    ring.SetLayer(P.Dwgs_User)
    ring.SetWidth(P.FromMM(0.1))
    board.Add(ring)
    board.BuildConnectivity()
    # SaveBoard also serializes project defaults. Save in isolation and copy
    # only the PCB so the user's ERC/design/netclass settings stay untouched.
    with tempfile.TemporaryDirectory(prefix="notchdeck-save-") as tmp:
        boardfile = Path(tmp) / args.output.name
        P.SaveBoard(str(boardfile), board)
        shutil.copyfile(boardfile, args.output)
    print(
        f"Saved {args.output}: {len(placed)} electrical footprints + 4 mounting holes, {len(nets)} nets"
    )


if __name__ == "__main__":
    main()
