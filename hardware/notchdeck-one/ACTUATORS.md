# Rev F solenoids, buzzer and battery protection

The sixth schematic sheet adds two battery-voltage solenoid outputs, an active
buzzer output and three 3.3V control signals for an external driver. These are
captured and floorplanned, **not routed or bench-qualified**. Actuator firmware
is not implemented. Do not connect loads while running the old Rev C/D image:
it assigns these GPIOs to other functions.

## Battery and short-circuit protection

Use a **protected 1S Li-ion pack**, with documented overcharge, overdischarge,
overcurrent and short-circuit cutoff. Connect its protected terminals to J2
(1 positive, 2 ground). The protection must be at the cell, before the cable.
An unprotected bare cell is not an approved power source. Select a pack rated
for the 500mA charger and at least 2A discharge, then qualify its cutoff and
recovery behavior with the finished controller. No particular pack is selected.

`BAT_RAW` is the PCB input **after the external pack protection**. It feeds the
charger, fuel gauge and existing logic power path. A separate branch is:

```text
protected pack → J2 / BAT_RAW → U13 electronic limiter → ACT_BAT → loads
                                                         load− → Q2/Q3/Q4 → GND
```

U13 is **TPS259531DSGR / C2155674**, not a one-time fuse. R56+R58 = 1.33kΩ
sets a nominal limit of `2000/1330 + 0.04 = 1.544A`. Allow approximately
1.41–1.68A including the IC's ±7.5% limit accuracy and 1% resistor tolerance;
this is a design estimate, not a measured trip band. Use **1.3A total operating
budget** for the bank and **1A maximum provisional target per solenoid**.

For a hard short, U13 quickly limits current (datasheet typical response 5µs),
then thermally shuts down if the overload persists. **This variant retries
automatically** after cooling. `ACT_nFAULT` asserts on thermal shutdown; it is
not an immediate overcurrent interrupt. Firmware must drop `ACT_EN` and latch
the bank off until an explicit user reset after a fault. The limiter protects
the actuator branch, including a positive harness wire shorted directly to
ground; the individual low-side FET cannot protect that particular fault.
The external pack protects shorts in the battery leads and upstream PCB nets.
Neither the MCP73832 charger nor the MAX17048 gauge provides pack protection.

R53 defaults the bank off during reset. Owned **2N7002 / C8545** parts Q5/Q6
interlock the charger: ACT_EN high turns Q5 on, pulling CHARGE_ENABLE low;
Q6 then opens R3's return to ground. The MCP73832 disables charging when PROG
floats. R59=100k pulls Q6's gate up for normal charging when actuation is off.
This prevents actuator loading from disturbing charge termination and permits
battery-powered actuation with USB connected. USB continues powering logic.
Use ACT_EN for the whole actuation session, not as the PWM signal.

Q6 carries only the PROG current (nominally 0.5mA). Its resistance adds to R3
and can reduce charge current; characterize charge current at minimum 3V3 and
temperature, and confirm off-state leakage leaves PROG above the datasheet's
200kΩ shutdown impedance. This is a new charge-control path requiring bench
validation, not a complete replacement battery-management system.

C47 is local 1µF input bypass; C48=100nF sets roughly 10ms rise at 4.2V. C45/C46
provide 44µF nominal output bulk (effective capacitance is lower under bias).
D23 clamps negative OUT excursions. The output capacitors can still deliver
a brief discharge into a short. Keep the battery harness short (≤10cm target),
measure input overshoot/output undershoot during short tests, and add damping
or a correctly rated clamp if measurements require it. This is not reverse
battery protection; key and polarity-check the battery harness.

## Ports and GPIOs

| Port | Pins | Intended load |
|---|---|---|
| J16 | 1 ACT_BAT, 2 SOL1_LOW | 1S solenoid 1, ≤1A target |
| J17 | 1 ACT_BAT, 2 SOL2_LOW | 1S solenoid 2, ≤1A target |
| J18 | 1 ACT_BAT, 2 BUZZ_LOW | External **active** buzzer rated across the usable 1S range; ≤100mA target |
| J19 | 1 GND, 2 SOL1_PWM_EXT, 3 SOL2_PWM_EXT, 4 BUZZ_PWM_EXT | High-impedance 3.3V inputs on an external driver |

J16–18 use the same JST PH two-pin footprint/part as J2 (C295747). J19 is the
JST PH four-pin C265102. Battery and load plugs must be clearly labelled or
mechanically distinguished in the product; do not accidentally interchange them.

| E73 pad | nRF GPIO | Signal | Circuit |
|---|---|---|---|
| 32 | P0.20 | SOL1_PWM | R43 330Ω → Q2 IN, R46 100kΩ to ground |
| 33 | P0.13 | SOL2_PWM | R44 330Ω → Q3 IN, R47 100kΩ to ground |
| 34 | P0.22 | BUZZ_PWM | R45 330Ω → Q4 IN, R48 100kΩ to ground |
| 35 | P0.24 | ACT_EN | R52 1kΩ → U13 EN; R53 100kΩ to ground; Q5/Q6 charge inhibit |
| 36 | P1.00 | ACT_nFAULT | U13 open-drain FLT; R57 10kΩ pull-up to 3V3 |

