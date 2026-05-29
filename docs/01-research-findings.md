# Research Findings — Zuiki Mascon, MasconPro & the Densha de GO! lineage

Captured from a multi-source, adversarially-verified research pass (24/25 claims confirmed) plus a
direct read of the SDL driver source. This is the factual basis for our emulation spec in
[`02-emulation-protocol-spec.md`](02-emulation-protocol-spec.md).

## TL;DR

- The Zuiki controllers are **plain USB HID joysticks** — *not* XInput, *not* Switch Pro Controller
  emulation, *not* a custom/vendor protocol. No driver required on Windows / macOS / Linux.
- The **power/brake lever is one 8-bit analog axis** with discrete per-notch byte values and **no
  transition values**. Everything else (buttons, hat) is conventional.
- USB VID/PID is **edition/mode-dependent** — a single unit may enumerate under more than one ID.
- The newer **MasconPro** got a **vendor-authored SDL driver** (`SDL_hidapi_zuiki.c`,
  `Copyright (C) 2025 Zuiki Inc.`) that exposes it on the *joystick* API — SDL maintainers
  explicitly declined to register it under the *gamepad* API ("this isn't a gamepad style
  controller").

## 1. Device class & USB IDs

| Device / edition | VID | PID | Notes |
|---|---|---|---|
| ZKNS-001, Densha de GO! edition | `0x0F0D` (HORI) | `0x00C1` | HORI = licensed Switch peripheral maker; product strings contain "for Nintendo Switch" |
| ZUIKI Switch edition / PC DInput mode | `0x33DD` (ZUIKI) | `0x0001` | |
| 1st Anniversary translucent | `0x33DD` | `0x0002` | |
| Mascon Red / Blue / Black | `0x33DD` | `0x0003` / `0x0004` / `0x0005` | |
| **MasconPro** | `0x33DD` | `0x0006` | wired USB, PC-focused, has an instrument-cluster screen |
| ZUIKI EVOTOP (PC/UWB/BT) | `0x33DD` | (EVOTOP PIDs) | a *conventional gamepad* w/ gyro+accel; the only **Bluetooth** Zuiki HID device |

The ZKNS-001 enumerates as **"HID-compliant joystick: 14 buttons, a hat switch, 4 axes."** On Windows
it is additionally a DirectInput controller (matched by ProductGuid prefix `000133dd` or product
name containing "mascon"). Older Switch variants appear in SDL's `controller_list.h` as
`k_eControllerType_SwitchInputOnlyController`.

> **Do not squat `0x33DD`** for our clone — that's Zuiki's vendor ID. We allocate our own (see spec).

## 2. The notch lever — single-axis encoding (ZKNS-001, native bytes)

Lever = HID **"Axis 2" = Switch left-stick Y (`SWITCH_LY`)**. The other three axes sit fixed at `0x80`.
**No transition values between notches** — it snaps directly to the next discrete value.

| Notch | Byte | | Notch | Byte |
|---|---|---|---|---|
| Emergency (EB) | `0x00` | | Neutral (N) | `0x80` |
| B8 | `0x05` | | P1 | `0x9F` |
| B7 | `0x13` | | P2 | `0xB7` |
| B6 | `0x20` | | P3 | `0xCE` |
| B5 | `0x2E` | | P4 | `0xE6` |
| B4 | `0x3C` | | P5 | `0xFF` |
| B3 | `0x49` | | | |
| B2 | `0x57` | | | |
| B1 | `0x65` | | | |

15 discrete positions (EB + B8..B1 + N + P1..P5). Software re-scales these raw bytes for its own use:
- **pygame**: floats on axis 1 — EB=−1.00, B1=−0.21, N=0.00, P1=+0.24, P5=+1.00
- **wesalvaro gist**: −100..+100 scale
- **BRMascon**: DirectInput 0–65535 thresholds — EB≈640, B8≈3072, N≈36668, P5=65535

⚠️ The 0–65535 / float / ±100 ranges are **software-side rescalings**. The native authoritative
values are the single bytes above. (A claim that the native values were *signed* — P5=−32768,
EB=+32767 — was **refuted** during verification; do not use it.)

## 3. The SDL MasconPro driver (`SDL_hidapi_zuiki.c`) — authoritative wire format

Vendor-contributed (`Copyright (C) 2025 Zuiki Inc.`). Key facts read directly from source:

- MasconPro → `HIDAPI_DriverZUIKI_HandleOldStatePacket`. **`joystick->nbuttons = 11`**, 1 hat, full
  axis set, **no sensors** (only the EVOTOP variants set `sensors_supported`).
- **The driver does NOT decode notches.** The lever is just read as a normal stick axis and
  forwarded; notch interpretation is left to the application.

**USB "old state packet" layout** (offsets are from the start of the report, *no* report-ID prefix):

| Byte | Meaning |
|---|---|
| `data[0]` | Button bitmask #1 — `0x01`=North `0x02`=East `0x04`=South `0x08`=West `0x10`=L-shoulder `0x20`=R-shoulder `0x40`=L-trigger(digital) `0x80`=R-trigger(digital) |
| `data[1]` | Button bitmask #2 — `0x01`=Back `0x02`=Start `0x04`=L-stick `0x08`=R-stick `0x10`=Guide `0x20`=Misc1 |
| `data[2]` | Hat / D-pad: `0..7` → 8 directions, else centered |
| `data[3]` | Left stick **X** |
| `data[4]` | Left stick **Y** ← **the power/brake lever** |
| `data[5]` | Right stick X |
| `data[6]` | Right stick Y |

Axis conversion macro (note the center is **`0x7f`** here, vs the `0x80` neutral in the ZKNS-001
docs — a 1-LSB discrepancy to be aware of):

```c
#define READ_STICK_AXIS(offset) \
    (data[offset] == 0x7f ? 0 : (Sint16)HIDAPI_RemapVal((float)((int)data[offset] - 0x7f), \
        -0x7f, 0xff - 0x7f, SDL_MIN_SINT16, SDL_MAX_SINT16))
```

**Effects / LEDs:** `SetJoystickLED` and sensors return `SDL_Unsupported()` for the MasconPro.
Rumble is an 8-byte packet, `rumble_packet[4]=low>>8, [5]=high>>8`, and `SendJoystickEffect`
forwards raw bytes via `SDL_HIDAPI_SendRumble`. This "repurpose the rumble/effect channel for raw
output packets (LED control)" path is the maintainer-blessed way to push data *to* the device.

**Bluetooth uses a DIFFERENT layout.** The same driver's `Handle_EVOTOP_PCBT_StatePacket` (for the
Bluetooth EVOTOP) shows the BT report is *not* byte-identical to USB: 16-bit little-endian axes at
`data[1..8]`, 10-bit analog triggers at `data[9..12]`, hat at `data[13]`, buttons at `data[14]/[15]`.
Two reasons: a report-ID/framing prefix shifts offsets, and they widened the payload. **Lesson for
us:** the *semantic* protocol transfers cleanly to BLE; exact byte offsets do not — budget for a
report-ID prefix.

