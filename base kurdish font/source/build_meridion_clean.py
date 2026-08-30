"""BASE Meridion Kurdish - clean family rebuild (v1.013).

This rebuild starts from the already-correct Regular master (whose Kurdish
letters are imported "same same" from letter fixing.pdf) and:

  1. Regenerates Medium / SemiBold / Bold with a clean stroke-outset weight
     (skia-pathops), replacing the previous faux-bold that produced lumpy,
     self-intersecting, ~9x-bloated outlines.
  2. Fixes the family naming so the typographic family is exactly
     "BASE Meridion Kurdish" and the weight names are sub-styles, with a valid
     RIBBI split and no leftover 'Base-Kurdish' WWS name.

Version 1.011 repairs three Kurdish targets in the Regular master before
the weight family is generated:

  * U+06B5 (ڵ): replace the malformed enlarged plain lam with the correct lam
    body plus its small-V mark.
  * U+0645 (م): restore the canonical connector band across joined forms.
  * U+0695 (ڕ): rebuild from this family's corrected reh body plus the existing
    small-V-below mark.

Version 1.012 restores the supplied PDF isolated meem at full size and gives it
Arabic/Kurdish reference spacing. This fixes word-end placement after Kurdish
non-joiners while retaining correct Unicode joining behavior.

Version 1.013 does two things:

  * Rebuilds the isolated meem (U+0645 / U+FEE1). What 1.012 shipped there was
    a foreign outline drawn at roughly half the family's stroke weight (pen ~53
    against a family norm of ~110), with a head counter of 254x145 where every
    other meem form - and the font's own untouched meem drawings glyph00100 /
    glyph00104 / uniFCCC - carry ~390x368 at y[127,495]. Kurdish spells a large
    share of its words with a final م after a non-joiner (ە و ر ا د ز ژ), and
    that is precisely the context which selects the isolated form, so the thin
    glyph is what readers saw at the end of words. It is replaced by this
    family's own isolated meem, fitted to the canonical head top of 636 - the
    same treatment the joined forms already had - and given family sidebearings.
  * Adds the missing symbol set (see meridion_symbol_set.py): punctuation,
    superior/inferior figures, vulgar fractions, maths, arrows, geometric
    shapes, ticks and boxes, letterlike marks, currency and Arabic signs.

Only stdlib + fontTools + skia-pathops + uharfbuzz required.
"""
from __future__ import annotations

import copy
import hashlib
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path

import pathops
import uharfbuzz as hb
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from meridion_symbol_set import (  # noqa: E402
    REQUIRED_SYMBOLS, SPACE_CODEPOINTS, build_symbols,
)

ROOT = Path(__file__).resolve().parents[1]
REGULAR_SRC = ROOT / "fonts" / "BASEMeridionKurdish-Regular.ttf"
# Pristine 1.010 master, kept in-tree so the meem rebuild is reproducible: it
# is the last build that still holds the family-weight isolated meem outline.
REFERENCE_SRC = ROOT / "source" / "reference" / "BASEMeridionKurdish-1.010-Regular.ttf"

FAMILY = "BASE Meridion Kurdish"
FILE_FAMILY = "BASEMeridionKurdish"
PACKAGE_STEM = "BASE-Meridion-Kurdish"
VERSION = "1.013"

# Canonical meem metrics, cross-checked against the font's own untouched meem
# drawings (glyph00100, glyph00104, uniFCCC) which no build has ever altered.
MEEM_HEAD_TOP = 636
MEEM_ISOLATED_RSB = 90
# OpenType timestamps count seconds from 1904-01-01. Pin the release build to
# 2026-08-18 00:00:00 UTC so repeated builds are byte-for-byte reproducible.
BUILD_TIMESTAMP = 3869856000
# Smooth mode: skip the geometric PDF joined-form transplants and keep the base
# font's smooth/flowing connected shapes (user pivoted to the smooth reference).
SMOOTH = True

# Build into a staging directory. Final binaries are copied into ``fonts/``
# only after shaping, table, and visual QA pass.
DIST = ROOT / "build" / f"{PACKAGE_STEM}-{VERSION}"
FONTS = DIST / "fonts"
DOCS = DIST / "documentation"
SOURCE = DIST / "source"
SPECIMEN = DIST / "specimen"


@dataclass(frozen=True)
class Style:
    label: str          # typographic subfamily (ID17)
    weight: int         # usWeightClass
    dilate: float       # stroke-outset radius in font units (0 = keep master)

    @property
    def stem(self) -> str:
        return f"{FILE_FAMILY}-{self.label}"

    @property
    def full(self) -> str:
        return f"{FAMILY} {self.label}"


STYLES = [
    Style("Regular", 400, 0.0),
    Style("Medium", 500, 14.0),
    Style("SemiBold", 600, 26.0),
    Style("Bold", 700, 40.0),
]


# --------------------------------------------------------------------------- #
# Clean weight generation
# --------------------------------------------------------------------------- #
def dilate_glyph(glyphset, gname, r):
    """Grow a glyph outward by r units using a centered stroke unioned with the
    fill. Produces a clean, self-intersection-free heavier outline."""
    fill = pathops.Path()
    glyphset[gname].draw(fill.getPen(glyphSet=glyphset))
    fill.simplify()

    stroked = pathops.Path()
    glyphset[gname].draw(stroked.getPen(glyphSet=glyphset))
    stroked.stroke(2 * r, pathops.LineCap.ROUND_CAP, pathops.LineJoin.ROUND_JOIN, 4.0)
    stroked.convertConicsToQuads(0.2)
    fill.convertConicsToQuads(0.2)

    result = pathops.op(fill, stroked, pathops.PathOp.UNION, fix_winding=True)
    result.simplify(fix_winding=True)

    ttpen = TTGlyphPen(glyphSet=None)
    result.draw(Cu2QuPen(ttpen, max_err=1.0, reverse_direction=True))
    return ttpen.glyph()


# --------------------------------------------------------------------------- #
# Round heh family (match the PDF isolated heh style in joined forms)
# --------------------------------------------------------------------------- #
# The base font's connected heh forms are a traditional naskh knot (uniFEEC) that
# clashes with the clean round isolated heh from the PDF. Rebuild the joined heh
# forms as the PDF round loop + baseline connectors so words match the design.
# Connection band measured from the base medial glyphs: y in [0, 150].
_CONN_Y0, _CONN_Y1 = 0, 150

