# NotchDeck One — net plan (E73 pad → peripheral)

Connection plan to make the KiCad schematic capture mechanical. Pad numbers are the
**E73-2G4M08S1C** module pads (per `lib/symbols/notchdeck:E73-2G4M08S1C`, confirmed against
Ebyte's pin table). Parts/refs follow [`PARTS.md`](PARTS.md). GPIO assignments are a proposed
default — adjust freely in capture, they're all software-defined.

> **Two design constraints baked in here:**
> 1. **AS5600 and MAX17048 share I²C address `0x36`** → they go on **two separate I²C buses**
>    (nRF52840 TWIM0 + TWIM1), not one shared bus.
> 2. **NFC pins** P0.09/P0.10 are reused as GPIO → firmware must set `CONFIG_NFCT_PINS_AS_GPIO`.
>    **P0.18** is used as `nRESET` → enable reset in UICR (Zephyr default). **P0.00/P0.01** are
>    used as GPIO → LFCLK runs from the internal RC (no 32.768 kHz crystal); see LFXO note.

## Full E73 pad assignment

| Pad | E73 signal | Net / function | Notes |
|---|---|---|---|
| 19 | VDD | **+3V3** | main supply |
| 23 | VDDH | **+3V3** | tie to VDD (normal-voltage mode) |
| 25 | DCCH | **NC** | high-voltage DC/DC node — leave open when VDD=VDDH=3V3 |
| 27 | VBUS | **USB_VBUS (5V)** | feeds nRF USB regulator + on-chip VBUS-detect (no GPIO needed) |
| 5, 21, 24 | GND | **GND** | |
| 29 | USB_D− | **USB_DM** | to USB-C D− pair |
| 31 | USB_D+ | **USB_DP** | to USB-C D+ pair |
| 26 | P0.18/RESET | **nRESET** | RESET button + SWD; double-tap → DFU (see firmware-update doc) |
| 37 | SWDIO | **SWDIO** | SWD header |
| 39 | SWDCLK | **SWDCLK** | SWD header |
| 12 | P0.26 | **I2C0_SDA** | → AS5600 (bus 0) |
| 14 | P0.06 | **I2C0_SCL** | → AS5600 (bus 0) |
| 20 | P0.12 | **I2C1_SDA** | → MAX17048 (bus 1) |
| 22 | P0.07 | **I2C1_SCL** | → MAX17048 (bus 1) |
| 16 | P0.08 | **WS2812_DIN** | LED data (SPIM MOSI / PWM+DMA) |
| 7 | P0.02/AIN0 | **REVERSER_AIN** | 3-pos reverser via resistor divider (ADC); or 2 GPIO |
| 28 | P0.15 | **FG_ALRT** | MAX17048 ALRT (open-drain in, pull-up) |
| 30 | P0.17 | **CHG_STAT** | MCP73832 STAT (open-drain in / LED) |
| 1 | P1.11 | BTN1 horn-hi (A) | momentary, active-low, internal pull-up |
| 2 | P1.10 | BTN2 horn-lo/bell (B) | |
| 6 | P1.13 | BTN3 door-close (X) | |
| 17 | P1.09 | BTN4 door-open (Y) | |
| 32 | P0.20 | BTN5 ATS-reset (L) | |
| 33 | P0.13 | BTN6 cab/view (R) | |
| 40 | P1.04 | BTN7 select | |
| 42 | P1.06 | BTN8 start | |
| 34 | P0.22 | HAT_UP | nav/D-pad |
| 35 | P0.24 | HAT_DOWN | |
| 36 | P1.00 | HAT_LEFT | |
| 38 | P1.02 | HAT_RIGHT | |
| 41 | P0.09/NFC1 | BTN9 pantograph | NFC→GPIO (UICR) |
| 43 | P0.10/NFC2 | BTN10 headlight | NFC→GPIO (UICR) |
| 11 | P0.00/XL1 | BTN11 (or LFXO) | GPIO if no 32 kHz xtal |
| 13 | P0.01/XL2 | BTN12 (or LFXO) | GPIO if no 32 kHz xtal |
| 3 | P0.03/AIN1 | **LEVER_S0** | coded-switch bit 0 (J5); GPIO in, ext 10k pull-up + RC debounce |
| 4 | P0.28/AIN4 | **LEVER_S1** | coded-switch bit 1 (J6); GPIO in, ext 10k pull-up + RC debounce |
| 8 | P0.29/AIN5 | spare (analog) | expansion |
| 9 | P0.31/AIN7 | spare (analog) | expansion |
| 10 | P0.30/AIN6 | spare (analog) | expansion |
| 15 | P0.05/AIN3 | **LEVER_S3** | coded-switch bit 3 (J8); GPIO in, ext 10k pull-up + RC debounce |
| 18 | P0.04/AIN2 | **LEVER_S2** | coded-switch bit 2 (J7); GPIO in, ext 10k pull-up + RC debounce |

Budget: 12 momentary buttons + 4-way hat (16 HID buttons + hat), 2× I²C, WS2812, reverser
ADC, 2 status inputs, **4-bit coded-switch lever input** (LEVER_S0–S3 on P0.03/P0.28/P0.04/P0.05)
— with **3 spare analog GPIOs** left (P0.29/P0.31/P0.30) for expansion. The coded-switch bits
are dedicated (not shared with the AS5600 I²C0), so both lever front-ends can be populated at once.

## Power architecture

```
USB-C VBUS (5V) ──[TVS/ESD]──┬─────────────► E73 VBUS (pad 27)   ; USB regulator + VBUS-detect
                             │
                             ├─► MCP73832 VDD (charge in)
                             │      MCP73832 VBAT ─► BAT+ (Li-ion 1S)   ; PROG R sets I_chg
                             │      MCP73832 STAT ─► CHG_STAT (P0.17) + LED
                             │
                             └─► [power-path OR-ing] ─► VSYS ─► AP2112K-3.3 ─► +3V3
   BAT+ ───────────────────────► [power-path OR-ing] ─┘                        │
                                                                    ┌──────────┴───────────┐
                                                            E73 VDD (19) + VDDH (23)   I²C/LED/etc.
```

- **+3V3 rail:** AP2112K-3.3 LDO from `VSYS`. Feeds E73 `VDD`(19) **and** `VDDH`(23) tied
  together (normal-voltage mode — the module's internal DC/DC inductor handles REG1; `DCCH`(25)
  stays open). Decouple VDD/VDDH with 100 nF + 1 µF each, plus a 4.7–10 µF bulk on +3V3.
  AP2112K `EN` → tie to `VIN` (always-on); 1 µF in/out caps.
- **VBUS to the module:** USB-C `VBUS` → E73 `VBUS`(27). The nRF52840's internal USB regulator
  uses this, and firmware reads VBUS-present from it (no GPIO needed — `vbus_present()` in
  `main.c`).
- **Charger:** MCP73832-2-OT, 1-cell Li-ion. `PROG` resistor sets charge current (e.g. 2 kΩ ≈
  500 mA, 10 kΩ ≈ 100 mA — match the battery). `STAT` → CHG_STAT (P0.17) + a charge LED.
- **Power-path:** Q1 AO3401A **drain (3) → BAT+, source (2) → VSYS**;
  its body diode conducts BAT+ toward VSYS and blocks VSYS-to-battery backfeed.
  Gate (1) → R4 100k → GND, and USB_VBUS → R5 1k → gate. D19 B5819W anode (2)
  → USB_VBUS, cathode (1) → VSYS. USB raises the gate and disconnects the battery
  from the load; R4 turns Q1 on when USB is absent.
- **Fuel gauge:** MAX17048 `VDD`(3) → BAT+ (it senses its own supply); `CELL`(2) → BAT+ per the ADI pin table (internally unconnected in MAX17048); `CTG`(1), `GND`(4), `EP`(9), `QSTRT`(6) → GND; `ALRT`(5) → FG_ALRT
  (P0.15) with pull-up. See the verified sources below.

## USB-C (J1, HRO TYPE-C-31-M-12)

- `VBUS` (A4/A9/B4/B9) → USB_VBUS net.
- `CC1`, `CC2` → 5.1 kΩ each to GND (UFP/sink — device role).
- `D+` (A6/B6 tied) → USB_DP → E73 pad 31; `D−` (A7/B7 tied) → USB_DM → E73 pad 29.
- `SBU1/SBU2` → NC. `Shield` → GND (optionally via a 1 MΩ ∥ 4.7 nF / bead).
- **ESD:** add a low-cap TVS array on D+/D−/VBUS (e.g. USBLC6-2 / SRV05 class) near the
  connector. (U7 is populated.)

## I²C buses (two, to dodge the 0x36 collision)

- **TWIM0 — AS5600** (U5): SDA=P0.26(12), SCL=P0.06(14), 4.7 kΩ pull-ups to +3V3.
  - VDD5V(1)+VDD3V3(2) → +3V3 (3.3 V mode: tie both, 100 nF + 1 µF decoupling).
  - OUT(3)=NC, PGO(5)=NC, DIR(8)→GND (CW = increasing), SDA(6)/SCL(7)→bus, GND(4)→GND.
  - Mechanical: diametric magnet centered over the package on the lever shaft.
- **TWIM1 — MAX17048** (U4): SDA=P0.12(20), SCL=P0.07(22), 4.7 kΩ pull-ups to +3V3.

## Lever sensing — two front-ends (interchangeable, or populate both)

The lever is a **discrete-detent** input (15 positions: EB, B8–B1, N, P1–P5), so this is
"which detent am I in," not a precision-angle problem. The choice is **contained entirely in
firmware `lever.c`** (`lever_get_notch()` returns a notch index); the notch→HID-byte table and
everything downstream are sensor-agnostic. Two options — and because the coded-switch bits are on
dedicated GPIO, both can be populated at once (firmware picks, or cross-checks one against the other):

### Option 1 — AS5600 magnetic angle (default)

Per the I²C section above. **Why drift isn't a concern here:** the AS5600 reports the *direction*
of a diametric magnet's field (ratiometric `atan2`), so magnet temp-coefficient (~−0.12 %/°C) and
aging barely shift the angle; on-chip temp compensation handles the silicon. Absolute accuracy is
~±1–2° (it's a budget part) against **~6–12° notch spacing**, and the mechanical detent **parks
the lever at each band's center**, far from the decision thresholds — so quantization is robust
(firmware adds hysteresis). It's *absolute* (no power-on homing). Real risks are mechanical, not
drift: magnet centering, air-gap (0.5–3 mm), shaft runout. Optional upgrade if you ever want more
margin: MT6701 (14-bit, ~same cost, JLCPCB-stocked).

### Option 2 — 4 binary/Gray coded switches (deterministic, authentic)

**4 switches** encode the notch position — either an on-board cam on the shaft, or (the mascon
case) a coded-switch assembly in the handle **wired in on a harness**. **Zero drift, zero
calibration, decodes as pure GPIO** — and it's how the real Densha de GO! / DGC-255 controllers
work (research doc §4). Use **Gray code** so exactly one bit changes per detent transition (no
transient-invalid codes); an unused/unknown code → hold last valid. Binary (BCD) coded switches
also work — de-Gray is just skipped in firmware.

This front-end is **on-board and dedicated** (its own 4 GPIO + connectors + debounce), so it can be
populated **alongside** the AS5600 (Option 1), not only as a swap — see "coexists" below.

4-bit Gray map (S3 S2 S1 S0), one bit changes between physically adjacent notches:

| Notch | code | | Notch | code |
|---|---|---|---|---|
| EB | 0000 | | B1 | 1100 |
| B8 | 0001 | | N  | 1101 |
| B7 | 0011 | | P1 | 1111 |
| B6 | 0010 | | P2 | 1110 |
| B5 | 0110 | | P3 | 1010 |
| B4 | 0111 | | P4 | 1011 |
| B3 | 0101 | | P5 | 1001 |
| B2 | 0100 | | *(unused)* | 1000 |

For an **on-board cam** (instead of the mascon harness) driving the same 4 nets, pick a switch
element:
- **Hall (recommended): 4× DRV5032FB** (SOT-23, contactless, no wear) + small magnet lobes on the
  cam. SMD-assemblable at JLCPCB.
- **Mechanical: 4× snap-action** (Omron SS-5GL / D2F-class, cam-lever actuated) — cheapest, most
  authentic *feel*, but contacts wear (~10⁵–10⁶ cycles) and are usually hand-mounted.

**GPIO — dedicated (coexists with the AS5600 on I²C0):** the 4 bits take 4 spare analog GPIO so
neither front-end blocks the other. `LEVER_S0`=P0.03(3), `LEVER_S1`=P0.28(4), `LEVER_S2`=P0.04(18),
`LEVER_S3`=P0.05(15). Active-low: each switch shorts its bit line to GND; open = high. MAX17048
stays on TWIM1, AS5600 on TWIM0. (This supersedes the earlier "reuse the freed I²C0 pins" plan,
which only worked as an AS5600 *swap*.)

**Connectors + hardware debounce (mascon harness):** the coded switches live in the handle and come
in on **one 2-pin JST-PH per bit** — `J5`=S0, `J6`=S1, `J7`=S2, `J8`=S3 (pin 1 = bit line, pin 2 =
GND). Each bit has an on-board **RC debounce**: 10 kΩ pull-up to +3V3, 1 kΩ series into the GPIO,
100 nF to GND → τ ≈ 1.1 ms release / 0.1 ms press. The series R also limits the cap-discharge
current and adds ESD margin on the cable; firmware still applies a few-ms software debounce on top.
Parts: `R14–R17` (pull-ups), `R18–R21` (series), `C14–C17` (caps) on the Lever sheet.

**Recommendation:** ship Option 1 (AS5600) for the simplest BOM. Populate the coded-switch input
(J5–J8) when you want calibration-free determinism / maximum authenticity or must interface a real
mascon's coded switch — and since its pins are dedicated, you can stuff both and let firmware choose.

## Programming / reset (see `../docs/05-firmware-update.md`)

- **SWD header**: SWDIO(37), SWDCLK(39), nRESET(26/P0.18), +3V3, GND. Use a Tag-Connect
  TC2030-IDC footprint or a 2×5 / 1×6 0.05″ header for factory bootloader install + debug.
- **RESET button** → nRESET (P0.18) to GND, with the bootloader's **double-tap-to-DFU** (no
  separate BOOT pin needed). 100 nF on nRESET.
- USB-C is the user-upgrade path (UF2 mass-storage). Details in the firmware-update doc.

## Decoupling & misc

- Per-supply: 100 nF close to each VDD/VDDH pad; 1 µF + 4.7–10 µF bulk on +3V3.
- RGB array D1–D16: VDD → USB_VBUS, GND → GND. It is **USB-powered only**.
  U8 SN74AHCT1G125DBVR: VCC→VBUS, /OE→GND, input→WS2812_DIN, output→R11 330Ω→D1 DIN.
  DOUT chains to the next DIN; D16 DOUT is NC. R26 100k holds DIN low during MCU reset.
  C20 is the buffer bypass; C21–C36 are 100nF per LED. C13 is 1uF bulk (10V or higher).
  Firmware must hold DIN low without USB and cap brightness to the source-current budget.
- Reverser J9: pin 1→3V3, pin 2→external SPDT common, pin 3→GND. The switch is
  center-off. R23/R24 (100k each) bias common to 1.65V in neutral. R25 (1k) feeds
  REVERSER_AIN; C37 (100nF) filters at the ADC. Forward/reverse select 3.3V/0V.
- D17/R12 show 3V3 power; D18/R13 run from 3V3 to CHG_STAT (active-low). R22 100k
  pulls CHG_STAT up to 3V3. U3 must be the open-drain MCP73832 variant.
- LFXO note: P0.00/P0.01 are used as GPIO → LFCLK = internal RC (fine for BLE, calibrated). To
  fit a 32.768 kHz crystal instead (lower sleep current / tighter timing), reclaim P0.00/P0.01
  and drop BTN11/BTN12 (or move buttons to a scan matrix).

## Support parts (now specified in PARTS.md)

The power-path P-FET (AO3401A) + Schottky (B5819W), USB ESD (USBLC6-2SC6), reset button, SWD
header, populated WS2812 level shifter (74AHCT1G125), and the pull-up/gate/decoupling passives are
all in [`PARTS.md`](PARTS.md) → "Power-path, protection & programming". All are stdlib KiCad
symbols with shipped 3D and are stocked at JLCPCB (AO3401A + B5819W are basic parts).

## Verified capture references (2026-10-02)

- [Microchip AN1149](https://ww1.microchip.com/downloads/en/AppNotes/01149c.pdf),
  load-sharing PMOS and Schottky topology.
- [Microchip MCP73831/2 datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/20001984g.pdf),
  STAT behavior: MCP73831 drives high at charge completion; MCP73832 releases its open drain.
- [ADI MAX17048/49 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max17048-max17049.pdf),
  pin table: CELL and VDD to the positive battery terminal; CTG/QSTRT/EP to ground.
- [TI SN74AHCT1G125](https://www.ti.com/lit/ds/symlink/sn74ahct1g125.pdf),
  4.5–5.5V supply and TTL-compatible input threshold.
- [ams AS5600 datasheet](https://look.ams-osram.com/m/7059eac7531a86fd/original/AS5600-DS000365.pdf),
  3.3V supply mode and sensor pinout.

Run `make verify-notchdeck-one` from `hardware/` for a strict net and ERC check.
The expected endpoint sets live in `scripts/notchdeck-netcheck.py`, independently
of the wiring manifest. See `README.md` for remaining pre-fabrication checks.