J19 signals branch off the MCU side through R49–51 (1kΩ each). They follow the
same commands as the onboard outputs and are **not gated by U13**. A 12V
booster/driver must supply its own current limit, flyback, default-off bias and
fault response. Use a common ground and high-impedance inputs, with no 5V/12V
pull-ups; never apply 12V to J16–18 or J19. These are short internal harnesses,
not qualified external hot-plug ports.

## Drivers and strike/hold behavior

Q2–4 use owned **ZXMS6005DGTA / C174045**, a protected low-side IntelliFET:
pin 1 IN, pin 2 and tab D, pin 3 S. They have current limiting and thermal
protection, but their internal limit is not a precision coil-current setting.
D20–22 are **B360A / C6807778**, cathode at ACT_BAT and anode at the switched
load return, providing local flyback paths.

Start with **500Hz PWM** for the solenoids. This is a qualification target,
not a measured result: this FET's switching delays make 20kHz operation a poor
default. The buzzer has its own oscillator and uses on/off control. Passive
audio transducers would need a different driver/timing review.

Required firmware sequence: initialize every output low; establish a valid
load profile and healthy battery; enable the bank; wait for its supply ramp;
apply a bounded full-duty strike, then the calibrated hold duty. Stagger strikes
and phase the hold channels so **instantaneous** bank demand remains within
1.3A, including the buzzer. Two simultaneous 1A strikes are outside this budget.
Duty control is open-loop: coil current varies with resistance, inductance,
temperature and battery voltage. There is no per-coil current sensor.

Enforce maximum strike duration, maximum on-time, communication timeout,
watchdog/reset shutdown, charger interlock, fault latch and undervoltage shutdown.
Use a provisional 3.6V loaded-battery actuation cutoff and confirm the FET input
actually stays ≥3.0V at temperature and load. Program suitable nRF GPIO drive
strength: logic VOH, resistor drop and FET input current must all fit that
margin. The 3.6V threshold is a starting point for bench calibration, not the
pack's deep-discharge cutoff. Keep actuation disabled until profiles and these
checks exist. Simple flyback slows release; measure whether that suits the
handle mechanism before finalizing the clamp scheme.

## Placement and validation evidence

The floorplan preserves Rev E placements and adds connectors at the right/top
edges, driver clusters near their connectors and U13 near the battery area.
Route the actuator rail/returns for the fault limit, with short flyback loops
and wide copper. The provisional Actuator net class uses 1mm tracks; this is
not a current-capacity certification. Return load current directly toward the
battery ground, away from sensor/radio ground paths; use an uninterrupted
reference plane. Give U13 its exposed-pad ground copper and thermal vias.
Q2/Q3 need suitable drain-tab copper: the FET's published 1.4A at 3V/25°C
rating assumes 15×15mm of 1oz copper and decreases with ambient temperature.

On 2026-10-04, KiCad 10.0.6 reports **zero ERC errors/warnings**, and the
independent contract covers **128 components, 91 nets and 402 endpoints**,
including 20 explicit no-connects. PCB pads/UUIDs/BOM agree with the schematic;
native DRC reports **zero rule/parity issues, 319 unrouted connections**.
These are **consistency checks**, not measured protection performance.

Manufacturer checks: U13 pin functions/variant and EP dimensions were compared
with TI's datasheet; Q2–4 pinout/input limits were compared with Diodes' drawing;
Q5/Q6's 1=G, 2=S, 3=D mapping with the selected JSCJ datasheet. The standard U13
footprint has the matching 0.5mm pitch and 0.9×1.6mm EP; its peripheral lands
are longer than TI's example. Final paste/thermal-via and assembly review remain.

The schematic/PCB analyzers and EMC screen were run. Missing planes/stitching,
USB bypass placement and unqualified harness filtering remain layout work.
The schematic analyzer's “missing flyback” heuristic does not recognize this
rail: the independent contract and rendered sheet show D20–22 across each
connector. No SPICE simulator is installed; coil R/L and actual loads are also
unspecified. This change check is not a full thermal, lifecycle or fabrication
review. Bench-test startup and running shorts at battery extremes, USB insertion and charge interlock,
fault/retry/reset behavior, temperature rise, coil release and radiated noise
before connecting the final mechanisms.

Sources: [Microchip MCP73831/2, sections 3.5 and 4.3 (floating PROG shutdown)](https://ww1.microchip.com/downloads/en/DeviceDoc/20001984g.pdf),
[TI TPS2595 datasheet, sections 8.3 and 9](https://www.ti.com/lit/ds/symlink/tps2595.pdf),
[Diodes ZXMS6005DG datasheet](https://www.diodes.com/datasheet/download/ZXMS6005DG.pdf),
[selected JSCJ 2N7002 datasheet](https://datasheet.lcsc.com/datasheet/pdf/a141b8bd86b14475955ac8c4d3eea0a8.pdf?productCode=C8545).
Cached PDFs and their provenance live in `hardware/datasheets/` (PDFs ignored by Git).