_HEH_GROUPS = {
    "uni0647": {"init": "uniFEEB", "medi": "uniFEEC", "fina": "uniFEEA"},   # heh
    "uni06BE": {"init": "uniFBAC", "medi": "uniFBAD", "fina": "uniFBAB"},   # heh doachashmee
}
# ae (Kurdish 'e') final form glyph — non-joining left, connects on the right.
_AE_ISO, _AE_FINA = "uni06D5", "glyph00572"


def _loop_path(glyf, glyphset, iso_name, target_h, cx, y_bottom):
    gi = glyf[iso_name]
    gi.recalcBounds(glyf)
    h = gi.yMax - gi.yMin
    w = gi.xMax - gi.xMin
    s = target_h / h
    lw = w * s
    lx = cx - lw / 2
    rec = RecordingPen()
    glyphset[iso_name].draw(rec)
    path = pathops.Path()
    pen = path.getPen(glyphSet=glyphset)

    def tf(x, y):
        return ((x - gi.xMin) * s + lx, (y - gi.yMin) * s + y_bottom)

    class _T:
        def moveTo(self, p): pen.moveTo(tf(*p))
        def lineTo(self, p): pen.lineTo(tf(*p))
        def qCurveTo(self, *pts): pen.qCurveTo(*[tf(*q) if q else None for q in pts])
        def curveTo(self, *pts): pen.curveTo(*[tf(*q) for q in pts])
        def closePath(self): pen.closePath()
        def endPath(self):
            try:
                pen.endPath()
            except Exception:
                pass

    rec.replay(_T())
    path.simplify()
    return path, lw


def _bar(x0, x1):
    p = pathops.Path()
    pen = p.getPen(glyphSet=None)
    pen.moveTo((x0, _CONN_Y0)); pen.lineTo((x1, _CONN_Y0))
    pen.lineTo((x1, _CONN_Y1)); pen.lineTo((x0, _CONN_Y1)); pen.closePath()
    return p


def _build_connected(glyf, glyphset, iso_name, kind, advance, target_h=650):
    cx = advance / 2
    loop, lw = _loop_path(glyf, glyphset, iso_name, target_h, cx, 0)
    res = loop
    if kind in ("medi", "init"):    # exit to the next letter -> LEFT edge
        res = pathops.op(res, _bar(-35, cx + lw * 0.15), pathops.PathOp.UNION, fix_winding=True)
    if kind in ("medi", "fina"):    # entry from previous letter -> RIGHT edge
        res = pathops.op(res, _bar(cx - lw * 0.15, advance + 35), pathops.PathOp.UNION, fix_winding=True)
    res.simplify(fix_winding=True)
    tt = TTGlyphPen(None)
    res.draw(Cu2QuPen(tt, max_err=1.0, reverse_direction=True))
    g = tt.glyph()
    g.recalcBounds(glyf)
    return g


def fix_heh_forms(font: TTFont) -> int:
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    glyphset = font.getGlyphSet()
    count = 0
    for iso, forms in _HEH_GROUPS.items():
        if iso not in glyf:
            continue
        for kind, gn in forms.items():
            if gn in glyf:
                adv = hmtx.metrics[gn][0]
                glyf[gn] = _build_connected(glyf, glyphset, iso, kind, adv)
                hmtx.metrics[gn] = (adv, glyf[gn].xMin)
                count += 1
    if _AE_FINA in glyf and _AE_ISO in glyf:
        adv = hmtx.metrics[_AE_FINA][0]
        glyf[_AE_FINA] = _build_connected(glyf, glyphset, _AE_ISO, "fina", adv)
        hmtx.metrics[_AE_FINA] = (adv, glyf[_AE_FINA].xMin)
        count += 1
    return count


# --------------------------------------------------------------------------- #
# Feh/qaf-style loop-head transplant: put the PDF isolated head into the joined
# forms so the body curves match the isolated design (not the base font).
# --------------------------------------------------------------------------- #
def _iso_pathops(glyphset, gn):
    p = pathops.Path()
    glyphset[gn].draw(p.getPen(glyphSet=glyphset))
    p.simplify()
    return p


def _rect(x0, y0, x1, y1):
    p = pathops.Path()
    pen = p.getPen(glyphSet=None)
    pen.moveTo((x0, y0)); pen.lineTo((x1, y0)); pen.lineTo((x1, y1)); pen.lineTo((x0, y1)); pen.closePath()
    return p


class _Trans:
    def __init__(self, pen, dx, dy):
        self.pen, self.dx, self.dy = pen, dx, dy
    def moveTo(self, p): self.pen.moveTo((p[0] + self.dx, p[1] + self.dy))
    def lineTo(self, p): self.pen.lineTo((p[0] + self.dx, p[1] + self.dy))
    def qCurveTo(self, *pts): self.pen.qCurveTo(*[(q[0] + self.dx, q[1] + self.dy) if q else None for q in pts])
    def curveTo(self, *pts): self.pen.curveTo(*[(q[0] + self.dx, q[1] + self.dy) for q in pts])
    def closePath(self): self.pen.closePath()
    def endPath(self):
        try:
            self.pen.endPath()
        except Exception:
            pass


def _translate(path, dx, dy):
    out = pathops.Path()
    path.draw(_Trans(out.getPen(glyphSet=None), dx, dy))
    return out


def _to_glyph(glyf, path):
    tt = TTGlyphPen(None)
    path.draw(Cu2QuPen(tt, max_err=1.0, reverse_direction=True))
    g = tt.glyph()
    g.recalcBounds(glyf)
    return g


