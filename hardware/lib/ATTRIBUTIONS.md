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

## Planned imports (see ../PARTS.md)

These are the parts NOT in the KiCad standard library and must be vendored before the
schematic/PCB can be completed. Fill in exact source URL + license as each is imported.

| Part | Symbol | Footprint | 3D | Source | License |
|---|---|---|---|---|---|
| Ebyte E73-2G4M08S1C (nRF52840 module) | ☐ | ☐ | ☐ | SnapEDA / Component Search Engine (Samacsys); Ebyte datasheet | _TBD_ |
| Analog Devices MAX17048 (fuel gauge) | ☐ | stdlib TDFN-8 2×2 | n/a | SnapEDA / Component Search Engine | _TBD_ |
| AMS AS5600 (magnetic angle) | ☐ | stdlib SOIC-8 | stdlib | SnapEDA | _TBD_ |
| USB-C 16P receptacle (JLCPCB TYPE-C 16PIN 2MD) | stdlib | ☐ | ☐ | community "TYPE-C-31-M-12" / SnapEDA | _TBD_ |
| WS2812B-2020 (if 2020 pkg chosen) | stdlib | ☐ | ☐ | SnapEDA / community | _TBD_ |
| Nordic nPM1300 (optional PMIC) | ☐ | stdlib QFN-32 5×5 | ☐ | Nordic KiCad library / SnapEDA | _TBD_ |

(☐ = needs importing. "stdlib" = use the KiCad-shipped part, nothing to vendor.)

Prefer **Component Search Engine (Samacsys)** / **SnapEDA** parts since they bundle
symbol + footprint + STEP together. Most are free under permissive/own-use terms — record
the exact license per part above.
