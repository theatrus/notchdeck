# NotchDeck One firmware

nRF52840 USB HID + BLE HOGP application using **nRF Connect SDK v3.3.0**, pinned in
[west.yml](west.yml). CI builds the nRF52840 DK bring-up image and six Rev C/D
handle profiles. Host tests exercise report layout and sensor-independent handle
behavior. The application has not been validated on a fabricated controller.

## Rev E panel / Rev G actuator support status

Rev G adds SOL1 P0.20, SOL2 P0.13, BUZZ P0.22, ACT_EN P0.24 and
BAT_nFAULT P1.00. ACT_EN inhibits charging only; stop PWM and keep charging inhibited on a fault. **No actuator backend is implemented.** Do not attach loads
when using the old Rev C/D overlays: these pins have different roles there.
Implement the default-off, strike/hold, 2A/100ms per-channel strike target and 4.3A total input budget, charger interlock/low
battery shutdown, watchdog and fault latch requirements in the
[actuator guide](../hardware/notchdeck-one/ACTUATORS.md) before energizing loads.

Rev E moves the 4×4 keys and RGB to an STM32G030 panel over I²C. **The existing
Rev C/D direct-GPIO overlay and LED driver do not operate that panel.** There is
no Rev E production image or STM32 firmware yet. The [panel guide](../hardware/notchdeck-buttons/README.md)
defines hardware pin functions and the interface requirements still to implement.

Handle decoding supports combined mascon or independent power/brake, with a
magnetic or Gray backend per handle, debounce/hysteresis, brake priority and
neutral re-arming. Magnetic calibration is deliberately empty until real detent
angles are measured. See [handle interfaces](../docs/06-handle-interfaces.md).

## Source layout

| Path | Responsibility |
|---|---|
| `src/hid_descriptor.h`, `src/report.h` | Shared HID descriptor and packed input/output reports |
| `src/handle_decode.c`, `src/handle_calibration.h` | Pure handle behavior and measured calibration inputs |
| `src/lever.c` | Sensor access and handle configuration |
| `src/report_engine.c` | Direct GPIO button input and report assembly; panel/nav/reverser integration pending |
| `src/transport_usb.c`, `src/transport_ble.c` | USB HID and BLE HIDS transports |
| `src/leds.c` | Legacy direct-strip lighting skeleton; Rev E panel backend pending |
| `src/main.c`, `src/dfu.c` | Boot-time transport choice, report loop and proposed bootloader-entry request |
| `boards/`, `configs/` | DK overlay and Rev C/D handle build profiles |
| `test/` | Host report and handle tests |

## Build

Use an NCS v3.3.0 toolchain environment with `west`, CMake/Ninja and the SDK's
Python dependencies installed. From the repository root, initialize a **new**
workspace with the local manifest if this checkout is not already in one:

```sh
west init -l firmware
west update
west zephyr-export
```

Do not reinitialize an existing SDK workspace. CI's exact environment is recorded
in [ci.yml](../.github/workflows/ci.yml). The default target is the DK bring-up
configuration, with placeholder peripheral pins and the DK flash layout:

```sh
# From the repository root:
make -C firmware test
make -C firmware build
make -C firmware uf2
make -C firmware release
```

The wrapper explicitly uses sysbuild. Default outputs are
`firmware/build/firmware/zephyr/zephyr.{uf2,hex}`; release copies them to
`firmware/dist/notchdeck-one-vX.Y.Z.{uf2,hex}`. Override `BOARD` or `BUILD` as needed;
relative `BUILD` paths are resolved from `firmware/`. Use a fresh build directory
when changing boards or moving an old non-sysbuild build to this wrapper.

Equivalent direct build from the repository root:

```sh
west build --sysbuild -b nrf52840dk/nrf52840 firmware -d build
# Outputs: build/firmware/zephyr/zephyr.uf2 and zephyr.hex
```

`make -C firmware flash` builds and flashes the selected target over SWD;
`make -C firmware menuconfig` opens the application's Kconfig. The default target
is for a connected DK, not a production Rev E flash recipe. For Rev C/D handle
compile profiles, use the [profile command](../docs/06-handle-interfaces.md#firmware-profiles-and-output).
Handle assignments survive into Rev E, but the panel needs a new integration.

## Tests and CI artifacts

`make -C firmware test` requires only a host C compiler. It checks seven-byte
report layouts, IDs, offsets and the DFU combo mask, plus Gray patterns,
calibration validation, angle wrapping, hysteresis, debounce, stale-input faults,
brake priority and re-arming.

[GitHub Actions](https://github.com/theatrus/notchdeck/actions/workflows/ci.yml) runs:

- `host-test`: both host tests and mechanical drawing/cam-table consistency.
- `firmware-build`: default DK sysbuild plus all six Rev C/D profiles.
- `hardware-checks`: both PCBs' net/ERC, schematic/PCB, BOM and floorplan DRC checks.

Download `notchdeck-one-firmware` for `notchdeck-one.uf2` and `notchdeck-one.hex`
from the **default DK build**. Profile builds are compile checks and are not
uploaded. `notchdeck-boms` contains both PCB assembly CSVs. Missing artifact files
fail CI; assembly ZIPs/CPLs are generated locally with `make -C hardware jlc`.

## Updates and versioning

UF2 output is enabled, but generating a UF2 file does **not** install or validate
an on-device bootloader. Double-tap Reset and Select+Start entry are proposed user
flows dependent on the final board/bootloader/flash layout. There is no OTA package
or tested update path yet; see [firmware updates](../docs/05-firmware-update.md).

`VERSION` supplies Zephyr's application version and release filenames.
`CONFIG_BT_DIS_FW_REV_STR` in `prj.conf` is currently a separate literal: update it
with `VERSION`. The release target copies files; it does not synchronize that
string, sign images, build a bootloader or publish a GitHub release.

## Remaining implementation

- Implement STM32 scanning/RGB firmware, a versioned I²C contract, and the main
  Rev E backend/overlay, including Select/Start merging and disconnect handling.
- Measure magnetic detent calibration and bench-test sensors, harnesses and faults.
- Implement panel navigation/hat conversion, reverser sampling and button debounce.
- Enforce the panel/USB current budget; finish output-report rendering and timeout
  behavior with the panel backend.
- Add live VBUS transport switching and MAX17048 battery-service updates.
- Finalize a production board definition, USB IDs, bootloader and flash partitions;
  implement feature-report handlers if retained. Validate USB/BLE behavior on hosts.
