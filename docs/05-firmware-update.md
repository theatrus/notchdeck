# Firmware update & user upgrades — NotchDeck One

How an end user (and we) put new firmware on the device. Goal: **a non-technical user can
upgrade over USB with no drivers and no tools**, with a wireless option and a guaranteed
recovery path.

## Recommended: UF2 bootloader over USB (drag-and-drop)

The primary user path is a **UF2 bootloader** — the same UX as Adafruit Feather / nice!nano /
many nRF52840 keyboards (including nrfmicro, which runs the *same E73 module*):

1. User double-taps the **RESET** button (or we trigger it from the app/a button combo).
2. The device re-enumerates as a **USB mass-storage drive** named e.g. `NOTCHDECK`.
3. User drags a `notchdeck-one.uf2` file onto the drive.
4. The bootloader writes + verifies it and reboots into the new firmware.

No drivers, no command line, works on Windows/macOS/Linux/ChromeOS. This is the default we
design the PCB and build around.

**Bootloader choice:** the open-source **Adafruit nRF52 Bootloader** (MIT) is the pragmatic
pick — it bundles UF2 mass-storage **+ CDC serial DFU + BLE OTA DFU** in one, is proven on the
E73/nRF52840, and exposes the double-tap-reset behaviour. It is flashed **once at the factory
via SWD**; thereafter all updates go through it (no SWD needed by users).

> Family ID for `uf2conv`: nRF52840 = **0xADA52840**. Build the app, then convert the signed
> hex/bin to `.uf2` for that family.

## Secondary: BLE OTA DFU (wireless)

Since NotchDeck is already a BLE peripheral, offer **over-the-air updates** too:

- Via the Adafruit bootloader's OTA, or **Nordic Secure DFU** (nrf_dfu) — both update from the
  **nRF Connect / nRF Toolbox** phone apps (or a future NotchDeck companion app).
- Nice for users without easy cable access; **signed** in the Nordic Secure DFU case.

This is a build-time add-on, not required for v1, but the bootloader choice above already
supports it.

## Developer / factory / recovery: SWD

- A **SWD header** (Tag-Connect TC2030 or a 0.05″ header) carries SWDIO(37), SWDCLK(39),
  nRESET(26), +3V3, GND — see [`../hardware/NETPLAN.md`](../hardware/NETPLAN.md).
- Used to (a) install the bootloader at production, (b) full-chip debug during development,
  (c) **un-brick** — SWD can always reflash the bootloader + app regardless of state.
- Tools: J-Link, or any CMSIS-DAP probe (e.g. a Pi Pico running picoprobe) with `nrfjprog` /
  `pyocd` / `openocd`.

## Build outputs

The Zephyr/NCS app (`firmware/`) should emit, per release:

| Artifact | For | How |
|---|---|---|
| `notchdeck-one.uf2` | **users** (drag-and-drop) | `west build` → `uf2conv.py` (family 0xADA52840), or Zephyr's `CONFIG_BUILD_OUTPUT_UF2` |
| `notchdeck-one.hex` | factory / SWD | `west build` artifact |
| OTA package (`.zip`) | BLE OTA | `nrfutil pkg generate` (Nordic Secure DFU) or the Adafruit OTA flow |
| bootloader `.hex` | one-time factory SWD flash | from the bootloader project, per-board build |

A `firmware/Makefile`/release script should produce the `.uf2` + OTA zip and stamp the version
into the BLE Device Information Service + USB bcdDevice.

## Architecture decision (pick during firmware bring-up)

- **Option 1 — Adafruit UF2 bootloader + Zephyr app as UF2 (recommended for v1).**
  Best user UX, least friction, proven on this exact module. App is built unsigned and wrapped
  to `.uf2`. Bootloader provides UF2 + CDC + BLE OTA.
- **Option 2 — MCUboot + USB DFU (SMP).** More "Zephyr-native", supports **signed images +
  rollback/recovery slots** (robust against bad/partial flashes), but the stock user tool is
  `mcumgr` (CLI/app) unless we add a UF2 front-end. Better security story, worse drag-and-drop
  UX out of the box.

**Plan:** ship v1 on Option 1 (UF2) for the cleanest user experience; revisit MCUboot signing
if/when we want secure, verified updates (see security note).

## Security trade-off

- **UF2 is unsigned** — anyone with physical USB access can flash any image. Fine for an open,
  user-hackable device (and consistent with the maker-friendly positioning); it cannot be
  exploited remotely (requires the physical double-tap-reset).
- For **signed/verified** updates (anti-bricking, anti-tamper), use **MCUboot** (Option 2) or
  **Nordic Secure DFU** with an image-signing key. This matters more for the BLE-OTA path
  (remote) than for local USB. Decide before any commercial release.

## PCB checklist (so the above works) — in `../hardware/NETPLAN.md`

- [x] USB-C with D+/D− to E73 pads 31/29, VBUS to pad 27 (mass-storage UF2 path).
- [x] RESET button on nRESET (P0.18) for **double-tap → DFU**.
- [x] SWD header (SWDIO/SWDCLK/nRESET/3V3/GND) for factory bootloader install + recovery.
- [ ] Optional: a dedicated **BOOT/DFU button** (only if we pick a bootloader that wants a pin
      instead of double-tap — Adafruit's uses double-tap, so usually not needed).
- [ ] Silkscreen the SWD pin 1 + a note that double-tap-reset enters the update drive.