def fix_feh_forms(font: TTFont) -> int:
    """Feh (ف). init/medi: transplant the PDF isolated head loop + connectors.
    fina: keep the exact isolated glyph (tail + head + dot) and add a right
    connector, so final feh matches the isolated design exactly."""
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    glyphset = font.getGlyphSet()
    cmap = font.getBestCmap()
    if 0x0641 not in cmap:
        return 0
    feh = cmap[0x0641]
    iso = _iso_pathops(glyphset, feh)
    head = pathops.op(iso, _rect(1150, -60, 1980, 1260), pathops.PathOp.INTERSECTION, fix_winding=True)
    head.simplify(fix_winding=True)
    hb = head.bounds
    count = 0

    def init_medi(kind, adv):
        dx = (adv - 40) - hb[2]
        h = _translate(head, dx, 0)
        hx0, hx1 = hb[0] + dx, hb[2] + dx
        res = h
        if kind in ("init", "medi"):
            res = pathops.op(res, _rect(-35, 0, hx0 + 120, 150), pathops.PathOp.UNION, fix_winding=True)
        if kind == "medi":
            res = pathops.op(res, _rect(hx1 - 120, 0, adv + 35, 150), pathops.PathOp.UNION, fix_winding=True)
        res.simplify(fix_winding=True)
        return _to_glyph(glyf, res)

    for kind, gn in [("init", "uniFED3"), ("medi", "uniFED4")]:
        if gn in glyf:
            adv = hmtx.metrics[gn][0]
            glyf[gn] = init_medi(kind, adv)
            hmtx.metrics[gn] = (adv, glyf[gn].xMin)
            count += 1
    # final = isolated feh + right connector (exact isolated body)
    gn = "uniFED2"
    if gn in glyf:
        adv = hmtx.metrics[gn][0]
        base = _iso_pathops(glyphset, feh)
        ib = base.bounds
        res = pathops.op(base, _rect(ib[2] - 160, 0, adv + 35, 150), pathops.PathOp.UNION, fix_winding=True)
        res.simplify(fix_winding=True)
        glyf[gn] = _to_glyph(glyf, res)
        hmtx.metrics[gn] = (adv, glyf[gn].xMin)
        count += 1
    return count


# --------------------------------------------------------------------------- #
# General body transplant: keep the PDF isolated body, drop the isolated tail
# (via a clip), reposition, and add baseline connectors. Used for letters whose
# body sits at a consistent height across forms (humps / loop heads).
#   clip_gt_x : keep isolated ink with x > this value (drops a left/low-x tail)
# --------------------------------------------------------------------------- #
# codepoint: (forms, clip_mode, clip_value, dy_body)
#   clip_mode "gtx" keeps isolated ink with x > value (drops a low-x tail);
#   "gty" keeps ink with y > value (used to lift a head off its descender).
#   dy_body shifts the extracted body vertically (meem head down to baseline).
_TRANSPLANTS = {
    0x0633: ({"init": "uniFEB3", "medi": "uniFEB4", "fina": "uniFEB2"}, "gtx", 560, 0),    # seen
    0x0634: ({"init": "uniFEB7", "medi": "uniFEB8", "fina": "uniFEB6"}, "gtx", 560, 0),    # sheen
    0x0642: ({"init": "uniFED7", "medi": "uniFED8", "fina": "uniFED6"}, "gtx", 720, 0),    # qaf
    0x0635: ({"init": "uniFEBB", "medi": "uniFEBC", "fina": "uniFEBA"}, "gtx", 1300, 0),   # sad
    0x0636: ({"init": "uniFEBF", "medi": "uniFEC0", "fina": "uniFEBE"}, "gtx", 1300, 0),   # dad
    0x0644: ({"init": "uniFEDF", "medi": "uniFEE0", "fina": "uniFEDE"}, "gtx", 820, 0),    # lam (stem)
    0x06A9: ({"init": "uniFB90", "medi": "uniFB91", "fina": "uniFB8F"}, "gtx", 1080, 0),   # kaf (corner+diagonal)
    0x06AF: ({"init": "uniFB94", "medi": "uniFB95", "fina": "uniFB93"}, "gtx", 1080, 0),   # gaf
    # meem (م) reverted to base joined forms: the head-drop transplant left the
    # loop floating above the baseline connector and detached the final form.
}


def _bar2(x0, x1):
    return _rect(x0, 0, x1, 150)


def transplant_body(font: TTFont, iso_cp, forms, clip_mode, clip_val, dy_body=0, right_margin=40) -> int:
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    glyphset = font.getGlyphSet()
    cmap = font.getBestCmap()
    if iso_cp not in cmap:
        return 0
    iso_gn = cmap[iso_cp]
    clip = _rect(clip_val, -80, 4000, 1400) if clip_mode == "gtx" else _rect(-200, clip_val, 4000, 1400)
    body = pathops.op(_iso_pathops(glyphset, iso_gn), clip, pathops.PathOp.INTERSECTION, fix_winding=True)
    body.simplify(fix_winding=True)
    if dy_body:
        body = _translate(body, 0, dy_body)
        body.simplify(fix_winding=True)
    bb = body.bounds
    count = 0
    for kind, gn in forms.items():
        if gn not in glyf:
            continue
        adv = hmtx.metrics[gn][0]
        if kind == "fina":
            base = _iso_pathops(glyphset, iso_gn)
            ib = base.bounds
            res = pathops.op(base, _bar2(ib[2] - 220, adv + 35), pathops.PathOp.UNION, fix_winding=True)
        else:
            dx = (adv - right_margin) - bb[2]
            b = _translate(body, dx, 0)
            hx0, hx1 = bb[0] + dx, bb[2] + dx
            res = b
            if kind in ("init", "medi"):
                res = pathops.op(res, _bar2(-35, hx0 + 150), pathops.PathOp.UNION, fix_winding=True)
            if kind == "medi":
                res = pathops.op(res, _bar2(hx1 - 150, adv + 35), pathops.PathOp.UNION, fix_winding=True)
        res.simplify(fix_winding=True)
        glyf[gn] = _to_glyph(glyf, res)
        hmtx.metrics[gn] = (adv, glyf[gn].xMin)
        count += 1
    return count


def fix_body_transplants(font: TTFont) -> int:
    total = 0
    for cp, (forms, mode, val, dy) in _TRANSPLANTS.items():
        total += transplant_body(font, cp, forms, mode, val, dy)
    return total


# --------------------------------------------------------------------------- #
# v1.011-v1.013 Kurdish target repairs
# --------------------------------------------------------------------------- #
def _recording_contours(glyphset, glyph_name: str) -> list[list[tuple[str, tuple]]]:
    """Return a decomposed glyph as individual recording-pen contours."""
    recording = RecordingPen()
    glyphset[glyph_name].draw(recording)
    contours: list[list[tuple[str, tuple]]] = []
    current: list[tuple[str, tuple]] = []
    for operation, arguments in recording.value:
        current.append((operation, arguments))
        if operation in {"closePath", "endPath"}:
            contours.append(current)
            current = []
    if current:
        contours.append(current)
    return contours


