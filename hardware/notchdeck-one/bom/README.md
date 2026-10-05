# notchdeck-one — Rev F sourcing

The logic/actuator board has **127 installed components across 37 JLCPCB codes**.
The [native BOM](jlcpcb-bom.csv), [tracking BOM](bom.csv), [selection JSON](jlcpcb-parts.json)
and [stock observations](jlcpcb-stock.csv) describe the captured schematic. The
JSON drives each symbol's MPN, manufacturer, LCSC code, datasheet and notes.

Use the [combined five-set report](../../jlcpcb-five-set-stock.csv) to avoid
counting shared parts independently on each board. A complete set contains
211 assembly components and 42 JLCPCB codes. Private balances remain in the
shared CSV outside Git. The user placed the earlier Rev E order; Rev F adds
parts that were not included in that order.

The 2026-10-04 PDT direct JLCPCB page checks show 1,716 orderable C174045 FETs,
3,063 C2155674 electronic limiters, 17,404 C295747 two-pin connectors and
18,511 C265102 four-pin connectors. Older rows retain their actual observation
dates. Community category/price snapshots are estimates, not live quotes.

For 20 sets plus 10% spares, the new top-up is 36 FETs, 22 limiters, 66 two-pin
and 16 four-pin connectors. The other additions fit owned stock after protecting
Tenkiro's recorded target. See the local
`~/Dropbox-elec/github/notchdeck-actuator-expansion-2026-10-04.csv` for balances,
assumptions and source links. No top-up cart or order has been made. The shared
inventory does not expose every live reservation; verify allocation at assembly.

[Actuator documentation](../ACTUATORS.md) covers the electronic short limiter,
protected-pack requirement, pin mappings, PWM limits and pending firmware/bench
work. No one-time fuse is selected. Both PCBs remain unrouted placement studies.
