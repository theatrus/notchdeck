#!/usr/bin/env python3
"""Generate Rev E intelligent 4x4 key/RGB board from this wiring manifest."""
from pathlib import Path
import json
import kschgen as K
from notchdeck_capture import Capture
HW=Path(__file__).resolve().parents[1]
PROJECT='notchdeck-buttons';DIR=HW/PROJECT
ROOT='605f75de-48c6-4dd7-a93a-325e780bcb70'
TITLE=dict(title='NotchDeck Buttons',date='2026-10-03',rev='E',company='BenchBits')
K.register_stdlib('Switch','SW_Push')
K.register_stdlib('LED','WS2812B')
K.register_stdlib('Device','C','R','D')
K.register_stdlib('Connector_Generic','Conn_01x06')
K.register_stdlib('power','+3V3','GND','PWR_FLAG')
K.register_stdlib('MCU_ST_STM32G0','STM32G030F6Px')
K.register_stdlib('74xGxx','74AHCT1G125')
K.register_stdlib('Power_Protection','USBLC6-2SC6')
K.register_lib('notchdeck',str(HW/'lib/symbols/notchdeck.kicad_sym'),'SWD_TC2030')
def C(ref,value,fp='Capacitor_SMD:C_0402_1005Metric'):return dict(ref=ref,lib_id='Device:C',value=value,fp=fp)
def R(ref,value):return dict(ref=ref,lib_id='Device:R',value=value,fp='Resistor_SMD:R_0402_1005Metric')
keys=[dict(ref=f'SW{i}',lib_id='Switch:SW_Push',value='SW_Push',fp='Button_Switch_SMD:SW_Push_1P1T_XKB_TS-1187A') for i in range(1,17)]
keys += [dict(ref=f'D{i}',lib_id='LED:WS2812B',value='WS2812B',fp='notchdeck:LED_XINGLIGHT_XL-5050RGBC-2812B') for i in range(1,17)]
keys += [dict(ref=f'D{i}',lib_id='Device:D',value='1N4148W',fp='Diode_SMD:D_SOD-123') for i in range(20,36)]
keys += [C(f'C{i}','100nF') for i in range(21,37)] + [C('C13','1uF','Capacitor_SMD:C_0805_2012Metric')]
logic=[
 dict(ref='U1',lib_id='MCU_ST_STM32G0:STM32G030F6Px',value='STM32G030F6P6TR',fp='Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm'),
 dict(ref='J1',lib_id='Connector_Generic:Conn_01x06',value='TO MAIN J15 / FFC',fp='Connector_FFC-FPC:JUSHUO_AFA07-S06FCA-00_1x6-1MP_P1.0mm_Horizontal'),
 dict(ref='J2',lib_id='notchdeck:SWD_TC2030',value='PANEL SWD',fp='Connector:Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical',in_bom=False),
 dict(ref='U2',lib_id='Power_Protection:USBLC6-2SC6',value='USBLC6-2SC6',fp='Package_TO_SOT_SMD:SOT-23-6'),
 dict(ref='U8',lib_id='74xGxx:74AHCT1G125',value='74AHCT1G125',fp='Package_TO_SOT_SMD:SOT-23-5'),
 C('C1','100nF'),C('C2','4.7uF','Capacitor_SMD:C_0805_2012Metric'),C('C3','100nF'),C('C4','100nF'),C('C5','100nF'),C('C20','100nF'),
 *[R(f'R{i}','10k') for i in range(1,6)],R('R6','100k'),R('R7','100k'),R('R11','330'),R('R26','100k'),
]
controller=dict(name='Controller',file='controller.kicad_sch',title='MCU, FFC and programming',page='2',big=[],small=logic)
array=dict(name='Buttons',file='buttons.kicad_sch',title='4x4 diode matrix and RGB',page='3',big=[],small=keys)
byref={p['ref']:p for p in logic+keys}
source=json.loads((DIR/'bom/jlcpcb-parts.json').read_text());assigned=set()
for code,p in source['parts'].items():
 for ref in p['references']:
  assert ref not in assigned
  c=byref[ref];assert c['fp']==p['footprint'],ref
  c.update(lcsc=code,mpn=p['mpn'],mfr=p['manufacturer'],datasheet=p['datasheet'])
  c['properties']={'JLCPCB Part Type':p['jlcpcb_category'],'BOM Checked':p.get('checked_at_utc',source['checked_at_utc'])[:10],'BOM Comments':p['bom_comments']}
  assigned.add(ref)
