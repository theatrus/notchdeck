# Rev D magnetic and Gray-coded handles

The same PCB supports a combined 15-position mascon, or separate power and brake
handles. Each handle independently uses an AS5600 magnetic sensor or Gray-coded
contacts. Dual-handle ranges are power Off/P1–P5 and brake Release/B1–B8/EB.
Both types are absolute: there is no incremental position count to lose at startup.
Mechanical detents establish the feel and stable positions in either case.
See the [own-build Japanese-style handle plan](07-japanese-handle-build.md) for
mechanical arrangement, harness construction and provisional detent/cam targets.

## Connections

| Handle | Magnetic | Gray contacts |
|---|---|---|
| Power (dual) | J10, mux channel 0; onboard U5 is the default sensor | J12: pins2–4=S0–S2 |
| Brake (dual) | J11, mux channel 1; requires an external sensor board | J5: pins2–5=S0–S3 |
| Combined mascon | J10/U5, mux channel 0 | J5 as above |

J10/J11 are keyed four-pin JST PH: **1=3V3, 2=GND, 3=SDA, 4=SCL**. Use a 3.3V
AS5600 board with local decoupling and no additional pull-ups. This is a short
internal harness interface (≤20cm initial target), operated at 100kHz; measure bus
rise times and noise on the assembled wiring. Power off before changing cables.

**Remove both R37 and R38 before connecting an external power/combined sensor at
J10.** They isolate onboard U5; leaving either connected can interfere with that
bus. Only one AS5600 per mux channel is permitted. J11 has no onboard sensor.
Firmware selects channel 0 (0x01) or channel 1 (0x02) on the TCA9543A at 0x70,
reads status/raw angle at 0x36, then deselects both. The fuel gauge at 0x36 remains
on the independent I2C1 controller. Do not enable both mux channels simultaneously.

Rev D uses one connector per cam: **J12 power: 1=GND, 2–4=S0–S2, 5=3V3**;
**J5 brake/mascon: 1=GND, 2–5=S0–S3, 6=3V3**. Leave the supply cavity
empty for passive switch harnesses. These replace J5–J8/J12–J14 in Rev C; the
MCU pin map is unchanged. A closed switch pulls its bit low;
open is high. External 10k pull-ups, 1k series resistors and 100nF capacitors are
already populated. Select gold/microload contacts qualified at 3.3V and roughly
0.33mA, or revise the circuit for the selected switch's required current. Do not
assume a mains-rated contact works reliably at this load. Mount and adjust cams
so each detent has a stable code well away from its switching boundary.

## Gray patterns for our cams

These are **electrical voltage levels**, not closure masks: 1=open,0=closed.
Read S3…S0 or S2…S0 left to right. Adjacent detents change exactly one bit. These
are bounded cams with end stops; the last-to-first transition is not supported.
All-open is reserved so an unplugged harness does not decode as a valid notch.
The maps supersede the earlier Rev B table, which used all-open as P1.

| Power position | S2 S1 S0 | Brake position | S3 S2 S1 S0 |
|---|---|---|---|
| Off | 001 | Release | 0000 |
| P1 | 011 | B1 | 0001 |
| P2 | 010 | B2 | 0011 |
| P3 | 110 | B3 | 0010 |
| P4 | 100 | B4 | 0110 |
| P5 | 101 | B5 | 0111 |
| — | — | B6 | 0101 |
| — | — | B7 | 0100 |
| — | — | B8 | 1100 |
| — | — | EB | 1101 |

| Combined position | S3 S2 S1 S0 |
|---|---|
| EB | 1110 |
| B8 | 1010 |
| B7 | 1011 |
| B6 | 1001 |
| B5 | 1000 |
| B4 | 0000 |
| B3 | 0001 |
| B2 | 0011 |
| B1 | 0010 |
| N | 0110 |
| P1 | 0111 |
| P2 | 0101 |
| P3 | 0100 |
| P4 | 1100 |
| P5 | 1101 |

The power map's unused patterns are 000 and 111.
For brake, unused patterns are 1000,1001,1010,1011,1110,1111. Combined reserves1111.
A broken individual wire can still turn one valid code into another; this wiring
is not redundant fault detection. Gray coding reduces ambiguous transitions,
but software debouncing and correct cam geometry are still required.

