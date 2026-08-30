"""BASE Meridion Kurdish - symbol construction toolkit (v1.013).

Draws the missing symbol set directly in the family's measured design
constants so new glyphs sit beside the existing ones without a style break.

Constants were measured from the shipped Regular master:
  * symbol stroke ......... 119 units (minus bar, arrow shaft, notequal bar)
  * symbol optical centre .. x=635, y=717 (arrow shafts, bullet)
  * math axis ............. y=675 (centre of U+2212 / en dash)
  * default advance ....... 1270 (28 existing symbol glyphs)
  * figure height ......... 1409 flat / 1430 round, overshoot -20
  * x-height / cap ........ 638 / 951

Only stdlib + fontTools + skia-pathops required.
"""
from __future__ import annotations

import math

import pathops
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib.tables._g_l_y_f import Glyph

# --------------------------------------------------------------------------- #
# Measured family constants
# --------------------------------------------------------------------------- #
STROKE = 119          # primary symbol stroke
HAIR = 96             # lighter stroke for small / secondary elements
CX, CY = 635, 717     # symbol optical centre
MATH_AXIS = 675
ADV = 1270            # default symbol advance
FIG_TOP = 1409        # flat figure height
OVER = 20             # round overshoot
CAP = 951
XH = 638
K = 0.5522847498      # circle bezier constant


# --------------------------------------------------------------------------- #
# Path primitives (all return pathops.Path in font units, y up)
# --------------------------------------------------------------------------- #
def P() -> pathops.Path:
    return pathops.Path()


def rect(x0, y0, x1, y1) -> pathops.Path:
    p = P()
    q = p.getPen()
    q.moveTo((x0, y0))
    q.lineTo((x1, y0))
    q.lineTo((x1, y1))
    q.lineTo((x0, y1))
    q.closePath()
    return p


def poly(points) -> pathops.Path:
    p = P()
    q = p.getPen()
    q.moveTo((points[0][0], points[0][1]))
    for pt in points[1:]:
        q.lineTo((pt[0], pt[1]))
    q.closePath()
    return p


def ellipse(cx, cy, rx, ry) -> pathops.Path:
    ox, oy = rx * K, ry * K
    p = P()
    q = p.getPen()
    q.moveTo((cx, cy + ry))
    q.curveTo((cx + ox, cy + ry), (cx + rx, cy + oy), (cx + rx, cy))
    q.curveTo((cx + rx, cy - oy), (cx + ox, cy - ry), (cx, cy - ry))
    q.curveTo((cx - ox, cy - ry), (cx - rx, cy - oy), (cx - rx, cy))
    q.curveTo((cx - rx, cy + oy), (cx - ox, cy + ry), (cx, cy + ry))
    q.closePath()
    return p


def circle(cx, cy, r) -> pathops.Path:
    return ellipse(cx, cy, r, r)


def bar(x0, x1, y=MATH_AXIS, w=STROKE) -> pathops.Path:
    return rect(x0, y - w / 2.0, x1, y + w / 2.0)


def vbar(y0, y1, x=CX, w=STROKE) -> pathops.Path:
    return rect(x - w / 2.0, y0, x + w / 2.0, y1)


def seg(p0, p1, w=STROKE, cap="butt") -> pathops.Path:
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy)
    if ln == 0:
        return P()
    ux, uy = dx / ln, dy / ln
    if cap == "square":
        x0 -= ux * w / 2.0
        y0 -= uy * w / 2.0
        x1 += ux * w / 2.0
        y1 += uy * w / 2.0
    nx, ny = -uy * w / 2.0, ux * w / 2.0
    body = poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny),
                 (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)])
    if cap == "round":
        body = union(body, circle(x0, y0, w / 2.0))
        body = union(body, circle(x1, y1, w / 2.0))
    return body


def polyline(points, w=STROKE, cap="butt", join_round=True) -> pathops.Path:
    out = P()
    for a, b in zip(points, points[1:]):
        out = union(out, seg(a, b, w, cap))
    if join_round and len(points) > 2:
        for pt in points[1:-1]:
            out = union(out, circle(pt[0], pt[1], w / 2.0))
    return out


def star(cx, cy, r_out, r_in, points=5, rot=90.0) -> pathops.Path:
    pts = []
    for i in range(points * 2):
        a = math.radians(rot + i * 180.0 / points)
        r = r_out if i % 2 == 0 else r_in
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return poly(pts)


def arc_stroke(cx, cy, r, a0, a1, w, steps=56) -> pathops.Path:
    inner, outer = r - w / 2.0, r + w / 2.0
    pts = []
    n = max(6, steps)
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + outer * math.cos(a), cy + outer * math.sin(a)))
    for i in range(n, -1, -1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + inner * math.cos(a), cy + inner * math.sin(a)))
    return poly(pts)


def earc_stroke(cx, cy, rx, ry, a0, a1, w, steps=64) -> pathops.Path:
    """Stroked elliptical arc - the workhorse for bowls and S curves."""
    pts = []
    n = max(8, steps)
    hw = w / 2.0
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + (rx + hw) * math.cos(a), cy + (ry + hw) * math.sin(a)))
    for i in range(n, -1, -1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + (rx - hw) * math.cos(a), cy + (ry - hw) * math.sin(a)))
    return poly(pts)


def ring(cx, cy, r_outer, w) -> pathops.Path:
    return diff(circle(cx, cy, r_outer), circle(cx, cy, r_outer - w))


def ering(cx, cy, rx, ry, w) -> pathops.Path:
    return diff(ellipse(cx, cy, rx, ry), ellipse(cx, cy, rx - w, ry - w))


