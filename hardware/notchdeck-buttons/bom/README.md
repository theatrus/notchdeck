# notchdeck-buttons — Rev E sourcing

Checked 2026-10-03. This board has **84 installed components across 13 JLCPCB codes**. The [native BOM](jlcpcb-bom.csv), [tracking BOM](bom.csv), [selection JSON](jlcpcb-parts.json), and [stock observations](jlcpcb-stock.csv) agree with the schematic. The JSON drives the MPN, manufacturer, LCSC, datasheet and notes on each symbol.

Use the [combined five-set stock report](../../jlcpcb-five-set-stock.csv) for purchasing: parts shared between the two boards must be counted together. Public quantities use JLCPCB’s **Available Order Qty** from direct page checks on 2026-10-03. The STM32G030 uses owned private inventory from the shared local CSV; its balance is not published. The shared inventory is a snapshot, with allocation/reservation breakdown unavailable. Confirm allocation and assembly attrition before ordering. The earlier Rev E order was placed and the shared inventory refreshed afterward; the Rev F actuator top-up is separate.

The button MCU is C529330; the new FFC connectors are C262712 (31,746 public available, ten needed), and key isolation diodes are C81598 (4,858,639 available, eighty needed). Older part observations retain their actual timestamps. Public availability covers the combined build; the MCU is covered by the local owned balance. The community JSON category/price snapshots are not live quotes and must not be mistaken for LCSC warehouse stock.

The [Molex cable](../../system-bom.csv) is bought once per complete set from DigiKey, not included in either PCB assembly BOM. Bare programming contacts and mounting holes are excluded from both BOM and CPL. External handle hardware, sensor carriers and enclosure parts are not a complete sourced kit.

Both PCBs are unrouted. Native net/ERC, PCB pad/UUID, BOM identity and package BOM/CPL consistency checks verify the saved design and exports. They do not validate PCB routing, CPL rotation at JLCPCB, electrical/thermal margins or cable/enclosure fit. See [hardware status](../../README.md) and [part constraints](../../PARTS.md). PDFs are cached locally; [manifest](../../datasheets/manifest.json) records sources and board-qualified references.

```sh
make -C hardware verify-notchdeck-buttons verify-pcb-notchdeck-buttons verify-bom-notchdeck-buttons
make -C hardware jlc-notchdeck-buttons
```