def _recorded_contour_bounds(contour: list[tuple[str, tuple]]) -> tuple[float, float, float, float]:
    path = pathops.Path()
    pen = path.getPen(glyphSet=None)
    for operation, arguments in contour:
        getattr(pen, operation)(*arguments)
    return path.bounds


def _replace_with_body_and_mark(
    font: TTFont,
    target_name: str,
    body_name: str,
    mark_source_name: str,
    mark_contour_index: int = -1,
    mark_transform: tuple[float, float, float, float, float, float] | None = None,
) -> bool:
    """Compose an exact family body with one existing mark contour."""
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    required = {target_name, body_name, mark_source_name}
    if not required.issubset(glyf.keys()):
        return False

    glyphset = font.getGlyphSet()
    contours = _recording_contours(glyphset, mark_source_name)
    if not contours:
        return False

    pen = TTGlyphPen(None)
    glyphset[body_name].draw(pen)
    mark_pen = TransformPen(pen, mark_transform) if mark_transform is not None else pen
    for operation, arguments in contours[mark_contour_index]:
        getattr(mark_pen, operation)(*arguments)
    new_glyph = pen.glyph()
    if new_glyph.numberOfContours <= 0:
        return False
    new_glyph.recalcBounds(glyf)

    advance = hmtx.metrics[target_name][0]
    glyf[target_name] = new_glyph
    hmtx.metrics[target_name] = (advance, new_glyph.xMin)
    return True


def _fit_glyph_bounds(
    font: TTFont,
    glyph_name: str,
    target_x: tuple[int, int] | None = None,
    target_y: tuple[int, int] | None = None,
) -> bool:
    """Affine-fit a glyph to fixed bounds; fixed targets make this idempotent."""
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    if glyph_name not in glyf or glyf[glyph_name].numberOfContours <= 0:
        return False

    old = glyf[glyph_name]
    old.recalcBounds(glyf)
    sx = sy = 1.0
    dx = dy = 0.0
    if target_x is not None:
        old_width = max(1, old.xMax - old.xMin)
        sx = (target_x[1] - target_x[0]) / old_width
        dx = target_x[0] - (old.xMin * sx)
    if target_y is not None:
        old_height = max(1, old.yMax - old.yMin)
        sy = (target_y[1] - target_y[0]) / old_height
        dy = target_y[0] - (old.yMin * sy)

    glyphset = font.getGlyphSet()
    pen = TTGlyphPen(None)
    glyphset[glyph_name].draw(TransformPen(pen, (sx, 0, 0, sy, dx, dy)))
    new_glyph = pen.glyph()
    if new_glyph.numberOfContours <= 0:
        return False
    new_glyph.recalcBounds(glyf)

    advance = hmtx.metrics[glyph_name][0]
    glyf[glyph_name] = new_glyph
    hmtx.metrics[glyph_name] = (advance, new_glyph.xMin)
    return True


def fix_lam_with_small_v(font: TTFont) -> int:
    """Rebuild every ڵ form from its exact plain-lam sibling + existing V."""
    cmap = font.getBestCmap()
    target = cmap.get(0x06B5)
    body = cmap.get(0x0644)
    if not target or not body:
        return 0

    count = 0
    # Basic initial/medial/final forms.
    counterparts = [
        ("glyph00452", "uniFEDF"),
        ("glyph00453", "uniFEE0"),
        ("glyph00454", "uniFEDE"),
        # Required lam-v + alef ligatures. These appear in common text such as
        # سڵاو, so they are part of the repair rather than incidental glyphs.
        ("glyph00680", "uniFEFB"),
        ("glyph00681", "uniFEFC"),
        ("glyph00682", "uniFEF5"),
        ("glyph00683", "uniFEF6"),
        ("glyph00684", "uniFEF7"),
        ("glyph00685", "uniFEF8"),
        ("glyph00686", "uniFEF9"),
        ("glyph00687", "uniFEFA"),
        ("glyph00688", "glyph00672"),
        ("glyph00689", "glyph00673"),
        ("glyph00690", "glyph00674"),
        ("glyph00691", "glyph00675"),
        ("glyph00692", "glyph00676"),
        ("glyph00693", "glyph00677"),
    ]
    for marked_name, plain_name in counterparts:
        count += int(_replace_with_body_and_mark(
            font, marked_name, plain_name, marked_name))

    # The isolated glyph had no V at all. Borrow the family V from its final
    # form and shift it 33 units right to optically center it on the plain stem.
    isolated_mark_position = (1.0, 0.0, 0.0, 1.0, 33.0, 0.0)
    count += int(_replace_with_body_and_mark(
        font, target, body, "glyph00454", mark_transform=isolated_mark_position))
    return count


def fix_meem_scale_and_joins(font: TTFont) -> int:
    """Restore canonical meem sizing, spacing, and the 0..155 join band."""
    cmap = font.getBestCmap()
    base = cmap.get(0x0645)
    count = 0
    # The old builder stretched these joined outlines to yMax=864. Their
    # ligatures and GPOS anchors remained at the canonical yMax=636. Restoring
    # the forms downward makes the connector strokes meet again at y=0..155.
    for glyph_name in ("uniFEE2", "uniFEE3", "uniFEE4"):
        if glyph_name not in font["glyf"]:
            continue
        glyph = font["glyf"][glyph_name]
        glyph.recalcBounds(font["glyf"])
        count += int(_fit_glyph_bounds(
            font, glyph_name, target_y=(glyph.yMin, MEEM_HEAD_TOP)))

    # v1.013: rebuild the isolated meem from this family's own drawing.
    #
    # 1.012 put the supplied PDF outline here at full size. Measured against
    # the rest of the family that outline is a different letter: stroke ~53
    # where the family runs ~110, and a head counter of 254x145 where the
    # joined forms and the font's own untouched meem drawings carry ~390x368.
    # Kurdish selects the isolated form at the end of any word whose meem
    # follows a non-joiner, so it dominated word endings.
    #
    # The replacement is the 1.010 master's uniFEE1 - same head, same weight
    # and same flat tail as the final form uniFEE2 - put through exactly the
    # y-fit that already corrected the joined forms, so all five meem glyphs
    # end up sharing one head at yMax 636 with the counter at y[127,495].
    if base and REFERENCE_SRC.exists():
        reference = TTFont(REFERENCE_SRC)
        ref_glyf = reference["glyf"]
        source_glyph = ref_glyf["uniFEE1"]
        source_glyph.recalcBounds(ref_glyf)
        scale_y = (MEEM_HEAD_TOP - source_glyph.yMin) / (source_glyph.yMax - source_glyph.yMin)
        shift_y = source_glyph.yMin - (source_glyph.yMin * scale_y)

        pen = TTGlyphPen(None)
        reference.getGlyphSet()["uniFEE1"].draw(
            TransformPen(pen, (1.0, 0, 0, scale_y, 0, shift_y)))
        isolated = pen.glyph()
        isolated.recalcBounds(font["glyf"])
        advance = isolated.xMax + MEEM_ISOLATED_RSB

        for name in (base, "uniFEE1"):
            if name in font["glyf"]:
                font["glyf"][name] = copy.deepcopy(isolated)
                font["hmtx"].metrics[name] = (advance, isolated.xMin)
                count += 1
        _copy_mark_anchors(font, "uniFEE2", (base, "uniFEE1"))
    return count


