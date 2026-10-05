# notchdeck-one — Rev G sourcing

The logic/actuator board has **129 installed components across 39 JLCPCB codes**.
The [native BOM](jlcpcb-bom.csv), [tracking BOM](bom.csv), [selection JSON](jlcpcb-parts.json)
and [stock observations](jlcpcb-stock.csv) describe the captured schematic. The
JSON drives each symbol's MPN, manufacturer, LCSC code, datasheet and notes.

Use the [combined five-set report](../../jlcpcb-five-set-stock.csv) to avoid
counting shared parts independently on each board. A complete set contains
213 assembly components and 44 JLCPCB codes. Private balances remain in the
shared CSV outside Git. The user placed the earlier Rev E order; Rev G adds
parts that were not included in that order.

The 2026-10-04 PDT JLCPCB checks show 110 C3662776 TPS259461LRPWR
protectors in stock; exact order allocation was not checked. Earlier live checks
show 1,716 orderable C174045 FETs, 17,404 C295747 two-pin connectors and
18,511 C265102 four-pin connectors. J2 uses owned C585880 Micro-Fit stock;
R60 uses C22775; its existing stock is reserved for Tenkiro, so buy 100 for a sensible passive price break. Older rows retain their observation dates. Catalog
category/price snapshots are estimates, not live quotes.

For 20 sets plus 10% spares, the top-up is **36 FETs, 22 C3662776 protectors,
44 C295747 two-pin and 16 C265102 four-pin connectors**. The previous C2155674
protector is no longer selected. C22775 also needs 22 pieces (recommend buying 100); the existing stock is reserved. Other additions fit recorded owned stock after
Tenkiro's allocation. See the local
`~/Dropbox-elec/github/notchdeck-actuator-expansion-2026-10-04.csv` for balances
and source links. No top-up cart or order has been made. Shared inventory does
not expose all live reservations; confirm free allocation before assembly.

[Actuator documentation](../ACTUATORS.md) covers the electronic short limiter,
protected-pack requirement, pin mappings, PWM limits and pending firmware/bench
work. No one-time fuse is selected. Both PCBs remain unrouted placement studies.
