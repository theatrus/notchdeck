# Battery protection and impulse outputs — Rev G

Two solenoid outputs target **2A strikes per channel, simultaneously**, followed
by a calibrated lower PWM hold current. This is a schematic and unrouted
floorplan, not a qualified 2A driver or working actuator firmware. No coils,
buzzer or battery pack have been selected. Keep loads disconnected until the
firmware and bench qualification below are complete.

## Full battery input protection

```text
protected 1S pack → J2 / BAT_RAW → U13 → BAT_PROT → Q1 / logic supply
                                          ├────→ fuel gauge
                                          └────→ J16/J17/J18 → loads → Q2/Q3/Q4 → GND
USB → MCP73832 charger ─────────────────────────→ BAT_PROT
                           charging returns through U13 to the battery
BAT_PROT → D24 (anode to cathode) → BAT_RAW: charge recovery while U13 is off
```

U13 is **TPS259461LRPWR / C3662776**, a bidirectional eFuse with a latched
thermal shutdown. **Every battery-fed functional branch is downstream of it**,
including logic, gauge and actuators. Only the input bypass C47, enable divider
and D24 cathode connect to BAT_RAW. D24 is reverse-biased during battery
discharge, so it cannot bypass the battery short protection. No disposable fuse
is fitted. USB VBUS is a separate source and is not protected by U13.

R56+R58 = **330Ω+330Ω = 660Ω** sets `3334/660 = 5.05A` nominal forward
current limit. The estimated range is **4.50–5.61A**, using ±10% IC accuracy and
1% resistors. Normal battery input demand must stay **≤4.3A**: two 2A strikes,
100mA buzzer and 200mA logic/panel/sensor allowance. This is a budget to measure,
not an instantaneous hard ceiling. U13's continuous operating rating is 5.5A;
its fast short threshold is about twice the set limit and brief overshoot is
possible before limiting. Leave ITIMER open for the fastest overcurrent response.

A severe short first triggers fast turn-off, followed by a current-limited
attempt after approximately 30µs. A persistent fault heats the eFuse until it
**latches off thermally**; it does not latch immediately at 5.05A. FLT asserts
for persistent forward overcurrent and thermal faults. Remove the fault, then
disconnect **both battery and USB** to reset the latch. There is no automatic
MCU power-cycling path. R52/R53 bias EN from the raw battery independently of
the MCU, avoiding a startup deadlock. OVLO is grounded; this circuit does not
provide reverse-battery protection or a separate adjustable overvoltage cutoff.

Use a **protected 1S pack rated for at least 6A discharge**, with a protection
cutoff and harness compatible with this load. Pack protection remains essential
for shorts in its leads, J2 and the short raw-input section before U13. Neither
the MCP73832 charger nor MAX17048 gauge supplies cell protection. Require a
usable protected-pack output ≥2.7V; actuator operation has a higher provisional
loaded-battery cutoff of 3.6V.

C47 is 1µF input bypass. C48=100nF with R60=100Ω follows TI's recommendation
for a DVDT capacitor above 10nF; nominal rise time is **210ms at 4.2V**. C45/C46
provide 44µF nominal bulk, reduced by voltage bias. D23 clamps negative output
excursions. The output capacitors can still discharge briefly into a short.
Keep battery leads short (≤10cm target) and qualify input overshoot and output
undershoot with the actual pack and harness.

## Charging and control

The eFuse conducts in both directions when enabled; its overcurrent protection
acts only from IN to OUT. MCP73832 limits charging current nominally to 500mA.
D24, a B360A Schottky, permits limited charging of a depleted/disabled pack until
U13 can turn on. It also means USB can back-power BAT_RAW while the eFuse is off.
Do not treat a latched eFuse as full electrical isolation with USB attached.

**ACT_EN now inhibits charging only. It does not switch U13 or remove voltage
from the actuator connectors.** Q5 pulls CHARGE_ENABLE low, Q6 opens the charger
PROG resistor return, and charging pauses. With ACT_EN low, R59 biases Q6 on
for normal charging. R46–48 hold the individual driver inputs off during reset.
Use ACT_EN for an entire actuation session, not as PWM. Check PROG leakage and
the actual charge current through Q6 on the bench.

Firmware must initialize PWM low, validate the battery and load profile, assert
ACT_EN, allow charging to stop, then permit strikes/hold. On BAT_nFAULT, stop all
PWM and **keep ACT_EN high to inhibit USB charging into the fault**; require an
explicit user reset. On battery-only faults the MCU may lose power, so firmware
cannot replace U13's hardware limiting/latch behavior. J19 follows raw MCU PWM.

The charger and MAX17048 connect to BAT_PROT. The eFuse drop slightly reduces
actual cell charging voltage and biases loaded gauge voltage; take rested
readings for calibration rather than interpreting a strike sag as cell SOC.

## Ports and GPIOs

| Port | Pins | Intended load |
|---|---|---|
| J2 | **1+2 BAT_RAW, 3+4 GND** | Owned Molex **430450401 / C585880** Micro-Fit 3.0, both contacts wired per polarity |
| J16 | 1 BAT_PROT, 2 SOL1_LOW | 1S solenoid 1, 2A strike target |
| J17 | 1 BAT_PROT, 2 SOL2_LOW | 1S solenoid 2, 2A strike target |
| J18 | 1 BAT_PROT, 2 BUZZ_LOW | 1S-rated active buzzer, ≤100mA |
| J19 | 1 GND, 2 SOL1_PWM_EXT, 3 SOL2_PWM_EXT, 4 BUZZ_PWM_EXT | High-impedance 3.3V inputs for a separate driver |