def _copy_mark_anchors(font: TTFont, source: str, targets: tuple[str, ...]) -> None:
    """Point a glyph's mark-attachment anchors at another glyph's.

    The rebuilt isolated meem is uniFEE2 minus its connector, drawn at the same
    place, so uniFEE2's harakat anchors are already correct for it."""
    if "GPOS" not in font:
        return
    for lookup in font["GPOS"].table.LookupList.Lookup:
        for subtable in lookup.SubTable:
            if type(subtable).__name__.startswith("Extension"):
                subtable = subtable.ExtSubTable
            if type(subtable).__name__ != "MarkBasePos":
                continue
            glyphs = subtable.BaseCoverage.glyphs
            if source not in glyphs:
                continue
            src_record = subtable.BaseArray.BaseRecord[glyphs.index(source)]
            for target in targets:
                if target not in glyphs:
                    continue
                record = subtable.BaseArray.BaseRecord[glyphs.index(target)]
                for index, anchor in enumerate(src_record.BaseAnchor):
                    if anchor is None or record.BaseAnchor[index] is None:
                        continue
                    record.BaseAnchor[index].XCoordinate = anchor.XCoordinate
                    record.BaseAnchor[index].YCoordinate = anchor.YCoordinate


def fix_rreh_body(font: TTFont) -> int:
    """Give ڕ the corrected family reh body while retaining its V-below mark."""
    cmap = font.getBestCmap()
    target = cmap.get(0x0695)
    body = cmap.get(0x0631)
    count = 0
    if not target or not body or "glyph00274" not in font["glyf"]:
        return count
    # Use absolute mark origins so rebuilding an already-fixed master is
    # idempotent (the V must not drift horizontally on each build).
    glyphset = font.getGlyphSet()
    isolated_bounds = _recorded_contour_bounds(_recording_contours(glyphset, target)[-1])
    final_bounds = _recorded_contour_bounds(_recording_contours(glyphset, "glyph00274")[-1])
    isolated_mark_position = (
        1.0, 0.0, 0.0, 1.0,
        268.0 - isolated_bounds[0], -872.0 - isolated_bounds[1],
    )
    final_mark_position = (
        1.0, 0.0, 0.0, 1.0,
        178.0 - final_bounds[0], -872.0 - final_bounds[1],
    )
    count += int(_replace_with_body_and_mark(
        font, target, body, target, mark_transform=isolated_mark_position))
    # The right-joining final form must use the matching corrected final reh.
    count += int(_replace_with_body_and_mark(
        font, "glyph00274", "uniFEAE", "glyph00274", mark_transform=final_mark_position))
    return count


def repair_kurdish_targets(font: TTFont) -> dict[str, int]:
    repairs = {
        "lam_with_small_v": fix_lam_with_small_v(font),
        "meem": fix_meem_scale_and_joins(font),
        "rreh": fix_rreh_body(font),
    }
    repairs["total"] = sum(repairs.values())
    return repairs


def apply_weight(font: TTFont, r: float) -> int:
    if r <= 0:
        return 0
    glyphset = font.getGlyphSet()
    glyf = font["glyf"]
    count = 0
    for gname in font.getGlyphOrder():
        g = glyf[gname]
        if g.numberOfContours > 0:  # simple contour glyphs; composites follow
            try:
                new = dilate_glyph(glyphset, gname, r)
            except Exception as exc:  # noqa: BLE001
                print(f"  ! dilate failed {gname}: {exc!r}")
                continue
            if new.numberOfContours > 0:
                new.recalcBounds(glyf)
                glyf[gname] = new
                count += 1
    return count


# --------------------------------------------------------------------------- #
# Naming
# --------------------------------------------------------------------------- #
def set_name(font: TTFont, nid: int, value: str) -> None:
    name = font["name"]
    name.names = [rec for rec in name.names if rec.nameID != nid]
    name.setName(value, nid, 3, 1, 0x0409)  # Windows / Unicode BMP / en-US
    name.setName(value, nid, 1, 0, 0)        # Mac Roman / en