## Magnetic calibration

Magnetic sensing avoids contact wear, but magnet alignment, gap and mechanical
movement still affect the measured angle. Use a diametrically magnetized magnet
centered on the shaft; check the AS5600 field-status flags throughout travel.

Measure raw 12-bit angles at every assembled detent and populate
[`handle_calibration.h`](../firmware/src/handle_calibration.h). Centers follow
logical order: combined EB through P5, power Off through P5, brake Release through
EB. Decreasing angles and a 4095→0 seam are supported. Set hysteresis in raw counts
(4096 counts per turn); adjacent centers must remain more than twice the hysteresis
apart. Validate margins under shaft load, vibration and temperature before choosing
that value. Do not use invented equally spaced centers for a real handle.

The supplied arrays intentionally have `count=0`: magnetic output stays faulted
until measured calibration is supplied. `lever_set_calibration()` also accepts
validated values for a future UI/persistence layer; no calibration UI or persistent
storage is implemented yet. Calls must be serialized with the report loop.

## Firmware profiles and output

From the repository root in an initialized NCS workspace:

```sh
west build -b nrf52840dk/nrf52840 firmware -d build-dual-gray -- \
  -DDTC_OVERLAY_FILE=boards/notchdeck_rev_c.overlay \
  '-DEXTRA_CONF_FILE=configs/rev_c.conf;configs/dual_gray.conf'
```

Replace the final profile with one of:

| Profile | Power/first | Brake |
|---|---|---|
| `combined_magnetic.conf` | Combined magnetic | unused |
| `combined_gray.conf` | Combined Gray | unused |
| `dual_magnetic.conf` | Magnetic | Magnetic |
| `dual_gray.conf` | Gray | Gray |
| `dual_mixed.conf` | Magnetic | Gray |
| `dual_gray_power.conf` | Gray | Magnetic |

The Rev C overlay also applies to Rev D (identical GPIO assignments). It replaces DK pin assignments, disables conflicting DK peripherals,
configures NFC pins as GPIO, reset in UICR and calibrated RC LFCLK. It still uses
the DK platform/flash layout for SDK bring-up, not a production board/bootloader.
The default build without that overlay remains the direct-I2C DK test setup.

Dual mode defaults to generic HID **Y=power (0…255)**, **X=brake (0…255)**.
Z remains reserved for the reverser. The seven-byte report layout is unchanged.
This is not a claim of exact DGC-255 emulation. Set
`CONFIG_NOTCHDECK_SPLIT_AXES=n` to use the existing combined Y-notch encoding,
with brake taking priority over power. Combined mode retains the original
EB=0x00/N=0x80/P5=0xFF mapping.

Gray samples must be stable for 16ms. Magnetic readings use nearest calibrated
centers with hysteresis; missing/weak/strong-field status is invalid. An invalid
sample holds the last accepted position for less than 100ms; on the next poll at
or beyond that limit, either failed handle produces power-off/emergency-brake
output and clears the arm state. I2C transfer timeouts can delay that poll.
Startup and fault recovery require both handles at neutral (or combined N) before
power is enabled. Any brake notch suppresses traction. Sensor type is explicit;
an unplugged sensor never causes automatic fallback to another backend.

## Verification and remaining work

`make -C firmware test` checks all cam patterns/adjacent transitions, angle wrap and
reversed travel, calibration rejection, hysteresis, debounce, uptime wrap, stale
input, brake priority and neutral re-arming. CI compiles all six profiles using the shared Rev C/D pin map.
Native hardware checks cover 140 symbols, 439 pin endpoints, schematic/PCB identity
and the 139-part JLCPCB assembly BOM. ERC and floorplan DRC are clean apart from
380 intentionally unrouted connections.

Before hardware use: build the cams or sensor carriers, measure/calibrate magnetic
handles, scope the harness signals, verify unplug/reconnect and startup behavior,
and test actual HID mappings. Nav/reverser scanning, RGB power limits, final
bootloader/USB IDs and the broader power/layout reviews remain open. External
sensor boards, magnets, microload switches, cams and mating harnesses are outside
the main PCB BOM and its five-board stock check.
