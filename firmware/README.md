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

## Firmware updates (see ../docs/05-firmware-update.md)

- **User path:** UF2 drag-and-drop. `CONFIG_BUILD_OUTPUT_UF2=y` emits `build/zephyr/zephyr.uf2`;
  the user double-taps RESET (or holds **Select + Start** at power-on → `dfu.c` writes the
  bootloader GPREGRET magic and resets) to mount the update drive, then drops the `.uf2`.
- **Version:** the `VERSION` file drives `app_version.h` and the BLE DIS firmware-revision
  (`CONFIG_BT_DIS_FW_REV_STR`, kept in sync by the `release` target).
- `make release` stamps versioned `dist/notchdeck-one-vX.Y.Z.{uf2,hex}`.
- The UF2 base address / flash partitions are finalized with the production board's bootloader
  (Adafruit nRF52 UF2 bootloader, flashed once via the SWD header). MCUboot + signed images is
  the documented secure-update upgrade path.

## Test & CI

- `make test` builds and runs `test/host_report_test.c` with a **plain host compiler** (no
  Zephyr) — it guards the wire contract: report sizes (7 B), field offsets (lever = Y = byte 4),
  report IDs, and the DFU boot-combo mask. Runs in CI as the fast `host-test` job.
- `.github/workflows/ci.yml` also builds the full NCS firmware (`firmware-build`, via
  `firmware/west.yml`) and runs KiCad library/ERC/BOM checks (`hardware-checks`).

## TODOs before first flash

- Set real `LEVER_ANGLE_MIN/MAX` and direction in `lever.c` after assembling the shaft.
- Map real button/nav/reverser GPIOs in the board overlay and `report_engine.c`.
- Define WS2812 SPI pinctrl for the target board.
- Allocate real USB VID/PID (`prj.conf`) — do **not** ship pid.codes placeholders or
  Zuiki's `0x33DD`.
- Implement live VBUS plug/unplug transport switching (skeleton picks once at boot).
