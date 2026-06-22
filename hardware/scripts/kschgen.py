"""kschgen — generate hierarchical KiCad 10 schematics from a data manifest.

This is the reusable engine behind the per-project *.schgen.py manifests. It
hand-authors KiCad-10 (version 20260306) schematic files in the proven format
used by the BenchBits projects (ministepper / pulsardew): one root sheet of
hierarchical sheet symbols, one child .kicad_sch per functional block, every
component resolving to a real library symbol + footprint, optional free-text
wiring notes per sheet.

A manifest registers the symbol libraries it uses, describes the sheets and the
components on them, then calls build(). See notchdeck-one.schgen.py for an
example. Components are PLACED (gridded, with refs/values/footprints/notes), not
wired — wiring is done afterwards in eeschema.

Usage from a manifest:

    import kschgen as K
    K.register_stdlib("Device", "R", "C")
    K.register_lib("notchdeck", "/abs/notchdeck.kicad_sym", "E73-2G4M08S1C")
    K.build(project="foo", proj_dir="/abs/foo", root_uuid="...",
            title=dict(title="Foo", date="2026-01-01", rev="A", company="X"),
            sheets=[ dict(name="MCU", file="mcu.kicad_sch", title="MCU",
                          page="2", big=[...], small=[...], note=(15,165,"...")) ])

Component dict keys: ref, lib_id, value, fp (footprint), and optional
lcsc, mpn, mfr, dnp (bool), datasheet.
"""
import os, re, uuid, json, glob

# ----------------------------------------------------------------------------
# symbol library registry:  lib_id ("Lib:Name") -> (source .kicad_sym, name)
# ----------------------------------------------------------------------------
SRC = {}
_STDLIB_DIR = None


def stdlib_dir():
    """Locate the installed KiCad standard symbol directory."""
    global _STDLIB_DIR
    if _STDLIB_DIR:
        return _STDLIB_DIR
    cands = []
    if os.environ.get("KICAD_SYMBOL_DIR"):
        cands.append(os.environ["KICAD_SYMBOL_DIR"])
    cands += [
        "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols",
        "/usr/share/kicad/symbols",
        "/usr/local/share/kicad/symbols",
        r"C:\Program Files\KiCad\10.0\share\kicad\symbols",
    ]
    cands += glob.glob("/Applications/KiCad*/KiCad.app/Contents/SharedSupport/symbols")
    for d in cands:
        if d and os.path.isdir(d):
            _STDLIB_DIR = d
            return d
    raise SystemExit("kschgen: cannot find KiCad standard symbol dir; "
                     "set KICAD_SYMBOL_DIR")


def register_stdlib(lib, *names):
    """Register symbols from a standard KiCad library (e.g. 'Device', 'R','C')."""
    f = os.path.join(stdlib_dir(), f"{lib}.kicad_sym")
    for n in names:
        SRC[f"{lib}:{n}"] = (f, n)


def register_lib(lib, path, *names):
    """Register symbols from a project/vendored .kicad_sym at an explicit path."""
    for n in names:
        SRC[f"{lib}:{n}"] = (path, n)


# ----------------------------------------------------------------------------
# extract a top-level (symbol "NAME" ...) block from a .kicad_sym by balancing
# ----------------------------------------------------------------------------
_filecache = {}


def _read(path):
    if path not in _filecache:
        _filecache[path] = open(path, encoding="utf-8").read()
    return _filecache[path]


def extract(path, name):
    txt = _read(path)
    m = re.search(r'\n\t\(symbol "' + re.escape(name) + r'"', txt)
    if not m:
        raise SystemExit(f"kschgen: symbol {name!r} not found in {path}")
    i = m.start() + 1                       # at the '(' before 'symbol'
    depth, j, instr = 0, i, False
    while j < len(txt):
        c = txt[j]
        if c == '"' and txt[j - 1] != '\\':
            instr = not instr
        elif not instr:
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    return txt[i:j + 1]
        j += 1
    raise SystemExit(f"kschgen: unbalanced parens extracting {name!r}")


def _extends_of(blk):
    m = re.search(r'\(extends "([^"]+)"', blk)
    return m.group(1) if m else None


def _flattened_block(path, name):
    """Return symbol NAME's block as a self-contained symbol. If it (extends ...)
    a parent, re-base the parent's full block (graphics + pins) onto NAME and drop
    the extends, so the symbol renders standalone. KiCad/eeschema resolves extends
    at load time, but kicad-cli's exporters do NOT — an unresolved derived symbol
    renders blank. Flattening here makes generated sheets render everywhere.
    Recurses through extends chains."""
    blk = extract(path, name)
    parent = _extends_of(blk)
    if not parent:
        return blk
    pblk = _flattened_block(path, parent)
    # rename the parent's graphic sub-symbols (PARENT_x_y -> NAME_x_y) then its
    # top symbol (PARENT -> NAME); property values (cosmetic) keep parent text —
    # the placed instance carries the real Reference/Value/Footprint/LCSC/MPN.
    g = pblk.replace('(symbol "' + parent + '_', '(symbol "' + name + '_')
    g = re.sub(r'^(\s*)\(symbol "' + re.escape(parent) + '"',
               r'\1(symbol "' + name + '"', g, count=1)
    return g