def update_names(font: TTFont, style: Style) -> None:
    ribbi_bold = style.label == "Bold"
    ribbi_regular = not ribbi_bold  # Regular, Medium, SemiBold are RIBBI "Regular"

    # RIBBI split so legacy (GDI) apps can reach every weight, while modern apps
    # group all four under the typographic family via ID16/17 and ID21/22.
    if style.label in ("Regular", "Bold"):
        win_family = FAMILY
    else:
        win_family = f"{FAMILY} {style.label}"
    win_subfamily = "Bold" if ribbi_bold else "Regular"

    # Drop every record we are about to redefine (all platforms), plus any
    # stale extras leaking the source name (e.g. old ID21='Base-Kurdish').
    keep = font["name"].names
    manage = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22}
    font["name"].names = [rec for rec in keep if rec.nameID not in manage]

    set_name(font, 0, f"Copyright (c) 2026 Base Agency. {FAMILY} font family. All rights reserved.")
    set_name(font, 1, win_family)
    set_name(font, 2, win_subfamily)
    set_name(font, 3, f"BaseAgency:{style.stem}:{VERSION}:2026")
    set_name(font, 4, style.full)
    set_name(font, 5, f"Version {VERSION}")
    set_name(font, 6, style.stem)
    set_name(font, 7, f"{FAMILY} is a trademark of Base Agency.")
    set_name(font, 8, "Base Agency")
    set_name(font, 9, "Base Agency Type Studio")
    set_name(font, 10, "Kurdish (Sorani) type family. Version 1.013 rebuilds the isolated meem so word-final meem matches the family weight and the joined forms, and adds the missing symbol set: punctuation, superior/inferior figures, fractions, maths, arrows, geometric shapes, currency and Arabic signs. Connected shaping stays active; clean stroke-based weight axis.")
    set_name(font, 13, "Proprietary font software owned or controlled by Base Agency. See LICENSE-BASE-AGENCY.txt.")
    set_name(font, 16, FAMILY)          # typographic family
    set_name(font, 17, style.label)     # typographic subfamily
    set_name(font, 18, style.full)      # compatible full (Mac)
    set_name(font, 21, FAMILY)          # WWS family
    set_name(font, 22, style.label)     # WWS subfamily

    os2 = font["OS/2"]
    os2.usWeightClass = style.weight
    os2.usWidthClass = 5
    os2.fsType = 0
    os2.achVendID = "BASE"
    os2.version = max(os2.version, 4)
    # bit5 BOLD, bit6 REGULAR, bit7 USE_TYPO_METRICS, bit8 WWS
    fs = 0x0080 | 0x0100  # USE_TYPO_METRICS + WWS (names are WWS-clean via 21/22)
    if ribbi_bold:
        fs |= 0x0020
    if ribbi_regular:
        fs |= 0x0040
    os2.fsSelection = fs

    head = font["head"]
    head.macStyle = 0x0001 if ribbi_bold else 0x0000
    head.modified = BUILD_TIMESTAMP
    font["post"].italicAngle = 0.0
    font["post"].isFixedPitch = 0
    if "DSIG" in font:
        del font["DSIG"]
    font.recalcTimestamp = False


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #
def recalc_head(font: TTFont) -> tuple[int, int]:
    glyf = font["glyf"]
    xn = yn = 10**9
    xx = yy = -(10**9)
    for gname in font.getGlyphOrder():
        g = glyf[gname]
        if g.numberOfContours != 0:
            g.recalcBounds(glyf)
            xn, yn = min(xn, g.xMin), min(yn, g.yMin)
            xx, yy = max(xx, g.xMax), max(yy, g.yMax)
    if xn == 10**9:
        xn = yn = xx = yy = 0
    head = font["head"]
    head.xMin, head.yMin, head.xMax, head.yMax = xn, yn, xx, yy
    return yn, yy


def finalize_vertical(fonts_meta: list[tuple[TTFont, Style]]) -> None:
    """Give every weight identical line metrics; win box covers the boldest."""
    reg = fonts_meta[0][0]
    typo_asc = reg["OS/2"].sTypoAscender
    typo_desc = reg["OS/2"].sTypoDescender
    typo_gap = reg["OS/2"].sTypoLineGap
    hhea_asc = reg["hhea"].ascent
    hhea_desc = reg["hhea"].descent

    win_asc = 0
    win_desc = 0
    for font, _ in fonts_meta:
        yn, yy = recalc_head(font)
        win_asc = max(win_asc, yy + 16)
        win_desc = max(win_desc, -yn + 16)

    for font, _ in fonts_meta:
        os2 = font["OS/2"]
        os2.sTypoAscender = typo_asc
        os2.sTypoDescender = typo_desc
        os2.sTypoLineGap = typo_gap
        os2.usWinAscent = win_asc
        os2.usWinDescent = win_desc
        hhea = font["hhea"]
        hhea.ascent = hhea_asc
        hhea.descent = hhea_desc
        hhea.lineGap = 0


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build() -> list[dict]:
    for folder in (FONTS, DOCS, SOURCE, SPECIMEN):
        folder.mkdir(parents=True, exist_ok=True)

    fonts_meta: list[tuple[TTFont, Style]] = []
    reports = []
    for style in STYLES:
        print(f"[{style.label}] loading master")
        font = TTFont(REGULAR_SRC)
        repairs = repair_kurdish_targets(font)
        # Symbols are drawn before the weight pass so the outset picks them up
        # and every weight carries the same coverage.
        symbols = build_symbols(font)
        if SMOOTH:
            # Smooth/flowing direction: keep the base font's smooth joined forms;
            # do NOT transplant the geometric PDF bodies into connected text.
            heh = feh = tp = 0
        else:
            heh = fix_heh_forms(font)          # round joined heh BEFORE weighting
            feh = fix_feh_forms(font)          # PDF head into joined feh
            tp = fix_body_transplants(font)    # PDF body into seen/sheen/qaf/sad/dad
        n = apply_weight(font, style.dilate)
        update_names(font, style)
        fonts_meta.append((font, style))
        reports.append({"style": style.label, "weight": style.weight,
                        "dilate_radius": style.dilate, "glyphs_reweighted": n,
                        "smooth": SMOOTH, "target_repairs": repairs,
                        "symbols_added": symbols,
                        "heh_forms_rounded": heh, "feh_forms_transplanted": feh})
        print(f"[{style.label}] repaired {repairs['total']} targets, "
              f"added {symbols['total']} symbols, smooth={SMOOTH}, "
              f"reweighted {n} glyphs")

    finalize_vertical(fonts_meta)

    for font, style in fonts_meta:
        font.recalcBBoxes = True
        out = FONTS / f"{style.stem}.ttf"
        font.save(out)
        # normalize + web font
        tt = TTFont(out)
        tt.recalcTimestamp = False
        tt["head"].modified = BUILD_TIMESTAMP
        tt.save(out)
        web = TTFont(out)
        web.recalcTimestamp = False
        web["head"].modified = BUILD_TIMESTAMP
        web.flavor = "woff2"
        web.save(FONTS / f"{style.stem}.woff2")
        print(f"[{style.label}] wrote {out.name} + woff2")

    return reports


