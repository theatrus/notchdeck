# NotchDeck One — firmware

Dual-mode (USB HID + BLE HOGP) controller firmware for the nRF52840, on the
**nRF Connect SDK (Zephyr)**. Implements the protocol in
[`../docs/02-emulation-protocol-spec.md`](../docs/02-emulation-protocol-spec.md).

> **Status: SKELETON.** This compiles *conceptually* against NCS but is **not yet built
> or tested**, and pin assignments are placeholders. The local editor will flag missing
> `zephyr/*.h` includes — that's expected; these sources only resolve under the NCS build
> system, not a bare clang. Treat it as a structured starting point, not flashable yet.

## Layout

```
firmware/
├── CMakeLists.txt
├── prj.conf                 # USB HID + BLE HIDS/BAS + settings + LED strip + I2C/GPIO
├── boards/
│   └── nrf52840dk_nrf52840.overlay   # bring-up overlay (PLACEHOLDER pins)
└── src/
    ├── hid_descriptor.h     # shared HID report descriptor (spec §1) — used by BOTH transports
    ├── report.h             # packed input/output report structs (spec §2/§5)
    ├── lever.{c,h}          # AS5600 angle -> canonical notch byte (spec §4) + hysteresis
    ├── report_engine.{c,h}  # buttons + lever -> input report; output report -> LEDs
    ├── transport_usb.c      # USB HID class (legacy usb_hid)
    ├── transport_ble.c      # BLE HID-over-GATT (HOGP), appearance = Gamepad
    ├── transport.h          # shared transport interface
    ├── leds.{c,h}           # WS2812 notch bar + status RGB; host output-report override
    └── main.c               # VBUS-based transport arbitration + report loop
```

## Build (once the toolchain is set up)

```sh
# with nRF Connect SDK / west installed and the workspace initialised
west build -b nrf52840dk/nrf52840 firmware
west flash
```

Target the **nRF52840 DK** for bring-up; create a proper board definition for the Ebyte
E73 / custom PCB later (and move `boards/*.overlay` content into it).

## Key design points

- **One HID descriptor, two transports.** `hid_descriptor.h` feeds both the USB HID class
  and the BLE HIDS Report Map — single source of truth. Mind the report-ID prefix
  difference between transports (spec §2).
- **Lever = one axis.** `lever.c` quantizes the AS5600 angle into the 15 mascon notches
  using the canonical Zuiki byte values (EB=0x00 … N=0x80 … P5=0xFF), with per-boundary
  hysteresis. No transition values are emitted.
- **LEDs.** Local lever-follow + connection/battery status by default; a host Output report
  (the channel Zuiki repurposes from "rumble") takes over for in-sim signalling.

## TODOs before first flash

- Set real `LEVER_ANGLE_MIN/MAX` and direction in `lever.c` after assembling the shaft.
- Map real button/nav/reverser GPIOs in the board overlay and `report_engine.c`.
- Define WS2812 SPI pinctrl for the target board.
- Allocate real USB VID/PID (`prj.conf`) — do **not** ship pid.codes placeholders or
  Zuiki's `0x33DD`.
- Implement live VBUS plug/unplug transport switching (skeleton picks once at boot).