def cache_entries(lib_id, acc=None):
    """Cache the flattened block for lib_id (extends resolved/inlined so each
    symbol renders standalone). Returns ordered list of (lib_id, block)."""
    if acc is None:
        acc = []
    if lib_id in [e[0] for e in acc]:
        return acc
    path, name = SRC[lib_id]
    blk = _flattened_block(path, name)
    entry = re.sub(r'^(\s*)\(symbol "' + re.escape(name) + '"',
                   r'\1(symbol "' + lib_id + '"', blk, count=1)
    acc.append((lib_id, entry))
    return acc


def pin_numbers(lib_id):
    path, name = SRC[lib_id]
    blk = extract(path, name)
    seen, out = set(), []
    for m in re.finditer(r'\(number "([^"]+)"', blk):
        n = m.group(1)
        if n not in seen:
            seen.add(n)
            out.append(n)
    parent = _extends_of(blk)
    if parent and not out:
        plid = f"{lib_id.split(':')[0]}:{parent}"
        SRC.setdefault(plid, (path, parent))
        return pin_numbers(plid)
    return out


# ----------------------------------------------------------------------------
# emitters
# ----------------------------------------------------------------------------
def U():
    return str(uuid.uuid4())


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _prop(name, val, x, y, hide=False, justify="left"):
    h = " (hide yes)" if hide else ""
    j = f" (justify {justify})" if justify else ""
    return (f'\t\t(property "{name}" "{esc(val)}"\n'
            f'\t\t\t(at {x:.4f} {y:.4f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)){j}){h}\n\t\t)\n')


def text_note(s, x, y, size=1.5):
    return (f'\t(text "{esc(s)}"\n\t\t(exclude_from_sim no)\n'
            f'\t\t(at {x:.2f} {y:.2f} 0)\n'
            f'\t\t(effects (font (size {size} {size})) (justify left top))\n'
            f'\t\t(uuid "{U()}")\n\t)\n')


def _comp(c, project, root_uuid, sheet_uuid):
    x, y = c["x"], c["y"]
    dnp = "yes" if c.get("dnp") else "no"
    s = ("\t(symbol\n"
         f'\t\t(lib_id "{c["lib_id"]}")\n'
         f'\t\t(at {x:.4f} {y:.4f} 0)\n\t\t(unit 1)\n'
         "\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n"
         f"\t\t(dnp {dnp})\n"
         f'\t\t(uuid "{U()}")\n')
    s += _prop("Reference", c["ref"], x + 3.81, y - 2.54)
    s += _prop("Value", c["value"], x + 3.81, y + 2.54)
    s += _prop("Footprint", c.get("fp", ""), x, y, hide=True, justify="")
    s += _prop("Datasheet", c.get("datasheet", "~"), x, y, hide=True, justify="")
    for k, fld in (("lcsc", "LCSC"), ("mpn", "MPN"), ("mfr", "Manufacturer")):
        if c.get(k):
            s += _prop(fld, c[k], x, y, hide=True, justify="")
    for pn in pin_numbers(c["lib_id"]):
        s += f'\t\t(pin "{pn}" (uuid "{U()}"))\n'
    s += ("\t\t(instances\n"
          f'\t\t\t(project "{project}"\n'
          f'\t\t\t\t(path "/{root_uuid}/{sheet_uuid}"\n'
          f'\t\t\t\t\t(reference "{c["ref"]}")\n\t\t\t\t\t(unit 1)\n'
          "\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n")
    return s


# ----------------------------------------------------------------------------
# layout — snap to a 100-mil grid so pins stay on-grid
# ----------------------------------------------------------------------------
G = 2.54


