# NotchDeck hardware

**Rev G logic and Rev E panel are two wired KiCad 10 assemblies:** `notchdeck-one` is the logic/handle board; `notchdeck-buttons` is the detachable 4×4 key/RGB board. The button board uses an owned **STM32G030F6P6TR / C529330** to scan a diode matrix and drive RGB locally. A six-way 1mm FFC carries I²C, interrupt and power. Select/Start remain direct inputs on the main board, alongside Reset.

| Project | Provisional PCB | Electrical components | Nets / endpoints | Assembly parts |
|---|---|---:|---|---:|
| [Logic](notchdeck-one/FLOORPLAN.md) | 115×90mm, four layers | 130 | 94 / 409 | 129 |
| [Buttons](notchdeck-buttons/README.md) | 86×120mm, two layers; 19mm key pitch | 85 | 56 / 235 | 84 |

Both have zero native ERC errors/warnings, complete independent net contracts, and matching PCB pad nets, schematic UUIDs and sourcing properties. Both are **unrouted floorplans**, with no tracks/vias/planes. Native DRC has no rule or schematic-parity violations; 323 logic and 211 button connections remain unrouted. Neither is ready to fabricate.

Open `notchdeck-one/notchdeck-one.kicad_pro` and
`notchdeck-buttons/notchdeck-buttons.kicad_pro` in KiCad 10 to inspect the complete
projects, then open each project's root schematic or PCB from its project manager.
The root schematics link the child sheets; symbols/footprints use standard KiCad
libraries plus the shared project-local `lib/` directory.

Magnetic and Gray-coded power/brake or combined mascon interfaces remain electrically unchanged. See [handle interfaces](../docs/06-handle-interfaces.md). U9 separates the two AS5600 address-0x36 channels; MAX17048 remains on another bus. Remove both R37/R38 before using an external power/combined sensor on J10.

Rev G adds [two solenoids, an active buzzer and external PWM](notchdeck-one/ACTUATORS.md). The actuator feed uses electronic current limiting, with no disposable fuse. A protected ≥6A 1S pack is mandatory for upstream battery-lead/PCB shorts. Full battery input protection is set to 5.05A nominal, with a 4.3A operating budget and two provisional 2A/100ms strikes. ACT_EN pauses charging; PWM pulldowns default the loads off.

## Source of truth and build

Edit `scripts/<project>.schgen.py` and each project's `bom/jlcpcb-parts.json`, then generate with the schematic editors closed. `notchdeck_capture.py` supplies shared wire/port capture; `kschgen.py` handles native files. Keep editor changes in those manifests before forcing regeneration. The saved PCBs become the source of truth once placement/routing proceeds; the seed floorplan script refuses to overwrite routed boards.

```sh
# From hardware/; <project> is notchdeck-one or notchdeck-buttons.
KSCHGEN_FORCE=1 make gen-notchdeck-one gen-notchdeck-buttons
make verify                     # both boards: net/ERC, PCB parity and BOM audits
make render-notchdeck-one render-notchdeck-buttons
make docs                       # both boards' images and BOMs
make jlc                        # two separate Gerber/drill/BOM/CPL ZIPs
make jlc-notchdeck-buttons       # or export one PCB
```

Pick-and-place files are `<project>/jlcpcb/<project>-CPL.csv`; ZIPs are `<project>/<project>-jlcpcb.zip`. These commands export the current design, including unfinished floorplans; they do not constitute a manufacturing release. Review rotations in JLCPCB before ordering. Generated exports are ignored by Git. CI audits both projects; on Linux pass `KICAD_PYTHON=python3` with `pcbnew` installed. See [script guide](scripts/README.md).

Use `KICAD_CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` on macOS
if the executable is not on PATH; the Makefile's native export targets need it.
The default `KICAD_PYTHON` points to KiCad's bundled macOS Python. Headless Linux
also needs the standard symbol/footprint tables installed, as shown in
[CI setup](../.github/workflows/ci.yml). Rendering PNG sheets requires an SVG
converter listed in the script guide.

CI publishes both generated BOM CSVs as `notchdeck-boms`; it does not publish
assembly ZIPs or CPLs. `make verify` does not include native DRC: CI runs that
separately, rejects rule/parity violations and reports unrouted counts. Before
manufacturing, all unintended unconnected items must also be resolved.

## Sourcing and remaining work

[PARTS.md](PARTS.md) maps all **213 installed parts / 44 JLCPCB codes** per set. [Five-set stock](jlcpcb-five-set-stock.csv) combines both boards’ usage: dated public availability or owned stock covers the five-set requirement; new C3662776 has 110 displayed in stock, with order allocation still to confirm. Private inventory balances remain outside Git. [System BOM](system-bom.csv) adds one DigiKey Molex 0151670213 cable per set. The user placed the earlier Rev E parts order; the shared CSV was refreshed afterward. Rev G additions need a separate top-up, recorded locally in `~/Dropbox-elec/github/notchdeck-actuator-expansion-2026-10-04.csv`. Stock observations do not reserve parts. Handle mechanisms, external sensor carriers, cell, keycaps and enclosure are not yet a sourced kit.

- Implement panel MCU firmware and main I²C integration. Existing Rev C/D direct-GPIO button/RGB firmware does **not** operate this Rev E panel. The [panel guide](notchdeck-buttons/README.md) records pin functions, scan behavior, address and programming requirements.
- Implement Rev G actuator startup/strike/hold, instantaneous current-budget scheduling, undervoltage shutdown, fault latching and timeout handling. No safe actuator image exists yet. Select actual coils/buzzer and a protected pack; qualify short behavior and temperature rise.
- Finalize enclosure, cable fit/retention and tolerances, mounting and connector access. The FFC is nominally compatible; its guaranteed thickness tolerance is wider than the connector drawing. Sample-fit or supplier approval remains required.
- Validate E73 land pattern/antenna region and MAX17048 exposed pad. Review final CPL orientation and assembly eligibility.
- Resolve USB source/current/inrush and the existing 500mA charger setting. RGB is USB-only; a ≤250mA total panel return target is below the 0.5A FFC-contact rating, but still needs firmware enforcement and a whole-system power budget. Review LDO margins and battery choice.
- Finish decoupling placement, USB/ESD routing, reference planes and ground stitching; route and run final DRC/DFM/EMC checks. Magnetic detents need measured calibration; handle hardware and power/thermal behavior need bench testing.

Connectivity and catalog checks establish internal consistency, not complete electrical, mechanical or production validation. No ERC exclusions were added.
