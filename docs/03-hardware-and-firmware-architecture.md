# Hardware and firmware architecture — Rev E

Rev E separates the controller's logic/handle connectors from its 4×4 button panel.
Both schematics are wired and checked; both PCBs remain unrouted. This describes
the captured design and identifies firmware that still needs implementing.
See [hardware status](../hardware/README.md) for validation and remaining work.

## Board responsibilities

| Logic: `notchdeck-one` | Panel: `notchdeck-buttons` |
|---|---|
| Ebyte E73-2G4M08S1C, nRF52840, JLCPCB C356849 | STM32G030F6P6TR, JLCPCB C529330 from owned inventory |
| USB HID and BLE HOGP, report engine and handle decoding | 4×4 diode matrix scan/debounce and local RGB generation |
| USB-C, charger, battery power path, 3V3 and fuel gauge | 3V3 MCU/key power and USB-only RGB power from FFC |
| Magnetic and Gray handle ports, optional reverser input | 16 keys at 19mm pitch and 16 addressable RGB LEDs |
| Local Select/Start plus Reset; SWD access | Separate TC2030 SWD access |
| 115×90mm, four layers | 86×120mm, two layers |

The nRF52840 supplies USB and BLE on one device. The second MCU keeps matrix/RGB
wiring local to the removable panel and reduces the interconnect to six conductors.
Its scan and I²C-target firmware is **not implemented yet**.

```text
USB host <--> E73 nRF52840 <--> BLE host
                  |
                  +-- I2C0 --+-- STM32 panel (planned address 0x20)
                  |          |      +-- 4x4 diode key matrix
                  |          |      +-- AHCT buffer --> 16 RGB LEDs
                  |          +-- TCA9543A mux (0x70)
                  |                 +-- channel 0: power / combined AS5600 (0x36)
                  |                 +-- channel 1: brake AS5600 (0x36)
                  +-- I2C1 ------ MAX17048 fuel gauge (0x36)
                  +-- GPIO ------ Gray handle ports, Select/Start, panel IRQ
                  +-- ADC ------- optional reverser
```

## Inputs and panel link

The [handle interface](06-handle-interfaces.md) supports a combined 15-position
mascon, or independent power Off/P1–P5 and brake Release/B1–B8/EB. Each active
handle independently selects magnetic or Gray-code sensing. Existing nRF code
implements calibrated angle hysteresis, Gray debounce, brake priority, stale-input
fault handling and neutral re-arming. Magnetic calibration arrays are intentionally
empty until actual detent angles are measured.

Both AS5600 channels use address 0x36. The mux selects one channel at a time;
the MAX17048 with the same address uses a separate nRF I²C controller. Remove
**both R37 and R38** to isolate onboard U5 before connecting an external
power/combined sensor at J10. J11 always needs an external brake sensor.

The six-way FFC carries GND, 3V3, SDA, SCL, IRQ and USB_VBUS. Two identical
bottom-contact connectors and the specified Type A cable use **main J15 pin n →
panel J1 pin 7−n**. The [panel guide](../hardware/notchdeck-buttons/README.md)
defines the exact cable, connector pinout, MCU aliases and scan requirements.
I²C runs at 100kHz; its versioned panel register/packet protocol remains to be
defined. The main firmware must merge panel input with local Select/Start,
release panel keys on communications loss, and send bounded RGB commands.

Rev E frees the old direct button/RGB GPIOs, including NFC pins. No external LF
crystal is populated; retain the nRF RC LFCLK and P0.18 reset/UICR configuration.
The [net plan](../hardware/NETPLAN.md) is the pad-level reference. Rev C/D firmware
overlays do not support the new panel despite unchanged handle pin assignments.

## HID and transport behavior

USB and BLE use the same descriptor and seven-byte input/output payloads; USB
includes a report-ID prefix. Combined handles emit the canonical Y-notch values;
dual profiles use Y=power and X=brake, or can select combined output with brake
priority. See the [protocol spec](02-emulation-protocol-spec.md).

Current `main.c` selects USB when VBUS is present **at boot**, otherwise BLE.
Live USB plug/unplug arbitration is still TODO. BLE includes HIDS, Battery Service,
Device Information and settings/bond storage, but live fuel-gauge updates are not
implemented. Host/game compatibility needs device testing. Feature report 3 is
declared in the descriptor without implemented handlers or a finalized layout.

## Power and lighting

USB_VBUS feeds the USB regulator, MCP73832 charger and panel RGB rail. A Schottky
USB feed and AO3401A battery power path supply VSYS, then AP2112K-3.3 supplies both
MCUs and key/sensor circuitry. MAX17048 monitors BAT+. This is the discrete power
path captured in the schematics; the earlier nPM1300 proposal is not populated.

The RGB chain and SN74AHCT1G125 level shifter are on the button board and powered
only from USB. The STM32 must hold RGB output low without VBUS and use timer/DMA
to avoid blocking I²C. Target **≤250mA total panel return current**, including
3V3 and LED loads. This limit is not yet enforced. The existing 500mA charger
setting, USB source allowance/inrush, battery choice and LDO margins require a
complete power review before fabrication. USB presence does not authorize
unrestricted full-white LEDs.

The current nRF `leds.c` is an older direct-strip skeleton: its host override,
warning lamps, speed/status rendering and timeout behavior are incomplete. Rev E
needs a panel transport backend. There is no selected display or buzzer assembly.

## Implementation and validation

NCS is pinned to v3.3.0 in `firmware/west.yml`. CI runs host report/handle tests,
checks generated mechanical drawings, and compiles the DK bring-up image plus six
Rev C/D handle profiles. The [firmware guide](../firmware/README.md) documents
commands and exact artifact paths. These checks do not establish Rev E firmware
support or a production bootloader/flash layout.

Hardware CI verifies both schematics' nets/ERC, PCB identity/pad nets, BOMs and
native DRC. Unconnected items are allowed only because the saved PCBs are
floorplans. Routing, final mechanical fit, power/thermal review, assembly checks
and bench validation remain open. Current selections and dated stock records
are linked from [sourcing](04-bom-sourcing.md).