def _layout(sh):
    bx = 18 * G
    for c in sh.get("big", []):
        c["x"], c["y"] = bx, 22 * G
        bx += 38 * G
    y0 = 48 * G if sh.get("big") else 16 * G
    cols, dx, dy = 10, 15 * G, 12 * G
    for k, c in enumerate(sh.get("small", [])):
        c["x"] = 12 * G + (k % cols) * dx
        c["y"] = y0 + (k // cols) * dy


# ----------------------------------------------------------------------------
# top-level build
# ----------------------------------------------------------------------------
def _title_block(title):
    s = "\t(title_block\n"
    s += f'\t\t(title "{esc(title.get("title", ""))}")\n'
    if title.get("date"):
        s += f'\t\t(date "{title["date"]}")\n'
    if title.get("rev"):
        s += f'\t\t(rev "{title["rev"]}")\n'
    if title.get("company"):
        s += f'\t\t(company "{esc(title["company"])}")\n'
    for i, cmt in enumerate(title.get("comments", []), 1):
        s += f'\t\t(comment {i} "{esc(cmt)}")\n'
    s += "\t)\n"
    return s


def _write_child(sh, project, root_uuid, title, paper):
    comps = sh.get("big", []) + sh.get("small", [])
    cache = []
    for c in comps:
        cache_entries(c["lib_id"], cache)
    ctitle = dict(title=f'{title.get("title","")} — {sh["title"]}',
                  date=title.get("date"), rev=title.get("rev"),
                  company=title.get("company"))
    out = ("(kicad_sch\n\t(version 20260306)\n\t(generator \"eeschema\")\n"
           "\t(generator_version \"10.0\")\n"
           f'\t(uuid "{sh["uuid"]}")\n\t(paper "{paper}")\n')
    out += _title_block(ctitle)
    out += "\t(lib_symbols\n"
    for _lid, entry in cache:
        out += entry + "\n"
    out += "\t)\n"
    for c in comps:
        out += _comp(c, project, root_uuid, sh["uuid"])
    if sh.get("note"):
        nx, ny, ntxt = sh["note"]
        out += text_note(ntxt, nx, ny)
    out += ('\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "'
            + sh["page"] + '")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)\n')
    open(os.path.join(sh["_dir"], sh["file"]), "w", encoding="utf-8").write(out)
    print(f"  {sh['file']:22s} {len(comps):3d} symbols, {len(cache)} lib_symbols"
          + ("  +note" if sh.get("note") else ""))


def _sheet_block(sh, x, y):
    w, h = 36.0, 22.0
    return ("\t(sheet\n"
            f"\t\t(at {x:.2f} {y:.2f})\n\t\t(size {w:.2f} {h:.2f})\n"
            "\t\t(fields_autoplaced yes)\n"
            "\t\t(stroke (width 0.1524) (type solid))\n"
            "\t\t(fill (color 0 0 0 0.0000))\n"
            f'\t\t(uuid "{sh["uuid"]}")\n'
            f'\t\t(property "Sheetname" "{esc(sh["name"])}"\n'
            f'\t\t\t(at {x:.2f} {y - 1.27:.2f} 0)\n'
            "\t\t\t(effects (font (size 1.27 1.27)) (justify left bottom))\n\t\t)\n"
            f'\t\t(property "Sheetfile" "{sh["file"]}"\n'
            f'\t\t\t(at {x:.2f} {y + h + 1.27:.2f} 0)\n'
            "\t\t\t(effects (font (size 1.27 1.27)) (justify left top))\n\t\t)\n\t)\n")


def build(project, proj_dir, root_uuid, title, sheets, paper="A3"):
    """Generate child sheets + root + update <project>.kicad_pro.

    sheets: list of dicts {name, file, title, page, big[], small[], note?, uuid?}
    """
    for sh in sheets:
        sh.setdefault("uuid", U())
        sh["_dir"] = proj_dir
        _layout(sh)

    print("child sheets:")
    for sh in sheets:
        _write_child(sh, project, root_uuid, title, paper)

    # root
    rtitle = dict(title)
    root = ("(kicad_sch\n\t(version 20260306)\n\t(generator \"eeschema\")\n"
            "\t(generator_version \"10.0\")\n"
            f'\t(uuid "{root_uuid}")\n\t(paper "{paper}")\n')
    root += _title_block(rtitle)
    root += "\t(lib_symbols)\n"
    x = 16 * G
    for sh in sheets:
        root += _sheet_block(sh, x, 16 * G)
        x += 22 * G
    root += ('\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n'
             "\t(embedded_fonts no)\n)\n")
    rpath = os.path.join(proj_dir, f"{project}.kicad_sch")
    open(rpath, "w", encoding="utf-8").write(root)
    print(f"root: {project}.kicad_sch  ({len(sheets)} sheet symbols)")

    # .kicad_pro sheets array
    pro = os.path.join(proj_dir, f"{project}.kicad_pro")
    if os.path.exists(pro):
        pj = json.load(open(pro))
        pj["sheets"] = ([[root_uuid, project]]
                        + [[sh["uuid"], sh["name"]] for sh in sheets])
        json.dump(pj, open(pro, "w"), indent=2)
        print(f"updated {project}.kicad_pro sheets array")
