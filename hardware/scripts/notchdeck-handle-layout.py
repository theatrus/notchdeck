#!/usr/bin/env python3
"""Render the adjustable panel study and export cam targets from firmware codes.

These are mechanical target angles, never AS5600 calibration constants. The SVG
is an envelope/wiring study, not a cutting file. Run from any working directory.
"""
from pathlib import Path
import csv
import html
import json
import math
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/mechanical'
cfg = json.loads((OUT / 'handle-layout.json').read_text())
firmware = (ROOT / 'firmware/src/handle_decode.c').read_text()
rows = []
for role, spec in cfg['detents'].items():
    match = re.search(rf'{role}_codes\[\] = \{{([^}}]+)\}}', firmware)
    codes = [int(x) for x in match[1].split(',')]
    bits = 3 if role == 'power' else 4
    assert len(codes) == len(spec['labels']) == len(spec['angles_deg'])
    assert (1 << bits) - 1 not in codes and len(set(codes)) == len(codes)
    assert all((a ^ b).bit_count() == 1 for a, b in zip(codes, codes[1:]))
    assert all(a < b for a, b in zip(spec['angles_deg'], spec['angles_deg'][1:]))
    for name, angle, code in zip(spec['labels'], spec['angles_deg'], codes):
        closed = [i for i in range(bits) if not code & (1 << i)]
        rows.append(dict(handle=role, position=name, provisional_angle_deg=angle,
                         levels_msb_first=f'{code:0{bits}b}',
                         switches_closed_to_ground=' '.join(f'S{i}' for i in closed),
                         header='J12' if role == 'power' else 'J5',
                         header_pins_connected_to_pin1=' '.join(str(i+2) for i in closed)))
with (OUT / 'detents-and-cams.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, rows[0].keys(), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)

s = ['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="1030" viewBox="0 0 1280 1030">',
     '<style>text{font-family:Arial,sans-serif;fill:#18303c}.small{font-size:13px}.label{font-size:17px;font-weight:bold}.title{font-size:25px;font-weight:bold}.sub{font-size:16px}.board{fill:#d7eadf;stroke:#51836a;stroke-width:1.5}.module{fill:#e6edf8;stroke:#5c77a1;stroke-width:1.5}.wire{fill:none;stroke:#378b87;stroke-width:2;stroke-dasharray:6 4}</style>',
     '<rect width="1280" height="1030" fill="#f8f7f3"/>']
def text(x, y, value, cls='small', anchor='start'):
    s.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}">{html.escape(value)}</text>')
