# NotchDeck One — net plan (E73 pad → peripheral)

Pad-level reference for the captured schematic. Pad numbers are the
**E73-2G4M08S1C** module pads (per `lib/symbols/notchdeck:E73-2G4M08S1C`, confirmed against
Ebyte's pin table). Parts/refs follow [`PARTS.md`](PARTS.md). GPIO assignments are the captured Rev F
default; change the manifest, independent net contract, saved PCB and firmware
together when reassigning them.

> **Two design constraints baked in here:**
> 1. **AS5600 and MAX17048 share I²C address `0x36`** → they go on **two separate I²C buses**
>    (nRF52840 TWIM0 + TWIM1), not one shared bus.
> 2. **P0.18** remains nRESET; enable reset in UICR. No LF crystal is populated, so retain RC LFCLK. Rev E frees the former NFC/LFXO button pins; old Rev C/D GPIO button firmware does not apply to the split panel.

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
| 26 | P0.18/RESET | **nRESET** | RESET button + SWD; double-tap DFU requires the planned bootloader |
| 37 | SWDIO | **SWDIO** | SWD header |
| 39 | SWDCLK | **SWDCLK** | SWD header |
| 12 | P0.26 | **I2C0_SDA** | → handle mux + button panel (bus 0) |
| 14 | P0.06 | **I2C0_SCL** | → handle mux + button panel (bus 0) |
| 20 | P0.12 | **I2C1_SDA** | → MAX17048 (bus 1) |
| 22 | P0.07 | **I2C1_SCL** | → MAX17048 (bus 1) |
| 16 | P0.08 | **NC** | Former direct button/RGB input; intentionally unused in Rev E |
| 7 | P0.02/AIN0 | **REVERSER_AIN** | 3-pos reverser via resistor divider (ADC); or 2 GPIO |
| 28 | P0.15 | **FG_ALRT** | MAX17048 ALRT (open-drain in, pull-up) |
| 30 | P0.17 | **CHG_STAT** | MCP73832 STAT (open-drain in / LED) |
| 1 | P1.11 | **PANEL_INT** | Button-board IRQ_N, active-low open drain; R42 10k pull-up |
| 2 | P1.10 | **NC** | Former direct button/RGB input; intentionally unused in Rev E |
| 6 | P1.13 | **NC** | Former direct button/RGB input; intentionally unused in Rev E |
| 17 | P1.09 | **NC** | Former direct button/RGB input; intentionally unused in Rev E |
| 32 | P0.20 | **SOL1_PWM** | Q2 solenoid 1 input and J19.2 via series resistors |
| 33 | P0.13 | **SOL2_PWM** | Q3 solenoid 2 input and J19.3 via series resistors |
| 40 | P1.04 | BTN7 select | |
| 42 | P1.06 | BTN8 start | |
| 34 | P0.22 | **BUZZ_PWM** | Q4 active buzzer input and J19.4 via series resistors |
| 35 | P0.24 | **ACT_EN** | Electronic limiter enable; default low; also suspends charging |
| 36 | P1.00 | **ACT_nFAULT** | U13 thermal fault, active-low open drain; 10k pull-up |
| 38 | P1.02 | **NC** | Former direct button/RGB input; intentionally unused in Rev E |
| 41 | P0.09/NFC1 | **NC** | Former direct button/RGB input; intentionally unused in Rev E |
| 43 | P0.10/NFC2 | **NC** | Former direct button/RGB input; intentionally unused in Rev E |
| 11 | P0.00/XL1 | **NC** | Former direct button/RGB input; intentionally unused in Rev E |
| 13 | P0.01/XL2 | **NC** | Former direct button/RGB input; intentionally unused in Rev E |
| 3 | P0.03/AIN1 | **LEVER_S0** | coded-switch bit 0 (J5.2); GPIO in, ext 10k pull-up + RC debounce |
| 4 | P0.28/AIN4 | **LEVER_S1** | coded-switch bit 1 (J5.3); GPIO in, ext 10k pull-up + RC debounce |
| 8 | P0.29/AIN5 | **POWER_S0** | power Gray bit 0, J12.2, external pull-up + RC |
| 9 | P0.31/AIN7 | **POWER_S1** | power Gray bit 1, J12.3, external pull-up + RC |
| 10 | P0.30/AIN6 | **POWER_S2** | power Gray bit 2, J12.4, external pull-up + RC |
| 15 | P0.05/AIN3 | **LEVER_S3** | coded-switch bit 3 (J5.5); GPIO in, ext 10k pull-up + RC debounce |
| 18 | P0.04/AIN2 | **LEVER_S2** | coded-switch bit 2 (J5.4); GPIO in, ext 10k pull-up + RC debounce |

Rev E moves all 16 panel keys and RGB output to the button MCU. Main retains BTN7 (SW18 Select) and BTN8 (SW19 Start); future firmware must combine the panel's corresponding keys with these. Rev F reuses five former GPIOs for the actuator bank, leaving nine spare GPIOs intentionally NC. Gray handle inputs and magnetic buses remain independent and unchanged.

## Rev E button interconnect

Main J15 is a six-way 1mm FFC, using Molex 0151670213 Type A. Pin1 GND, pin2 3V3, pin3 I2C0_SDA, pin4 I2C0_SCL, pin5 PANEL_INT, pin6 USB_VBUS. Button J1 reverses the assignment: **main n → button 7−n**. R42 pulls IRQ up; U12 protects SDA/SCL and C44 bypasses 3V3. Existing R9/R10 are the only upstream I²C pull-ups. Use 100kHz; panel target address is 0x20. The main logic board remains the I²C controller.

Button U1 is STM32G030F6P6TR, scanning PA0–3 rows and PA4–7 columns with one isolation diode per key. PB6/PB7 AF6 provide I2C1; PC15 is open-drain IRQ; PA8 TIM1_CH1 AF2 drives local U8 AHCT and the RGB chain; PA12 ADC_IN16 measures divided VBUS. Key power is 3V3 including battery; RGB is USB-only. See [panel pin plan, cable ratings and firmware requirements](notchdeck-buttons/README.md). Both MCUs require separately programmed firmware; the Rev C/D overlay is not a Rev E firmware solution.

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
                                                            E73 VDD (19) + VDDH (23)   panel MCU / sensors
```

- **+3V3 rail:** AP2112K-3.3 LDO from `VSYS`. Feeds E73 `VDD`(19) **and** `VDDH`(23) tied
  together (normal-voltage mode — the module's internal DC/DC inductor handles REG1; `DCCH`(25)
  stays open). Decouple VDD/VDDH with 100 nF + 1 µF each, plus a 4.7–10 µF bulk on +3V3.
  AP2112K `EN` → tie to `VIN` (always-on); 1 µF in/out caps.
- **VBUS to the module:** USB-C `VBUS` → E73 `VBUS`(27). The nRF52840's internal USB regulator
  uses this, and firmware reads VBUS-present from it (no GPIO needed — `vbus_present()` in
  `main.c`).
- **Charger:** MCP73832-2-OT, 1-cell Li-ion. `PROG` resistor sets charge current (e.g. 2 kΩ ≈
  500 mA, 10 kΩ ≈ 100 mA — match the battery). Rev F places Q6 in R3's return so the actuator-enable interlock can float PROG and suspend charging. `STAT` → CHG_STAT (P0.17) + a charge LED.
- **Power-path:** Q1 AO3401A **drain (3) → BAT+, source (2) → VSYS**;
  its body diode conducts BAT+ toward VSYS and blocks VSYS-to-battery backfeed.
  Gate (1) → R4 100k → GND, and USB_VBUS → R5 1k → gate. D19 B5819W anode (2)
  → USB_VBUS, cathode (1) → VSYS. USB raises the gate and disconnects the battery
  from the load; R4 turns Q1 on when USB is absent.
- **Fuel gauge:** MAX17048 `VDD`(3) → BAT+ (it senses its own supply); `CELL`(2) → BAT+ per the ADI pin table (internally unconnected in MAX17048); `CTG`(1), `GND`(4), `EP`(9), `QSTRT`(6) → GND; `ALRT`(5) → FG_ALRT
  (P0.15) with pull-up. See the verified sources below.

## Rev F actuator branch

The sheet `Actuators` receives `BAT_RAW` from Power, a charger-enable link back to Power, and five MCU signals through root-sheet wires. `BAT_RAW` is J2 battery positive after **external protected-pack cutoff**; the older power diagram labels this BAT+. U13 TPS259531 IN3/4 connects to BAT_RAW; OUT5 feeds ACT_BAT. EN2 is default-low; ACT_EN also drives Q5 to open the charger PROG return through Q6; FLT6 goes to P1.00; GND8/EP9 are grounded. ILM7 sees R56+R58=1.33k; dVdt1 sees C48=100nF. The limit is nominally 1.54A, with a 1.3A operating bank budget.

J16/J17/J18 pin1 is ACT_BAT and pin2 is the protected low-side switched return. J19 pins1–4 are GND, SOL1_PWM_EXT, SOL2_PWM_EXT, BUZZ_PWM_EXT; these are **3.3V logic only** and follow the raw MCU commands independently of U13. See [actuator pinouts, battery protection boundaries and strike/hold requirements](notchdeck-one/ACTUATORS.md). There is no one-time fuse. The cell-side protection must handle dead shorts upstream of this branch.

## USB-C (J1, HRO TYPE-C-31-M-12)

- `VBUS` (A4/A9/B4/B9) → USB_VBUS net.
- `CC1`, `CC2` → 5.1 kΩ each to GND (UFP/sink — device role).
- `D+` (A6/B6 tied) → USB_DP → E73 pad 31; `D−` (A7/B7 tied) → USB_DM → E73 pad 29.
- `SBU1/SBU2` → NC. `Shield` → GND (optionally via a 1 MΩ ∥ 4.7 nF / bead).
- **ESD:** add a low-cap TVS array on D+/D−/VBUS (e.g. USBLC6-2 / SRV05 class) near the
  connector. (U7 is populated.)

## I²C buses and independent handle inputs (Rev E)

- **TWIM0:** SDA=P0.26 (pad12), SCL=P0.06 (pad14), R9/R10 4.7k pull-ups. Button MCU target 0x20 shares this upstream bus.
  U9 TCA9543APWR at 0x70 isolates two AS5600 address-0x36 channels. A0/A1 are
  grounded, RESET follows nRESET with R39 10k pull-up; INT0/INT1 have 10k pull-ups
  and INT output is deliberately unconnected. C38 bypasses its 3V3 supply.
- **Channel 0:** POWER_MAG_SDA/SCL, R27/R28 4.7k pull-ups, J10 power/combined
  sensor. Onboard U5 connects through R37/R38 (0Ω0603). **Remove BOTH links before
  attaching an external AS5600 to J10.** U5 remains powered but isolated.
- **Channel 1:** BRAKE_MAG_SDA/SCL, R29/R30 4.7k pull-ups, J11 external brake sensor.
- **J10/J11:** pin1=3V3, pin2=GND, pin3=SDA, pin4=SCL. U10/U11 USBLC6-2SC6
  protect data lines; C39/C40 bypass the ports. Use 3.3V sensors with local
  decoupling, short internal harnesses (≤20cm target), 100kHz and verify rise times.
  Do not hot-plug or add harness pull-ups without recalculating bus loading.
- **U5:** VDD5V(1)+VDD3V3(2) to3V3, C11/C12 local decoupling, DIR(8) and GND(4)
  grounded, OUT(3)/PGO(5) deliberately NC. Diametric magnet above package center.
- **TWIM1:** MAX17048 U4 at 0x36, SDA=P0.12 (pad20), SCL=P0.07 (pad22).
  It remains physically independent of both magnetic handles.

Firmware enables only one U9 channel at a time (write 0x01 or 0x02), reads the
sensor, then deselects both (0x00). Never select 0x03: identical sensor addresses
would collide. A stuck downstream bus may still require reset or power cycling;
this is an internal harness interface, not an industrial long-cable link.

Rev E retains the Rev D Gray inputs on J5 (six pins) and J12 (five pins). Pin1=GND, then
S0 upward; the final pin is 3V3 and is left unwired in passive contact harnesses.
This consolidates seven Rev C connectors without changing any MCU assignments:

| Role | Connectors | Nets / GPIOs | Input circuits |
|---|---|---|---|
| Brake or combined | J5.2–J5.5, S0–S3 | LEVER_S0–S3; P0.03/P0.28/P0.04/P0.05 | R14–17 10k pull-ups, R18–21 1k series, C14–17 100nF |
| Power | J12.2–J12.4, S0–S2 | POWER_S0–S2; P0.29/P0.31/P0.30 | R31–33 10k pull-ups, R34–36 1k series, C41–43 100nF |

Use contacts rated for microloads around **3.3V / 0.33mA**. A high-current switch
may not reliably conduct such a small current. RC time constants are about1.1ms
on release and0.1ms on closure; firmware adds16ms stability filtering. Open=1,
closed=0. The new cam maps reserve all-open as invalid and **supersede the earlier
Rev B table**. See [handle guide](../docs/06-handle-interfaces.md) for every pattern,
calibration, profile selection and fault behavior. External cams/switches/sensor
boards and harnesses are separate from the main PCB assembly BOM.

## Programming / reset (see `../docs/05-firmware-update.md`)

- **Main SWD**: SWDIO(37), SWDCLK(39), nRESET(26/P0.18), +3V3, GND at
  J3 keyed 2×5 header and bare J4 TC2030 contacts; use only one probe connection.
- **RESET SW17** → nRESET (P0.18) to GND; 100nF on nRESET. Double-tap DFU
  requires a compatible bootloader, which is not integrated yet.
- **Panel SWD** is separate at bare J2 TC2030. No panel USB or I²C updater exists.
- USB-C UF2 mass-storage is the proposed main-board user-upgrade path; see
  [update status](../docs/05-firmware-update.md) before using build artifacts.

## Decoupling & misc

- Per-supply: 100 nF close to each VDD/VDDH pad; 1 µF + 4.7–10 µF bulk on +3V3.
- **On the button board**, RGB array D1–D16: VDD → USB_VBUS, GND → GND. It is **USB-powered only**.
  U8 SN74AHCT1G125DBVR: VCC→VBUS, /OE→GND, input→RGB_PWM (STM32 PA8), output→R11 330Ω→D1 DIN.
  DOUT chains to the next DIN; D16 DOUT is NC. R26 100k holds DIN low during MCU reset.
  C20 is the buffer bypass; C21–C36 are 100nF per LED. C13 is 1uF bulk (10V or higher).
  Firmware must hold DIN low without USB and cap brightness to the source-current budget.
- Reverser J9: pin 1→3V3, pin 2→external SPDT common, pin 3→GND. The switch is
  center-off. R23/R24 (100k each) bias common to 1.65V in neutral. R25 (1k) feeds
  REVERSER_AIN; C37 (100nF) filters at the ADC. Forward/reverse select 3.3V/0V.
- D17/R12 show 3V3 power; D18/R13 run from 3V3 to CHG_STAT (active-low). R22 100k
  pulls CHG_STAT up to 3V3. U3 must be the open-drain MCP73832 variant.
- LFXO note: P0.00/P0.01 are now intentionally NC; no crystal is populated. Keep internal RC LFCLK unless hardware and firmware are deliberately revised together.

## Support parts (now specified in PARTS.md)

The power-path P-FET (AO3401A) + Schottky (B5819W), USB ESD (USBLC6-2SC6), reset button, SWD
header, populated WS2812 level shifter (74AHCT1G125), and the pull-up/gate/decoupling passives are
all listed in [`PARTS.md`](PARTS.md), with exact catalog codes and footprints.
Some parts use project-local symbols/footprints and lack dedicated 3D models;
see [attributions](lib/ATTRIBUTIONS.md). Stock observations are dated in the BOM files.

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

Run `make verify` from `hardware/` for a strict net and ERC check.
The expected endpoint sets live in `scripts/notchdeck-netcheck.py`, independently
of the wiring manifest. See `README.md` for remaining pre-fabrication checks.
