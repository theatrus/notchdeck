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


# Rev E: main logic/connector board, no 4x4 array.
PLACEMENT.update({
    "J5": (159.2, 109, 90), "J9": (79, 134.2, 0),
    "R23": (78,128,90), "R24": (80.5,128,90), "R25": (84,128,0), "C37": (87,128,90),
    "J10": (119,134.2,0), "J11": (145,134.2,0),
    "U10": (119,125,0), "U11": (145,125,0), "C39": (123,125,90), "C40": (149,125,90),
    "J15": (124,64,90), "SW18": (128,104,0), "SW19": (147,104,0),
})
PLACEMENT.pop("C13")
for ref in ("U8","R11","R26","C20"):PLACEMENT.pop(ref)
PLACEMENT.update({"J15":(135,54.2,180),"U12":(135,62,0),"C44":(140,62,90),"R42":(130,63,90)})
# Rev F keeps all Rev E component locations and adds the actuator bank.
PLACEMENT.update({
    "J16": (159.2, 74, 90), "J17": (159.2, 89, 90),
    "J18": (117, 55.8, 180), "J19": (55.8, 97, 270),
    "Q2": (144, 73, 0), "Q3": (144, 89, 0), "Q4": (117, 79, 0),
    "D20": (152, 72, 90), "D21": (152, 88, 90), "D22": (117, 66, 0),
    "C45": (150, 79, 90), "C46": (150, 94, 90),
    "R43": (135, 72, 0), "R44": (135, 88, 0), "R45": (114, 87, 0),
    "R46": (136, 76, 90), "R47": (136, 92, 90), "R48": (122, 87, 90),
    "Q6": (70.5, 78.5, 0), "R59": (74, 78.5, 90),
    "U13": (77, 87, 0), "C47": (74, 87, 90), "D23": (81, 84, 90),
    "C48": (74, 92, 90), "Q5": (83, 95, 0), "R52": (77, 98, 0),
    "R53": (80, 98, 90), "R54": (84, 99, 0), "R55": (87, 95, 90),
    "R56": (79, 90, 0), "R58": (79, 92, 0), "R57": (73, 98, 90),
    "R49": (66, 94, 0), "R50": (66, 97, 0), "R51": (66, 100, 0),
})
PLACEMENT.update({"J2": (60, 79, 90), "C19": (66.5, 76.5, 90), "U4": (68, 86, 0), "C10": (65.5, 86, 90), "R6": (71, 84, 0), "R7": (71, 86, 0), "R8": (71, 88, 0), "D24": (87, 88, 90), "R60": (74, 94.5, 0)})
BUTTON_PLACEMENT={
 "J1":(93,165,0),"J2":(66,154,0),"U1":(94,147,90),"U2":(106,162,0),
 "U8":(118,151,0),"R11":(118,146,0),"R26":(114,151,90),"C20":(122,151,90),"C13":(124,141,90),
 "C1":(97,141.8,0),"C2":(101,143,90),"C3":(83,145,90),"C4":(105,156,90),"C5":(103,165,90),
 "R1":(83,141,0),"R2":(84,152,90),"R3":(87,152,90),"R4":(90,152,90),"R5":(93,152,90),
 "R6":(109,154,90),"R7":(109,158,90),
}
for row in range(4):
    for col in range(4):
        x,y=64.5+col*19,72+row*19
        BUTTON_PLACEMENT[f"SW{row*4+col+1}"]=(x,y,0)
        BUTTON_PLACEMENT[f"D{20+row*4+col}"]=(x+7,y+2.5,90)
        led=row*4+(col+1 if row%2==0 else 4-col)
        BUTTON_PLACEMENT[f"D{led}"]=(x,y-7,180 if row%2==0 else 0)
        BUTTON_PLACEMENT[f"C{20+led}"]=(x,y-10.8,0)


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
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", choices=("notchdeck-one","notchdeck-buttons"), default="notchdeck-one")
    ap.add_argument("--output",type=Path)
    ap.add_argument("--replace-unrouted",action="store_true")
    args=ap.parse_args()
    project_name=args.project
    project=HW/project_name
    output=args.output or project/(project_name+".kicad_pcb")
    identities={}
    # Preserve footprint identities; the migration may draw moved parts from main.
    for name in ("notchdeck-one",project_name):
        source=HW/name/(name+".kicad_pcb")
        if not source.exists():continue
        with tempfile.TemporaryDirectory(prefix="notchdeck-old-") as tmp:
            copy=Path(tmp)/"board.kicad_pcb";shutil.copyfile(source,copy)
            old=P.LoadBoard(str(copy))
            if name==project_name:
                if len(old.GetTracks()) or any(not z.GetIsRuleArea() for z in old.Zones()):
                    ap.error("Refusing to replace routing or copper pours")
                if len(old.GetFootprints()) and not args.replace_unrouted:
                    ap.error("Use --replace-unrouted for an intentional floorplan reset")
            for fp in old.GetFootprints():
                identities[fp.GetReference()]=(fp.GetFPIDAsString(),fp.m_Uuid.AsString())
    with tempfile.TemporaryDirectory(prefix="notchdeck-floorplan-") as tmp:
        netfile=Path(tmp)/"schematic.xml"
        subprocess.run([os.environ.get("KICAD_CLI","kicad-cli"),"sch","export","netlist","--format","kicadxml","-o",str(netfile),str(project/(project_name+".kicad_sch"))],check=True)
        tree=ET.parse(netfile)
    board=P.BOARD()
    is_main=project_name=="notchdeck-one"
    placements=PLACEMENT if is_main else BUTTON_PLACEMENT
    board.SetCopperLayerCount(4 if is_main else 2)
    board.GetDesignSettings().SetBoardThickness(P.FromMM(1.6))
    title=board.GetTitleBlock();title.SetTitle(project_name+" - provisional floorplan");title.SetRevision("G" if is_main else "E");title.SetDate("2026-10-04" if is_main else "2026-10-03");title.SetCompany("BenchBits")
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
    assert {c.attrib["ref"] for c in components} == set(placements)
    placed = {}
    for c in components:
        ref = c.attrib["ref"]
        fp = load_footprint(c.findtext("footprint"))
        if ref in identities and identities[ref][0] == c.findtext("footprint"):
            fp.SetUuid(P.KIID(identities[ref][1]))
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
        x, y, angle = placements[ref]
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
        if ref == "J1" and project_name == "notchdeck-one":
            fp.Reference().SetPosition(mm(59, 54))
        if ref == "J2" and is_main:
            fp.Reference().SetPosition(mm(55.8, 85))
        if ref == "J3":
            fp.Reference().SetPosition(mm(93, 74.5))
        if ref == "J9":
            fp.Reference().SetLayer(P.F_Fab)
        if ref == "U7":
            fp.Reference().SetPosition(mm(65, 66.5))
        if ref in ("U10", "U11", "U12"):
            fp.Reference().SetPosition(mm(x - 4, y))
        if ref == "U12":
            fp.Reference().SetPosition(mm(x, y + 3.5))
        if ref in ("J10", "J11", "J12", "J5", "J15") or (project_name == "notchdeck-buttons" and ref == "J1"):
            fp.Reference().SetLayer(P.F_Fab)
            fp.Reference().SetPosition(mm(x,y))
        if ref in ("D17", "D18"):
            fp.Reference().SetLayer(P.F_Fab)
        if is_main and ref in ("J16", "J17", "J18", "J19", "D20", "D21", "D22", "D23", "D24", "Q6"):
            fp.Reference().SetLayer(P.F_Fab)
            fp.Reference().SetPosition(mm(x, y))
        if is_main and ref in ("Q2", "Q3", "Q4"):
            fp.Reference().SetPosition(mm(x, y - 5.5))
        if ref == "U1" and is_main:
            fp.Reference().SetPosition(mm(102, 53))
            for item in fp.GraphicalItems():
                if isinstance(item, P.PCB_TEXT):
                    item.SetLayer(P.F_Fab)
        if ref == "U1" and not is_main:
            fp.Reference().SetPosition(mm(x, y - 7.2))
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

    width,height=(115,90) if is_main else (86,120)
    corners=[(50,50),(50+width,50),(50+width,50+height),(50,50+height)]
    for a,b in zip(corners,corners[1:]+corners[:1]):line(board,a,b)
    for i,(x,y) in enumerate([(55,55),(45+width,55),(45+width,45+height),(55,45+height)],1):
        fp=load_footprint("MountingHole:MountingHole_3.2mm_M3")
        fp.SetReference(f"H{i}");fp.SetValue("M3 provisional")
        if f"H{i}" in identities:fp.SetUuid(P.KIID(identities[f"H{i}"][1]))
        fp.SetAttributes(fp.GetAttributes()|P.FP_EXCLUDE_FROM_BOM|P.FP_EXCLUDE_FROM_POS_FILES|P.FP_BOARD_ONLY)
        board.Add(fp);fp.SetPosition(mm(x,y));fp.Value().SetVisible(False);fp.Reference().SetLayer(P.F_Fab)
        fp.Reference().SetPosition(mm(x,y));field_style(fp.Reference())
    if is_main:
        z=P.ZONE(board);z.SetIsRuleArea(True)
        layers=P.LSET()
        for layer in (P.F_Cu,P.In1_Cu,P.In2_Cu,P.B_Cu):layers.AddLayer(layer)
        z.SetLayerSet(layers);z.SetZoneName("U1 ANTENNA - NO COPPER ALL LAYERS")
        z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowPads(True);z.SetDoNotAllowZoneFills(True)
        z.Outline().NewOutline()
        for x,y in [(81,43),(105,43),(105,51.3),(81,51.3)]:z.Outline().Append(P.FromMM(x),P.FromMM(y))
        board.Add(z)
        text(board,"ANTENNA: NO COPPER / METAL",93,46,.8,P.Dwgs_User)
        for value,x,y in [("USB",60,66),("J2: 1,2 BAT+ / 3,4 GND",62,89),("SWD",93,90),("TC2030",104,87),("RESET",106,56),("POWER GRAY",62,129),("BRAKE / MASCON GRAY",146,117),("POWER MAG",119,138),("BRAKE MAG",145,138),("REV F/N/R",79,138),("SELECT",128,111),("START",147,111),("J15 BUTTON FFC",135,69),("REMOVE R37/R38 FOR J10",80,120)]:text(board,value,x,y,.8)
        text(board,"NOTCHDECK LOGIC / REV G",123,98,1)
        for value,x,y in [("SOL1",160,81),("SOL2",160,96),("BUZZ",117,61),("J19 3V3 PWM ONLY",78,103)]:text(board,value,x,y,.8)
        notes=["J15 -> BUTTON J1: 6-WAY 1mm FFC TYPE A", "J15: 1 GND / 2 3V3 / 3 SDA / 4 SCL / 5 IRQ / 6 USB5V", "MAIN PIN n -> BUTTON PIN 7-n - POWER OFF TO INSERT", "SW18 SELECT=BTN7; SW19 START=BTN8 (PARALLEL)", "J12: 1 GND / 2..4 POWER S0..S2 / 5 3V3", "J5: 1 GND / 2..5 BRAKE S0..S3 / 6 3V3", "PASSIVE GRAY CAMS: LEAVE 3V3 CAVITY EMPTY"]
    else:
        text(board,"NOTCHDECK BUTTONS / REV E",93,55,1)
        for row in range(4):
            for col in range(4):
                n=row*4+col+1
                name=f"BTN {n}" if n<=12 else ["UP","DOWN","LEFT","RIGHT"][n-13]
                text(board,name,64.5+col*19,77+row*19,.8)
        text(board,"J1 -> MAIN J15",93,160,.8)
        text(board,"PANEL SWD",66,161,.8)
        notes=["6-WAY 1mm FFC TYPE A - CONTACTS TOWARD PCB", "J1: 1 USB5V / 2 IRQ / 3 SCL / 4 SDA / 5 3V3 / 6 GND", "MAIN J15 PIN n -> THIS J1 PIN 7-n", "USB RGB ONLY - 250mA PANEL CURRENT TARGET", "STM32G030 / I2C 0x20 / SEPARATE FIRMWARE"]
    for i,value in enumerate(notes):
        text(board,value,50+width/2,(95 if is_main else 80)+i*4,.8,P.B_SilkS)
    for drawing in board.GetDrawings():
        if isinstance(drawing,P.PCB_TEXT) and drawing.GetLayer()==P.B_SilkS:drawing.SetMirrored(True)
    text(board,f"PROVISIONAL {width} x {height} mm / UNROUTED - DO NOT FABRICATE",50+width/2,54+height,1,P.Dwgs_User)
    board.BuildConnectivity()
    with tempfile.TemporaryDirectory(prefix="notchdeck-save-") as tmp:
        file=Path(tmp)/output.name;P.SaveBoard(str(file),board);shutil.copyfile(file,output)
    print(f"Saved {output}: {len(placed)} electrical footprints + 4 mounting holes, {len(nets)} nets")


if __name__=="__main__":main()
