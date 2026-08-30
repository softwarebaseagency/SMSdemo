"""BASE Meridion Kurdish - the v1.013 symbol additions.

Every glyph here is constructed from the family's own measured constants
(see meridion_symbols.py) so the new symbols share the existing colour,
optical centre and advance conventions.

Measured references used below:
  symbol stroke 119 | figure stroke 181 | currency stroke 145
  symbol centre (635, 717) | math axis 675 | default advance 1270
  figure height 1409 (flat) / 1430 (round) | superior scale sx .645 sy .600
  superior bottom y=563 | fraction slash from onehalf: x[345,1371] y[0,1409]
"""
from __future__ import annotations

import math

from meridion_symbols import (
    ADV, CAP, CX, CY, FIG_TOP, HAIR, MATH_AXIS, OVER, STROKE, XH,
    arc_stroke, bar, center_to, circle, diff, earc_stroke, ellipse, ering,
    fit_height, glyph_path, install, install_alias, install_blank, isect,
    mirror_x, mirror_y, P, place_lsb, poly, polyline, rect, ring, rotate,
    scale_about, seg, star, translate, union, unions, vbar, width_of, xform,
)

FIG_STROKE = 181          # stroke of the lining figures
CUR_STROKE = 145          # stroke used by $ / EUR class symbols
SUP_SX, SUP_SY = 0.645, 0.600
SUP_BOTTOM = 563          # measured from the existing superior figures
SUB_BOTTOM = -190
SIDE = 45                 # side bearing for superior / inferior figures

DIGITS = ["zero", "one", "two", "three", "four", "five",
          "six", "seven", "eight", "nine"]


def _bb(p):
    return p.bounds


def _put(font, name, path, cp, adv=None, pad=90):
    """Install a path, defaulting the advance to ink width + pad."""
    b = _bb(path)
    if b is None:
        return install_blank(font, name, adv or ADV, cp)
    if adv is None:
        adv = (b[2] - b[0]) + pad
    return install(font, name, path, adv, cp)


