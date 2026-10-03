# Third-party library parts

Vendored KiCad symbols / footprints / 3D models live in this `lib/` directory and are
referenced project-locally via `sym-lib-table` / `fp-lib-table` (the `notchdeck:` library).
Record every imported part here with its **source** and **license**.

Import workflow (matches the other BenchBits hardware projects):

```sh
# 1. drop the pre-built KiCad part in place
cp <download>/Foo.kicad_mod   lib/footprints.pretty/
cp <download>/Foo.step        lib/3dmodels/
# 2. append the (symbol "Foo" ...) block to lib/symbols/notchdeck.kicad_sym
#    (drop any vendor library prefix on the embedded Footprint property so it
#     resolves against our project-local "notchdeck:" library)
# 3. repoint the footprint's 3D path to our local copy:
sed -i '' 's|\${KICAD.*_3RD_PARTY}/3dmodels/.*/|\${KIPRJMOD}/../lib/3dmodels/|' \
    lib/footprints.pretty/Foo.kicad_mod
```

## Imported / authored parts

| Part | Symbol | Footprint | 3D | Source | License |
|---|---|---|---|---|---|
| Ebyte E73-2G4M08S1C (nRF52840 module) | ✅ `notchdeck:E73-2G4M08S1C` | ✅ `EBYTE_E73-2G4M08S1C.kicad_mod` | ✅ `3dmodels/EBYTE_E73-2G4M08S1C.step` | joric/nrfmicro | **Unlicense (public domain)** |
| AMS AS5600 (magnetic angle) | ✅ `notchdeck:AS5600` (authored) | stdlib `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` | stdlib | in-house, from ams datasheet v1-06 pinout (Fig.4) | own work |
| ADI MAX17048 (fuel gauge) | ✅ `notchdeck:MAX17048` (authored) | stdlib `Package_DFN_QFN:TDFN-8-1EP_2x2mm_P0.5mm_EP0.8x1.2mm` | stdlib | in-house, from ADI datasheet pinout | own work |
| USB-C 16P receptacle (HRO TYPE-C-31-M-12, C165948) | stdlib | stdlib `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` | stdlib | KiCad standard library | CC-BY-SA 4.0 |
| Nordic nPM1300 (optional, Option A only) | ☐ not yet | stdlib `Package_DFN_QFN:QFN-32-1EP_5x5mm…` | ☐ | Nordic KiCad lib / SnapEDA | _TBD_ |

### E73-2G4M08S1C — details

- `footprints.pretty/EBYTE_E73-2G4M08S1C.kicad_mod` — the 43-pad module footprint, taken from
  joric/nrfmicro (`hardware/nrfmicro.pretty/E73-2G4M08S1C-52840.kicad_mod`), upgraded to the
  KiCad 10 format with `kicad-cli fp upgrade`, renamed, and relinked to the 3D model below.
- `3dmodels/EBYTE_E73-2G4M08S1C.step` — module STEP from the same repo.
- `symbols/notchdeck.kicad_sym` → `E73-2G4M08S1C` — symbol extracted from nrfmicro's schematic
  (`nrfmicro.kicad_sch` lib_symbols), upgraded with `kicad-cli sym upgrade`, footprint property
  repointed to `notchdeck:EBYTE_E73-2G4M08S1C`, BOM props (LCSC/MPN/Manufacturer) added.

Source repo: <https://github.com/joric/nrfmicro> — released into the public domain (Unlicense),
so no attribution is required; recorded here for provenance. The nrfmicro footprint pin/pad
numbering and the extracted symbol come from the same project, so they are mutually consistent.

(☐ = still to import. "stdlib" = KiCad-shipped, nothing vendored.)

### Revision B schematic symbol corrections

E73 GPIO/USB/SWDIO pins are modeled as bidirectional, including pad 28 (P0.15),
which the imported symbol incorrectly typed as a power input. The pad map is unchanged.

`notchdeck:SWD_2x05` and `notchdeck:SWD_TC2030` derive from KiCad 10's
`Connector:Conn_ARM_JTAG_SWD_10` and `Connector:Conn_ARM_SWD_TagConnect_TC2030-NL`.
They use passive signal pins to model physical connectors wired in parallel;
only one probe may be connected at a time. Graphics and pin numbering are unchanged.
Source: installed KiCad symbol library, KiCad library contributors.
License: [CC-BY-SA 4.0 with the KiCad library exception](https://www.kicad.org/libraries/license/).

### Selected JLCPCB footprint drawings (2026-10-03)

The following footprints are original project work transcribed from manufacturer
dimensions, not imported third-party KiCad library graphics. Dedicated 3D models
are not provided. Verify final assembly rotation in the assembler's CPL preview.

- `footprints.pretty/LED_XINGLIGHT_XL-5050RGBC-2812B.kicad_mod`: XINGLIGHT
  XL-5050RGBC-2812B, JLCPCB C2843785. [Manufacturer datasheet, p11](https://datasheet.lcsc.com/datasheet/pdf/40b65f6fea0587c0483bbbd4496835fd.pdf?productCode=C2843785)
  (PDF title includes `WS2812B`). The 5×5mm body has four 1.3mm-square lands;
  pad centers x=±2.2mm, y=±1.55mm. Top view: 1 VDD upper left, 2 DOUT lower left,
  3 GND lower right, 4 DIN upper right. The package chamfer is at GND; the separate
  silkscreen dot marks pin 1. Courtyard adds 0.25mm to the land/body envelope.
- `footprints.pretty/Samtec_FTSH-105-01-L-DV-K.kicad_mod`: Samtec
  FTSH-105-01-L-DV-K-TR, JLCPCB C448647. [Samtec FTSH-DV footprint drawing, rev H](https://suddendocs.samtec.com/prints/ftsh-1xx-xx-xxx-dv-xxx-footprint.pdf),
  sheet 1: 1.27mm pitch, 0.74×2.79mm lands, 6.86mm outer span. The drawing is
  rotated 90° for KiCad's two-column symbol convention, pin 1 upper left, odds on
  the left. [Samtec catalog package drawing](https://datasheet.lcsc.com/datasheet/pdf/75565f450863f224a13c3fa6d9c6afc1.pdf?productCode=C448647)
  gives the keyed body envelope of 5.08×11.18mm. The selected `-K` option has no
  alignment holes; courtyard adds 0.5mm to the pad/body envelope.

### TCA9543APWR (Rev C)

Project-authored `notchdeck:TCA9543APWR` symbol, own work, transcribed from the
[TI TCA9543A datasheet pin-functions table](https://www.ti.com/lit/ds/symlink/tca9543a.pdf).
PW/TSSOP14 mapping: 1=A0,2=A1,3=RESET,4=INT0,5=SD0,6=SC0,7=GND,8=INT1,
9=SD1,10=SC1,11=INT,12=SCL,13=SDA,14=VCC. Standard KiCad TSSOP14 footprint.
