# BOM & JLCPCB Sourcing — NotchDeck

JLCPCB/LCSC availability of the major functional blocks (checked May 2026). All Nordic + most
support parts are **Extended** (one-time ~$3 feeder fee each; verify in-stock at order time). Goal:
confirm the whole design is assemblable at JLCPCB, with cheap, well-stocked fallbacks where a
preferred part is thin on stock.

## MCU / radio — see [`03-hardware-and-firmware-architecture.md`](03-hardware-and-firmware-architecture.md)

- **Prototype:** Ebyte **E73-2G4M08S1C** onboard ceramic antenna — `C356849` (~240, $7.19).
- u.FL external-antenna variant: E73-2G4M08S1**CX** — `C2764963` (~399, $5.96).
- Cost-down bare chip: nRF52840-QIAA-R — `C190794` (~1,178, $3.80).

## Power path

A train controller mostly sits on a desk, so USB-powered is the common case; battery + BLE is the
roaming case. Two ways to build the power path:

### Option A — integrated PMIC (cleanest, fewest parts)
| Function | Part | LCSC | Pkg | Stock | ~Unit | Notes |
|---|---|---|---|---|---|---|
| Charger + buck + fuel-gauge + load switches | **nPM1300-QEAA** | `C7501206` | QFN-32 | ~168 | $4.22 | Nordic PMIC; pairs natively with nRF52840, feeds Battery Service. **Stock is thin (~168)** — buy ahead or keep Option B as backup. |

### Option B — discrete (cheap, deep stock, drop-in fallback)
| Function | Part | LCSC | Pkg | Stock | ~Unit | Notes |
|---|---|---|---|---|---|---|
| Li-ion charger | **MCP73831T-2ACI/OT** | `C424093` | SOT-23-5 | ~2,727 | $0.87 | simple 1-cell linear charger |
| or charger | TP4056 | `C16581` (PREF) | ESOP-8 | ~64,751 | $0.16 | ubiquitous, dirt cheap |
| Fuel gauge | **MAX17048G+T10** | `C2682616` | DFN-8 | ~4,403 | $2.32 | battery % for Battery Service |
| 3V3 LDO | **AP2112K-3.3** | `C23380830` | SOT-23-5 | ~52,879 | $0.08 | 600 mA, cheap, deep stock |
| or LDO | TLV75533 | `C404027` | SOT-23-5 | ~30,147 | $0.19 | TI alt |

> Recommendation: **start with Option B** (deep stock, ~$1 less risk) for the first board; migrate to
> the nPM1300 later if its power management / fuel-gauge integration earns its keep. The E73 module
> already contains the nRF DC-DC inductors, so a plain 3V3 LDO from USB or battery is sufficient.

## USB-C connector

| Part | LCSC | Stock | ~Unit | Notes |
|---|---|---|---|---|
| **TYPE-C 16PIN 2MD(073)** | `C2765186` | ~735,053 | $0.058 | 16-pin power+USB2.0 receptacle, huge stock — the default |
| TYPE-C-31-M-12 | `C165948` | ~336,394 | $0.16 | the other very common 16-pin part |

16-pin (USB 2.0 + CC) is all we need — FS USB + power. Add the two **CC pull-downs (5.1 kΩ)** for
sink detection.

## Lever position sensor

The lever is the signature input — pick by desired feel/reliability:

| Approach | Part | LCSC | Stock | ~Unit | Notes |
|---|---|---|---|---|---|
| **Magnetic absolute (recommended)** | **AS5600** | `C499458` | ~36,593 | $1.04 | 12-bit angle over I²C/PWM from a diametric magnet; no contacts to wear, clean per-notch quantization in firmware |
| Linear hall | SS49E (SS49EUA) | `C23083852` | ~1,240 | $0.15 | analog field → ADC; cheap, needs calibration |
| Mechanical encoder (incremental) | EC11-type | `C2833295` | ~4,819 | $0.014 | detented rotary; incremental (count, not absolute) — needs homing |
| Mechanical encoder (Bourns) | PEC11R-4215F-S0024 | `C143790` | ~797 | $2.36 | quality detented encoder, low stock |

