# NotchDeck

[![CI](https://github.com/theatrus/notchdeck/actions/workflows/ci.yml/badge.svg)](https://github.com/theatrus/notchdeck/actions/workflows/ci.yml)

**NotchDeck One** is a BenchBits train controller project with USB HID and Bluetooth LE HID.
It supports our own Japanese-style **separate power lever and rotary brake**, or a
**combined mascon**. Each handle can use an AS5600 magnetic sensor or a Gray-code
contact cam. The goal is a driverless joystick with host-controlled lighting;
host/game compatibility has not yet been bench-tested.

## Current design: Rev E

| Assembly | Function | Provisional floorplan |
|---|---|---|
| [Logic / connectors](hardware/notchdeck-one/FLOORPLAN.md) | E73 nRF52840 module, USB/BLE, battery power, handle ports, Select/Start and Reset | 115×90mm, four layers |
| [Button panel](hardware/notchdeck-buttons/README.md) | STM32G030, detachable 4×4 diode key matrix, 16 RGB LEDs | 86×120mm, two layers, 19mm key pitch |

A six-way 1mm FFC carries power, I²C and interrupt between boards. The selected cable
is Molex **0151670213** (DigiKey **WM13121-ND**); the panel guide records its reversed
connector numbering and remaining fit checks. The STM32G030 **C529330** was selected
from owned JLCPCB inventory.

Both hierarchical schematics are wired and pass strict ERC, complete net checks,
schematic/PCB parity and BOM audits. **Both PCBs are unrouted floorplans and are not
ready for fabrication.** The [hardware guide](hardware/README.md) tracks routing,
mechanical, power-budget and assembly work still required.

The nRF firmware builds against NCS v3.3.0, with host tests and six Rev C/D handle
profiles compiled in CI. **Rev E panel firmware and main-board I²C integration are
not implemented.** The old direct-GPIO button/RGB overlay does not operate Rev E.
Magnetic handles also require measured detent calibration. No production firmware,
bootloader integration or fabricated-controller validation is claimed.

## Handles and reports

Combined mode sends discrete notch values on HID **Y**: EB=`0x00`, N=`0x80`, P5=`0xFF`.
Separate-handle mode uses **Y=power, X=brake**, with brake priority and neutral
re-arming. Both magnetic and contact backends use absolute positions. See the
[handle interface](docs/06-handle-interfaces.md) for cam codes, calibration and
profiles, and the [own-build guide](docs/07-japanese-handle-build.md) for mechanisms
and the provisional panel layout.

## Checks and exports

Run from the repository root:

```sh
make -C firmware test             # host compiler only
make -C hardware verify           # KiCad 10 + Python with pcbnew
make -C hardware jlc              # separate logic and button assembly ZIPs
```

On Linux, pass `KICAD_PYTHON=python3` to hardware checks with KiCad's Python module
installed. The [hardware guide](hardware/README.md) covers setup and regeneration;
the [firmware guide](firmware/README.md) covers NCS builds and release commands.

Each hardware ZIP contains Gerbers, drill, BOM and pick-and-place (CPL) files.
Exports describe the current unfinished boards; exporting does not approve them
for manufacture. [Sourcing](docs/04-bom-sourcing.md) covers **five complete sets**:
176 installed parts and 37 JLCPCB codes per set, plus the separate cable. Stock
observations are dated snapshots, with private inventory retained outside Git.

[GitHub Actions](https://github.com/theatrus/notchdeck/actions/workflows/ci.yml)
publishes `notchdeck-boms` (both assembly BOMs) and `notchdeck-one-firmware`
(default nRF52840 DK bring-up UF2/HEX). Handle profiles are compile checks only;
there is no Rev E or STM32 image in those artifacts. CI checks floorplan DRC rules
and parity while allowing the documented unrouted connections.

## Documentation

| Guide | Contents |
|---|---|
| [Hardware](hardware/README.md) | KiCad projects, validation, manufacturing exports and open work |
| [Firmware](firmware/README.md) | Build/test commands, CI artifacts and implementation status |
| [Architecture](docs/03-hardware-and-firmware-architecture.md) | Two-board design, buses, power and firmware responsibilities |
| [Sourcing](docs/04-bom-sourcing.md) | Assembly BOMs, five-set stock accounting and external parts |
| [Parts](hardware/PARTS.md) / [net plan](hardware/NETPLAN.md) | Exact selections, footprints, pad assignments and wiring |
| [Handle interfaces](docs/06-handle-interfaces.md) | Magnetic/Gray harnesses, codes, profiles and fault behavior |
| [Japanese-style handle build](docs/07-japanese-handle-build.md) | Own-build mechanics, provisional layout and cam targets |
| [Protocol](docs/02-emulation-protocol-spec.md) | HID reports, notch encoding and planned lighting features |
| [Firmware updates](docs/05-firmware-update.md) | Current artifacts, SWD access and proposed user-update path |
| [Research](docs/01-research-findings.md) | Original Zuiki/Densha de GO! protocol research and references |

## License

TBD; a project-wide license has not yet been selected. Third-party library sources
and licenses are recorded in [attributions](hardware/lib/ATTRIBUTIONS.md).
