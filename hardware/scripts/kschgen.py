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
    # Top-level symbols are indented with a tab (KiCad stdlib) or spaces in
    # some project libraries; accept either form.
    m = re.search(r'\n[ \t]*\(symbol "' + re.escape(name) + r'"', txt)
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


def _env_truthy(name):
    return os.environ.get(name, "").lower() in ("1", "true", "yes", "on")


def _force_regen(force=False):
    return force or _env_truthy("KSCHGEN_FORCE")


def _schematic_uuid(path):
    """Return an existing .kicad_sch file UUID, if the sheet already exists."""
    if not os.path.exists(path):
        return None
    txt = open(path, encoding="utf-8").read()
    m = re.search(r'\(kicad_sch\b.*?\(uuid "([^"]+)"\)', txt, re.S)
    return m.group(1) if m else None


def _prop(name, val, x, y, hide=False, justify="left"):
    h = " (hide yes)" if hide else ""
    j = f" (justify {justify})" if justify else ""
    return (f'\t\t(property "{name}" "{esc(val)}"\n'
            f'\t\t\t(at {x:.4f} {y:.4f} 0)\n'
            f'\t\t\t(effects (font (size 1.27 1.27)){j}){h}\n\t\t)\n')


# Schematic notes are rendered in a MONOSPACE font so wiring tables/columns line
# up. "Courier New" is broadly available (macOS/Windows; Linux substitutes a mono
# face); KiCad falls back to its stroke font if absent -- content still reads.
NOTE_FONT = "Courier New"


def text_note(s, x, y, size=1.27, mono=True):
    face = f'(face "{NOTE_FONT}") ' if mono else ""
    return (f'\t(text "{esc(s)}"\n\t\t(exclude_from_sim no)\n'
            f'\t\t(at {x:.2f} {y:.2f} 0)\n'
            f'\t\t(effects (font {face}(size {size} {size})) (justify left top))\n'
            f'\t\t(uuid "{U()}")\n\t)\n')


def note_block(*lines):
    """Join note lines into one monospace block (newlines preserved by esc())."""
    return "\n".join(lines)


