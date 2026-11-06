"""Build presence-pcb.kicad_pcb from the schematic netlist.

Run with KiCad's bundled Python (it provides the pcbnew module):

    kicad-cli sch export netlist --format kicadsexpr -o /tmp/presence.net presence-pcb.kicad_sch
    <KiCad python> scripts/build_board.py /tmp/presence.net

Geometry comes from the Fusion design presence-skeleton (read only; values are
listed in hardware/README.md). Coordinates below are skeleton coordinates in mm:
origin at the radar centre, x to the right, y UP, looking at the front of the
PCB. They are converted to KiCad coordinates (y down) by K().

The script places every footprint, routes the board with a small two-layer grid
router (no autorouter dependency), adds the GND pours, keep-outs and silkscreen,
and saves the board. It is deterministic: re-running it rebuilds the same board.
"""
import heapq
import math
import os
import re
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.normpath(os.path.join(HERE, ".."))
PCB = os.path.join(PROJ, "presence-pcb.kicad_pcb")
STD_FP = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"

# ---------------------------------------------------------------- skeleton --
# presence-skeleton (hardware/README.md): pcb_half_w = ld2460_length/2 + pcb_margin,
# pcb_top = ld2460_width/2 + pcb_margin, pcb_bottom = ld2460_width/2 +
# layout_gap_radar_xiao + xiao_length.
PCB_HALF_W = 26.75
PCB_TOP = 18.0
PCB_BOTTOM = 39.955
HOLE_INSET = 3.0  # pcb_hole_inset
HOLES = [(-PCB_HALF_W + HOLE_INSET, PCB_TOP - HOLE_INSET), (PCB_HALF_W - HOLE_INSET, PCB_TOP - HOLE_INSET),
         (-PCB_HALF_W + HOLE_INSET, -PCB_BOTTOM + HOLE_INSET), (PCB_HALF_W - HOLE_INSET, -PCB_BOTTOM + HOLE_INSET)]
XIAO_CENTRE = (10.0, -29.4775)  # xiao_side_offset, -(ld2460_width/2 + gap + xiao_length/2)
XIAO_HALF = (17.78 / 2, 20.955 / 2)
RADAR_HALF = (49.5 / 2, 32.0 / 2)
J1_CENTRE = (20.75, -0.78)  # LD2460 J1 (2x4) header centre
JP103_CENTRE = (-20.75, -1.31)  # LD2460 JP103 (2x2) header centre
# Antenna zone (sketch "Antenna zone"): on the right inner wall, y -23.75 .. 13.75.
ANT_Y = (-23.75, 13.75)

ORIGIN = (100.0, 100.0)  # KiCad position of the radar centre


def K(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(ORIGIN[0] + x), pcbnew.FromMM(ORIGIN[1] - y))


def W(v):
    """KiCad VECTOR2I -> skeleton (x, y)."""
    return (pcbnew.ToMM(v.x) - ORIGIN[0], ORIGIN[1] - pcbnew.ToMM(v.y))


# ----------------------------------------------------------------- netlist --
def parse_sexpr(text):
    tokens = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack, cur = [], []
    for t in tokens:
        if t == "(":
            stack.append(cur)
            cur = []
        elif t == ")":
            done = cur
            cur = stack.pop()
            cur.append(done)
        else:
            cur.append(t[1:-1] if t.startswith('"') else t)
    return cur[0]


