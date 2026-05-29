# Hardware & Firmware Architecture — BenchBits Master Controller

How the dual-mode (USB + BLE) HID stack from [`02-emulation-protocol-spec.md`](02-emulation-protocol-spec.md)
maps onto a low-power Nordic nRF SoC.

## 1. SoC selection

The hard requirement is **a single low-power part that has both a USB device controller and a BLE
radio**. Most of the nRF52 line has BLE but *no* USB — only a few parts have the USB peripheral.

| Part | Core | Flash / RAM | USB | BLE | Verdict |
|---|---|---|---|---|---|
| **nRF52840** | M4F @64 MHz | 1 MB / 256 KB | **FS USB 2.0 device** | 5.x | ✅ **Recommended.** USB + BLE on one chip, ample flash/RAM for HOGP + USB HID + LED engine + (optional) display assets. Mature in nRF Connect SDK / Zephyr. |
| nRF52833 | M4F @64 MHz | 512 KB / 128 KB | FS USB 2.0 device | 5.x | ✅ Cheaper fallback; fine if no large display assets. |
| nRF52820 | M4F @64 MHz | 256 KB / 32 KB | FS USB 2.0 device | 5.x | ⚠️ Works but RAM-tight for dual stack + display; minimal builds only. |
| nRF5340 | dual M33 | 1 MB+256 KB / 512 KB+64 KB | FS USB 2.0 device | 5.x | ◯ Overkill unless a rich display/UI or heavy concurrent processing; higher BOM/complexity. Pick if adding a TFT cab display. |
| nRF52832 | M4F | 512 KB / 64 KB | **none** | 5.x | ❌ No USB — disqualified. |

**Decision: nRF52840.** Sweet spot of USB + BLE + memory + tooling. Move to nRF5340 only if a
full graphical cab display drives the requirement; drop to nRF52833 to shave cost if not.

### JLCPCB / LCSC availability (checked May 2026)

All Nordic SoCs here are **Extended** parts (one-time ~$3 feeder fee; must be in stock at order time)
— there is no Basic nRF52840.

| Option | LCSC | Package | Stock | ~Unit | Notes |
|---|---|---|---|---|---|
| **nRF52840-QIAA-R** | `C190794` | aQFN-73 (7×7) | ~1,178 | $3.80 | bare chip; you own crystals + antenna + π-match + RF cert |
| nRF52840-QIAA-R7 | `C1851953` | aQFN-73 | ~355 | $3.70 | reel variant |
| nRF52840-CKAA-R | `C3606910` | WLCSP-94 | ~239 | $5.65 | |
| nRF52840-QFAA-F-R | `C3606918` | QFN-48 | ~112 | $10.30 | |
| **Ebyte E73-2G4M08S1C** | `C2764963` / `C356849` | module 18×13 mm | ~399 / 240 | $5.96 / 7.19 | **nRF52840 module: PCB antenna + crystals + matching, pre-certified** |
| nRF52833-QDAA-R | `C2895249` | **QFN-40 (5×5)** | ~4,196 | $3.26 | fallback SoC; easier package, better stock, 512 KB/128 KB |
| nRF52833-QIAA-R | `C504799` | aQFN-73 | ~590 | $3.53 | |

Not in the JLCPCB library (would need consigned assembly): Raytac **MDBT50Q**, Insight **ISP1807**.

**Sourcing recommendation:**
1. **Prototype → Ebyte E73-2G4M08S1C module** (`C2764963`). No RF layout/tuning, certified, in stock —
   de-risks the first spin for ~$2 over the bare chip.
2. **Cost-down rev → bare nRF52840-QIAA** (`C190794`) once the RF/antenna/cert work is justified.
3. **If aQFN-73 placement or stock is a concern → nRF52833-QDAA** (`C2895249`): QFN-40, ~4k stock,
   still USB+BLE; accept 512 KB/128 KB (fine unless a graphical display is added).

SoftDevice/stack: **nRF Connect SDK (Zephyr)** — it ships both building blocks:
- USB HID device class (`usb_hid`, `CONFIG_USB_DEVICE_HID`)
- BLE HID-over-GATT / HOGP via the HIDS service (`CONFIG_BT_HIDS`)
- Battery Service, Device Information Service, settings/bonding storage

Both can be compiled in and selected at runtime — see transport arbitration below.

## 2. Block diagram (logical)

```
                +-----------------------------+
   USB-C  <---->|  USB FS device (HID)        |\
   (VBUS sense) |                             | \
                +-----------------------------+  \      +------------------+
                                                   ---->|  Report Engine   |
   2.4 GHz <--->|  BLE radio (HOGP / HIDS)    |---/      |  - notch decode  |
   antenna      |  + Battery + DIS services   |/        |  - debounce      |
                +-----------------------------+         |  - button matrix |
                                                        |  - LED policy    |
   Lever encoder  --(detent contacts / hall / pot)----->|                  |
   Buttons        --(GPIO matrix)--------------------->  +---------+--------+
   Hat            --(GPIO)                                        |
                                                                  v
                                          +----------------------------------------+
                                          | LED / lamp subsystem                   |
                                          |  - notch indicator bar (WS2812B)       |
                                          |  - RGB status LED                      |
                                          |  - warning lamps (ATS/door/EB/overspd) |
                                          |  - optional SPI OLED/TFT (speed/notch) |
                                          +----------------------------------------+
   Battery (Li-ion) -> PMIC/charger (nPM1300) -> 3V3 + fuel gauge -> Battery Service
```