# --------------------------------------------------------------------------- #
# Validation (shaping) via harfbuzz
# --------------------------------------------------------------------------- #
def shape(path: Path, text: str) -> list[str]:
    data = path.read_bytes()
    face = hb.Face(data)
    hb_font = hb.Font(face)
    hb_font.scale = (face.upem, face.upem)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    buf.language = "ckb"
    hb.shape(hb_font, buf)
    tt = TTFont(path)
    return [tt.getGlyphName(i.codepoint) for i in buf.glyph_infos]


def adjacent_ink_overlaps(path: Path, text: str) -> list[bool]:
    """Report whether each adjacent shaped glyph pair shares filled join ink."""
    data = path.read_bytes()
    face = hb.Face(data)
    hb_font = hb.Font(face)
    hb_font.scale = (face.upem, face.upem)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.direction = "rtl"
    buf.script = "arab"
    buf.language = "ckb"
    hb.shape(hb_font, buf)

    font = TTFont(path)
    glyphset = font.getGlyphSet()
    order = font.getGlyphOrder()
    cursor = 0
    placed: list[pathops.Path] = []
    for info, position in zip(buf.glyph_infos, buf.glyph_positions):
        outline = _iso_pathops(glyphset, order[info.codepoint])
        placed.append(_translate(
            outline,
            cursor + position.x_offset,
            position.y_offset,
        ))
        cursor += position.x_advance

    overlaps: list[bool] = []
    for left, right in zip(placed, placed[1:]):
        intersection = pathops.op(
            left, right, pathops.PathOp.INTERSECTION, fix_winding=True)
        overlaps.append(len(intersection) > 0)
    return overlaps


def glyph_geometry(font: TTFont, glyph_name: str) -> dict:
    glyf = font["glyf"]
    hmtx = font["hmtx"]
    glyph = glyf[glyph_name]
    glyph.recalcBounds(glyf)
    contour_points: list[int] = []
    if glyph.numberOfContours > 0:
        _coordinates, end_points, _flags = glyph.getCoordinates(glyf)
        previous = -1
        for end_point in end_points:
            contour_points.append(end_point - previous)
            previous = end_point
    return {
        "advance": hmtx.metrics[glyph_name][0],
        "lsb": hmtx.metrics[glyph_name][1],
        "bbox": [glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax],
        "contours": glyph.numberOfContours,
        "contour_points": contour_points,
    }


