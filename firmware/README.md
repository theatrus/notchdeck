# NotchDeck One — firmware

Dual-mode (USB HID + BLE HOGP) controller firmware for the nRF52840, on the
**nRF Connect SDK (Zephyr)**. Implements the protocol in
[`../docs/02-emulation-protocol-spec.md`](../docs/02-emulation-protocol-spec.md).

The firmware builds in CI against NCS. Rev C adds independently selectable magnetic
and Gray-coded handles, with host tests and six compile profiles. It has not been
bench-validated on the controller. Magnetic calibration is deliberately empty until
real detent angles are measured. See [handle interfaces](../docs/06-handle-interfaces.md)
for wiring, profiles, calibration and fault behavior.

## Rev E split hardware

Rev E moves the 4×4 buttons and RGB to an STM32G030 panel over I²C. **The existing Rev C/D direct-GPIO overlay and LED driver are not compatible with that panel.** Panel firmware, a versioned I²C protocol and main-board integration remain to be implemented; handle pin assignments are unchanged. See [panel interface and programming](../hardware/notchdeck-buttons/README.md). No Rev E flashable image is provided yet.

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
- **Handles.** Combined mascon or independent power/brake, with magnetic/Gray
  backends per handle. Dual mode reports generic power Y and brake X; optional
  combined output retains the canonical notch values. Brake overrides traction.
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

- Measure detent centers into `handle_calibration.h` for each magnetic handle.
- Bench-test the Rev C pin map and implement nav/reverser scanning in `report_engine.c`.
- Define WS2812 SPI pinctrl for the target board.
- Allocate real USB VID/PID (`prj.conf`) — do **not** ship pid.codes placeholders or
  Zuiki's `0x33DD`.
- Implement live VBUS plug/unplug transport switching (skeleton picks once at boot).

Rev C and Rev D builds use `boards/notchdeck_rev_c.overlay` plus `configs/rev_c.conf` and a
handle profile; see the [build examples](../docs/06-handle-interfaces.md#firmware-profiles-and-output).
`make test` also runs the sensor-independent handle behavior tests in
`test/host_handle_test.c`.

Rev D changes the Gray harness connectors only; the Rev C overlay and all six
profiles remain compatible. See `docs/07-japanese-handle-build.md` for assemblies.
