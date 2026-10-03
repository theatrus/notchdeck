# Emulation Protocol Spec — NotchDeck

Defines the on-wire HID contract our device presents over **both** transports. Design goals:

1. **Driverless** standard HID joystick on Windows / macOS / Linux / Android / iOS.
2. **One report descriptor** shared by USB and BLE; only framing differs (report-ID prefix).
3. **Lever = one 8-bit axis** carrying discrete notch bytes — bit-compatible with the Zuiki/SDL
   convention (lever on **Y**), so existing tooling (BRMascon, SDL passthrough, sim native support)
   can map the same notch values. Actual host/game compatibility needs testing.
4. A clean **host→device output report** for LEDs / lamps / instrument data.

**Implementation status (Rev E):** input/output report layouts exist in firmware,
and six handle profiles compile. Dual handles use the same report with Y=power
and X=brake. Panel key/nav integration and most lighting behavior remain unfinished.
Feature report 3 is declared in the descriptor but has no implemented handlers;
its layout below is reserved. See [firmware status](../firmware/README.md).

## 0. Identity

| Field | USB | BLE |
|---|---|---|
| Vendor/Product ID | **allocate our own** — e.g. [pid.codes](https://pid.codes) test VID `0x1209` + a sub-PID, or a real assigned VID. **Never** ship Zuiki's `0x33DD`. | n/a (GATT) |
| Product string | `NotchDeck One` | same, as GAP Device Name |
| Appearance | — | `0x03C4` (Gamepad) |
| HID version | `bcdHID 0x0111` | HID Information char |

> Compatibility note: if you *deliberately* want SDL's dedicated `SDL_HIDAPI_DriverZUIKI` to bind
> (rather than generic HID parsing), you must advertise `0x33DD/0x0006` *and* match the USB
> "old state packet" offsets exactly (no report ID). We **do not** do this by default — generic HID
> parsing uses our own descriptor. No Zuiki-identity compatibility profile is
> implemented; shipping IDs must be allocated to this project.

## 1. Unified HID Report Descriptor

One Application Collection (Joystick). **Input = Report ID 1**, **LED/lamp Output = Report ID 2**,
optional **instrument Feature = Report ID 3**.

```c
static const uint8_t HID_REPORT_DESCRIPTOR[] = {
    0x05, 0x01,        // Usage Page (Generic Desktop)
    0x09, 0x04,        // Usage (Joystick)
    0xA1, 0x01,        // Collection (Application)

    // ---------- INPUT REPORT (ID 1) ----------
    0x85, 0x01,        //   Report ID (1)

    // 16 buttons
    0x05, 0x09,        //   Usage Page (Button)
    0x19, 0x01,        //   Usage Minimum (Button 1)
    0x29, 0x10,        //   Usage Maximum (Button 16)
    0x15, 0x00,        //   Logical Minimum (0)
    0x25, 0x01,        //   Logical Maximum (1)
    0x75, 0x01,        //   Report Size (1)
    0x95, 0x10,        //   Report Count (16)
    0x81, 0x02,        //   Input (Data,Var,Abs)            -> 2 bytes

    // Hat switch (4-bit) + 4-bit padding
    0x05, 0x01,        //   Usage Page (Generic Desktop)
    0x09, 0x39,        //   Usage (Hat switch)
    0x15, 0x00,        //   Logical Minimum (0)
    0x25, 0x07,        //   Logical Maximum (7)
    0x35, 0x00,        //   Physical Minimum (0)
    0x46, 0x3B, 0x01,  //   Physical Maximum (315)
    0x65, 0x14,        //   Unit (Eng Rot: Degrees)
    0x75, 0x04,        //   Report Size (4)
    0x95, 0x01,        //   Report Count (1)
    0x81, 0x42,        //   Input (Data,Var,Abs,Null)       -> 0.5 byte
    0x65, 0x00,        //   Unit (None)
    0x75, 0x04,        //   Report Size (4)
    0x95, 0x01,        //   Report Count (1)
    0x81, 0x03,        //   Input (Const,Var,Abs) padding   -> 0.5 byte

    // 4 axes: X, Y(=lever), Z, Rz  each 0..255
    0x05, 0x01,        //   Usage Page (Generic Desktop)
    0x09, 0x30,        //   Usage (X)
    0x09, 0x31,        //   Usage (Y)        <-- POWER/BRAKE LEVER (notch axis)
    0x09, 0x32,        //   Usage (Z)        <-- reserved (reverser, optional)
    0x09, 0x35,        //   Usage (Rz)       <-- reserved (aux dial, optional)
    0x15, 0x00,        //   Logical Minimum (0)
    0x26, 0xFF, 0x00,  //   Logical Maximum (255)
    0x75, 0x08,        //   Report Size (8)
    0x95, 0x04,        //   Report Count (4)
    0x81, 0x02,        //   Input (Data,Var,Abs)            -> 4 bytes

    // ---------- OUTPUT REPORT (ID 2): LEDs / lamps ----------
    0x85, 0x02,        //   Report ID (2)
    // 8 standard indicator bits (notch/usage LEDs)
    0x05, 0x08,        //   Usage Page (LEDs)
    0x19, 0x01,        //   Usage Minimum (1)
    0x29, 0x08,        //   Usage Maximum (8)
    0x75, 0x01,        //   Report Size (1)
    0x95, 0x08,        //   Report Count (8)
    0x91, 0x02,        //   Output (Data,Var,Abs)           -> 1 byte
    // Vendor block: RGB status (R,G,B) + master brightness + speed + flags + warn
    0x06, 0x00, 0xFF,  //   Usage Page (Vendor-Defined 0xFF00)
    0x09, 0x01,        //   Usage (vendor)
    0x15, 0x00,        //   Logical Minimum (0)
    0x26, 0xFF, 0x00,  //   Logical Maximum (255)
    0x75, 0x08,        //   Report Size (8)
    0x95, 0x06,        //   Report Count (6)
    0x91, 0x02,        //   Output (Data,Var,Abs)           -> 6 bytes

    // ---------- FEATURE REPORT (ID 3): instrument / config (optional) ----------
    0x85, 0x03,        //   Report ID (3)
    0x06, 0x00, 0xFF,  //   Usage Page (Vendor-Defined)
    0x09, 0x02,        //   Usage (vendor)
    0x75, 0x08,        //   Report Size (8)
    0x95, 0x07,        //   Report Count (7)
    0xB1, 0x02,        //   Feature (Data,Var,Abs)          -> 7 bytes

    0xC0               // End Collection
};
```

## 2. INPUT report (device → host), Report ID 1

**7 payload bytes.** Offsets shown two ways because the report-ID prefix differs by transport.

| Payload byte / BLE value offset | USB report offset (including ID) | Field | Notes |
|---|---|---|---|
| 0 | byte 1 | Buttons 1–8 | bit0=B1 … bit7=B8 |
| 1 | byte 2 | Buttons 9–16 | |
| 2 | byte 3 | Hat (low nibble) + pad | `0..7` = N,NE,E,SE,S,SW,W,NW; `0x0F`/`8` = centered (null) |
| 3 | byte 4 | **X** axis | combined: center `0x80`; dual: brake `0..255` |
| **4** | byte 5 | **Y axis** | combined: discrete notch bytes (§4); dual: power `0..255` |
| 5 | byte 6 | **Z** axis | reserved: reverser (3-pos) or center `0x80` |
| 6 | byte 7 | **Rz** axis | reserved: aux dial or center `0x80` |

The current USB implementation prefixes the seven-byte payload with report ID 1.
BLE HIDS identifies it through the Report Reference and sends the seven-byte
payload without that prefix. Payload offsets remain identical. This is not the
Zuiki USB packet without report IDs; its notch values inform our encoding.

## 3. Button & hat map

Mirror the SDL/Zuiki gamepad-button assignment so existing remappers line up, then extend.

| Button | Suggested cab function | Maps to (gamepad sense) |
|---|---|---|
| 1 | Confirm / Horn-high | South (A) |
| 2 | Horn-low / Bell | East (B) |
| 3 | Door close | West (X) |
| 4 | Door open | North (Y) |
| 5 | ATS / ATC reset | L-shoulder |
| 6 | Cab / view | R-shoulder |
| 7 | Select | Back |
| 8 | Start / Pause | Start |
| 9–16 | Pantograph, headlight, sander, wiper, etc. | extension |
| Hat | Menu / camera / lookaround | D-pad |

Buttons are momentary (1=pressed). The host (or an adapter like BRMascon) decides whether to treat
them as held or as edge-triggered taps.

Rev E physically provides panel keys BTN1–BTN12 plus Up/Down/Left/Right; the last
four feed the hat once panel integration is implemented. Main Select/Start must
be ORed with panel buttons 7/8. HID button slots 13–16 remain available for future
inputs; the descriptor capacity is not a count of dedicated button switches.

## 4. Notch-lever axis encoding (Y axis) — **canonical**

Combined mode adopts the Zuiki ZKNS-001 notch values. This alone does not establish
drop-in compatibility with host software. **Snap directly between values — emit
no transition bytes.** The implemented Gray backend uses 16ms stable-state debounce;
magnetic sensing uses calibrated centers and hysteresis.

| Notch | Y byte | Normalized (host, [−1,+1]) |
|---|---|---|
| Emergency (EB) | `0x00` | −1.00 |
| B8 | `0x05` | −0.96 |
| B7 | `0x13` | −0.85 |
| B6 | `0x20` | −0.75 |
| B5 | `0x2E` | −0.64 |
| B4 | `0x3C` | −0.53 |
| B3 | `0x49` | −0.43 |
| B2 | `0x57` | −0.32 |
| B1 | `0x65` | −0.21 |
| **Neutral (N)** | `0x80` | 0.00 |
| P1 | `0x9F` | +0.24 |
| P2 | `0xB7` | +0.43 |
| P3 | `0xCE` | +0.61 |
| P4 | `0xE6` | +0.80 |
| P5 | `0xFF` | +1.00 |

Notes:
- 15 positions = EB + B8…B1 + N + P1…P5. Runtime notch-count selection is not
  implemented; current profiles use the documented P5/B8 baseline.
- Center: hardware-native neutral is `0x80`; the SDL driver centers at `0x7f`. The 1-LSB difference
  is cosmetic. **Pick `0x80` for neutral** (matches Zuiki docs); hosts that recenter at `0x7f` will
  read neutral as ≈+0.004, negligible.
- **Implemented dual mode:** Y=power Off…P5 and X=brake Release…EB, each scaled
  `0..255`, with brake suppressing power. There are no DGC-255 transition markers
  or runtime profile selector. Build-time `CONFIG_NOTCHDECK_SPLIT_AXES=n` selects
  combined Y encoding. See [handle profiles](06-handle-interfaces.md#firmware-profiles-and-output).

## 5. OUTPUT report (host → device), Report ID 2 — LEDs / lamps

The table defines intended behavior. Transport reception and partial brightness/
ownership logic exist; status overrides, speed/indicator rendering and host timeout
remain TODO. Rev E also needs the I²C panel backend and enforced current limits.

7 payload bytes. This is how a simulator drives our lights (the same role Zuiki's repurposed
"rumble/effect" packet plays — the sim writes an output report; over BLE the host writes the HID
Output Report characteristic; over USB it's a SET_REPORT / interrupt-OUT).

| Payload byte | Field | Meaning |
|---|---|---|
| 0 | Indicator bits | bit0 ATS lamp · bit1 door-open lamp · bit2 EB/buzzer lamp · bit3 overspeed · bit4–7 spare |
| 1 | Status R | RGB status LED red 0–255 (overrides local state color while non-zero, see §7) |
| 2 | Status G | green |
| 3 | Status B | blue |
| 4 | Master brightness | global LED brightness 0–255 (host can dim) |
| 5 | Speed | current train speed, scaled 0–255 → 0–`SPEED_FULL` km/h, drives meter/bargraph |
| 6 | Flags | bit0 notch-bar follow-host · bit1 sleep LEDs · bit2 demo · bit3–7 spare |

If the host never sends an output report, the device runs its **local default** lighting (notch bar
follows the lever, status LED shows connection/battery). Host writes take priority while present and
fall back to local defaults after a timeout.

## 6. FEATURE report (Report ID 3) — config / instrument (optional)

Bidirectional GET/SET for things that aren't per-frame: notch-count profile select, brightness
limits, calibration, firmware/protocol version, display page select. 7 bytes, vendor-defined; layout
TBD as features land.

## 7. Lights & LEDs we can offer

These are proposed behaviors, not completed features. Rev E has a 16-pixel panel
chain; there is no separate display, buzzer or warning-lamp assembly selected.

1. **Notch position indicator** — a linear bar (addressable WS2812B strip, or discrete/charlieplexed
   LEDs) mirroring the lever: brake notches one color (e.g. amber→red toward EB), power another
   (green), neutral a single center pip. Local by default; host can take it over (`flags bit0`).
2. **RGB status LED** — connection/power state: USB-attached = steady cyan; BLE advertising = slow
   blue blink; BLE connected = green; pairing = white blink; battery low = amber; charging = pulsing.
   Host can override color (bytes 1–3) for in-sim signalling.
3. **Instrument / speed display** — host pushes `speed` (byte 5) to drive an LED ring/bargraph
   "speedometer," or (MasconPro-style) a small **SPI OLED/TFT** showing speed + current notch. The
   display is fed by the output (or feature) report; no extra USB/BLE plumbing.
4. **Warning lamps** — discrete ATS/ATC, door-open, EB, overspeed lamps from §5 byte 0 indicator bits
   (plus an optional piezo for the ATS/EB buzzer).
5. **Backlight** — lever scale / button legends, brightness from byte 4.

**Rev E power behavior:** the panel RGB supply is USB-only; keys remain powered
on battery. Firmware must keep RGB output low without VBUS and enforce the panel
return-current target (≤250mA) within the total USB/charger budget. A host brightness
request must not override that limit. See power budget in
[`03-hardware-and-firmware-architecture.md`](03-hardware-and-firmware-architecture.md).

## 8. Report size summary (on the wire)

| Report | ID | Dir | Payload | +ID = total |
|---|---|---|---|---|
| Joystick state | 1 | IN | 7 B | 8 B |
| LED/lamp | 2 | OUT | 7 B | 8 B |
| Config/instrument | 3 | FEATURE | 7 B | 8 B |

The +ID column is the USB report length; BLE input/output characteristic values
carry the seven-byte payload. Feature report 3 remains reserved and unimplemented.