The **AS5600 + a custom detented shaft** gives the truest "snap to notch" behavior with no wear and a
clean mapping straight to the §4 notch byte. Note: the *detents themselves* (the mechanical feel of
B8…EB / P1…P5) come from a custom shaft/cam — that's a mechanical-design item, not an LCSC part.

## Buttons / hat

Standard tactile switches + a 4/5-way nav for the hat. Many cheap options (e.g. SKHHxx tactiles,
SMD nav switches) — not pinned here; any in-stock tactile works. Cab buttons (horn/door/etc.) can be
larger panel-mount momentary switches sourced separately.

## LEDs / lamps — see protocol [`02-emulation-protocol-spec.md`](02-emulation-protocol-spec.md) §7

| Function | Part | LCSC | Stock | ~Unit | Notes |
|---|---|---|---|---|---|
| Addressable RGB (notch bar / status) | **WS2812B-2020** | `C965555` | ~360,285 | $0.077 | 2×2 mm; compact for a notch bar |
| or 5050 RGB | XL-5050RGBC-2812B | `C2843785` | ~928,000 | $0.041 | bigger, brightest, cheapest |
| or SK6812 MINI-E | `C5149201` | ~161,209 | $0.079 | WS2812-compatible, reverse-mount options |
| Warning lamps | discrete 0603/0805 LEDs | — | huge | <$0.01 | ATS/door/EB/overspeed indicators |

All driven by nRF **PWM + EasyDMA** (WS2812 timing) / GPIO. Gate the strip behind a load switch and
default-dim on battery (LEDs dominate the battery budget, not the radio).

## Optional cab display

SPI OLED (SSD1306/SH1107) or small TFT for speed + notch readout, fed by the output/feature report.
Common SSD1306 modules and bare driver ICs are stocked at JLCPCB; spec when/if the display feature is
committed (and revisit nRF5340 if it grows into a full graphical cluster).

## Verdict

**Every functional block is buildable at JLCPCB today.** Nothing forces a hand-consigned part if we
use the E73 module + discrete power path (Option B) + AS5600 lever + WS2812B. The only thin-stock
preferred part is the nPM1300 PMIC, for which Option B is a deep-stock drop-in alternative.

---

### Aside: the modules NOT in the JLCPCB library

`MABF…`, Raytac **MDBT50Q**, and Insight SiP **ISP1807** are all **pre-certified nRF52840 modules** —
the same *role* as the Ebyte E73 (SoC + crystals + antenna + matching + worldwide RF cert in one
shielded part), just from different vendors. They're popular in commercial products but are **not
stocked by JLCPCB**, so using one means consigned/hand assembly. Quick orientation:

- **Raytac MDBT50Q** — Nordic's main module partner; the de-facto "gold standard" drop-in (used on
  e.g. Adafruit's nRF52840 Feather). Three antenna variants: **-1MV2** (chip antenna), **-P1MV2**
  (PCB antenna), **-U1MV2** (u.FL external). Full cert suite: FCC / IC / MIC-Telec / KC / SRRC / NCC /
  CE / RCM. Castellated + LGA pads, BT 5.4 qualified.
- **Insight SiP ISP1807** — a very small nRF52840 **System-in-Package** (antenna + crystals + DC-DC +
  matching integrated), pre-certified; chosen when board space is at a premium.

We default to the **Ebyte E73** purely because it is the **JLCPCB-native** pre-certified nRF52840
module. If we ever move assembly to a house that stocks Raytac (or hand-consign), the **MDBT50Q-1MV2**
(chip antenna) is the natural pin-strategy upgrade.

### Sources
- Ebyte E73-2G4M08S1C — https://www.cdebyte.com/products/E73-2G4M08S1C ·
  manual https://www.cdebyte.com/pdf-down.aspx?id=560 ·
  JLCPCB part https://jlcpcb.com/partdetail/Chengdu_Ebyte_ElecTech-E732G4M08S1C/C356849
- Raytac MDBT50Q — https://www.raytac.com/product/ins.php?index_id=24 ·
  datasheet https://cdn.sparkfun.com/assets/learn_tutorials/8/2/0/Raytac_MDBT50Q.pdf
- Insight SiP ISP1807 — https://www.insightsip.com/products/bluetooth-smart-modules/isp1807