def find(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def val(node, key):
    f = find(node, key)
    return f[0][1] if f else None


def read_netlist(path):
    root = parse_sexpr(open(path).read())
    comps = {}
    for c in find(find(root, "components")[0], "comp"):
        ref = val(c, "ref")
        props = {p[1][1]: p[2][1] for p in find(c, "property") if len(p) > 2}
        comps[ref] = dict(value=val(c, "value"), footprint=val(c, "footprint"),
                          tstamp=val(c, "tstamps"), props=props,
                          datasheet=val(c, "datasheet") or "", description=val(c, "description") or "")
    nets = {}
    for n in find(find(root, "nets")[0], "net"):
        nets[val(n, "name")] = [(val(nd, "ref"), val(nd, "pin")) for nd in find(n, "node")]
    return comps, nets


# --------------------------------------------------------------- placement --
# Each entry: ref -> ("centre", x, y, rot) or ("pads", {pad: (x, y), pad2: (x, y)}).
PLACE = {
    "U1": ("centre", XIAO_CENTRE[0], XIAO_CENTRE[1], 180),  # USB-C down
    "J1": ("centre", J1_CENTRE[0], J1_CENTRE[1], 0),
    "J2": ("centre", JP103_CENTRE[0], JP103_CENTRE[1], 0),
    "H1": ("centre", HOLES[0][0], HOLES[0][1], 0),
    "H2": ("centre", HOLES[1][0], HOLES[1][1], 0),
    "H3": ("centre", HOLES[2][0], HOLES[2][1], 0),
    "H4": ("centre", HOLES[3][0], HOLES[3][1], 0),
    # Hardwired 5 V input at the bottom edge, then the Schottky into VBUS.
    "J5": ("pads", {"1": (-15.0, -37.034), "2": (-17.54, -37.034)}),
    "D1": ("pads", {"1": (-7.0, -37.034), "2": (-11.0, -37.034)}),
    "C5": ("pads", {"1": (-3.2, -37.034), "2": (-3.2, -35.134)}),
    # Qwiic LDO
    "U2": ("centre", -9.0, -31.0, 180),
    "C3": ("pads", {"1": (-5.0, -33.6), "2": (-6.9, -33.6)}),
    "C4": ("pads", {"1": (-12.4, -31.95), "2": (-12.4, -30.05)}),
    # Qwiic socket on the left edge (opening toward the hinge side), 1x4 pads beside it
    "J3": ("centre", -23.32, -27.5, 270),
    "J4": ("pads", {"1": (-17.6, -21.0), "2": (-17.6, -23.54)}),
    "R1": ("pads", {"1": (-14.6, -20.4), "2": (-14.6, -22.3)}),
    "R2": ("pads", {"1": (-12.6, -20.4), "2": (-12.6, -22.3)}),
    # Radar 5 V filter right below JP103 (under the radar, low parts only)
    "C2": ("pads", {"1": (-21.75, -5.25), "2": (-21.75, -7.15)}),
    "C1": ("pads", {"1": (-19.5, -5.25), "2": (-19.5, -7.15)}),
    "FB1": ("pads", {"2": (-17.0, -5.25), "1": (-17.0, -7.15)}),
    # Test pads: spare XIAO pins
    "TP1": ("centre", 24.6, -31.6, 0),  # D0
    "TP2": ("centre", 21.8, -31.6, 0),  # D1
    "TP3": ("centre", 24.2, -29.0, 0),  # D3
    "TP4": ("centre", 24.2, -21.794, 0),  # D6
    "TP5": ("centre", -1.8, -21.794, 0),  # D7
    "TP6": ("centre", -1.8, -29.414, 0),  # D10
    "TP7": ("centre", -1.8, -25.6, 0),  # GND
    "TP8": ("centre", -1.8, -31.954, 0),  # 3V3
}


def load_fp(fpid):
    lib, name = fpid.split(":")
    d = os.path.join(PROJ, "presence.pretty") if lib == "presence" else os.path.join(STD_FP, lib + ".pretty")
    fp = pcbnew.FootprintLoad(d, name)
    if fp is None:
        raise RuntimeError("footprint not found: " + fpid)
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


def pad_world(fp, num):
    for p in fp.Pads():
        if p.GetNumber() == num:
            return W(p.GetPosition())
    raise KeyError(num)


def place(fp, spec):
    if spec[0] == "centre":
        _, x, y, rot = spec
        fp.SetOrientationDegrees(rot)
        fp.SetPosition(K(x, y))
        return
    pads = spec[1]
    (a, pa), (b, pb) = list(pads.items())[:2]
    want = math.atan2(pb[1] - pa[1], pb[0] - pa[0])
    best = None
    for rot in (0, 90, 180, 270):
        fp.SetOrientationDegrees(rot)
        fp.SetPosition(K(0, 0))
        qa, qb = pad_world(fp, a), pad_world(fp, b)
        got = math.atan2(qb[1] - qa[1], qb[0] - qa[0])
        err = abs(math.atan2(math.sin(got - want), math.cos(got - want)))
        if best is None or err < best[0]:
            best = (err, rot)
    fp.SetOrientationDegrees(best[1])
    fp.SetPosition(K(0, 0))
    qa = pad_world(fp, a)
    fp.SetPosition(K(pa[0] - qa[0], pa[1] - qa[1]))


# ------------------------------------------------------------------ router --
RES = 0.1  # grid pitch, mm
CLR = 0.2  # copper clearance (board rule)
MARGIN = 0.08  # extra router margin for grid quantisation
VIA_D, VIA_DRILL = 0.6, 0.3
EDGE_CLR = 0.3
WIDTHS = {"VIN_HW": 0.8, "5V": 0.8, "RADAR_5V": 0.6, "QWIIC_3V3": 0.5, "GND": 0.5}
SIG_W = 0.25

X0, Y0 = -PCB_HALF_W, -PCB_BOTTOM
NX = int(round(2 * PCB_HALF_W / RES)) + 1
NY = int(round((PCB_TOP + PCB_BOTTOM) / RES)) + 1
LAYERS = (pcbnew.F_Cu, pcbnew.B_Cu)


def cell_xy(ix, iy):
    return (X0 + ix * RES, Y0 + iy * RES)


class Shape:
    """Copper (or forbidden area) in skeleton coords: rect, circle or segment."""

    def __init__(self, kind, net, layers, *g):
        self.kind, self.net, self.layers, self.g = kind, net, layers, g

    def bbox(self):
        k, g = self.kind, self.g
        if k == "rect":
            return g
        if k == "circle":
            return (g[0] - g[2], g[1] - g[2], g[0] + g[2], g[1] + g[2])
        x1, y1, x2, y2, r = g
        return (min(x1, x2) - r, min(y1, y2) - r, max(x1, x2) + r, max(y1, y2) + r)

    def dist(self, x, y):
        k, g = self.kind, self.g
        if k == "rect":
            dx = max(g[0] - x, 0, x - g[2])
            dy = max(g[1] - y, 0, y - g[3])
            return math.hypot(dx, dy)
        if k == "circle":
            return max(0.0, math.hypot(x - g[0], y - g[1]) - g[2])
        x1, y1, x2, y2, r = g
        vx, vy = x2 - x1, y2 - y1
        L = vx * vx + vy * vy
        t = 0 if L == 0 else max(0, min(1, ((x - x1) * vx + (y - y1) * vy) / L))
        return max(0.0, math.hypot(x - x1 - t * vx, y - y1 - t * vy) - r)


class Router:
    def __init__(self, board):
        self.board = board
        self.shapes = []  # copper of all nets
        self.forbid = {L: [] for L in LAYERS}  # keep-out shapes per layer (tracks + vias)

    def add_pad_shapes(self):
        for fp in self.board.GetFootprints():
            for p in fp.Pads():
                bb = p.GetBoundingBox()
                (x1, y2), (x2, y1) = W(bb.GetOrigin()), W(bb.GetEnd())
                net = p.GetNetname()
                layers = [L for L in LAYERS if p.IsOnLayer(L)]
                if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    net, layers = "__npth__", list(LAYERS)
                if p.GetShape() == pcbnew.PAD_SHAPE_CIRCLE:
                    cx, cy = W(p.GetPosition())
                    self.shapes.append(Shape("circle", net, layers, cx, cy, (x2 - x1) / 2))
                else:
                    self.shapes.append(Shape("rect", net, layers, x1, min(y1, y2), x2, max(y1, y2)))
                if p.HasHole():  # holes block both layers for other nets
                    cx, cy = W(p.GetPosition())
                    r = pcbnew.ToMM(p.GetDrillSize().x) / 2
                    self.shapes.append(Shape("circle", net, list(LAYERS), cx, cy, r))

    def grid_blocked(self, net, layer, infl):
        g = bytearray(NX * NY)
        lim = EDGE_CLR + infl - CLR  # edge clearance replaces copper clearance
        nb = int(math.ceil(lim / RES)) if lim > 0 else 0
        for iy in range(NY):
            for ix in range(NX):
                if ix < nb or iy < nb or ix >= NX - nb or iy >= NY - nb:
                    g[iy * NX + ix] = 1
        items = [s for s in self.shapes if s.net != net and layer in s.layers]
        items += [(s, True) for s in self.forbid[layer]]
        for it in items:
            s, keep = (it if isinstance(it, tuple) else (it, False))
            d = (infl - CLR) if keep else infl
            x1, y1, x2, y2 = s.bbox()
            ix1 = max(0, int(math.floor((x1 - d - X0) / RES)))
            ix2 = min(NX - 1, int(math.ceil((x2 + d - X0) / RES)))
            iy1 = max(0, int(math.floor((y1 - d - Y0) / RES)))
            iy2 = min(NY - 1, int(math.ceil((y2 + d - Y0) / RES)))
            for iy in range(iy1, iy2 + 1):
                y = Y0 + iy * RES
                row = iy * NX
                for ix in range(ix1, ix2 + 1):
                    if not g[row + ix] and s.dist(X0 + ix * RES, y) < d:
                        g[row + ix] = 1
        return g

    def own_cells(self, net, layer, pads):
        cells = set()
        for (x1, y1, x2, y2) in pads:
            for iy in range(int(math.ceil((y1 - Y0) / RES)), int(math.floor((y2 - Y0) / RES)) + 1):
                for ix in range(int(math.ceil((x1 - X0) / RES)), int(math.floor((x2 - X0) / RES)) + 1):
                    if 0 <= ix < NX and 0 <= iy < NY:
                        cells.add((ix, iy, layer))
        return cells

    def route_net(self, net, pads_by_layer_list, width, via_ok=True, max_expand=3_000_000):
        """pads_by_layer_list: list of pads, each a dict layer -> list of rects (shrunk)."""
        infl = CLR + width / 2 + MARGIN
        blocked = {L: self.grid_blocked(net, L, infl) for L in LAYERS}
        vinfl = CLR + VIA_D / 2 + MARGIN
        vblock = [a | b for a, b in zip(self.grid_blocked(net, LAYERS[0], vinfl),
                                        self.grid_blocked(net, LAYERS[1], vinfl))]
        pad_cells = []
        for pd in pads_by_layer_list:
            cs = set()
            for L, rects in pd.items():
                cs |= self.own_cells(net, L, rects)
            pad_cells.append(cs)
        for cs in pad_cells:
            for (ix, iy, L) in cs:
                blocked[L][iy * NX + ix] = 0
        tree = set(pad_cells[0])
        remaining = list(range(1, len(pad_cells)))
        segs, vias = [], []
        while remaining:
            # nearest remaining pad to the tree (by centroid distance)
            tx = sum(c[0] for c in tree) / len(tree)
            ty = sum(c[1] for c in tree) / len(tree)
            remaining.sort(key=lambda i: min((c[0] - tx) ** 2 + (c[1] - ty) ** 2 for c in pad_cells[i]))
            i = remaining.pop(0)
            if pad_cells[i] & tree:
                tree |= pad_cells[i]
                continue
            path = self.astar(pad_cells[i], tree, blocked, vblock, via_ok, max_expand)
            if path is None:
                raise RuntimeError(f"could not route {net} pad #{i}")
            s, v = self.path_to_segments(path)
            segs += s
            vias += v
            tree |= pad_cells[i]
            tree |= set(path)
        for (a, b, L) in segs:
            self.shapes.append(Shape("seg", net, [L], a[0], a[1], b[0], b[1], width / 2))
        for (x, y) in vias:
            self.shapes.append(Shape("circle", net, list(LAYERS), x, y, VIA_D / 2))
        return segs, vias

    def astar(self, starts, goals, blocked, vblock, via_ok, max_expand):
        gx = [c[0] for c in goals]
        gy = [c[1] for c in goals]
        gminx, gmaxx, gminy, gmaxy = min(gx), max(gx), min(gy), max(gy)

        def h(ix, iy):
            dx = max(gminx - ix, 0, ix - gmaxx)
            dy = max(gminy - iy, 0, iy - gmaxy)
            return (max(dx, dy) + 0.414 * min(dx, dy))

        openh, came, cost = [], {}, {}
        for s in starts:
            cost[s] = 0
            came[s] = None
            heapq.heappush(openh, (h(s[0], s[1]), 0, s))
        moves = [(1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
        n = 0
        while openh:
            f, gc, cur = heapq.heappop(openh)
            if gc > cost.get(cur, 1e18):
                continue
            if cur in goals:
                path = []
                while cur is not None:
                    path.append(cur)
                    cur = came[cur]
                return path[::-1]
            n += 1
            if n > max_expand:
                return None
            ix, iy, L = cur
            nbrs = []
            for dx, dy, c in moves:
                jx, jy = ix + dx, iy + dy
                if 0 <= jx < NX and 0 <= jy < NY and not blocked[L][jy * NX + jx]:
                    if dx and dy and (blocked[L][iy * NX + jx] or blocked[L][jy * NX + ix]):
                        continue
                    # small penalty for changing direction keeps tracks straight
                    pc = came.get(cur)
                    turn = 0
                    if pc is not None and pc[2] == L and (ix - pc[0], iy - pc[1]) != (dx, dy):
                        turn = 0.6
                    # prefer B.Cu for long runs a little less than F.Cu? keep neutral
                    nbrs.append(((jx, jy, L), c + turn))
            if via_ok and not vblock[iy * NX + ix]:
                other = LAYERS[1] if L == LAYERS[0] else LAYERS[0]
                if not blocked[other][iy * NX + ix]:
                    nbrs.append(((ix, iy, other), 25))
            for nxt, c in nbrs:
                ng = gc + c
                if ng < cost.get(nxt, 1e18):
                    cost[nxt] = ng
                    came[nxt] = cur
                    heapq.heappush(openh, (ng + h(nxt[0], nxt[1]), ng, nxt))
        return None

    @staticmethod
    def path_to_segments(path):
        segs, vias = [], []
        i = 0
        while i < len(path) - 1:
            a = path[i]
            if path[i + 1][2] != a[2]:
                vias.append(cell_xy(a[0], a[1]))
                i += 1
                continue
            j = i + 1
            d = (path[j][0] - a[0], path[j][1] - a[1])
            while j + 1 < len(path) and path[j + 1][2] == a[2] and (path[j + 1][0] - path[j][0], path[j + 1][1] - path[j][1]) == d:
                j += 1
            segs.append((cell_xy(a[0], a[1]), cell_xy(path[j][0], path[j][1]), a[2]))
            i = j
        return segs, vias


# ------------------------------------------------------------------- build --
def main(netlist):
    comps, nets = read_netlist(netlist)
    # Start from an empty board every run (removing items from a loaded board
    # upsets the footprint loader); NewBoard keeps the project's design rules.
    board = pcbnew.NewBoard(PCB)

    # Nets
    netobj = {}
    for name in nets:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        netobj[name] = n
    pad_net = {}
    for name, nodes in nets.items():
        for ref, pin in nodes:
            pad_net[(ref, pin)] = name

    # Footprints
    fps = {}
    for ref, c in sorted(comps.items()):
        fp = load_fp(c["footprint"])
        fp.SetReference(ref)
        fp.SetValue(c["value"])
        fp.SetPath(pcbnew.KIID_PATH("/" + c["tstamp"]))
        for k in ("MPN", "LCSC", "Manufacturer"):
            if c["props"].get(k):
                fp.SetField(k, c["props"][k])
                fp.GetField(k).SetVisible(False)
        if ref not in PLACE:
            raise RuntimeError("no placement for " + ref)
        board.Add(fp)
        place(fp, PLACE[ref])
        for p in fp.Pads():
            key = (ref, p.GetNumber())
            if key in pad_net:
                p.SetNet(netobj[pad_net[key]])
        fps[ref] = fp
        fp.SetField("Datasheet", c["datasheet"])
        fp.SetField("Description", c["description"])
        for k in ("Datasheet", "Description"):
            fp.GetField(k).SetVisible(False)
        # Reference designators go on the fab (assembly) layer; the silkscreen
        # carries the hand-placed labels from add_silkscreen() instead.
        fp.Reference().SetLayer(pcbnew.F_Fab)
        fp.Reference().SetVisible(True)
        fp.Value().SetVisible(False)
    for ref in ("TP1", "TP2", "TP3", "TP4", "TP5", "TP6", "TP7", "TP8", "H1", "H2", "H3", "H4"):
        fps[ref].SetAttributes(fps[ref].GetAttributes() | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
    for ref in ("R1", "R2", "J4", "J5"):
        fps[ref].SetDNP(True)

    # Board outline (skeleton "Layout front", PCB rectangle)
    pts = [(-PCB_HALF_W, -PCB_BOTTOM), (PCB_HALF_W, -PCB_BOTTOM), (PCB_HALF_W, PCB_TOP), (-PCB_HALF_W, PCB_TOP)]
    for a, b in zip(pts, pts[1:] + pts[:1]):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(K(*a))
        s.SetEnd(K(*b))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(pcbnew.FromMM(0.1))
        board.Add(s)

    # Keep-out areas
    xiao_ko = (XIAO_CENTRE[0] - XIAO_HALF[0] + 2.9, XIAO_CENTRE[1] - XIAO_HALF[1] + 1.0,
               XIAO_CENTRE[0] + XIAO_HALF[0] - 2.9, XIAO_CENTRE[1] + XIAO_HALF[1] - 1.0)
    ant_ko = (PCB_HALF_W - 5.5, ANT_Y[0] - 2.0, PCB_HALF_W, PCB_TOP)

    def rule_area(rect, layers, tracks, vias, pour, name):
        z = pcbnew.ZONE(board)
        z.SetIsRuleArea(True)
        z.SetZoneName(name)
        ls = pcbnew.LSET()
        for L in layers:
            ls.AddLayer(L)
        z.SetLayerSet(ls)
        z.SetDoNotAllowTracks(tracks)
        z.SetDoNotAllowVias(vias)
        z.SetDoNotAllowZoneFills(pour)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        o = z.Outline()
        o.NewOutline()
        x1, y1, x2, y2 = rect
        for (x, y) in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
            o.Append(K(x, y))
        board.Add(z)

    rule_area(xiao_ko, [pcbnew.F_Cu], True, True, True, "XIAO underside: no exposed copper features")
    rule_area(ant_ko, [pcbnew.F_Cu, pcbnew.B_Cu], False, False, True, "Antenna side: no copper pour")

    router = Router(board)
    router.add_pad_shapes()
    router.forbid[pcbnew.F_Cu].append(Shape("rect", None, [pcbnew.F_Cu], *xiao_ko))

    # Pads per net, shrunk a little so routes enter from inside
    def pads_of(net):
        out = []
        for ref, pin in nets[net]:
            if ref.startswith("#"):
                continue
            for p in fps[ref].Pads():
                if p.GetNumber() != pin:
                    continue
                bb = p.GetBoundingBox()
                (x1, y2), (x2, y1) = W(bb.GetOrigin()), W(bb.GetEnd())
                cx, cy = W(p.GetPosition())
                hw = min(0.25, (x2 - x1) / 4)
                hh = min(0.25, (max(y1, y2) - min(y1, y2)) / 4)
                r = [(cx - hw, cy - hh, cx + hw, cy + hh)]
                out.append({L: r for L in LAYERS if p.IsOnLayer(L)})
        return out

    order = ["VIN_HW", "5V", "RADAR_5V", "QWIIC_3V3", "D8", "D9", "D4", "D5",
             "D0", "D1", "D3", "D6", "D7", "D10", "3V3"]
    netname = {}
    for full in nets:
        netname[full.lstrip("/")] = full
    for short in order:
        full = netname[short]
        w = WIDTHS.get(short, SIG_W)
        segs, vias = router.route_net(full, pads_of(full), w)
        for (a, b, L) in segs:
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(K(*a))
            t.SetEnd(K(*b))
            t.SetWidth(pcbnew.FromMM(w))
            t.SetLayer(L)
            t.SetNet(netobj[full])
            board.Add(t)
        for (x, y) in vias:
            add_via(board, x, y, netobj[full])
        print(f"routed {short}: {len(segs)} segments, {len(vias)} vias")

    # GND: every SMD GND pad gets a short track to its own via into the B.Cu plane.
    gnd = netname["GND"]
    for ref, pin in nets[gnd]:
        if ref.startswith("#"):
            continue
        for p in fps[ref].Pads():
            if p.GetNumber() != pin or p.HasHole():
                continue
            cx, cy = W(p.GetPosition())
            seg, vxy = route_to_via(router, gnd, (cx, cy))
            for (a, b, L) in seg:
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(K(*a))
                t.SetEnd(K(*b))
                t.SetWidth(pcbnew.FromMM(WIDTHS["GND"]))
                t.SetLayer(L)
                t.SetNet(netobj[gnd])
                board.Add(t)
            add_via(board, vxy[0], vxy[1], netobj[gnd])

    # Stitching vias on a grid where there is room on both layers
    vinfl = CLR + VIA_D / 2 + 0.3
    gb = [a | b for a, b in zip(router.grid_blocked(gnd, LAYERS[0], vinfl), router.grid_blocked(gnd, LAYERS[1], vinfl))]
    n = 0
    y = -PCB_BOTTOM + 3.0
    while y < PCB_TOP - 2.0:
        x = -PCB_HALF_W + 3.0
        while x < PCB_HALF_W - 2.0:
            inside_ko = (xiao_ko[0] - 0.5 <= x <= xiao_ko[2] + 0.5 and xiao_ko[1] - 0.5 <= y <= xiao_ko[3] + 0.5) or \
                        (ant_ko[0] - 1.0 <= x and ant_ko[1] - 1.0 <= y)
            ix, iy = int(round((x - X0) / RES)), int(round((y - Y0) / RES))
            if not inside_ko and not gb[iy * NX + ix]:
                add_via(board, x, y, netobj[gnd])
                router.shapes.append(Shape("circle", gnd, list(LAYERS), x, y, VIA_D / 2))
                n += 1
            x += 4.0
        y += 4.0
    print("stitching vias:", n)

    # GND pours, both layers, everywhere except the keep-outs above
    for L in LAYERS:
        z = pcbnew.ZONE(board)
        z.SetLayer(L)
        z.SetNet(netobj[gnd])
        z.SetZoneName("GND " + ("front" if L == pcbnew.F_Cu else "back"))
        z.SetLocalClearance(pcbnew.FromMM(0.25))
        z.SetMinThickness(pcbnew.FromMM(0.25))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(pcbnew.FromMM(0.3))
        z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.4))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        o = z.Outline()
        o.NewOutline()
        for (x, y) in pts:
            o.Append(K(x, y))
        board.Add(z)

    add_silkscreen(board)
    # Drill/place origin at the bottom-left board corner (used by the fab exports)
    board.GetDesignSettings().SetAuxOrigin(K(-PCB_HALF_W, -PCB_BOTTOM))
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(PCB, board)
    print("saved", PCB)


def add_via(board, x, y, net):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(K(x, y))
    v.SetDrill(pcbnew.FromMM(VIA_DRILL))
    v.SetWidth(pcbnew.FromMM(VIA_D))
    v.SetNet(net)
    board.Add(v)


def route_to_via(router, net, xy):
    """Shortest F.Cu track from an SMD pad centre to a spot where a via fits."""
    w = WIDTHS["GND"]
    blocked = router.grid_blocked(net, pcbnew.F_Cu, CLR + w / 2 + MARGIN)
    vinfl = CLR + VIA_D / 2 + MARGIN
    vb = [a | b for a, b in zip(router.grid_blocked(net, LAYERS[0], vinfl), router.grid_blocked(net, LAYERS[1], vinfl))]
    sx, sy = int(round((xy[0] - X0) / RES)), int(round((xy[1] - Y0) / RES))
    blocked[sy * NX + sx] = 0
    from collections import deque
    q = deque([(sx, sy)])
    prev = {(sx, sy): None}
    while q:
        c = q.popleft()
        d0 = math.hypot(c[0] - sx, c[1] - sy) * RES
        if not vb[c[1] * NX + c[0]] and d0 >= 0.9:
            path = []
            while c is not None:
                path.append(c)
                c = prev[c]
            path = path[::-1]
            a, b = cell_xy(*path[0]), cell_xy(*path[-1])
            # straight segment from pad centre to via (BFS path is near-straight;
            # verify the straight line stays clear, else follow the BFS path)
            segs = []
            pts = [cell_xy(*p) for p in path]
            segs.append((a, b, pcbnew.F_Cu))
            if not straight_clear(blocked, a, b):
                segs = [(pts[i], pts[i + 1], pcbnew.F_Cu) for i in range(len(pts) - 1)]
            router.shapes.append(Shape("seg", net, [pcbnew.F_Cu], a[0], a[1], b[0], b[1], w / 2))
            router.shapes.append(Shape("circle", net, list(LAYERS), b[0], b[1], VIA_D / 2))
            return segs, b
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (c[0] + dx, c[1] + dy)
            if 0 <= n[0] < NX and 0 <= n[1] < NY and n not in prev and not blocked[n[1] * NX + n[0]]:
                prev[n] = c
                q.append(n)
    raise RuntimeError("no via spot near %r" % (xy,))


def straight_clear(blocked, a, b):
    n = int(math.hypot(b[0] - a[0], b[1] - a[1]) / (RES / 2)) + 1
    for i in range(n + 1):
        t = i / n
        x, y = a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])
        ix, iy = int(round((x - X0) / RES)), int(round((y - Y0) / RES))
        if blocked[iy * NX + ix]:
            return False
    return True