# --------------------------------------------------------------------------- #
# Boolean / transform helpers
# --------------------------------------------------------------------------- #
def _op(a, b, op):
    aa = pathops.Path(a)
    aa.simplify(fix_winding=True)
    bb = pathops.Path(b)
    bb.simplify(fix_winding=True)
    r = pathops.op(aa, bb, op, fix_winding=True)
    r.simplify(fix_winding=True)
    return r


def union(a, b):
    return _op(a, b, pathops.PathOp.UNION)


def diff(a, b):
    return _op(a, b, pathops.PathOp.DIFFERENCE)


def isect(a, b):
    return _op(a, b, pathops.PathOp.INTERSECTION)


def unions(*paths):
    out = P()
    for p in paths:
        out = union(out, p)
    return out


def xform(path, sx=1.0, sy=1.0, dx=0.0, dy=0.0, rot=0.0, ox=0.0, oy=0.0):
    """Scale then rotate about (ox, oy), then translate by (dx, dy)."""
    out = P()
    pen = out.getPen()
    ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def tf(pt):
        x, y = pt[0] - ox, pt[1] - oy
        x, y = x * sx, y * sy
        x, y = x * ca - y * sa, x * sa + y * ca
        return (x + ox + dx, y + oy + dy)

    for verb, pts in path.segments:
        if verb == "moveTo":
            pen.moveTo(tf(pts[0]))
        elif verb == "lineTo":
            pen.lineTo(tf(pts[0]))
        elif verb == "curveTo":
            pen.curveTo(*[tf(p) for p in pts])
        elif verb == "qCurveTo":
            pen.qCurveTo(*[tf(p) for p in pts])
        elif verb == "closePath":
            pen.closePath()
        elif verb == "endPath":
            pen.endPath()
    out.simplify(fix_winding=True)
    return out


def translate(path, dx, dy):
    return xform(path, dx=dx, dy=dy)


def mirror_x(path, axis=CX):
    return xform(path, sx=-1.0, ox=axis, oy=0.0)


def mirror_y(path, axis=CY):
    return xform(path, sy=-1.0, ox=0.0, oy=axis)


def rotate(path, deg, ox=CX, oy=CY):
    return xform(path, rot=deg, ox=ox, oy=oy)


def scale_about(path, s, ox=CX, oy=CY):
    return xform(path, sx=s, sy=s, ox=ox, oy=oy)


def center_to(path, cx=CX, cy=CY):
    b = path.bounds
    if b is None:
        return path
    return translate(path, cx - (b[0] + b[2]) / 2.0, cy - (b[1] + b[3]) / 2.0)


def fit_height(path, height, cy=CY):
    b = path.bounds
    if b is None or b[3] - b[1] == 0:
        return path
    s = height / (b[3] - b[1])
    return center_to(scale_about(path, s, (b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0),
                     (b[0] + b[2]) / 2.0, cy)


def width_of(path):
    b = path.bounds
    return 0 if b is None else b[2] - b[0]


def place_lsb(path, lsb):
    b = path.bounds
    if b is None:
        return path
    return translate(path, lsb - b[0], 0)


# --------------------------------------------------------------------------- #
# Glyph installation
# --------------------------------------------------------------------------- #
def path_to_glyph(path) -> Glyph:
    p = pathops.Path(path)
    p.simplify(fix_winding=True)
    p.convertConicsToQuads(0.2)
    pen = TTGlyphPen(glyphSet=None)
    p.draw(Cu2QuPen(pen, max_err=0.8, reverse_direction=True))
    return pen.glyph()


def glyph_path(font, name) -> pathops.Path:
    """Extract an existing glyph as a path, decomposing components."""
    gs = font.getGlyphSet()
    p = P()
    gs[name].draw(p.getPen(glyphSet=gs))
    p.simplify(fix_winding=True)
    return p


def _ensure_name(font, name):
    if name not in font.getGlyphOrder():
        order = list(font.getGlyphOrder())
        order.append(name)
        font.setGlyphOrder(order)


def map_codepoint(font, cp, name):
    for table in font["cmap"].tables:
        if table.platformID not in (0, 3):
            continue
        if table.format == 4 and cp > 0xFFFF:
            continue
        if table.format in (0, 4, 6, 12):
            table.cmap[cp] = name


def install(font, name, path, advance=ADV, codepoint=None, lsb=None):
    glyf = font["glyf"]
    g = path_to_glyph(path)
    _ensure_name(font, name)
    glyf[name] = g
    g.recalcBounds(glyf)
    side = lsb if lsb is not None else (g.xMin if g.numberOfContours else 0)
    font["hmtx"].metrics[name] = (int(round(advance)), int(round(side)))
    if codepoint is not None:
        map_codepoint(font, codepoint, name)
    return name


def install_blank(font, name, advance, codepoint=None):
    g = Glyph()
    g.numberOfContours = 0
    g.xMin = g.yMin = g.xMax = g.yMax = 0
    _ensure_name(font, name)
    font["glyf"][name] = g
    font["hmtx"].metrics[name] = (int(round(advance)), 0)
    if codepoint is not None:
        map_codepoint(font, codepoint, name)
    return name


def install_alias(font, name, source_name, codepoint, advance=None):
    """Reuse an existing outline under a new name/codepoint."""
    glyf = font["glyf"]
    if source_name not in glyf:
        return None
    import copy as _copy
    _ensure_name(font, name)
    glyf[name] = _copy.deepcopy(glyf[source_name])
    adv, side = font["hmtx"].metrics[source_name]
    font["hmtx"].metrics[name] = (int(advance) if advance else adv, side)
    map_codepoint(font, codepoint, name)
    return name