def pin_table(pairs, header=("PIN", "SIGNAL"), cols=2, indent="  "):
    """Format [(pin, signal), ...] as an aligned monospace table."""
    pairs = [(str(p), str(s)) for p, s in pairs]
    n = len(pairs)
    per = (n + cols - 1) // cols if cols > 1 else n
    pw = max([len(p) for p, _ in pairs] + [len(header[0])])
    sw = max([len(s) for _, s in pairs] + [len(header[1])])

    def cell(p, s):
        return f"{p:>{pw}}  {s:<{sw}}"

    rows = [indent + "    ".join([cell(*header)] * min(cols, (n + per - 1) // per))]
    for i in range(per):
        line = [cell(*pairs[i])]
        j = i + per
        while j < n:
            line.append(cell(*pairs[j]))
            j += per
        rows.append(indent + "    ".join(line))
    return "\n".join(rows).rstrip()


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
    # Park the wiring note BELOW every component so long generated tables do
    # not overlap the automatically placed symbol grid.
    n = len(sh.get("small", []))
    small_bottom = y0 + ((n - 1) // cols) * dy if n else 0
    big_bottom = 22 * G + 45 if sh.get("big") else 0
    sh["_note_y"] = max(small_bottom, big_bottom) + 16


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


def _write_child(sh, project, root_uuid, title, paper, force=False):
    path = os.path.join(sh["_dir"], sh["file"])
    if os.path.exists(path) and not _force_regen(force):
        print(f"  {sh['file']:22s} kept existing ({sh['uuid']})")
        return
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
        out += text_note(ntxt, nx, sh.get("_note_y", ny))
    out += ('\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "'
            + sh["page"] + '")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)\n')
    open(path, "w", encoding="utf-8").write(out)
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


# ============================================================================
# multi-channel + wiring extensions
# ----------------------------------------------------------------------------
# The flat build() above PLACES components. The helpers below additionally WIRE
# them (wires + net labels) and support a *reused* sheet — one child .kicad_sch
# instantiated by several sheet symbols (a KiCad "multi-channel" design), where
# each instance annotates to its own reference designators. Used by boards whose
# structure repeats (e.g. the display's identical 7-seg rows).
# ============================================================================

_PIN_RE = re.compile(
    r'\(pin\b.*?\(at\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\).*?'
    r'\(length\s+([\d.]+)\).*?\(name\s+"([^"]*)".*?\(number\s+"([^"]+)"', re.S)


def pin_geom(lib_id):
    """[{number,name,x,y,angle,length}] for lib_id's pins (library coords, +Y up)."""
    path, name = SRC[lib_id]
    blk = extract(path, name)
    return [dict(number=m.group(6), name=m.group(5),
                 x=float(m.group(1)), y=float(m.group(2)),
                 angle=int(float(m.group(3))), length=float(m.group(4)))
            for m in _PIN_RE.finditer(blk)]


# outward (away-from-body) unit direction of a pin, in SHEET coords (+Y down).
# lib angle 0 = body to the right (pin exits left); 180 = exits right;
# 90 = exits down on screen; 270 = exits up on screen (Y is flipped vs the lib).
_OUTWARD = {0: (-1.0, 0.0), 180: (1.0, 0.0), 90: (0.0, 1.0), 270: (0.0, -1.0)}


def _sheet_xy(c, p):
    """Pin p's connection point in sheet coords for comp c placed at orient 0."""
    return (round(c["x"] + p["x"], 4), round(c["y"] - p["y"], 4))


def pin_at(c, number):
    """(x, y, angle) of pin #number's connection point for placed comp c."""
    for p in pin_geom(c["lib_id"]):
        if p["number"] == str(number):
            x, y = _sheet_xy(c, p)
            return (x, y, p["angle"])
    raise KeyError(f'{c["lib_id"]}: no pin #{number}')


def pin_named(c, name):
    """[(x, y, angle), ...] connection points of pins whose name == name."""
    out = []
    for p in pin_geom(c["lib_id"]):
        if p["name"] == name:
            x, y = _sheet_xy(c, p)
            out.append((x, y, p["angle"]))
    return out


# ---- schematic element emitters (strings) ----------------------------------
def w_wire(x1, y1, x2, y2):
    return (f'\t(wire (pts (xy {x1:.4f} {y1:.4f}) (xy {x2:.4f} {y2:.4f}))\n'
            f'\t\t(stroke (width 0) (type default))\n\t\t(uuid "{U()}")\n\t)\n')


def w_junction(x, y):
    return (f'\t(junction (at {x:.4f} {y:.4f}) (diameter 0) (color 0 0 0 0)\n'
            f'\t\t(uuid "{U()}")\n\t)\n')


def _lbl_angle(dx, dy):
    return 0 if dx > 0 else 180 if dx < 0 else 270 if dy < 0 else 90


def w_label(t, x, y, a=0):
    return (f'\t(label "{esc(t)}"\n\t\t(at {x:.4f} {y:.4f} {a})\n'
            f'\t\t(effects (font (size 1.27 1.27)) (justify left bottom))\n'
            f'\t\t(uuid "{U()}")\n\t)\n')


def w_hlabel(t, x, y, a=0, shape="input"):
    return (f'\t(hierarchical_label "{esc(t)}"\n\t\t(shape {shape})\n'
            f'\t\t(at {x:.4f} {y:.4f} {a})\n'
            f'\t\t(effects (font (size 1.27 1.27)) (justify left))\n'
            f'\t\t(uuid "{U()}")\n\t)\n')


def w_glabel(t, x, y, a=0, shape="bidirectional"):
    return (f'\t(global_label "{esc(t)}"\n\t\t(shape {shape})\n'
            f'\t\t(at {x:.4f} {y:.4f} {a})\n\t\t(fields_autoplaced yes)\n'
            f'\t\t(effects (font (size 1.27 1.27)) (justify left))\n'
            f'\t\t(uuid "{U()}")\n\t)\n')


def net_pin(c, ref, net, kind="label", stub=2.54, shape="input"):
    """Wire a short stub outward from a pin and attach a net label of `kind`
    (label / hlabel / glabel). Returns the s-expr string."""
    if str(ref).isdigit():
        x, y, ang = pin_at(c, ref)
    else:
        x, y, ang = pin_named(c, ref)[0]
    dx, dy = _OUTWARD[ang]
    ex, ey = round(x + dx * stub, 4), round(y + dy * stub, 4)
    s = w_wire(x, y, ex, ey)
    a = _lbl_angle(dx, dy)
    s += ({"label": w_label, "hlabel": lambda t, X, Y, A: w_hlabel(t, X, Y, A, shape),
           "glabel": lambda t, X, Y, A: w_glabel(t, X, Y, A, shape)}[kind])(net, ex, ey, a)
    return s


# ---- placed symbol with one OR MANY instance paths -------------------------
def w_symbol(c, project, instances):
    """A placed symbol. instances = [(path, reference), ...]; more than one path
    makes it a reused (multi-channel) symbol annotated per instance."""
    x, y = c["x"], c["y"]
    dnp = "yes" if c.get("dnp") else "no"
    inbom = "no" if c.get("in_bom") is False else "yes"
    ref0 = instances[0][1]
    s = ("\t(symbol\n"
         f'\t\t(lib_id "{c["lib_id"]}")\n'
         f'\t\t(at {x:.4f} {y:.4f} 0)\n\t\t(unit 1)\n'
         "\t\t(exclude_from_sim no)\n"
         f"\t\t(in_bom {inbom})\n\t\t(on_board yes)\n"
         f"\t\t(dnp {dnp})\n"
         f'\t\t(uuid "{U()}")\n')
    s += _prop("Reference", ref0, x + 3.81, y - 2.54)
    s += _prop("Value", c.get("value", ""), x + 3.81, y + 2.54)
    s += _prop("Footprint", c.get("fp", ""), x, y, hide=True, justify="")
    s += _prop("Datasheet", c.get("datasheet", "~"), x, y, hide=True, justify="")
    for k, fld in (("lcsc", "LCSC"), ("mpn", "MPN"), ("mfr", "Manufacturer")):
        if c.get(k):
            s += _prop(fld, c[k], x, y, hide=True, justify="")
    for pn in pin_numbers(c["lib_id"]):
        s += f'\t\t(pin "{pn}" (uuid "{U()}"))\n'
    s += "\t\t(instances\n" + f'\t\t\t(project "{project}"\n'
    for path, ref in instances:
        s += (f'\t\t\t\t(path "{path}"\n\t\t\t\t\t(reference "{ref}")\n'
              "\t\t\t\t\t(unit 1)\n\t\t\t\t)\n")
    s += "\t\t\t)\n\t\t)\n\t)\n"
    return s


# ---- sheet symbol (with hierarchical pins) ---------------------------------
def w_sheet(name, file, uuid, x, y, w, h, pins):
    """A sheet symbol. pins = [(name, ptype, px, py, angle), ...] on its border."""
    s = ("\t(sheet\n"
         f"\t\t(at {x:.4f} {y:.4f})\n\t\t(size {w:.4f} {h:.4f})\n"
         "\t\t(fields_autoplaced yes)\n"
         "\t\t(stroke (width 0.1524) (type solid))\n"
         "\t\t(fill (color 0 0 0 0.0000))\n"
         f'\t\t(uuid "{uuid}")\n'
         f'\t\t(property "Sheetname" "{esc(name)}"\n'
         f'\t\t\t(at {x:.4f} {y - 1.27:.4f} 0)\n'
         "\t\t\t(effects (font (size 1.27 1.27)) (justify left bottom))\n\t\t)\n"
         f'\t\t(property "Sheetfile" "{esc(file)}"\n'
         f'\t\t\t(at {x:.4f} {y + h + 1.27:.4f} 0)\n'
         "\t\t\t(effects (font (size 1.27 1.27)) (justify left top))\n\t\t)\n")
    for (pn, pt, px, py, pa) in pins:
        s += (f'\t\t(pin "{esc(pn)}" {pt}\n'
              f'\t\t\t(at {px:.4f} {py:.4f} {pa})\n'
              f'\t\t\t(effects (font (size 1.27 1.27)) (justify left))\n'
              f'\t\t\t(uuid "{U()}")\n\t\t)\n')
    s += "\t)\n"
    return s


def _sch_open(uuid, title, paper):
    out = ("(kicad_sch\n\t(version 20260306)\n\t(generator \"eeschema\")\n"
           "\t(generator_version \"10.0\")\n"
           f'\t(uuid "{uuid}")\n\t(paper "{paper}")\n')
    out += _title_block(title)
    return out


def write_wired_child(sh, project, root_uuid, title, paper, force=False):
    """Write a child sheet that carries pre-computed instance paths + wiring.

    sh keys:
      uuid, file, title, page
      comps      : [(comp_dict, [(path, ref), ...]), ...]
      wiring     : pre-emitted s-expr string (built with w_wire/net_pin/...)
      notes      : [(x, y, text), ...]  (optional)
    """
    path = os.path.join(sh["_dir"], sh["file"])
    sh["uuid"] = _schematic_uuid(path) or sh.get("uuid") or U()
    if os.path.exists(path) and not _force_regen(force):
        print(f"  {sh['file']:24s} kept existing ({sh['uuid']})")
        return
    ctitle = dict(title=f'{title.get("title","")} — {sh["title"]}',
                  date=title.get("date"), rev=title.get("rev"),
                  company=title.get("company"))
    out = _sch_open(sh["uuid"], ctitle, paper)
    cache = []
    for c, _inst in sh["comps"]:
        cache_entries(c["lib_id"], cache)
    out += "\t(lib_symbols\n"
    for _lid, entry in cache:
        out += entry + "\n"
    out += "\t)\n"
    for c, inst in sh["comps"]:
        out += w_symbol(c, project, inst)
    out += sh.get("wiring", "")
    for (nx, ny, ntxt) in sh.get("notes", []):
        out += text_note(ntxt, nx, ny)
    out += ('\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "'
            + sh["page"] + '")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)\n')
    open(path, "w", encoding="utf-8").write(out)
    n = len(sh["comps"])
    print(f"  {sh['file']:24s} {n:3d} symbols x{len(sh['comps'][0][1]) if n else 0}"
          f"  {len(cache)} lib_symbols  +wired")


def write_root(project, proj_dir, root_uuid, title, sheet_symbols, wiring,
               pro_sheets, paper="A3", force=False):
    """Write the root schematic from pre-built sheet-symbol + wiring strings."""
    rpath = os.path.join(proj_dir, f"{project}.kicad_sch")
    root_uuid = _schematic_uuid(rpath) or root_uuid
    if os.path.exists(rpath) and not _force_regen(force):
        print(f"root: {project}.kicad_sch  kept existing ({root_uuid})")
    else:
        root = _sch_open(root_uuid, dict(title), paper)
        root += "\t(lib_symbols)\n"
        root += sheet_symbols
        root += wiring
        root += ('\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n'
                 "\t(embedded_fonts no)\n)\n")
        open(rpath, "w", encoding="utf-8").write(root)
        print(f"root: {project}.kicad_sch")
    pro = os.path.join(proj_dir, f"{project}.kicad_pro")
    if os.path.exists(pro):
        pj = json.load(open(pro))
        sheets_array = [[root_uuid, project]] + pro_sheets
        if pj.get("sheets") != sheets_array:
            pj["sheets"] = sheets_array
            json.dump(pj, open(pro, "w"), indent=2)
            print(f"updated {project}.kicad_pro sheets array")


def build(project, proj_dir, root_uuid, title, sheets, paper="A3", force=False):
    """Create missing child sheets + root + update <project>.kicad_pro.

    sheets: list of dicts {name, file, title, page, big[], small[], note?, uuid?}
    Existing .kicad_sch files are kept intact by default. Set force=True or
    KSCHGEN_FORCE=1 to rebuild them, reusing their existing sheet UUIDs.
    """
    force = _force_regen(force)
    rpath = os.path.join(proj_dir, f"{project}.kicad_sch")
    root_uuid = _schematic_uuid(rpath) or root_uuid

    for sh in sheets:
        sh["_dir"] = proj_dir
        child_path = os.path.join(proj_dir, sh["file"])
        sh["uuid"] = _schematic_uuid(child_path) or sh.get("uuid") or U()
        _layout(sh)

    print("child sheets:")
    for sh in sheets:
        _write_child(sh, project, root_uuid, title, paper, force=force)

    # root
    if os.path.exists(rpath) and not force:
        print(f"root: {project}.kicad_sch  kept existing ({root_uuid})")
    else:
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
        open(rpath, "w", encoding="utf-8").write(root)
        print(f"root: {project}.kicad_sch  ({len(sheets)} sheet symbols)")

    # .kicad_pro sheets array
    pro = os.path.join(proj_dir, f"{project}.kicad_pro")
    if os.path.exists(pro):
        pj = json.load(open(pro))
        sheets_array = ([[root_uuid, project]]
                        + [[sh["uuid"], sh["name"]] for sh in sheets])
        if pj.get("sheets") != sheets_array:
            pj["sheets"] = sheets_array
            json.dump(pj, open(pro, "w"), indent=2)
            print(f"updated {project}.kicad_pro sheets array")