def validate() -> dict:
    samples = [
        "کوردستان", "فۆنت", "پەروەردە", "زانکۆ", "نووسین", "ئەکادیمی", "پ چ ژ ڤ گ",
        "ڵ", "دڵ", "هەڵە", "سڵاو", "بڵ", "ڵب", "بڵب",
        "ڵا", "بڵا", "ڵآ", "بڵآ", "ڵأ", "بڵأ", "ڵإ", "بڵإ",
        "ڵٱ", "بڵٱ", "ڵٲ", "بڵٲ", "ڵٳ", "بڵٳ",
        "م", "کەم", "ئەم", "دەم", "مەم", "گەرم", "ممم", "ئمب", "بمب", "تمب", "ثمب", "لم", "لمب",
        "کما", "کمآ", "کمأ", "کمإ", "نمب", "يمب",
        "ڕ", "ڕوون", "بڕ", "ڕب", "بەڕێوەبردن", "گۆڕانکاری",
    ]
    expected_shaping = {
        "ڵ": ["uni06B5"],
        "سڵاو": ["uni0648", "glyph00681", "uniFEB3"],
        "بڵ": ["glyph00454", "uniFE91"],
        "ڵب": ["uniFE90", "glyph00452"],
        "بڵب": ["uniFE90", "glyph00453", "uniFE91"],
        "ڵا": ["glyph00680"],
        "بڵا": ["glyph00681", "uniFE91"],
        "ڵآ": ["glyph00682"],
        "بڵآ": ["glyph00683", "uniFE91"],
        "ڵأ": ["glyph00684"],
        "بڵأ": ["glyph00685", "uniFE91"],
        "ڵإ": ["glyph00686"],
        "بڵإ": ["glyph00687", "uniFE91"],
        "ڵٱ": ["glyph00688"],
        "بڵٱ": ["glyph00689", "uniFE91"],
        "ڵٲ": ["glyph00690"],
        "بڵٲ": ["glyph00691", "uniFE91"],
        "ڵٳ": ["glyph00692"],
        "بڵٳ": ["glyph00693", "uniFE91"],
        "م": ["uni0645"],
        "کەم": ["uni0645", "glyph00572", "uniFB90"],
        "ئەم": ["uni0645", "glyph00572", "uniFE8B"],
        "دەم": ["uni0645", "uni06D5", "uni062F"],
        "مەم": ["uni0645", "glyph00572", "uniFEE3"],
        "گەرم": ["uni0645", "uni0631", "glyph00572", "uniFB94"],
        "ممم": ["uniFEE2", "uniFEE4", "uniFEE3"],
        "ئمب": ["uniFE90", "glyph00615"],
        "بمب": ["uniFE90", "glyph00620"],
        "تمب": ["uniFE90", "glyph00625"],
        "ثمب": ["uniFE90", "glyph00630"],
        "لم": ["glyph00750"],
        "لمب": ["uniFE90", "uniFCCC"],
        "کما": ["glyph00756", "uniFB90"],
        "کمآ": ["glyph00757", "uniFB90"],
        "کمأ": ["glyph00758", "uniFB90"],
        "کمإ": ["glyph00759", "uniFB90"],
        "نمب": ["uniFE90", "glyph00761"],
        "يمب": ["uniFE90", "glyph00765"],
        "ڕ": ["uni0695"],
        "بڕ": ["glyph00274", "uniFE91"],
        # ڕ is right-joining only. It must remain separate from the following ب.
        "ڕب": ["uni0628", "uni0695"],
    }
    expected_overlaps = {
        "بڵ": [True],
        "ڵب": [True],
        "بڵب": [True, True],
        "بم": [True],
        "مب": [True],
        "مم": [True],
        "ممم": [True, True],
        "بمب": [True],
        "بڕ": [True],
        # Correct Unicode behavior: ڕ joins to the preceding letter only.
        "ڕب": [False],
        "بڕب": [False, True],
    }
    target_names = [
        "uni06B5", "glyph00452", "glyph00453", "glyph00454",
        *[f"glyph{glyph_id:05d}" for glyph_id in range(680, 694)],
        "uni0645", "uniFEE1", "uniFEE2", "uniFEE3", "uniFEE4",
        "glyph00100", "glyph00104", "glyph00615", "glyph00620", "glyph00625", "glyph00630",
        "glyph00750", "uniFCCC", "glyph00756", "glyph00757", "glyph00758", "glyph00759",
        "glyph00761", "glyph00765",
        "uni0695", "glyph00274",
    ]
    out = {"family": FAMILY, "version": VERSION, "styles": []}
    for style in STYLES:
        path = FONTS / f"{style.stem}.ttf"
        font = TTFont(path)
        shaping = {s: shape(path, s) for s in samples}
        notdef = [s for s, gs in shaping.items() if ".notdef" in gs]
        if notdef:
            raise RuntimeError({"file": path.name, "notdef": notdef})
        shaping_failures = {
            sample: {"expected": expected, "actual": shaping[sample]}
            for sample, expected in expected_shaping.items()
            if shaping[sample] != expected
        }
        if shaping_failures:
            raise RuntimeError({"file": path.name, "shaping_failures": shaping_failures})

        overlaps = {sample: adjacent_ink_overlaps(path, sample) for sample in expected_overlaps}
        overlap_failures = {
            sample: {"expected": expected, "actual": overlaps[sample]}
            for sample, expected in expected_overlaps.items()
            if overlaps[sample] != expected
        }
        if overlap_failures:
            raise RuntimeError({"file": path.name, "join_failures": overlap_failures})

        geometry = {name: glyph_geometry(font, name) for name in target_names}
        lam_v = geometry["uni06B5"]
        max_lam_extent = lam_v["advance"] + 30 + round(style.dilate)
        if lam_v["contours"] < 2 or lam_v["bbox"][2] > max_lam_extent:
            raise RuntimeError({"file": path.name, "malformed_lam_with_small_v": lam_v})

        malformed_rreh = {
            name: geometry[name]
            for name in ("uni0695", "glyph00274")
            if geometry[name]["contours"] < 2
        }
        if malformed_rreh:
            raise RuntimeError({"file": path.name, "joined_rreh_mark": malformed_rreh})

        # Every meem - isolated, initial, medial, final - must share one head
        # top, and it must match the font's own untouched meem drawings.
        expected_meem_top = round(MEEM_HEAD_TOP + style.dilate)
        bad_meem = {
            name: data
            for name, data in geometry.items()
            if name in {"uni0645", "uniFEE1", "uniFEE2", "uniFEE3", "uniFEE4"}
            and abs(data["bbox"][3] - expected_meem_top) > 3
        }
        if bad_meem:
            raise RuntimeError({"file": path.name, "inconsistent_meem_top": bad_meem})

        for reference_name in ("glyph00100", "glyph00104"):
            reference_top = geometry[reference_name]["bbox"][3]
            if abs(reference_top - expected_meem_top) > 3:
                raise RuntimeError({"file": path.name,
                                    "meem_disagrees_with_canonical_drawing": {
                                        reference_name: reference_top,
                                        "expected": expected_meem_top}})

        # The isolated meem must carry the family's stroke weight, not the
        # half-weight outline 1.012 shipped. Measured on the widest run of the
        # head ring, which the thin import could never reach.
        for name in ("uni0645", "uniFEE1"):
            width = geometry[name]["bbox"][2] - geometry[name]["bbox"][0]
            if width < 900:
                raise RuntimeError({"file": path.name,
                                    "isolated_meem_too_narrow": geometry[name]})
            advance, lsb = font["hmtx"].metrics[name]
            if advance - geometry[name]["bbox"][2] < 40:
                raise RuntimeError({"file": path.name,
                                    "isolated_meem_crowded": (advance, geometry[name]["bbox"])})

        glyf = font["glyf"]
        if (glyf["uni0645"].compile(glyf) != glyf["uniFEE1"].compile(glyf)
                or font["hmtx"].metrics["uni0645"] != font["hmtx"].metrics["uniFEE1"]):
            raise RuntimeError({"file": path.name, "isolated_meem_not_canonical": geometry["uni0645"]})

        # Symbol coverage: every codepoint the symbol pass claims to add must
        # be present, mapped, and non-empty unless it is a space.
        cmap = font.getBestCmap()
        blank_ok = set(SPACE_CODEPOINTS)
        missing = [f"U+{cp:04X}" for cp in REQUIRED_SYMBOLS if cp not in cmap]
        if missing:
            raise RuntimeError({"file": path.name, "missing_symbols": missing[:40]})
        empty = [f"U+{cp:04X}" for cp in REQUIRED_SYMBOLS
                 if cp not in blank_ok
                 and font["glyf"][cmap[cp]].numberOfContours == 0]
        if empty:
            raise RuntimeError({"file": path.name, "empty_symbols": empty[:40]})

        if style.label == "Regular":
            reh = glyph_geometry(font, "uni0631")
            reh_final = glyph_geometry(font, "uniFEAE")
            if geometry["uni0695"]["contour_points"][0] != reh["contour_points"][0]:
                raise RuntimeError({"file": path.name, "rreh_body_mismatch": geometry["uni0695"]})
            if geometry["glyph00274"]["contour_points"][0] != reh_final["contour_points"][0]:
                raise RuntimeError({"file": path.name, "rreh_final_body_mismatch": geometry["glyph00274"]})

        nm = font["name"]
        if nm.getDebugName(5) != f"Version {VERSION}":
            raise RuntimeError({"file": path.name, "wrong_version": nm.getDebugName(5)})
        out["styles"].append({
            "file": path.name,
            "typographic_family": nm.getDebugName(16),
            "typographic_subfamily": nm.getDebugName(17),
            "win_family": nm.getDebugName(1),
            "win_subfamily": nm.getDebugName(2),
            "full_name": nm.getDebugName(4),
            "postscript": nm.getDebugName(6),
            "usWeightClass": font["OS/2"].usWeightClass,
            "glyphs": len(font.getGlyphOrder()),
            "unicode_codepoints": len(font.getBestCmap()),
            "notdef_free": True,
            "target_shaping": {sample: shaping[sample] for sample in expected_shaping},
            "target_join_overlaps": overlaps,
            "target_geometry": geometry,
        })
    return out


if __name__ == "__main__":
    reports = build()
    validation = validate()
    validation["build_reports"] = reports
    (DOCS / "validation-report.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
