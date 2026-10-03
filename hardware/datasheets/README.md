# Local datasheet cache

`manifest.json` records manufacturer PDFs for the reviewed JLCPCB selections in
both projects’ `bom/jlcpcb-parts.json` files. Cached PDFs use their `C<number>.pdf`
catalog codes and remain git-ignored. References are board-qualified to avoid U1/J1 collisions. Download each manifest URL to its listed
filename to rebuild the cache.

Catalog matching and document drawing checks are described in
[`../notchdeck-one/bom/README.md`](../notchdeck-one/bom/README.md). A downloaded PDF
does not mean every electrical or mechanical parameter has been verified.

The initial automated MPN search returned unrelated parts for several connectors.
Those results were rejected; this manifest uses the exact selected catalog codes
and URLs instead. Do not accept a fuzzy distributor-search result without checking
its manufacturer, MPN and package. Older local PDFs outside this manifest are not
authoritative selections.
