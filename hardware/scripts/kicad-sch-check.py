#!/usr/bin/env python3
"""kicad-sch-check — sanity-check a (hierarchical) KiCad schematic.

    scripts/kicad-sch-check.py <root.kicad_sch>

Exports a netlist + runs ERC via kicad-cli (forcing a full hierarchy parse),
then reports:
  - component count
  - any components missing a footprint
  - duplicate references
  - ERC violation tally by type

Exit status is non-zero on a STRUCTURAL problem (no components, a missing
footprint, or a duplicate reference). ERC violations are reported but do not
fail the check on their own — an unwired placement legitimately has
pin_not_connected / power_pin_not_driven, and a couple of lib_symbol_mismatch
warnings are expected for `extends`-based library symbols until first saved in
eeschema.

kicad-cli is located via $KICAD_CLI, then PATH, then the macOS app bundle.
"""
import os, re, sys, subprocess, tempfile, shutil, collections


def find_cli():
    env = os.environ.get("KICAD_CLI")
    if env and shutil.which(env):
        return env
    p = shutil.which("kicad-cli")
    if p:
        return p
    for c in ["/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli",
              "/usr/bin/kicad-cli", "/usr/local/bin/kicad-cli"]:
        if os.path.exists(c):
            return c
    sys.exit("kicad-sch-check: kicad-cli not found (set $KICAD_CLI)")


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: kicad-sch-check.py <root.kicad_sch>")
    sch = os.path.abspath(sys.argv[1])
    if not os.path.exists(sch):
        sys.exit(f"kicad-sch-check: no such file: {sch}")
    cli = find_cli()
    tmp = tempfile.mkdtemp(prefix="schcheck-")
    net = os.path.join(tmp, "out.net")
    erc = os.path.join(tmp, "out.erc")

    nl = subprocess.run([cli, "sch", "export", "netlist", "-o", net, sch],
                        capture_output=True, text=True)
    if not os.path.exists(net):
        print(nl.stdout + nl.stderr)
        shutil.rmtree(tmp, ignore_errors=True)
        sys.exit("kicad-sch-check: netlist export failed")
    subprocess.run([cli, "sch", "erc", "-o", erc, sch],
                   capture_output=True, text=True)

    t = open(net).read()
    comp_sec = t[t.index("(components"):t.index("(libparts")] if "(libparts" in t \
        else t[t.index("(components"):]
    blocks = re.split(r"\n\t\t\(comp\b", comp_sec)[1:]
    refs, nofp = [], []
    for b in blocks:
        m = re.search(r'\(ref "([^"]+)"', b)
        if not m:
            continue
        r = m.group(1)
        refs.append(r)
        if not re.search(r'\(footprint "[^"]+"', b):
            nofp.append(r)
    dups = sorted({r for r in refs if refs.count(r) > 1})

    erc_tally = collections.Counter()
    if os.path.exists(erc):
        for m in re.finditer(r"\[([a-z_]+)\]", open(erc).read()):
            erc_tally[m.group(1)] += 1

    print(f"schematic : {sch}")
    print(f"components: {len(refs)}")
    print(f"footprints: {len(refs) - len(nofp)}/{len(refs)} assigned"
          + ("" if not nofp else f"   MISSING: {', '.join(nofp)}"))
    print(f"duplicate refs: {', '.join(dups) if dups else 'none'}")
    if erc_tally:
        print("ERC violations:")
        for k, n in erc_tally.most_common():
            print(f"  {n:4d}  {k}")
    else:
        print("ERC violations: none")

    shutil.rmtree(tmp, ignore_errors=True)
    bad = (len(refs) == 0) or nofp or dups
    if bad:
        print("\nFAIL: structural problem (see above)")
        sys.exit(1)
    print("\nOK: structure sound (ERC items above are informational)")


if __name__ == "__main__":
    main()
