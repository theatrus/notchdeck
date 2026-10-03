"""Shared visible-wire capture for the two generated NotchDeck boards."""
import os
import kschgen as K
G = 2.54

class Capture:
    def __init__(self, sh, project_dir, root_uuid, title, project):
        self.project, self.root_uuid, self.title = project, root_uuid, title
        self.sh = sh
        sh["_dir"] = project_dir
        sh["uuid"] = K._schematic_uuid(os.path.join(project_dir, sh["file"])) or K.U()
        self.path = f"/{root_uuid}/{sh['uuid']}"
        self.parts = {c["ref"]: c for c in sh.get("big", []) + sh.get("small", [])}
        self.placed = {}
        self.extra = []
        self.segments = []
        self.points = set()
        self.connected = set()
        self.power_count = 0
        self.notes = []

    def place(self, ref, x, y, angle=0, **kw):
        c = dict(self.parts[ref], x=x * G, y=y * G, angle=angle, **kw)
        self.placed[ref] = c
        return c

    def pin(self, ref, n):
        self.connected.add((ref, str(n)))
        return K.pin_at(self.placed[ref], str(n))[:2]

    def wire(self, *points):
        for a, b in zip(points, points[1:]):
            a, b = tuple(round(v, 4) for v in a), tuple(round(v, 4) for v in b)
            assert a[0] == b[0] or a[1] == b[1], (a, b)
            if a != b:
                self.segments.append((a, b))
                self.points.update((a, b))

    def join(self, a, b, via=()):
        self.wire(self.pin(*a), *via, self.pin(*b))

    def label(self, net, p, angle=0):
        self.points.add(p)
        self.extra.append(K.w_label(net, *p, angle))

    def stub(self, ref, pin, net, length=2, kind="label"):
        x, y, a = K.pin_at(self.placed[ref], str(pin))
        dx, dy = K._OUTWARD[a]
        p = (round(x + dx * length * G, 4), round(y + dy * length * G, 4))
        self.wire(self.pin(ref, pin), p)
        if kind == "power":
            self.power(net, p)
        else:
            self.label(net, p, K._lbl_angle(dx, dy))
        return p

    def nc(self, ref, *pins):
        for n in pins:
            x, y = self.pin(ref, n)
            self.extra.append(f'\t(no_connect (at {x} {y}) (uuid "{K.U()}"))\n')

    def power(self, net, p, flag=False):
        if net not in ("GND", "+3V3") and not flag:
            self.label(net, p)
            return
        self.power_count += 1
        ref = f"#PWR{int(self.sh['page'])*100+self.power_count:03}"
        sym = "PWR_FLAG" if flag else net
        self.placed[ref] = dict(
            ref=ref,
            lib_id="power:" + sym,
            value=sym,
            x=p[0],
            y=p[1],
            in_bom=False,
            hide_value=net == "GND",
            value_offset=(-2.54, -3.81),
        )
        self.points.add(p)

    def rail(self, net, pins, y, flag=False):
        ps = [self.pin(*p) for p in pins]
        yy = y * G
        xs = sorted(set(p[0] for p in ps))
        for p in ps:
            self.wire(p, (p[0], yy))
        for a, b in zip(xs, xs[1:]):
            self.wire((a, yy), (b, yy))
        self.power(net, (xs[0], yy))
        if flag:
            self.power(net, (xs[-1], yy), flag=True)

    def port(self, net, x, y, shape="bidirectional"):
        p = (x * G, y * G)
        q = ((x + 10) * G, y * G)
        self.extra.append(K.w_hlabel(net, *p, 180, shape))
        self.wire(p, q)
        self.label(net, q)

    def note(self, x, y, text):
        self.notes.append((x * G, y * G, text))

    def finish(self):
        assert not set(self.parts) - set(self.placed), set(self.parts) - set(self.placed)
        missing = {
            (r, p["number"])
            for r, c in self.placed.items()
            if not r.startswith("#")
            for p in K.pin_geom(c["lib_id"])
        } - self.connected
        assert not missing, missing
        edges = set()
        for a, b in self.segments:
            pts = sorted(
                {
                    p
                    for p in self.points
                    if (a[0] == b[0] == p[0] and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))
                    or (a[1] == b[1] == p[1] and min(a[0], b[0]) <= p[0] <= max(a[0], b[0]))
                }
            )
            edges.update(zip(pts, pts[1:]))
        from collections import Counter

        degree = Counter(p for e in edges for p in e)
        wiring = "".join(K.w_wire(*a, *b) for a, b in sorted(edges))
        wiring += "".join(K.w_junction(*p) for p, n in degree.items() if n > 2) + "".join(
            self.extra
        )
        self.sh.update(
            comps=[(c, [(self.path, r)]) for r, c in self.placed.items()],
            wiring=wiring,
            notes=self.notes,
        )
        K.write_wired_child(self.sh, self.project, self.root_uuid, self.title, "A3")