for ref,note in source['non_assembly'].items():byref[ref]['properties']={'BOM Comments':note}
assert assigned|set(source['non_assembly'])==set(byref)
PORTS=[f'ROW{i}' for i in range(4)]+[f'COL{i}' for i in range(4)]+['LED_DATA','USB_VBUS']
s=Capture(controller,str(DIR),ROOT,TITLE,PROJECT)
s.place('U1',66,32,ref_offset=(-33.02,-24.13),value_offset=(-33.02,-21.59))
# G030 TSSOP20 uses several internally bonded GPIOs: only selected functions
# drive those pads, with the other aliases left analog/high impedance.
pm={1:'SDA',3:'IRQ_N',4:'+3V3',5:'GND',6:'NRST',7:'ROW0',8:'ROW1',9:'ROW2',10:'ROW3',11:'COL0',12:'COL1',13:'COL2',14:'COL3',15:'RGB_PWM',17:'VBUS_SENSE',18:'SWDIO',19:'SWCLK',20:'SCL'}
for pin,net in pm.items():s.stub('U1',pin,net)
s.nc('U1',2,16)
s.place('J1',18,17,180,ref_offset=(-2.54,-12.7),value_offset=(-2.54,-10.16))
# Type A same-side contacts + identical bottom-contact connectors reverse numbering.
for pin,net in {1:'USB_VBUS',2:'IRQ_N',3:'SCL',4:'SDA',5:'+3V3',6:'GND'}.items():s.stub('J1',pin,net)
s.place('U2',26,43,ref_offset=(7.62,-12.7),value_offset=(7.62,-10.16))
for pin,net in {1:'SDA',6:'SDA',3:'SCL',4:'SCL',5:'+3V3',2:'GND'}.items():s.stub('U2',pin,net)
for ref,x in [('C1',91),('C2',100),('C5',109)]:
 s.place(ref,x,14);s.stub(ref,1,'+3V3',kind='power');s.stub(ref,2,'GND',kind='power')
s.place('R1',115,28);s.stub('R1',1,'+3V3',kind='power');s.stub('R1',2,'NRST')
s.place('C3',125,31);s.stub('C3',1,'NRST');s.stub('C3',2,'GND',kind='power')
for i in range(4):
 ref=f'R{i+2}';s.place(ref,90+12*i,43);s.stub(ref,1,'+3V3',kind='power');s.stub(ref,2,f'COL{i}')
s.place('J2',25,80,ref_offset=(-7.62,-15.24),value_offset=(-7.62,-12.7))
for pin,net in {1:'+3V3',2:'SWDIO',3:'NRST',4:'SWCLK',5:'GND'}.items():s.stub('J2',pin,net)
s.nc('J2',6)
s.place('R6',51,73);s.place('R7',51,83);s.join(('R6',2),('R7',1))
s.stub('R6',1,'USB_VBUS');s.stub('R7',2,'GND',kind='power')
s.place('C4',63,83)
s.wire((51*2.54,78*2.54),(63*2.54,78*2.54),s.pin('C4',1))
s.label('VBUS_SENSE',(55*2.54,78*2.54));s.stub('C4',2,'GND',kind='power')
s.place('U8',91,75,ref_offset=(15.24,-17.78),value_offset=(15.24,-15.24))
for pin,net in {1:'GND',3:'GND',5:'USB_VBUS',2:'RGB_PWM'}.items():s.stub('U8',pin,net)
s.place('R26',74,89);s.stub('R26',1,'RGB_PWM');s.stub('R26',2,'GND',kind='power')
s.place('R11',107,75,90,ref_offset=(-2.54,-5.08),value_offset=(-2.54,-2.54));s.join(('U8',4),('R11',1));s.stub('R11',2,'LED_DATA')
s.place('C20',119,79);s.stub('C20',1,'USB_VBUS');s.stub('C20',2,'GND',kind='power')
for i,net in enumerate(PORTS):s.port(net,139,12+i*5)
for i,net in enumerate(['+3V3','GND','USB_VBUS']):
 p=((20+15*i)*2.54,103*2.54);q=(p[0]+5*2.54,p[1]);s.power(net,p);s.wire(p,q);s.power(net,q,flag=True)