## 4. Densha de GO! lineage (for context / optional compat modes)

- **DGC-255** one-handle USB PC controller (Taito `0x0AE4`/`0x0003`): HID joystick, 2 axes, 6 buttons,
  hat. Unlike the Zuiki it **splits brake and power onto two separate axes** and reports **`0xFF`
  during transitions** between notches. Brake axis: EB `0xB9` → B1 `0x8A`; power axis: N `0x81` →
  P5 `0x00`.
- **Classic console controllers** (N64/PS1/Saturn/Dreamcast): native per-console controller protocol,
  notches encoded as **multi-bit button combinations** — 3 bits power, 4 bits brake (Emergency = all
  brake bits released). Not an axis.
- **`ddgo-pnp-controller`** (Marc Riera, Rust): converts the Densha de GO! Plug & Play into a USB
  controller emulating many profiles (Switch one-handle, two-handle PC/PS1/N64/Saturn/Dreamcast/PS2,
  Shinkansen, Multi Train Controller). Shinkansen mode maps power to P2-P4-P7-P10-P13.

## 5. What consuming software does (why notch→axis matters)

- **BRMascon** (C#/.NET 9): reads the mascon over DirectInput (SharpDX), thresholds the Y-axis into
  notches, and emulates a **virtual Xbox 360 pad via ViGEmBus**, translating lever *motion* into
  trigger/bumper **taps** (games expect incremental presses, not absolute notch). Per-train profiles
  for 4–7 power-notch classes. ~100 ms tap-queue latency.
- **ZUIKI_to_JRE** (C#/WinForms, cracrayol): adapts the Switch mascon to *JR EAST Train Simulator*;
  INI-configurable bindings, notch-count profiles ("B1 mode" KiHa 54 vs "B6 mode"). **Now
  deprecated** — JRETS added native Zuiki support.

Common thread: hardware emits the lever as one discrete-byte axis; every consumer (a) thresholds it
back into named notches and (b) re-expresses it (incremental taps / configurable keys / passthrough).

## Sources

- Marc Riera — **Train Controller Database** & **ddgo-controller-docs** (canonical reverse-engineering reference):
  - https://traincontrollerdb.marcriera.cat/hardware/zkns001/
  - https://marcriera.github.io/ddgo-controller-docs/controllers/usb/zkns001/
  - https://marcriera.github.io/ddgo-controller-docs/controllers/usb/dgc255/
  - https://marcriera.github.io/ddgo-controller-docs/controllers/classic/tech/
- **SDL** MasconPro driver: PR https://github.com/libsdl-org/SDL/pull/13770 ·
  source https://github.com/libsdl-org/SDL/blob/main/src/joystick/hidapi/SDL_hidapi_zuiki.c
- GitHub: https://github.com/lmaodick1239/BRMascon · https://github.com/cracrayol/ZUIKI_to_JRE ·
  https://github.com/cracrayol/ConToJREts · https://github.com/marcriera/ddgo-pnp-controller
- Gist (SWITCH_LY mapping): https://gist.github.com/wesalvaro/a4a21fc3d1eebe58878b6516d9357245

## Open questions

- Exact HID report descriptor of the real MasconPro (its lever almost certainly uses the same
  single-byte Y-axis encoding, per the SDL passthrough, but not independently dumped).
- macOS IOKit / Game Controller framework enumeration quirks (inferred from HID-class, not tested).
- Full functional meaning of the 14 ZKNS-001 buttons (only "A = horn" confirmed).
