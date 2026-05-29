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