s.note(8,57,'U1: owned STM32G030F6P6TR. HSI/PLL; no crystal. I2C1 target 0x20 on PB6/PB7 AF6.\nROW0..3 = PA0..3; COL0..3 = PA4..7; RGB = PA8 TIM1_CH1 AF2; IRQ = PC15 open drain.\nLeave bonded PB8, PB3/4/5, PB0/1/2, PA10 and PA15 analog. SWD PA13/14; boot from flash.\nVBUS_SENSE = PA12 ADC_IN16: half VBUS. Default RGB low/off; enable only with USB.')
s.note(70,96,'FFC Type A, 1mm, 0.30mm end thickness; Molex 0151670213.\nButton pinout is reversed vs main: 1 USB5V / 2 IRQ / 3 SCL / 4 SDA / 5 3V3 / 6 GND.\nDo not add I2C pull-ups here. Main R9/R10=4.7k; 100kHz, 177.8mm cable.\nSeparate panel firmware + SWD fixture required; no panel USB bootloader.')
s.finish()
s=Capture(array,str(DIR),ROOT,TITLE,PROJECT)
G=2.54
# Visible rows and columns with one isolation diode per switch, no ghost keys.
for row in range(4):
 y=15+row*13;rowpoints=[]
 for col in range(4):
  x=24+col*31;i=row*4+col+1
  sw,diode=f'SW{i}',f'D{19+i}'
  s.place(sw,x,y,ref_offset=(-2.54,-6.35),value_offset=(-2.54,-3.81),hide_value=True)
  s.place(diode,x-7,y,ref_offset=(-2.54,-6.35),value_offset=(-2.54,-3.81),hide_value=True)
  s.join((diode,2),(sw,1))
  p=s.pin(diode,1);q=(p[0],(y+5)*G);s.wire(p,q);rowpoints.append(q)
  p=s.pin(sw,2);q=((x+5)*G,p[1]);s.wire(p,q)
  if row:s.wire(((x+5)*G,15*G),q)
  else:s.label(f'COL{col}',q)
 for a,b in zip(rowpoints,rowpoints[1:]):s.wire(a,b)
 s.label(f'ROW{row}',rowpoints[0])
s.note(12,66,'Scan one row LOW, leave other rows high impedance; columns have 10k pull-ups on Controller.\nEach diode cathode points toward its row. SW1..12 map to BTN1..12; SW13..16 to hat U/D/L/R.')
for row in range(2):
 y=76+16*row
 for col in range(8):
  i=row*8+col+1;x=12+16*col
  s.place(f'D{i}',x,y,ref_offset=(-3.81,-6.35),value_offset=(-3.81,6.35),hide_value=True)
  s.place(f'C{20+i}',x+5,y-2.5,ref_offset=(1.27,-2.54),value_offset=(1.27,2.54))
  if col:s.join((f'D{i-1}',2),(f'D{i}',4))
 s.rail('USB_VBUS',[(f'D{row*8+i}',1) for i in range(1,9)]+[(f'C{20+row*8+i}',1) for i in range(1,9)],y-5)
 s.rail('GND',[(f'D{row*8+i}',3) for i in range(1,9)]+[(f'C{20+row*8+i}',2) for i in range(1,9)],y+5)
s.stub('D1',4,'LED_DATA');s.stub('D8',2,'LED_ROW2',length=8);s.stub('D9',4,'LED_ROW2');s.nc('D16',2)
s.place('C13',144,89);s.stub('C13',1,'USB_VBUS');s.stub('C13',2,'GND',kind='power')
for i,net in enumerate(PORTS):s.port(net,138,12+i*4)
s.note(135,60,'RGB: USB only.\nDefault OFF.\nFirmware limits current;\n250mA panel target.\nReview USB + charger\npower budget before fab.')
s.finish()
blocks='';wiring=''
for sh,x,side in [(controller,20,0),(array,100,180)]:
 pins=[(net,'bidirectional',(x+45 if side==0 else x)*G,(30+i*4)*G,side) for i,net in enumerate(PORTS)]
 blocks+=K.w_sheet(sh['name'],sh['file'],sh['uuid'],x*G,24*G,45*G,49*G,pins,project=PROJECT,parent_path=f'/{ROOT}',page=sh['page'])
for i,net in enumerate(PORTS):wiring+=K.w_wire(65*G,(30+i*4)*G,100*G,(30+i*4)*G)+K.w_label(net,78*G,(30+i*4)*G)
wiring+=K.text_note('NOTCHDECK BUTTON BOARD / REV E\nSTM32G030 scans a diode-isolated 4x4 matrix and drives 16 RGB LEDs.\nFFC J1 connects to main J15; this project has its own BOM, CPL and PCB.\nProvisional floorplan: do not fabricate before routing and firmware validation.',20*G,12*G)
K.write_root(PROJECT,str(DIR),ROOT,TITLE,blocks,wiring,[[s['uuid'],s['name']] for s in (controller,array)],paper='A3')
