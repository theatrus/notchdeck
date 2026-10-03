#!/usr/bin/env python3
"""Independent complete panel net contract, strict ERC and FFC pin-order audit."""
from pathlib import Path
import os, json, subprocess, tempfile, xml.etree.ElementTree as ET
HW=Path(__file__).resolve().parents[1]
CLI=os.environ.get('KICAD_CLI','kicad-cli')
def export(project,path):
 subprocess.run([CLI,'sch','export','netlist','--format','kicadxml','-o',str(path),str(HW/project/(project+'.kicad_sch'))],check=True)
 return ET.parse(path)
def nets(doc):
 actual={};pins={}
 for n in doc.findall('./nets/net'):
  values={f"{p.get('ref')}.{p.get('pin')}" for p in n.findall('node')}
  assert not values & pins.keys()
  actual[n.get('name')]=values
  pins.update({v:n.get('name') for v in values})
 return actual,pins
with tempfile.TemporaryDirectory(prefix='notchdeck-panelcheck-') as tmp:
 tmp=Path(tmp);doc=export('notchdeck-buttons',tmp/'panel.xml');actual,pins=nets(doc);expected={}
 def net(name,values):expected[name]=set(values.split()) if isinstance(values,str) else set(values)
 net('+3V3','C1.1 C2.1 C5.1 U1.4 U2.5 J1.5 J2.1 R1.1 R2.1 R3.1 R4.1 R5.1')
 net('GND',set('C1.2 C2.2 C3.2 C4.2 C5.2 C13.2 C20.2 U1.5 U2.2 U8.1 U8.3 R7.2 R26.2 J1.6 J2.5'.split())|{f'C{i}.2' for i in range(21,37)}|{f'D{i}.3' for i in range(1,17)})
 net('/USB_VBUS',set('J1.1 C13.1 C20.1 U8.5 R6.1'.split())|{f'C{i}.1' for i in range(21,37)}|{f'D{i}.1' for i in range(1,17)})
 for name,values in {
  '/Controller/SDA':'J1.4 U1.1 U2.1 U2.6',
  '/Controller/SCL':'J1.3 U1.20 U2.3 U2.4',
  '/Controller/IRQ_N':'J1.2 U1.3',
  '/Controller/NRST':'U1.6 R1.2 C3.1 J2.3',
  '/Controller/SWDIO':'U1.18 J2.2',
  '/Controller/SWCLK':'U1.19 J2.4',
  '/Controller/RGB_PWM':'U1.15 R26.1 U8.2',
  '/Controller/VBUS_SENSE':'U1.17 C4.1 R6.2 R7.1',
  '/LED_DATA':'D1.4 R11.2',
  '/Buttons/LED_ROW2':'D8.2 D9.4',
 }.items():net(name,values)
 for i in range(4):
  net(f'/ROW{i}',{f'U1.{7+i}'}|{f'D{20+4*i+j}.1' for j in range(4)})
  net(f'/COL{i}',{f'U1.{11+i}',f'R{2+i}.2'}|{f'SW{1+4*j+i}.2' for j in range(4)})
 internals=[f'D{19+i}.2 SW{i}.1' for i in range(1,17)]+['U8.4 R11.1']+[f'D{i}.2 D{i+1}.4' for i in range(1,16) if i!=8]
 for values in internals:net(pins[values.split()[0]],values)
 for pin in ['D16.2','U1.2','U1.16','J2.6']:
  assert pins[pin].startswith('unconnected-');net(pins[pin],{pin})
 assert actual.keys()==expected.keys(),actual.keys()^expected.keys()
 for name,values in expected.items():assert values==actual[name],(name,values^actual[name])
 comps={c.get('ref'):c for c in doc.findall('./components/comp')};assert len(comps)==85
 for ref,value in {'U1':'STM32G030F6P6TR','R1':'10k','R2':'10k','R3':'10k','R4':'10k','R5':'10k','R6':'100k','R7':'100k','R11':'330','R26':'100k','C2':'4.7uF','U8':'74AHCT1G125',**{f'D{i}':'1N4148W' for i in range(20,36)}}.items():assert comps[ref].findtext('value')==value
 main,mainpins=nets(export('notchdeck-one',tmp/'main.xml'))
 # The same-side Type A cable between two identical bottom-contact connectors
 # maps n -> 7-n. Check signals AND both rails; catching a reversal here is vital.
 pairs={1:('GND','GND'),2:('+3V3','+3V3'),3:('/I2C0_SDA','/Controller/SDA'),4:('/I2C0_SCL','/Controller/SCL'),5:('/PANEL_INT','/Controller/IRQ_N'),6:('/USB_VBUS','/USB_VBUS')}
 for pin,(a,b) in pairs.items():
  assert mainpins[f'J15.{pin}']==a and pins[f'J1.{7-pin}']==b,(pin,a,b)
 project=HW/'notchdeck-buttons/notchdeck-buttons.kicad_pro';assert not json.loads(project.read_text()).get('erc',{}).get('erc_exclusions')
 subprocess.run([CLI,'sch','erc','--format','json','--exit-code-violations','-o',str(tmp/'erc.json'),str(project.with_suffix('.kicad_sch'))],check=True)
 erc=json.loads((tmp/'erc.json').read_text());assert not [v for s in erc['sheets'] for v in s['violations']]
 print(f'PASS: {len(comps)} panel components, {len(actual)} nets, {len(pins)} endpoints; zero ERC; all 6 FFC conductors match Type A reversal')