def text(board, s, x, y, size=0.8, layer=pcbnew.F_SilkS, rot=0, mirror=False):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(K(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
    t.SetTextThickness(pcbnew.FromMM(size * 0.15))
    t.SetTextAngleDegrees(rot)
    t.SetMirrored(mirror)
    board.Add(t)


def add_silkscreen(board):
    # Radar outline on the fab layer, so placement is easy to check.
    pts = [(-RADAR_HALF[0], -RADAR_HALF[1]), (RADAR_HALF[0], -RADAR_HALF[1]),
           (RADAR_HALF[0], RADAR_HALF[1]), (-RADAR_HALF[0], RADAR_HALF[1])]
    for a, b in zip(pts, pts[1:] + pts[:1]):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(K(*a))
        s.SetEnd(K(*b))
        s.SetLayer(pcbnew.F_Fab)
        s.SetWidth(pcbnew.FromMM(0.1))
        board.Add(s)
    text(board, "HLK-LD2460 (antennas face out)", 0, 11.0, 1.0, pcbnew.F_Fab)
    text(board, "LD2460", 0, 6.0, 1.2)
    text(board, "J1: Tx2>D9  Rx2<D8", 9.0, 3.2, 0.8)
    text(board, "JP103: 5V GND", -12.0, 3.2, 0.8)
    text(board, "XIAO ESP32-S3", 10.0, -17.3, 0.8)
    text(board, "USB-C", 10.0, -39.0, 0.8)
    text(board, "QWIIC 3V3", -23.0, -32.4, 0.8)
    text(board, "GND 3V3 D4 D5", -17.6, -18.6, 0.8)
    text(board, "+5V", -15.0, -34.6, 0.8)
    text(board, "GND", -17.54, -34.6, 0.8)
    text(board, "5V IN", -16.3, -39.0, 0.8)
    for (s, x, y) in (("D0", 24.6, -33.2), ("D1", 21.8, -33.2), ("D3", 24.2, -27.4), ("D6", 24.2, -20.2),
                      ("D7", -3.6, -21.794), ("D10", -3.9, -29.414), ("GND", -3.9, -25.6), ("3V3", -3.9, -31.954)):
        text(board, s, x, y, 0.8)
    text(board, "presence v1", 0, 16.0, 1.0, pcbnew.B_SilkS, mirror=True)
    text(board, "github.com/joshuata/impresence-esphome", 0, 14.0, 0.8, pcbnew.B_SilkS, mirror=True)
    text(board, "CERN-OHL-S-2.0", 0, 12.2, 0.8, pcbnew.B_SilkS, mirror=True)


if __name__ == "__main__":
    main(sys.argv[1])