def rect(x,y,w,h,cls,rx=0):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{cls}"/>')
def line(x1,y1,x2,y2,stroke='#18303c',width=1):
    s.append(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{stroke}" stroke-width="{width}"/>')
text(45,42,'NotchDeck One · Rev D handle integration','title')
text(45,69,'Own-build Japanese-style controls · one PCB · magnetic or Gray contacts on either handle','sub')
text(45,94,'Provisional 400 × 220 mm panel. Top view, driver at the bottom. Envelopes only; no cutout dimensions.','small')
for panel_y, mode in [(140,'dual'),(580,'combined')]:
    text(45,panel_y-12,'Separate power + rotary brake' if mode=='dual' else 'Combined mascon alternative','label')
    ox,oy,scale=45,panel_y,1.7
    W,D=cfg['panel']['width'],cfg['panel']['depth']
    s.append(f'<rect x="{ox}" y="{oy}" width="{W*scale}" height="{D*scale}" rx="14" fill="#fff" stroke="#a1a8a8" stroke-width="2"/>')
    def xy(x,y):return ox+x*scale,oy+y*scale
    pcb=cfg['pcb'];bx,by=xy(pcb['x'],pcb['y'])
    rect(bx,by,pcb['width']*scale,pcb['depth']*scale,'board')
    text(bx+9,by+42,'MAIN PCB','small')
    text(bx+9,by+61,'145 × 105','small')
    # Derived from the actual Rev D PCB placements, relative to its (50,50) corner.
    for row in range(4):
        for col in range(4):
            px,py=xy(pcb['x']+72+19*col,pcb['y']+34+19*row)
            rect(px-6,py-6,12,12,'module',2)
    for hx,hy in [(5,5),(140,5),(140,100),(5,100)]:
        px,py=xy(pcb['x']+hx,pcb['y']+hy)
        s.append(f'<circle cx="{px}" cy="{py}" r="3" fill="#fff" stroke="#51836a"/>')
    for label,px,py in [('J10 MAG P',83,5.8),('J11 MAG B',108,5.8),('J12 GRAY P',5.8,65),('J5 GRAY B/M',139.2,64)]:
        x,y=xy(pcb['x']+px,pcb['y']+py)
        s.append(f'<circle cx="{x}" cy="{y}" r="3.5" fill="#207f78"/>')
        # Port labels live outside the populated switch grid.
        if label.startswith('J10') or label.startswith('J11'):text(x,by-6,label.split()[0],'small','middle')
        elif label.startswith('J12'):text(bx-8,y-8,'J12','small','end')
        elif label.startswith('J5'):text(bx+pcb['width']*scale+8,y-8,'J5','small')
    m=cfg['power_module' if mode=='dual' else 'combined_module'];cx,cy=xy(m['x'],m['y'])
    rect(cx-m['width']*scale/2,cy-m['depth']*scale/2,m['width']*scale,m['depth']*scale,'module',10)
    line(cx,cy-52,cx,cy+52,'#5c77a1',7)
    rect(cx-24,cy+5,48,16,'module',5)
    text(cx,cy-65,'POWER' if mode=='dual' else 'MASCON','label','middle')
    text(cx,cy+76,'Off → P5' if mode=='dual' else 'EB ← N → P5','small','middle')
    # Dashed paths indicate optional alternatives, not physical cable lengths.
    x0,y0=xy(pcb['x']+83,pcb['y']+5.8)
    s.append(f'<path d="M{x0},{y0} L{bx-16},{y0} L{cx},{cy-45}" class="wire"/>')
    gx,gy=xy(pcb['x']+(5.8 if mode=='dual' else 139.2),pcb['y']+(65 if mode=='dual' else 64))
    s.append(f'<path d="M{gx},{gy} L{gx},{oy+132*scale} L{cx+30},{cy-30}" class="wire"/>')
    if mode=='dual':
        m=cfg['brake_module'];cx,cy=xy(m['x'],m['y']);rad=m['radius']*scale
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" class="module"/>')
        for a in cfg['detents']['brake']['angles_deg']:
            th=math.radians(a-150)
            line(cx+(rad-10)*math.cos(th),cy+(rad-10)*math.sin(th),cx+(rad-2)*math.cos(th),cy+(rad-2)*math.sin(th),'#5c77a1',2)
        line(cx,cy,cx+48,cy-28,'#5c77a1',8)
        text(cx,cy+35,'BRAKE','label','middle');text(cx,cy+56,'Release → B8 → EB','small','middle')
        x0,y0=xy(pcb['x']+108,pcb['y']+5.8)
        s.append(f'<path d="M{x0},{y0} L{cx},{y0} L{cx},{cy-rad}" class="wire"/>')
        gx,gy=xy(pcb['x']+139.2,pcb['y']+64)
        s.append(f'<path d="M{gx},{gy} L{cx-30},{cy-rad+5}" class="wire"/>')
    else:
        text(*xy(330,143),'Brake station blank','small','middle')
        text(*xy(330,157),'J11 / J12 unused','small','middle')
    text(ox+W*scale/2,oy+D*scale-10,'DRIVER','small','middle')
    tx=775;ty=panel_y+30
    notes=(['POWER · 6 detents','Off, P1–P5','Magnetic J10 / Gray J12','','BRAKE · 10 detents','Release, B1–B8, emergency','Magnetic J11 / Gray J5','','Independent sensors; mixed types allowed.','Brake suppresses traction in firmware.'] if mode=='dual' else ['MASCON · 15 detents','EB, B8–B1, N, P1–P5','Magnetic J10 / Gray J5','','Use one selected sensor backend per handle.','Remove R37 + R38 for external J10 sensor.','Magnetic centers must be measured.','','Chassis carries handle and stop loads.','PCB and sensors carry no shaft load.'])
    for i,note in enumerate(notes):text(tx,ty+i*29,note,'label' if i in (0,4) and mode=='dual' or i==0 else 'sub')
text(45,1000,'Dashed lines show interface choices, not routed harnesses. Verify cable length, hand clearance and under-panel depth on a mock-up.','small')
s.append('</svg>')
(OUT/'handle-layout.svg').write_text('\n'.join(s)+'\n')
print(f'Wrote panel study and {len(rows)} detent targets; cam codes match firmware and exclude all-open.')