J2 uses the standard 43045-0400 footprint, compatible with the selected -0401
contact finish. Use the matching 43025-series four-circuit receptacle and
appropriate 20AWG crimp contacts; fit both positive and both return wires.
Mating parts remain a harness sourcing item. J16–18 remain JST PH C295747;
2A is the PH contact rating with 24AWG wire, so do not exceed it. J19 is JST PH
C265102. The larger battery connector prevents confusing it with a load port.

| E73 pad / GPIO | Signal | Circuit |
|---|---|---|
| 32 / P0.20 | SOL1_PWM | R43 330Ω → Q2 IN; R46 100kΩ to ground |
| 33 / P0.13 | SOL2_PWM | R44 330Ω → Q3 IN; R47 100kΩ to ground |
| 34 / P0.22 | BUZZ_PWM | R45 330Ω → Q4 IN; R48 100kΩ to ground |
| 35 / P0.24 | ACT_EN | R54 → Q5/Q6 charger inhibit; no connection to U13 EN |
| 36 / P1.00 | BAT_nFAULT | U13 FLT4, open drain; R57 10kΩ pull-up to 3V3 |

J19 branches through R49–51, 1kΩ each. A 12V booster/driver needs its own
supply protection, current control, flyback and default-off inputs. Use common
ground; no 5V/12V pull-ups or 12V on J16–19. These are short internal harnesses,
not qualified hot-plug ports.

## Provisional strike and hold profile

Q2–4 remain owned **ZXMS6005DGTA / C174045**: IN1, drain2/tab, source3. The
3V-input specification includes a 2.2A minimum internal limiting threshold and
250mΩ maximum RDS(on) at 1A/25°C. Its published 5A pulsed absolute maximum at
3.3V is not a continuous rating. A 2A pulse suggests approximately 1W conduction
loss using 250mΩ; resistance increases with temperature and the 1A test point
is not a guarantee of that loss at 2A. Thermal/SOA qualification is required.

Initial bench profile: **2A peak target, ≤100ms strike, no more than one full
100ms strike per second per channel**, then hold at **≤0.7A average and ≤1A RMS**
per coil. Apply the repetition limit to sliding one-second windows. Start at a
shorter pulse and increase only as measurements justify. These are provisional
limits, not implemented firmware settings. Two simultaneous strikes fit the
4.3A input budget; stagger them if battery sag or measured demand requires it.

Start hold PWM at **500Hz**. The FET's switching delays make 20kHz a poor default.
Duty cycle alone does not regulate current: select and measure each coil at
maximum battery voltage/cold resistance, calibrate strike and hold profiles,
and include flyback-current decay. There is no per-channel current sensor.
Enforce pulse duration, RMS/average hold budgets, maximum session duration,
watchdog, communication timeout and fault shutdown. Confirm driver IN ≥3.0V
using suitable nRF GPIO drive strength and the loaded 3.6V actuation cutoff.

D20–22 are B360A flyback diodes, cathodes on BAT_PROT and anodes on switched
returns. Measure release time; a simple freewheel diode slows mechanical release.
Q4 drives an active buzzer on/off, not an unspecified passive audio transducer.

## Layout and validation

Reserve substantial drain-tab copper for Q2/Q3; the datasheet's 1.4A continuous
rating at 3V/25°C assumes 15×15mm of 1oz copper and derates with temperature.
Use short flyback loops and battery returns away from sensor/radio paths.
The provisional Battery net class uses 2mm tracks and Actuator branches use 1mm;
route planes/pours and verify temperature rise and fault capacity before fab.

U13 uses project-authored **TI_RPW0010A**, transcribed from TI's 4225183/A
land/stencil drawings. Pins 5/6 are the long IN/OUT power bars; **there is no
central ground EP**. Do not put ground vias through those bars. Corner lands
use joined pad sections. Final paste, rotation and thermal copper need assembler
review. J2's 3mm grid, 1.02mm signal drills and 3mm locating hole match Molex's
SD-43045-001 drawing; -0400/-0401 differ in finish.

KiCad 10.0.6: **zero ERC errors/warnings**, independent contract for **130
components, 94 nets, 409 endpoints and 22 intentional NCs**. PCB nets, UUID paths
and BOM fields agree. Native DRC has **zero rule/parity issues and 323 unrouted
connections**. These are consistency checks, not measured electrical performance.
The schematic/PCB analyzers and EMC screen were rerun. Remaining layout findings
include no ground planes/stitching, USB bypass placement, fiducials and test
access. The schematic analyzer reports missing U5 pull-ups across R37/R38 and
split 3V3 rails; the independent KiCad netlist verifies those 0Ω links and the
single sourced global 3V3 net. These analyzer findings are not additional ERC
failures. Manufacturer pin/land checks above are manual, datasheet-backed;
current/pulse/thermal limits remain engineering estimates pending measurement.

Qualification still includes startup/running shorts at battery extremes, USB
insertion, charging recovery/interlock, latch reset, temperature, coil release,
and EMC. No SPICE simulator or coil R/L model is available locally.

Sources: [TI TPS25946, sections 8.3/9 and RPW drawings](https://www.ti.com/lit/ds/symlink/tps25946.pdf),
[Diodes ZXMS6005DG](https://www.diodes.com/datasheet/download/ZXMS6005DG.pdf),
[Microchip MCP73831/2](https://ww1.microchip.com/downloads/en/DeviceDoc/20001984g.pdf),
[Molex 43045 drawing](https://datasheet.lcsc.com/datasheet/pdf/b6e3df063c26f8567b294b4b1d02bfdf.pdf?productCode=C585880),
[JST PH rating](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf).
