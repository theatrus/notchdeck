# BenchBits Master Controller

> Working name. A dual-mode (USB + BLE) train **master controller** ("mascon") — an
> open-hardware reimplementation of the Zuiki / Densha de GO! style one-handle power/brake
> lever, built on a low-power Nordic nRF SoC.

The goal is a controller that plugs in over **USB HID** *and* roams over **Bluetooth LE HID**,
presenting to every host (Windows / macOS / Linux / Android / iOS / Switch-class hosts) as a
standard, **driverless HID joystick** — exactly like the commercial Zuiki Mascon does — while
adding host-controllable **lamps/LEDs** (notch indicator, status RGB, instrument/warning lamps,
optional display) that simulators can drive.

## Why this is feasible as one chip

HID is **transport-agnostic**: the same input report (buttons + hat + a notch-lever axis) rides
over USB HID, Bluetooth Classic HID, or BLE HID-over-GATT with no semantic change — only framing
(report-ID prefix, endpoint vs GATT characteristic) differs. The **nRF52840** has both a
full-speed USB 2.0 device controller *and* a BLE 5.x radio on one low-power Cortex-M4F, so a single
part covers both transports. See [`docs/03-hardware-and-firmware-architecture.md`](docs/03-hardware-and-firmware-architecture.md).

## The one load-bearing input

The power/brake lever is **a single 8-bit analog axis carrying discrete per-notch byte values** —
*not* a stack of buttons. Emergency = `0x00`, brake `B8…B1` climbs, Neutral ≈ `0x80`, power
`P1…P5` climbs to `0xFF`. Every consuming app's real job is to *threshold that axis back into named
notches*. We emit it on the **Y axis** (the convention SDL and the Zuiki driver use). Full encoding
table in [`docs/02-emulation-protocol-spec.md`](docs/02-emulation-protocol-spec.md).

## Documents

| Doc | Contents |
|---|---|
| [`docs/01-research-findings.md`](docs/01-research-findings.md) | What the Zuiki Mascon / MasconPro and the Densha de GO! lineage actually do on the wire — VID/PIDs, HID class, byte tables, the SDL driver, reverse-engineering sources. Verified research. |
| [`docs/02-emulation-protocol-spec.md`](docs/02-emulation-protocol-spec.md) | Our emulation spec: unified HID report descriptor, input/output report layouts, byte offsets (USB vs BLE), notch-axis encoding table, button/hat map, LED output reports. |
| [`docs/03-hardware-and-firmware-architecture.md`](docs/03-hardware-and-firmware-architecture.md) | nRF SoC selection, dual-mode (USB/BLE) transport arbitration, BLE HOGP + Battery service, USB HID class, power budget, and the LED/lamp/display subsystem. |
| [`docs/04-bom-sourcing.md`](docs/04-bom-sourcing.md) | JLCPCB/LCSC availability for every block — module, power path, USB-C, lever sensor, LEDs — with part numbers, stock, and fallbacks. Confirms the design is fully assemblable. |

## Status

Research + protocol framing. No firmware or hardware committed yet. Name is provisional.

## License

TBD (intend permissive — MIT/Apache-2.0 — for an open-hardware/firmware project).
