# NotchDeck Buttons — Rev E

An independent 4×4 key/RGB assembly driven by **STM32G030F6P6TR (C529330)** from owned JLCPCB stock. It connects to the logic board through a six-conductor FFC. The schematic is wired and checked; the 86×120mm two-layer PCB is an **unrouted floorplan**. Panel firmware and main-controller integration are not implemented yet.

## Connector and cable

Both connectors are **JUSHUO AFA07-S06FCA-00 / C262712**, 6 contacts, 1mm pitch, bottom contact, nominal 0.30mm FFC ends. Use **Molex 0151670213**, DigiKey **WM13121-ND**, Type A same-side exposed contacts, 177.8mm long. Five cables are listed in the [system BOM](../system-bom.csv); the assembly BOMs contain only the PCB connectors.

Identical bottom-contact connectors at opposite ends of a Type A cable reverse connector numbering. The schematic compensates deliberately: **main pin n connects to button pin 7−n**. Insert exposed contacts toward each PCB; power off for insertion/removal. This is an internal enclosure interconnect.

| Main J15 | Signal | Button J1 |
|---:|---|---:|
| 1 | GND | 6 |
| 2 | 3V3 — MCU and keys, including battery operation | 5 |
| 3 | SDA — I2C0 on main, I2C1 PB7 AF6 on panel | 4 |
| 4 | SCL — I2C0 on main, I2C1 PB6 AF6 on panel | 3 |
| 5 | IRQ_N — PC15 open drain to E73 P1.11 | 2 |
| 6 | USB_VBUS — RGB only | 1 |

The [JUSHUO family specification](https://datasheet.lcsc.com/datasheet/pdf/8c3225c8bd3c5aba9addae56ddc79a88.pdf?productCode=C262714) explicitly covers AFA07-S**FCA-00 and rates contacts at 0.5A. The [Molex family specification](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/151/15167/PS-15167-001-001.pdf) rates the cable at 0.8A per conductor at 23°C; the connector limits this link. Target **≤250mA total panel return current**, including 3V3 and LED loads, subject to the main USB/charger budget. This is a firmware/current-budget requirement, not an implemented hardware limit. Full-white unrestricted LEDs are not supported by this budget.

Pitch, contact side and nominal end thickness agree with the drawings. JUSHUO specifies 0.30±0.03mm cable thickness; Molex guarantees 0.30±0.05mm ends, so worst-case tolerance compatibility is **not established**. Validate insertion, retention and contact resistance on samples, or obtain supplier approval before production. Confirm end-to-end pin numbering with a continuity check before first power. Stock: JLCPCB 31,746 available connectors; DigiKey 139 cables on 2026-10-03, before reservations/attrition.

## MCU pin plan

| U1 pad | Selected GPIO/function | Net |
|---:|---|---|
| 1 | PB7 / I2C1_SDA AF6 | SDA |
| 3 | PC15 open drain | IRQ_N |
| 4 / 5 | VDD / VSS | 3V3 / GND |
| 6 | NRST | 10k pull-up, 100nF, J2 reset |
| 7–10 | PA0–PA3 | ROW0–ROW3 |
| 11–14 | PA4–PA7 | COL0–COL3, external 10k pull-ups |
| 15 | PA8 / TIM1_CH1 AF2 | RGB_PWM → AHCT U8 |
| 17 | PA12 / ADC_IN16 | VBUS_SENSE, 100k/100k divider and 100nF |
| 18 / 19 | PA13 / PA14 | SWDIO / SWCLK |
| 20 | PB6 / I2C1_SCL AF6 | SCL |

Pads 2 and 16 are intentionally unused. On internally bonded pads, leave the unused PB8, PB3/PB4/PB5, PB0/PB1/PB2, PA10 and PA15 aliases analog/high impedance. SWD must remain enabled, and boot option bytes must select user flash without sacrificing PA14 SWCLK. Use HSI/PLL; no crystal or external flash is required. Evidence: [ST DS12991](https://www.st.com/resource/en/datasheet/stm32g030f6.pdf), pin/alternate-function and package tables. Stock identity/footprint checked against the selected TSSOP-20 ordering code.

Each key has a 1N4148W: column → switch → diode anode → cathode → row. Pull one row low, leave the other rows high impedance, wait for settling, then read four active-low columns. This orientation supports simultaneous keys without ghost paths. SW1–SW12 retain BTN1–BTN12; SW13–SW16 are Up, Down, Left, Right. Physical button pitch is 19mm.

The local AHCT buffer and RGB chain use USB_VBUS. The MCU uses 3V3, so key input works on battery. Use the VBUS divider as an ADC input, not a digital threshold. Hold RGB_PWM low whenever USB is absent and at reset; R26 provides the default pull-down. J2 is bare TC2030-NL SWD access, excluded from assembly: 1=3V3, 2=SWDIO, 3=NRST, 4=SWCLK, 5=GND, 6=NC. Program the MCU via SWD; there is no panel USB connector or implemented I²C bootloader.

## Firmware interface to implement

Use I²C target address **0x20** on the upstream main I2C0 bus at 100kHz. Main R9/R10 provide its only pull-ups. The handle mux remains 0x70 and selected magnetic sensor 0x36; the fuel gauge remains on separate I2C1. Start with a 1kHz complete matrix scan, roughly 10ms stable-state debounce, and an atomic 16-bit pressed-key bitmap with a sequence counter. Assert IRQ until the latest stable state is acknowledged, avoiding a lost update when a key changes during a read. Retain a periodic poll as a fallback.

Define a versioned register/packet contract before implementing either side. Include LED frame/brightness commands and status (VBUS, firmware version, faults); use timer/DMA so RGB generation does not block I²C service. On communications loss, main releases panel keys and panel turns LEDs off. OR main SW18/SW19 into Select/Start so either physical location works. Define low-power scanning/wake behavior for BLE use and test rollover, debounce, reset during transfer, cable disconnect, brownout and USB removal. No wire protocol or executable panel firmware is claimed by this hardware revision.

## Checks

`make -C hardware verify` verifies both assemblies. Panel audit covers 85 components, 56 nets, 235 endpoints, four intentional NCs and every FFC conductor; native ERC has zero errors/warnings. BOM/CPL contains 84 parts (13 catalog codes). See [floorplan](FLOORPLAN.md) for placement/routing status.
