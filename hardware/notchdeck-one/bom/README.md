# NotchDeck One — JLCPCB sourcing snapshot

Checked **2026-10-03**: all **115 purchasable components** have exact JLCPCB catalog
part numbers, manufacturer/MPN, footprints and datasheet links. There are **29 unique
part numbers**: 16 Basic and 13 Extended in the dated catalog snapshot. All 29
reported positive stock. The native export has 34 rows because shared parts serve
different functional values, such as the reset button and lever connectors.

This is an **unrouted placement study**, not a fabrication release or an order.
Stock, categories and prices came from the community `jlcsearch` JLCPCB catalog;
each query URL and timestamp is retained in `jlcpcb-parts.json`. LCSC's separate
inventory was not used as JLCPCB stock. Recheck JLCPCB stock, assembly eligibility,
fees, attrition and CPL orientation when preparing an order.

## Files and source of truth

- [`jlcpcb-parts.json`](jlcpcb-parts.json): reviewed part choices, reference assignments,
  exact catalog identity, datasheet URLs, stock source and snapshot date. The schematic
  generator loads this file and emits the properties onto every symbol.
- [`jlcpcb-bom.csv`](jlcpcb-bom.csv): checked native KiCad assembly export, with explicit
  comma-separated designators and the required `LCSC Part #` column. No reference ranges.
- [`bom.csv`](bom.csv): BOM-skill tracking export. `Chosen_Distributor=LCSC` denotes
  its production sourcing channel. `LC_Stock` is intentionally blank because this
  review checked JLCPCB inventory, recorded separately in the JSON.
- [`../../datasheets/manifest.json`](../../datasheets/manifest.json): selected datasheet
  URLs and local cache paths. PDFs stay in `hardware/datasheets/` and are git-ignored.

Schematic properties remain the export source of truth. Update the selection JSON,
regenerate with the schematic editor closed, update the PCB from the schematic,
run the checks, and refresh both CSV snapshots. The native exporter groups by
Value, Footprint, LCSC, MPN and Manufacturer, so red and green indicators cannot
silently merge merely because both have the functional value `LED`.

## Corrections and drawing checks

| References | Selection / change | Evidence and confidence |
|---|---|---|
| U2 | Diodes AP2112K-3.3TRG1, C51118 | Exact catalog manufacturer/MPN match; replaces a code for a different manufacturer. High confidence in identity. |
| U7 | ST USBLC6-2SC6, C7519 | Exact catalog manufacturer/MPN match; replaces a code for a different manufacturer. High confidence in identity. |
| U3 | MCP73832T-2ACI/OT, C38066 | Manufacturer datasheet confirms the open-drain STAT variant needed by the 3V3 pull-up. No MCP73831 substitution. High confidence. |
| U8 | TI SN74AHCT1G125DBVR, C7484 | AHCT input thresholds support the 3V3 data signal with the buffer powered at 5V. No AHC/HC substitution. High confidence. |
| U5 / D19 | AS5600-ASOT / JSCJ B5819W SL | Corrected ordering suffix and manufacturer to the catalog identities. High confidence. |
| D1–D16 | XINGLIGHT XL-5050RGBC-2812B, C2843785 | Manufacturer PDF p11: 5×5mm body, 1.3mm square pads, centers x=±2.2 / y=±1.55mm; top-view 1=VDD, 2=DOUT, 3=GND, 4=DIN. New footprint follows this pattern. High confidence in drawing transcription; CPL rotation still requires review. |
| J3 | Samtec FTSH-105-01-L-DV-K-TR, C448647 | Keyed shroud requires a larger body/courtyard than the generic header. Samtec FTSH-DV footprint drawing rev H: 0.74×2.79mm pads, 6.86mm outer span, 1.27mm pitch. No alignment holes for the selected -K option. New footprint; moved 2mm down to clear C9. High confidence in drawing transcription. |
| J2/J5–J9 | Exact JST PH SMT right-angle variants | Manufacturer drawing and selected KiCad family/pin count agree. High confidence in part identity. Mating harnesses are separate. |
| SW1–SW17 | XKB TS-1187A-B-A-B, C318884 | Exact TS-1187A package variant; drawing reviewed against the existing footprint. High confidence in identity and pad grouping. |
| D17 / D18 | C965805 yellow-green / C2286 red | Separate catalog parts and BOM rows; low-Vf green selected for the existing 3V3 indicator circuit. Catalog/datasheet evidence. |
| Passives | Samsung MLCCs and UNI-ROYAL resistors | Catalog value, tolerance, voltage and imperial package checked against the schematic. Ratings included in symbol BOM Comments. Catalog evidence; no measured DC-bias/thermal characterization. |

Sources are linked per part in the JSON and [parts table](../../PARTS.md).
Custom footprint provenance and the Samtec drawing URL are in
[`../../lib/ATTRIBUTIONS.md`](../../lib/ATTRIBUTIONS.md).

## Exclusions and open work

J4 is the bare TC2030-NL programming contact pattern: no physical component is
ordered or placed. It is excluded from both BOM and placement output. H1–H4 are
PCB-only mounting holes. The protected cell, mating cables, probe, magnet, lever,
external switches, keycaps and enclosure are outside this PCB assembly BOM.

The imported E73 land pattern/antenna clearance and MAX17048 exposed-pad land
pattern remain review items. Charging current, USB power/inrush, RGB brightness,
LDO margins and enclosure geometry remain as documented in
[`../FLOORPLAN.md`](../FLOORPLAN.md). Neither catalog availability nor clean ERC/DRC
closes those items.

## Verification

From `hardware/`:

```sh
make verify-notchdeck-one verify-pcb-notchdeck-one verify-bom-notchdeck-one
kicad-cli pcb drc --schematic-parity --format json \
  -o /tmp/notchdeck-drc.json notchdeck-one/notchdeck-one.kicad_pcb
```

- Native ERC: zero errors/warnings, no exclusions.
- Net contract: 116 components, 80 nets, 360 endpoints, 14 intentional NCs.
- PCB audit: all endpoints, schematic UUID paths, part fields and BOM/placement
  exclusions match.
- BOM audit: 115 references, 29 codes, quantities, MPNs, manufacturers, footprints
  and notes match the reviewed selection data.
- Native PCB DRC: zero rule/parity issues; **313 unconnected items** remain.

The audit checks saved design consistency, not current catalog stock or tested
hardware behavior. No components or boards have been ordered.