# --------------------------------------------------------------------------- #
# 1. Spaces and invisibles
# --------------------------------------------------------------------------- #
def spaces(font):
    em = font["head"].unitsPerEm
    space_adv = font["hmtx"].metrics["space"][0]
    figure_adv = font["hmtx"].metrics["zero"][0]
    period_adv = font["hmtx"].metrics["period"][0]
    table = [
        (0x2000, "enquad", em // 2),
        (0x2001, "emquad", em),
        (0x2004, "threeperemspace", em // 3),
        (0x2005, "fourperemspace", em // 4),
        (0x2006, "sixperemspace", em // 6),
        (0x2007, "figurespace", figure_adv),
        (0x2008, "punctuationspace", period_adv),
        (0x200B, "zerowidthspace", 0),
        (0x202F, "narrownbspace", round(em * 0.1666)),
        (0x205F, "mediummathspace", round(em * 4 / 18)),
        (0x2060, "wordjoiner", 0),
        (0xFEFF, "zerowidthnobreakspace", 0),
        (0x061C, "arabiclettermark", 0),
    ]
    n = 0
    for cp, name, adv in table:
        install_blank(font, name, adv, cp)
        n += 1
    return n


# --------------------------------------------------------------------------- #
# 2. Punctuation completions
# --------------------------------------------------------------------------- #
def punctuation(font):
    n = 0
    # dashes reuse the family's existing dash drawings
    for cp, name, src in ((0x2012, "figuredash", "endash"),
                          (0x2015, "horizontalbar", "emdash")):
        if install_alias(font, name, src, cp):
            n += 1

    # hyphenation point = the family's mid dot
    if install_alias(font, "hyphenationpoint", "periodcentered", 0x2027):
        n += 1

    prime = glyph_path(font, "minute")            # x[537,754] y[1012,1487]
    pb = _bb(prime)
    step = 232                                    # spacing used by U+2033
    tri = unions(translate(prime, -step, 0), prime, translate(prime, step, 0))
    _put(font, "triple prime".replace(" ", ""), tri, 0x2034, adv=ADV)
    n += 1
    _put(font, "reversedprime", mirror_x(prime, (pb[0] + pb[2]) / 2), 0x2035, adv=ADV)
    n += 1

    # ‱  per ten thousand = perthousand plus one more zero
    pt = glyph_path(font, "perthousand")
    ptb = _bb(pt)
    zero_o = ring(0, 0, 118, 62)
    small = translate(zero_o, ptb[2] + 130, 175)
    _put(font, "perkthousand", union(pt, small), 0x2031, adv=1560)
    n += 1

    # ※ reference mark: centre dot with four kite strokes
    marks = P()
    for a in (45, 135, 225, 315):
        r = math.radians(a)
        p0 = (CX + 268 * math.cos(r), CY + 268 * math.sin(r))
        p1 = (CX + 470 * math.cos(r), CY + 470 * math.sin(r))
        marks = union(marks, seg(p0, p1, 104, "round"))
    ref = union(marks, circle(CX, CY, 132))
    _put(font, "referencemark", ref, 0x203B, adv=ADV)
    n += 1

    # ‽ interrobang and its inverted twin, ⁇ ⁈ ⁉ ‼ pairs
    q = glyph_path(font, "question")
    ex = glyph_path(font, "exclam")
    qb, eb = _bb(q), _bb(ex)
    # the exclamation stem runs down through the question's neck so both
    # marks stay legible in the single combined glyph
    stem_w = eb[2] - eb[0]
    inter = union(q, rect((qb[0] + qb[2]) / 2.0 - stem_w / 2.0, 330,
                          (qb[0] + qb[2]) / 2.0 + stem_w / 2.0, 980))
    _put(font, "interrobang", inter, 0x203D, adv=font["hmtx"].metrics["question"][0])
    n += 1
    inv = mirror_y(mirror_x(inter, (qb[0] + qb[2]) / 2), FIG_TOP / 2)
    _put(font, "invertedinterrobang", inv, 0x2E18,
         adv=font["hmtx"].metrics["question"][0])
    n += 1

    def _pair(a, b, cp, name):
        pa, pb_ = glyph_path(font, a), glyph_path(font, b)
        wa = font["hmtx"].metrics[a][0]
        out = union(pa, translate(pb_, wa, 0))
        _put(font, name, out, cp, adv=wa + font["hmtx"].metrics[b][0])

    _pair("question", "question", 0x2047, "questiondouble"); n += 1
    _pair("question", "exclam", 0x2048, "questionexclam"); n += 1
    _pair("exclam", "question", 0x2049, "exclamquestion"); n += 1
    _pair("exclam", "exclam", 0x203C, "exclamdouble"); n += 1

    # ⁂ asterism: three asterisks in a triangle
    ast = glyph_path(font, "asterisk")
    ab = _bb(ast)
    ast = translate(ast, -(ab[0] + ab[2]) / 2, -(ab[1] + ab[3]) / 2)
    tri3 = unions(translate(ast, CX, 1180),
                  translate(ast, CX - 360, 620),
                  translate(ast, CX + 360, 620))
    _put(font, "asterism", tri3, 0x2042, adv=1560)
    n += 1
    # ⁑ two asterisks aligned vertically
    two_ast = union(translate(ast, CX, 1180), translate(ast, CX, 620))
    _put(font, "asteriskaligned", two_ast, 0x2051, adv=ADV)
    n += 1

    # ‣ triangular bullet, ⁃ hyphen bullet
    tribullet = poly([(500, 566), (500, 868), (790, 717)])
    _put(font, "triangularbullet", tribullet, 0x2023, adv=ADV)
    n += 1
    _put(font, "hyphenbullet", bar(479, 791, 717, 119), 0x2043, adv=ADV)
    n += 1

    # ‖ double vertical line, ‗ double low line, ‸ caret
    dbl = union(vbar(-425, 1484, CX - 150, 133), vbar(-425, 1484, CX + 150, 133))
    _put(font, "dblverticalbar", dbl, 0x2016, adv=880)
    n += 1
    low = union(bar(20, 811, -293, 98), bar(20, 811, -461, 98))
    _put(font, "dbllowline", low, 0x2017, adv=831)
    n += 1
    caret = polyline([(180, 480), (500, 900), (820, 480)], 110, "butt")
    _put(font, "caretinsert", caret, 0x2038, adv=1000)
    n += 1

    # ‛ and ‟ reversed quotes
    for cp, name, src in ((0x201B, "quotereversed", "quoteleft"),
                          (0x201F, "quotedblreversed", "quotedblleft")):
        p = glyph_path(font, src)
        b = _bb(p)
        _put(font, name, mirror_x(p, (b[0] + b[2]) / 2), cp,
             adv=font["hmtx"].metrics[src][0])
        n += 1
    return n


# --------------------------------------------------------------------------- #
# 3. Superior / inferior figures and their operators
# --------------------------------------------------------------------------- #
def _small_digit(font, name, bottom):
    p = glyph_path(font, name)
    p = xform(p, sx=SUP_SX, sy=SUP_SY)
    b = _bb(p)
    return translate(p, SIDE - b[0], bottom - b[1])


def superiors(font):
    n = 0
    for i, dname in enumerate(DIGITS):
        for cps, tag, bottom in ((0x2070, "superior", SUP_BOTTOM),
                                 (0x2080, "inferior", SUB_BOTTOM)):
            cp = cps + i
            if cps == 0x2070:
                cp = {0: 0x2070, 1: 0x00B9, 2: 0x00B2, 3: 0x00B3}.get(i, 0x2070 + i)
            g = _small_digit(font, dname, bottom)
            b = _bb(g)
            install(font, f"{dname}{tag}", g, (b[2] - b[0]) + 2 * SIDE, cp)
            n += 1

    # operators, scaled from the family's own plus / minus / equal / parens
    ops = [("plus", 0x207A, 0x208A), ("minus", 0x207B, 0x208B),
           ("equal", 0x207C, 0x208C),
           ("parenleft", 0x207D, 0x208D), ("parenright", 0x207E, 0x208E)]
    for src, sup_cp, sub_cp in ops:
        p = glyph_path(font, src)
        sc = xform(p, sx=SUP_SX, sy=SUP_SY)
        b = _bb(sc)
        h = b[3] - b[1]
        for cp, tag, mid in ((sup_cp, "superior", SUP_BOTTOM + 846 / 2),
                             (sub_cp, "inferior", SUB_BOTTOM + 846 / 2)):
            g = translate(sc, SIDE - b[0], mid - (b[1] + b[3]) / 2)
            gb = _bb(g)
            install(font, f"{src}{tag}", g, (gb[2] - gb[0]) + 2 * SIDE, cp)
            n += 1

    # ⁿ superscript n
    stem = 96
    nn = unions(rect(0, 0, stem, 560),
                rect(300, 0, 300 + stem, 560),
                arc_stroke(150 + stem / 2 - 0.5, 430, 150, 0, 180, stem))
    nn = translate(nn, SIDE, SUP_BOTTOM)
    b = _bb(nn)
    install(font, "nsuperior", nn, (b[2] - b[0]) + 2 * SIDE, 0x207F)
    n += 1
    return n


# --------------------------------------------------------------------------- #
# 4. Vulgar fractions
# --------------------------------------------------------------------------- #
_FRACTIONS = [
    (0x2150, 1, 7), (0x2151, 1, 9), (0x2152, 1, 10),
    (0x2153, 1, 3), (0x2154, 2, 3),
    (0x2155, 1, 5), (0x2156, 2, 5), (0x2157, 3, 5), (0x2158, 4, 5),
    (0x2159, 1, 6), (0x215A, 5, 6),
    (0x215B, 1, 8), (0x215C, 3, 8), (0x215D, 5, 8), (0x215E, 7, 8),
    (0x2189, 0, 3),
]
_FRACNAMES = {0x2150: "oneseventh", 0x2151: "oneninth", 0x2152: "onetenth",
              0x2153: "onethird", 0x2154: "twothirds", 0x2155: "onefifth",
              0x2156: "twofifths", 0x2157: "threefifths", 0x2158: "fourfifths",
              0x2159: "onesixth", 0x215A: "fivesixths", 0x215B: "oneeighth",
              0x215C: "threeeighths", 0x215D: "fiveeighths",
              0x215E: "seveneighths", 0x2189: "zerothirds"}


def _fraction_slash(font):
    """Reuse the exact diagonal used by the family's own onehalf."""
    p = glyph_path(font, "onehalf")
    best = None
    for c in p.contours:
        b = c.bounds
        if b and (b[3] - b[1]) > 1300:
            best = c
    return best if best is not None else p


def fractions(font):
    slash = _fraction_slash(font)
    sb = _bb(slash)
    n = 0
    for cp, num, den in _FRACTIONS:
        num_p = _small_digit(font, DIGITS[num], SUP_BOTTOM)
        nb = _bb(num_p)
        num_p = translate(num_p, 56 - nb[0], 0)
        nb = _bb(num_p)

        den_digits = [int(ch) for ch in str(den)]
        den_p = P()
        x = 0.0
        for d in den_digits:
            g = _small_digit(font, DIGITS[d], 0)
            gb = _bb(g)
            g = translate(g, x - gb[0], 0)
            den_p = union(den_p, g)
            x = _bb(den_p)[2] + 55
        db = _bb(den_p)
        den_p = translate(den_p, 1051 - db[0], 0)
        db = _bb(den_p)

        whole = unions(num_p, slash, den_p)
        install(font, _FRACNAMES[cp], whole, db[2] + 56, cp)
        n += 1
    return n


# --------------------------------------------------------------------------- #
# 5. Mathematical operators
# --------------------------------------------------------------------------- #
def _slash_overlay(path, w=STROKE):
    """The cancelling stroke used by the family's own notequal, centred on
    the glyph it negates and just long enough to clear it."""
    b = _bb(path)
    cx, cy = (b[0] + b[2]) / 2.0, (b[1] + b[3]) / 2.0
    half = max((b[3] - b[1]) / 2.0, 380) + 110
    return seg((cx - half * 0.40, cy - half), (cx + half * 0.40, cy + half), w, "butt")


def math_ops(font):
    n = 0
    L, R = 215, 1055           # the family's minus bar extents
    gap = 175

    def put(name, path, cp, adv=ADV):
        nonlocal n
        _put(font, name, path, cp, adv=adv)
        n += 1

    # ∓ minus-or-plus: bar on top, plus below, drawn to the family's ± metrics
    pm_adv = font["hmtx"].metrics["plusminus"][0]
    pb = _bb(glyph_path(font, "plusminus"))
    pw = STROKE * 1.2
    mp = unions(bar(pb[0], pb[2], pb[3] - pw / 2.0, pw),
                bar(pb[0], pb[2], pb[1] + 430, pw),
                vbar(pb[1], pb[1] + 860, (pb[0] + pb[2]) / 2.0, pw))
    put("minusplus", mp, 0x2213, pm_adv)

    # ∖ set minus, ∗ asterisk operator, ∘ ring operator, ⋅ dot operator
    put("setminus", seg((330, 120), (940, 1230), STROKE, "butt"), 0x2216)
    ast = glyph_path(font, "asterisk")
    ab = _bb(ast)
    put("asteriskmath", translate(ast, CX - (ab[0] + ab[2]) / 2,
                                  CY - (ab[1] + ab[3]) / 2), 0x2217)
    put("ringoperator", ring(CX, MATH_AXIS, 196, 96), 0x2218)
    put("bulletoperator", circle(CX, MATH_AXIS, 118), 0x2219)
    put("dotmath", circle(CX, MATH_AXIS, 97), 0x22C5)

    # ∝ proportional to: a closed loop on the left opening into a right fork
    lp_cx, lp_rx, lp_ry = 440, 215, 255
    a_open = 16
    prop = earc_stroke(lp_cx, MATH_AXIS, lp_rx, lp_ry, a_open, 360 - a_open, STROKE)
    ex_y = lp_ry * math.sin(math.radians(a_open))
    ex_x = lp_cx + lp_rx * math.cos(math.radians(a_open))
    prop = unions(prop,
                  seg((ex_x, MATH_AXIS + ex_y), (1055, MATH_AXIS + 300), STROKE, "butt"),
                  seg((ex_x, MATH_AXIS - ex_y), (1055, MATH_AXIS - 300), STROKE, "butt"))
    put("proportional", prop, 0x221D)

    # ∠ ∡ ∢ angles - the arc sits close to the vertex so it reads as a sweep
    vx, vy = 225, 190
    ang = union(seg((vx, vy), (1090, vy), STROKE, "butt"),
                seg((vx, vy), (1035, 1000), STROKE, "butt"))
    put("angle", ang, 0x2220)
    put("measuredangle", union(ang, arc_stroke(vx, vy, 330, 4, 42, 84)), 0x2221)
    put("sphericalangle",
        union(ang, union(arc_stroke(vx, vy, 330, 4, 42, 84),
                         arc_stroke(vx, vy, 560, 4, 42, 84))), 0x2222)

    # ∣ ∥ divides / parallel
    put("divides", vbar(120, 1230, CX, STROKE), 0x2223, 700)
    put("parallel", union(vbar(120, 1230, CX - 160, STROKE),
                          vbar(120, 1230, CX + 160, STROKE)), 0x2225, 1000)

    # ∧ ∨ ∩ ∪ logic and sets
    wedge = polyline([(240, 190), (CX, 1180), (1030, 190)], STROKE, "butt")
    put("logicaland", wedge, 0x2227)
    put("logicalor", mirror_y(wedge, MATH_AXIS), 0x2228)
    cup = union(arc_stroke(CX, 560, 395, 180, 360, STROKE),
                union(vbar(560, 1180, CX - 395, STROKE),
                      vbar(560, 1180, CX + 395, STROKE)))
    put("union", cup, 0x222A)
    put("intersection", mirror_y(cup, MATH_AXIS), 0x2229)

    # ∬ ∮ from the family's own integral
    integ = glyph_path(font, "integral")
    iadv = font["hmtx"].metrics["integral"][0]
    put("dblintegral", union(integ, translate(integ, 430, 0)), 0x222C, iadv + 430)
    ib = _bb(integ)
    put("contourintegral",
        union(integ, ring((ib[0] + ib[2]) / 2, (ib[1] + ib[3]) / 2, 300, 96)),
        0x222E, iadv)

    # ∴ ∵ ∶ ∷
    def dot(x, y, r=105):
        return circle(x, y, r)
    tri_up = unions(dot(CX, 1120), dot(CX - 275, 320), dot(CX + 275, 320))
    put("therefore", tri_up, 0x2234)
    put("because", mirror_y(tri_up, 720), 0x2235)
    put("ratio", union(dot(CX, 1035), dot(CX, 315)), 0x2236, 700)
    put("proportion", union(union(dot(CX - 230, 1035), dot(CX - 230, 315)),
                            union(dot(CX + 230, 1035), dot(CX + 230, 315))),
        0x2237, 1160)

    # ∼ ≃ ≅ ≍ ≡ ≢ tilde / equality family
    tilde = glyph_path(font, "asciitilde")
    tb = _bb(tilde)
    tilde_c = translate(tilde, CX - (tb[0] + tb[2]) / 2, 0)
    put("similar", translate(tilde_c, 0, MATH_AXIS - (tb[1] + tb[3]) / 2), 0x223C)
    bar_lo = bar(L, R, MATH_AXIS - 300, STROKE)
    put("asymptotic", union(translate(tilde_c, 0, 265 - (tb[1] + tb[3]) / 2 + 560),
                            bar(L, R, 420, STROKE)), 0x2243)
    approx = glyph_path(font, "approxequal")
    ab2 = _bb(approx)
    put("congruent",
        union(translate(approx, CX - (ab2[0] + ab2[2]) / 2, 900 - ab2[1]),
              bar(L, R, 420, STROKE)), 0x2245,
        font["hmtx"].metrics["approxequal"][0])
    put("equivalent", union(translate(tilde_c, 0, 980 - (tb[1] + tb[3]) / 2),
                            translate(tilde_c, 0, 430 - (tb[1] + tb[3]) / 2)),
        0x224D)
    ident = unions(bar(L, R, MATH_AXIS + 275, STROKE),
                   bar(L, R, MATH_AXIS, STROKE),
                   bar(L, R, MATH_AXIS - 275, STROKE))
    put("identical", ident, 0x2261)
    put("notidentical", union(ident, _slash_overlay(ident)), 0x2262)

    # ≪ ≫
    chev = polyline([(760, 1150), (300, MATH_AXIS), (760, 200)], STROKE, "butt")
    much_less = union(chev, translate(chev, 360, 0))
    put("muchless", much_less, 0x226A, 1420)
    put("muchgreater", mirror_x(much_less, CX), 0x226B, 1420)

    # ⊂ ⊃ ⊆ ⊇ ∈ ∉ ∋
    def cshape(open_right=True):
        c = union(arc_stroke(CX, MATH_AXIS, 400, 90, 270, STROKE),
                  union(bar(CX, CX + 330, MATH_AXIS + 400 - STROKE / 2, STROKE),
                        bar(CX, CX + 330, MATH_AXIS - 400 + STROKE / 2, STROKE)))
        return c if open_right else mirror_x(c, CX)
    sub = cshape(True)
    put("subset", sub, 0x2282, 1420)
    put("superset", mirror_x(sub, CX), 0x2283, 1420)
    under = bar(CX - 400, CX + 330, MATH_AXIS - 620, STROKE)
    put("subsetequal", union(sub, under), 0x2286, 1420)
    put("supersetequal", union(mirror_x(sub, CX), mirror_x(under, CX)), 0x2287, 1420)
    elem = union(cshape(True), bar(CX - 260, CX + 300, MATH_AXIS, STROKE))
    put("element", elem, 0x2208, 1420)
    put("notelement", union(elem, _slash_overlay(elem)), 0x2209, 1420)
    put("contains", mirror_x(elem, CX), 0x220B, 1420)

    # ∅ empty set, ⌀ diameter
    oval = ering(CX, MATH_AXIS, 360, 470, STROKE)
    slash_ = seg((CX - 470, MATH_AXIS - 590), (CX + 470, MATH_AXIS + 590),
                 STROKE, "butt")
    put("emptyset", union(oval, slash_), 0x2205, 1300)
    dia = union(ring(CX, MATH_AXIS, 400, STROKE),
                seg((CX - 470, MATH_AXIS - 470), (CX + 470, MATH_AXIS + 470),
                    STROKE, "butt"))
    put("diameter", dia, 0x2300, 1300)

    # ∀ ∃ ∄ ∇
    forall = polyline([(190, 1230), (CX, 150), (1080, 1230)], FIG_STROKE * 0.72, "butt")
    forall = union(forall, bar(400, 870, 560, FIG_STROKE * 0.72))
    put("forall", forall, 0x2200, 1370)
    ex = unions(bar(330, 940, 1230 - STROKE / 2, STROKE),
                bar(330, 940, MATH_AXIS, STROKE),
                bar(330, 940, 120 + STROKE / 2, STROKE),
                vbar(120, 1230, 940 - STROKE / 2, STROKE))
    put("thereexists", ex, 0x2203, 1270)
    put("notexists", union(ex, _slash_overlay(ex)), 0x2204, 1270)
    nabla = diff(poly([(170, 1230), (1100, 1230), (635, 150)]),
                 poly([(170 + 250, 1230 - 150), (1100 - 250, 1230 - 150),
                       (635, 150 + 265)]))
    put("nabla", nabla, 0x2207, 1370)

    # ⊕ ⊗
    r = 430
    circ = ring(CX, MATH_AXIS, r, STROKE)
    plus_in = union(bar(CX - 260, CX + 260, MATH_AXIS, STROKE),
                    vbar(MATH_AXIS - 260, MATH_AXIS + 260, CX, STROKE))
    put("circleplus", union(circ, plus_in), 0x2295, 1300)
    x_in = union(seg((CX - 195, MATH_AXIS - 195), (CX + 195, MATH_AXIS + 195), STROKE),
                 seg((CX - 195, MATH_AXIS + 195), (CX + 195, MATH_AXIS - 195), STROKE))
    put("circlemultiply", union(circ, x_in), 0x2297, 1300)

    # ∛ ∜ from the family's radical
    rad = glyph_path(font, "radical")
    radadv = font["hmtx"].metrics["radical"][0]
    three_s = _small_digit(font, "three", 0)
    tb3 = _bb(three_s)
    three_s = xform(three_s, sx=0.72, sy=0.72)
    tb3 = _bb(three_s)
    put("cuberoot", union(rad, translate(three_s, 40 - tb3[0], 760 - tb3[1])),
        0x221B, radadv)
    four_s = xform(_small_digit(font, "four", 0), sx=0.72, sy=0.72)
    tb4 = _bb(four_s)
    put("fourthroot", union(rad, translate(four_s, 40 - tb4[0], 760 - tb4[1])),
        0x221C, radadv)

    # ⌈ ⌉ ⌊ ⌋ ⟨ ⟩
    ceil_l = union(vbar(-330, 1290, 430, STROKE),
                   bar(430 - STROKE / 2, 820, 1290 - STROKE / 2, STROKE))
    put("ceilingleft", ceil_l, 0x2308, 900)
    put("ceilingright", mirror_x(ceil_l, 625), 0x2309, 900)
    floor_l = union(vbar(-330, 1290, 430, STROKE),
                    bar(430 - STROKE / 2, 820, -330 + STROKE / 2, STROKE))
    put("floorleft", floor_l, 0x230A, 900)
    put("floorright", mirror_x(floor_l, 625), 0x230B, 900)
    angl = polyline([(760, 1290), (360, 480), (760, -330)], STROKE, "butt")
    put("angleleft", angl, 0x27E8, 900)
    put("angleright", mirror_x(angl, 560), 0x27E9, 900)

    # ⌐ reversed not sign, ⌒ arc
    notg = glyph_path(font, "logicalnot")
    nb = _bb(notg)
    put("revlogicalnot", mirror_x(notg, (nb[0] + nb[2]) / 2), 0x2310,
        font["hmtx"].metrics[font.getBestCmap()[0x00AC]][0])
    put("arc", arc_stroke(CX, 500, 420, 35, 145, STROKE), 0x2312)

    # Δ ∆ Ω π  (symbol-block Greek used in maths)
    delta = diff(poly([(150, 150), (1120, 150), (635, 1290)]),
                 poly([(150 + 300, 150 + 175), (1120 - 300, 150 + 175),
                       (635, 1290 - 330)]))
    put("Delta", delta, 0x0394, 1330)
    _put(font, "increment", delta, 0x2206, adv=1330); n += 1
    omega = union(arc_stroke(CX, 720, 400, -46, 226, FIG_STROKE * 0.72),
                  union(bar(150, 500, 150 + FIG_STROKE * 0.36, FIG_STROKE * 0.72),
                        bar(770, 1120, 150 + FIG_STROKE * 0.36, FIG_STROKE * 0.72)))
    put("Omega", omega, 0x03A9, 1330)
    _put(font, "Ohm", omega, 0x2126, adv=1330); n += 1
    pi = unions(bar(170, 1100, 1150, FIG_STROKE * 0.72),
                vbar(150, 1150, 420, FIG_STROKE * 0.72),
                vbar(150, 1150, 870, FIG_STROKE * 0.72))
    put("pi", pi, 0x03C0, 1270)
    return n


# --------------------------------------------------------------------------- #
# 6. Arrows - built from the family's own arrow drawing
# --------------------------------------------------------------------------- #
def _arrow_parts(font):
    """Split the family's arrowright into its head and its shaft."""
    a = glyph_path(font, "arrowright")
    shaft_box = rect(174 - 2, 657 - 1, 1016, 776 + 1)
    head = diff(a, shaft_box)
    return a, head


TIP = (1135, CY)          # the tip of the family's own arrowright


def _head_at(head, to, deg=0.0, s=1.0):
    """Move/rotate/scale the family's arrow head so its tip lands on `to`."""
    h = scale_about(head, s, TIP[0], TIP[1])
    if deg:
        h = rotate(h, deg, TIP[0], TIP[1])
    return translate(h, to[0] - TIP[0], to[1] - TIP[1])


def arrows(font):
    n = 0
    whole, head = _arrow_parts(font)

    def put(name, path, cp, adv=ADV):
        nonlocal n
        _put(font, name, path, cp, adv=adv)
        n += 1

    # diagonals: rotations of the family's own right arrow, scaled back up so
    # they read at the same optical size as the horizontal/vertical ones
    for cp, name, deg in ((0x2197, "arrownortheast", 45),
                          (0x2196, "arrownorthwest", 135),
                          (0x2199, "arrowsouthwest", 225),
                          (0x2198, "arrowsoutheast", 315)):
        put(name, scale_about(rotate(whole, deg, CX, CY), 1.22, CX, CY), cp)

    # ↔ ↕ double-ended: heads shrunk to 0.70 about their own tip so the two
    # chevrons cannot meet in the middle and close into a diamond
    hr = _head_at(head, TIP, s=0.70)
    hl = mirror_x(hr, CX)
    lr = unions(hr, hl, bar(190, 1080, CY, STROKE))
    put("arrowleftright", lr, 0x2194)
    put("arrowupdown", rotate(lr, 90, CX, CY), 0x2195)

    # ↚ ↛ barred arrows
    al = glyph_path(font, "arrowleft")
    put("arrowleftnot", union(al, _slash_overlay(al, 96)), 0x219A)
    put("arrowrightnot", union(whole, _slash_overlay(whole, 96)), 0x219B)

    # ⇒ ⇐ ⇑ ⇓ ⇔ ⇕ double-line arrows
    d_shaft = union(bar(230, 940, CY + 120, STROKE * 0.8),
                    bar(230, 940, CY - 120, STROKE * 0.8))
    d_head = polyline([(830, CY + 470), (1160, CY), (830, CY - 470)],
                      STROKE * 0.8, "butt")
    dbl_r = union(d_shaft, d_head)
    put("arrowdblright", dbl_r, 0x21D2)
    put("arrowdblleft", mirror_x(dbl_r, CX), 0x21D0)
    put("arrowdblup", rotate(dbl_r, 90, CX, CY), 0x21D1)
    put("arrowdbldown", rotate(dbl_r, -90, CX, CY), 0x21D3)
    dbl_lr = unions(d_head, mirror_x(d_head, CX),
                    bar(330, 940, CY + 120, STROKE * 0.8),
                    bar(330, 940, CY - 120, STROKE * 0.8))
    put("arrowdblleftright", dbl_lr, 0x21D4)
    put("arrowdblupdown", rotate(dbl_lr, 90, CX, CY), 0x21D5)

    # ↩ ↪ hooked arrows: shaft left, then a hook curling up on the right
    hooked_l = unions(_head_at(head, (150, CY), deg=180, s=0.70),
                      bar(150, 1010, CY, STROKE),
                      earc_stroke(1010, CY + 190, 190, 190, -90, 90, STROKE),
                      vbar(CY + 190, CY + 400, 1200 - STROKE / 2.0, STROKE))
    put("arrowlefthook", hooked_l, 0x21A9)
    put("arrowrighthook", mirror_x(hooked_l, CX), 0x21AA)

    # ↵ carriage return: bar across the top, down the right, head pointing left
    ret = unions(bar(320, 1060, CY + 400, STROKE),
                 vbar(CY - 130, CY + 400, 1060 - STROKE / 2.0, STROKE),
                 bar(320, 1060, CY - 130, STROKE),
                 _head_at(head, (250, CY - 130), deg=180, s=0.62))
    put("arrowreturn", ret, 0x21B5)

    # ↰ ↱ up then turn, tip pointing sideways
    up_l = unions(vbar(CY - 470, CY + 330, 950 - STROKE / 2.0, STROKE),
                  bar(330, 950, CY + 330 - STROKE / 2.0, STROKE),
                  _head_at(head, (250, CY + 330 - STROKE / 2.0), deg=180, s=0.62))
    put("arrowuptipleft", up_l, 0x21B0)
    put("arrowuptipright", mirror_x(up_l, CX), 0x21B1)

    # ↺ ↻ open circle arrows: a gapped ring closed by a solid tangential head
    r = 360
    a_end = 48
    ex, ey = (CX + r * math.cos(math.radians(a_end)),
              CY + r * math.sin(math.radians(a_end)))
    tip = math.radians(a_end + 74)          # pointing along the anticlockwise run
    barb = 250
    tri_head = poly([(ex + barb * math.cos(tip), ey + barb * math.sin(tip)),
                     (ex + barb * math.cos(tip + 2.3), ey + barb * math.sin(tip + 2.3)),
                     (ex + barb * math.cos(tip - 2.3), ey + barb * math.sin(tip - 2.3))])
    circ_arrow = union(arc_stroke(CX, CY, r, a_end, 330, STROKE), tri_head)
    put("arrowanticlockwise", circ_arrow, 0x21BA)
    put("arrowclockwise", mirror_x(circ_arrow, CX), 0x21BB)

    # ⇄ ⇅ paired arrows
    small = scale_about(whole, 0.78, CX, CY)
    pair = union(translate(small, 0, 220), translate(mirror_x(small, CX), 0, -220))
    put("arrowrightoverleft", pair, 0x21C4)
    put("arrowupdownpair", rotate(pair, 90, CX, CY), 0x21C5)

    # ⇦ ⇧ ⇨ ⇩ white (outlined) block arrows
    w = 96
    body = poly([(230, CY - 200), (760, CY - 200), (760, CY - 430),
                 (1150, CY), (760, CY + 430), (760, CY + 200), (230, CY + 200)])
    inner = poly([(230 + w, CY - 200 + w), (760 + w * 0.4, CY - 200 + w),
                  (760 + w * 0.4, CY - 300),
                  (1150 - w * 1.6, CY), (760 + w * 0.4, CY + 300),
                  (760 + w * 0.4, CY + 200 - w), (230 + w, CY + 200 - w)])
    white_r = diff(body, inner)
    put("arrowwhiteright", white_r, 0x21E8)
    put("arrowwhiteleft", mirror_x(white_r, CX), 0x21E6)
    put("arrowwhiteup", rotate(white_r, 90, CX, CY), 0x21E7)
    put("arrowwhitedown", rotate(white_r, -90, CX, CY), 0x21E9)

    # ➡ black rightwards arrow
    black_r = poly([(200, CY - 175), (720, CY - 175), (720, CY - 420),
                    (1140, CY), (720, CY + 420), (720, CY + 175), (200, CY + 175)])
    put("arrowblackright", black_r, 0x27A1)
    return n


# --------------------------------------------------------------------------- #
# 7. Geometric shapes
# --------------------------------------------------------------------------- #
def geometric(font):
    n = 0

    def put(name, path, cp, adv=ADV):
        nonlocal n
        _put(font, name, path, cp, adv=adv)
        n += 1

    def sq(side, w=None):
        h = side / 2.0
        outer = rect(CX - h, CY - h, CX + h, CY + h)
        return outer if w is None else diff(outer, rect(CX - h + w, CY - h + w,
                                                        CX + h - w, CY + h - w))

    put("blacksquare", sq(880), 0x25A0)
    put("whitesquare", sq(880, 108), 0x25A1)
    put("blacksmallsquare", sq(470), 0x25AA, 880)
    put("whitesmallsquare", sq(470, 88), 0x25AB, 880)
    put("blackmediumsquare", sq(760), 0x25FC)
    put("whitemediumsquare", sq(760, 100), 0x25FB)
    put("blackmediumsmallsquare", sq(610), 0x25FE, 1000)
    put("whitemediumsmallsquare", sq(610, 96), 0x25FD, 1000)
    put("blackrectangle", rect(CX - 520, CY - 230, CX + 520, CY + 230), 0x25AC)
    put("whiterectangle", diff(rect(CX - 520, CY - 230, CX + 520, CY + 230),
                               rect(CX - 520 + 100, CY - 230 + 100,
                                    CX + 520 - 100, CY + 230 - 100)), 0x25AD)

    def tri(dirn, size, w=None):
        r = size / 2.0
        if dirn == "up":
            pts = [(CX - r, CY - r * 0.86), (CX + r, CY - r * 0.86), (CX, CY + r * 0.94)]
        elif dirn == "down":
            pts = [(CX - r, CY + r * 0.86), (CX + r, CY + r * 0.86), (CX, CY - r * 0.94)]
        elif dirn == "right":
            pts = [(CX - r * 0.86, CY - r), (CX - r * 0.86, CY + r), (CX + r * 0.94, CY)]
        else:
            pts = [(CX + r * 0.86, CY - r), (CX + r * 0.86, CY + r), (CX - r * 0.94, CY)]
        outer = poly(pts)
        if w is None:
            return outer
        cx = sum(p[0] for p in pts) / 3.0
        cy = sum(p[1] for p in pts) / 3.0
        inner = poly([(cx + (x - cx) * (1 - w / (size * 0.42)),
                       cy + (y - cy) * (1 - w / (size * 0.42))) for x, y in pts])
        return diff(outer, inner)

    for dirn, black_cp, white_cp, sblack, swhite in (
            ("up", 0x25B2, 0x25B3, 0x25B4, 0x25B5),
            ("down", 0x25BC, 0x25BD, 0x25BE, 0x25BF),
            ("right", 0x25B6, 0x25B7, 0x25B8, 0x25B9),
            ("left", 0x25C0, 0x25C1, 0x25C2, 0x25C3)):
        put(f"blacktriangle{dirn}", tri(dirn, 900), black_cp)
        put(f"whitetriangle{dirn}", tri(dirn, 900, 104), white_cp)
        put(f"blacksmalltriangle{dirn}", tri(dirn, 500), sblack, 880)
        put(f"whitesmalltriangle{dirn}", tri(dirn, 500, 80), swhite, 880)

    put("blackpointerright", tri("right", 760), 0x25BA, 1100)
    put("blackpointerleft", tri("left", 760), 0x25C4, 1100)

    dia = poly([(CX, CY + 500), (CX + 400, CY), (CX, CY - 500), (CX - 400, CY)])
    put("blackdiamond", dia, 0x25C6)
    put("whitediamond", diff(dia, poly([(CX, CY + 500 - 175), (CX + 400 - 140, CY),
                                        (CX, CY - 500 + 175), (CX - 400 + 140, CY)])),
        0x25C7)
    loz = poly([(CX, CY + 520), (CX + 320, CY), (CX, CY - 520), (CX - 320, CY)])
    put("lozenge", diff(loz, poly([(CX, CY + 520 - 180), (CX + 320 - 112, CY),
                                   (CX, CY - 520 + 180), (CX - 320 + 112, CY)])),
        0x25CA)

    put("blackcircle", circle(CX, CY, 440), 0x25CF)
    put("whitecircle", ring(CX, CY, 440, 108), 0x25CB)
    put("largecircle", ring(CX, CY, 520, 104), 0x25EF)
    put("whitebullet", ring(CX, CY, 175, 84), 0x25E6, 880)
    half = isect(circle(CX, CY, 440), rect(CX - 440, CY - 440, CX, CY + 440))
    put("circlelefthalfblack", union(ring(CX, CY, 440, 104), half), 0x25D0)
    put("circlerighthalfblack",
        union(ring(CX, CY, 440, 104), mirror_x(half, CX)), 0x25D1)
    return n


# --------------------------------------------------------------------------- #
# 8. Ticks, boxes, stars, suits, music, warning
# --------------------------------------------------------------------------- #
def misc_symbols(font):
    n = 0

    def put(name, path, cp, adv=ADV):
        nonlocal n
        _put(font, name, path, cp, adv=adv)
        n += 1

    check = polyline([(215, 690), (470, 400), (1055, 1060)], STROKE, "round")
    check_h = polyline([(200, 690), (470, 370), (1070, 1075)], 168, "round")
    put("checkmark", check, 0x2713)
    put("checkmarkheavy", check_h, 0x2714)
    ex_x = union(seg((250, 320), (1020, 1110), STROKE, "round"),
                 seg((250, 1110), (1020, 320), STROKE, "round"))
    ex_h = union(seg((240, 310), (1030, 1120), 168, "round"),
                 seg((240, 1120), (1030, 310), 168, "round"))
    put("ballotx", ex_x, 0x2717)
    put("ballotxheavy", ex_h, 0x2718)
    put("multiplicationx", ex_x, 0x2715)
    put("multiplicationxheavy", ex_h, 0x2716)

    box = diff(rect(CX - 450, CY - 450, CX + 450, CY + 450),
               rect(CX - 450 + 104, CY - 450 + 104, CX + 450 - 104, CY + 450 - 104))
    put("ballotbox", box, 0x2610)
    inner_check = polyline([(300, 700), (500, 470), (990, 1020)], 128, "round")
    put("ballotboxcheck", union(box, inner_check), 0x2611)
    inner_x = union(seg((330, 420), (940, 1010), 128, "round"),
                    seg((330, 1010), (940, 420), 128, "round"))
    put("ballotboxx", union(box, inner_x), 0x2612)

    put("blackstar", star(CX, CY, 500, 205, 5), 0x2605)
    st = star(CX, CY, 500, 205, 5)
    put("whitestar", diff(st, star(CX, CY, 500 - 150, 205 - 62, 5)), 0x2606)
    put("blackfourpointedstar", star(CX, CY, 490, 150, 4), 0x2726)
    f4 = star(CX, CY, 490, 150, 4)
    put("whitefourpointedstar", diff(f4, star(CX, CY, 490 - 150, 150 - 46, 4)), 0x2727)
    put("sixpointedblackstar", star(CX, CY, 480, 235, 6), 0x2736)
    put("circledwhitestar",
        union(ring(CX, CY, 520, 96), star(CX, CY, 330, 135, 5)), 0x272A)
    heavy_ast = P()
    for i in range(6):
        a = math.radians(90 + i * 60)
        heavy_ast = union(heavy_ast, seg((CX, CY),
                                         (CX + 430 * math.cos(a), CY + 430 * math.sin(a)),
                                         150, "round"))
    put("heavyasterisk", heavy_ast, 0x2731)

    # card suits
    spade = unions(poly([(CX, CY + 470), (CX + 430, CY - 60), (CX - 430, CY - 60)]),
                   circle(CX - 235, CY - 90, 235), circle(CX + 235, CY - 90, 235),
                   poly([(CX - 175, CY - 460), (CX + 175, CY - 460),
                         (CX + 40, CY - 200), (CX - 40, CY - 200)]))
    put("spade", spade, 0x2660)
    heart = unions(poly([(CX - 470, CY + 145), (CX + 470, CY + 145), (CX, CY - 470)]),
                   circle(CX - 240, CY + 175, 240), circle(CX + 240, CY + 175, 240))
    put("heart", heart, 0x2665)
    put("heartsuitwhite", diff(heart, scale_about(heart, 0.62, CX, CY + 40)), 0x2661)
    put("heartheavy", heart, 0x2764)
    diamond_s = poly([(CX, CY + 500), (CX + 380, CY), (CX, CY - 500), (CX - 380, CY)])
    put("diamondsuit", diamond_s, 0x2666)
    put("diamondsuitwhite",
        diff(diamond_s, poly([(CX, CY + 500 - 165), (CX + 380 - 125, CY),
                              (CX, CY - 500 + 165), (CX - 380 + 125, CY)])), 0x2662)
    club = unions(circle(CX, CY + 250, 245), circle(CX - 265, CY - 105, 245),
                  circle(CX + 265, CY - 105, 245),
                  poly([(CX - 160, CY - 460), (CX + 160, CY - 460),
                        (CX + 45, CY - 130), (CX - 45, CY - 130)]))
    put("club", club, 0x2663)
    # outline suits: shrink the solid shape and subtract it so the remaining
    # ring keeps an even weight all the way round
    put("spadesuitwhite",
        diff(spade, scale_about(spade, 0.72, CX, CY - 25)), 0x2664)
    put("clubsuitwhite",
        diff(club, scale_about(club, 0.70, CX, CY - 25)), 0x2667)

    # music
    def note(stem_x, head_x):
        return union(ellipse(head_x, CY - 330, 200, 150),
                     rect(stem_x - 55, CY - 330, stem_x + 55, CY + 520))
    n1 = note(CX + 150, CX - 55)
    flag = poly([(CX + 205, CY + 520), (CX + 430, CY + 300), (CX + 430, CY + 110),
                 (CX + 205, CY + 330)])
    put("musicalnote", union(n1, flag), 0x266A)
    n_a = note(CX - 120, CX - 325)
    n_b = note(CX + 430, CX + 225)
    beam = poly([(CX - 175, CY + 520), (CX + 485, CY + 520),
                 (CX + 485, CY + 330), (CX - 175, CY + 330)])
    put("musicalnotedbl", unions(n_a, n_b, beam), 0x266B)
    beam2 = translate(beam, 0, -230)
    put("musicalnotesixteenth", unions(n_a, n_b, beam, beam2), 0x266C)
    flat = union(rect(CX - 260, CY - 330, CX - 150, CY + 620),
                 diff(ellipse(CX - 40, CY - 120, 250, 235),
                      ellipse(CX - 40, CY - 120, 250 - 105, 235 - 105)))
    flat = isect(flat, rect(CX - 300, CY - 400, CX + 260, CY + 700))
    put("musicflat", flat, 0x266D)
    sharp = unions(rect(CX - 230, CY - 430, CX - 120, CY + 500),
                   rect(CX + 120, CY - 500, CX + 230, CY + 430),
                   poly([(CX - 400, CY + 30), (CX + 400, CY + 165),
                         (CX + 400, CY + 30), (CX - 400, CY - 105)]),
                   poly([(CX - 400, CY - 330), (CX + 400, CY - 195),
                         (CX + 400, CY - 330), (CX - 400, CY - 465)]))
    put("musicsharp", sharp, 0x266F)

    # ⚠ warning
    tri_o = poly([(CX - 560, CY - 400), (CX + 560, CY - 400), (CX, CY + 560)])
    tri_i = poly([(CX - 560 + 210, CY - 400 + 120), (CX + 560 - 210, CY - 400 + 120),
                  (CX, CY + 560 - 250)])
    warn = union(diff(tri_o, tri_i),
                 union(rect(CX - 55, CY - 200, CX + 55, CY + 175),
                       circle(CX, CY - 300, 68)))
    put("warning", warn, 0x26A0, 1400)
    bolt = poly([(CX + 180, CY + 560), (CX - 330, CY - 30), (CX - 30, CY - 30),
                 (CX - 180, CY - 560), (CX + 330, CY + 60), (CX + 30, CY + 60)])
    put("highvoltage", bolt, 0x26A1)
    return n


# --------------------------------------------------------------------------- #
# 9. Letterlike symbols
# --------------------------------------------------------------------------- #
def _letter_C(x, y, h, w, s, open_deg=52):
    rx, ry = (w - s) / 2.0, (h - s) / 2.0
    return earc_stroke(x + w / 2.0, y + h / 2.0, rx, ry,
                       open_deg, 360 - open_deg, s)


def _letter_O(x, y, h, w, s):
    return ering(x + w / 2.0, y + h / 2.0, w / 2.0, h / 2.0, s)


def _letter_L(x, y, h, w, s):
    return union(rect(x, y, x + s, y + h), rect(x, y, x + w, y + s))


def _letter_T(x, y, h, w, s):
    return union(rect(x, y + h - s, x + w, y + h),
                 rect(x + w / 2.0 - s / 2.0, y, x + w / 2.0 + s / 2.0, y + h))


def _letter_P(x, y, h, w, s, bowl=0.52):
    bh = h * bowl
    cy = y + h - bh / 2.0
    bowl_p = earc_stroke(x + s / 2.0, cy, w - s, (bh - s) / 2.0, -90, 90, s)
    return unions(rect(x, y, x + s, y + h), bowl_p,
                  rect(x, y + h - s, x + s / 2.0 + 40, y + h),
                  rect(x, y + h - bh - s / 2.0, x + s / 2.0 + 40, y + h - bh + s / 2.0))


def _letter_N(x, y, h, w, s):
    return unions(rect(x, y, x + s, y + h), rect(x + w - s, y, x + w, y + h),
                  seg((x + s / 2.0, y + h), (x + w - s / 2.0, y), s, "butt"))


def _letter_W(x, y, h, w, s):
    q = w / 4.0
    return unions(seg((x + s / 2, y + h), (x + q * 0.85, y), s, "butt"),
                  seg((x + q * 0.85, y), (x + w / 2.0, y + h * 0.68), s, "butt"),
                  seg((x + w / 2.0, y + h * 0.68), (x + w - q * 0.85, y), s, "butt"),
                  seg((x + w - q * 0.85, y), (x + w - s / 2, y + h), s, "butt"))


def _letter_R(x, y, h, w, s):
    return union(_letter_P(x, y, h, w, s),
                 seg((x + w * 0.46, y + h * 0.46), (x + w, y), s, "butt"))


def _letter_F(x, y, h, w, s):
    return unions(rect(x, y, x + s, y + h), rect(x, y + h - s, x + w, y + h),
                  rect(x, y + h * 0.5 - s / 2.0, x + w * 0.82, y + h * 0.5 + s / 2.0))


def _letter_G(x, y, h, w, s):
    c = _letter_C(x, y, h, w, s, 34)
    return unions(c,
                  rect(x + w * 0.58, y + h * 0.40 - s / 2.0, x + w, y + h * 0.40 + s / 2.0),
                  rect(x + w - s, y + h * 0.40 - s / 2.0, x + w, y + h * 0.50))


def _letter_B(x, y, h, w, s):
    ry = (h / 2.0 - s / 2.0) / 2.0
    top = earc_stroke(x + s / 2.0, y + h - ry - s / 2.0, w - s, ry, -90, 90, s)
    bot = earc_stroke(x + s / 2.0, y + ry + s / 2.0, w - s, ry, -90, 90, s)
    caps = unions(rect(x, y + h - s, x + s / 2.0 + 40, y + h),
                  rect(x, y, x + s / 2.0 + 40, y + s),
                  rect(x, y + h / 2.0 - s / 2.0, x + s / 2.0 + 40, y + h / 2.0 + s / 2.0))
    return unions(rect(x, y, x + s, y + h), top, bot, caps)


def _letter_A(x, y, h, w, s):
    return unions(seg((x + s / 2, y), (x + w / 2.0, y + h), s, "butt"),
                  seg((x + w / 2.0, y + h), (x + w - s / 2, y), s, "butt"),
                  rect(x + w * 0.22, y + h * 0.3 - s / 2.0,
                       x + w * 0.78, y + h * 0.3 + s / 2.0))


def _letter_M(x, y, h, w, s):
    return unions(rect(x, y, x + s, y + h), rect(x + w - s, y, x + w, y + h),
                  seg((x + s / 2.0, y + h), (x + w / 2.0, y + h * 0.34), s, "butt"),
                  seg((x + w / 2.0, y + h * 0.34), (x + w - s / 2.0, y + h), s, "butt"))


def _letter_K(x, y, h, w, s):
    return unions(rect(x, y, x + s, y + h),
                  seg((x + s, y + h * 0.42), (x + w, y + h), s, "butt"),
                  seg((x + s, y + h * 0.42), (x + w, y), s, "butt"))


def _letter_S(x, y, h, w, s):
    """Two bowls that meet exactly at mid-height.

    The upper bowl runs anticlockwise from the right terminal over the top and
    down to its own 270 degree point; the lower bowl runs clockwise from its
    90 degree point round to the left terminal.  Choosing ry = (h-s)/4 puts
    both of those points on the same spot, so the curve joins cleanly.
    """
    rx = (w - s) / 2.0
    ry = (h - s) / 4.0
    cx = x + w / 2.0
    y_top = y + h - ry - s / 2.0
    y_bot = y + ry + s / 2.0
    top = earc_stroke(cx, y_top, rx, ry, 8, 272, s)
    bot = earc_stroke(cx, y_bot, rx, ry, 88, -172, s)
    return union(top, bot)


def _letter_D(x, y, h, w, s):
    bowl = earc_stroke(x + s / 2.0, y + h / 2.0, w - s, (h - s) / 2.0, -90, 90, s)
    caps = union(rect(x, y + h - s, x + s / 2.0 + 40, y + h),
                 rect(x, y, x + s / 2.0 + 40, y + s))
    return unions(rect(x, y, x + s, y + h), bowl, caps)


def _letter_E(x, y, h, w, s):
    return unions(rect(x, y, x + s, y + h), rect(x, y + h - s, x + w, y + h),
                  rect(x, y, x + w, y + s),
                  rect(x, y + h * 0.5 - s / 2.0, x + w * 0.85, y + h * 0.5 + s / 2.0))


def letterlike(font):
    n = 0
    H, S = 1220, 168
    deg = glyph_path(font, "degree")
    db = _bb(deg)
    deg_s = scale_about(deg, 0.78, (db[0] + db[2]) / 2, (db[1] + db[3]) / 2)
    db = _bb(deg_s)

    def put(name, path, cp, adv=None):
        nonlocal n
        _put(font, name, path, cp, adv=adv, pad=150)
        n += 1

    # ℃ ℉
    c_letter = _letter_C(0, 0, H, 940, S)
    f_letter = _letter_F(0, 0, H, 820, S)
    for name, letter, cp in (("degreecelsius", c_letter, 0x2103),
                             ("degreefahrenheit", f_letter, 0x2109)):
        d = translate(deg_s, 60 - db[0], H - (db[3] - db[1]) - db[1])
        lb = _bb(d)
        put(name, union(d, translate(letter, lb[2] + 120, 0)), cp)

    # № numero
    N = _letter_N(0, 0, H, 900, S)
    o_small = _letter_O(0, 0, H * 0.52, 470, S * 0.86)
    ob = _bb(o_small)
    o_small = translate(o_small, 1040, H - (ob[3] - ob[1]))
    ob = _bb(o_small)
    underline = rect(ob[0], ob[1] - 190, ob[2], ob[1] - 190 + S * 0.7)
    put("numero", unions(N, o_small, underline), 0x2116)

    # ℅ care of
    c_o = _letter_C(0, 0, H * 0.62, 560, S * 0.88)
    o_o = _letter_O(0, 0, H * 0.62, 560, S * 0.88)
    ob2 = _bb(o_o)
    slash = seg((640, -110), (1010, H * 0.9), S * 0.8, "butt")
    put("careof", unions(c_o, slash, translate(o_o, 1080, 0)), 0x2105)

    # Å angstrom
    A = _letter_A(0, 0, H, 940, S)
    ab = _bb(A)
    ringlet = ring((ab[0] + ab[2]) / 2, H + 205, 150, S * 0.72)
    put("angstrom", union(A, ringlet), 0x212B)

    # ℓ script small l: a tall narrow ascender loop closing at the waist,
    # then a foot swinging out to the right
    sl = S * 0.78
    ell = union(earc_stroke(455, 800, 175, 430, -75, 250, sl),
                earc_stroke(640, 265, 260, 245, 178, 352, sl))
    put("scriptl", ell, 0x2113)

    # ℗ ℠
    circ = ring(CX, CY, 560, 104)
    P_l = _letter_P(0, 0, 640, 430, 128)
    pb = _bb(P_l)
    put("soundcopyright",
        union(circ, translate(P_l, CX - (pb[0] + pb[2]) / 2, CY - (pb[1] + pb[3]) / 2)),
        0x2117, adv=1500)
    S_l = _letter_S(0, 0, 560, 420, 112)
    M_l = _letter_M(0, 0, 560, 560, 112)
    sm = union(S_l, translate(M_l, 560, 0))
    smb = _bb(sm)
    put("servicemark", translate(sm, 154 - smb[0], 799 - smb[1]), 0x2120, adv=ADV)
    return n


# --------------------------------------------------------------------------- #
# 10. Currency
# --------------------------------------------------------------------------- #
def currency(font):
    n = 0
    H = 1300           # currency letter height
    S = CUR_STROKE
    OVERHANG = 105     # how far the cancelling bars stick out

    def put(name, path, cp, adv=None):
        nonlocal n
        _put(font, name, path, cp, adv=adv, pad=200)
        n += 1

    def hbars(path, ys, extra=OVERHANG, w=None):
        b = _bb(path)
        out = path
        for y in ys:
            out = union(out, rect(b[0] - extra, y - (w or S * 0.78) / 2.0,
                                  b[2] + extra, y + (w or S * 0.78) / 2.0))
        return out

    # ₹ Indian rupee: two head bars, a descending stem, and the diagonal leg
    rupee = unions(rect(150, H - S, 920, H),
                   rect(150, H * 0.70 - S / 2.0, 920, H * 0.70 + S / 2.0),
                   rect(470, 0, 470 + S, H * 0.70 + S / 2.0),
                   seg((470 + S, H * 0.40), (900, 0), S, "butt"))
    put("rupeeindian", rupee, 0x20B9)

    # ₺ Turkish lira
    lira_t = unions(seg((430, H), (430, 210), S, "butt"),
                    seg((430, 210), (830, 330), S, "butt"),
                    rect(180, H * 0.62, 800, H * 0.62 + S * 0.8),
                    rect(180, H * 0.44, 800, H * 0.44 + S * 0.8))
    lira_t = union(lira_t, seg((300, H * 0.70), (760, H * 0.90), S * 0.8, "butt"))
    put("liraturkish", lira_t, 0x20BA)

    # ₽ ruble
    P_ = _letter_P(180, 0, H, 700, S)
    put("ruble", union(P_, rect(60, H * 0.30 - S * 0.4, 780, H * 0.30 + S * 0.4)),
        0x20BD)

    # ₩ won
    W_ = _letter_W(60, 0, H, 1180, S)
    put("won", hbars(W_, [H * 0.42, H * 0.60], 40), 0x20A9)

    # ₪ new shekel: a sheen-like left hook and a het-like right hook
    shek = unions(rect(150, H * 0.30, 150 + S, H),          # left stem
                  rect(150, H - S, 620, H),                 # top link
                  rect(620 - S, H * 0.30, 620, H),          # inner stem down
                  rect(620 - S, H * 0.30, 1010, H * 0.30 + S),   # cross to right
                  rect(1010 - S, 0, 1010, H * 0.30 + S),    # right stem down
                  rect(700, H - S, 1010, H),                # right top bar
                  rect(700, H * 0.62, 700 + S, H))          # right hook stem
    put("shekel", shek, 0x20AA)

    # ₫ dong
    D_ = _letter_D(140, 0, H * 0.92, 760, S)
    put("dong", union(D_, rect(60, -190, 980, -190 + S * 0.85)), 0x20AB)

    # ₴ hryvnia
    S_ = _letter_S(140, 0, H, 780, S)
    put("hryvnia", hbars(S_, [H * 0.38, H * 0.56], 60), 0x20B4)

    # ₸ tenge
    T_ = _letter_T(140, 0, H * 0.88, 800, S)
    put("tenge", union(T_, rect(140, H * 0.88 + 130, 940, H * 0.88 + 130 + S * 0.85)),
        0x20B8)

    # ₾ lari
    lari = unions(_letter_C(140, 0, H * 0.9, 820, S, 44),
                  rect(140, H * 0.9 + 120, 960, H * 0.9 + 120 + S * 0.8))
    put("lari", lari, 0x20BE)

    # ₼ manat: a wide arch on a central stem, cut by the baseline bar
    manat = unions(earc_stroke(560, H * 0.34, 400, H * 0.42, 0, 180, S),
                   rect(560 - S / 2.0, 0, 560 + S / 2.0, H * 0.90),
                   rect(80, 0, 1040, S * 0.85))
    put("manat", manat, 0x20BC)

    # ₿ bitcoin
    B_ = _letter_B(180, 0, H, 700, S)
    tick = union(rect(360, H, 360 + S * 0.7, H + 175),
                 rect(620, H, 620 + S * 0.7, H + 175))
    tick2 = union(rect(360, -175, 360 + S * 0.7, 0),
                  rect(620, -175, 620 + S * 0.7, 0))
    put("bitcoin", unions(B_, tick, tick2), 0x20BF)

    # ₦ naira
    N_ = _letter_N(140, 0, H, 880, S)
    put("naira", hbars(N_, [H * 0.40, H * 0.58], 55), 0x20A6)

    # ₱ peso
    P2 = _letter_P(180, 0, H, 700, S)
    put("peso", hbars(P2, [H * 0.62, H * 0.80], 90), 0x20B1)

    # ₡ colon sign
    C2 = _letter_C(160, 0, H, 860, S, 46)
    put("colonsign", union(C2, seg((300, -140), (860, H + 140), S * 0.72, "butt")),
        0x20A1)

    # ₵ cedi
    C3 = _letter_C(160, 0, H, 860, S, 40)
    put("cedi", union(C3, rect(520, -170, 520 + S * 0.8, H + 170)), 0x20B5)

    # ₲ guarani
    G_ = _letter_G(160, 0, H, 880, S)
    put("guarani", union(G_, rect(560, -180, 560 + S * 0.8, H * 0.5)), 0x20B2)

    # ₮ tugrik
    T2 = _letter_T(140, 0, H, 820, S)
    put("tugrik", hbars(T2, [H * 0.34, H * 0.52], 40), 0x20AE)

    # ₭ kip
    K_ = _letter_K(160, 0, H, 820, S)
    put("kip", hbars(K_, [H * 0.60], 60), 0x20AD)

    # ₨ rupee (Rs)
    R_ = _letter_R(120, 0, H, 720, S)
    s_small = _letter_S(880, 0, H * 0.62, 480, S * 0.9)
    put("rupeesign", union(R_, s_small), 0x20A8)

    # ₤ lira, ₣ franc, ₧ peseta
    L_ = _letter_L(160, 0, H, 760, S)
    put("liraitalian", hbars(L_, [H * 0.50, H * 0.66], 50), 0x20A4)
    F_ = _letter_F(160, 0, H, 780, S)
    put("franc", union(F_, rect(60, H * 0.20 - S * 0.4, 620, H * 0.20 + S * 0.4)),
        0x20A3)
    P3 = _letter_P(120, 0, H, 640, S)
    put("peseta", union(P3, _letter_T(760, 0, H, 640, S)), 0x20A7)

    # ₥ mill, ₠ euro-currency, ₰ pfennig, ₳ austral
    M2 = _letter_M(120, 0, H, 1000, S)
    put("mill", union(M2, seg((90, H * 0.22), (1160, H * 0.72), S * 0.7, "butt")), 0x20A5)
    C4 = _letter_C(160, 0, H, 860, S, 46)
    E_ = _letter_E(280, H * 0.12, H * 0.74, 560, S * 0.85)
    put("eurocurrency", union(C4, E_), 0x20A0)
    P4 = _letter_P(140, 0, H, 640, S)
    put("pfennig", union(P4, seg((80, H * 0.18), (860, H * 0.62), S * 0.7, "butt")), 0x20B0)
    A2 = _letter_A(140, 0, H, 940, S)
    put("austral", hbars(A2, [H * 0.62, H * 0.78], 40), 0x20B3)

    # ﷼ Arabic rial: a real ر-ي-ا-ل ligature, composed from this family's own
    # letters at reduced scale so it matches Kurdish text rather than a
    # geometric approximation of it.
    cmap = font.getBestCmap()
    parts = []
    x = 0.0
    for gname in ("uniFEFB", "uniFEF4", "uni0631"):   # لا  ـيـ  ر  (visual L->R)
        if gname not in font["glyf"]:
            parts = []
            break
        p = xform(glyph_path(font, gname), sx=0.52, sy=0.52)
        b = _bb(p)
        if b is None:
            continue
        p = translate(p, x - b[0], -b[1] + 40)
        parts.append(p)
        x = _bb(p)[2] - 60
    if parts:
        rial = unions(*parts)
    else:
        rial = unions(rect(690, 250, 690 + S, 1080),
                      earc_stroke(430, 430, 300, 300, 200, 340, S))
    rb = _bb(rial)
    put("rialsign", translate(rial, 90 - rb[0], 0), 0xFDFC)
    return n


# --------------------------------------------------------------------------- #
# 11. Arabic marks
# --------------------------------------------------------------------------- #
def arabic_marks(font):
    n = 0

    def put(name, path, cp, adv=ADV):
        nonlocal n
        _put(font, name, path, cp, adv=adv)
        n += 1

    zero_o = ring(0, 0, 128, 66)
    pm = glyph_path(font, font.getBestCmap()[0x066A])   # ٪ arabic percent
    pb = _bb(pm)

    # ؉ ؊ arabic per mille / per ten thousand: ٪ plus extra zeros
    put("arabicpermille",
        union(pm, translate(zero_o, pb[2] + 175, 175)), 0x0609,
        font["hmtx"].metrics[font.getBestCmap()[0x066A]][0] + 330)
    put("arabicperkthousand",
        unions(pm, translate(zero_o, pb[2] + 175, 175),
               translate(zero_o, pb[2] + 470, 175)), 0x060A,
        font["hmtx"].metrics[font.getBestCmap()[0x066A]][0] + 620)

    # ٮ dotless beh, ٯ dotless qaf - the family's own bodies with dots removed
    for cp, name, src in ((0x066E, "arabicdotlessbeh", 0x0628),
                          (0x066F, "arabicdotlessqaf", 0x0642)):
        gname = font.getBestCmap()[src]
        p = glyph_path(font, gname)
        b = _bb(p)
        keep = [c for c in p.contours
                if c.bounds and (c.bounds[2] - c.bounds[0]) > (b[2] - b[0]) * 0.35]
        body = P()
        for c in keep:
            body = union(body, c)
        put(name, body, cp, font["hmtx"].metrics[gname][0])

    # ۩ place of sajdah, ۞ rub el hizb, ۝ end of ayah
    rub = P()
    sq = poly([(CX, CY + 470), (CX + 470, CY), (CX, CY - 470), (CX - 470, CY)])
    rub = union(diff(sq, scale_about(sq, 0.68, CX, CY)),
                diff(rotate(sq, 45, CX, CY), scale_about(rotate(sq, 45, CX, CY), 0.68, CX, CY)))
    put("arabicrubelhizb", rub, 0x06DE, 1400)
    # ۝ end of ayah: a ring with a small rosette of rays, not a face
    rays = P()
    for a in range(0, 360, 45):
        rr = math.radians(a)
        rays = union(rays, seg((CX + 180 * math.cos(rr), CY + 180 * math.sin(rr)),
                               (CX + 300 * math.cos(rr), CY + 300 * math.sin(rr)),
                               72, "butt"))
    ayah = unions(ring(CX, CY, 470, 96), rays, circle(CX, CY, 110))
    put("arabicendofayah", ayah, 0x06DD, 1400)
    sajdah = unions(arc_stroke(CX, CY - 120, 430, 0, 180, 104),
                    rect(CX - 470, CY - 240, CX + 470, CY - 240 + 104),
                    rect(CX - 60, CY + 310, CX + 60, CY + 520))
    put("arabicsajdah", sajdah, 0x06E9, 1400)

    # ؆ ؇ arabic-indic cube / fourth root, ؈ ray
    rad = glyph_path(font, "radical")
    radadv = font["hmtx"].metrics["radical"][0]
    three_ar = glyph_path(font, font.getBestCmap()[0x0663])
    tb = _bb(three_ar)
    three_ar = xform(three_ar, sx=0.55, sy=0.55)
    tb = _bb(three_ar)
    put("arabiccuberoot", union(rad, translate(three_ar, 40 - tb[0], 800 - tb[1])),
        0x0606, radadv)
    four_ar = xform(glyph_path(font, font.getBestCmap()[0x0664]), sx=0.55, sy=0.55)
    fb = _bb(four_ar)
    put("arabicfourthroot", union(rad, translate(four_ar, 40 - fb[0], 800 - fb[1])),
        0x0607, radadv)
    ray = unions(rect(CX - 55, 0, CX + 55, 980),
                 arc_stroke(CX, 980, 210, 0, 180, 96),
                 rect(CX - 265, 0, CX + 265, 96))
    put("arabicray", ray, 0x0608, 1200)

    # ؄ ؅ signs that sit above a number - keep them zero-advance marks
    for cp, name in ((0x0604, "arabicsignsamvat"), (0x0605, "arabicnumbermarkabove")):
        mark = unions(arc_stroke(0, 0, 210, 0, 180, 84),
                      rect(-230, -60, -230 + 84, 40),
                      rect(230 - 84, -60, 230, 40))
        install(font, name, translate(mark, 0, 1180), 0, cp)
        n += 1
    return n


# --------------------------------------------------------------------------- #
# Post-build check list
# --------------------------------------------------------------------------- #
# Codepoints that are legitimately blank.
SPACE_CODEPOINTS = (0x2000, 0x2001, 0x2004, 0x2005, 0x2006, 0x2007, 0x2008,
                    0x200B, 0x202F, 0x205F, 0x2060, 0xFEFF, 0x061C,
                    0x0604, 0x0605)

# At least one representative from every group, so a group that silently fails
# to build is caught by the release validation rather than by a reader.
REQUIRED_SYMBOLS = (
    # spaces / invisibles
    0x2000, 0x2007, 0x200B, 0x202F, 0x2060, 0xFEFF,
    # punctuation
    0x2012, 0x2015, 0x2027, 0x2031, 0x2034, 0x2035, 0x203B, 0x203D, 0x2E18,
    0x2047, 0x2048, 0x2049, 0x203C, 0x2042, 0x2051, 0x2023, 0x2043, 0x2016,
    0x2017, 0x2038, 0x201B, 0x201F,
    # superior / inferior
    0x2070, 0x2074, 0x2079, 0x207A, 0x207D, 0x207F,
    0x2080, 0x2084, 0x2089, 0x208A, 0x208E,
    # fractions
    0x2150, 0x2152, 0x2153, 0x2154, 0x215B, 0x215E, 0x2189,
    # maths
    0x2213, 0x2216, 0x2217, 0x2218, 0x221B, 0x221D, 0x2220, 0x2223, 0x2225,
    0x2227, 0x2228, 0x2229, 0x222A, 0x222C, 0x222E, 0x2234, 0x2235, 0x2236,
    0x223C, 0x2243, 0x2245, 0x2261, 0x2262, 0x226A, 0x226B, 0x2282, 0x2286,
    0x2208, 0x2209, 0x2205, 0x2200, 0x2203, 0x2207, 0x2295, 0x2297, 0x22C5,
    0x2300, 0x2308, 0x230B, 0x27E8, 0x27E9, 0x0394, 0x03A9, 0x03C0, 0x2206,
    # arrows
    0x2194, 0x2195, 0x2196, 0x2199, 0x219A, 0x21A9, 0x21B0, 0x21B5, 0x21BA,
    0x21C4, 0x21D0, 0x21D4, 0x21E8, 0x27A1,
    # geometric
    0x25A0, 0x25A1, 0x25AA, 0x25B2, 0x25B3, 0x25B6, 0x25BC, 0x25C0, 0x25C6,
    0x25C7, 0x25CB, 0x25CF, 0x25E6, 0x25EF, 0x25FC,
    # ticks, boxes, stars, suits, music
    0x2605, 0x2606, 0x2610, 0x2611, 0x2612, 0x2713, 0x2714, 0x2717, 0x2718,
    0x2726, 0x2731, 0x2660, 0x2663, 0x2665, 0x2666, 0x266A, 0x266D, 0x266F,
    0x26A0, 0x26A1,
    # letterlike
    0x2103, 0x2105, 0x2109, 0x2113, 0x2116, 0x2117, 0x2120, 0x212B,
    # currency
    0x20A0, 0x20A1, 0x20A3, 0x20A4, 0x20A5, 0x20A6, 0x20A7, 0x20A8, 0x20A9,
    0x20AA, 0x20AB, 0x20AD, 0x20AE, 0x20B0, 0x20B1, 0x20B2, 0x20B3, 0x20B4,
    0x20B5, 0x20B8, 0x20B9, 0x20BA, 0x20BC, 0x20BD, 0x20BE, 0x20BF, 0xFDFC,
    # Arabic signs
    0x0606, 0x0607, 0x0608, 0x0609, 0x060A, 0x066E, 0x066F, 0x06DD, 0x06DE,
    0x06E9,
)


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def build_symbols(font) -> dict:
    counts = {
        "spaces": spaces(font),
        "punctuation": punctuation(font),
        "superiors_inferiors": superiors(font),
        "fractions": fractions(font),
        "math": math_ops(font),
        "arrows": arrows(font),
        "geometric": geometric(font),
        "misc_symbols": misc_symbols(font),
        "letterlike": letterlike(font),
        "currency": currency(font),
        "arabic_marks": arabic_marks(font),
    }
    counts["total"] = sum(counts.values())
    return counts