## 3. Dual-mode transport arbitration

One report engine, two transports. Default policy: **USB takes priority when VBUS is present**;
otherwise BLE. (Simultaneous double-input is confusing for hosts, so mutual exclusion by default,
configurable.)

```
on boot:
    init report engine (encoder, buttons, LEDs)
    if VBUS present:
        enumerate USB HID; radio idle (lowest EMI/power) or advertise-on-demand
        mode = USB
    else:
        start BLE advertising (HOGP); mode = BLE; enter low-power
on VBUS rising edge:
    switch to USB; stop/park BLE link (optionally keep bond)
on VBUS falling edge (unplug):
    tear down USB; resume BLE advertising/reconnect
```

- **VBUS detect** via the nRF `USBREG`/`VBUSDETECT` (or a divider on a GPIO) is the mode signal.
- The **same `HID_REPORT_DESCRIPTOR`** feeds the USB HID class *and* the BLE HIDS Report Map — one
  source of truth. Only framing differs (USB endpoint vs GATT Report characteristic; mind the
  report-ID prefix noted in the protocol spec §2).
- Output reports (LEDs) arrive via USB SET_REPORT/interrupt-OUT or the BLE HID Output Report
  characteristic — both land in the same handler.

### BLE GATT services
- **HID Service `0x1812`** (HOGP): Report Map (= our descriptor), Input/Output/Feature Report
  characteristics, Protocol Mode, HID Information, HID Control Point. Appearance `0x03C4` (Gamepad).
- **Battery Service `0x180F`** — % from the fuel gauge.
- **Device Information Service `0x180A`** — manufacturer / model / FW rev.
- Security: LE Secure Connections + bonding; store bonds in Zephyr `settings`. Standard HOGP pairs
  with Windows/macOS/Linux/Android/iOS out of the box.

## 4. Input front-end

- **Lever:** the cleanest emulation matches the real hardware — **detented rotary with one contact
  set per notch** (or a gray-coded/absolute encoder, or a hall-effect absolute sensor). Firmware maps
  the decoded position straight to the §4 notch byte. A potentiometer is possible but needs
  hysteresis windows per notch and risks drift — prefer discrete detent sensing for crisp,
  transition-free output. Debounce a few ms; emit only on settled change.
- **Buttons / hat:** GPIO matrix (or direct GPIO if pin count allows), standard scan + debounce →
  the two button bytes and hat nibble.
- **Optional reverser:** 3-position switch → Z axis (`0x00`/`0x80`/`0xFF`) or two buttons.

## 5. LED / lamp subsystem

Implements protocol §5/§7. Two control sources merged by the LED policy: **local** (lever-driven
notch bar, connection/battery status) and **host** (output report) — host wins while present, with
fallback after a timeout.

- **Notch bar:** WS2812B strip driven by nRF **PWM + EasyDMA** (or I2S) for glitch-free timing
  without bit-banging. Brake side amber→red toward EB, power side green, neutral center pip.
- **Status RGB:** one addressable or PWM RGB LED.
- **Warning lamps + buzzer:** GPIO / PWM from output-report indicator bits.
- **Optional display:** SPI OLED (SSD1306/SH1107) or small TFT showing speed (output byte 5) + notch;
  this is the nRF5340-justifying feature if it grows into a full cab cluster.

## 6. Power budget (battery / BLE mode)

| Rail / load | Notes |
|---|---|
| nRF52840 BLE connected | ~ single-digit mA average at modest connection interval; µA in sleep |
| USB attached | bus-powered; LEDs can run full brightness |
| WS2812B strip | the dominant battery load — ~tens of mA **per LED** at full white. **Gate behind a load switch; default dimmed on battery; allow host/idle to sleep them** (protocol §5 flags). |
| Charger / PMIC | **nPM1300** (Li-ion charge + buck + fuel gauge + load switches) pairs well with nRF52840 and feeds the Battery Service. |

Rule: **addressable LEDs are the runtime killer, not the radio.** Keep them off/dim unless on USB or
explicitly enabled.

## 7. Suggested repo layout (when firmware lands)

```
benchbits-master-controller/
├── docs/                      # this research + spec (here now)
├── firmware/                  # nRF Connect SDK (Zephyr) app
│   ├── src/
│   │   ├── hid_descriptor.h   # the shared HID report descriptor (spec §1)
│   │   ├── report_engine.c    # encoder/button -> input report; output report -> LEDs
│   │   ├── transport_usb.c    # USB HID class glue
│   │   ├── transport_ble.c    # HOGP / HIDS glue
│   │   └── leds.c             # notch bar / status / lamps / display
│   ├── boards/                # custom board overlay/defconfig
│   └── prj.conf
├── hardware/                  # KiCad project (schematic + PCB)
└── host-tools/                # optional test/remap utilities
```

## 8. Build/runtime profiles

- `single-axis` (default) — lever on Y, Zuiki-compatible.
- `two-axis` — DGC-255-style brake/power split with `0xFF` transitions.
- `notch-count` — restrict emitted notches to a train class (4–7 power notches), set via feature
  report (spec §6) or a build-time Kconfig.
- `zuiki-compat-vidpid` (off by default) — advertise `0x33DD/0x0006` + USB no-report-ID offsets so
  SDL's dedicated ZUIKI driver binds; otherwise use our own VID/PID + generic HID parsing.
